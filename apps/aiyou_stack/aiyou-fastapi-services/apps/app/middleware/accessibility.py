# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Accessibility middleware for adding WCAG-compliant HTTP headers.

This middleware adds headers that improve accessibility for:
- Screen readers
- Browser compatibility
- Content type detection
- Security (which also improves accessibility)
"""

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AccessibilityMiddleware(BaseHTTPMiddleware):
    """Add accessibility-related HTTP headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add accessibility headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with accessibility headers added

        """
        response = await call_next(request)

        # Security headers (also improve accessibility)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content type (important for assistive technology)
        if "content-type" not in response.headers:
            response.headers["Content-Type"] = "application/json; charset=utf-8"

        # Cache control for dynamic content
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response
