# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Rate Limiting Middleware

Prevents brute force attacks and API abuse

Security Features:
- Per-IP rate limiting
- Configurable limits (per minute, per hour)
- Returns 429 Too Many Requests on limit exceeded
"""

from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import get_settings

settings = get_settings()


class RateLimiter:
    """Simple in-memory rate limiter

    Note: For production with multiple instances, use Redis-based rate limiting
    """

    def __init__(self):
        # Storage: {ip: [(timestamp, count), ...]}
        self.requests: dict[str, list[tuple[datetime, int]]] = defaultdict(list)
        self.minute_limit = settings.RATE_LIMIT_PER_MINUTE
        self.hour_limit = settings.RATE_LIMIT_PER_HOUR

    def is_allowed(self, ip: str) -> tuple[bool, str]:
        """Check if request from IP is allowed

        Args:
            ip: Client IP address

        Returns:
            Tuple of (is_allowed, error_message)

        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        # Clean old entries
        self.requests[ip] = [(ts, count) for ts, count in self.requests[ip] if ts > hour_ago]

        # Count requests
        minute_count = sum(count for ts, count in self.requests[ip] if ts > minute_ago)
        hour_count = sum(count for ts, count in self.requests[ip])

        # Check limits
        if minute_count >= self.minute_limit:
            return False, f"Rate limit exceeded: {self.minute_limit} requests per minute"

        if hour_count >= self.hour_limit:
            return False, f"Rate limit exceeded: {self.hour_limit} requests per hour"

        # Add current request
        self.requests[ip].append((now, 1))

        return True, ""

    def cleanup(self):
        """Remove expired entries (call periodically)"""
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        for ip in list(self.requests.keys()):
            self.requests[ip] = [(ts, count) for ts, count in self.requests[ip] if ts > hour_ago]
            if not self.requests[ip]:
                del self.requests[ip]


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply rate limiting to all requests

    Security:
    - Prevents brute force attacks
    - Mitigates DoS attempts
    - Per-IP tracking
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        is_allowed, error_message = rate_limiter.is_allowed(client_ip)

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message,
                headers={"Retry-After": "60"},
            )

        response = await call_next(request)
        return response
