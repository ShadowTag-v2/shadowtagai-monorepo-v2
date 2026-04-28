# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AWS Cost Optimizer service - Core business logic for cost optimization.

This service analyzes AWS costs, identifies waste, provides right-sizing
recommendations, and implements auto-scaling strategies.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from src.aws.ce_client import get_cost_explorer_client
from src.config import settings
from src.models.cost_optimizer_models import (
    CostAnalysisResponse,
    CostDataPoint,
    CostSummary,
    OptimizationRecommendation,
    OptimizationType,
    RecommendationsResponse,
    WasteAnalysisResponse,
)

logger = logging.getLogger(__name__)


class CostOptimizerService:
    """AWS Cost Optimizer service for analyzing and optimizing cloud costs.

    Capabilities:
    - Cost analysis and reporting
    - Right-sizing recommendations
    - Idle resource detection
    - Waste elimination
    - Auto-scaling recommendations
    - Savings Plans and Reserved Instance recommendations
    """

    def __init__(self):
        """Initialize the cost optimizer service."""
        self.ce_client = get_cost_explorer_client()
        logger.info("Cost Optimizer Service initialized")

    async def analyze_costs(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
        granularity: str = "DAILY",
        group_by: list[str] | None = None,
        service_filter: list[str] | None = None,
    ) -> CostAnalysisResponse:
        """Analyze AWS costs for a given period.

        Args:
            start_date: Analysis start date (defaults to 30 days ago)
            end_date: Analysis end date (defaults to today)
            granularity: Data granularity (DAILY, MONTHLY, HOURLY)
            group_by: Dimensions to group by
            service_filter: Filter by specific services

        Returns:
            CostAnalysisResponse with detailed cost breakdown

        """
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_dt = datetime.now() - timedelta(days=settings.cost_lookback_days)
                start_date = start_dt.strftime("%Y-%m-%d")

            logger.info(f"Analyzing costs from {start_date} to {end_date}")

            # Build group_by parameter for AWS API
            group_by_params = None
            if group_by:
                group_by_params = [{"Type": "DIMENSION", "Key": dim} for dim in group_by]

            # Build filter for services
            filter_expr = None
            if service_filter:
                filter_expr = {"Dimensions": {"Key": "SERVICE", "Values": service_filter}}

            # Get cost data from AWS
            cost_data = self.ce_client.get_cost_and_usage(
                start_date=start_date,
                end_date=end_date,
                granularity=granularity,
                metrics=["UnblendedCost"],
                group_by=group_by_params,
                filter_expr=filter_expr,
            )

            # Process the response
            data_points = self._process_cost_data(cost_data)
            summary = self._calculate_cost_summary(data_points, start_date, end_date, cost_data)

            return CostAnalysisResponse(
                summary=summary,
                data_points=data_points,
                granularity=granularity,
            )

        except Exception as e:
            logger.error(f"Error analyzing costs: {e}")
            raise

    async def get_optimization_recommendations(
        self,
        optimization_types: list[OptimizationType] | None = None,
        min_savings_threshold: float = 100.0,
        include_forecast: bool = False,
    ) -> RecommendationsResponse:
        """Generate cost optimization recommendations.

        Args:
            optimization_types: Types of optimizations to analyze
            min_savings_threshold: Minimum savings to include
            include_forecast: Whether to include cost forecast

        Returns:
            RecommendationsResponse with actionable recommendations

        """
        try:
            logger.info("Generating optimization recommendations")

            recommendations: list[OptimizationRecommendation] = []

            # If no specific types requested, analyze all
            if not optimization_types:
                optimization_types = [
                    OptimizationType.RIGHT_SIZING,
                    OptimizationType.SAVINGS_PLANS,
                    OptimizationType.RESERVED_INSTANCES,
                ]

            # Get right-sizing recommendations
            if OptimizationType.RIGHT_SIZING in optimization_types:
                rightsizing_recs = await self._get_rightsizing_recommendations(
                    min_savings_threshold,
                )
                recommendations.extend(rightsizing_recs)

            # Get Savings Plans recommendations
            if OptimizationType.SAVINGS_PLANS in optimization_types:
                savings_plans_recs = await self._get_savings_plans_recommendations(
                    min_savings_threshold,
                )
                recommendations.extend(savings_plans_recs)

            # Get Reserved Instance recommendations
            if OptimizationType.RESERVED_INSTANCES in optimization_types:
                ri_recs = await self._get_reservation_recommendations(min_savings_threshold)
                recommendations.extend(ri_recs)

            # Calculate total savings
            total_savings = sum(rec.estimated_savings for rec in recommendations)

            # Get forecast if requested
            forecast = None
            if include_forecast:
                forecast = await self._get_cost_forecast()

            return RecommendationsResponse(
                total_estimated_savings=total_savings,
                recommendations_count=len(recommendations),
                recommendations=recommendations,
                forecast=forecast,
            )

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    async def analyze_waste(self) -> WasteAnalysisResponse:
        """Analyze AWS resource waste and identify optimization opportunities.

        Returns:
            WasteAnalysisResponse with waste breakdown and recommendations

        """
        try:
            logger.info("Analyzing resource waste")

            # This is a simplified implementation
            # In production, you'd integrate with CloudWatch, Trusted Advisor, etc.

            idle_resources = await self._identify_idle_resources()
            unused_resources = await self._identify_unused_resources()

            # Calculate waste costs
            idle_cost = sum(r.get("monthly_cost", 0) for r in idle_resources)
            unused_cost = sum(r.get("monthly_cost", 0) for r in unused_resources)

            waste_categories = {
                "idle_resources": idle_cost,
                "unused_resources": unused_cost,
                "oversized_resources": 0,  # Placeholder
                "unattached_volumes": 0,  # Placeholder
            }

            total_waste = sum(waste_categories.values())

            return WasteAnalysisResponse(
                total_waste_cost=total_waste,
                waste_categories=waste_categories,
                idle_resources=idle_resources,
                unused_resources=unused_resources,
                optimization_potential=total_waste * 0.8,  # Assume 80% can be optimized
            )

        except Exception as e:
            logger.error(f"Error analyzing waste: {e}")
            raise

    # Private helper methods

    def _process_cost_data(self, cost_data: dict[str, Any]) -> list[CostDataPoint]:
        """Process raw cost data into data points."""
        data_points = []

        for result in cost_data.get("ResultsByTime", []):
            date = result.get("TimePeriod", {}).get("Start", "")

            # Handle grouped data
            if "Groups" in result:
                for group in result["Groups"]:
                    amount = float(
                        group.get("Metrics", {}).get("UnblendedCost", {}).get("Amount", 0),
                    )
                    service = group.get("Keys", ["Unknown"])[0]

                    data_points.append(
                        CostDataPoint(date=date, amount=round(amount, 2), service=service),
                    )
            else:
                # Ungrouped data
                amount = float(result.get("Total", {}).get("UnblendedCost", {}).get("Amount", 0))
                data_points.append(CostDataPoint(date=date, amount=round(amount, 2)))

        return data_points

    def _calculate_cost_summary(
        self,
        data_points: list[CostDataPoint],
        start_date: str,
        end_date: str,
        raw_data: dict[str, Any],
    ) -> CostSummary:
        """Calculate cost summary from data points."""
        total_cost = sum(dp.amount for dp in data_points)

        # Calculate date range
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days or 1

        avg_daily_cost = total_cost / days

        # Get top services
        service_costs: dict[str, float] = {}
        for dp in data_points:
            if dp.service:
                service_costs[dp.service] = service_costs.get(dp.service, 0) + dp.amount

        top_services = [
            {"service": service, "cost": round(cost, 2)}
            for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return CostSummary(
            total_cost=round(total_cost, 2),
            average_daily_cost=round(avg_daily_cost, 2),
            period_start=start_date,
            period_end=end_date,
            top_services=top_services,
        )

    async def _get_rightsizing_recommendations(
        self,
        min_savings: float,
    ) -> list[OptimizationRecommendation]:
        """Get EC2 right-sizing recommendations."""
        try:
            data = self.ce_client.get_rightsizing_recommendations()
            recommendations = []

            for rec in data.get("RightsizingRecommendations", []):
                current_instance = rec.get("CurrentInstance", {})
                savings = float(
                    rec.get("ModifyRecommendationDetail", {})
                    .get("TargetInstances", [{}])[0]
                    .get("EstimatedMonthlySavings", 0),
                )

                if savings >= min_savings:
                    recommendations.append(
                        OptimizationRecommendation(
                            recommendation_type=OptimizationType.RIGHT_SIZING,
                            resource_id=current_instance.get("ResourceId"),
                            resource_type="EC2 Instance",
                            current_cost=float(current_instance.get("MonthlyCost", 0)),
                            estimated_savings=round(savings, 2),
                            savings_percentage=round(
                                (savings / float(current_instance.get("MonthlyCost", 1))) * 100,
                                2,
                            ),
                            description=f"Right-size {current_instance.get('ResourceId')}",
                            action_items=[
                                "Review instance metrics",
                                "Create backup/snapshot",
                                "Apply new instance type",
                            ],
                            priority="HIGH" if savings > 500 else "MEDIUM",
                        ),
                    )

            return recommendations

        except Exception as e:
            logger.warning(f"Could not get rightsizing recommendations: {e}")
            return []

    async def _get_savings_plans_recommendations(
        self,
        min_savings: float,
    ) -> list[OptimizationRecommendation]:
        """Get Savings Plans recommendations."""
        try:
            data = self.ce_client.get_savings_plans_recommendations()
            recommendations = []

            for rec in data.get("SavingsPlansPurchaseRecommendation", {}).get(
                "SavingsPlansPurchaseRecommendationDetails",
                [],
            ):
                savings = float(rec.get("EstimatedMonthlySavingsAmount", 0))

                if savings >= min_savings:
                    recommendations.append(
                        OptimizationRecommendation(
                            recommendation_type=OptimizationType.SAVINGS_PLANS,
                            resource_id=None,
                            resource_type="Savings Plan",
                            current_cost=float(rec.get("EstimatedOnDemandCost", 0)),
                            estimated_savings=round(savings, 2),
                            savings_percentage=round(
                                float(rec.get("EstimatedSavingsPercentage", 0)),
                                2,
                            ),
                            description=f"Purchase {rec.get('SavingsPlansType')} Savings Plan",
                            action_items=[
                                "Review commitment terms",
                                "Validate usage patterns",
                                "Purchase Savings Plan",
                            ],
                            priority="HIGH" if savings > 1000 else "MEDIUM",
                        ),
                    )

            return recommendations

        except Exception as e:
            logger.warning(f"Could not get Savings Plans recommendations: {e}")
            return []

    async def _get_reservation_recommendations(
        self,
        min_savings: float,
    ) -> list[OptimizationRecommendation]:
        """Get Reserved Instance recommendations."""
        try:
            data = self.ce_client.get_reservation_recommendations()
            recommendations = []

            for rec in data.get("Recommendations", []):
                details = rec.get("RecommendationDetails", {})
                savings = float(details.get("EstimatedMonthlySavingsAmount", 0))

                if savings >= min_savings:
                    recommendations.append(
                        OptimizationRecommendation(
                            recommendation_type=OptimizationType.RESERVED_INSTANCES,
                            resource_id=None,
                            resource_type="Reserved Instance",
                            current_cost=float(details.get("EstimatedOnDemandCost", 0)),
                            estimated_savings=round(savings, 2),
                            savings_percentage=round(
                                float(details.get("EstimatedSavingsPercentage", 0)),
                                2,
                            ),
                            description="Purchase Reserved Instances",
                            action_items=[
                                "Review RI terms and conditions",
                                "Validate instance usage",
                                "Purchase Reserved Instances",
                            ],
                            priority="MEDIUM",
                        ),
                    )

            return recommendations

        except Exception as e:
            logger.warning(f"Could not get RI recommendations: {e}")
            return []

    async def _get_cost_forecast(self) -> dict[str, Any]:
        """Get cost forecast for next 30 days."""
        try:
            start_date = datetime.now().strftime("%Y-%m-%d")
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

            forecast = self.ce_client.get_cost_forecast(start_date=start_date, end_date=end_date)

            return {
                "period_start": start_date,
                "period_end": end_date,
                "forecasted_cost": round(float(forecast.get("Total", {}).get("Amount", 0)), 2),
                "unit": "USD",
            }

        except Exception as e:
            logger.warning(f"Could not get cost forecast: {e}")
            return {}

    async def _identify_idle_resources(self) -> list[dict[str, Any]]:
        """Identify idle resources.

        In production, this would integrate with CloudWatch metrics,
        AWS Compute Optimizer, and Trusted Advisor.
        """
        # Placeholder implementation
        logger.info("Identifying idle resources (placeholder)")
        return []

    async def _identify_unused_resources(self) -> list[dict[str, Any]]:
        """Identify unused resources.

        In production, this would check for unattached EBS volumes,
        unused Elastic IPs, orphaned snapshots, etc.
        """
        # Placeholder implementation
        logger.info("Identifying unused resources (placeholder)")
        return []


# Global service instance
_cost_optimizer_service: CostOptimizerService | None = None


def get_cost_optimizer_service() -> CostOptimizerService:
    """Get or create the global Cost Optimizer service instance.

    Returns:
        CostOptimizerService instance

    """
    global _cost_optimizer_service

    if _cost_optimizer_service is None:
        _cost_optimizer_service = CostOptimizerService()

    return _cost_optimizer_service
