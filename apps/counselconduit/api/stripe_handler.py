# apps/counselconduit/api/stripe_handler.py
"""Stripe Webhook Handler with HMAC Signature Verification.

Routes:
    POST /webhooks/stripe  — Receives Stripe events with signature verification.

Security:
    - HMAC-SHA256 signature verification via Stripe-Signature header
    - Raw body parsing (required for signature verification)
    - Tolerates up to 300s clock skew (Stripe default)
    - All events are logged; only subscribed events trigger side effects

Subscribed Events:
    - checkout.session.completed  → Provision attorney access
    - customer.subscription.updated → Update tier
    - customer.subscription.deleted → Revoke access
    - invoice.payment_succeeded    → Record billing event
    - invoice.payment_failed       → Alert + grace period
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

logger = logging.getLogger("counselconduit.stripe")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Stripe sends events signed with this secret.
# Set via: STRIPE_WEBHOOK_SECRET=whsec_... in .env
_WEBHOOK_SECRET: str | None = None

# Maximum age (seconds) of a webhook event before rejection.
_MAX_AGE_SECONDS = 300


def _get_webhook_secret() -> str:
    """Lazy-load webhook secret from environment."""
    global _WEBHOOK_SECRET  # noqa: PLW0603
    if _WEBHOOK_SECRET is None:
        _WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    return _WEBHOOK_SECRET


def verify_stripe_signature(
    payload: bytes,
    sig_header: str,
    secret: str,
    tolerance: int = _MAX_AGE_SECONDS,
) -> dict[str, Any]:
    """Verify Stripe webhook signature (v1 scheme) without the stripe SDK.

    Stripe-Signature format:
        t=<timestamp>,v1=<signature>[,v0=<legacy>]

    Verification:
        1. Extract timestamp and v1 signature from header
        2. Construct signed_payload = f"{timestamp}.{payload_body}"
        3. Compute expected = HMAC-SHA256(secret, signed_payload)
        4. Compare via constant-time comparison
        5. Reject if timestamp is older than tolerance

    Raises:
        HTTPException(400): Missing or malformed signature header
        HTTPException(401): Signature mismatch or replay attack

    Returns:
        Parsed JSON event body.
    """
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header.",
        )

    # Parse header elements
    elements: dict[str, str] = {}
    for item in sig_header.split(","):
        key_val = item.strip().split("=", 1)
        if len(key_val) == 2:
            elements[key_val[0]] = key_val[1]

    timestamp_str = elements.get("t")
    signature = elements.get("v1")

    if not timestamp_str or not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed Stripe-Signature header: missing t or v1.",
        )

    # Compute expected signature
    try:
        timestamp = int(timestamp_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed Stripe-Signature header: non-integer timestamp.",
        ) from exc

    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(expected, signature):
        logger.warning("Stripe signature mismatch — potential forgery attempt.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        )

    # Replay protection: reject stale events
    if abs(time.time() - timestamp) > tolerance:
        logger.warning("Stripe webhook timestamp outside tolerance (%ds).", tolerance)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Webhook timestamp too old — possible replay attack.",
        )

    # Parse and return event payload
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON in webhook body.",
        ) from exc


# ── Event Handlers ──────────────────────────────────────────────────────────

def _handle_checkout_completed(event: dict[str, Any]) -> dict[str, str]:
    """Provision attorney access after successful checkout."""
    session = event.get("data", {}).get("object", {})
    customer_email = session.get("customer_email", "unknown")
    subscription_id = session.get("subscription", "unknown")
    logger.info(
        "Checkout completed: email=%s subscription=%s",
        customer_email,
        subscription_id,
    )
    # TODO: Write to Firestore via MCP — create attorney record
    return {"action": "provisioned", "email": customer_email}


def _handle_subscription_updated(event: dict[str, Any]) -> dict[str, str]:
    """Update attorney tier on subscription change."""
    subscription = event.get("data", {}).get("object", {})
    sub_id = subscription.get("id", "unknown")
    sub_status = subscription.get("status", "unknown")
    logger.info("Subscription updated: id=%s status=%s", sub_id, sub_status)
    # TODO: Update Firestore attorney tier via MCP
    return {"action": "tier_updated", "subscription_id": sub_id, "status": sub_status}


def _handle_subscription_deleted(event: dict[str, Any]) -> dict[str, str]:
    """Revoke attorney access on subscription cancellation."""
    subscription = event.get("data", {}).get("object", {})
    sub_id = subscription.get("id", "unknown")
    logger.info("Subscription deleted: id=%s — revoking access.", sub_id)
    # TODO: Revoke Firestore access via MCP
    return {"action": "access_revoked", "subscription_id": sub_id}


def _handle_invoice_payment_succeeded(event: dict[str, Any]) -> dict[str, str]:
    """Record successful billing event for Triple-Dip telemetry."""
    invoice = event.get("data", {}).get("object", {})
    amount = invoice.get("amount_paid", 0)
    customer = invoice.get("customer", "unknown")
    logger.info(
        "Invoice paid: customer=%s amount=%d cents",
        customer,
        amount,
    )
    # TODO: Record billing event in Firestore via MCP
    return {"action": "payment_recorded", "customer": customer, "amount_cents": amount}


def _handle_invoice_payment_failed(event: dict[str, Any]) -> dict[str, str]:
    """Alert on failed payment — enter grace period."""
    invoice = event.get("data", {}).get("object", {})
    customer = invoice.get("customer", "unknown")
    attempt_count = invoice.get("attempt_count", 0)
    logger.warning(
        "Invoice payment FAILED: customer=%s attempt=%d",
        customer,
        attempt_count,
    )
    # TODO: Set grace period flag in Firestore via MCP
    return {"action": "payment_failed", "customer": customer, "attempt": attempt_count}


# Event type → handler mapping
_EVENT_HANDLERS: dict[str, Any] = {
    "checkout.session.completed": _handle_checkout_completed,
    "customer.subscription.updated": _handle_subscription_updated,
    "customer.subscription.deleted": _handle_subscription_deleted,
    "invoice.payment_succeeded": _handle_invoice_payment_succeeded,
    "invoice.payment_failed": _handle_invoice_payment_failed,
}


# ── Route ───────────────────────────────────────────────────────────────────

@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request) -> dict[str, Any]:
    """Receive and verify Stripe webhook events.

    The endpoint reads the raw body for HMAC verification,
    then dispatches to the appropriate event handler.
    Returns 200 immediately — Stripe retries on 4xx/5xx.
    """
    secret = _get_webhook_secret()
    if not secret:
        logger.error("STRIPE_WEBHOOK_SECRET is not set — rejecting all webhooks.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured.",
        )

    # Read raw body (required for signature verification — NOT parsed JSON)
    raw_body = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    # Verify signature
    event = verify_stripe_signature(raw_body, sig_header, secret)

    event_type = event.get("type", "unknown")
    event_id = event.get("id", "unknown")
    logger.info("Stripe event received: type=%s id=%s", event_type, event_id)

    # Dispatch to handler
    handler = _EVENT_HANDLERS.get(event_type)
    if handler:
        result = handler(event)
        return {"received": True, "event_type": event_type, "result": result}

    # Unhandled event type — acknowledge but don't process
    logger.debug("Unhandled Stripe event type: %s", event_type)
    return {"received": True, "event_type": event_type, "result": "no_handler"}
