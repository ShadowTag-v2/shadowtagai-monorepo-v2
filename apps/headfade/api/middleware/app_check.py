"""
Firebase App Check enforcement middleware.

Validates the X-Firebase-AppCheck header on all /api/* routes when
HEADFADE_APPCHECK_ENFORCED=true. Graceful degradation: when enforcement
is disabled (default in dev), requests without tokens pass through.

See: https://firebase.google.com/docs/app-check/custom-resource-backend
"""

import logging
import os

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("headfade.appcheck")

_ENFORCE = os.environ.get("HEADFADE_APPCHECK_ENFORCED", "false").lower() == "true"
_EXEMPT_PATHS = frozenset(
  {"/health", "/api/health", "/docs", "/openapi.json", "/redoc"}
)


async def app_check_middleware(request: Request, call_next):
  """Verify Firebase App Check tokens for /api/* endpoints.

  In production, HEADFADE_APPCHECK_ENFORCED=true rejects requests
  without valid App Check tokens. In development, requests pass
  through with a warning log.
  """
  path = request.url.path

  # Skip enforcement for health checks, docs, and non-API paths
  if path in _EXEMPT_PATHS or not path.startswith("/api"):
    return await call_next(request)

  token = request.headers.get("X-Firebase-AppCheck")

  if not token:
    if _ENFORCE:
      logger.warning(
        "App Check: missing token on %s from %s",
        path,
        request.client.host if request.client else "unknown",
      )
      return JSONResponse(
        status_code=401,
        content={
          "detail": "Missing App Check token. Enable Firebase App Check in your client."
        },
      )
    # Dev mode: allow through but log
    logger.debug("App Check: token not provided (enforcement disabled)")
    return await call_next(request)

  # Verify the token using Firebase Admin SDK
  try:
    import firebase_admin.app_check

    decoded = firebase_admin.app_check.verify_token(token)
    # Attach the decoded claims to request state for downstream use
    request.state.app_check_claims = decoded
    logger.debug("App Check: verified for app=%s", decoded.get("sub", "unknown"))

  except ImportError:
    # firebase_admin.app_check may not be available in older SDK versions
    logger.warning(
      "App Check: firebase_admin.app_check not available, skipping verification"
    )

  except Exception as e:
    if _ENFORCE:
      logger.warning("App Check: verification failed — %s", e)
      return JSONResponse(
        status_code=401,
        content={"detail": "Invalid App Check token."},
      )
    logger.debug("App Check: verification failed (enforcement disabled) — %s", e)

  return await call_next(request)
