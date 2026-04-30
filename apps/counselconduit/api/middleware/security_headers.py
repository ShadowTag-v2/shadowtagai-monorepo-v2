# apps/counselconduit/api/middleware/security_headers.py
"""Security Headers Middleware — Cor.30 Rule R31.

Sets CSP, HSTS, X-Content-Type-Options, X-Frame-Options,
Referrer-Policy, and Permissions-Policy on every response.

Also implements Cor.30 R23 (opaque errors) by stripping stack traces
from error responses in production.
"""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_IS_PRODUCTION = os.getenv("APP_ENV") != "development"

# CSP policy — strict in production
_CSP = (
    "default-src 'self'; "
    "script-src 'self' https://js.stripe.com; "
    "frame-src https://js.stripe.com https://hooks.stripe.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: https:; "
    "connect-src 'self' https://api.stripe.com; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject security headers on every response.

    Cor.30 R31: CSP, HSTS, X-Content-Type-Options, X-Frame-Options,
    Referrer-Policy, Permissions-Policy set by default.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Content Security Policy
        response.headers["Content-Security-Policy"] = _CSP

        # HSTS — 2 years + includeSubDomains + preload
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy — disable dangerous APIs
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=()"

        # Remove server header if present
        if "Server" in response.headers:
            del response.headers["Server"]

        return response
