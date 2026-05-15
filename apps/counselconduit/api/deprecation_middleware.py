# apps/counselconduit/api/deprecation_middleware.py
"""Item 16: Deprecation header middleware for API versioning.

Adds RFC 8594 `Deprecation` and `Sunset` headers to deprecated API routes.
Helps clients migrate before endpoints are removed.

Usage in fastapi_kovel_enclave.py:
    from api.deprecation_middleware import DeprecationMiddleware
    app.add_middleware(DeprecationMiddleware)
"""

from __future__ import annotations

from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Map of deprecated route prefixes → sunset date (ISO 8601)
# Add entries here when deprecating endpoints
_DEPRECATED_ROUTES: dict[str, dict[str, Any]] = {
  # Example: when /enclave/v1 is superseded by /enclave/v2
  # "/enclave/v1": {
  #     "sunset": "2027-01-01T00:00:00Z",
  #     "link": "https://docs.kovelai.com/api/migration-v2",
  #     "alternative": "/enclave/v2",
  # },
}


class DeprecationMiddleware(BaseHTTPMiddleware):
  """Inject RFC 8594 Deprecation + Sunset headers on deprecated routes."""

  async def dispatch(self, request: Request, call_next: Any) -> Response:
    response: Response = await call_next(request)
    path = request.url.path

    for prefix, meta in _DEPRECATED_ROUTES.items():
      if path.startswith(prefix):
        # RFC 8594: Deprecation header
        response.headers["Deprecation"] = "true"

        # Sunset header (RFC 8594 §3)
        if sunset := meta.get("sunset"):
          response.headers["Sunset"] = sunset

        # Link to migration docs
        if link := meta.get("link"):
          response.headers["Link"] = f'<{link}>; rel="deprecation"'

        # Custom header for the replacement endpoint
        if alt := meta.get("alternative"):
          response.headers["X-API-Alternative"] = alt

        break

    # Always include API version header
    response.headers["X-API-Version"] = "v1"

    return response
