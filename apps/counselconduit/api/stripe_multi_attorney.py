# apps/counselconduit/api/stripe_multi_attorney.py
"""Stripe Connect: Multi-Attorney Billing Split.

Implements Connected Accounts for law firms where multiple attorneys
share a single firm subscription but need individual usage tracking
and optional per-attorney billing.

Architecture:
  - Firm = Stripe Customer (pays the subscription)
  - Attorney = Stripe Connected Account (receives usage-based splits)
  - Usage is tracked per-attorney in Firestore, billed monthly to the firm

For MVP: All billing goes through the firm's subscription.
For v2: Connect accounts enable revenue sharing with individual attorneys.
"""

from __future__ import annotations

import os
import logging

import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
logger = logging.getLogger(__name__)


async def create_firm_customer(
    firm_name: str, admin_email: str, metadata: dict | None = None
) -> dict:
    """Create a Stripe Customer representing the law firm."""
    customer = stripe.Customer.create(
        name=firm_name,
        email=admin_email,
        metadata={
            "type": "law_firm",
            "platform": "kovelai",
            **(metadata or {}),
        },
    )
    logger.info("firm_customer_created", customer_id=customer.id, firm=firm_name)
    return {"customer_id": customer.id, "firm_name": firm_name}


async def add_attorney_seat(
    customer_id: str,
    attorney_email: str,
    attorney_name: str,
    bar_number: str,
) -> dict:
    """Add an attorney seat to a firm's subscription.

    For MVP: Just track in metadata. For v2: Create a Connected Account.
    """
    # Track as a subscription item metadata update
    subscriptions = stripe.Subscription.list(customer=customer_id, limit=1)
    if not subscriptions.data:
        return {"error": "No active subscription for this firm"}

    sub = subscriptions.data[0]
    current_seats = int(sub.metadata.get("attorney_seats", "1"))

    stripe.Subscription.modify(
        sub.id,
        metadata={
            **sub.metadata,
            "attorney_seats": str(current_seats + 1),
            f"attorney_{current_seats + 1}_email": attorney_email,
            f"attorney_{current_seats + 1}_name": attorney_name,
            f"attorney_{current_seats + 1}_bar": bar_number,
        },
    )

    logger.info(
        "attorney_seat_added",
        customer_id=customer_id,
        attorney=attorney_email,
        total_seats=current_seats + 1,
    )
    return {
        "attorney_email": attorney_email,
        "seat_number": current_seats + 1,
        "subscription_id": sub.id,
    }


async def get_firm_usage(customer_id: str) -> dict:
    """Get usage breakdown for a firm's subscription."""
    subscriptions = stripe.Subscription.list(customer=customer_id, limit=1)
    if not subscriptions.data:
        return {"error": "No active subscription"}

    sub = subscriptions.data[0]
    invoices = stripe.Invoice.list(customer=customer_id, limit=3)

    return {
        "subscription_id": sub.id,
        "status": sub.status,
        "current_period_end": sub.current_period_end,
        "attorney_seats": int(sub.metadata.get("attorney_seats", "1")),
        "recent_invoices": [
            {
                "id": inv.id,
                "amount_paid": inv.amount_paid / 100,
                "status": inv.status,
                "period_end": inv.period_end,
            }
            for inv in invoices.data
        ],
    }


async def create_enterprise_invoice(
    customer_id: str,
    line_items: list[dict],
    memo: str = "",
) -> dict:
    """Create a custom invoice for enterprise clients.

    Args:
        customer_id: Stripe customer ID.
        line_items: List of {"description": str, "amount": int (cents)}.
        memo: Optional invoice memo.
    """
    for item in line_items:
        stripe.InvoiceItem.create(
            customer=customer_id,
            amount=item["amount"],
            currency="usd",
            description=item["description"],
        )

    invoice = stripe.Invoice.create(
        customer=customer_id,
        auto_advance=True,  # Auto-finalize
        collection_method="send_invoice",
        days_until_due=30,
        footer=memo or "KovelAI Enterprise — Net 30",
    )

    logger.info(
        "enterprise_invoice_created",
        invoice_id=invoice.id,
        customer_id=customer_id,
        total=invoice.total / 100,
    )
    return {"invoice_id": invoice.id, "total": invoice.total / 100}
