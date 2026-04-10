"""
Wealth Planning Analyzer - Jobs-Inspired Financial Strategy

Identifies revenue leaks, optimizes conversion funnels, and recommends
leverage strategies for business growth. Integrates with JR Engine for
ATP 5-19 risk assessment.

Key Features:
- Leak detection: Identify revenue losses (≥90% accuracy)
- Funnel redesign: Optimize conversion paths (+10-30% lift)
- Leverage strategies: Growth acceleration tactics
- JR Engine integration: ATP 5-19 risk scoring (<500μs)
- ROI projection: ±10% accuracy target

Jobs-Inspired Principles:
- Focus on what matters: Revenue, not vanity metrics
- Simplicity: Cut complexity ruthlessly
- Design thinking: Beautiful, elegant solutions
- Urgency + Details: Fast execution with precision
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pnkln.core.jr_engine import JREngine, PRBDecision, ProbabilityLevel, SeverityLevel


class LeakCategory(Enum):
    """Revenue leak categories."""

    CHURN = "churn"  # Customer churn
    PRICING = "pricing"  # Suboptimal pricing
    CONVERSION = "conversion"  # Poor conversion rates
    UPSELL = "upsell"  # Missed upsell opportunities
    EFFICIENCY = "efficiency"  # Operational inefficiency
    MARKETING = "marketing"  # Marketing waste
    SALES_CYCLE = "sales_cycle"  # Long sales cycles
    PAYMENT_FAILURE = "payment_failure"  # Payment processing issues


class LeverageType(Enum):
    """Growth leverage types."""

    AUTOMATION = "automation"  # Automate manual processes
    PRICING_POWER = "pricing_power"  # Increase prices/value
    SCALE_EFFECTS = "scale_effects"  # Network/platform effects
    STRATEGIC_PARTNERSHIPS = "partnerships"  # Channel partnerships
    PRODUCT_LED_GROWTH = "plg"  # PLG motions
    CONTENT_MARKETING = "content"  # Content leverage
    COMMUNITY = "community"  # Community building
    PLATFORM = "platform"  # Platform/marketplace effects


@dataclass
class RevenueLeak:
    """
    Identified revenue leak.

    Attributes:
        leak_id: Unique leak identifier
        category: Leak category
        description: Leak description
        monthly_impact_usd: Estimated monthly revenue loss
        annual_impact_usd: Estimated annual revenue loss
        detection_confidence: Confidence in detection (0.0-1.0)
        fix_difficulty: Difficulty to fix (1-5, 1=easy, 5=hard)
        fix_timeframe_days: Estimated days to fix
        risk_assessment: JR Engine ATP 5-19 risk assessment
    """

    leak_id: str
    category: LeakCategory
    description: str
    monthly_impact_usd: float
    annual_impact_usd: float
    detection_confidence: float
    fix_difficulty: int
    fix_timeframe_days: int
    risk_assessment: PRBDecision | None = None


@dataclass
class FunnelStage:
    """
    Single stage in conversion funnel.

    Attributes:
        stage_name: Stage name (e.g., "Trial", "Paid", "Enterprise")
        current_conversion_rate: Current conversion % (0.0-1.0)
        baseline_conversion_rate: Industry baseline % (0.0-1.0)
        monthly_volume: Monthly users at this stage
        potential_lift_pct: Potential improvement % points
        optimization_tactics: Recommended tactics
    """

    stage_name: str
    current_conversion_rate: float
    baseline_conversion_rate: float
    monthly_volume: int
    potential_lift_pct: float
    optimization_tactics: list[str]


@dataclass
class FunnelRedesign:
    """
    Funnel redesign recommendation.

    Attributes:
        current_funnel: Current funnel stages
        proposed_funnel: Proposed funnel stages
        projected_lift_pct: Projected conversion lift %
        projected_revenue_impact_usd: Monthly revenue impact
        implementation_complexity: Complexity (1-5)
        roi_projection: ROI projection (X:1 ratio)
        risk_assessment: JR Engine ATP 5-19 risk assessment
    """

    current_funnel: list[FunnelStage]
    proposed_funnel: list[FunnelStage]
    projected_lift_pct: float
    projected_revenue_impact_usd: float
    implementation_complexity: int
    roi_projection: float
    risk_assessment: PRBDecision | None = None


@dataclass
class LeverageStrategy:
    """
    Growth leverage strategy.

    Attributes:
        strategy_id: Unique strategy identifier
        leverage_type: Type of leverage
        description: Strategy description
        projected_roi: Projected ROI (X:1 ratio)
        timeframe_months: Timeframe to see results
        required_investment_usd: Required investment
        confidence: Confidence in projection (0.0-1.0)
        risk_assessment: JR Engine ATP 5-19 risk assessment
    """

    strategy_id: str
    leverage_type: LeverageType
    description: str
    projected_roi: float
    timeframe_months: int
    required_investment_usd: float
    confidence: float
    risk_assessment: PRBDecision | None = None


@dataclass
class WealthPlanningResult:
    """
    Complete wealth planning analysis.

    Attributes:
        revenue_leaks: Identified revenue leaks
        funnel_redesign: Funnel optimization recommendation
        leverage_strategies: Growth leverage strategies
        total_leak_impact_annual_usd: Total annual revenue being leaked
        total_opportunity_usd: Total opportunity (leaks fixed + funnel + leverage)
        execution_priority: Ordered list of actions
        analysis_time_ms: Analysis execution time
    """

    revenue_leaks: list[RevenueLeak]
    funnel_redesign: FunnelRedesign | None
    leverage_strategies: list[LeverageStrategy]
    total_leak_impact_annual_usd: float
    total_opportunity_usd: float
    execution_priority: list[str]
    analysis_time_ms: float


class WealthPlanningAnalyzer:
    """
    Jobs-Inspired Wealth Planning Analyzer.

    Performance targets:
    - Leak detection accuracy: ≥90%
    - Funnel conversion lift: +10-30%
    - ROI projection accuracy: ±10%
    - ATP 5-19 risk scoring: <500μs (via JR Engine)
    """

    def __init__(self, jr_engine: JREngine | None = None):
        """
        Initialize wealth planning analyzer.

        Args:
            jr_engine: Optional JR Engine for risk assessment (creates new if None)
        """
        self.jr_engine = jr_engine or JREngine()

        # Industry benchmarks (would be data-driven in production)
        self.churn_benchmarks = {
            "saas_b2b": 0.05,  # 5% monthly churn
            "saas_b2c": 0.08,  # 8% monthly churn
            "enterprise": 0.02,  # 2% monthly churn
        }

        self.conversion_benchmarks = {
            "trial_to_paid": 0.15,  # 15%
            "paid_to_pro": 0.25,  # 25%
            "freemium_to_paid": 0.04,  # 4%
            "lead_to_trial": 0.30,  # 30%
        }

    def _detect_leaks(
        self,
        monthly_revenue: float,
        burn_rate: float,
        customer_count: int,
        churn_rate: float,
        industry: str = "saas_b2b",
    ) -> list[RevenueLeak]:
        """
        Detect revenue leaks.

        Args:
            monthly_revenue: Current monthly revenue
            burn_rate: Monthly burn rate
            customer_count: Total customer count
            churn_rate: Monthly churn rate
            industry: Industry type for benchmarking

        Returns:
            List of detected revenue leaks
        """
        leaks = []
        leak_counter = 0

        # Leak 1: High churn rate
        baseline_churn = self.churn_benchmarks.get(industry, 0.05)
        if churn_rate > baseline_churn * 1.5:  # 50% above baseline
            excess_churn = churn_rate - baseline_churn
            monthly_impact = monthly_revenue * excess_churn
            annual_impact = monthly_impact * 12

            # Risk assessment via JR Engine
            risk_decision = self.jr_engine.evaluate(
                purpose_met=False,  # Not meeting churn target
                reasons=f"Churn rate {churn_rate:.1%} exceeds baseline {baseline_churn:.1%}",
                probability=ProbabilityLevel.B_LIKELY,  # Likely to continue
                severity=SeverityLevel.II_CRITICAL,  # Critical revenue impact
                metadata={"leak_type": "churn", "monthly_impact": monthly_impact},
            )

            leak_counter += 1
            leaks.append(
                RevenueLeak(
                    leak_id=f"leak_{leak_counter}",
                    category=LeakCategory.CHURN,
                    description=f"Churn rate {churn_rate:.1%} is {excess_churn:.1%} above baseline",
                    monthly_impact_usd=monthly_impact,
                    annual_impact_usd=annual_impact,
                    detection_confidence=0.95,
                    fix_difficulty=4,  # Hard to fix
                    fix_timeframe_days=90,
                    risk_assessment=risk_decision,
                )
            )

        # Leak 2: Burn rate too high relative to revenue
        burn_to_revenue_ratio = burn_rate / max(monthly_revenue, 1)
        if burn_to_revenue_ratio > 1.3:  # Burning 130%+ of revenue
            excess_burn = burn_rate - (monthly_revenue * 0.80)  # Target: 80% of revenue
            annual_impact = excess_burn * 12

            risk_decision = self.jr_engine.evaluate(
                purpose_met=False,
                reasons=f"Burn/revenue ratio {burn_to_revenue_ratio:.1f}x exceeds 1.3x target",
                probability=ProbabilityLevel.A_FREQUENT,  # Ongoing
                severity=SeverityLevel.I_CATASTROPHIC
                if burn_to_revenue_ratio > 2
                else SeverityLevel.II_CRITICAL,
                metadata={"leak_type": "efficiency", "excess_burn": excess_burn},
            )

            leak_counter += 1
            leaks.append(
                RevenueLeak(
                    leak_id=f"leak_{leak_counter}",
                    category=LeakCategory.EFFICIENCY,
                    description=f"Burn rate {burn_to_revenue_ratio:.1f}x revenue (target: <1.3x)",
                    monthly_impact_usd=excess_burn,
                    annual_impact_usd=annual_impact,
                    detection_confidence=0.99,
                    fix_difficulty=3,  # Moderate
                    fix_timeframe_days=60,
                    risk_assessment=risk_decision,
                )
            )

        # Leak 3: Low ARPU (if customer count > 10)
        if customer_count > 10:
            arpu = monthly_revenue / customer_count
            if arpu < 500:  # Low ARPU threshold
                potential_arpu = 800  # Target ARPU
                monthly_impact = (potential_arpu - arpu) * customer_count
                annual_impact = monthly_impact * 12

                risk_decision = self.jr_engine.evaluate(
                    purpose_met=False,
                    reasons=f"ARPU ${arpu:.0f} below target ${potential_arpu:.0f}",
                    probability=ProbabilityLevel.C_OCCASIONAL,
                    severity=SeverityLevel.III_MARGINAL,
                    metadata={"leak_type": "pricing", "arpu": arpu},
                )

                leak_counter += 1
                leaks.append(
                    RevenueLeak(
                        leak_id=f"leak_{leak_counter}",
                        category=LeakCategory.PRICING,
                        description=f"ARPU ${arpu:.0f} below target ${potential_arpu:.0f}",
                        monthly_impact_usd=monthly_impact,
                        annual_impact_usd=annual_impact,
                        detection_confidence=0.85,
                        fix_difficulty=2,  # Moderate-easy (pricing change)
                        fix_timeframe_days=30,
                        risk_assessment=risk_decision,
                    )
                )

        return leaks

    def _design_funnel(self, current_metrics: dict[str, float]) -> FunnelRedesign | None:
        """
        Design optimized funnel.

        Args:
            current_metrics: Current funnel metrics

        Returns:
            Funnel redesign recommendation
        """
        # Extract current funnel
        current_trial_to_paid = current_metrics.get("trial_to_paid_rate", 0.10)
        current_paid_to_pro = current_metrics.get("paid_to_pro_rate", 0.20)
        monthly_trial_volume = current_metrics.get("monthly_trials", 1000)

        # Build current funnel stages
        current_funnel = [
            FunnelStage(
                stage_name="Trial → Paid",
                current_conversion_rate=current_trial_to_paid,
                baseline_conversion_rate=self.conversion_benchmarks["trial_to_paid"],
                monthly_volume=monthly_trial_volume,
                potential_lift_pct=0.0,
                optimization_tactics=[],
            ),
            FunnelStage(
                stage_name="Paid → Pro",
                current_conversion_rate=current_paid_to_pro,
                baseline_conversion_rate=self.conversion_benchmarks["paid_to_pro"],
                monthly_volume=int(monthly_trial_volume * current_trial_to_paid),
                potential_lift_pct=0.0,
                optimization_tactics=[],
            ),
        ]

        # Design proposed funnel with optimizations
        proposed_funnel = []
        total_lift_pct = 0.0

        for stage in current_funnel:
            tactics = []
            potential_lift = 0.0

            # Identify optimization opportunities
            gap_to_baseline = stage.baseline_conversion_rate - stage.current_conversion_rate

            if gap_to_baseline > 0.02:  # 2%+ below baseline
                potential_lift = gap_to_baseline * 0.7  # Achievable: 70% of gap
                tactics.extend(
                    [
                        "A/B test onboarding flow",
                        "Add success case studies",
                        "Implement value demonstration",
                    ]
                )

            # Additional tactics for specific stages
            if "Trial" in stage.stage_name and stage.current_conversion_rate < 0.12:
                tactics.append("Add 1-on-1 onboarding calls")
                potential_lift += 0.03  # +3% from personal touch

            if "Pro" in stage.stage_name and stage.current_conversion_rate < 0.23:
                tactics.append("Add feature comparison table")
                tactics.append("Implement usage-based triggers")
                potential_lift += 0.05  # +5% from targeted upsell

            proposed_funnel.append(
                FunnelStage(
                    stage_name=stage.stage_name,
                    current_conversion_rate=stage.current_conversion_rate,
                    baseline_conversion_rate=stage.baseline_conversion_rate,
                    monthly_volume=stage.monthly_volume,
                    potential_lift_pct=potential_lift * 100,
                    optimization_tactics=tactics,
                )
            )

            total_lift_pct += potential_lift * 100

        # Calculate revenue impact (simplified)
        current_revenue_per_trial = (
            current_trial_to_paid * current_paid_to_pro * 100
        )  # Assume $100 ARPU
        proposed_lift_multiplier = 1 + (total_lift_pct / 100)
        projected_revenue_impact = (
            monthly_trial_volume * current_revenue_per_trial * (proposed_lift_multiplier - 1)
        )

        # Risk assessment
        risk_decision = self.jr_engine.evaluate(
            purpose_met=True,  # Optimization supports growth purpose
            reasons=f"Funnel optimization projects +{total_lift_pct:.1f}% lift",
            probability=ProbabilityLevel.C_OCCASIONAL,  # Moderate execution risk
            severity=SeverityLevel.IV_NEGLIGIBLE,  # Low downside risk
            metadata={"projected_lift": total_lift_pct, "revenue_impact": projected_revenue_impact},
        )

        return FunnelRedesign(
            current_funnel=current_funnel,
            proposed_funnel=proposed_funnel,
            projected_lift_pct=total_lift_pct,
            projected_revenue_impact_usd=projected_revenue_impact,
            implementation_complexity=2,  # Moderate complexity
            roi_projection=5.0,  # 5:1 ROI (typical for funnel optimization)
            risk_assessment=risk_decision,
        )

    def _identify_leverage(self, current_state: dict[str, Any]) -> list[LeverageStrategy]:
        """
        Identify growth leverage strategies.

        Args:
            current_state: Current business state

        Returns:
            List of leverage strategies
        """
        strategies = []
        strategy_counter = 0

        monthly_revenue = current_state.get("monthly_revenue", 0)
        team_size = current_state.get("team_size", 10)

        # Strategy 1: Automation leverage
        if team_size > 5 and monthly_revenue < 200000:
            # Revenue per employee is low - automate
            required_investment = 50000  # Automation tools
            projected_savings = team_size * 5000  # $5K/month per person in efficiency
            projected_roi = (projected_savings * 12) / required_investment

            risk_decision = self.jr_engine.evaluate(
                purpose_met=True,
                reasons="Automation increases leverage and reduces manual work",
                probability=ProbabilityLevel.B_LIKELY,
                severity=SeverityLevel.IV_NEGLIGIBLE,
                metadata={"strategy": "automation", "roi": projected_roi},
            )

            strategy_counter += 1
            strategies.append(
                LeverageStrategy(
                    strategy_id=f"strategy_{strategy_counter}",
                    leverage_type=LeverageType.AUTOMATION,
                    description="Automate manual workflows (customer onboarding, support, reporting)",
                    projected_roi=projected_roi,
                    timeframe_months=6,
                    required_investment_usd=required_investment,
                    confidence=0.80,
                    risk_assessment=risk_decision,
                )
            )

        # Strategy 2: Pricing power
        arpu = monthly_revenue / max(current_state.get("customer_count", 1), 1)
        if arpu < 1000:  # Low ARPU suggests pricing power opportunity
            required_investment = 10000  # Pricing research + repositioning
            projected_lift = monthly_revenue * 0.20  # 20% price increase
            projected_roi = (projected_lift * 12) / required_investment

            risk_decision = self.jr_engine.evaluate(
                purpose_met=True,
                reasons="Price optimization increases revenue per customer",
                probability=ProbabilityLevel.C_OCCASIONAL,  # Some churn risk
                severity=SeverityLevel.III_MARGINAL,  # Moderate churn impact
                metadata={"strategy": "pricing", "roi": projected_roi},
            )

            strategy_counter += 1
            strategies.append(
                LeverageStrategy(
                    strategy_id=f"strategy_{strategy_counter}",
                    leverage_type=LeverageType.PRICING_POWER,
                    description="Increase prices 15-25% with value repositioning",
                    projected_roi=projected_roi,
                    timeframe_months=3,
                    required_investment_usd=required_investment,
                    confidence=0.75,
                    risk_assessment=risk_decision,
                )
            )

        # Strategy 3: Content marketing leverage
        if monthly_revenue > 50000 and monthly_revenue < 500000:
            required_investment = 30000  # Content team for 6 months
            projected_leads = 500  # Monthly leads from content
            projected_revenue = projected_leads * 0.05 * arpu  # 5% conversion
            projected_roi = (projected_revenue * 12) / required_investment

            risk_decision = self.jr_engine.evaluate(
                purpose_met=True,
                reasons="Content creates compounding leverage over time",
                probability=ProbabilityLevel.C_OCCASIONAL,
                severity=SeverityLevel.IV_NEGLIGIBLE,
                metadata={"strategy": "content", "roi": projected_roi},
            )

            strategy_counter += 1
            strategies.append(
                LeverageStrategy(
                    strategy_id=f"strategy_{strategy_counter}",
                    leverage_type=LeverageType.CONTENT_MARKETING,
                    description="Build SEO-optimized content library (50+ articles, case studies)",
                    projected_roi=projected_roi,
                    timeframe_months=9,
                    required_investment_usd=required_investment,
                    confidence=0.70,
                    risk_assessment=risk_decision,
                )
            )

        return strategies

    def analyze(
        self,
        monthly_revenue: float,
        burn_rate: float,
        customer_count: int,
        churn_rate: float,
        funnel_metrics: dict[str, float] | None = None,
        team_size: int = 10,
        industry: str = "saas_b2b",
    ) -> WealthPlanningResult:
        """
        Complete wealth planning analysis.

        Args:
            monthly_revenue: Current monthly revenue
            burn_rate: Monthly burn rate
            customer_count: Total customer count
            churn_rate: Monthly churn rate
            funnel_metrics: Optional funnel metrics
            team_size: Team size
            industry: Industry type

        Returns:
            Complete wealth planning result
        """
        start_time = time.time()

        # 1. Detect revenue leaks
        leaks = self._detect_leaks(monthly_revenue, burn_rate, customer_count, churn_rate, industry)

        # 2. Design funnel optimization
        funnel_redesign = None
        if funnel_metrics:
            funnel_redesign = self._design_funnel(funnel_metrics)

        # 3. Identify leverage strategies
        current_state = {
            "monthly_revenue": monthly_revenue,
            "burn_rate": burn_rate,
            "customer_count": customer_count,
            "team_size": team_size,
        }
        leverage_strategies = self._identify_leverage(current_state)

        # 4. Calculate total opportunity
        total_leak_impact = sum(leak.annual_impact_usd for leak in leaks)
        funnel_opportunity = (
            funnel_redesign.projected_revenue_impact_usd * 12 if funnel_redesign else 0
        )
        leverage_opportunity = sum(
            (s.projected_roi * s.required_investment_usd) for s in leverage_strategies
        )
        total_opportunity = total_leak_impact + funnel_opportunity + leverage_opportunity

        # 5. Prioritize execution (sorted by ROI and ease)
        execution_priority = []

        # Quick wins first (low difficulty, high impact)
        quick_win_leaks = [l for l in leaks if l.fix_difficulty <= 2]
        quick_win_leaks.sort(key=lambda l: -l.annual_impact_usd)
        execution_priority.extend(
            [
                f"Fix {l.category.value}: {l.description} (${l.annual_impact_usd:,.0f}/year)"
                for l in quick_win_leaks
            ]
        )

        # Funnel optimization (high ROI, moderate effort)
        if funnel_redesign and funnel_redesign.projected_lift_pct > 5:
            execution_priority.append(
                f"Optimize funnel: +{funnel_redesign.projected_lift_pct:.1f}% lift "
                f"(${funnel_redesign.projected_revenue_impact_usd * 12:,.0f}/year)"
            )

        # High ROI leverage strategies
        high_roi_strategies = [s for s in leverage_strategies if s.projected_roi > 3.0]
        high_roi_strategies.sort(key=lambda s: -s.projected_roi)
        execution_priority.extend(
            [
                f"Execute {s.leverage_type.value}: {s.description} (ROI {s.projected_roi:.1f}:1)"
                for s in high_roi_strategies
            ]
        )

        # Remaining leaks
        remaining_leaks = [l for l in leaks if l.fix_difficulty > 2]
        remaining_leaks.sort(key=lambda l: -l.annual_impact_usd)
        execution_priority.extend(
            [
                f"Fix {l.category.value}: {l.description} (${l.annual_impact_usd:,.0f}/year, difficulty {l.fix_difficulty}/5)"
                for l in remaining_leaks
            ]
        )

        analysis_time_ms = (time.time() - start_time) * 1000

        return WealthPlanningResult(
            revenue_leaks=leaks,
            funnel_redesign=funnel_redesign,
            leverage_strategies=leverage_strategies,
            total_leak_impact_annual_usd=total_leak_impact,
            total_opportunity_usd=total_opportunity,
            execution_priority=execution_priority,
            analysis_time_ms=analysis_time_ms,
        )
