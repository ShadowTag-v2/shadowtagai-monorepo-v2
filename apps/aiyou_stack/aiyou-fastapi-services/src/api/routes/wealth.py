# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Wealth Planning and Financial Optimization API Routes
Based on Pinkln Ultrathink wealth acceleration framework
"""

from fastapi import APIRouter, HTTPException

from src.models.glicko import PerformanceTracker
from src.models.wealth_planning import (
    FinancialLeak,
    FunnelRedesign,
    FunnelStage,
    LeakType,
    WealthAccelerationAction,
    WealthAnalysis,
    WealthPlanningRequest,
)

router = APIRouter()

# Initialize performance tracker for strategies
performance_tracker = PerformanceTracker()


@router.get("/", summary="Get wealth planning overview")
async def get_wealth_planning_overview():
    """Get an overview of the wealth planning framework"""
    return {
        "framework": "Pinkln Ultrathink Wealth Acceleration",
        "structure": "Spot Leaks → Redesign Funnels → Leverage Viral/Conversion",
        "output_format": {
            "part_1": "HARD TRUTH - Brutal honesty about current state",
            "part_2": "PLAN - Actionable steps with ROI projections",
            "part_3": "CHALLENGE - Timeline + accountability",
        },
        "leak_types": [leak.value for leak in LeakType],
        "funnel_stages": [stage.value for stage in FunnelStage],
        "pricing": "$50 per business analysis (Tier 4 API)",
    }


@router.post("/analyze", response_model=WealthAnalysis, summary="Generate wealth analysis")
async def create_wealth_analysis(request: WealthPlanningRequest):
    """Generate a comprehensive wealth planning analysis

    This analyzes your business for financial leaks, redesigns your funnel,
    and provides brutal honesty + actionable plan + accountability challenge.
    """
    try:
        # Calculate metrics
        churn_rate = (
            request.churned_customers_monthly / request.customer_count
            if request.customer_count > 0
            else 0
        )
        revenue_lost_to_churn = request.monthly_revenue * churn_rate

        # Calculate CAC if not provided
        if request.cac is None:
            # Rough estimate: assume 30% of expenses go to acquisition
            acquisition_expenses = request.monthly_expenses * 0.3
            request.cac = (
                acquisition_expenses / request.new_customers_monthly
                if request.new_customers_monthly > 0
                else 0
            )

        # Calculate LTV (simplified: average customer pays for 1/churn_rate months)
        avg_revenue_per_customer = (
            request.monthly_revenue / request.customer_count if request.customer_count > 0 else 0
        )
        ltv = (
            avg_revenue_per_customer / churn_rate
            if churn_rate > 0
            else avg_revenue_per_customer * 12
        )

        cac_ltv_ratio = request.cac / ltv if ltv > 0 else 0

        # Identify leaks
        leaks = []
        total_monthly_leak = 0

        # Leak 1: High churn rate
        if churn_rate > 0.05:  # > 5% monthly churn
            leak_cost = revenue_lost_to_churn
            leaks.append(
                FinancialLeak(
                    leak_type=LeakType.CHURN_RATE,
                    current_state=f"{churn_rate * 100:.1f}% monthly churn vs 5% industry average - bleeding ${leak_cost:,.0f}/month",
                    estimated_cost_monthly=leak_cost,
                    impact_severity=min(10, int(churn_rate / 0.05 * 5)),
                    evidence=[
                        f"Losing {request.churned_customers_monthly} customers per month",
                        f"Revenue loss: ${leak_cost:,.0f}/month",
                        f"Churn rate {churn_rate / 0.05:.1f}x industry average",
                    ],
                ),
            )
            total_monthly_leak += leak_cost

        # Leak 2: CAC/LTV ratio
        if cac_ltv_ratio > 0.33:
            leak_cost = (cac_ltv_ratio - 0.33) * request.monthly_revenue
            leaks.append(
                FinancialLeak(
                    leak_type=LeakType.CAC_LTV_RATIO,
                    current_state=f"CAC/LTV ratio is {cac_ltv_ratio:.2f} (should be <0.33) - unsustainable economics",
                    estimated_cost_monthly=leak_cost,
                    impact_severity=min(10, int(cac_ltv_ratio / 0.33 * 5)),
                    evidence=[
                        f"CAC: ${request.cac:,.0f}",
                        f"LTV: ${ltv:,.0f}",
                        f"Ratio: {cac_ltv_ratio:.2f} (target: <0.33)",
                    ],
                ),
            )
            total_monthly_leak += leak_cost

        # Generate hard truth
        months_to_goal = request.timeline_months
        revenue_gap = request.revenue_goal_monthly - request.monthly_revenue
        monthly_growth_needed = revenue_gap / months_to_goal if months_to_goal > 0 else revenue_gap

        hard_truth = f"""You're currently at ${request.monthly_revenue:,.0f}/month MRR with {churn_rate * 100:.1f}% monthly churn.
You're bleeding ${total_monthly_leak:,.0f}/month through leaks.
Your CAC/LTV ratio is {cac_ltv_ratio:.2f} (should be <0.33) - you're spending ${request.cac:,.0f} to acquire customers worth ${ltv:,.0f}.

To hit ${request.revenue_goal_monthly:,.0f}/month in {months_to_goal} months, you need ${monthly_growth_needed:,.0f}/month growth.
With current churn, you're running on a treadmill. Fix retention FIRST or growth is impossible."""

        # Funnel redesigns
        funnel_redesigns = [
            FunnelRedesign(
                stage=FunnelStage.ACTIVATION,
                current_conversion=0.25,  # Assumption
                target_conversion=0.60,
                strategies=[
                    "Implement automated onboarding sequence (Days 1, 3, 7, 14)",
                    "Add interactive product tour with progress tracking",
                    "Offer 1-on-1 onboarding call within first 48 hours",
                    "Create activation checklist with dopamine hits",
                ],
                expected_roi=4.2,
                implementation_difficulty=3,
            ),
            FunnelRedesign(
                stage=FunnelStage.RETENTION,
                current_conversion=1.0 - churn_rate,
                target_conversion=0.95,
                strategies=[
                    "Launch customer success program for at-risk accounts",
                    "Add usage monitoring with proactive outreach triggers",
                    "Create customer community for peer support",
                    "Implement feature adoption campaigns",
                ],
                expected_roi=6.5,
                implementation_difficulty=4,
            ),
        ]

        # Action plan
        action_plan = [
            WealthAccelerationAction(
                action="Launch automated onboarding email sequence",
                timeline="Week 1-2",
                estimated_cost=3000,
                projected_revenue_impact=monthly_growth_needed * 0.3,
                roi_months=1,
                priority=10,
            ),
            WealthAccelerationAction(
                action="Implement churn prediction model + at-risk customer outreach",
                timeline="Week 2-4",
                estimated_cost=8000,
                projected_revenue_impact=revenue_lost_to_churn * 0.5,
                roi_months=2,
                priority=9,
            ),
            WealthAccelerationAction(
                action="Create upsell pathway for existing customers",
                timeline="Week 4-8",
                estimated_cost=12000,
                projected_revenue_impact=monthly_growth_needed * 0.4,
                roi_months=3,
                priority=8,
            ),
        ]

        # Challenge
        challenge_statement = f"""Cut churn from {churn_rate * 100:.1f}% to 5% in 90 days.
Grow MRR from ${request.monthly_revenue:,.0f} to ${request.revenue_goal_monthly:,.0f} in {months_to_goal} months.
Get CAC/LTV ratio under 0.33 or your business model doesn't work.

This is not optional. Your runway depends on it."""

        milestone_timeline = {
            "Week 2": "Onboarding sequence live + 30% activation improvement",
            "Week 4": f"Churn reduced to {max(5, churn_rate * 100 * 0.8):.1f}%",
            "Week 8": f"MRR grown ${monthly_growth_needed * 2:,.0f}",
            "Week 12": f"Churn at 5%, MRR at ${request.monthly_revenue + monthly_growth_needed * 3:,.0f}",
        }

        success_metrics = [
            f"Churn rate: {churn_rate * 100:.1f}% → 5%",
            f"MRR: ${request.monthly_revenue:,.0f} → ${request.revenue_goal_monthly:,.0f}",
            f"CAC/LTV ratio: {cac_ltv_ratio:.2f} → 0.30",
            f"Monthly leak: ${total_monthly_leak:,.0f} → $0",
        ]

        analysis = WealthAnalysis(
            business_name=request.business_name,
            hard_truth=hard_truth,
            financial_leaks=leaks,
            total_monthly_leak=total_monthly_leak,
            current_mrr=request.monthly_revenue,
            churn_rate=churn_rate,
            cac=request.cac,
            ltv=ltv,
            cac_ltv_ratio=cac_ltv_ratio,
            funnel_redesigns=funnel_redesigns,
            action_plan=action_plan,
            projected_monthly_impact=sum(a.projected_revenue_impact or 0 for a in action_plan),
            challenge_statement=challenge_statement,
            milestone_timeline=milestone_timeline,
            success_metrics=success_metrics,
        )

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {e!s}") from e


@router.get("/leaks", summary="List common financial leak types")
async def list_leak_types():
    """Get descriptions of common financial leaks"""
    return {
        "leak_types": [
            {
                "type": "CHURN_RATE",
                "description": "Customer churn rate too high (>5% monthly)",
                "typical_impact": "High",
                "detection": "Track monthly customer retention rate",
            },
            {
                "type": "CAC_LTV_RATIO",
                "description": "Customer Acquisition Cost vs Lifetime Value ratio >0.33",
                "typical_impact": "Critical",
                "detection": "CAC / LTV calculation",
            },
            {
                "type": "NO_UPSELL",
                "description": "No expansion revenue from existing customers",
                "typical_impact": "Medium",
                "detection": "Track revenue per customer over time",
            },
            {
                "type": "CONVERSION_BOTTLENECK",
                "description": "Funnel stages with abnormally low conversion",
                "typical_impact": "Medium-High",
                "detection": "Funnel analysis across all stages",
            },
            {
                "type": "PRICING_MISALIGNMENT",
                "description": "Price doesn't match value delivered",
                "typical_impact": "Medium",
                "detection": "Customer feedback + competitive analysis",
            },
            {
                "type": "INEFFICIENT_SPENDING",
                "description": "High costs in low-ROI channels",
                "typical_impact": "Medium",
                "detection": "ROI analysis by marketing channel",
            },
        ],
    }


@router.get("/example", summary="Get example wealth analysis")
async def get_wealth_analysis_example():
    """Get a pre-filled example of a wealth analysis"""
    return {
        "business_name": "SaaS Startup XYZ",
        "hard_truth": "You're bleeding $45K/month through churn and have 6 months of runway. CAC/LTV is 0.67 (should be <0.33). You're acquiring faster than retaining - a treadmill to bankruptcy.",
        "financial_leaks": [
            {
                "leak_type": "CHURN_RATE",
                "current_state": "15% monthly churn vs 5% industry avg - bleeding $30K/month",
                "estimated_cost_monthly": 30000,
                "impact_severity": 9,
                "evidence": [
                    "MRR down from $200K to $170K in 2 months",
                    "15% monthly churn vs 5% target",
                    "60% of exits cite poor onboarding",
                ],
            },
            {
                "leak_type": "NO_UPSELL",
                "current_state": "Zero expansion revenue from existing customers",
                "estimated_cost_monthly": 15000,
                "impact_severity": 7,
                "evidence": [
                    "No pricing tiers above $99/month",
                    "No upsell campaigns",
                    "Power users hitting limits but not upgrading",
                ],
            },
        ],
        "total_monthly_leak": 45000,
        "action_plan": [
            {
                "action": "Launch automated onboarding (Days 1/3/7/14)",
                "timeline": "Week 1-2",
                "estimated_cost": 5000,
                "projected_revenue_impact": 15000,
                "roi_months": 1,
                "priority": 10,
            },
            {
                "action": "Add $299 & $999 pricing tiers with premium features",
                "timeline": "Week 2-4",
                "estimated_cost": 8000,
                "projected_revenue_impact": 25000,
                "roi_months": 1,
                "priority": 9,
            },
        ],
        "challenge_statement": "Cut churn from 15% to 7% in 90 days or you're out of business. Your runway depends on it.",
        "success_metrics": [
            "Churn: 15% → 7%",
            "MRR: $200K → $260K",
            "CAC/LTV: 0.67 → 0.30",
            "Runway: 6 months → 12 months",
        ],
    }


@router.post("/performance/track", summary="Track strategy performance with Glicko-2")
async def track_strategy_performance(
    strategy_id: str,
    opponent_id: str,
    outcome: float,  # 1.0 = win, 0.5 = draw, 0.0 = loss
    strategy_name: str = None,
    opponent_name: str = None,
):
    """Track performance of different wealth strategies using Glicko-2 ratings

    Compare strategies A/B and track which performs better over time.
    Accounts for uncertainty and volatility.
    """
    # Ensure players exist
    if strategy_id not in performance_tracker.players:
        performance_tracker.add_player(strategy_id, strategy_name)
    if opponent_id not in performance_tracker.players:
        performance_tracker.add_player(opponent_id, opponent_name)

    # Record match
    performance_tracker.record_match(strategy_id, opponent_id, outcome)

    # Update ratings
    updated = performance_tracker.update_all_ratings()

    return {
        "match_recorded": {"player1": strategy_id, "player2": opponent_id, "score": outcome},
        "updated_ratings": {
            strategy_id: {
                "rating": updated[strategy_id].mu,
                "uncertainty": updated[strategy_id].phi,
                "volatility": updated[strategy_id].sigma,
                "games_played": updated[strategy_id].games_played,
            },
            opponent_id: {
                "rating": updated[opponent_id].mu,
                "uncertainty": updated[opponent_id].phi,
                "volatility": updated[opponent_id].sigma,
                "games_played": updated[opponent_id].games_played,
            },
        },
    }


@router.get("/performance/leaderboard", summary="Get strategy performance leaderboard")
async def get_performance_leaderboard(min_games: int = 3):
    """Get leaderboard of strategies ranked by Glicko-2 rating

    Higher rating = better performing strategy
    Lower uncertainty = more confident in rating
    """
    leaderboard = performance_tracker.get_leaderboard(min_games=min_games)

    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "strategy_id": player.player_id,
                "name": player.name or player.player_id,
                "rating": round(player.mu, 1),
                "uncertainty": round(player.phi, 1),
                "volatility": round(player.sigma, 4),
                "games_played": player.games_played,
                "confidence_interval": (
                    round(player.mu - 2 * player.phi, 1),
                    round(player.mu + 2 * player.phi, 1),
                ),
            }
            for i, player in enumerate(leaderboard)
        ],
        "total_strategies": len(leaderboard),
        "min_games_filter": min_games,
    }
