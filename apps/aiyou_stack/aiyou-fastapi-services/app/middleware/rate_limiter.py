"""Rate limiting middleware for API protection"""

import time
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.settings import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent API abuse
    Supports TurboAPI configuration for high RPS
    """

    def __init__(self, app):
        super().__init__(app)
        self.request_counts = defaultdict(list)
        self.max_requests = settings.MAX_REQUESTS_PER_MINUTE
        self.turbo_max_rps = settings.TURBO_API_MAX_RPS

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Get client identifier (IP address)
        client_ip = request.client.host

        # Get current time
        current_time = time.time()

        # Clean old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip] if current_time - req_time < 60
        ]

        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "max_requests": self.max_requests,
                    "period": "1 minute",
                },
            )

        # Add current request
        self.request_counts[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.max_requests - len(self.request_counts[client_ip]))
        )

        return response
