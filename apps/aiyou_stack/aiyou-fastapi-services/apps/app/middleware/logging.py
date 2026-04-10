"""
Logging middleware for request/response tracking.

Provides:
- Unique request IDs for tracing
- Request/response logging
- Performance monitoring
- Error tracking
"""

import logging
import time
import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses with correlation IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with logging and timing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with request ID header added
        """
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log incoming request
        start_time = time.time()
        logger.info(
            f"REQUEST | {request_id} | {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            logger.error(
                f"ERROR | {request_id} | {str(e)}",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True,
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"RESPONSE | {request_id} | {response.status_code} | {process_time:.3f}s",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time,
            },
        )

        # Add request ID to response headers for debugging
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response
