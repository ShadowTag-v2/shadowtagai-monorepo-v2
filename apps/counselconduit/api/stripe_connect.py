# apps/counselconduit/api/stripe_connect.py
"""Stripe Connect Account Provisioning for CounselConduit.

Manages attorney Stripe accounts, checkout sessions, and billing portal.

Flow:
    1. Attorney signs up → Create Stripe customer
    2. Attorney selects tier → Create checkout session
    3. Payment succeeds → Webhook provisions access (stripe_handler.py)
    4. Attorney manages billing → Redirect to Stripe billing portal
"""

from __future__ import annotations

import logging
import os
from typing import Any

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from apps.counselconduit.api.auth import get_current_attorney

logger = logging.getLogger("counselconduit.stripe_connect")

router = APIRouter(prefix="/billing", tags=["billing"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

# Price IDs from .env
_PRICE_IDS = {
    "trial": os.getenv("STRIPE_PRICE_TRIAL", "price_FREE"),
    "professional": os.getenv("STRIPE_PRICE_PROFESSIONAL", ""),
    "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", ""),
}

_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "https://kovelai.web.app/chat.html?session=success")
_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "https://kovelai.web.app/pricing.html")


class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""
    tier: str  # professional | enterprise
    annual: bool = False


class PortalRequest(BaseModel):
    """Request to access billing portal."""
    return_url: str = "https://kovelai.web.app/dashboard.html"


@router.post("/checkout")
async def create_checkout_session(
    req: CheckoutRequest,
    attorney: dict[str, Any] = Depends(get_current_attorney),
):
    """Create a Stripe Checkout session for subscription."""
    price_id = _PRICE_IDS.get(req.tier)
    if not price_id or req.tier == "trial":
        raise HTTPException(status_code=400, detail="Invalid tier for checkout.")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=attorney.get("email"),
            success_url=_SUCCESS_URL,
            cancel_url=_CANCEL_URL,
            metadata={
                "attorney_uid": attorney.get("uid", ""),
                "tier": req.tier,
            },
        )
        logger.info("Checkout created: attorney=%s tier=%s", attorney.get("uid"), req.tier)
        return {"checkout_url": session.url, "session_id": session.id}
    except stripe.error.StripeError as e:
        logger.error("Stripe error: %s", e)
        raise HTTPException(status_code=500, detail="Payment service error.")


@router.post("/portal")
async def create_billing_portal(
    req: PortalRequest,
    attorney: dict[str, Any] = Depends(get_current_attorney),
):
    """Redirect attorney to Stripe billing portal."""
    try:
        # Look up Stripe customer by email
        customers = stripe.Customer.list(email=attorney.get("email"), limit=1)
        if not customers.data:
            raise HTTPException(status_code=404, detail="No billing account found.")

        session = stripe.billing_portal.Session.create(
            customer=customers.data[0].id,
            return_url=req.return_url,
        )
        return {"portal_url": session.url}
    except stripe.error.StripeError as e:
        logger.error("Stripe portal error: %s", e)
        raise HTTPException(status_code=500, detail="Billing portal error.")


@router.get("/usage")
async def get_usage(
    attorney: dict[str, Any] = Depends(get_current_attorney),
):
    """Get current billing period usage for the attorney."""
    # In production: query Firestore for token usage
    return {
        "attorney_id": attorney.get("uid"),
        "tokens_used": 0,
        "tokens_limit": 100_000,
        "billing_period": "2026-04",
        "tier": "professional",
    }
