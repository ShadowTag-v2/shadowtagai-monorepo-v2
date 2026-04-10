"""
Revenue Tracker: Turn AI operations into $ insights.

Every interaction is a potential revenue opportunity.
Track, measure, optimize.

Philosophy: You can't optimize what you don't measure.
"""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class OpportunityType(StrEnum):
    """Types of revenue opportunities."""

    UPSELL = "upsell"  # Premium tier, more features
    CROSS_SELL = "cross_sell"  # Related product/service
    TIME_SAVED = "time_saved"  # Automation value
    ERROR_PREVENTION = "error_prevention"  # Avoided cost
    PERFORMANCE_GAIN = "performance_gain"  # Efficiency boost
    NEW_FEATURE = "new_feature"  # Product gap


class RevenueOpportunity(BaseModel):
    """Single revenue opportunity detected."""

    type: OpportunityType
    value_usd: float = Field(description="Estimated revenue or cost savings")
    confidence: float = Field(ge=0.0, le=1.0)
    description: str
    action: str = Field(description="Recommended next step")
    priority: int = Field(ge=1, le=10)
    detected_at: datetime = Field(default_factory=datetime.now)


class UsageMetrics(BaseModel):
    """Usage metrics for monetization analysis."""

    total_requests: int = 0
    reasoning_requests: int = 0  # CoT, ToT, MAD
    agent_collaborations: int = 0
    avg_latency_ms: float = 0.0
    tokens_consumed: int = 0
    compute_cost_usd: float = 0.0


class RevenueTracker:
    """
    Track and identify revenue opportunities.

    Usage:
        tracker = RevenueTracker()

        # Analyze a conversation
        opportunities = tracker.analyze_conversation([
            {"role": "user", "content": "I need to process 1M records daily"},
            {"role": "assistant", "content": "Current solution: manual CSV uploads"}
        ])
        # → Detects: automation opportunity, potential enterprise upsell

        # Track usage
        tracker.log_request(endpoint="/analyze", reasoning="MAD", latency=1200)
        metrics = tracker.get_metrics()
        # → Shows heavy usage of premium features → upsell opportunity

    Revenue opportunities:
    - Heavy API users without paid tier
    - Advanced feature usage (multi-agent, ToT) → premium
    - Time saved via automation → calculate ROI, show value
    - Error patterns → offer support/consulting
    - Performance issues → infrastructure upsell
    """

    def __init__(self):
        """Initialize revenue tracker."""
        self.opportunities: list[RevenueOpportunity] = []
        self.metrics = UsageMetrics()

    def analyze_conversation(self, messages: list[dict]) -> list[RevenueOpportunity]:
        """
        Analyze conversation for revenue signals.

        Args:
            messages: List of {role, content} message dicts

        Returns:
            List of detected opportunities
        """
        opportunities = []

        # Join all messages
        full_text = " ".join(m.get("content", "") for m in messages).lower()

        # Pattern detection (placeholder - would use NLP/LLM in production)

        # 1. Scale signals → enterprise tier
        scale_keywords = [
            "million",
            "thousands",
            "scale",
            "production",
            "enterprise",
            "team",
            "company",
        ]
        if any(kw in full_text for kw in scale_keywords):
            opportunities.append(
                RevenueOpportunity(
                    type=OpportunityType.UPSELL,
                    value_usd=5000.0,  # Enterprise tier price
                    confidence=0.7,
                    description="User mentions scale/team → enterprise candidate",
                    action="Offer enterprise demo + custom pricing",
                    priority=8,
                )
            )

        # 2. Time-saving automation
        time_keywords = ["manual", "hours", "daily", "repetitive", "automate"]
        if any(kw in full_text for kw in time_keywords):
            # Calculate time saved → $$$
            estimated_hours_saved = 40  # per month
            hourly_rate = 75  # typical developer rate
            monthly_value = estimated_hours_saved * hourly_rate

            opportunities.append(
                RevenueOpportunity(
                    type=OpportunityType.TIME_SAVED,
                    value_usd=monthly_value,
                    confidence=0.8,
                    description=f"Automation saves ~{estimated_hours_saved}h/month → ${monthly_value}",
                    action="Show ROI calculator: automation value vs. subscription cost",
                    priority=9,
                )
            )

        # 3. Feature requests → new product
        feature_keywords = ["wish", "would be great if", "feature request", "need"]
        if any(kw in full_text for kw in feature_keywords):
            opportunities.append(
                RevenueOpportunity(
                    type=OpportunityType.NEW_FEATURE,
                    value_usd=0.0,  # Future value
                    confidence=0.6,
                    description="User requesting feature not in current product",
                    action="Add to product roadmap, offer beta access for feedback",
                    priority=6,
                )
            )

        self.opportunities.extend(opportunities)
        return opportunities

    def log_request(
        self,
        endpoint: str,
        reasoning: Literal["CoT", "ToT", "RCR", "MAD"] | None = None,
        latency: float = 0.0,
        tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        """
        Log a request for usage analytics.

        Args:
            endpoint: API endpoint called
            reasoning: Reasoning strategy used (if any)
            latency: Response time in ms
            tokens: Tokens consumed
            cost_usd: Actual LLM cost (from LLMResponse)
        """
        self.metrics.total_requests += 1

        if reasoning:
            self.metrics.reasoning_requests += 1

            # Heavy reasoning usage → upsell to premium
            if self.metrics.reasoning_requests > 100 and self.metrics.total_requests < 150:
                # >66% usage of advanced features
                self.opportunities.append(
                    RevenueOpportunity(
                        type=OpportunityType.UPSELL,
                        value_usd=99.0,  # Monthly premium tier
                        confidence=0.85,
                        description="Heavy usage of advanced reasoning (66%+ of requests)",
                        action="Offer premium tier with unlimited reasoning",
                        priority=9,
                    )
                )

        # Update metrics
        total = self.metrics.total_requests
        self.metrics.avg_latency_ms = (self.metrics.avg_latency_ms * (total - 1) + latency) / total
        self.metrics.tokens_consumed += tokens

        # Cost tracking (use actual cost if provided, else estimate)
        if cost_usd > 0:
            self.metrics.compute_cost_usd += cost_usd
        else:
            # Fallback estimate
            # Claude Sonnet 4.5: ~$3/1M input, ~$15/1M output
            # Assume 50/50 split
            token_cost = (tokens / 1_000_000) * 9.0
            self.metrics.compute_cost_usd += token_cost

    def get_metrics(self) -> UsageMetrics:
        """Get current usage metrics."""
        return self.metrics

    def get_opportunities(
        self, min_priority: int = 1, min_confidence: float = 0.0
    ) -> list[RevenueOpportunity]:
        """
        Get detected revenue opportunities.

        Args:
            min_priority: Minimum priority (1-10)
            min_confidence: Minimum confidence (0-1)

        Returns:
            Filtered list of opportunities, sorted by value
        """
        filtered = [
            opp
            for opp in self.opportunities
            if opp.priority >= min_priority and opp.confidence >= min_confidence
        ]

        # Sort by value (highest first)
        return sorted(filtered, key=lambda x: x.value_usd, reverse=True)

    def calculate_roi(self) -> dict:
        """
        Calculate ROI for the service.

        Returns:
            Dict with revenue, cost, ROI ratio
        """
        total_opportunity_value = sum(opp.value_usd for opp in self.opportunities)
        compute_cost = self.metrics.compute_cost_usd

        roi = total_opportunity_value / compute_cost if compute_cost > 0 else float("inf")

        return {
            "total_opportunity_value_usd": total_opportunity_value,
            "compute_cost_usd": compute_cost,
            "roi_ratio": roi,
            "opportunities_count": len(self.opportunities),
        }

    def __repr__(self) -> str:
        return (
            f"RevenueTracker(requests={self.metrics.total_requests}, "
            f"opportunities={len(self.opportunities)})"
        )
