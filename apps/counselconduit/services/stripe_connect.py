# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""Stripe Connect onboarding flow for law firms.

Implements the dual-billing engine:
1. Client -> Lawyer: Client subscribes to AI portal
2. Lawyer -> Us: Auto-scaling tiered subscription

Uses Stripe Connect Standard accounts for law firm onboarding.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FirmOnboardingState:
    """Tracks the onboarding state of a law firm."""

    tenant_id: str = ""
    firm_name: str = ""
    stripe_account_id: str = ""  # Connected account ID (acct_xxx)
    onboarding_complete: bool = False
    tier: str = "solo"  # solo | practice | enterprise
    monthly_price_cents: int = 29900  # $299 default


class StripeConnectService:
    """Manages Stripe Connect onboarding for law firms.

    Pricing tiers (auto-bump on usage):
    - Solo: $299/mo (1-2 attorneys)
    - Practice: $599/mo (3-10 attorneys)
    - Enterprise: $999/mo (10+ attorneys)

    All tiers include ALL LLM API costs + 85%+ margin.
    """

    TIER_PRICES = {
        "solo": 29900,  # $299
        "practice": 59900,  # $599
        "enterprise": 99900,  # $999
    }

    def __init__(self, stripe_secret_key: str = "") -> None:
        """Initialize with Stripe API key.

        Args:
            stripe_secret_key: From GCP Secret Manager (production)
                or .env (local development).
        """
        self._api_key = stripe_secret_key

    async def create_connect_account(
        self,
        *,
        tenant_id: str,
        firm_name: str,
        email: str,
    ) -> FirmOnboardingState:
        """Create a Stripe Connect Standard account for a law firm.

        Args:
            tenant_id: Internal tenant ID.
            firm_name: The law firm's name.
            email: The primary contact email.

        Returns:
            FirmOnboardingState with the new Connect account ID.
        """
        try:
            import stripe

            stripe.api_key = self._api_key

            account = stripe.Account.create(
                type="standard",
                email=email,
                business_type="company",
                company={"name": firm_name},
                metadata={
                    "tenant_id": tenant_id,
                    "platform": "counselconduit",
                },
            )

            state = FirmOnboardingState(
                tenant_id=tenant_id,
                firm_name=firm_name,
                stripe_account_id=account.id,
            )

            logger.info(
                "Stripe Connect account created: tenant=%s acct=%s",
                tenant_id,
                account.id,
            )
            return state

        except ImportError:
            logger.error("stripe package not installed")
            raise
        except Exception as e:
            logger.error("Stripe Connect error: %s", e)
            raise

    async def create_onboarding_link(
        self,
        stripe_account_id: str,
        return_url: str = "https://counselconduit-767252945109.us-central1.run.app/onboarding/complete",
        refresh_url: str = "https://counselconduit-767252945109.us-central1.run.app/onboarding/refresh",
    ) -> str:
        """Create a Stripe Connect onboarding link.

        Args:
            stripe_account_id: The Connected account ID.
            return_url: URL to redirect after completion.
            refresh_url: URL if the link expires.

        Returns:
            The onboarding link URL.
        """
        try:
            import stripe

            stripe.api_key = self._api_key

            link = stripe.AccountLink.create(
                account=stripe_account_id,
                type="account_onboarding",
                return_url=return_url,
                refresh_url=refresh_url,
            )
            return link.url

        except ImportError:
            logger.error("stripe package not installed")
            raise

    async def create_subscription(
        self,
        *,
        stripe_account_id: str,
        tier: str = "solo",
    ) -> str:
        """Create a platform subscription for a law firm.

        Args:
            stripe_account_id: The Connected account ID.
            tier: The subscription tier (solo/practice/enterprise).

        Returns:
            The Stripe subscription ID.
        """
        price_cents = self.TIER_PRICES.get(tier, self.TIER_PRICES["solo"])

        try:
            import stripe

            stripe.api_key = self._api_key

            # Create the subscription on the platform account
            # (not on the connected account)
            subscription = stripe.Subscription.create(
                customer=stripe_account_id,
                items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": price_cents,
                            "recurring": {"interval": "month"},
                            "product_data": {
                                "name": f"CounselConduit {tier.title()} Plan",
                            },
                        },
                    }
                ],
                metadata={
                    "tier": tier,
                    "platform": "counselconduit",
                },
            )

            logger.info(
                "Subscription created: acct=%s tier=%s sub=%s",
                stripe_account_id,
                tier,
                subscription.id,
            )
            return subscription.id

        except ImportError:
            logger.error("stripe package not installed")
            raise
