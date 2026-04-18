"""FastAPI routes for AWS Cost Optimizer Operations.

Endpoints for cost analysis, optimization recommendations, and waste elimination.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.cost_optimizer_models import (
    CostAnalysisRequest,
    CostAnalysisResponse,
    ErrorResponse,
    RecommendationRequest,
    RecommendationsResponse,
    WasteAnalysisResponse,
)
from src.services.cost_optimizer import CostOptimizerService, get_cost_optimizer_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/cost-optimizer",
    tags=["Cost Optimizer"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
    },
)


@router.post(
    "/analyze",
    response_model=CostAnalysisResponse,
    summary="Analyze AWS Costs",
    description="""
    Analyze AWS costs for a specified time period with optional grouping and filtering.

    **Features:**
    - Historical cost analysis
    - Group by service, instance type, region, etc.
    - Filter by specific AWS services
    - Configurable granularity (daily, monthly, hourly)

    **Returns:** Detailed cost breakdown with summary statistics.
    """,
)
async def analyze_costs(
    request: CostAnalysisRequest,
    service: CostOptimizerService = Depends(get_cost_optimizer_service),
) -> CostAnalysisResponse:
    """Analyze AWS costs for the specified parameters."""
    try:
        logger.info(f"Cost analysis request: {request.model_dump()}")

        result = await service.analyze_costs(
            start_date=request.start_date,
            end_date=request.end_date,
            granularity=request.granularity.value,
            group_by=request.group_by,
            service_filter=request.service_filter,
        )

        return result

    except Exception as e:
        logger.error(f"Error in analyze_costs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="Get Optimization Recommendations",
    description="""
    Generate actionable cost optimization recommendations to reduce AWS spending.

    **Optimization Types:**
    - RIGHT_SIZING: Downsize over-provisioned resources
    - IDLE_RESOURCES: Identify and eliminate idle resources
    - SAVINGS_PLANS: Purchase Savings Plans for committed usage
    - RESERVED_INSTANCES: Purchase Reserved Instances
    - AUTO_SCALING: Implement auto-scaling for variable workloads
    - WASTE_ELIMINATION: Remove wasteful spending

    **Target:** 50% cost reduction through systematic optimizations.
    """,
)
async def get_recommendations(
    request: RecommendationRequest,
    service: CostOptimizerService = Depends(get_cost_optimizer_service),
) -> RecommendationsResponse:
    """Get cost optimization recommendations."""
    try:
        logger.info(f"Recommendations request: {request.model_dump()}")

        result = await service.get_optimization_recommendations(
            optimization_types=request.optimization_types,
            min_savings_threshold=request.min_savings_threshold or 100.0,
            include_forecast=request.include_forecast,
        )

        return result

    except Exception as e:
        logger.error(f"Error in get_recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/waste-analysis",
    response_model=WasteAnalysisResponse,
    summary="Analyze Resource Waste",
    description="""
    Identify and quantify wasted AWS spending across your infrastructure.

    **Analyzes:**
    - Idle EC2 instances
    - Unattached EBS volumes
    - Unused Elastic IPs
    - Orphaned snapshots
    - Over-provisioned resources

    **Returns:** Detailed waste breakdown with optimization potential.
    """,
)
async def analyze_waste(
    service: CostOptimizerService = Depends(get_cost_optimizer_service),
) -> WasteAnalysisResponse:
    """Analyze AWS resource waste."""
    try:
        logger.info("Waste analysis request")

        result = await service.analyze_waste()

        return result

    except Exception as e:
        logger.error(f"Error in analyze_waste: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/insights",
    summary="Get Cost Insights",
    description="""
    Get high-level cost insights and trends.

    Provides a quick overview of:
    - Current spending trends
    - Month-over-month changes
    - Top cost drivers
    - Optimization opportunities
    """,
)
async def get_insights(
    days: int = Query(30, ge=1, le=90, description="Number of days to analyze"),
    service: CostOptimizerService = Depends(get_cost_optimizer_service),
):
    """Get cost insights for the specified period."""
    try:
        logger.info(f"Insights request for {days} days")

        # Quick analysis
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        analysis = await service.analyze_costs(
            start_date=start_date,
            end_date=end_date,
            granularity="DAILY",
        )

        # Calculate trend
        if len(analysis.data_points) >= 2:
            recent_avg = sum(dp.amount for dp in analysis.data_points[-7:]) / min(
                7,
                len(analysis.data_points[-7:]),
            )

            earlier_avg = sum(dp.amount for dp in analysis.data_points[:7]) / min(
                7,
                len(analysis.data_points[:7]),
            )

            trend = "increasing" if recent_avg > earlier_avg else "decreasing"
            trend_percentage = (
                abs((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
            )
        else:
            trend = "stable"
            trend_percentage = 0

        return {
            "period_days": days,
            "total_cost": analysis.summary.total_cost,
            "average_daily_cost": analysis.summary.average_daily_cost,
            "top_services": analysis.summary.top_services[:3],
            "trend": trend,
            "trend_percentage": round(trend_percentage, 2),
            "analyzed_at": analysis.analyzed_at,
        }

    except Exception as e:
        logger.error(f"Error in get_insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/status",
    summary="Service Status",
    description="Check the health and status of the Cost Optimizer service.",
)
async def get_status():
    """Get service status and health check."""
    try:
        # Test AWS connection
        service = get_cost_optimizer_service()
        aws_connected = True

        try:
            # Quick test call
            service.ce_client.get_cost_categories()
        except Exception as e:
            logger.warning(f"AWS connection test failed: {e}")
            aws_connected = False

        return {
            "status": "operational" if aws_connected else "degraded",
            "aws_connection": aws_connected,
            "service": "AWS Cost Optimizer Operations",
            "version": "1.0.0",
            "capabilities": [
                "cost_analysis",
                "optimization_recommendations",
                "waste_detection",
                "right_sizing",
                "auto_scaling",
                "savings_plans",
                "reserved_instances",
            ],
        }

    except Exception as e:
        logger.error(f"Error in get_status: {e}")
        return {"status": "error", "error": str(e)}
