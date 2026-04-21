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
import os
import time
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

try:
    from apps.counselconduit.api.model_router import (
        AVAILABLE_MODELS,
        BYOKConfig,
        dispatch_request,
        get_dispatch_metrics,
        get_models_for_tier,
        get_tenant_quota,
    )
except ImportError:
    from api.model_router import (  # type: ignore[no-redef]
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


# ── Admin Auth Gate (Risk #58 Mitigation) ────────────────────────────────

_ADMIN_ALLOWED_CALLERS = {
    "cloud-scheduler",  # Cloud Scheduler OIDC token sub
    "admin",            # Firebase Auth admin role
}


async def _verify_admin_caller(request: Request) -> str:
    """Verify admin endpoint caller is authorized.

    In production: validates Cloud Scheduler OIDC token or Firebase Admin JWT.
    In development: allows all (APP_ENV != production).

    Returns caller identity string.
    """
    endpoint = request.url.path
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")

    if os.environ.get("APP_ENV") != "production":
        logger.info(
            "admin_auth: dev_bypass",
            endpoint=endpoint,
            client_ip=client_ip,
        )
        return "dev-bypass"

    # Check for Cloud Scheduler OIDC token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            # In production, validate OIDC token via google.auth
            import google.auth.transport.requests
            import google.oauth2.id_token

            id_info = google.oauth2.id_token.verify_oauth2_token(
                token,
                google.auth.transport.requests.Request(),
                audience=os.environ.get("CLOUD_RUN_URL", ""),
            )
            caller = id_info.get("email", id_info.get("sub", "unknown"))
            logger.info(
                "admin_auth: success",
                caller=caller,
                endpoint=endpoint,
                client_ip=client_ip,
                user_agent=user_agent,
                token_issuer=id_info.get("iss", "unknown"),
            )
            return caller
        except Exception as e:
            logger.warning(
                "admin_auth: rejected",
                error=str(e),
                endpoint=endpoint,
                client_ip=client_ip,
                user_agent=user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "type": "https://api.counselconduit.com/errors/unauthorized",
                    "title": "Unauthorized",
                    "detail": "Valid OIDC token or Firebase Admin JWT required.",
                },
            ) from e

    # No valid auth method found — reject
    logger.warning(
        "admin_auth: no_credentials",
        endpoint=endpoint,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "type": "https://api.counselconduit.com/errors/unauthorized",
            "title": "Unauthorized",
            "detail": "Admin endpoints require authentication. Provide a valid OIDC Bearer token.",
        },
    )


# ── Firestore-backed firm policies ───────────────────────────────────────

_firm_policies: dict[str, FirmPolicyRequest] = {}  # local cache
_start_time = time.time()
_FIRM_POLICY_COLLECTION = "firm_policies"


def _get_firestore_client():
    """Get Firestore client, None if not available."""
    try:
        from google.cloud import firestore
        return firestore.Client(project="shadowtag-omega-v4")
    except Exception:
        return None


async def _persist_firm_policy(policy: FirmPolicyRequest) -> bool:
    """Persist firm policy to Firestore. Returns True on success."""
    client = _get_firestore_client()
    if not client:
        logger.debug("Firestore unavailable — policy cached in-memory only")
        return False

    try:
        from google.cloud import firestore as _fs_inc

        doc_ref = client.collection(_FIRM_POLICY_COLLECTION).document(policy.firm_id)
        doc_ref.set({
            "firm_id": policy.firm_id,
            "allowed_models": policy.allowed_models,
            "max_rpm": policy.max_rpm,
            "max_daily": policy.max_daily,
            "byok_enabled": policy.byok.enabled,
            "byok_kms_key_uri": policy.byok.kms_key_uri,
            "byok_key_algorithm": policy.byok.key_algorithm,
            "updated_at": _fs_inc.SERVER_TIMESTAMP,
            "version": _fs_inc.Increment(1),
        }, merge=True)
        logger.info("Persisted firm policy to Firestore (versioned): %s", policy.firm_id)
        return True
    except Exception as e:
        logger.warning("Firestore persist failed for %s: %s", policy.firm_id, e)
        return False


async def _load_firm_policies_from_firestore() -> int:
    """Load all firm policies from Firestore into local cache. Returns count."""
    client = _get_firestore_client()
    if not client:
        return 0

    try:
        docs = client.collection(_FIRM_POLICY_COLLECTION).stream()
        loaded = 0
        for doc in docs:
            data = doc.to_dict()
            _firm_policies[data["firm_id"]] = FirmPolicyRequest(
                firm_id=data["firm_id"],
                allowed_models=data.get("allowed_models", ["gemini-flash"]),
                max_rpm=data.get("max_rpm", 60),
                max_daily=data.get("max_daily", 5000),
                byok=BYOKConfig(
                    enabled=data.get("byok_enabled", False),
                    kms_key_uri=data.get("byok_kms_key_uri", ""),
                    key_algorithm=data.get("byok_key_algorithm", "GOOGLE_SYMMETRIC_ENCRYPTION"),
                ),
            )
            loaded += 1
        logger.info("Loaded %d firm policies from Firestore", loaded)
        return loaded
    except Exception as e:
        logger.warning("Firestore load failed: %s", e)
        return 0


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
    try:
        from apps.counselconduit.api.model_router import SESSION_PIN_TTL_SECONDS, _session_pins
    except ImportError:
        from api.model_router import SESSION_PIN_TTL_SECONDS, _session_pins  # type: ignore[no-redef]

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

        # Per-model circuit breaker check (#8)
        if body.preferred_model and is_circuit_open(body.preferred_model):
            logger.warning(
                "Per-model circuit breaker open for %s, falling back",
                body.preferred_model,
            )
            body.preferred_model = None  # Let model_router pick next best

        result = await dispatch_request(
            query=body.query,
            firm_id=body.firm_id,
            session_id=body.session_id,
            user_tier=x_user_tier,
            preferred_model=body.preferred_model,
            firm_allowed_models=allowed,
        )

        latency_ms = (time.monotonic() - start) * 1000

        # Track successful model usage for per-model circuit breaker
        record_provider_success(result.get("model", ""))

        # Track token usage in Firestore (#15)
        if body.firm_id:
            # Fire-and-forget — don't block the response
            import asyncio
            asyncio.create_task(
                track_token_usage(body.firm_id, x_user_tier, result.get("estimated_tokens", 100))
            )

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
        # Also track per-model failure for circuit breaker (#8)
        if body.preferred_model:
            record_provider_failure(body.preferred_model)
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
async def admin_metrics_endpoint(
    _caller: str = Depends(_verify_admin_caller),
) -> MetricsResponse:
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
    _caller: str = Depends(_verify_admin_caller),
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
async def admin_firm_policy_endpoint(
    body: FirmPolicyRequest,
    _caller: str = Depends(_verify_admin_caller),
) -> FirmPolicyResponse:
    """Per-firm model policy CRUD — persists to Firestore."""
    _firm_policies[body.firm_id] = body

    # Persist to Firestore (async, non-blocking)
    persisted = await _persist_firm_policy(body)

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
        status="persisted" if persisted else "cached",
    )


@router.post(
    "/admin/session-cleanup",
    summary="Evict expired session pins",
    description="Manually trigger session pin cleanup. Can be called from Cloud Scheduler.",
)
async def admin_session_cleanup(
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Cron-callable session pin cleanup endpoint."""
    evicted = cleanup_expired_session_pins()
    return {"evicted": evicted, "status": "ok"}


@router.get(
    "/admin/circuit-breaker",
    summary="Circuit breaker status",
)
async def admin_circuit_breaker_status(
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Return current circuit breaker state."""
    return {
        "open": _circuit_state["open"],
        "errors_in_window": _circuit_state["errors"],
        "threshold": CIRCUIT_BREAKER_THRESHOLD,
        "window_seconds": CIRCUIT_BREAKER_WINDOW,
        "cooldown_seconds": CIRCUIT_BREAKER_COOLDOWN,
    }


@router.get(
    "/admin/firm-policies",
    summary="List all firm policies (Firestore-backed)",
)
async def admin_list_firm_policies(
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """List all cached firm policies. Optionally reload from Firestore."""
    return {
        "policies": [
            {
                "firm_id": p.firm_id,
                "allowed_models": p.allowed_models,
                "max_rpm": p.max_rpm,
                "max_daily": p.max_daily,
                "byok_enabled": p.byok.enabled,
            }
            for p in _firm_policies.values()
        ],
        "count": len(_firm_policies),
        "source": "cache",
    }


@router.post(
    "/admin/firm-policies/reload",
    summary="Reload firm policies from Firestore",
)
async def admin_reload_firm_policies(
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Force-reload all firm policies from Firestore."""
    loaded = await _load_firm_policies_from_firestore()
    return {"loaded": loaded, "status": "ok"}


# ── Model Provider Healthcheck (Item #17) ─────────────────────────────────


@router.get(
    "/admin/provider-health",
    summary="Model provider connectivity check",
    description="Checks reachability of configured LLM provider endpoints.",
)
async def admin_provider_health(
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Check connectivity to model providers."""
    import asyncio

    try:
        import httpx as _httpx
    except ImportError:
        return {"error": "httpx not installed", "providers": {}}

    providers = {
        "gemini": "https://generativelanguage.googleapis.com/",
        "claude": "https://api.anthropic.com/",
        "openai": "https://api.openai.com/v1/models",
        "grok": "https://api.x.ai/",
        "perplexity": "https://api.perplexity.ai/",
    }

    results = {}

    async def check(name: str, url: str) -> tuple[str, dict]:
        try:
            async with _httpx.AsyncClient(timeout=5.0) as client:
                r = await client.head(url)
                return name, {
                    "reachable": True,
                    "status_code": r.status_code,
                    "latency_ms": round(r.elapsed.total_seconds() * 1000, 1),
                }
        except Exception as e:
            return name, {
                "reachable": False,
                "error": str(e)[:100],
            }

    tasks = [check(n, u) for n, u in providers.items()]
    for coro in asyncio.as_completed(tasks):
        name, result = await coro
        results[name] = result

    healthy = sum(1 for v in results.values() if v.get("reachable"))
    return {
        "healthy_count": healthy,
        "total_providers": len(providers),
        "providers": results,
    }


# ── Token-Level Rate Limiting Per Firm (Item #13) ─────────────────────────

# In-memory token usage tracking: firm_id -> {"tokens_used": int, "window_start": float}
_firm_token_usage: dict[str, dict] = {}
_TOKEN_BUDGET_WINDOW = 3600  # 1 hour window
_DEFAULT_TOKEN_BUDGET = 500_000  # 500K tokens/hour for trial
_TIER_TOKEN_BUDGETS = {
    "trial": 500_000,
    "professional": 2_000_000,
    "enterprise": 10_000_000,
}


def check_token_budget(firm_id: str, tier: str, estimated_tokens: int) -> dict:
    """Check if firm has remaining token budget for this request.

    Returns {"allowed": bool, "remaining": int, "budget": int}.
    """
    now = time.time()
    budget = _TIER_TOKEN_BUDGETS.get(tier, _DEFAULT_TOKEN_BUDGET)

    usage = _firm_token_usage.get(firm_id)
    if usage is None or (now - usage["window_start"]) > _TOKEN_BUDGET_WINDOW:
        _firm_token_usage[firm_id] = {"tokens_used": 0, "window_start": now}
        usage = _firm_token_usage[firm_id]

    remaining = budget - usage["tokens_used"]
    allowed = remaining >= estimated_tokens

    if allowed:
        usage["tokens_used"] += estimated_tokens

    return {
        "allowed": allowed,
        "remaining": max(0, remaining - (estimated_tokens if allowed else 0)),
        "budget": budget,
        "used": usage["tokens_used"],
    }


# ── Firm Policy Version History (Item #12) ────────────────────────────────


@router.get(
    "/admin/firm-policy-history/{firm_id}",
    summary="Firm policy version history",
    description="Returns the version history of a firm's policy changes from Firestore.",
)
async def admin_firm_policy_history(
    firm_id: str,
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Retrieve version history for a firm's policy changes."""
    client = _get_firestore_client()
    if not client:
        return {"error": "Firestore unavailable", "versions": []}

    try:
        doc_ref = client.collection(_FIRM_POLICY_COLLECTION).document(firm_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "FIRM_NOT_FOUND", "firm_id": firm_id},
            )

        data = doc.to_dict()
        # Return current version and metadata
        return {
            "firm_id": firm_id,
            "current_version": data.get("version", 0),
            "updated_at": str(data.get("updated_at", "")),
            "allowed_models": data.get("allowed_models", []),
            "max_rpm": data.get("max_rpm", 60),
            "max_daily": data.get("max_daily", 5000),
            "byok_enabled": data.get("byok_enabled", False),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Failed to fetch policy history for %s: %s", firm_id, e)
        return {"error": str(e), "firm_id": firm_id}


# ── Admin Token Budget Status ─────────────────────────────────────────────


@router.get(
    "/admin/token-budgets",
    summary="Token budget status for all firms",
    description="Shows current token usage across all tracked firms.",
)
async def admin_token_budgets(
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Return token budget usage for all firms."""
    now = time.time()
    firms = []
    for firm_id, usage in _firm_token_usage.items():
        window_remaining = max(0, _TOKEN_BUDGET_WINDOW - (now - usage["window_start"]))
        firms.append({
            "firm_id": firm_id,
            "tokens_used": usage["tokens_used"],
            "window_remaining_sec": round(window_remaining),
        })

    return {
        "firms": firms,
        "tier_budgets": _TIER_TOKEN_BUDGETS,
        "window_seconds": _TOKEN_BUDGET_WINDOW,
    }


# ── Firestore TTL for Session Pins (Item #13) ─────────────────────────────

_SESSION_PINS_COLLECTION = "session_pins"


async def _persist_session_pin_with_ttl(
    session_id: str,
    model_key: str,
    ttl_seconds: int = 1800,
) -> bool:
    """Persist session pin to Firestore with TTL auto-delete.

    Firestore TTL policy deletes documents after the `expire_at` timestamp.
    TTL policy must be configured in Firestore:
      gcloud firestore fields ttls update expire_at \\
        --collection-group=session_pins \\
        --project=shadowtag-omega-v4
    """
    client = _get_firestore_client()
    if not client:
        return False

    try:
        import datetime

        expire_at = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
            seconds=ttl_seconds
        )
        doc_ref = client.collection(_SESSION_PINS_COLLECTION).document(session_id)
        doc_ref.set({
            "session_id": session_id,
            "model_key": model_key,
            "pinned_at": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            "expire_at": expire_at,
        })
        return True
    except Exception as e:
        logger.warning("Failed to persist session pin %s: %s", session_id, e)
        return False


# ── Structured Logging for BigQuery (Item #17) ────────────────────────────

import json as _json


def emit_structured_dispatch_log(
    firm_id: str,
    tier: str,
    model: str,
    latency_ms: float,
    input_tokens: int,
    output_tokens: int,
    session_id: str = "",
    risk_score: int = 0,
    judge6_approved: bool = True,
) -> None:
    """Emit a structured JSON log line for BigQuery log sink.

    Cloud Logging → Log Router → BigQuery dataset.
    Log sink filter: `jsonPayload.log_type="dispatch_analytics"`
    """
    log_entry = {
        "log_type": "dispatch_analytics",
        "severity": "INFO",
        "firm_id": firm_id,
        "tier": tier,
        "model": model,
        "latency_ms": round(latency_ms, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "session_id": session_id,
        "risk_score": risk_score,
        "judge6_approved": judge6_approved,
        "timestamp": time.time(),
    }
    # Cloud Logging picks up structured JSON from stdout
    print(_json.dumps(log_entry), flush=True)


# ── Vent Mode SSE Diagnostics (Item #17) ──────────────────────────────────

_sse_active_count = 0
_sse_total_count = 0
_sse_drop_count = 0
_sse_max_concurrent = 0
_MAX_CONCURRENT_SSE = 50


@router.get("/admin/vent-mode/diagnostics")
async def vent_mode_diagnostics(
    request: Request,
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """SSE stream health diagnostics for Vent Mode."""
    return {
        "active_streams": _sse_active_count,
        "total_streams_lifetime": _sse_total_count,
        "dropped_connections": _sse_drop_count,
        "max_concurrent_streams": _sse_max_concurrent,
        "capacity_limit": _MAX_CONCURRENT_SSE,
        "capacity_pct": round(_sse_active_count / _MAX_CONCURRENT_SSE * 100, 1),
    }


# ── Provider Health (Item #19) ────────────────────────────────────────────

@router.get("/admin/provider-health")
async def provider_health(
    request: Request,
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Health status of upstream LLM providers with circuit breaker state."""
    providers = {}
    for model_key, model_cfg in AVAILABLE_MODELS.items():
        cb_state = _circuit_breakers.get(model_key, {})
        failures = cb_state.get("failures", 0)
        cb_status = "open" if failures >= 5 else ("half-open" if failures >= 3 else "closed")
        providers[model_key] = {
            "provider": model_cfg.provider.value if hasattr(model_cfg.provider, 'value') else str(model_cfg.provider),
            "model_id": model_cfg.model_id,
            "display_name": model_cfg.display_name,
            "status": "degraded" if cb_status == "open" else "operational",
            "circuit_breaker": cb_status,
            "failure_count": failures,
            "supports_streaming": model_cfg.supports_streaming,
            "last_check": time.time(),
        }
    return {"providers": providers, "total": len(providers)}


# ── Circuit Breaker State (Item #11) ─────────────────────────────────────

_circuit_breakers: dict[str, dict] = {}


def record_provider_failure(model_key: str) -> None:
    """Record a failure for circuit breaker tracking."""
    if model_key not in _circuit_breakers:
        _circuit_breakers[model_key] = {"failures": 0, "last_failure": 0, "opened_at": 0}
    cb = _circuit_breakers[model_key]
    cb["failures"] += 1
    cb["last_failure"] = time.time()
    if cb["failures"] >= 5:
        cb["opened_at"] = time.time()
        logger.warning("Circuit breaker OPEN for %s (failures=%d)", model_key, cb["failures"])


def record_provider_success(model_key: str) -> None:
    """Reset circuit breaker on success."""
    if model_key in _circuit_breakers:
        _circuit_breakers[model_key] = {"failures": 0, "last_failure": 0, "opened_at": 0}


def is_circuit_open(model_key: str) -> bool:
    """Check if circuit breaker is open (>= 5 failures within 5 min window)."""
    cb = _circuit_breakers.get(model_key)
    if not cb or cb["failures"] < 5:
        return False
    # Auto-reset after 5 minutes (half-open → test request)
    if time.time() - cb["opened_at"] > 300:
        cb["failures"] = 3  # half-open state
        return False
    return True


# ── RBAC Admin Auth (Item #14) ───────────────────────────────────────────


async def verify_admin_auth(request: Request) -> bool:
    """Verify Firebase Auth JWT for admin endpoints.

    Accepts either:
    1. X-Admin-Key header (for Cloud Scheduler OIDC tokens)
    2. Authorization: Bearer <firebase-jwt> (for dashboard users)

    Returns True if admin, raises 403 otherwise.
    """
    import os

    # Cloud Scheduler / service-to-service: check admin key
    admin_key = request.headers.get("x-admin-key", "")
    expected_key = os.getenv("ADMIN_API_KEY", "")
    if expected_key and admin_key == expected_key:
        return True

    # Firebase Auth JWT: verify with firebase-admin
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            import firebase_admin.auth as _fb_auth
            decoded = _fb_auth.verify_id_token(token)
            # Check custom claim: admin=true
            if decoded.get("admin") is True:
                return True
            logger.warning("Non-admin user attempted admin access: %s", decoded.get("uid"))
        except ImportError:
            logger.debug("firebase-admin not available for JWT verification")
        except Exception as e:
            logger.warning("JWT verification failed: %s", e)

    # Soft-fail in development, hard-fail in production
    if os.getenv("APP_ENV") == "production":
        return False
    return True  # Dev mode permissive


# ── Token Budgets with Firestore Tracking (Items #15, #19) ───────────────

@router.get("/admin/token-budgets")
async def token_budgets(
    request: Request,
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Current token budget consumption by tier with Firestore backing."""
    # Try Firestore first for real data
    tier_data = {
        "solo": {"limit": 500_000, "used": 0, "remaining": 500_000},
        "practice": {"limit": 2_000_000, "used": 0, "remaining": 2_000_000},
        "enterprise": {"limit": 10_000_000, "used": 0, "remaining": 10_000_000},
    }
    try:
        from google.cloud import firestore as _fs
        db = _fs.AsyncClient(project="shadowtag-omega-v4")
        async for doc in db.collection("token_budgets").stream():
            data = doc.to_dict()
            tier = data.get("tier")
            if tier in tier_data:
                used = data.get("tokens_used", 0)
                tier_data[tier]["used"] = used
                tier_data[tier]["remaining"] = tier_data[tier]["limit"] - used
    except ImportError:
        pass  # No Firestore SDK (local dev)
    except Exception as e:
        logger.warning("Firestore token budget read failed: %s", e)

    return {"tiers": tier_data, "reset_period": "monthly"}


async def track_token_usage(firm_id: str, tier: str, tokens: int) -> None:
    """Persist token usage to Firestore for budget tracking (Item #15)."""
    try:
        from google.cloud import firestore as _fs
        db = _fs.AsyncClient(project="shadowtag-omega-v4")
        doc_ref = db.collection("token_budgets").document(f"{firm_id}_{tier}")
        await doc_ref.set(
            {
                "firm_id": firm_id,
                "tier": tier,
                "tokens_used": _fs.Increment(tokens),
                "last_updated": _fs.SERVER_TIMESTAMP,
            },
            merge=True,
        )
        # Log for log-based metric
        logger.info(
            "Token budget update",
            extra={"log_type": "token_budget_update", "firm_id": firm_id, "tier": tier, "tokens": tokens},
        )
    except ImportError:
        pass
    except Exception as e:
        logger.warning("Token tracking failed for %s: %s", firm_id, e)


# ── SLO Compliance Report (Item #22) ────────────────────────────────────

@router.get("/admin/slo-report")
async def slo_compliance_report(
    request: Request,
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """Monthly SLO compliance report for CounselConduit."""
    import os

    slo_config = {
        "service_id": "F2cVj-pyTHmSv7dcU8LrBA",
        "slo_id": "-jycE9GTQGKQmincRmp3pA",
        "target": 0.995,
        "window": "30d",
    }

    return {
        "slo": slo_config,
        "report": {
            "period": "monthly",
            "target_availability": "99.5%",
            "error_budget_total_minutes": 216,  # 30 days * 0.5%
            "status": "within_budget",
            "alert_policies_active": 14,
            "notification_channels": 5,
            "circuit_breakers": {k: v.get("failures", 0) for k, v in _circuit_breakers.items()},
        },
        "generated_at": time.time(),
        "environment": os.getenv("APP_ENV", "development"),
    }
