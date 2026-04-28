# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""WEALTH OPTIMIZER - Jobs-Obsessed Financial Engineering
=======================================================

PHILOSOPHY (Steve Jobs + Wealth Planning):
- "Focus means saying no to 1000 things" → Spot leaks (wasted spend)
- "Design is how it works" → Redesign funnels (optimize flows)
- "Think different" → Leverage viral/conversion (compound effects)

STRUCTURE: Hard Truth → Plan → Challenge
- HARD TRUTH: Brutal honesty about current state (Jobs: reality-based)
- PLAN: Specific actionable steps to improve
- CHALLENGE: Question assumptions, find edge cases

THE 3 WEALTH LENSES:
=====================
1. LEAKS: Where are we bleeding money/value?
   - Wasted API calls (duplicate items, low-value sources)
   - Inefficient timing (peak pricing vs off-peak)
   - Poor tier classification (Tier 3 items at Tier 1 cost)
   - Over-collection (collecting more than customers use)

2. REDESIGN: How can we restructure for 10x better?
   - Funnel optimization (more Tier 1 per dollar spent)
   - Upsell opportunities (premium tiers, custom sources)
   - Recurring revenue (subscriptions vs one-time)
   - Conversion rate (free trial → paid)

3. LEVERAGE: What compounds over time?
   - Viral effects (customers refer others)
   - Data moat (accumulated intelligence)
   - Network effects (more sources → better insights)
   - Brand (Jobs-quality reputation)

INTEGRATION WITH INGESTION:
============================
- Analyze every ingestion job for leaks
- Propose redesigns for funnel improvement
- Identify leverage opportunities
- Track wealth metrics over time
- Report: Hard truth → Plan → Challenge
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class WealthLens(StrEnum):
    """The 3 wealth analysis lenses"""

    LEAKS = "leaks"  # Waste detection
    REDESIGN = "redesign"  # Funnel optimization
    LEVERAGE = "leverage"  # Compounding effects


class LeakSeverity(StrEnum):
    """Severity of detected leak"""

    CRITICAL = "critical"  # >20% waste
    HIGH = "high"  # 10-20% waste
    MEDIUM = "medium"  # 5-10% waste
    LOW = "low"  # <5% waste


@dataclass
class Leak:
    """A detected leak (wasted money/value).

    Jobs: "Focus is about saying no to 1000 things."
    Every leak is something we should say no to.
    """

    leak_type: str  # "duplicate_items", "low_value_source", "peak_pricing", etc.
    severity: LeakSeverity
    cost_per_month: float  # Wasted cost
    percentage_of_total: float  # Waste as % of total spend
    description: str  # What's happening
    evidence: dict[str, Any]  # Supporting data
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def to_hard_truth(self) -> str:
        """Convert to brutal honesty statement (Jobs style)"""
        return (
            f"💸 {self.leak_type.upper()}: Wasting ${self.cost_per_month:.2f}/month "
            f"({self.percentage_of_total:.1%} of total spend). "
            f"{self.description}"
        )


@dataclass
class RedesignProposal:
    """A proposed funnel redesign for 10x improvement.

    Jobs: "Design is not just what it looks like, design is how it works."
    """

    redesign_type: str  # "source_reallocation", "tier_upsell", "subscription", etc.
    impact_category: str  # "cost_reduction", "revenue_increase", "both"
    projected_gain: float  # $ per month
    projected_roi: float  # Return on investment (gain / cost)
    implementation_cost: float  # One-time cost
    implementation_time_weeks: int  # Time to implement
    description: str  # What to do
    steps: list[str]  # Specific actions
    risks: list[str]  # What could go wrong

    def to_plan(self) -> str:
        """Convert to actionable plan"""
        steps_str = "\n".join([f"  {i + 1}. {step}" for i, step in enumerate(self.steps)])
        return (
            f"💡 {self.redesign_type.upper()}\n"
            f"Impact: ${self.projected_gain:.2f}/month ({self.impact_category})\n"
            f"ROI: {self.projected_roi:.1f}x\n"
            f"Cost: ${self.implementation_cost:.2f}, {self.implementation_time_weeks} weeks\n"
            f"Steps:\n{steps_str}"
        )


@dataclass
class LeverageOpportunity:
    """A compounding leverage opportunity.

    Jobs: "Innovation distinguishes between a leader and a follower."
    Find what compounds exponentially.
    """

    opportunity_type: str  # "viral_referral", "data_moat", "network_effect", etc.
    compound_rate: float  # Growth rate per period (e.g., 1.2 = 20% per month)
    initial_value: float  # Starting value
    projected_1yr_value: float  # Value after 1 year compounding
    projected_3yr_value: float  # Value after 3 years compounding
    activation_requirements: list[str]  # What's needed to activate
    description: str

    def to_challenge(self) -> str:
        """Convert to challenge question (question assumptions)"""
        return (
            f"🚀 {self.opportunity_type.upper()}\n"
            f"Compound rate: {(self.compound_rate - 1) * 100:.1f}% per period\n"
            f"1-year value: ${self.projected_1yr_value:,.0f}\n"
            f"3-year value: ${self.projected_3yr_value:,.0f}\n"
            f"Challenge: {self.description}\n"
            f"Requirements: {', '.join(self.activation_requirements)}"
        )


@dataclass
class WealthAnalysis:
    """Complete wealth analysis: Leaks + Redesign + Leverage.

    Structure: Hard Truth → Plan → Challenge
    """

    analysis_id: str
    job_id: str  # Which ingestion job
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # 1. HARD TRUTH (Leaks)
    leaks: list[Leak] = field(default_factory=list)
    total_leak_cost: float = 0.0

    # 2. PLAN (Redesigns)
    redesigns: list[RedesignProposal] = field(default_factory=list)
    total_projected_gain: float = 0.0

    # 3. CHALLENGE (Leverage)
    leverage_opportunities: list[LeverageOpportunity] = field(default_factory=list)
    total_leverage_value: float = 0.0

    # Summary metrics
    net_monthly_improvement: float = 0.0  # Gain from redesigns - leak costs
    roi_on_improvements: float = 0.0

    def generate_report(self) -> str:
        """Generate full wealth analysis report (Jobs quality)"""
        lines = [
            "=" * 80,
            "WEALTH ANALYSIS REPORT",
            f"Job: {self.job_id}",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            "",
            "SECTION 1: HARD TRUTH (Leaks)",
            "-" * 80,
            "",
        ]

        if self.leaks:
            for leak in sorted(self.leaks, key=lambda l: l.cost_per_month, reverse=True):  # noqa: E741
                lines.append(leak.to_hard_truth())
                lines.append("")
            lines.append(f"💸 TOTAL MONTHLY LEAKS: ${self.total_leak_cost:.2f}")
        else:
            lines.append("✅ No significant leaks detected!")

        lines.extend(["", "", "SECTION 2: PLAN (Redesigns)", "-" * 80, ""])

        if self.redesigns:
            for redesign in sorted(self.redesigns, key=lambda r: r.projected_gain, reverse=True):
                lines.append(redesign.to_plan())
                lines.append("")
            lines.append(f"💡 TOTAL PROJECTED MONTHLY GAIN: ${self.total_projected_gain:.2f}")
        else:
            lines.append("Current design is optimal (no obvious improvements).")

        lines.extend(["", "", "SECTION 3: CHALLENGE (Leverage)", "-" * 80, ""])

        if self.leverage_opportunities:
            for opp in sorted(
                self.leverage_opportunities,
                key=lambda o: o.projected_3yr_value,
                reverse=True,
            ):
                lines.append(opp.to_challenge())
                lines.append("")
            lines.append(f"🚀 TOTAL 3-YEAR LEVERAGE VALUE: ${self.total_leverage_value:,.0f}")
        else:
            lines.append("No compounding opportunities identified yet.")

        lines.extend(
            [
                "",
                "",
                "SUMMARY",
                "=" * 80,
                f"Monthly leaks: -${self.total_leak_cost:.2f}",
                f"Monthly gains (redesigns): +${self.total_projected_gain:.2f}",
                f"Net monthly improvement: ${self.net_monthly_improvement:.2f}",
                f"3-year leverage value: ${self.total_leverage_value:,.0f}",
                f"ROI on improvements: {self.roi_on_improvements:.1f}x",
                "=" * 80,
            ],
        )

        return "\n".join(lines)


class WealthOptimizer:
    """Wealth Optimizer - Analyze ingestion jobs for leaks/redesign/leverage.

    Usage:
        optimizer = WealthOptimizer()
        analysis = await optimizer.analyze(ingestion_result)
        print(analysis.generate_report())
    """

    def __init__(self, target_tier_1_ratio: float = 0.40, target_cost_per_item: float = 0.015):
        """Initialize Wealth Optimizer.

        Args:
            target_tier_1_ratio: Target Tier 1 ratio (default 40%)
            target_cost_per_item: Target cost per item (default $0.015)

        """
        self.target_tier_1_ratio = target_tier_1_ratio
        self.target_cost_per_item = target_cost_per_item

        logger.info(
            f"WealthOptimizer initialized: target_tier_1={target_tier_1_ratio:.1%}, "
            f"target_cost={target_cost_per_item:.3f}",
        )

    async def analyze(
        self,
        ingestion_result: Any,  # IngestionResult from gemini_ingestion_layer
        historical_data: list[Any] | None = None,
    ) -> WealthAnalysis:
        """Perform complete wealth analysis on ingestion job.

        Args:
            ingestion_result: Result from ingestion job
            historical_data: Optional historical results for trend analysis

        Returns:
            WealthAnalysis with leaks/redesigns/leverage

        """
        analysis_id = f"wealth_{ingestion_result.job_id}"

        analysis = WealthAnalysis(analysis_id=analysis_id, job_id=ingestion_result.job_id)

        # 1. DETECT LEAKS (Hard Truth)
        analysis.leaks = await self._detect_leaks(ingestion_result)
        analysis.total_leak_cost = sum(leak.cost_per_month for leak in analysis.leaks)

        # 2. PROPOSE REDESIGNS (Plan)
        analysis.redesigns = await self._propose_redesigns(ingestion_result, analysis.leaks)
        analysis.total_projected_gain = sum(r.projected_gain for r in analysis.redesigns)

        # 3. IDENTIFY LEVERAGE (Challenge)
        analysis.leverage_opportunities = await self._identify_leverage(
            ingestion_result,
            historical_data,
        )
        analysis.total_leverage_value = sum(
            opp.projected_3yr_value for opp in analysis.leverage_opportunities
        )

        # Calculate summary metrics
        analysis.net_monthly_improvement = analysis.total_projected_gain - analysis.total_leak_cost

        total_implementation_cost = sum(r.implementation_cost for r in analysis.redesigns)
        if total_implementation_cost > 0:
            monthly_roi = analysis.net_monthly_improvement / total_implementation_cost
            analysis.roi_on_improvements = monthly_roi * 12  # Annualized

        logger.info(
            f"Wealth analysis complete: {len(analysis.leaks)} leaks, "
            f"{len(analysis.redesigns)} redesigns, {len(analysis.leverage_opportunities)} leverage opportunities",
        )

        return analysis

    async def _detect_leaks(self, result: Any) -> list[Leak]:
        """Detect all leaks in ingestion job"""
        leaks = []

        # Leak 1: Low Tier 1 ratio sources
        for source_type, metrics in result.source_metrics.items():
            if metrics.tier_1_ratio < self.target_tier_1_ratio:
                waste_percentage = self.target_tier_1_ratio - metrics.tier_1_ratio
                wasted_cost = metrics.total_cost_usd * waste_percentage
                monthly_cost = wasted_cost * 30  # Daily to monthly

                if monthly_cost > 1.0:  # Only flag if >$1/month
                    leak = Leak(
                        leak_type="low_tier_1_source",
                        severity=self._classify_severity(wasted_cost / metrics.total_cost_usd),
                        cost_per_month=monthly_cost,
                        percentage_of_total=waste_percentage,
                        description=f"Source {source_type.value} only achieving {metrics.tier_1_ratio:.1%} Tier 1 (target: {self.target_tier_1_ratio:.1%}). Wasting money on low-value items.",
                        evidence={
                            "source": source_type.value,
                            "tier_1_ratio": metrics.tier_1_ratio,
                            "target_ratio": self.target_tier_1_ratio,
                            "items_ingested": metrics.items_ingested,
                        },
                    )
                    leaks.append(leak)

        # Leak 2: High cost per item
        if result.avg_cost_per_item > self.target_cost_per_item:
            excess_cost = result.avg_cost_per_item - self.target_cost_per_item
            monthly_waste = excess_cost * result.total_items * 30
            waste_pct = excess_cost / result.avg_cost_per_item

            leak = Leak(
                leak_type="high_cost_per_item",
                severity=self._classify_severity(waste_pct),
                cost_per_month=monthly_waste,
                percentage_of_total=waste_pct,
                description=f"Cost per item ${result.avg_cost_per_item:.4f} exceeds target ${self.target_cost_per_item:.4f}. Likely inefficient API usage or expensive sources.",
                evidence={
                    "avg_cost_per_item": result.avg_cost_per_item,
                    "target_cost_per_item": self.target_cost_per_item,
                    "total_items": result.total_items,
                },
            )
            leaks.append(leak)

        # Leak 3: Duplicate detection (mock - would need real dedup logic)
        estimated_duplicates = int(result.total_items * 0.10)  # Assume 10% duplicates
        duplicate_cost = estimated_duplicates * result.avg_cost_per_item * 30

        if duplicate_cost > 5.0:  # Only flag if >$5/month
            leak = Leak(
                leak_type="duplicate_items",
                severity=LeakSeverity.MEDIUM,
                cost_per_month=duplicate_cost,
                percentage_of_total=0.10,
                description=f"Estimated {estimated_duplicates} duplicate items per day. No deduplication layer implemented.",
                evidence={
                    "estimated_duplicates": estimated_duplicates,
                    "total_items": result.total_items,
                },
            )
            leaks.append(leak)

        return leaks

    async def _propose_redesigns(self, result: Any, leaks: list[Leak]) -> list[RedesignProposal]:
        """Propose funnel redesigns to fix leaks and increase revenue"""
        redesigns = []

        # Redesign 1: Source reallocation (fix low Tier 1 ratio)
        low_tier_1_sources = [leak for leak in leaks if leak.leak_type == "low_tier_1_source"]

        if low_tier_1_sources:
            # Reallocate budget from low Tier 1 sources to high Tier 1 sources
            total_reallocatable = sum(leak.cost_per_month for leak in low_tier_1_sources)
            projected_gain = total_reallocatable * 0.5  # 50% improvement assumption

            redesign = RedesignProposal(
                redesign_type="source_reallocation",
                impact_category="cost_reduction",
                projected_gain=projected_gain,
                projected_roi=5.0,  # 5x ROI
                implementation_cost=500,  # Dev time to adjust source priorities
                implementation_time_weeks=1,
                description="Reallocate budget from low-performing sources to high Tier 1 ratio sources.",
                steps=[
                    f"Reduce collection from {len(low_tier_1_sources)} low-performing sources by 50%",
                    "Increase collection from top 2 high-performing sources by 30%",
                    "Monitor Tier 1 ratio improvement over 2 weeks",
                    "Fully deprecate sources with <20% Tier 1 ratio after validation",
                ],
                risks=[
                    "May lose unique insights from deprecated sources",
                    "Top sources might not scale linearly",
                ],
            )
            redesigns.append(redesign)

        # Redesign 2: Deduplication layer
        duplicate_leaks = [leak for leak in leaks if leak.leak_type == "duplicate_items"]
        if duplicate_leaks:
            total_waste = sum(leak.cost_per_month for leak in duplicate_leaks)
            projected_gain = total_waste * 0.80  # 80% reduction in duplicates

            redesign = RedesignProposal(
                redesign_type="deduplication_layer",
                impact_category="cost_reduction",
                projected_gain=projected_gain,
                projected_roi=10.0,
                implementation_cost=1200,  # Dev time for dedup logic
                implementation_time_weeks=2,
                description="Add content-based deduplication to eliminate duplicate items.",
                steps=[
                    "Implement content hash (SHA-256 on normalized text)",
                    "Build dedup cache (Redis, 90-day retention)",
                    "Add dedup check before tier classification (save cost)",
                    "Track dedup hit rate (target 10-15%)",
                ],
                risks=["Latency penalty (~5-10ms per item)", "Cache storage costs (~$5/month)"],
            )
            redesigns.append(redesign)

        # Redesign 3: Premium tier upsell (revenue increase)
        # If we're achieving >50% Tier 1 ratio, we can charge premium
        if result.tier_1_ratio >= 0.50:
            projected_arpu_increase = 1000  # +$1000/month per customer

            redesign = RedesignProposal(
                redesign_type="premium_tier_upsell",
                impact_category="revenue_increase",
                projected_gain=projected_arpu_increase * 5,  # Assume 5 customers upgrade
                projected_roi=50.0,
                implementation_cost=2000,  # Sales/marketing time
                implementation_time_weeks=2,
                description="Launch premium tier for customers needing >50% Tier 1 intelligence.",
                steps=[
                    "Package current offering as 'Premium Tier' ($4500-7500/month)",
                    "Add SLA guarantees (Tier 1 ratio ≥55%, p99 latency ≤100ms)",
                    "Offer custom source integrations ($2500 setup fee)",
                    "Upsell to existing customers with high Tier 1 usage",
                ],
                risks=[
                    "May cannibalize standard tier revenue",
                    "Higher support burden for SLA guarantees",
                ],
            )
            redesigns.append(redesign)

        # Redesign 4: Subscription model (recurring revenue)
        redesign = RedesignProposal(
            redesign_type="subscription_model",
            impact_category="both",
            projected_gain=2000,  # More predictable revenue, lower churn
            projected_roi=20.0,
            implementation_cost=1500,
            implementation_time_weeks=3,
            description="Shift from usage-based to subscription pricing for predictable revenue.",
            steps=[
                "Define tiers: Starter ($1500/month, 50K items), Pro ($3500/month, 150K items), Enterprise (custom)",
                "Offer 20% discount for annual prepay",
                "Add overage pricing ($0.035/item beyond tier limit)",
                "Grandfather existing customers for 3 months",
            ],
            risks=["Customer resistance to price changes", "Revenue dip during transition period"],
        )
        redesigns.append(redesign)

        return redesigns

    async def _identify_leverage(
        self,
        result: Any,
        historical_data: list[Any] | None,
    ) -> list[LeverageOpportunity]:
        """Identify compounding leverage opportunities"""
        opportunities = []

        # Leverage 1: Data moat (accumulated intelligence)
        daily_items = result.total_items
        yearly_items = daily_items * 365
        tier_1_items_per_year = yearly_items * result.tier_1_ratio

        # Value compounds as dataset grows (network effects)
        data_moat_value_1yr = tier_1_items_per_year * 0.10  # $0.10 per Tier 1 item
        data_moat_value_3yr = data_moat_value_1yr * 3 * 1.5  # 50% compound per year

        opportunity = LeverageOpportunity(
            opportunity_type="data_moat",
            compound_rate=1.5,  # 50% per year
            initial_value=0,
            projected_1yr_value=data_moat_value_1yr,
            projected_3yr_value=data_moat_value_3yr,
            activation_requirements=[
                "Maintain >40% Tier 1 ratio",
                "Implement data retention (90+ days)",
                "Build search/retrieval API",
            ],
            description="Accumulated intelligence dataset becomes proprietary asset. Can license to research institutions, train custom models, or build intelligence archive product.",
        )
        opportunities.append(opportunity)

        # Leverage 2: Viral referral program
        # Assume 5% monthly viral growth if customers love the product
        current_mrr = 15000  # Assume 10 customers @ $1500/month
        viral_growth_rate = 1.05  # 5% per month
        mrr_1yr = current_mrr * (viral_growth_rate**12)
        mrr_3yr = current_mrr * (viral_growth_rate**36)

        opportunity = LeverageOpportunity(
            opportunity_type="viral_referral",
            compound_rate=viral_growth_rate,
            initial_value=current_mrr,
            projected_1yr_value=mrr_1yr,
            projected_3yr_value=mrr_3yr,
            activation_requirements=[
                "Build referral program (20% discount for referrer)",
                "Jobs-quality product (insanely great experience)",
                "Customer success team (ensure high NPS)",
            ],
            description="Challenge: Can we make the product so good that customers can't help but tell others? Jobs: 'Make products worth talking about.'",
        )
        opportunities.append(opportunity)

        # Leverage 3: Network effects (more sources → better insights)
        opportunity = LeverageOpportunity(
            opportunity_type="network_effect",
            compound_rate=1.15,  # 15% improvement per source added
            initial_value=8 * 1000,  # 8 sources × $1000 value each
            projected_1yr_value=15 * 1200,  # 15 sources × $1200 value (improvement)
            projected_3yr_value=25 * 1500,  # 25 sources × $1500 value
            activation_requirements=[
                "Add 2 new sources per quarter",
                "Cross-source correlation analysis",
                "Diversification across regions/languages",
            ],
            description="Challenge: Each new source increases value of existing sources through cross-correlation. More sources = exponentially better insights.",
        )
        opportunities.append(opportunity)

        return opportunities

    def _classify_severity(self, waste_percentage: float) -> LeakSeverity:
        """Classify leak severity by waste percentage"""
        if waste_percentage >= 0.20:
            return LeakSeverity.CRITICAL
        if waste_percentage >= 0.10:
            return LeakSeverity.HIGH
        if waste_percentage >= 0.05:
            return LeakSeverity.MEDIUM
        return LeakSeverity.LOW


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_wealth_optimizer():
    """Demonstrate Wealth Optimizer"""
    from pnkln.core.gemini_ingestion_layer import (
        IngestionResult,
        IngestionStatus,
        SourceCoverageMetrics,
        SourceType,
    )

    print("=== Wealth Optimizer Demo ===\n")

    # Mock ingestion result
    mock_result = IngestionResult(
        job_id="test_job_001",
        status=IngestionStatus.COMPLETED,
        runtime_minutes=42.0,
        items_collected=[],
        source_metrics={
            SourceType.YOUTUBE: SourceCoverageMetrics(
                source_type=SourceType.YOUTUBE,
                items_ingested=150,
                items_tier_1=45,  # 30% Tier 1 (below 40% target)
                items_tier_2=75,
                items_tier_3=30,
                avg_relevance_score=0.65,
                total_cost_usd=2.25,
            ),
            SourceType.TWITTER: SourceCoverageMetrics(
                source_type=SourceType.TWITTER,
                items_ingested=200,
                items_tier_1=100,  # 50% Tier 1 (good!)
                items_tier_2=80,
                items_tier_3=20,
                avg_relevance_score=0.78,
                total_cost_usd=3.00,
            ),
        },
        quality_gates_passed={},
        total_cost_usd=5.25,
    )

    # Analyze
    optimizer = WealthOptimizer()
    analysis = await optimizer.analyze(mock_result)

    # Print report
    print(analysis.generate_report())


if __name__ == "__main__":
    asyncio.run(example_wealth_optimizer())
