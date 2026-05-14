# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Wealth-Planning Model Component.

Structured approach to wealth optimization:
1. Spot leaks (revenue drains)
2. Redesign funnels (upsells/recurring)
3. Leverage viral/conversion
4. Structured response (hard truth → plan → challenge)
"""

from typing import Any
from pydantic import BaseModel, Field
from enum import Enum


class LeakType(str, Enum):
    """Types of revenue leaks."""

    CHURN = "churn"
    CAC_TOO_HIGH = "cac_too_high"
    LOW_LTV = "low_ltv"
    CONVERSION_DROP = "conversion_drop"
    PRICING_MISALIGNMENT = "pricing_misalignment"
    NO_UPSELL = "no_upsell"
    NO_RECURRING = "no_recurring"


class RevenueLeak(BaseModel):
    """Identified revenue leak."""

    leak_type: LeakType
    description: str
    estimated_impact_usd_monthly: float
    confidence: float = Field(ge=0.0, le=1.0)


class FunnelRedesign(BaseModel):
    """Funnel optimization recommendation."""

    stage: str = Field(description="Funnel stage (awareness, consideration, decision, retention)")
    current_conversion: float = Field(description="Current conversion rate (%)")
    target_conversion: float = Field(description="Target conversion rate (%)")
    tactics: list[str] = Field(description="Specific tactics to implement")
    estimated_lift_usd_monthly: float


class LeverageStrategy(BaseModel):
    """Viral or conversion leverage strategy."""

    strategy_type: str = Field(description="viral, referral, content, partnership")
    description: str
    viral_coefficient: float | None = Field(None, description="K-factor for viral strategies")
    implementation_effort: str = Field(description="low, medium, high")
    estimated_roi: float = Field(description="Estimated ROI multiple (e.g., 3.5x)")


class WealthPlan(BaseModel):
    """
    Structured wealth planning response.

    Format: Hard Truth → Plan → Challenge
    """

    # Hard Truth
    hard_truth: str = Field(description="Brutal honesty about current state and leaks")
    leaks: list[RevenueLeak]

    # Plan
    plan: str = Field(description="Actionable plan to address leaks and optimize")
    funnel_redesigns: list[FunnelRedesign]
    leverage_strategies: list[LeverageStrategy]

    # Challenge
    challenge: str = Field(description="Specific challenge with timeline and accountability")
    implementation_timeline_days: int

    # Projections
    total_leak_impact_usd_monthly: float
    total_opportunity_usd_monthly: float
    net_improvement_usd_monthly: float

    def get_roi_summary(self) -> dict[str, Any]:
        """Get ROI summary for plan."""
        return {
            "current_leaks_monthly": self.total_leak_impact_usd_monthly,
            "opportunity_monthly": self.total_opportunity_usd_monthly,
            "net_improvement_monthly": self.net_improvement_usd_monthly,
            "annual_impact": self.net_improvement_usd_monthly * 12,
            "implementation_days": self.implementation_timeline_days,
        }


class WealthAccelerator:
    """
    Wealth planning accelerator agent.

    Analyzes business metrics and generates structured wealth plans.
    """

    def analyze_business(
        self,
        revenue_monthly: float,
        cac: float,
        ltv: float,
        churn_rate: float,
        conversion_rates: dict[str, float],
    ) -> WealthPlan:
        """
        Analyze business and generate wealth plan.

        Args:
            revenue_monthly: Monthly recurring revenue
            cac: Customer acquisition cost
            ltv: Lifetime value
            churn_rate: Monthly churn rate (%)
            conversion_rates: Conversion rates by funnel stage

        Returns:
            Structured WealthPlan with leaks, plan, and challenge
        """
        leaks = []
        funnel_redesigns = []
        leverage_strategies = []

        # Detect leaks
        if churn_rate > 5.0:
            leaks.append(
                RevenueLeak(
                    leak_type=LeakType.CHURN,
                    description=f"{churn_rate}% monthly churn is bleeding revenue",
                    estimated_impact_usd_monthly=revenue_monthly * (churn_rate / 100),
                    confidence=0.95,
                )
            )
            funnel_redesigns.append(
                FunnelRedesign(
                    stage="retention",
                    current_conversion=100 - churn_rate,
                    target_conversion=97.0,  # Target 3% churn
                    tactics=[
                        "Add onboarding sequence",
                        "Implement health score monitoring",
                        "Create retention playbook for at-risk customers",
                    ],
                    estimated_lift_usd_monthly=revenue_monthly * ((churn_rate - 3.0) / 100),
                )
            )

        if cac / ltv > 0.33:
            leaks.append(
                RevenueLeak(
                    leak_type=LeakType.CAC_TOO_HIGH,
                    description=f"CAC/LTV ratio {cac / ltv:.2f} is unsustainable (target <0.33)",
                    estimated_impact_usd_monthly=revenue_monthly * 0.2,  # Estimated impact
                    confidence=0.85,
                )
            )

        # Add leverage strategies
        leverage_strategies.append(
            LeverageStrategy(
                strategy_type="referral",
                description="Implement referral program with 20% discount for referrer + referee",
                viral_coefficient=1.2,
                implementation_effort="medium",
                estimated_roi=3.5,
            )
        )

        # Calculate totals
        total_leak_impact = sum(leak.estimated_impact_usd_monthly for leak in leaks)
        total_opportunity = sum(fr.estimated_lift_usd_monthly for fr in funnel_redesigns)
        net_improvement = total_opportunity - (total_leak_impact * 0.3)  # Assume 70% leak recovery

        # Generate structured response
        hard_truth = (
            f"You're leaving ${total_leak_impact:,.0f}/month on the table. "
            f"Current churn rate of {churn_rate}% is killing growth. "
            f"CAC/LTV ratio of {cac / ltv:.2f} means you're paying too much for customers."
        )

        plan = (
            f"Focus on retention first: Reduce churn from {churn_rate}% to 3% within 60 days. "
            f"Then optimize CAC via referral program (target 1.2x viral coefficient). "
            f"This unlocks ${net_improvement:,.0f}/month in net improvement."
        )

        challenge = (
            "Challenge: Implement retention playbook and referral program within 60 days. "
            "Track weekly: churn rate, referral signups, CAC trend. "
            "Report back with results or explain why you failed."
        )

        return WealthPlan(
            hard_truth=hard_truth,
            leaks=leaks,
            plan=plan,
            funnel_redesigns=funnel_redesigns,
            leverage_strategies=leverage_strategies,
            challenge=challenge,
            implementation_timeline_days=60,
            total_leak_impact_usd_monthly=total_leak_impact,
            total_opportunity_usd_monthly=total_opportunity,
            net_improvement_usd_monthly=net_improvement,
        )
