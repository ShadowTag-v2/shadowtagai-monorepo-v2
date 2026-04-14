"""Revenue Tier Implementation

Implements Free/Pro/Enterprise tiers with feature gates and monetization hooks.

REVENUE MODEL:
- Free: Single mode selection (internal OR web), manual choice
- Pro: Automatic hybrid routing, seamless UX ($19.99/mo)
- Enterprise: Custom tool chains, SLA guarantees ($500+/mo)

MONETIZATION HOOKS:
- Usage tracking for billing
- Feature gates for tier enforcement
- Upsell triggers when free users hit limits
- A/B test framework for pricing optimization
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from pnkln.config.constants import LTV_CAC_MIN, ROI_TARGET, TIER_PRICING, QueryIntent, RevenueTier


# ============================================================================
# TIER DEFINITIONS
# ============================================================================
@dataclass
class TierFeatures:
    """Features available for each tier."""

    tier: str
    hybrid_routing: bool  # Auto-detect internal+web
    custom_tool_chains: bool  # Build custom workflows
    priority_support: bool  # SLA guarantees
    api_access: bool  # Programmatic access
    query_limit_monthly: int  # Query quota
    synthesis_enabled: bool  # Result synthesis
    analytics_dashboard: bool  # Usage insights


TIER_FEATURE_MATRIX = {
    RevenueTier.FREE: TierFeatures(
        tier=RevenueTier.FREE,
        hybrid_routing=False,
        custom_tool_chains=False,
        priority_support=False,
        api_access=False,
        query_limit_monthly=100,
        synthesis_enabled=False,
        analytics_dashboard=False,
    ),
    RevenueTier.PRO: TierFeatures(
        tier=RevenueTier.PRO,
        hybrid_routing=True,
        custom_tool_chains=False,
        priority_support=False,
        api_access=True,
        query_limit_monthly=10000,
        synthesis_enabled=True,
        analytics_dashboard=True,
    ),
    RevenueTier.ENTERPRISE: TierFeatures(
        tier=RevenueTier.ENTERPRISE,
        hybrid_routing=True,
        custom_tool_chains=True,
        priority_support=True,
        api_access=True,
        query_limit_monthly=1000000,
        synthesis_enabled=True,
        analytics_dashboard=True,
    ),
}


# ============================================================================
# USAGE TRACKING
# ============================================================================
@dataclass
class UsageRecord:
    """Single usage event."""

    user_id: str
    timestamp: datetime
    query: str
    intent: str
    tier: str
    cost_usd: float
    latency_ms: float


class UsageTracker:
    """Tracks usage for billing and upsell triggers.

    CRITICAL: This is the revenue engine data source.
    Must be reliable, auditable, and tamper-proof.
    """

    def __init__(self):
        """Initialize tracker."""
        self.records: list[UsageRecord] = []
        self._user_quotas: dict[str, int] = {}  # user_id -> remaining quota

    def record_usage(
        self, user_id: str, query: str, intent: str, tier: str, cost_usd: float, latency_ms: float,
    ) -> None:
        """Record a usage event.

        Args:
            user_id: User identifier
            query: Query executed
            intent: QueryIntent (internal/web/hybrid)
            tier: User's revenue tier
            cost_usd: Cost of this query
            latency_ms: Execution latency

        """
        record = UsageRecord(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            query=query,
            intent=intent,
            tier=tier,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
        )

        self.records.append(record)

        # Decrement quota
        if user_id not in self._user_quotas:
            features = TIER_FEATURE_MATRIX[tier]
            self._user_quotas[user_id] = features.query_limit_monthly

        self._user_quotas[user_id] -= 1

    def get_remaining_quota(self, user_id: str, tier: str) -> int:
        """Get remaining monthly quota for user."""
        if user_id not in self._user_quotas:
            features = TIER_FEATURE_MATRIX[tier]
            return features.query_limit_monthly

        return max(0, self._user_quotas[user_id])

    def has_quota(self, user_id: str, tier: str) -> bool:
        """Check if user has remaining quota."""
        return self.get_remaining_quota(user_id, tier) > 0

    def get_user_usage(self, user_id: str, start_date: datetime | None = None) -> list[UsageRecord]:
        """Get usage records for user."""
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=30)

        return [r for r in self.records if r.user_id == user_id and r.timestamp >= start_date]

    def calculate_bill(self, user_id: str, tier: str) -> dict:
        """Calculate monthly bill for user.

        Returns:
            Dict with base_price, usage_charges, total, query_count

        """
        # Get current month usage
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        usage = self.get_user_usage(user_id, month_start)

        base_price = TIER_PRICING[tier]
        usage_charges = sum(r.cost_usd for r in usage)
        total = base_price + usage_charges

        return {
            "user_id": user_id,
            "tier": tier,
            "base_price_usd": base_price,
            "usage_charges_usd": usage_charges,
            "total_usd": total,
            "query_count": len(usage),
            "period_start": month_start.isoformat(),
            "period_end": datetime.utcnow().isoformat(),
        }


# ============================================================================
# FEATURE GATES
# ============================================================================
class FeatureGate:
    """Enforces tier-based feature access.

    CRITICAL: This protects revenue by blocking free users
    from premium features.
    """

    @staticmethod
    def check_hybrid_access(tier: str) -> bool:
        """Check if tier has hybrid routing access."""
        features = TIER_FEATURE_MATRIX[tier]
        return features.hybrid_routing

    @staticmethod
    def check_api_access(tier: str) -> bool:
        """Check if tier has API access."""
        features = TIER_FEATURE_MATRIX[tier]
        return features.api_access

    @staticmethod
    def check_custom_chains(tier: str) -> bool:
        """Check if tier has custom tool chain access."""
        features = TIER_FEATURE_MATRIX[tier]
        return features.custom_tool_chains

    @staticmethod
    def get_features(tier: str) -> TierFeatures:
        """Get all features for tier."""
        return TIER_FEATURE_MATRIX[tier]

    @staticmethod
    def validate_request(tier: str, intent: str, user_id: str, tracker: UsageTracker) -> dict:
        """Validate if request is allowed for tier.

        Returns:
            Dict with allowed (bool), reason (str), upsell_trigger (bool)

        """
        # Check quota
        if not tracker.has_quota(user_id, tier):
            return {
                "allowed": False,
                "reason": f"Monthly quota exceeded for {tier} tier",
                "upsell_trigger": True,
                "upsell_message": (
                    "Upgrade to Pro for 10,000 queries/month "
                    f"(currently {TIER_FEATURE_MATRIX[tier].query_limit_monthly})"
                ),
            }

        # Check hybrid access
        if intent == QueryIntent.HYBRID and not FeatureGate.check_hybrid_access(tier):
            return {
                "allowed": False,
                "reason": "Hybrid routing requires Pro tier",
                "upsell_trigger": True,
                "upsell_message": (
                    "Upgrade to Pro ($19.99/mo) for automatic hybrid routing. "
                    "Free tier: choose Internal OR Web manually."
                ),
            }

        return {"allowed": True, "reason": "Request authorized", "upsell_trigger": False}


# ============================================================================
# MONETIZATION ANALYTICS
# ============================================================================
class RevenueAnalytics:
    """Analytics for revenue optimization and bootstrap validation.

    CRITICAL: Must validate ROI ≥3× (18mo) and LTV:CAC ≥4:1 (12mo)
    """

    @staticmethod
    def calculate_ltv(
        avg_monthly_revenue: float, avg_customer_lifetime_months: float, gross_margin: float = 0.80,
    ) -> float:
        """Calculate customer lifetime value.

        Args:
            avg_monthly_revenue: Average monthly revenue per customer
            avg_customer_lifetime_months: Average retention period
            gross_margin: Gross profit margin (default: 80%)

        Returns:
            LTV in USD

        """
        return avg_monthly_revenue * avg_customer_lifetime_months * gross_margin

    @staticmethod
    def calculate_cac(total_acquisition_cost: float, customers_acquired: int) -> float:
        """Calculate customer acquisition cost.

        Args:
            total_acquisition_cost: Total spent on acquisition
            customers_acquired: Number of customers acquired

        Returns:
            CAC in USD

        """
        if customers_acquired == 0:
            return 0.0
        return total_acquisition_cost / customers_acquired

    @staticmethod
    def validate_bootstrap_gates(ltv: float, cac: float, roi_18mo: float) -> dict:
        """Validate against bootstrap discipline gates.

        Gates:
        - ROI ≥3× in 18 months
        - LTV:CAC ≥4:1 in 12 months

        Returns:
            Dict with pass/fail and recommendations

        """
        ltv_cac_ratio = ltv / cac if cac > 0 else 0

        gates = {
            "roi_gate": {"target": ROI_TARGET, "actual": roi_18mo, "pass": roi_18mo >= ROI_TARGET},
            "ltv_cac_gate": {
                "target": LTV_CAC_MIN,
                "actual": ltv_cac_ratio,
                "pass": ltv_cac_ratio >= LTV_CAC_MIN,
            },
        }

        all_pass = all(g["pass"] for g in gates.values())

        recommendation = ""
        if not all_pass:
            if not gates["roi_gate"]["pass"]:
                recommendation += f"⚠️  ROI {roi_18mo:.1f}× < {ROI_TARGET}× target. "
                recommendation += "Reduce costs or increase revenue. "

            if not gates["ltv_cac_gate"]["pass"]:
                recommendation += f"⚠️  LTV:CAC {ltv_cac_ratio:.1f}:1 < {LTV_CAC_MIN}:1 target. "
                recommendation += "Improve retention or reduce acquisition costs. "

        return {
            "gates": gates,
            "all_pass": all_pass,
            "recommendation": recommendation.strip()
            if recommendation
            else "✅ All bootstrap gates passed",
        }

    @staticmethod
    def calculate_pricing_optimization(usage_data: list[UsageRecord], current_price: float) -> dict:
        """Suggest pricing optimization based on usage patterns.

        Uses Van Westendorp Price Sensitivity Meter approach.
        """
        # Placeholder for A/B test framework
        # In production, this analyzes:
        # - Price elasticity
        # - Feature usage by tier
        # - Upgrade conversion rates
        # - Churn correlation with pricing

        return {
            "current_price": current_price,
            "suggested_price_range": (15.00, 24.99),
            "optimal_price": 19.99,
            "confidence": 0.75,
            "test_variants": [
                {"price": 14.99, "expected_conversion_lift": 0.15},
                {"price": 19.99, "expected_conversion_lift": 0.00},  # Control
                {"price": 24.99, "expected_conversion_lift": -0.08},
            ],
        }


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================
_tracker = UsageTracker()


def get_usage_tracker() -> UsageTracker:
    """Get global usage tracker instance."""
    return _tracker
