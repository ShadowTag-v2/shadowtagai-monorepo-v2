"""RevenueGate - Enforces "No Pay, No AI" doctrine via Stripe.
"""

import os

import stripe
from fastapi import HTTPException

# MOCK DB: Replace with Redis/Postgres in Production
_MOCK_CREDIT_DB = {
    "founder_key_001": 999999,  # Founder Node (Unlimited)
    "user_standard_01": 0,  # Needs top up
}


class RevenueGate:
    def __init__(self):
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock")
        self.price_per_analysis = 1  # 1 Credit per video

    def check_credits(self, api_key: str) -> bool:
        balance = _MOCK_CREDIT_DB.get(api_key, 0)

        if balance < self.price_per_analysis:
            payment_link = self._create_checkout_session(customer_id="generic_user")
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient Credits. Top up here: {payment_link}",
            )
        return True

    def deduct_credit(self, api_key: str):
        if api_key in _MOCK_CREDIT_DB:
            _MOCK_CREDIT_DB[api_key] -= self.price_per_analysis
            print(f"///▞ REVENUE :: Deducted 1 Credit. Balance: {_MOCK_CREDIT_DB[api_key]}")

    def _create_checkout_session(self, customer_id: str) -> str:
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {"name": "ShadowTagAi Credit"},
                            "unit_amount": 2000,
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url="https://shadowtag.ai/success",
                cancel_url="https://shadowtag.ai/cancel",
            )
            return session.url
        except Exception:
            return "https://shadowtag.ai/pricing"
