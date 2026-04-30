"""Security middleware for FastAPI application."""

import time
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger()


class SandboxMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce sandboxing policies and track requests."""

    def __init__(
        self,
        app: ASGIApp,
        max_requests_per_minute: int = 60,
    ):
        super().__init__(app)
        self.max_requests_per_minute = max_requests_per_minute
        self.request_history: dict = {}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request through sandboxing middleware."""
        client_ip = request.client.host if request.client else "unknown"
        start_time = time.time()

        # Rate limiting
        if not self._check_rate_limit(client_ip):
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                path=request.url.path,
            )
            return Response(
                content="Rate limit exceeded",
                status_code=429,
            )

        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )

        try:
            response = await call_next(request)

            # Log response
            duration = time.time() - start_time
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
                client_ip=client_ip,
            )

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration=duration,
                client_ip=client_ip,
            )
            raise

    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit."""
        current_time = time.time()
        minute_ago = current_time - 60

        # Initialize or clean old requests
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []

        # Remove requests older than 1 minute
        self.request_history[client_ip] = [
            timestamp for timestamp in self.request_history[client_ip] if timestamp > minute_ago
        ]

        # Check rate limit
        if len(self.request_history[client_ip]) >= self.max_requests_per_minute:
            return False

        # Add current request
        self.request_history[client_ip].append(current_time)
        return True


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate and sanitize requests."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Validate request before processing."""
        # Validate content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            logger.warning(
                "request_too_large",
                content_length=content_length,
                path=request.url.path,
            )
            return Response(
                content="Request body too large",
                status_code=413,
            )

        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            allowed_types = [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
            ]
            if not any(ct in content_type for ct in allowed_types):
                logger.warning(
                    "invalid_content_type",
                    content_type=content_type,
                    path=request.url.path,
                )
                return Response(
                    content="Invalid content type",
                    status_code=415,
                )

        return await call_next(request)
