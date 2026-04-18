# apps/counselconduit/api/middleware/__init__.py
"""CounselConduit middleware package.

Includes:
- RateLimitMiddleware: IP-based rate limiting
- SecurityHeadersMiddleware: CSP, HSTS, X-Frame-Options, etc.
- attorney_rate_limit: per-attorney sliding window rate limiter
"""

from __future__ import annotations

import logging
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("counselconduit.middleware")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP-based rate limiting middleware.

    Uses an in-memory sliding window (per-pod).
    For production at scale, replace with Redis/Memorystore.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rpm = requests_per_minute
        self._windows: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean + check window
        window = self._windows.get(client_ip, [])
        window = [t for t in window if now - t < 60]
        self._windows[client_ip] = window

        if len(window) >= self.rpm:
            return JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": "60"},
            )

        window.append(now)
        self._windows[client_ip] = window
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses (Cor.30 R31)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://js.stripe.com; "
            "frame-src https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' https://api.stripe.com https://counselconduit-*.run.app; "
            "img-src 'self' data:; "
        )
        # HSTS (only in production)
        import os

        if os.getenv("APP_ENV") != "development":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        return response
