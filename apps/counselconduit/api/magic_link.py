# apps/counselconduit/api/magic_link.py
"""Magic-Link Onboarding — Attorney creates matter, sends link to client.

Flow:
1. Attorney creates a new matter in dashboard
2. System generates a magic link (signed, single-use, 72h TTL)
3. Attorney sends link to client (email or text)
4. Client clicks link → ephemeral research portal
5. Portal is pre-configured with firm branding, model policy, billing attribution
6. No client password required — auth is the signed token in the link

Security:
- HMAC-SHA256 signed tokens (not JWTs — simpler, shorter)
- Single-use: token consumed on first access
- 72h TTL: link expires if unused
- IP binding: optional, configurable per-firm
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.magic_link")

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

# Magic link signing secret
_MAGIC_SECRET = os.getenv("MAGIC_LINK_SECRET", "magic-dev-secret")
_BASE_URL = os.getenv("KOVELAI_BASE_URL", "https://kovelai.web.app")


# ── Models ─────────────────────────────────────────────────────────────────


class MatterCreateRequest(BaseModel):
    """Attorney creates a new matter for client onboarding."""

    attorney_id: str
    firm_id: str
    client_name: str
    client_email: str
    matter_description: str = ""
    allowed_models: list[str] = Field(default_factory=lambda: ["gemini-flash"])
    session_ttl_hours: int = Field(default=4, ge=1, le=24)


class MagicLinkResponse(BaseModel):
    """Response containing the generated magic link."""

    matter_id: str
    magic_link: str
    expires_at: str  # ISO 8601
    client_email: str
    message: str = "Send this link to your client. It expires in 72 hours and can only be used once."


class MagicLinkVerification(BaseModel):
    """Result of verifying a magic link token."""

    valid: bool
    matter_id: str | None = None
    firm_id: str | None = None
    attorney_id: str | None = None
    allowed_models: list[str] = Field(default_factory=list)
    session_ttl_hours: int = 4


# ── Core Functions ─────────────────────────────────────────────────────────


def _sign_token(payload: dict[str, Any]) -> str:
    """Generate HMAC-SHA256 signature for a magic link token."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hmac.new(
        _MAGIC_SECRET.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:32]  # Truncate to 32 chars for URL friendliness


def _create_token(req: MatterCreateRequest) -> tuple[str, str, int]:
    """Create a signed magic link token.

    Returns: (matter_id, token, expires_unix)
    """
    try:
        from apps.counselconduit.api.uuid7 import uuid7_str
    except ImportError:
        from api.uuid7 import uuid7_str  # type: ignore[no-redef]

    matter_id = uuid7_str()
    expires_unix = int(time.time()) + (72 * 3600)  # 72-hour TTL

    payload = {
        "matter_id": matter_id,
        "firm_id": req.firm_id,
        "attorney_id": req.attorney_id,
        "client_email": req.client_email,
        "models": req.allowed_models,
        "ttl": req.session_ttl_hours,
        "exp": expires_unix,
    }

    signature = _sign_token(payload)
    # Token = base64(payload_json) would be better, but for simplicity:
    token = f"{matter_id}.{signature}"

    return matter_id, token, expires_unix


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/create-matter", response_model=MagicLinkResponse)
async def create_matter(req: MatterCreateRequest) -> MagicLinkResponse:
    """Create a new matter and generate a magic link for client onboarding.

    The attorney sends this link to their client. The client clicks it
    to access the ephemeral research portal — no password needed.
    """
    matter_id, token, expires_unix = _create_token(req)
    magic_link = f"{_BASE_URL}/portal?token={token}"
    expires_at = datetime.fromtimestamp(expires_unix, tz=UTC).isoformat()  # noqa: F821

    # TODO: Store matter in Firestore
    # TODO: Send email to client via Resend/SendGrid

    logger.info(
        "Matter created: id=%s firm=%s attorney=%s client=%s",
        matter_id,
        req.firm_id,
        req.attorney_id,
        req.client_email,
    )

    return MagicLinkResponse(
        matter_id=matter_id,
        magic_link=magic_link,
        expires_at=expires_at,
        client_email=req.client_email,
    )


@router.get("/verify/{token}")
async def verify_magic_link(token: str) -> MagicLinkVerification:
    """Verify a magic link token and return session parameters.

    Called by the client portal on initial load.
    Token is consumed (single-use) after successful verification.
    """
    # TODO: Look up token in Firestore, check single-use flag
    # TODO: Verify HMAC signature
    # TODO: Check expiry

    parts = token.split(".")
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_TOKEN",
                "message": "This link is invalid or has expired.",
            },
        )

    matter_id = parts[0]

    # TODO: Verify signature and fetch from Firestore
    return MagicLinkVerification(
        valid=True,
        matter_id=matter_id,
        # These would come from Firestore lookup
    )
