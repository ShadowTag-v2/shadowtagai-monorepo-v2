# apps/counselconduit/api/vent_mode.py
"""Vent Mode — SSE Streaming Chat + Flat-Fee Intake Retainer.

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

Streaming: SSE (Server-Sent Events) for real-time chat experience.
Prompt Repetition: Applied for non-reasoning models (arXiv 2512.14982).
"""

from __future__ import annotations

import json
import logging
from typing import Any
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
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


# ── Vent System Prompt (OWASP LLM01: structurally isolated) ───────────

_VENT_SYSTEM_PROMPT = (
    "You are an empathetic legal intake specialist for a law firm. "
    "Your role is to listen to the client's situation with understanding, "
    "identify potential legal issues, and help them articulate their concerns. "
    "Rules: (1) Be warm and validating — they're stressed. "
    "(2) Identify legal issues from their narrative. "
    "(3) Never give legal advice — only identify issues. "
    "(4) Ask clarifying questions to understand the full picture. "
    "(5) Keep responses concise (2-3 paragraphs max)."
)


# ── SSE Streaming ─────────────────────────────────────────────────────


async def _stream_vent_response(
    message: str,
    session_id: str,
    history: list[dict[str, str]] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream a Vent Mode response via LiteLLM as SSE events.

    Applies prompt repetition for non-reasoning models.
    """
    model_id = "gemini-3.1-flash-lite-preview"

    # Build message history
    messages = [{"role": "system", "content": _VENT_SYSTEM_PROMPT}]
    if history:
        messages.extend(history)

    # Apply prompt repetition (arXiv 2512.14982)
    repeated_message = (
        f"{message}\n\n"
        f"---\n\n"
        f"[INSTRUCTION REPEAT]\n"
        f"{_VENT_SYSTEM_PROMPT}\n\n"
        f"Respond to the client's message above with empathy and issue identification."
    )
    messages.append({"role": "user", "content": repeated_message})

    try:
        import litellm

        response = await litellm.acompletion(
            model=model_id,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,  # Slightly creative for empathy
            stream=True,
        )

        full_response = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"

        # Final event with metadata
        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id, 'full_length': len(full_response)})}\n\n"

    except ImportError:
        # Fallback for dev mode without litellm
        fallback = (
            "I hear you, and I understand this situation is stressful. "
            "Let me identify the key issues from what you've described. "
            "[Note: Live model routing not yet configured — "
            "this is a development placeholder.]"
        )
        for word in fallback.split(" "):
            yield f"data: {json.dumps({'type': 'chunk', 'content': word + ' '})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

    except Exception as e:
        logger.error("Vent stream failed: %s", e)
        yield f"data: {json.dumps({'type': 'error', 'message': 'An error occurred. Please try again.'})}\n\n"


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/start", response_model=VentCheckoutResponse)
async def start_vent_session(req: VentSessionRequest) -> VentCheckoutResponse:
    """Start a Vent Mode intake session.

    Creates a Stripe Checkout session for the flat intake fee.
    The fee goes to the attorney's Stripe Connect account.
    After payment, client is redirected to the Vent chat interface.
    """
    try:
        from apps.counselconduit.api.uuid7 import uuid7_str
    except ImportError:
        from api.uuid7 import uuid7_str  # type: ignore[no-redef]

    session_id = uuid7_str()

    # Store session in Firestore
    try:
        try:
            from apps.counselconduit.api.firestore_client import store_session
        except ImportError:
            from api.firestore_client import store_session  # type: ignore[no-redef]

        await store_session(
            req.firm_id,
            {
                "session_id": session_id,
                "attorney_id": req.attorney_id,
                "client_name": req.client_name,
                "client_email": req.client_email,
                "fee_amount_cents": req.fee_amount_cents,
                "type": "vent_mode",
                "status": "pending_payment",
                "messages": [],
            },
        )
    except Exception as e:
        logger.warning("Firestore store failed (non-fatal): %s", e)

    # Create Stripe Checkout (Connect destination)
    checkout_url = f"https://checkout.stripe.com/pay/placeholder_{session_id}"
    try:
        import stripe
        import os

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        if stripe.api_key:
            checkout = stripe.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": req.fee_amount_cents,
                            "product_data": {
                                "name": "Legal Intake Session (Vent Mode)",
                                "description": "Confidential AI-assisted intake session",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                success_url=f"https://kovelai.web.app/vent/{session_id}?status=paid",
                cancel_url="https://kovelai.web.app/vent/cancelled",
                metadata={
                    "session_id": session_id,
                    "firm_id": req.firm_id,
                    "attorney_id": req.attorney_id,
                },
            )
            checkout_url = checkout.url or checkout_url
    except Exception as e:
        logger.warning("Stripe checkout failed (using placeholder): %s", e)

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
    """Send a message in an active Vent session (non-streaming)."""
    # Store message in Firestore
    try:
        try:
            from apps.counselconduit.api.firestore_client import append_session_message
        except ImportError:
            from api.firestore_client import append_session_message  # type: ignore[no-redef]

        await append_session_message(
            firm_id="default",  # TODO: resolve from session
            session_id=msg.session_id,
            role="user",
            content=msg.message,
        )
    except Exception as e:
        logger.warning("Message store failed: %s", e)

    return {
        "session_id": msg.session_id,
        "response": "I understand your situation. Let me identify the key legal issues here...",
        "identified_issues_so_far": [],
    }


@router.post("/message/stream")
async def stream_vent_message(msg: VentMessage) -> StreamingResponse:
    """Stream a Vent Mode response via Server-Sent Events.

    Real-time streaming chat interface for empathetic intake.
    Uses prompt repetition (arXiv 2512.14982) for accuracy boost.
    """
    return StreamingResponse(
        _stream_vent_response(msg.message, msg.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/summarize", response_model=VentIntakeSummary)
async def generate_intake_summary(session_id: str) -> VentIntakeSummary:
    """Generate the final intake summary from a completed Vent session.

    Sent to the attorney dashboard for review.
    Triggers magic-link generation for full Oracle Studio access.
    """
    # TODO: Aggregate all session messages from Firestore
    # TODO: Run through Gemini Pro for structured extraction

    return VentIntakeSummary(
        session_id=session_id,
        client_narrative="[Intake summary pending — model routing not yet wired]",
        identified_issues=["Contract dispute", "Potential breach of fiduciary duty"],
        suggested_practice_areas=["Commercial Litigation", "Business Law"],
        urgency_level="medium",
        recommended_next_step="Full Oracle Studio research session",
        estimated_complexity="moderate",
    )
