"""Stripe Manager - Billing Infrastructure
"""

import os


class StripeManager:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("STRIPE_API_KEY")
        if not self.api_key:
            print("[WARN] No Stripe API Key found. Billing will be simulated.")

    def create_checkout_session(self, customer_email: str, price_id: str) -> str:
        """Creates a checkout session and returns the URL.
        """
        if not self.api_key:
            return f"https://checklist.stripe.com/simulated/{price_id}?email={customer_email}"

        # Real implementation would involve 'stripe.checkout.Session.create'
        # For MVP/Scaffold, we return a mock URL
        print(f"[*] Creating Stripe Session for {customer_email} on price {price_id}")
        return f"https://checkout.stripe.com/pay/cs_test_{price_id}"

    def check_subscription_status(self, customer_email: str) -> bool:
        """Verifies if a customer has an active subscription.
        """
        # Simulation: Always return True for "test" emails
        return "test" in customer_email
