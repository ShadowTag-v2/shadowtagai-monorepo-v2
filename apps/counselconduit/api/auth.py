# apps/counselconduit/api/auth.py
"""Firebase Auth JWT Verification for CounselConduit.

Verifies Firebase ID tokens from the KovelAI frontend.
Extracts attorney UID and email for request context.

Flow:
    1. Client sends Firebase ID token in X-Kovel-Auth header
    2. This module verifies signature + expiry against Firebase
    3. Returns decoded claims (uid, email, etc.)
    4. FastAPI dependency injection wires this into routes
"""

from __future__ import annotations

import logging
import os
from typing import Any

import firebase_admin
from fastapi import Header, HTTPException, status
from firebase_admin import auth, credentials

logger = logging.getLogger("counselconduit.auth")

_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_APP_INITIALIZED = False


def _ensure_firebase_app() -> None:
    """Initialize Firebase Admin SDK (idempotent)."""
    global _APP_INITIALIZED  # noqa: PLW0603
    if _APP_INITIALIZED:
        return

    try:
        firebase_admin.get_app()
    except ValueError:
        # No app exists — initialize with ADC
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"projectId": _PROJECT_ID})
        else:
            # Use Application Default Credentials (Cloud Run, local gcloud)
            firebase_admin.initialize_app(options={"projectId": _PROJECT_ID})
        logger.info("Firebase Admin SDK initialized: project=%s", _PROJECT_ID)

    _APP_INITIALIZED = True


def verify_firebase_token(id_token: str) -> dict[str, Any]:
    """Verify a Firebase ID token and return decoded claims.

    Args:
        id_token: The Firebase ID token from the client.

    Returns:
        Decoded token claims including uid, email, etc.

    Raises:
        HTTPException(401): Token is invalid, expired, or revoked.
    """
    _ensure_firebase_app()

    try:
        decoded = auth.verify_id_token(id_token, check_revoked=True)
        return decoded
    except auth.RevokedIdTokenError:
        logger.warning("Revoked Firebase token presented")
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please re-authenticate.",
        )
    except auth.InvalidIdTokenError as e:
        logger.warning("Invalid Firebase token: %s", e)
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
    except auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase token")
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please re-authenticate.",
        )
    except Exception as e:
        logger.error("Firebase auth error: %s", e)
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error.",
        )


async def get_current_attorney(x_kovel_auth: str = Header(None)) -> dict[str, Any]:
    """FastAPI dependency: Extract and verify attorney from request header.

    Usage in routes:
        @app.post("/endpoint")
        async def handler(attorney: dict = Depends(get_current_attorney)):
            uid = attorney["uid"]
    """
    if not x_kovel_auth:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kovel Authentication Missing. Operation Terminated.",
        )

    # Development mode bypass
    if os.getenv("APP_ENV") == "development" and x_kovel_auth.startswith("dev_"):
        return {
            "uid": x_kovel_auth,
            "email": "dev@kovelai.test",
            "name": "Development Attorney",
        }

    claims = verify_firebase_token(x_kovel_auth)
    return {
        "uid": claims.get("uid", ""),
        "email": claims.get("email", ""),
        "name": claims.get("name", ""),
        "email_verified": claims.get("email_verified", False),
    }
