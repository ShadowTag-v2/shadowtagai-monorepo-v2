# apps/counselconduit/api/sandbox_router.py
"""Phase 3 Sandbox Router Middleware for CounselConduit.

Enforces tenant isolation, resource quotas, and tool execution sandboxing.
Acts as middleware between the FastAPI app and all tenant-scoped operations.

Architecture:
- Routes requests through tenant context extraction
- Validates per-tenant quotas (API calls, tokens, storage)
- Delegates tool execution to Cloud Run Jobs (gVisor-isolated)
- Issues ephemeral LiteLLM proxy tokens
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("counselconduit.sandbox_router")

# ── Configuration ─────────────────────────────────────────────────────────

_TOKEN_TTL_SECONDS = int(os.getenv("PROXY_TOKEN_TTL", "900"))  # 15 min
_MAX_TOKENS_PER_SESSION = int(os.getenv("MAX_TOKENS_PER_SESSION", "100000"))

# Per-tier resource quotas
TIER_QUOTAS = {
    "trial": {
        "max_api_calls_per_hour": 50,
        "max_daily_tokens": 50_000,
        "max_concurrent_sessions": 1,
        "models": ["gemini-3.1-flash-lite-preview"],
    },
    "solo": {
        "max_api_calls_per_hour": 200,
        "max_daily_tokens": 500_000,
        "max_concurrent_sessions": 3,
        "models": ["gemini-3.1-flash-lite-preview", "gemini-3.1-pro"],
    },
    "practice": {
        "max_api_calls_per_hour": 1000,
        "max_daily_tokens": 2_000_000,
        "max_concurrent_sessions": 10,
        "models": ["gemini-3.1-flash-lite-preview", "gemini-3.1-pro", "claude-sonnet-4-5"],
    },
    "enterprise": {
        "max_api_calls_per_hour": 10000,
        "max_daily_tokens": 50_000_000,
        "max_concurrent_sessions": 50,
        "models": ["*"],  # All models
    },
}


# ── Data Classes ──────────────────────────────────────────────────────────


@dataclass
class TenantContext:
    """Extracted tenant context from request."""
    firm_id: str
    attorney_id: str | None = None
    session_id: str | None = None
    tier: str = "trial"
    quotas: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProxyToken:
    """Ephemeral proxy token for LiteLLM."""
    token: str
    firm_id: str
    session_id: str
    model: str
    max_tokens: int
    expires_at: float


# ── Tenant Context Extraction ─────────────────────────────────────────────

# In-memory quota tracking (production: Redis or Firestore)
_hourly_counts: dict[str, list[float]] = {}  # firm_id -> [timestamps]


def extract_tenant_context(request: Request) -> TenantContext | None:
    """Extract tenant context from request headers or JWT claims.

    Returns None for public endpoints that don't require tenant context.
    """
    # Skip non-tenant endpoints
    if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
        return None

    # Extract from JWT claims (set by auth middleware)
    firm_id = request.headers.get("X-Firm-ID") or getattr(request.state, "firm_id", None)
    attorney_id = request.headers.get("X-Attorney-ID") or getattr(request.state, "attorney_id", None)
    session_id = request.headers.get("X-Session-ID")

    if not firm_id:
        return None

    # Look up tier from Firestore (cached with 5-min TTL in production)
    tier = _get_firm_tier(firm_id)
    quotas = TIER_QUOTAS.get(tier, TIER_QUOTAS["trial"])

    return TenantContext(
        firm_id=firm_id,
        attorney_id=attorney_id,
        session_id=session_id,
        tier=tier,
        quotas=quotas,
    )


def _get_firm_tier(firm_id: str) -> str:
    """Get the billing tier for a firm. Production: cached Firestore lookup."""
    try:
        try:
            from apps.counselconduit.api.firestore_client import _get_client
        except ImportError:
            from api.firestore_client import _get_client  # type: ignore[no-redef]

        db = _get_client()
        doc = db.collection("firms").document(firm_id).get()
        if doc.exists:
            return doc.to_dict().get("tier", "trial")
    except Exception:
        pass
    return "trial"


# ── Quota Enforcement ─────────────────────────────────────────────────────


def check_quota(ctx: TenantContext) -> bool:
    """Check if the tenant is within their hourly API call quota.

    Returns True if allowed, False if quota exceeded.
    """
    max_calls = ctx.quotas.get("max_api_calls_per_hour", 50)
    now = time.monotonic()
    window = 3600  # 1 hour

    if ctx.firm_id not in _hourly_counts:
        _hourly_counts[ctx.firm_id] = []

    # Purge expired entries
    _hourly_counts[ctx.firm_id] = [
        ts for ts in _hourly_counts[ctx.firm_id] if now - ts < window
    ]

    if len(_hourly_counts[ctx.firm_id]) >= max_calls:
        return False

    _hourly_counts[ctx.firm_id].append(now)
    return True


# ── Proxy Token Generation ────────────────────────────────────────────────


def issue_proxy_token(
    firm_id: str,
    session_id: str,
    model: str,
    max_tokens: int = _MAX_TOKENS_PER_SESSION,
) -> ProxyToken:
    """Issue an ephemeral proxy token for LiteLLM access.

    Token is bound to:
    - Specific firm + session
    - Specific model
    - Token budget (max_tokens)
    - TTL (15 minutes default)
    """
    import hashlib
    import secrets

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(f"{firm_id}:{session_id}:{raw_token}".encode()).hexdigest()[:48]

    return ProxyToken(
        token=f"ctx_{token_hash}",
        firm_id=firm_id,
        session_id=session_id,
        model=model,
        max_tokens=max_tokens,
        expires_at=time.time() + _TOKEN_TTL_SECONDS,
    )


# ── Middleware ─────────────────────────────────────────────────────────────


class SandboxMiddleware(BaseHTTPMiddleware):
    """Starlette middleware for tenant isolation and quota enforcement.

    Intercepts all requests to:
    1. Extract tenant context
    2. Enforce per-tier quotas
    3. Inject tenant context into request state
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Extract tenant context
        ctx = extract_tenant_context(request)

        if ctx:
            # Enforce quotas
            if not check_quota(ctx):
                logger.warning(
                    "Quota exceeded: firm=%s tier=%s",
                    ctx.firm_id,
                    ctx.tier,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "code": "QUOTA_EXCEEDED",
                        "tier": ctx.tier,
                        "message": f"API call quota exceeded for {ctx.tier} tier. Upgrade to increase limits.",
                    },
                )

            # Inject context into request state
            request.state.tenant_ctx = ctx
            request.state.firm_id = ctx.firm_id
            request.state.tier = ctx.tier

        response = await call_next(request)

        # Add tenant headers for tracing
        if ctx:
            response.headers["X-Tenant-Tier"] = ctx.tier

        return response
