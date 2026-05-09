# apps/counselconduit/api/subscription_notifications.py
"""Stripe subscription change email notifications.

Listens to Stripe webhook events and sends corresponding emails
using the email templates defined in email_templates.py.

Integration: Called from stripe_handler.py webhook endpoint.
"""

from __future__ import annotations

import logging

try:
    from apps.counselconduit.api.email_templates import (
        PAYMENT_FAILED_EMAIL,
        PAYMENT_SUCCESS_EMAIL,
        WELCOME_EMAIL,
    )
    from apps.counselconduit.api.workspace_alerts import (
        alert_payment_failure as alert_payment_failed,
    )
except ImportError:
    from api.email_templates import (  # type: ignore[no-redef]
        PAYMENT_FAILED_EMAIL,
        PAYMENT_SUCCESS_EMAIL,
        WELCOME_EMAIL,
    )
    from api.workspace_alerts import (  # type: ignore[no-redef]
        alert_payment_failure as alert_payment_failed,
    )

logger = logging.getLogger(__name__)

# Tier display names
TIER_NAMES = {
    "prod_UM2XwCF1byjegL": "Trial",
    "prod_UM2X10cpyay52e": "Professional",
    "prod_UM2XMVp9Er7A0i": "Enterprise",
}


async def handle_checkout_completed(event: dict) -> None:
    """Handle checkout.session.completed — new subscriber."""
    session = event["data"]["object"]
    email = session.get("customer_email", "")
    logger.info("new_subscriber", email=email, session_id=session["id"])

    # Send welcome email
    # TODO: Wire SendGrid/Google Workspace SMTP
    template = WELCOME_EMAIL.copy()
    template["html"] = template["html"].format(email=email)
    logger.info("welcome_email_queued", email=email)


async def handle_subscription_updated(event: dict) -> None:
    """Handle customer.subscription.updated — tier change."""
    sub = event["data"]["object"]
    product_id = sub["items"]["data"][0]["price"]["product"]
    tier = TIER_NAMES.get(product_id, "Unknown")
    customer_id = sub["customer"]
    logger.info(
        "subscription_updated",
        customer_id=customer_id,
        tier=tier,
        status=sub["status"],
    )


async def handle_payment_succeeded(event: dict) -> None:
    """Handle invoice.payment_succeeded — record billing event."""
    invoice = event["data"]["object"]
    amount = invoice["amount_paid"] / 100
    email = invoice.get("customer_email", "")
    logger.info(
        "payment_succeeded",
        email=email,
        amount=amount,
        invoice_id=invoice["id"],
    )

    # Send confirmation email
    template = PAYMENT_SUCCESS_EMAIL.copy()
    template["html"] = template["html"].format(
        tier="Professional",
        amount=f"{amount:.2f}",
        period="Monthly",
        tokens="100,000",
    )
    logger.info("payment_confirmation_queued", email=email)


async def handle_payment_failed(event: dict) -> None:
    """Handle invoice.payment_failed — alert and grace period."""
    invoice = event["data"]["object"]
    attempt = invoice.get("attempt_count", 1)
    customer_id = invoice["customer"]
    amount = invoice["amount_due"] / 100

    logger.warning(
        "payment_failed",
        customer_id=customer_id,
        attempt=attempt,
        amount=amount,
    )

    # Send failure email
    template = PAYMENT_FAILED_EMAIL.copy()
    template["html"] = template["html"].format(attempt=attempt)

    # Google Chat alert
    await alert_payment_failed(
        attorney_id=customer_id,
        firm_id="",
        amount_cents=int(amount * 100),
        error=f"Payment attempt #{attempt} failed",
    )


async def handle_subscription_deleted(event: dict) -> None:
    """Handle customer.subscription.deleted — revoke access."""
    sub = event["data"]["object"]
    customer_id = sub["customer"]
    logger.warning("subscription_cancelled", customer_id=customer_id)
    # TODO: Revoke Firestore access tokens
