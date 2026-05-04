# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Admin Auth Gate — Risk #58 Mitigation.

Provides middleware-style authentication verification for admin endpoints.
Implements zero-trust verification via Firebase ID token validation.

Architecture:
  - Extracts Bearer token from Authorization header
  - Verifies token against Firebase Auth (or mock in tests)
  - Checks admin claim in custom claims
  - Returns 401/403 on failure, passes through on success

Usage in FastAPI:
    from admin_auth_gate import verify_admin_auth, AdminClaim

    @app.get("/admin/dashboard")
    async def dashboard(claim: AdminClaim = Depends(verify_admin_auth)):
        return {"admin": claim.uid}
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

logger = logging.getLogger(__name__)


# ── Types ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AdminClaim:
    """Verified admin identity from a Firebase ID token."""

    uid: str
    email: str
    is_admin: bool = False
    custom_claims: dict[str, Any] | None = None


class TokenVerifier(Protocol):
    """Protocol for pluggable token verification backends."""

    def verify_id_token(self, token: str) -> dict[str, Any]:
        """Verify a Firebase ID token and return its decoded claims."""
        ...


# ── Errors ─────────────────────────────────────────────────────────────────


class AuthError(Exception):
    """Base authentication error."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class MissingTokenError(AuthError):
    """No Bearer token provided."""

    def __init__(self) -> None:
        super().__init__("Missing or malformed Authorization header", 401)


class InvalidTokenError(AuthError):
    """Token failed verification."""

    def __init__(self, detail: str = "") -> None:
        msg = f"Invalid or expired token{f': {detail}' if detail else ''}"
        super().__init__(msg, 401)


class InsufficientPrivilegesError(AuthError):
    """Token valid but lacks admin claim."""

    def __init__(self) -> None:
        super().__init__("Insufficient privileges: admin claim required", 403)


# ── Core Gate ──────────────────────────────────────────────────────────────


def extract_bearer_token(authorization: str | None) -> str:
    """Extract the token from 'Bearer <token>' format.

    Raises:
        MissingTokenError: If header is missing or malformed.
    """
    if not authorization:
        raise MissingTokenError()
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise MissingTokenError()
    return parts[1]


def verify_admin_claim(
    token: str,
    *,
    verifier: TokenVerifier | None = None,
    admin_claim_key: str = "admin",
) -> AdminClaim:
    """Verify a Firebase ID token and check for admin claim.

    Args:
        token: The raw ID token string.
        verifier: Optional custom verifier (for testing). If None, uses
                  firebase_admin.auth.verify_id_token.
        admin_claim_key: The custom claim key that indicates admin status.
                        Defaults to "admin".

    Returns:
        AdminClaim with verified identity.

    Raises:
        InvalidTokenError: Token verification failed.
        InsufficientPrivilegesError: Token valid but no admin claim.
    """
    # Resolve verifier
    if verifier is None:
        try:
            import firebase_admin.auth as firebase_auth

            decoded = firebase_auth.verify_id_token(token)
        except ImportError:
            raise InvalidTokenError("firebase_admin not available") from None
        except Exception as exc:
            raise InvalidTokenError(str(exc)) from exc
    else:
        try:
            decoded = verifier.verify_id_token(token)
        except Exception as exc:
            raise InvalidTokenError(str(exc)) from exc

    # Extract identity
    uid = decoded.get("uid", decoded.get("sub", ""))
    email = decoded.get("email", "")
    custom_claims = decoded.get("custom_claims", {})

    # Check admin claim — it can be at the top level or in custom_claims
    is_admin = bool(decoded.get(admin_claim_key) or (isinstance(custom_claims, dict) and custom_claims.get(admin_claim_key)))

    if not is_admin:
        logger.warning(
            "Admin auth gate: access denied for uid=%s email=%s (missing '%s' claim)",
            uid,
            email,
            admin_claim_key,
        )
        raise InsufficientPrivilegesError()

    logger.info("Admin auth gate: access granted for uid=%s email=%s", uid, email)
    return AdminClaim(
        uid=uid,
        email=email,
        is_admin=True,
        custom_claims=custom_claims if isinstance(custom_claims, dict) else None,
    )


def gate_admin_request(
    authorization: str | None,
    *,
    verifier: TokenVerifier | None = None,
    admin_claim_key: str = "admin",
) -> AdminClaim:
    """Full pipeline: extract token → verify → check admin claim.

    This is the single function to call from endpoint handlers.

    Args:
        authorization: The full Authorization header value.
        verifier: Optional custom token verifier.
        admin_claim_key: Custom claim key for admin status.

    Returns:
        AdminClaim on success.

    Raises:
        MissingTokenError: No token provided.
        InvalidTokenError: Token invalid.
        InsufficientPrivilegesError: Not an admin.
    """
    token = extract_bearer_token(authorization)
    return verify_admin_claim(token, verifier=verifier, admin_claim_key=admin_claim_key)


__all__ = [
    "AdminClaim",
    "AuthError",
    "InsufficientPrivilegesError",
    "InvalidTokenError",
    "MissingTokenError",
    "TokenVerifier",
    "extract_bearer_token",
    "gate_admin_request",
    "verify_admin_claim",
]
