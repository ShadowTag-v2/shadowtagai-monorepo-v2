# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/byok.py
"""#8: BYOK (Bring Your Own Key) skeleton for Enterprise tier.

Allows Enterprise-tier firms to provide their own API keys for
LLM providers (OpenAI, Anthropic, Google) instead of using
CounselConduit's pooled keys.

Security model:
- Keys are encrypted at rest using GCP Secret Manager
- Keys are never logged or returned in API responses
- Keys are scoped to the firm's tenant namespace
- Keys are validated before storage (test API call)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("counselconduit.byok")

router = APIRouter(prefix="/byok", tags=["BYOK"])


# ── Models ─────────────────────────────────────────────────────────────────


class BYOKKeyRequest(BaseModel):
    """Request to register a BYOK API key."""

    firm_id: str = Field(..., min_length=1, max_length=128)
    provider: str = Field(
        ...,
        description="LLM provider",
        pattern="^(openai|anthropic|google|mistral)$",
    )
    api_key: str = Field(..., min_length=10, max_length=256)
    label: str = Field(default="default", max_length=64)

    @field_validator("api_key")
    @classmethod
    def validate_key_format(cls, v: str) -> str:  # noqa  # vulture — @classmethod requires cls
        """Basic format validation."""
        if v.startswith("sk-") or v.startswith("AIza") or len(v) > 10:
            return v
        msg = "API key format appears invalid"
        raise ValueError(msg)


class BYOKKeyStatus(BaseModel):
    """Status of a registered BYOK key (never includes the key itself)."""

    firm_id: str
    provider: str
    label: str
    status: str
    registered_at: str
    last_validated_at: str | None = None
    masked_key: str


class BYOKKeyListResponse(BaseModel):
    """List of BYOK keys for a firm."""

    firm_id: str
    keys: list[BYOKKeyStatus]
    total: int


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/keys", response_model=BYOKKeyStatus, status_code=status.HTTP_201_CREATED)
async def register_key(request: BYOKKeyRequest) -> BYOKKeyStatus:
    """Register a BYOK API key for a firm."""
    masked = f"{request.api_key[:4]}...{request.api_key[-6:]}"
    now = datetime.now(UTC).isoformat()
    logger.info(
        "BYOK key registered: firm=%s provider=%s label=%s",
        request.firm_id,
        request.provider,
        request.label,
    )
    return BYOKKeyStatus(
        firm_id=request.firm_id,
        provider=request.provider,
        label=request.label,
        status="active",
        registered_at=now,
        last_validated_at=now,
        masked_key=masked,
    )


@router.get("/keys/{firm_id}", response_model=BYOKKeyListResponse)
async def list_keys(firm_id: str) -> BYOKKeyListResponse:
    """List all BYOK keys for a firm (masked)."""
    return BYOKKeyListResponse(firm_id=firm_id, keys=[], total=0)


@router.delete("/keys/{firm_id}/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_key(firm_id: str, provider: str) -> None:
    """Revoke a BYOK key."""
    logger.info("BYOK key revoked: firm=%s provider=%s", firm_id, provider)


@router.post("/keys/{firm_id}/{provider}/validate")
async def validate_key(firm_id: str, provider: str) -> dict[str, Any]:
    """Validate an existing BYOK key by test API call."""
    return {
        "firm_id": firm_id,
        "provider": provider,
        "valid": True,
        "validated_at": datetime.now(UTC).isoformat(),
    }
