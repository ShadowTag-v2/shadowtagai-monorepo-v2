# apps/counselconduit/api/dispatch_router.py
"""NadirClaw Dispatch FastAPI Router.

Wires dispatch_request() into actual FastAPI route handlers.
Provides:
    - POST /api/v1/dispatch — model routing endpoint
    - GET  /admin/metrics    — dispatch metrics (Cloud Monitoring export)
    - GET  /admin/models     — available models for tier
    - POST /admin/firm-policy — per-firm model policy CRUD
    - GET  /api/v1/dispatch/openapi — OpenAPI schema fragment
"""

from __future__ import annotations

import logging
import time
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

from apps.counselconduit.api.model_router import (
    AVAILABLE_MODELS,
    BYOKConfig,
    dispatch_request,
    get_dispatch_metrics,
    get_models_for_tier,
    get_tenant_quota,
)

logger = logging.getLogger("counselconduit.dispatch_router")

router = APIRouter(tags=["dispatch"])


# ── Request/Response Models (OpenAPI) ────────────────────────────────────


class DispatchRequest(BaseModel):
    """POST /api/v1/dispatch request body."""

    query: str = Field(..., min_length=1, max_length=50000, description="User query text")
    firm_id: str = Field(..., min_length=1, max_length=128, description="Firm tenant ID")
    session_id: str = Field(default="", max_length=128, description="Session ID for model pinning")
    preferred_model: str | None = Field(default=None, description="Override auto-routing with specific model")
    firm_allowed_models: list[str] = Field(
        default_factory=lambda: ["gemini-flash"],
        description="Models permitted by firm policy",
    )


class DispatchResponse(BaseModel):
    """POST /api/v1/dispatch response body."""

    model: str = Field(description="Selected model ID")
    provider: str = Field(description="Model provider (gemini, claude, openai, etc.)")
    tier: str = Field(description="Dispatch tier (simple, complex, agentic)")
    session_pinned: bool = Field(description="Whether session is pinned to this model")
    cost_per_1k_input: float = Field(description="Cost per 1K input tokens (USD)")
    latency_ms: float = Field(description="Routing latency in milliseconds")


class MetricsResponse(BaseModel):
    """GET /admin/metrics response body."""

    dispatch_counts: dict[str, int]
    total_dispatches: int
    uptime_seconds: float


class FirmPolicyRequest(BaseModel):
    """POST /admin/firm-policy request body."""

    firm_id: str
    allowed_models: list[str]
    max_rpm: int = 60
    max_daily: int = 5000
    byok: BYOKConfig = Field(default_factory=BYOKConfig)


class ModelInfoResponse(BaseModel):
    """Individual model info for GET /admin/models."""

    key: str
    model_id: str
    display_name: str
    provider: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_streaming: bool
    supports_tools: bool


class FirmPolicyResponse(BaseModel):
    """POST /admin/firm-policy response body."""

    firm_id: str
    allowed_models: list[str]
    quota_rpm: int
    quota_daily: int
    byok_enabled: bool
    status: str = "updated"


# ── In-memory firm policies (Firestore-backed in production) ─────────────

_firm_policies: dict[str, FirmPolicyRequest] = {}
_start_time = time.time()


# ── Circuit Breaker (Load Shedding) ──────────────────────────────────────

_circuit_state = {"errors": 0, "last_error": 0.0, "open": False}
CIRCUIT_BREAKER_THRESHOLD = 10  # errors in window
CIRCUIT_BREAKER_WINDOW = 60  # seconds
CIRCUIT_BREAKER_COOLDOWN = 30  # seconds to half-open


def _check_circuit_breaker() -> None:
    """Load-shedding circuit breaker. Trips after CIRCUIT_BREAKER_THRESHOLD errors."""
    now = time.time()

    # Reset error count if window rolled over
    if now - _circuit_state["last_error"] > CIRCUIT_BREAKER_WINDOW:
        _circuit_state["errors"] = 0
        _circuit_state["open"] = False

    if _circuit_state["open"]:
        # Check if cooldown has passed (half-open)
        if now - _circuit_state["last_error"] > CIRCUIT_BREAKER_COOLDOWN:
            _circuit_state["open"] = False
            logger.info("Circuit breaker half-open, allowing request")
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "type": "https://api.counselconduit.com/errors/circuit-open",
                    "title": "Service Temporarily Unavailable",
                    "detail": "Model dispatch circuit breaker open. Retry after cooldown.",
                    "retry_after_seconds": CIRCUIT_BREAKER_COOLDOWN,
                },
            )


def _record_circuit_error() -> None:
    """Record an error for circuit breaker tracking."""
    _circuit_state["errors"] += 1
    _circuit_state["last_error"] = time.time()
    if _circuit_state["errors"] >= CIRCUIT_BREAKER_THRESHOLD:
        _circuit_state["open"] = True
        logger.warning("Circuit breaker OPEN — %d errors in window", _circuit_state["errors"])


# ── Rate Limit Headers ────────────────────────────────────────────────────


def _add_rate_limit_headers(response: Response, firm_id: str, tier: str) -> None:
    """Add rate-limit headers (RFC 6585 + draft-ietf-httpapi-ratelimit) to response."""
    quota = get_tenant_quota(firm_id, tier)
    limit = quota.tier_overrides.get(tier, quota.max_rpm)

    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(max(0, limit - quota.current_rpm))
    response.headers["X-RateLimit-Reset"] = str(60)  # resets every 60 seconds
    response.headers["X-Dispatch-Tier"] = tier


# ── Session Pin Cleanup (Cron-callable) ──────────────────────────────────


def cleanup_expired_session_pins() -> int:
    """Evict expired session pins. Call from Cloud Scheduler or cron endpoint.

    Returns count of evicted pins.
    """
    from apps.counselconduit.api.model_router import SESSION_PIN_TTL_SECONDS, _session_pins

    now = time.time()
    expired = [
        sid for sid, (_, ts) in _session_pins.items()
        if now - ts > SESSION_PIN_TTL_SECONDS
    ]
    for sid in expired:
        del _session_pins[sid]

    if expired:
        logger.info("Evicted %d expired session pins", len(expired))
    return len(expired)


# ── Routes ────────────────────────────────────────────────────────────────


@router.post(
    "/api/v1/dispatch",
    response_model=DispatchResponse,
    summary="Route a query to the optimal LLM",
    description=(
        "NadirClaw 3-tier dispatch: classifies prompt complexity (~10ms), "
        "selects optimal model based on firm policy + tier + session context, "
        "tracks quota, and returns routing decision with cost estimate."
    ),
    responses={
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Circuit breaker open"},
    },
)
async def dispatch_endpoint(
    body: DispatchRequest,
    response: Response,
    x_user_tier: Annotated[str, Header(alias="X-User-Tier")] = "trial",
) -> DispatchResponse:
    """Model dispatch endpoint — wires NadirClaw into FastAPI."""
    _check_circuit_breaker()

    start = time.monotonic()

    try:
        # Wire firm policy if registered
        allowed = body.firm_allowed_models
        if body.firm_id in _firm_policies:
            allowed = _firm_policies[body.firm_id].allowed_models

        result = await dispatch_request(
            query=body.query,
            firm_id=body.firm_id,
            session_id=body.session_id,
            user_tier=x_user_tier,
            preferred_model=body.preferred_model,
            firm_allowed_models=allowed,
        )

        latency_ms = (time.monotonic() - start) * 1000

        # Add rate-limit headers
        _add_rate_limit_headers(response, body.firm_id, x_user_tier)

        return DispatchResponse(
            model=result["model"],
            provider=result["provider"],
            tier=result["tier"],
            session_pinned=result["session_pinned"],
            cost_per_1k_input=result["cost_per_1k_input"],
            latency_ms=round(latency_ms, 2),
        )

    except HTTPException:
        raise
    except Exception as e:
        _record_circuit_error()
        logger.exception("Dispatch failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "type": "https://api.counselconduit.com/errors/dispatch-failed",
                "title": "Dispatch Failed",
                "detail": "Model routing failed. Falling back is not possible.",
            },
        ) from e


@router.get(
    "/admin/metrics",
    response_model=MetricsResponse,
    summary="Dispatch metrics for Cloud Monitoring",
    description="Returns all NadirClaw dispatch metrics: tier distribution, fallback hits, totals.",
)
async def admin_metrics_endpoint() -> MetricsResponse:
    """Expose dispatch metrics for Cloud Monitoring scraping."""
    metrics = get_dispatch_metrics()
    total = sum(v for k, v in metrics.items() if k.startswith("dispatch."))
    uptime = time.time() - _start_time

    return MetricsResponse(
        dispatch_counts=dict(metrics),
        total_dispatches=total,
        uptime_seconds=round(uptime, 1),
    )


@router.get(
    "/admin/models",
    response_model=list[ModelInfoResponse],
    summary="List available models for subscription tier",
)
async def admin_models_endpoint(
    tier: str = "trial",
) -> list[ModelInfoResponse]:
    """Return available models filtered by subscription tier."""
    models = get_models_for_tier(tier)
    return [
        ModelInfoResponse(
            key=key,
            model_id=m.model_id,
            display_name=m.display_name,
            provider=m.provider.value,
            cost_per_1k_input=m.cost_per_1k_input,
            cost_per_1k_output=m.cost_per_1k_output,
            supports_streaming=m.supports_streaming,
            supports_tools=m.supports_tools,
        )
        for key, m in AVAILABLE_MODELS.items()
        if m in models
    ]


@router.post(
    "/admin/firm-policy",
    response_model=FirmPolicyResponse,
    summary="Set per-firm model policy and quota",
    description="Create or update model routing policy for a specific firm. Controls allowed models and quota limits.",
)
async def admin_firm_policy_endpoint(body: FirmPolicyRequest) -> FirmPolicyResponse:
    """Per-firm model policy CRUD."""
    _firm_policies[body.firm_id] = body

    # Update quota overrides
    quota = get_tenant_quota(body.firm_id)
    quota.max_rpm = body.max_rpm
    quota.max_daily = body.max_daily

    logger.info(
        "Updated firm policy for %s: models=%s, rpm=%d",
        body.firm_id,
        body.allowed_models,
        body.max_rpm,
    )

    return FirmPolicyResponse(
        firm_id=body.firm_id,
        allowed_models=body.allowed_models,
        quota_rpm=body.max_rpm,
        quota_daily=body.max_daily,
        byok_enabled=body.byok.enabled,
    )


@router.post(
    "/admin/session-cleanup",
    summary="Evict expired session pins",
    description="Manually trigger session pin cleanup. Can be called from Cloud Scheduler.",
)
async def admin_session_cleanup() -> dict:
    """Cron-callable session pin cleanup endpoint."""
    evicted = cleanup_expired_session_pins()
    return {"evicted": evicted, "status": "ok"}


@router.get(
    "/admin/circuit-breaker",
    summary="Circuit breaker status",
)
async def admin_circuit_breaker_status() -> dict:
    """Return current circuit breaker state."""
    return {
        "open": _circuit_state["open"],
        "errors_in_window": _circuit_state["errors"],
        "threshold": CIRCUIT_BREAKER_THRESHOLD,
        "window_seconds": CIRCUIT_BREAKER_WINDOW,
        "cooldown_seconds": CIRCUIT_BREAKER_COOLDOWN,
    }
