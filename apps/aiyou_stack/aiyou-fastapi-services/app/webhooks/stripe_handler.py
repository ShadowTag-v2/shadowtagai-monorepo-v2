#!/usr/bin/env python3
"""Stripe Webhook Handler with Signature Verification

Handles subscription lifecycle events for the ShadowTag product matrix:
- Consumer: $149/mo (Vanguard Box)
- Enterprise: $20K/mo (CounselConduit)
- EU26: $28.3K/mo (GDPR-compliant)

Usage:
    Deployed as a FastAPI endpoint at /api/webhooks/stripe
    Set STRIPE_WEBHOOK_SECRET in .env

Events handled:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.paid
    - invoice.payment_failed
    - checkout.session.completed
"""

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# Idempotency store (in production, use Redis or Firestore)
_processed_events: dict[str, float] = {}
_IDEMPOTENCY_TTL = 86400  # 24 hours


def _get_webhook_secret() -> str:
    """Get Stripe webhook secret from environment."""
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        msg = "STRIPE_WEBHOOK_SECRET not set in environment"
        raise ValueError(msg)
    return secret


def verify_stripe_signature(
    payload: bytes,
    sig_header: str,
    webhook_secret: str,
    tolerance: int = 300,
) -> dict[str, Any]:
    """Verify Stripe webhook signature (v1 scheme).

    Implementation of Stripe's signature verification without requiring
    the stripe Python package. Uses raw HMAC-SHA256.

    Args:
        payload: Raw request body bytes.
        sig_header: Stripe-Signature header value.
        webhook_secret: Webhook endpoint secret (whsec_...).
        tolerance: Maximum age of event in seconds (default 5 min).

    Returns:
        Parsed event object.

    Raises:
        HTTPException: If signature verification fails.
    """
    # Parse signature header
    # Format: t=TIMESTAMP,v1=SIGNATURE[,v0=LEGACY_SIGNATURE]
    elements = {}
    for item in sig_header.split(","):
        key, _, value = item.partition("=")
        elements[key.strip()] = value.strip()

    timestamp_str = elements.get("t")
    signature = elements.get("v1")

    if not timestamp_str or not signature:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe-Signature header format",
        )

    # Verify timestamp tolerance
    try:
        timestamp = int(timestamp_str)
    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail="Invalid timestamp in Stripe-Signature",
        ) from err

    current_time = int(time.time())
    if abs(current_time - timestamp) > tolerance:
        raise HTTPException(
            status_code=400,
            detail=f"Webhook timestamp too old ({abs(current_time - timestamp)}s > {tolerance}s tolerance)",
        )

    # Compute expected signature
    signed_payload = f"{timestamp}.".encode() + payload
    expected_sig = hmac.new(
        webhook_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison
    if not hmac.compare_digest(expected_sig, signature):
        raise HTTPException(
            status_code=400,
            detail="Webhook signature verification failed",
        )

    # Parse and return event
    try:
        event = json.loads(payload)
    except json.JSONDecodeError as err:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        ) from err

    return event


def _is_duplicate(event_id: str) -> bool:
    """Check if event was already processed (idempotency)."""
    now = time.time()

    # Cleanup expired entries
    expired = [k for k, v in _processed_events.items() if now - v > _IDEMPOTENCY_TTL]
    for k in expired:
        del _processed_events[k]

    if event_id in _processed_events:
        logger.info(f"Duplicate event skipped: {event_id}")
        return True

    _processed_events[event_id] = now
    return False


# ─── Event Handlers ────────────────────────────────────────


async def handle_subscription_created(event_data: dict[str, Any]) -> dict:
    """Handle customer.subscription.created event."""
    subscription = event_data.get("object", {})
    customer_id = subscription.get("customer")
    plan_id = subscription.get("plan", {}).get("id")
    amount = subscription.get("plan", {}).get("amount", 0)

    logger.info(
        f"Subscription created: customer={customer_id}, plan={plan_id}, "
        f"amount=${amount / 100:.2f}/mo",
    )

    # Map to product tier
    tier = _map_amount_to_tier(amount)

    return {
        "action": "subscription_created",
        "customer_id": customer_id,
        "plan_id": plan_id,
        "tier": tier,
        "amount_cents": amount,
        "status": "active",
    }


async def handle_subscription_updated(event_data: dict[str, Any]) -> dict:
    """Handle customer.subscription.updated event."""
    subscription = event_data.get("object", {})
    customer_id = subscription.get("customer")
    status = subscription.get("status")
    cancel_at = subscription.get("cancel_at_period_end")

    logger.info(
        f"Subscription updated: customer={customer_id}, "
        f"status={status}, cancel_at_period_end={cancel_at}",
    )

    return {
        "action": "subscription_updated",
        "customer_id": customer_id,
        "status": status,
        "cancel_at_period_end": cancel_at,
    }


async def handle_subscription_deleted(event_data: dict[str, Any]) -> dict:
    """Handle customer.subscription.deleted event."""
    subscription = event_data.get("object", {})
    customer_id = subscription.get("customer")

    logger.info(f"Subscription cancelled: customer={customer_id}")

    return {
        "action": "subscription_deleted",
        "customer_id": customer_id,
        "status": "cancelled",
        "cancelled_at": datetime.utcnow().isoformat(),
    }


async def handle_invoice_paid(event_data: dict[str, Any]) -> dict:
    """Handle invoice.paid event."""
    invoice = event_data.get("object", {})
    customer_id = invoice.get("customer")
    amount_paid = invoice.get("amount_paid", 0)
    invoice_id = invoice.get("id")

    logger.info(
        f"Invoice paid: customer={customer_id}, "
        f"amount=${amount_paid / 100:.2f}, invoice={invoice_id}",
    )

    return {
        "action": "invoice_paid",
        "customer_id": customer_id,
        "amount_cents": amount_paid,
        "invoice_id": invoice_id,
    }


async def handle_invoice_payment_failed(event_data: dict[str, Any]) -> dict:
    """Handle invoice.payment_failed event."""
    invoice = event_data.get("object", {})
    customer_id = invoice.get("customer")
    attempt_count = invoice.get("attempt_count", 0)

    logger.warning(
        f"Payment failed: customer={customer_id}, attempt={attempt_count}",
    )

    return {
        "action": "payment_failed",
        "customer_id": customer_id,
        "attempt_count": attempt_count,
        "next_attempt": invoice.get("next_payment_attempt"),
    }


async def handle_checkout_completed(event_data: dict[str, Any]) -> dict:
    """Handle checkout.session.completed event."""
    session = event_data.get("object", {})
    customer_id = session.get("customer")
    mode = session.get("mode")

    logger.info(
        f"Checkout completed: customer={customer_id}, mode={mode}",
    )

    return {
        "action": "checkout_completed",
        "customer_id": customer_id,
        "mode": mode,
        "payment_status": session.get("payment_status"),
    }


def _map_amount_to_tier(amount_cents: int) -> str:
    """Map subscription amount to product tier.

    Product Matrix:
    - $149/mo ($14900) → consumer (Vanguard Box)
    - $5000/mo ($500000) → foundation_base
    - $20000/mo ($2000000) → enterprise (CounselConduit)
    - $28300/mo ($2830000) → eu26 (GDPR-compliant)
    """
    tiers = {
        14900: "consumer_vanguard_box",
        500000: "foundation_base",
        2000000: "enterprise_counselconduit",
        2830000: "eu26_gdpr",
    }

    # Find closest tier
    closest = min(tiers.keys(), key=lambda x: abs(x - amount_cents))
    if abs(closest - amount_cents) <= 100:  # Within $1 tolerance
        return tiers[closest]

    return f"custom_{amount_cents}"


# ─── Event Router ──────────────────────────────────────────

EVENT_HANDLERS = {
    "customer.subscription.created": handle_subscription_created,
    "customer.subscription.updated": handle_subscription_updated,
    "customer.subscription.deleted": handle_subscription_deleted,
    "invoice.paid": handle_invoice_paid,
    "invoice.payment_failed": handle_invoice_payment_failed,
    "checkout.session.completed": handle_checkout_completed,
}


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="Stripe-Signature"),
) -> dict:
    """Stripe webhook endpoint with signature verification.

    Security:
    - Verifies HMAC-SHA256 signature
    - Rejects events older than 5 minutes
    - Deduplicates via idempotency key
    - Maps amounts to product tier doctrine
    """
    # Read raw body for signature verification
    payload = await request.body()

    # Verify signature
    webhook_secret = _get_webhook_secret()
    event = verify_stripe_signature(payload, stripe_signature, webhook_secret)

    # Extract event metadata
    event_id = event.get("id", "unknown")
    event_type = event.get("type", "unknown")
    event_data = event.get("data", {})

    logger.info(f"Webhook received: type={event_type}, id={event_id}")

    # Idempotency check
    if _is_duplicate(event_id):
        return {"status": "duplicate", "event_id": event_id}

    # Route to handler
    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        result = await handler(event_data)
        logger.info(f"Event processed: {event_type} → {result.get('action')}")
        return {
            "status": "processed",
            "event_id": event_id,
            "event_type": event_type,
            "result": result,
        }

    # Unhandled event type
    logger.warning(f"Unhandled event type: {event_type}")
    return {
        "status": "ignored",
        "event_id": event_id,
        "event_type": event_type,
        "message": f"Event type '{event_type}' not handled",
    }
