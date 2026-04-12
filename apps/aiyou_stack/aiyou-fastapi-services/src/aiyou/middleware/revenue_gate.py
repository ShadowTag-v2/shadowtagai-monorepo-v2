"""Revenue Gate Middleware

Enforces "No Pay, No AI" rule. All AI endpoints require payment verification.
Returns 402 Payment Required for unpaid requests.
"""

import logging
from collections.abc import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RevenueGateMiddleware(BaseHTTPMiddleware):
    """Middleware that blocks unpaid requests to AI endpoints."""

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled

        # Endpoints that require payment
        self.protected_paths = [
            "/api/v1/ai/",
            "/api/v1/gemini/",
            "/verify/video",
            "/api/v1/shadowtag/analyze",
        ]

        # Endpoints that are always free
        self.free_paths = [
            "/health",
            "/status",
            "/docs",
            "/openapi.json",
            "/revenue/ingest",  # Revenue recording is always allowed
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        """Check payment status before allowing request."""

        if not self.enabled:
            return await call_next(request)

        # Allow free endpoints
        if any(request.url.path.startswith(path) for path in self.free_paths):
            return await call_next(request)

        # Check if this is a protected endpoint
        is_protected = any(request.url.path.startswith(path) for path in self.protected_paths)

        if is_protected:
            # Check for payment verification header
            paid_header = request.headers.get("X-User-Paid")
            stripe_session = request.headers.get("X-Stripe-Session-ID")

            if not paid_header and not stripe_session:
                logger.warning(f"Unpaid request blocked: {request.url.path}")
                raise HTTPException(
                    status_code=402,
                    detail="Payment required. Please purchase credits at /api/v1/billing/checkout",
                )

            # TODO: Validate Stripe session ID against Stripe API
            # For now, trust the header (replace with real validation in prod)
            if stripe_session:
                logger.info(f"Paid request authorized: {stripe_session}")

        return await call_next(request)
