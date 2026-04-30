"""Growth Engineer API Routes

FastAPI routes for the Growth Engineer agent.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.agents import GrowthEngineerAgent
from app.models import (
    ABTestRequest,
    AgentMetadata,
    AgentResponse,
    AnalyticsTrackingRequest,
    EngagementFeatureRequest,
    GeneralGrowthQuery,
    GrowthMetricsRequest,
    HealthResponse,
    ReferralOptimizationRequest,
    UserHookAnalysisRequest,
    ViralLoopRequest,
)

router = APIRouter(
    prefix="/api/v1/growth",
    tags=["Growth Engineering"],
    responses={404: {"description": "Not found"}},
)


# Initialize the Growth Engineer agent
growth_agent = GrowthEngineerAgent()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for the Growth Engineer agent."""
    metadata = growth_agent.get_metadata()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        agent=metadata["name"],
        version=metadata["version"],
    )


@router.get("/metadata", response_model=AgentMetadata)
async def get_agent_metadata():
    """Get metadata about the Growth Engineer agent."""
    metadata = growth_agent.get_metadata()
    return AgentMetadata(**metadata)


@router.post("/analyze/user-hooks", response_model=AgentResponse)
async def analyze_user_hooks(request: UserHookAnalysisRequest):
    """Analyze application to find user hooks and engagement opportunities.

    This endpoint helps identify:
    - Current activation points and "aha moments"
    - Friction points that prevent engagement
    - Opportunities for new hooks and engagement features
    - Recommended hook implementation strategy
    - Success metrics to track
    """
    try:
        app_data = {
            "app_name": request.app_name,
            "user_flows": request.user_flows,
            "current_features": request.current_features,
            "metrics": request.metrics,
            "goals": request.goals,
        }

        result = await growth_agent.analyze_user_hooks(app_data)

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type=result["analysis_type"],
            results=result["results"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing user hooks: {e!s}",
        ) from e


@router.post("/design/viral-loop", response_model=AgentResponse)
async def design_viral_loop(request: ViralLoopRequest):
    """Design a viral loop mechanism for your product.

    This endpoint provides:
    - Viral loop mechanism design
    - Expected viral coefficient (k-factor) calculation
    - Implementation steps and technical requirements
    - Key metrics to track
    - A/B testing strategy for optimization
    - Potential challenges and solutions
    """
    try:
        product_info = {
            "product_name": request.product_name,
            "value_proposition": request.value_proposition,
            "target_audience": request.target_audience,
            "current_users": request.current_users,
            "sharing_incentive": request.sharing_incentive,
            "constraints": request.constraints,
        }

        result = await growth_agent.design_viral_loop(product_info)

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type=result["analysis_type"],
            results=result["results"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error designing viral loop: {e!s}",
        ) from e


@router.post("/experiment/ab-test", response_model=AgentResponse)
async def create_ab_test(request: ABTestRequest):
    """Create and configure an A/B test experiment.

    This endpoint provides:
    - Null and alternative hypotheses
    - Sample size calculation
    - Test duration estimate
    - Statistical significance threshold
    - Implementation code/pseudocode
    - Analysis plan and decision criteria
    - Potential confounding factors
    """
    try:
        experiment_config = {
            "experiment_name": request.experiment_name,
            "hypothesis": request.hypothesis,
            "variants": request.variants,
            "primary_metric": request.primary_metric,
            "secondary_metrics": request.secondary_metrics,
            "expected_effect_size": request.expected_effect_size,
            "traffic_allocation": request.traffic_allocation,
        }

        result = await growth_agent.create_ab_test(experiment_config)

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type=result["analysis_type"],
            results=result["results"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating A/B test: {e!s}",
        ) from e


@router.post("/analyze/metrics", response_model=AgentResponse)
async def analyze_growth_metrics(request: GrowthMetricsRequest):
    """Analyze growth metrics and provide optimization recommendations.

    This endpoint provides:
    - Key insights from the data
    - Growth bottlenecks and opportunities
    - Metric health assessment
    - Prioritized recommendations for improvement
    - Expected impact of each recommendation
    - Implementation complexity and timeline
    """
    try:
        metrics_data = {
            "metrics": request.metrics,
            "time_period": request.time_period,
            "goals": request.goals,
            "benchmarks": request.benchmarks,
        }

        result = await growth_agent.analyze_growth_metrics(metrics_data)

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type=result["analysis_type"],
            results=result["results"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing growth metrics: {e!s}",
        ) from e


@router.post("/design/engagement-feature", response_model=AgentResponse)
async def design_engagement_feature(request: EngagementFeatureRequest):
    """Design an engagement feature with viral potential.

    This endpoint provides:
    - Feature design and user experience flow
    - Engagement mechanics and psychology principles used
    - Viral potential and sharing opportunities
    - Implementation technical requirements
    - Success metrics and KPIs
    - Potential risks and ethical considerations
    - Rollout and testing strategy
    """
    try:
        feature_request = {
            "feature_type": request.feature_type,
            "objective": request.objective,
            "target_users": request.target_users,
            "constraints": request.constraints,
            "existing_features": request.existing_features,
        }

        result = await growth_agent.design_engagement_feature(feature_request)

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type=result["analysis_type"],
            results=result["results"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error designing engagement feature: {e!s}",
        ) from e


@router.post("/implement/analytics", response_model=AgentResponse)
async def implement_analytics_tracking(request: AnalyticsTrackingRequest):
    """Implement analytics tracking for growth metrics.

    This endpoint provides:
    - Event taxonomy and naming conventions
    - Implementation code for tracking
    - Data schema and storage recommendations
    - Dashboard and reporting structure
    - Privacy and compliance considerations
    - Testing and validation approach
    """
    try:
        tracking_requirements = {
            "events_to_track": request.events_to_track,
            "metrics_needed": request.metrics_needed,
            "platform": request.platform,
            "tools": request.tools,
            "compliance_requirements": request.compliance_requirements,
        }

        result = await growth_agent.implement_analytics_tracking(tracking_requirements)

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type=result["analysis_type"],
            results=result["results"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error implementing analytics: {e!s}",
        ) from e


@router.post("/optimize/referral", response_model=AgentResponse)
async def optimize_referral_system(request: ReferralOptimizationRequest):
    """Optimize an existing referral system for better performance.

    This endpoint provides:
    - Current performance analysis
    - Bottlenecks in the referral flow
    - Optimization opportunities (incentives, UX, messaging)
    - A/B test ideas for improvement
    - Expected impact on referral metrics
    - Implementation plan and code changes
    """
    try:
        referral_data = {
            "referral_metrics": request.referral_metrics,
            "referral_flow": request.referral_flow,
            "incentives": request.incentives,
            "issues": request.issues,
        }

        result = await growth_agent.optimize_referral_system(referral_data)

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type=result["analysis_type"],
            results=result["results"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing referral system: {e!s}",
        ) from e


@router.post("/query", response_model=AgentResponse)
async def general_growth_query(request: GeneralGrowthQuery):
    """Handle general growth engineering queries.

    Use this endpoint for any growth engineering questions or requests
    that don't fit into the specific categories above.
    """
    try:
        result = await growth_agent.general_growth_query(
            user_query=request.query,
            context=request.context,
        )

        return AgentResponse(
            success=True,
            timestamp=result["timestamp"],
            analysis_type="general",
            results=result["results"],
            metadata={"query": result["query"]},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {e!s}",
        ) from e
