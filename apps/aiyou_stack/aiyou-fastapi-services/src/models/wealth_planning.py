"""Wealth Planning and Financial Optimization Models
Based on Pinkln Ultrathink wealth acceleration framework
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class LeakType(StrEnum):
    """Types of financial leaks that drain business value"""

    CHURN_RATE = "Churn Rate Too High"
    CAC_LTV_RATIO = "CAC/LTV Ratio Unsustainable"
    NO_UPSELL = "No Upsell/Recurring Revenue"
    CONVERSION_BOTTLENECK = "Conversion Funnel Bottlenecks"
    PRICING_MISALIGNMENT = "Pricing Misalignment"
    INEFFICIENT_SPENDING = "Inefficient Spending"
    MISSED_OPPORTUNITIES = "Missed Revenue Opportunities"


class FinancialLeak(BaseModel):
    """A specific financial leak with impact assessment"""

    leak_type: LeakType
    current_state: str = Field(..., description="Brutal honesty about current situation")
    estimated_cost_monthly: float | None = Field(None, description="Monthly cost in dollars")
    impact_severity: int = Field(..., ge=1, le=10, description="Severity rating 1-10")
    evidence: list[str] = Field(default_factory=list, description="Data points proving this leak")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "leak_type": "CHURN_RATE",
                "current_state": "Losing 15% of customers monthly - bleeding $30K/month in MRR",
                "estimated_cost_monthly": 30000,
                "impact_severity": 9,
                "evidence": [
                    "MRR decreased from $200K to $170K over last 2 months",
                    "15% monthly churn vs industry average of 5%",
                    "Exit survey shows 60% leave due to lack of onboarding",
                ],
            },
        },
    )


class FunnelStage(StrEnum):
    """Stages in customer acquisition/revenue funnel"""

    AWARENESS = "Awareness"
    ACQUISITION = "Acquisition"
    ACTIVATION = "Activation"
    RETENTION = "Retention"
    REVENUE = "Revenue"
    REFERRAL = "Referral"


class FunnelRedesign(BaseModel):
    """Recommendations for funnel optimization"""

    stage: FunnelStage
    current_conversion: float = Field(..., description="Current conversion rate (0-1)")
    target_conversion: float = Field(..., description="Target conversion rate (0-1)")
    strategies: list[str] = Field(..., description="Specific tactics to improve conversion")
    expected_roi: float | None = Field(None, description="Expected ROI multiple (e.g., 3.5 = 3.5x)")
    implementation_difficulty: int = Field(..., ge=1, le=5, description="1=Easy, 5=Very Hard")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stage": "ACTIVATION",
                "current_conversion": 0.25,
                "target_conversion": 0.60,
                "strategies": [
                    "Implement automated onboarding sequence (Days 1, 3, 7, 14)",
                    "Add interactive product tour with progress tracking",
                    "Offer 1-on-1 onboarding call within first 48 hours",
                    "Create activation checklist with dopamine hits (visual progress)",
                ],
                "expected_roi": 4.2,
                "implementation_difficulty": 3,
            },
        },
    )


class WealthAccelerationAction(BaseModel):
    """Specific action item with ROI projection"""

    action: str = Field(..., description="Clear, actionable step")
    responsible_party: str | None = None
    timeline: str = Field(..., description="When this should be completed")
    estimated_cost: float | None = Field(None, description="Implementation cost in dollars")
    projected_revenue_impact: float | None = Field(None, description="Monthly revenue impact")
    roi_months: int | None = Field(None, description="Months to break even")
    priority: int = Field(..., ge=1, le=10, description="Priority 1-10")


class WealthAnalysis(BaseModel):
    """Complete wealth planning analysis
    Structure: Spot leaks → Redesign funnels → Leverage viral/conversion
    """

    business_name: str
    analysis_date: datetime | None = None

    # Part 1: HARD TRUTH (Brutal Honesty)
    hard_truth: str = Field(..., description="Brutally honest assessment of current state")
    financial_leaks: list[FinancialLeak] = Field(..., description="Identified leaks")
    total_monthly_leak: float = Field(..., description="Total money bleeding per month")

    # Key Metrics
    current_mrr: float | None = Field(None, description="Monthly Recurring Revenue")
    churn_rate: float | None = Field(None, description="Monthly churn rate (0-1)")
    cac: float | None = Field(None, description="Customer Acquisition Cost")
    ltv: float | None = Field(None, description="Lifetime Value")
    cac_ltv_ratio: float | None = Field(None, description="CAC:LTV ratio (should be < 0.33)")

    # Part 2: PLAN (Actionable Steps with ROI)
    funnel_redesigns: list[FunnelRedesign] = Field(default_factory=list)
    action_plan: list[WealthAccelerationAction] = Field(..., description="Prioritized actions")
    projected_monthly_impact: float = Field(..., description="Expected monthly revenue increase")

    # Part 3: CHALLENGE (Timeline + Accountability)
    challenge_statement: str = Field(..., description="Accountability challenge")
    milestone_timeline: dict[str, str] = Field(..., description="Key milestones with dates")
    success_metrics: list[str] = Field(..., description="How to measure success")
    accountability_partner: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "business_name": "SaaS Startup XYZ",
                "hard_truth": "You're bleeding $45K/month through churn and have 6 months of runway left. CAC/LTV ratio is 0.67 (should be <0.33). You're acquiring customers faster than you're retaining them - this is a treadmill to bankruptcy.",
                "financial_leaks": [
                    {
                        "leak_type": "CHURN_RATE",
                        "current_state": "15% monthly churn vs 5% industry avg",
                        "estimated_cost_monthly": 30000,
                        "impact_severity": 9,
                    },
                    {
                        "leak_type": "NO_UPSELL",
                        "current_state": "Zero expansion revenue from existing customers",
                        "estimated_cost_monthly": 15000,
                        "impact_severity": 7,
                    },
                ],
                "total_monthly_leak": 45000,
                "current_mrr": 200000,
                "churn_rate": 0.15,
                "cac": 800,
                "ltv": 1200,
                "cac_ltv_ratio": 0.67,
                "action_plan": [
                    {
                        "action": "Launch automated onboarding sequence (Days 1/3/7/14)",
                        "timeline": "Week 1-2",
                        "estimated_cost": 5000,
                        "projected_revenue_impact": 15000,
                        "roi_months": 1,
                        "priority": 10,
                    },
                ],
                "projected_monthly_impact": 60000,
                "challenge_statement": "Cut churn from 15% to 7% in 90 days or you're out of business. Your runway depends on it.",
                "milestone_timeline": {
                    "Week 2": "Onboarding sequence live",
                    "Week 4": "Churn reduced to 12%",
                    "Week 8": "Churn reduced to 9%",
                    "Week 12": "Churn at 7% - sustainable",
                },
                "success_metrics": [
                    "Churn rate: 15% → 7%",
                    "MRR: $200K → $260K",
                    "CAC/LTV ratio: 0.67 → 0.30",
                    "Runway: 6 months → 12 months",
                ],
            },
        },
    )


class MoneyOptimizationStrategy(BaseModel):
    """Enhanced money optimization combining 'Doing Less Better Results'
    with Pinkln wealth acceleration
    """

    # Basic optimization (from original framework)
    current_state: str | None = None
    focus_areas: list[str] = Field(default_factory=list)
    strategies: list[str] = Field(
        default=[
            "Track your spending and cut three unnecessary expenses",
            "Redirect savings to investments or experiences with long-term value",
        ],
    )
    action_items: list[str] = Field(default_factory=list)

    # Advanced wealth analysis (Pinkln framework)
    wealth_analysis: WealthAnalysis | None = Field(
        None,
        description="Deep wealth planning analysis (for businesses/serious optimization)",
    )

    # Integration
    priority_level: int | None = Field(None, ge=1, le=10)
    notes: str | None = None


class WealthPlanningRequest(BaseModel):
    """Request for wealth planning analysis"""

    business_name: str
    business_type: str = Field(..., description="SaaS, E-commerce, Services, etc.")

    # Financial data
    monthly_revenue: float
    monthly_expenses: float
    customer_count: int
    new_customers_monthly: int
    churned_customers_monthly: int
    cac: float | None = None

    # Pain points
    biggest_challenges: list[str] = Field(..., description="Top 3-5 business challenges")
    suspected_leaks: list[str] = Field(default_factory=list)

    # Goals
    revenue_goal_monthly: float
    timeline_months: int = Field(..., description="Months to achieve goal")
