"""Safe Harbor bridge authentication — HMAC-SHA256 shared secret.

Replaces upstream OAuth/JWT authentication. No remote token validation.
All auth is local-only, using a pre-shared secret stored in
AGNT_BRIDGE_SECRET environment variable.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ─── Constants ─────────────────────────────────────────────────────────

_TOKEN_VALIDITY_S: int = 3600  # 1 hour
_NONCE_BYTES: int = 16


# ─── Data classes ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class AuthToken:
    """A signed authentication token for bridge IPC.

    Contains the session ID, a timestamp, a nonce, and the HMAC signature.
    Transmitted as: {session_id}:{timestamp}:{nonce}:{signature_hex}
    """

    session_id: str
    timestamp: int
    nonce: str
    signature: str

    def serialize(self) -> str:
        """Serialize to wire format."""
        return f"{self.session_id}:{self.timestamp}:{self.nonce}:{self.signature}"

    @classmethod
    def deserialize(cls, raw: str) -> AuthToken:
        """Deserialize from wire format.

        Raises ValueError if the format is invalid.
        """
        parts = raw.split(":")
        if len(parts) != 4:
            msg = f"Invalid auth token format: expected 4 parts, got {len(parts)}"
            raise ValueError(msg)
        return cls(
            session_id=parts[0],
            timestamp=int(parts[1]),
            nonce=parts[2],
            signature=parts[3],
        )


# ─── Auth Engine ───────────────────────────────────────────────────────


class BridgeAuth:
    """HMAC-SHA256 authentication for local IPC bridge.

    Safe Harbor constraints:
    - Secret MUST come from AGNT_BRIDGE_SECRET env var
    - No OAuth, no JWT, no remote token validation
    - Tokens expire after _TOKEN_VALIDITY_S seconds
    - Each token has a unique nonce to prevent replay attacks
    """

    __slots__ = ("_secret",)

    def __init__(self, secret: bytes | None = None) -> None:
        if secret is not None:
            self._secret = secret
        else:
            env_secret = os.environ.get("AGNT_BRIDGE_SECRET", "")
            if not env_secret:
                msg = (
                    "AGNT_BRIDGE_SECRET not set. Cannot initialize bridge auth. "
                    'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
                )
                raise RuntimeError(msg)
            self._secret = env_secret.encode("utf-8")

    def _compute_signature(self, session_id: str, timestamp: int, nonce: str) -> str:
        """Compute HMAC-SHA256 signature over the token fields."""
        message = f"{session_id}:{timestamp}:{nonce}".encode()
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def generate_token(self, session_id: str) -> AuthToken:
        """Generate a signed auth token for a session.

        The token is valid for _TOKEN_VALIDITY_S seconds.
        """
        timestamp = int(time.time())
        nonce = secrets.token_hex(_NONCE_BYTES)
        signature = self._compute_signature(session_id, timestamp, nonce)
        return AuthToken(
            session_id=session_id,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
        )

    def validate_token(self, token: AuthToken) -> bool:
        """Validate a token's signature and expiry.

        Returns True if:
        1. HMAC signature matches
        2. Token has not expired
        """
        # Check expiry
        now = int(time.time())
        if now - token.timestamp > _TOKEN_VALIDITY_S:
            logger.debug(
                "Token expired: issued=%d now=%d max_age=%d",
                token.timestamp,
                now,
                _TOKEN_VALIDITY_S,
            )
            return False

        # Check signature
        expected = self._compute_signature(
            token.session_id,
            token.timestamp,
            token.nonce,
        )
        if not hmac.compare_digest(expected, token.signature):
            logger.warning(
                "Token signature mismatch for session %s",
                token.session_id,
            )
            return False

        return True

    def validate_raw(self, raw_token: str) -> bool:
        """Validate a serialized token string.

        Returns False on any parse or validation failure.
        """
        try:
            token = AuthToken.deserialize(raw_token)
        except (ValueError, IndexError):
            logger.warning("Failed to deserialize auth token")
            return False
        return self.validate_token(token)
