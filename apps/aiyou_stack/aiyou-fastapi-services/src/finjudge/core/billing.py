# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
from datetime import datetime

import stripe
from pydantic import BaseModel

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_mock_key")


class SubscriptionStatus(BaseModel):
    is_active: bool
    plan_id: str
    expires_at: datetime | None


class StripeManager:
    """Handles all Stripe interactions for FinJudge SaaS."""

    def __init__(self):
        self.pro_price_id = os.getenv("STRIPE_PRO_PRICE_ID", "price_123456")
        self.domain = os.getenv("DOMAIN", "http://localhost:8000")

    def create_checkout_session(self, user_id: str, email: str) -> str:
        """Create a checkout session for the Pro Plan.
        Returns the checkout URL.
        """
        try:
            session = stripe.checkout.Session.create(
                customer_email=email,
                client_reference_id=user_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": self.pro_price_id,
                        "quantity": 1,
                    },
                ],
                mode="subscription",
                success_url=f"{self.domain}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{self.domain}/cancel",
            )
            return session.url
        except Exception as e:
            # Fallback for dev/mock mode
            if "sk_test_mock" in stripe.api_key:
                return f"http://localhost:8000/mock-checkout?user={user_id}"
            raise e

    def check_subscription(self, api_key: str) -> SubscriptionStatus:
        """Verify if an API key (mapped to a user) has an active subscription."""
        # In a real app, we'd look up the user_id from the api_key in our DB first.
        # Here we simulate the logic.

        # MOCK LOGIC for v0.2
        if api_key.startswith("sk-pro"):
            return SubscriptionStatus(
                is_active=True,
                plan_id="pro_monthly",
                expires_at=datetime(2026, 1, 1),
            )

        return SubscriptionStatus(is_active=False, plan_id="free", expires_at=None)
