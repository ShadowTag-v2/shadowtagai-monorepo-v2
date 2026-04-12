import os

import stripe

from .pricing_matrix import TIER_30_PRICE_USD

# Mock key for build - Replace with Secret Manager in Prod
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_mock_key_antigravity")


class StripeGate:
    @staticmethod
    def create_checkout_session(success_url: str, cancel_url: str) -> str:
        """
        The Card Reader.
        Redirects to a pre-configured Stripe Payment Link (No-Code).
        """
        # FLASH LIQUIDITY: Use the link directly.
        payment_link = os.getenv("STRIPE_PAYMENT_LINK")

        if payment_link:
            return payment_link

        # Fallback to Mock if no link provided
        return f"https://checkout.stripe.com/mock_hosted_page?amount={TIER_30_PRICE_USD}"
