# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Security middleware — rate limiting, request validation, and security headers.

Provides the three middleware classes expected by test_security_middleware.py.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to every response."""

    SECURITY_HEADERS: dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        response = await call_next(request)
        for header, value in self.SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter by client IP."""

    def __init__(self, app: Any, max_requests: int = 100, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        self._requests[client_ip] = [t for t in self._requests[client_ip] if t > window_start]
        if len(self._requests[client_ip]) >= self.max_requests:
            return True
        self._requests[client_ip].append(now)
        return False

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        client_ip = self._get_client_ip(request)
        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
            )
        return await call_next(request)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming requests for common security issues."""

    MAX_CONTENT_LENGTH: int = 10 * 1024 * 1024  # 10 MB

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_CONTENT_LENGTH:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request entity too large"},
            )
        return await call_next(request)


__all__ = [
    "RateLimitMiddleware",
    "RequestValidationMiddleware",
    "SecurityHeadersMiddleware",
]
