"""Token Budget Meter — Client Portal Component (#18).

FastAPI endpoint that returns token budget status as a visual meter.
Used by the client-facing portal to show remaining quota.
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Annotated

logger = logging.getLogger("counselconduit.token_meter")

router = APIRouter(tags=["client-portal"])


class TokenMeterResponse(BaseModel):
    """Token budget meter for client portal display."""

    firm_id: str
    tier: str
    budget_limit: int
    budget_used: int
    budget_remaining: int
    usage_pct: float
    status: str  # "ok" | "warning" | "critical" | "exhausted"
    reset_at: str  # ISO8601 — next daily reset
    warning_threshold_pct: float = 80.0
    critical_threshold_pct: float = 95.0


# Tier limits (tokens per day)
TIER_DAILY_LIMITS = {
    "trial": 10_000,
    "solo": 100_000,
    "professional": 500_000,
    "enterprise": 2_000_000,
}


@router.get(
    "/api/v1/token-meter",
    response_model=TokenMeterResponse,
    summary="Token budget meter for client portal",
    description="Returns current token consumption and remaining budget for display in the client portal.",
)
async def token_meter(
    firm_id: str,
    x_user_tier: Annotated[str, Header(alias="X-User-Tier")] = "trial",
) -> TokenMeterResponse:
    """Return token budget status for a firm."""
    limit = TIER_DAILY_LIMITS.get(x_user_tier, TIER_DAILY_LIMITS["trial"])

    # Try to read real usage from Firestore
    used = 0
    try:
        from google.cloud import firestore

        db = firestore.AsyncClient(project="shadowtag-omega-v4")
        doc = await db.collection("token_budgets").document(firm_id).get()
        if doc.exists:
            data = doc.to_dict()
            used = data.get("daily_tokens_used", 0)
    except Exception:
        logger.debug("Firestore unavailable, using in-memory fallback")

    remaining = max(0, limit - used)
    usage_pct = round((used / limit) * 100, 1) if limit > 0 else 0

    if usage_pct >= 100:
        status = "exhausted"
    elif usage_pct >= 95:
        status = "critical"
    elif usage_pct >= 80:
        status = "warning"
    else:
        status = "ok"

    # Calculate next daily reset (midnight UTC)
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    reset_at = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    return TokenMeterResponse(
        firm_id=firm_id,
        tier=x_user_tier,
        budget_limit=limit,
        budget_used=used,
        budget_remaining=remaining,
        usage_pct=usage_pct,
        status=status,
        reset_at=reset_at.isoformat(),
    )
