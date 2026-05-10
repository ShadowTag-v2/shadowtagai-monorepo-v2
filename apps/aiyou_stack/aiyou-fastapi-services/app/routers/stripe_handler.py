"""Stripe Webhook Handler with Signature Verification

Handles Stripe webhook events for subscription lifecycle:
- checkout.session.completed → Activate subscription
- invoice.payment_succeeded → Record payment
- invoice.payment_failed → Flag account
- customer.subscription.updated → Sync tier changes
- customer.subscription.deleted → Deactivate subscription

Pricing tiers (from BUSINESS_CONTEXT_LOCKED.md):
- Consumer: $149/mo
- Enterprise: $20,000/mo
- EU26 Compliance: $28,300/mo
"""

from __future__ import annotations

import logging
import os
from typing import Any

import stripe
from fastapi import APIRouter, Header, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Environment configuration
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

# Tier mapping from Stripe Price IDs (set these in .env)
PRICE_TO_TIER = {
    os.environ.get("STRIPE_PRICE_CONSUMER", "price_consumer"): "consumer",
    os.environ.get("STRIPE_PRICE_ENTERPRISE", "price_enterprise"): "enterprise",
    os.environ.get("STRIPE_PRICE_EU26", "price_eu26"): "eu26",
}


def _verify_signature(payload: bytes, sig_header: str) -> stripe.Event:
    """Verify Stripe webhook signature using HMAC.

    Args:
        payload: Raw request body bytes.
        sig_header: Stripe-Signature header value.

    Returns:
        Verified Stripe Event object.

    Raises:
        HTTPException: If signature is invalid or secret is missing.
    """
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail="STRIPE_WEBHOOK_SECRET not configured",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error("Stripe signature verification failed", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail="Invalid signature") from e
    except ValueError as e:
        logger.error("Invalid Stripe payload", extra={"error": str(e)})
        raise HTTPException(status_code=400, detail="Invalid payload") from e

    return event


async def _handle_checkout_completed(session: dict[str, Any]) -> dict[str, Any]:
    """Handle checkout.session.completed — activate new subscription."""
    customer_id = session.get("customer", "")
    subscription_id = session.get("subscription", "")
    customer_email = session.get("customer_email", "")

    logger.info(
        "Checkout completed",
        extra={
            "customer_id": customer_id,
            "subscription_id": subscription_id,
            "email": customer_email,
        },
    )

    # TODO: Update user subscription in database
    # await db.update_subscription(customer_email, subscription_id, status="active")

    return {
        "action": "subscription_activated",
        "customer_id": customer_id,
        "subscription_id": subscription_id,
    }


async def _handle_payment_succeeded(invoice: dict[str, Any]) -> dict[str, Any]:
    """Handle invoice.payment_succeeded — record successful payment."""
    customer_id = invoice.get("customer", "")
    amount = invoice.get("amount_paid", 0)
    currency = invoice.get("currency", "usd")

    logger.info(
        "Payment succeeded",
        extra={
            "customer_id": customer_id,
            "amount": amount,
            "currency": currency,
        },
    )

    return {
        "action": "payment_recorded",
        "customer_id": customer_id,
        "amount_cents": amount,
    }


async def _handle_payment_failed(invoice: dict[str, Any]) -> dict[str, Any]:
    """Handle invoice.payment_failed — flag account for dunning."""
    customer_id = invoice.get("customer", "")
    attempt_count = invoice.get("attempt_count", 0)

    logger.warning(
        "Payment failed",
        extra={
            "customer_id": customer_id,
            "attempt_count": attempt_count,
        },
    )

    # TODO: Send dunning email, potentially downgrade after N attempts
    # if attempt_count >= 3:
    #     await db.downgrade_to_free(customer_id)

    return {
        "action": "payment_failed_flagged",
        "customer_id": customer_id,
        "attempt_count": attempt_count,
    }


async def _handle_subscription_updated(subscription: dict[str, Any]) -> dict[str, Any]:
    """Handle customer.subscription.updated — sync tier changes."""
    customer_id = subscription.get("customer", "")
    status = subscription.get("status", "")
    items = subscription.get("items", {}).get("data", [])

    # Determine new tier from price
    new_tier = "free"
    for item in items:
        price_id = item.get("price", {}).get("id", "")
        if price_id in PRICE_TO_TIER:
            new_tier = PRICE_TO_TIER[price_id]
            break

    logger.info(
        "Subscription updated",
        extra={
            "customer_id": customer_id,
            "status": status,
            "tier": new_tier,
        },
    )

    return {
        "action": "subscription_tier_synced",
        "customer_id": customer_id,
        "tier": new_tier,
        "status": status,
    }


async def _handle_subscription_deleted(subscription: dict[str, Any]) -> dict[str, Any]:
    """Handle customer.subscription.deleted — deactivate subscription."""
    customer_id = subscription.get("customer", "")

    logger.info(
        "Subscription deleted",
        extra={"customer_id": customer_id},
    )

    # TODO: Downgrade to free tier
    # await db.update_subscription(customer_id, status="canceled", tier="free")

    return {
        "action": "subscription_deactivated",
        "customer_id": customer_id,
    }


# Event handler dispatch table
EVENT_HANDLERS = {
    "checkout.session.completed": _handle_checkout_completed,
    "invoice.payment_succeeded": _handle_payment_succeeded,
    "invoice.payment_failed": _handle_payment_failed,
    "customer.subscription.updated": _handle_subscription_updated,
    "customer.subscription.deleted": _handle_subscription_deleted,
}


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="Stripe-Signature"),
) -> dict[str, Any]:
    """Stripe webhook endpoint with signature verification.

    All webhook events are verified using HMAC before processing.
    Unhandled event types are acknowledged but not processed.
    """
    payload = await request.body()

    # CRITICAL: Verify signature before any processing
    event = _verify_signature(payload, stripe_signature)

    event_type = event.get("type", "")
    event_data = event.get("data", {}).get("object", {})

    logger.info("Stripe webhook received", extra={"type": event_type})

    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        result = await handler(event_data)
        return {"status": "processed", "event_type": event_type, **result}

    # Acknowledge unhandled events
    logger.debug("Unhandled Stripe event", extra={"type": event_type})
    return {"status": "acknowledged", "event_type": event_type}
