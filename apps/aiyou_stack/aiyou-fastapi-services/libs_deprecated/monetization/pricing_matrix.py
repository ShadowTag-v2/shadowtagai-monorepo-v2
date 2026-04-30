"""ANTIGRAVITY // PRICING MATRIX
Doctrine: "Generational Wealth"
"""

import random
from enum import StrEnum


class SubscriptionTier(StrEnum):
    BASIC = "BASIC_DEFENSE"  # $3k/mo
    EU_COMPLIANCE = "EU_26_SHIELD"  # Basic + 30%
    FINANCIAL = "FINANCIAL_DYNAMIC"  # Monte Carlo
    SOVEREIGN = "TIER_30_SOVEREIGN"  # $1M


# BASE CONSTANTS
BASE_SUBSCRIPTION_CENTS = 3000 * 100  # $3,000.00
TIER_30_PRICE_USD = 100000000  # $1,000,000.00
CURRENCY = "usd"
PRODUCT_NAME = "ShadowTag Tier 30: RED SHIRT PROTOCOL"
DESCRIPTION = "Full unadulterated access used by Vertical Sovereigns. We build your AI and System while you sleep."


def calculate_price(tier: SubscriptionTier, risk_surface_score: int = 10) -> int:
    """Calculates dynamic pricing based on '10 Fingers & Monte Carlo' Doctrine."""
    price = BASE_SUBSCRIPTION_CENTS

    if tier == SubscriptionTier.BASIC:
        return price

    if tier == SubscriptionTier.EU_COMPLIANCE:
        # EU Premium: +30%
        return int(price * 1.30)

    if tier == SubscriptionTier.FINANCIAL:
        # FINANCIAL LAYER: Monte Carlo Dynamic Pricing
        # "10 Fingers": We assume 'risk_surface_score' represents this.
        # $500 per risk point premium.
        risk_premium = risk_surface_score * 500 * 100

        # Monte Carlo Variance (0.8x to 1.5x based on market volatility simulation)
        volatility = random.uniform(0.8, 1.5)

        total_raw = price + risk_premium
        final_price = int(total_raw * volatility)

        return final_price

    if tier == SubscriptionTier.SOVEREIGN:
        return TIER_30_PRICE_USD

    return price
