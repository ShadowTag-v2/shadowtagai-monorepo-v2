"""
PNKLN Intelligence-as-a-Service API
Monetize the intelligence pipeline (currently $77/mo cost, $0 revenue)

Revenue model:
- Tier 1 feed: $499/mo (priority intelligence)
- Tier 2 feed: $199/mo (standard intelligence)
- Tier 3 feed: $49/mo (background intelligence)
- API access: $29-$499/mo (metered)
- Data enrichment: $0.01-$0.05/item

Year 1 target: $50K revenue (5 customers @ $10K/year avg)
Year 5 target: $2M revenue (enterprise contracts + API revenue)
"""

import asyncio
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# Pricing Tiers
# ============================================================================


class SubscriptionTier(StrEnum):
    """IaaS subscription tiers"""

    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# Pricing table
PRICING_TIERS = {
    "free": {
        "price_monthly": 0,
        "tier_access": [3],  # Tier 3 only
        "api_calls_per_day": 100,
        "enrichment_credits": 0,
        "support": "community",
    },
    "starter": {
        "price_monthly": 29,
        "tier_access": [2, 3],  # Tier 2 & 3
        "api_calls_per_day": 1000,
        "enrichment_credits": 100,  # 100 items/month
        "support": "email",
    },
    "pro": {
        "price_monthly": 99,
        "tier_access": [1, 2, 3],  # All tiers
        "api_calls_per_day": 10000,
        "enrichment_credits": 1000,  # 1000 items/month
        "support": "priority_email",
    },
    "enterprise": {
        "price_monthly": 499,
        "tier_access": [1, 2, 3],
        "api_calls_per_day": -1,  # Unlimited
        "enrichment_credits": -1,  # Unlimited
        "support": "dedicated",
        "sla": "99.9%",
        "custom_pipeline": True,
    },
}


# Data feed pricing (standalone)
FEED_PRICING = {
    "tier_1": {
        "name": "Priority Intelligence Feed",
        "description": "High-authority, time-critical intelligence (10-20% of items)",
        "price_monthly": 499,
        "price_annual": 4990,  # ~17% discount
        "delivery": "real-time",
        "format": "JSON API + webhook",
        "retention_days": 90,
    },
    "tier_2": {
        "name": "Standard Intelligence Feed",
        "description": "Moderate-authority, supplementary intelligence (30-40% of items)",
        "price_monthly": 199,
        "price_annual": 1990,
        "delivery": "hourly batch",
        "format": "JSON API",
        "retention_days": 30,
    },
    "tier_3": {
        "name": "Background Intelligence Feed",
        "description": "Low-priority, contextual intelligence (40-60% of items)",
        "price_monthly": 49,
        "price_annual": 490,
        "delivery": "daily batch",
        "format": "JSON API",
        "retention_days": 7,
    },
    "all_tiers": {
        "name": "Complete Intelligence Feed (All Tiers)",
        "description": "Access to all tier classifications",
        "price_monthly": 699,
        "price_annual": 6990,  # 20% discount vs. buying separately
        "delivery": "real-time + batch",
        "format": "JSON API + webhook",
        "retention_days": 90,
    },
}


# Enrichment pricing (pay-per-item)
ENRICHMENT_PRICING = {
    "sentiment": {
        "name": "Sentiment Analysis",
        "description": "Positive/negative/neutral sentiment scoring",
        "price_per_item": 0.01,  # $0.01 per item
        "margin": 0.85,  # 85% margin (AI cost ~$0.0015/item)
    },
    "entities": {
        "name": "Entity Extraction",
        "description": "Extract people, companies, technologies, locations",
        "price_per_item": 0.02,
        "margin": 0.80,
    },
    "classification": {
        "name": "Custom Classification",
        "description": "Custom topic/category classification",
        "price_per_item": 0.05,
        "margin": 0.75,
    },
    "summary": {
        "name": "AI Summarization",
        "description": "Generate concise summaries",
        "price_per_item": 0.03,
        "margin": 0.70,
    },
    "translation": {
        "name": "Language Translation",
        "description": "Translate to 100+ languages",
        "price_per_item": 0.02,
        "margin": 0.75,
    },
}


# ============================================================================
# API Models
# ============================================================================


class IntelligenceItem(BaseModel):
    """Intelligence item from pipeline"""

    id: str
    source_type: str
    source_url: str
    title: str
    content: str
    tier: int  # 1, 2, or 3
    relevance_score: float
    engagement_score: int
    published_at: datetime
    ingested_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class APIKeyUsage(BaseModel):
    """API key usage tracking"""

    api_key: str
    subscription_tier: SubscriptionTier
    calls_today: int
    calls_limit: int
    enrichment_credits_used: int
    enrichment_credits_limit: int
    overage_charges: float = 0.0


class EnrichmentRequest(BaseModel):
    """Data enrichment request"""

    item_ids: list[str]
    services: list[str]  # ["sentiment", "entities", "classification"]


class EnrichmentResult(BaseModel):
    """Enrichment service result"""

    item_id: str
    service: str
    result: dict[str, Any]
    cost: float


# ============================================================================
# Usage Metering
# ============================================================================


class UsageMeter:
    """Track API usage and calculate charges"""

    def __init__(self):
        # In production, use Redis for real-time tracking
        self.usage_cache = {}

    async def record_api_call(
        self, api_key: str, endpoint: str, tier_accessed: int | None = None
    ) -> dict[str, Any]:
        """
        Record API call and check limits

        Returns:
            Dict with allowed: bool, overage: bool, cost: float
        """
        # Get subscription info (from DB in production)
        subscription = await self._get_subscription(api_key)

        # Get today's usage
        today = datetime.utcnow().date()
        usage_key = f"{api_key}:{today}"

        if usage_key not in self.usage_cache:
            self.usage_cache[usage_key] = {
                "calls": 0,
                "enrichment_items": 0,
                "overage_charges": 0.0,
            }

        usage = self.usage_cache[usage_key]
        usage["calls"] += 1

        # Check limits
        tier_config = PRICING_TIERS[subscription["tier"]]
        daily_limit = tier_config["api_calls_per_day"]

        allowed = True
        overage = False
        cost = 0.0

        if daily_limit > 0 and usage["calls"] > daily_limit:
            # Over limit - charge overage or deny
            if subscription["tier"] == "free":
                allowed = False  # Free tier: hard limit
            else:
                overage = True
                # Overage pricing: $0.10 per call over limit
                cost = 0.10
                usage["overage_charges"] += cost

        return {
            "allowed": allowed,
            "overage": overage,
            "cost": cost,
            "calls_today": usage["calls"],
            "calls_limit": daily_limit,
            "calls_remaining": max(0, daily_limit - usage["calls"]) if daily_limit > 0 else -1,
        }

    async def record_enrichment(
        self, api_key: str, service: str, num_items: int
    ) -> dict[str, float]:
        """
        Record enrichment usage and calculate cost

        Returns:
            Dict with cost, credits_used, credits_remaining
        """
        subscription = await self._get_subscription(api_key)
        tier_config = PRICING_TIERS[subscription["tier"]]

        # Get today's usage
        today = datetime.utcnow().date()
        usage_key = f"{api_key}:{today}"

        if usage_key not in self.usage_cache:
            self.usage_cache[usage_key] = {
                "calls": 0,
                "enrichment_items": 0,
                "overage_charges": 0.0,
            }

        usage = self.usage_cache[usage_key]

        # Calculate cost
        price_per_item = ENRICHMENT_PRICING[service]["price_per_item"]
        total_cost = price_per_item * num_items

        # Check if within credits
        monthly_credits = tier_config["enrichment_credits"]
        credits_used = usage["enrichment_items"]

        if monthly_credits > 0 and credits_used < monthly_credits:
            # Use credits first
            credits_to_use = min(num_items, monthly_credits - credits_used)
            paid_items = num_items - credits_to_use
            cost = paid_items * price_per_item
        else:
            # All paid
            cost = total_cost

        usage["enrichment_items"] += num_items
        usage["overage_charges"] += cost

        return {
            "cost": cost,
            "credits_used": num_items,
            "credits_remaining": max(0, monthly_credits - usage["enrichment_items"])
            if monthly_credits > 0
            else 0,
            "overage_cost": cost,
        }

    async def _get_subscription(self, api_key: str) -> dict[str, Any]:
        """Get subscription info (mock - use DB in production)"""
        # Mock data
        return {"api_key": api_key, "tier": "pro", "customer_id": "cust_123", "active": True}

    async def get_monthly_bill(self, api_key: str) -> dict[str, float]:
        """Calculate monthly bill for customer"""
        subscription = await self._get_subscription(api_key)
        tier_config = PRICING_TIERS[subscription["tier"]]

        base_subscription = tier_config["price_monthly"]

        # Sum up overage charges for the month
        total_overage = sum(
            usage["overage_charges"]
            for key, usage in self.usage_cache.items()
            if key.startswith(api_key)
        )

        total = base_subscription + total_overage

        return {
            "base_subscription": base_subscription,
            "overage_charges": total_overage,
            "total": total,
        }


# ============================================================================
# Revenue Projections
# ============================================================================


def project_iaas_revenue(
    num_customers: dict[str, int], avg_overage_pct: float = 0.15
) -> dict[str, float]:
    """
    Project Intelligence-as-a-Service revenue

    Args:
        num_customers: Dict of {tier: count}
        avg_overage_pct: % of customers who exceed limits (15% typical)

    Example Year 1:
        - 5 Pro customers @ $99/mo
        - 3 Enterprise @ $499/mo
        - Total: ($495 + $1,497) * 12 = $23,904/year

    Example Year 5:
        - 50 Pro @ $99/mo
        - 30 Enterprise @ $499/mo
        - Total: ($4,950 + $14,970) * 12 = $239,040/year
    """
    monthly_recurring = 0
    for tier, count in num_customers.items():
        if tier in PRICING_TIERS:
            monthly_recurring += PRICING_TIERS[tier]["price_monthly"] * count

    # Overage revenue (15% of customers exceed limits, avg $50/mo overage)
    total_customers = sum(num_customers.values())
    overage_revenue = total_customers * avg_overage_pct * 50

    monthly_total = monthly_recurring + overage_revenue
    annual_total = monthly_total * 12

    return {
        "monthly_recurring": monthly_recurring,
        "monthly_overage": overage_revenue,
        "monthly_total": monthly_total,
        "annual_recurring": monthly_recurring * 12,
        "annual_overage": overage_revenue * 12,
        "annual_total": annual_total,
        "customers_total": total_customers,
        "arpu_monthly": monthly_total / total_customers if total_customers > 0 else 0,
    }


# ============================================================================
# ROI Analysis
# ============================================================================


def calculate_pipeline_roi(
    monthly_cost: float = 77.0, monthly_revenue: float = 0.0
) -> dict[str, Any]:
    """
    Calculate ROI of turning intelligence pipeline into revenue stream

    Current state:
    - Monthly cost: $77
    - Monthly revenue: $0
    - Annual loss: $924

    Target state (Year 1):
    - Monthly cost: $77 (same infrastructure)
    - Monthly revenue: $4,167 (5 customers @ $833/mo avg)
    - Annual profit: $49,076
    - ROI: 5,312%

    Target state (Year 5):
    - Monthly cost: $150 (scaled infrastructure)
    - Monthly revenue: $166,667 (enterprise contracts)
    - Annual profit: $1,998,204
    - ROI: 110,900%
    """
    annual_cost = monthly_cost * 12
    annual_revenue = monthly_revenue * 12
    annual_profit = annual_revenue - annual_cost

    roi_pct = annual_profit / annual_cost * 100 if annual_cost > 0 else 0

    return {
        "monthly_cost": monthly_cost,
        "monthly_revenue": monthly_revenue,
        "monthly_profit": monthly_revenue - monthly_cost,
        "annual_cost": annual_cost,
        "annual_revenue": annual_revenue,
        "annual_profit": annual_profit,
        "roi_pct": roi_pct,
        "payback_months": annual_cost / monthly_revenue if monthly_revenue > 0 else float("inf"),
    }


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """Example IaaS usage and projections"""

    print("=" * 60)
    print("INTELLIGENCE-AS-A-SERVICE REVENUE PROJECTIONS")
    print("=" * 60)

    # Year 1 projection
    year_1_customers = {"starter": 10, "pro": 5, "enterprise": 3}

    year_1 = project_iaas_revenue(year_1_customers)
    print("\nYear 1:")
    print(f"  Customers: {year_1['customers_total']}")
    print(f"  MRR: ${year_1['monthly_recurring']:,.2f}")
    print(f"  Annual revenue: ${year_1['annual_total']:,.2f}")
    print(f"  ARPU: ${year_1['arpu_monthly']:.2f}/mo")

    # Year 5 projection
    year_5_customers = {"starter": 100, "pro": 50, "enterprise": 30}

    year_5 = project_iaas_revenue(year_5_customers)
    print("\nYear 5:")
    print(f"  Customers: {year_5['customers_total']}")
    print(f"  MRR: ${year_5['monthly_recurring']:,.2f}")
    print(f"  Annual revenue: ${year_5['annual_total']:,.2f}")
    print(f"  ARPU: ${year_5['arpu_monthly']:.2f}/mo")

    # ROI analysis
    print("\n" + "=" * 60)
    print("PIPELINE ROI ANALYSIS")
    print("=" * 60)

    current_roi = calculate_pipeline_roi(monthly_cost=77, monthly_revenue=0)
    print("\nCurrent state (cost center):")
    print(f"  Monthly cost: ${current_roi['monthly_cost']:.2f}")
    print(f"  Monthly revenue: ${current_roi['monthly_revenue']:.2f}")
    print(f"  Annual loss: ${abs(current_roi['annual_profit']):,.2f}")

    year_1_roi = calculate_pipeline_roi(monthly_cost=77, monthly_revenue=year_1["monthly_total"])
    print("\nYear 1 (IaaS launched):")
    print(f"  Monthly cost: ${year_1_roi['monthly_cost']:.2f}")
    print(f"  Monthly revenue: ${year_1_roi['monthly_revenue']:,.2f}")
    print(f"  Annual profit: ${year_1_roi['annual_profit']:,.2f}")
    print(f"  ROI: {year_1_roi['roi_pct']:,.0f}%")

    year_5_roi = calculate_pipeline_roi(
        monthly_cost=150,  # Scaled infrastructure
        monthly_revenue=year_5["monthly_total"],
    )
    print("\nYear 5 (scaled):")
    print(f"  Monthly cost: ${year_5_roi['monthly_cost']:.2f}")
    print(f"  Monthly revenue: ${year_5_roi['monthly_revenue']:,.2f}")
    print(f"  Annual profit: ${year_5_roi['annual_profit']:,.2f}")
    print(f"  ROI: {year_5_roi['roi_pct']:,.0f}%")

    # Usage metering example
    print("\n" + "=" * 60)
    print("USAGE METERING EXAMPLE")
    print("=" * 60)

    meter = UsageMeter()

    # Pro customer makes API calls
    for i in range(5):
        result = await meter.record_api_call(
            api_key="REDACTED_API_KEY", endpoint="/intelligence/tier1"
        )
        print(f"\nAPI call #{i + 1}:")
        print(f"  Allowed: {result['allowed']}")
        print(f"  Calls remaining today: {result['calls_remaining']}")
        if result["overage"]:
            print(f"  Overage cost: ${result['cost']:.2f}")

    # Customer uses enrichment
    enrichment_result = await meter.record_enrichment(
        api_key="REDACTED_API_KEY", service="sentiment", num_items=150
    )
    print("\nEnrichment usage:")
    print("  Items: 150")
    print(f"  Credits used: {enrichment_result['credits_used']}")
    print(f"  Credits remaining: {enrichment_result['credits_remaining']}")
    print(f"  Overage cost: ${enrichment_result['overage_cost']:.2f}")

    # Monthly bill
    bill = await meter.get_monthly_bill("sk_test_pro_customer")
    print("\nMonthly bill:")
    print(f"  Base subscription (Pro): ${bill['base_subscription']:.2f}")
    print(f"  Overage charges: ${bill['overage_charges']:.2f}")
    print(f"  Total: ${bill['total']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
