# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import APIRouter, HTTPException, Request, Header
import stripe
import os
import logging
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger("Kosmos.Billing.CorYay")

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

# The Core Pricing Matrix (Dynamic pricing based on active Citadels)
CORYAY_MATRIX_PRICING = {
    "BASE_5K": 500000,  # $5,000.00
    "CITADEL_JUSTITIA": 300000,  # $3,000.00
    "CITADEL_CADUCEUS": 350000,  # $3,500.00
    "CITADEL_OMNISCIENCE": 350000,  # $3,500.00
}


class CheckoutRequest(BaseModel):
    selected_citadels: list[str]


@router.post("/api/billing/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest):
    """
    Constructs the Stripe Checkout session mathematically enforcing the matrix.
    Base Tier is structurally mandatory.
    """
    line_items = []

    # 1. Base Tier Enforced (The Fiduciary Trap)
    line_items.append(
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Uphillsnowball Sovereign Base Tier (Includes Warrant Protocol)"},
                "unit_amount": CORYAY_MATRIX_PRICING["BASE_5K"],
                "recurring": {"interval": "month"},
            },
            "quantity": 1,
        }
    )

    # 2. Add requested Citadels
    for citadel in req.selected_citadels:
        if citadel in CORYAY_MATRIX_PRICING and citadel != "BASE_5K":
            line_items.append(
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"Citadel Protocol: {citadel.split('_')[1]}"},
                        "unit_amount": CORYAY_MATRIX_PRICING[citadel],
                        "recurring": {"interval": "month"},
                    },
                    "quantity": 1,
                }
            )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card", "us_bank_account"],
            line_items=line_items,
            mode="subscription",
            success_url="https://www.shadowtagai.com/success",
            cancel_url="https://www.shadowtagai.com/cancel",
        )
        return {"url": checkout_session.url}
    except Exception as e:
        logger.error(f"Stripe Session Generation Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/billing/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """Webhook listener to instantly deploy AWS/GCP resources upon payment success."""
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, endpoint_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook Error: {str(e)}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        logger.info(f"Payment Secured. Engaging Kosmos Provisioning for {session.get('customer_email')}")
        # Call the Kosmos deployment orchestrator here to spin up the actual infrastructure

    return {"status": "success"}
