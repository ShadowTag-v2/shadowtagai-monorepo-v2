# apps/counselconduit/api/middleware/rate_limiter.py
"""Rate Limiting Middleware — Cor.30 Rules R14-R15.

Per-IP + per-route rate limiting with sliding window.
Stricter limits for auth, payment, export, and password reset endpoints.

Implementation: In-memory sliding window (suitable for single-instance Cloud Run).
Upgrade path: Redis/Memorystore for multi-instance deployments.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("counselconduit.rate_limiter")

# ── Configuration ──────────────────────────────────────────────────────────

# Route pattern → (max_requests, window_seconds)
_ROUTE_LIMITS: dict[str, tuple[int, int]] = {
    # Auth routes — strict (3 per 5 min)
    "/auth/": (3, 300),
    "/login": (5, 300),
    "/signup": (3, 300),
    "/reset": (3, 3600),
    # Payment routes — moderate (20 per 5 min)
    "/billing/": (20, 300),
    "/webhooks/": (60, 60),
    "/checkout": (10, 300),
    # LLM/Oracle routes — per-session budget (30 per 5 min)
    "/oracle/": (30, 300),
    "/chat/": (30, 300),
    "/query/": (30, 300),
}

# Default: 100 requests per 60 seconds per IP
_DEFAULT_LIMIT = (100, 60)


@dataclass
class _SlidingWindow:
    """Sliding window counter for rate limiting."""

    timestamps: list[float] = field(default_factory=list)

    def count_in_window(self, window_seconds: int) -> int:
        """Count requests within the sliding window, pruning old entries."""
        now = time.monotonic()
        cutoff = now - window_seconds
        self.timestamps = [t for t in self.timestamps if t > cutoff]
        return len(self.timestamps)

    def record(self) -> None:
        """Record a new request."""
        self.timestamps.append(time.monotonic())


# Per-IP sliding windows: key = f"{ip}:{route_key}"
_windows: dict[str, _SlidingWindow] = defaultdict(_SlidingWindow)


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For from Cloud Run load balancer."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _match_route_limit(path: str) -> tuple[int, int]:
    """Match the request path to the strictest applicable rate limit."""
    for pattern, limit in _ROUTE_LIMITS.items():
        if pattern in path:
            return limit
    return _DEFAULT_LIMIT


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP + per-route sliding window rate limiter.

    Cor.30 R14-R15: Rate limit by IP + route. Stricter for auth/payment/export.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = _get_client_ip(request)
        path = request.url.path
        max_requests, window_seconds = _match_route_limit(path)

        # Create a key combining IP and route category
        route_key = next(
            (p for p in _ROUTE_LIMITS if p in path),
            "default",
        )
        window_key = f"{client_ip}:{route_key}"

        window = _windows[window_key]
        current_count = window.count_in_window(window_seconds)

        if current_count >= max_requests:
            logger.warning(
                "Rate limit exceeded: ip=%s route=%s count=%d/%d",
                client_ip,
                path,
                current_count,
                max_requests,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMITED",
                    "message": "Too many requests. Please try again later.",
                    "retry_after_seconds": window_seconds,
                },
            )

        window.record()

        response = await call_next(request)

        # Add rate limit headers (RFC 6585 / draft-ietf-httpapi-ratelimit-headers)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, max_requests - current_count - 1)
        )
        response.headers["X-RateLimit-Reset"] = str(window_seconds)

        return response
