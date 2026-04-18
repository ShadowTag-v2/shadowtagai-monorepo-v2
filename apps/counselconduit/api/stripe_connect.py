# apps/counselconduit/api/stripe_connect.py
"""Stripe Connect — Attorney onboarding + payment splitting.

Flow:
1. Attorney signs up → we create a Stripe Connect Express account
2. Attorney completes Stripe onboarding (KYC, bank account)
3. Client pays for Vent Mode or Oracle Studio session
4. Payment goes to attorney's Connect account minus our platform fee
5. We bill the attorney separately via subscription (Solo/Practice/Enterprise)

This implements the dual-billing engine from BUSINESS_CONTEXT_LOCKED.md:
- Client → Attorney: Direct payment for services via Stripe Connect
- Attorney → Us: Subscription fee for AI platform access
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.stripe_connect")

router = APIRouter(prefix="/connect", tags=["Stripe Connect"])

_STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY", "")
_PLATFORM_URL = os.getenv("KOVELAI_BASE_URL", "https://kovelai.web.app")


# ── Models ─────────────────────────────────────────────────────────────────


class ConnectOnboardRequest(BaseModel):
    """Attorney initiates Stripe Connect onboarding."""
    attorney_id: str
    firm_id: str
    email: str
    business_name: str | None = None
    country: str = "US"


class ConnectOnboardResponse(BaseModel):
    """Response with Stripe Connect onboarding URL."""
    account_id: str
    onboarding_url: str
    message: str = "Complete your Stripe account setup to start receiving payments."


class ConnectStatusResponse(BaseModel):
    """Status of attorney's Stripe Connect account."""
    account_id: str
    charges_enabled: bool
    payouts_enabled: bool
    details_submitted: bool
    requirements: list[str] = Field(default_factory=list)


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post("/onboard", response_model=ConnectOnboardResponse)
async def create_connect_account(req: ConnectOnboardRequest) -> ConnectOnboardResponse:
    """Create a Stripe Connect Express account and return the onboarding URL.

    The attorney completes KYC and bank account setup on Stripe's hosted page.
    After completion, they're redirected back to our dashboard.
    """
    try:
        import stripe

        stripe.api_key = _STRIPE_SECRET

        # Create Express Connect account
        account = stripe.Account.create(
            type="express",
            country=req.country,
            email=req.email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_profile={
                "mcc": "8111",  # Legal Services
                "product_description": "AI-powered legal research services",
            },
            metadata={
                "attorney_id": req.attorney_id,
                "firm_id": req.firm_id,
                "platform": "counselconduit",
            },
        )

        # Create onboarding link
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=f"{_PLATFORM_URL}/dashboard/connect/refresh",
            return_url=f"{_PLATFORM_URL}/dashboard/connect/complete",
            type="account_onboarding",
        )

        logger.info(
            "Connect account created: account=%s attorney=%s",
            account.id,
            req.attorney_id,
        )

        return ConnectOnboardResponse(
            account_id=account.id,
            onboarding_url=account_link.url,
        )

    except ImportError:
        logger.warning("stripe not installed — mock response")
        return ConnectOnboardResponse(
            account_id=f"acct_mock_{req.attorney_id[:8]}",
            onboarding_url=f"{_PLATFORM_URL}/dashboard/connect/mock",
        )
    except Exception as e:
        logger.error("Connect onboard failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "CONNECT_ONBOARD_FAILED", "message": str(e)},
        ) from e


@router.get("/status/{account_id}", response_model=ConnectStatusResponse)
async def get_connect_status(account_id: str) -> ConnectStatusResponse:
    """Check the status of an attorney's Stripe Connect account."""
    try:
        import stripe

        stripe.api_key = _STRIPE_SECRET
        account = stripe.Account.retrieve(account_id)

        requirements = []
        if account.requirements and account.requirements.currently_due:
            requirements = list(account.requirements.currently_due)

        return ConnectStatusResponse(
            account_id=account_id,
            charges_enabled=account.charges_enabled,
            payouts_enabled=account.payouts_enabled,
            details_submitted=account.details_submitted,
            requirements=requirements,
        )

    except ImportError:
        return ConnectStatusResponse(
            account_id=account_id,
            charges_enabled=False,
            payouts_enabled=False,
            details_submitted=False,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ACCOUNT_NOT_FOUND", "message": str(e)},
        ) from e


@router.post("/create-payment-intent")
async def create_connected_payment(
    amount_cents: int,
    attorney_account_id: str,
    session_id: str,
    description: str = "Legal research session",
) -> dict[str, Any]:
    """Create a payment intent that sends funds to the attorney's Connect account.

    Platform fee (our cut) is calculated as 15% of the transaction.
    """
    try:
        import stripe

        stripe.api_key = _STRIPE_SECRET

        PLATFORM_FEE_PCT = 15  # 15% platform fee

        application_fee = int(amount_cents * PLATFORM_FEE_PCT / 100)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency="usd",
            description=description,
            application_fee_amount=application_fee,
            transfer_data={
                "destination": attorney_account_id,
            },
            metadata={
                "session_id": session_id,
                "platform": "counselconduit",
            },
        )

        return {
            "client_secret": payment_intent.client_secret,
            "payment_intent_id": payment_intent.id,
            "amount": amount_cents,
            "platform_fee": application_fee,
        }

    except ImportError:
        return {
            "client_secret": f"pi_mock_{session_id[:8]}_secret",
            "payment_intent_id": f"pi_mock_{session_id[:8]}",
            "amount": amount_cents,
            "platform_fee": int(amount_cents * 0.15),
        }
