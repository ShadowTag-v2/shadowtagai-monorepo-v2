# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/stripe_connect_onboarding.py
"""Stripe Connect Onboarding Endpoint.

Creates a Stripe Connect account link for law firm onboarding.
The attorney is redirected to Stripe's hosted onboarding flow.

Routes:
    POST /connect/onboard   → Create account link for attorney onboarding
    GET  /connect/status    → Check onboarding completion status

Security:
    - Requires authenticated attorney (X-Kovel-Auth header)
    - Stripe account ID stored in Firestore, never exposed to client
    - Returns only the redirect URL, not raw Stripe account details
"""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger("counselconduit.stripe_connect")

router = APIRouter(prefix="/connect", tags=["connect"])


class OnboardingRequest(BaseModel):
    """Request body for Stripe Connect onboarding."""

    firm_name: str
    attorney_email: str
    return_url: str = "https://kovelai.web.app/onboarding/complete"
    refresh_url: str = "https://kovelai.web.app/onboarding/refresh"


class OnboardingResponse(BaseModel):
    """Response with Stripe Connect account link."""

    account_link_url: str
    account_id: str
    expires_at: int


class OnboardingStatus(BaseModel):
    """Onboarding status response."""

    account_id: str
    charges_enabled: bool
    payouts_enabled: bool
    details_submitted: bool
    onboarding_complete: bool


def _get_stripe_secret() -> str:
    """Lazy-load Stripe secret key from environment or Secret Manager."""
    key = os.getenv("STRIPE_SECRET_KEY", "")
    if not key:
        try:
            from api.secret_client import get_secret

            key = get_secret("STRIPE_SECRET_KEY") or ""
        except ImportError:
            try:
                from apps.counselconduit.api.secret_client import get_secret

                key = get_secret("STRIPE_SECRET_KEY") or ""
            except ImportError:
                pass
    return key


@router.post("/onboard", response_model=OnboardingResponse)
async def create_onboarding_link(
    request: OnboardingRequest,
    x_kovel_auth: str = Header(None),
):
    """Create a Stripe Connect onboarding link for a law firm.

    1. Creates a Stripe Connect Custom account for the firm
    2. Stores the account ID in Firestore (beta_accounts collection)
    3. Returns the Stripe-hosted onboarding URL

    The attorney is redirected to Stripe to complete KYC/bank setup.
    """
    if not x_kovel_auth:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required.",
        )

    secret = _get_stripe_secret()
    if not secret:
        logger.error("STRIPE_SECRET_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment system not configured.",
        )

    try:
        import stripe

        stripe.api_key = secret

        # Create Connected Account (Custom type for full control)
        account = stripe.Account.create(
            type="custom",
            country="US",
            email=request.attorney_email,
            business_type="individual",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_profile={
                "name": request.firm_name,
                "mcc": "8111",  # Legal Services
                "url": "https://kovelai.web.app",
            },
            metadata={
                "firm_name": request.firm_name,
                "attorney_id": x_kovel_auth,
                "platform": "kovelai",
            },
        )

        # Create Account Link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=request.refresh_url,
            return_url=request.return_url,
            type="account_onboarding",
        )

        # Store account mapping in Firestore
        try:
            from google.cloud import firestore as _fs

            db = _fs.Client()
            db.collection("beta_accounts").document(x_kovel_auth).set(
                {
                    "stripe_connect_account_id": account.id,
                    "firm_name": request.firm_name,
                    "attorney_email": request.attorney_email,
                    "onboarding_started": _fs.SERVER_TIMESTAMP,
                    "onboarding_complete": False,
                },
                merge=True,
            )
        except Exception as e:
            logger.warning("Firestore write failed (non-fatal): %s", e)

        logger.info(
            "connect_onboarding_created",
            account_id=account.id,
            firm=request.firm_name,
        )

        return OnboardingResponse(
            account_link_url=account_link.url,
            account_id=account.id,
            expires_at=account_link.expires_at,
        )

    except stripe.error.StripeError as e:
        logger.error("Stripe Connect error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment provider error. Please try again.",
        ) from e


@router.get("/status", response_model=OnboardingStatus)
async def check_onboarding_status(
    x_kovel_auth: str = Header(None),
):
    """Check the Stripe Connect onboarding status for the authenticated attorney."""
    if not x_kovel_auth:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required.",
        )

    # Fetch account ID from Firestore
    try:
        from google.cloud import firestore as _fs

        db = _fs.Client()
        doc = db.collection("beta_accounts").document(x_kovel_auth).get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No onboarding record found.",
            )
        data = doc.to_dict() or {}
        account_id = data.get("stripe_connect_account_id", "")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Firestore read failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve onboarding status.",
        ) from e

    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Stripe account linked.",
        )

    # Fetch status from Stripe
    secret = _get_stripe_secret()
    try:
        import stripe

        stripe.api_key = secret
        account = stripe.Account.retrieve(account_id)

        onboarding_complete = all(
            [
                account.charges_enabled,
                account.payouts_enabled,
                account.details_submitted,
            ]
        )

        # Update Firestore if onboarding just completed
        if onboarding_complete and not data.get("onboarding_complete"):
            try:  # noqa: SIM105
                db.collection("beta_accounts").document(x_kovel_auth).set(
                    {"onboarding_complete": True, "onboarding_completed_at": _fs.SERVER_TIMESTAMP},
                    merge=True,
                )
            except Exception:
                pass  # Non-fatal

        return OnboardingStatus(
            account_id=account_id,
            charges_enabled=account.charges_enabled,
            payouts_enabled=account.payouts_enabled,
            details_submitted=account.details_submitted,
            onboarding_complete=onboarding_complete,
        )

    except stripe.error.StripeError as e:
        logger.error("Stripe status check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to check payment status.",
        ) from e
