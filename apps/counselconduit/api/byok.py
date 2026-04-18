# apps/counselconduit/api/byok.py
"""BYOK — Bring Your Own Key for Enterprise Firms.

Enterprise firms can use their own API keys for LLM providers,
bypassing our proxy layer. Benefits:
- Direct billing from firm to provider
- Custom rate limits and model access
- Data residency compliance (firm chooses region)

Security:
- Keys are encrypted at rest (GCP Secret Manager)
- Keys are NEVER logged, returned in responses, or stored in Firestore
- Keys are injected into ephemeral sandbox-bound tokens per session
- Keys are scoped to the firm's tenant namespace
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.byok")

router = APIRouter(prefix="/byok", tags=["BYOK"])


# ── Models ─────────────────────────────────────────────────────────────────


class BYOKProviderConfig(BaseModel):
    """Configuration for a BYOK provider."""

    provider: str = Field(..., pattern="^(gemini|claude|openai|grok|perplexity)$")
    api_key: str = Field(..., min_length=10, max_length=200)
    region: str = Field(default="us-central1", description="Preferred API region")
    model_id: str | None = Field(None, description="Override default model ID")


class BYOKSetupRequest(BaseModel):
    """Enterprise firm configures BYOK providers."""

    firm_id: str
    providers: list[BYOKProviderConfig] = Field(..., max_length=5)


class BYOKStatus(BaseModel):
    """Status of BYOK configuration for a firm."""

    firm_id: str
    configured_providers: list[str]
    is_active: bool
    last_rotated: str | None = None


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/configure", response_model=BYOKStatus)
async def configure_byok(req: BYOKSetupRequest) -> BYOKStatus:
    """Configure BYOK providers for an enterprise firm.

    Keys are validated, encrypted, and stored in GCP Secret Manager.
    They are NEVER returned in any API response after this call.
    """
    # TODO: Validate each key by making a test call to the provider
    # TODO: Encrypt and store in GCP Secret Manager
    # TODO: Update firm record in Firestore with BYOK flag

    configured = [p.provider for p in req.providers]

    logger.info(
        "BYOK configured: firm=%s providers=%s",
        req.firm_id,
        configured,
    )

    return BYOKStatus(
        firm_id=req.firm_id,
        configured_providers=configured,
        is_active=True,
    )


@router.get("/status/{firm_id}", response_model=BYOKStatus)
async def get_byok_status(firm_id: str) -> BYOKStatus:
    """Check BYOK configuration status for a firm.

    Returns which providers are configured (but NEVER the keys themselves).
    """
    # TODO: Query GCP Secret Manager for configured providers
    return BYOKStatus(
        firm_id=firm_id,
        configured_providers=[],
        is_active=False,
    )


@router.post("/rotate/{firm_id}")
async def rotate_byok_keys(firm_id: str) -> dict[str, Any]:
    """Trigger key rotation for a firm's BYOK configuration.

    The firm must provide new keys within 24 hours or the
    BYOK config is disabled and traffic falls back to our proxy.
    """
    # TODO: Mark current keys as pending-rotation in Secret Manager
    # TODO: Send email to firm admin with rotation instructions

    return {
        "firm_id": firm_id,
        "status": "rotation_initiated",
        "message": "Please provide new API keys within 24 hours.",
    }
