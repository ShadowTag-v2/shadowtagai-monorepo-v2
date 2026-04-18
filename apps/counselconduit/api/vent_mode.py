# apps/counselconduit/api/vent_mode.py
"""Vent Mode — Flat-Fee Intake Retainer.

The "Vent" is the first touchpoint: client pays a flat fee ($50-250)
for a structured intake session where they can describe their problem
in natural language. The AI:

1. Listens and validates ("I hear you")
2. Identifies legal issues from the narrative
3. Suggests which practice areas are relevant
4. Generates a structured intake summary for the attorney
5. Triggers the magic-link for the full Oracle Studio

Billing: Flat-fee via Stripe Checkout (one-time, not subscription).
The fee goes directly to the attorney's Stripe Connect account.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.vent_mode")

router = APIRouter(prefix="/vent", tags=["Vent Mode"])


# ── Models ─────────────────────────────────────────────────────────────────

class VentSessionRequest(BaseModel):
    """Client starts a Vent Mode intake session."""
    firm_id: str
    attorney_id: str
    client_name: str
    client_email: str
    fee_amount_cents: int = Field(default=5000, ge=2500, le=25000)  # $25-$250


class VentMessage(BaseModel):
    """Client message in a Vent session."""
    session_id: str
    message: str = Field(..., min_length=1, max_length=5000)


class VentIntakeSummary(BaseModel):
    """AI-generated intake summary from Vent session."""
    session_id: str
    client_narrative: str  # anonymized summary
    identified_issues: list[str]
    suggested_practice_areas: list[str]
    urgency_level: str  # low, medium, high, critical
    recommended_next_step: str
    estimated_complexity: str  # simple, moderate, complex


class VentCheckoutResponse(BaseModel):
    """Stripe Checkout session for Vent intake fee."""
    checkout_url: str
    session_id: str
    amount_display: str  # e.g., "$50.00"


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/start", response_model=VentCheckoutResponse)
async def start_vent_session(req: VentSessionRequest) -> VentCheckoutResponse:
    """Start a Vent Mode intake session.

    Creates a Stripe Checkout session for the flat intake fee.
    The fee goes to the attorney's Stripe Connect account.
    After payment, client is redirected to the Vent chat interface.
    """
    from apps.counselconduit.api.uuid7 import uuid7_str

    session_id = uuid7_str()

    # TODO: Create Stripe Checkout session with Connect destination
    # TODO: Store session in Firestore with status=pending_payment

    checkout_url = f"https://checkout.stripe.com/pay/placeholder_{session_id}"

    logger.info(
        "Vent session started: id=%s firm=%s fee=%d",
        session_id,
        req.firm_id,
        req.fee_amount_cents,
    )

    return VentCheckoutResponse(
        checkout_url=checkout_url,
        session_id=session_id,
        amount_display=f"${req.fee_amount_cents / 100:.2f}",
    )


@router.post("/message")
async def send_vent_message(msg: VentMessage) -> dict[str, Any]:
    """Send a message in an active Vent session.

    The AI responds with empathetic acknowledgment and issue identification.
    System prompt is isolated (OWASP LLM01).
    """
    # TODO: Verify session is active and paid
    # TODO: Route to Gemini Flash for fast, empathetic responses
    # TODO: Accumulate messages for final intake summary

    return {
        "session_id": msg.session_id,
        "response": "I understand your situation. Let me identify the key legal issues here...",
        "identified_issues_so_far": [],
    }


@router.post("/summarize", response_model=VentIntakeSummary)
async def generate_intake_summary(session_id: str) -> VentIntakeSummary:
    """Generate the final intake summary from a completed Vent session.

    Sent to the attorney dashboard for review.
    Triggers magic-link generation for full Oracle Studio access.
    """
    # TODO: Aggregate all session messages
    # TODO: Run through Gemini Pro for structured extraction
    # TODO: Generate magic link for full research portal

    return VentIntakeSummary(
        session_id=session_id,
        client_narrative="[Intake summary pending — model routing not yet wired]",
        identified_issues=["Contract dispute", "Potential breach of fiduciary duty"],
        suggested_practice_areas=["Commercial Litigation", "Business Law"],
        urgency_level="medium",
        recommended_next_step="Full Oracle Studio research session",
        estimated_complexity="moderate",
    )
