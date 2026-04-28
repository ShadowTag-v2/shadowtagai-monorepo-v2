# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Request logging middleware"""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all API requests"""

    async def dispatch(self, request: Request, call_next):
        """Log request and response"""
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} Duration: {duration:.3f}s",
        )

        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)

        return response
