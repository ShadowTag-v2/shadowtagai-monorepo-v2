"""Revenue Model Configuration
Defines pricing tiers and projections for ShadowTagAi agent platform
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PricingTier(Enum):
    """Pricing tier levels"""

    BASE = "base"
    USAGE = "usage"
    WHITE_GLOVE = "white_glove"
    ENTERPRISE = "enterprise"


@dataclass
class TierPricing:
    """Pricing for a specific tier"""

    tier: PricingTier
    monthly_price_usd: float
    features: list[str]
    target_customer: str
    expected_churn_rate: float  # Monthly churn rate


@dataclass
class RevenueModel:
    """Revenue model and projections"""

    # Pricing tiers
    base_tier: TierPricing
    white_glove_tier: TierPricing
    enterprise_tier: TierPricing

    # Usage pricing
    price_per_validated_lead: float = 0.10

    # LTV/CAC projections
    average_customer_lifetime_months: int = 18
    target_cac_usd: float = 1000.0
    expected_churn_rate_monthly: float = 0.05  # 5%/mo

    # Sales cycle
    expected_sales_cycle_days: int = 30  # Aggressive
    conservative_sales_cycle_days: int = 90  # Conservative

    def calculate_ltv(self, tier: PricingTier) -> float:
        """Calculate customer lifetime value for a tier"""
        if tier == PricingTier.BASE:
            monthly_revenue = self.base_tier.monthly_price_usd
        elif tier == PricingTier.WHITE_GLOVE:
            monthly_revenue = self.white_glove_tier.monthly_price_usd
        elif tier == PricingTier.ENTERPRISE:
            monthly_revenue = self.enterprise_tier.monthly_price_usd
        else:
            raise ValueError("Usage tier doesn't have fixed LTV")

        ltv = monthly_revenue * self.average_customer_lifetime_months
        return ltv

    def calculate_ltv_cac_ratio(self, tier: PricingTier, actual_cac: float = None) -> float:
        """Calculate LTV:CAC ratio"""
        cac = actual_cac or self.target_cac_usd
        ltv = self.calculate_ltv(tier)
        return ltv / cac if cac > 0 else float("inf")

    def calculate_break_even_timeline_days(
        self, tier: PricingTier, actual_cac: float = None,
    ) -> int:
        """Calculate days to break even on CAC"""
        cac = actual_cac or self.target_cac_usd

        if tier == PricingTier.BASE:
            monthly_revenue = self.base_tier.monthly_price_usd
        elif tier == PricingTier.WHITE_GLOVE:
            monthly_revenue = self.white_glove_tier.monthly_price_usd
        elif tier == PricingTier.ENTERPRISE:
            monthly_revenue = self.enterprise_tier.monthly_price_usd
        else:
            raise ValueError("Usage tier doesn't have fixed monthly revenue")

        months_to_break_even = cac / monthly_revenue if monthly_revenue > 0 else float("inf")
        return int(months_to_break_even * 30)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tiers": {
                "base": {
                    "monthly_price_usd": self.base_tier.monthly_price_usd,
                    "features": self.base_tier.features,
                    "target_customer": self.base_tier.target_customer,
                    "ltv": self.calculate_ltv(PricingTier.BASE),
                    "ltv_cac_ratio": self.calculate_ltv_cac_ratio(PricingTier.BASE),
                },
                "white_glove": {
                    "monthly_price_usd": self.white_glove_tier.monthly_price_usd,
                    "features": self.white_glove_tier.features,
                    "target_customer": self.white_glove_tier.target_customer,
                    "ltv": self.calculate_ltv(PricingTier.WHITE_GLOVE),
                    "ltv_cac_ratio": self.calculate_ltv_cac_ratio(PricingTier.WHITE_GLOVE),
                },
                "enterprise": {
                    "monthly_price_usd": self.enterprise_tier.monthly_price_usd,
                    "features": self.enterprise_tier.features,
                    "target_customer": self.enterprise_tier.target_customer,
                    "ltv": self.calculate_ltv(PricingTier.ENTERPRISE),
                    "ltv_cac_ratio": self.calculate_ltv_cac_ratio(PricingTier.ENTERPRISE),
                },
                "usage": {
                    "price_per_validated_lead": self.price_per_validated_lead,
                },
            },
            "projections": {
                "average_customer_lifetime_months": self.average_customer_lifetime_months,
                "target_cac_usd": self.target_cac_usd,
                "expected_churn_rate_monthly": self.expected_churn_rate_monthly,
                "sales_cycle_days_range": [
                    self.expected_sales_cycle_days,
                    self.conservative_sales_cycle_days,
                ],
            },
        }


# Default revenue model based on thread rollup
DEFAULT_REVENUE_MODEL = RevenueModel(
    base_tier=TierPricing(
        tier=PricingTier.BASE,
        monthly_price_usd=297.0,
        features=[
            "Core enforcement (JR Engine + Judge #6 Lite)",
            "Basic audit trails",
            "GDPR/CAN-SPAM compliance checks",
            "Email support",
        ],
        target_customer="SaaS companies with EU customers",
        expected_churn_rate=0.05,  # 5%/mo
    ),
    white_glove_tier=TierPricing(
        tier=PricingTier.WHITE_GLOVE,
        monthly_price_usd=997.0,
        features=[
            "All Base tier features",
            "Human review of audit trails",
            "Priority support",
            "Custom compliance rules (up to 10)",
            "PDF audit reports",
        ],
        target_customer="US healthcare (HIPAA compliance)",
        expected_churn_rate=0.03,  # 3%/mo
    ),
    enterprise_tier=TierPricing(
        tier=PricingTier.ENTERPRISE,
        monthly_price_usd=9970.0,
        features=[
            "All White-glove tier features",
            "Custom rules + legal review",
            "Unlimited compliance rules",
            "Dedicated account manager",
            "SLA guarantees",
            "SOC2/HIPAA documentation",
        ],
        target_customer="Financial services (SOC2/audit requirements)",
        expected_churn_rate=0.01,  # 1%/mo
    ),
    price_per_validated_lead=0.10,
    average_customer_lifetime_months=18,
    target_cac_usd=1000.0,
    expected_churn_rate_monthly=0.05,
    expected_sales_cycle_days=30,
    conservative_sales_cycle_days=90,
)


# Competitive baseline (for reference)
COMPETITIVE_BASELINE = {
    "godofprompt_ai": {
        "monthly_price_usd": 997.0,
        "features": [
            "Prompt templates",
            "Community access",
        ],
        "gaps": [
            "No enforcement",
            "No audit trails",
            "No compliance value",
        ],
    },
}
