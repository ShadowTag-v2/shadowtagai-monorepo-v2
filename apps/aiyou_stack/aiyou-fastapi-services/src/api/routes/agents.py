"""API routes for AI agents"""

from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.agents.market_analyst.agent import MarketAnalystAgent
from src.agents.market_analyst.config import MARKET_ANALYST_CONFIG
from src.models.schemas import (
    AgentInfo,
    CompetitorAnalysisRequest,
    CompetitorAnalysisResponse,
    FeaturePrioritizationRequest,
    HealthResponse,
    MarketAnalysisRequest,
    MarketAnalysisResponse,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Initialize Market Analyst agent
try:
    market_analyst = MarketAnalystAgent()
except ValueError as e:
    market_analyst = None
    print(f"Warning: Market Analyst agent not initialized: {e}")


@router.post(
    "/market-analyst/analyze",
    response_model=MarketAnalysisResponse,
    summary="Perform market analysis",
    description="Analyze competitive landscape, features, and market positioning",
)
async def analyze_market(request: MarketAnalysisRequest) -> MarketAnalysisResponse:
    """Perform comprehensive market analysis using Market Analyst agent

    This endpoint accepts:
    - A text prompt describing the analysis needed
    - Optional product name, competitors, and features
    - Analysis type selection

    Returns detailed competitive analysis with strategic recommendations.
    """
    if market_analyst is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market Analyst agent not available. Check ANTHROPIC_API_KEY.",
        )

    try:
        # Build context from request
        context = {"analysis_type": request.analysis_type.value}

        if request.product:
            context["product"] = request.product
        if request.competitors:
            context["competitors"] = request.competitors
        if request.features:
            context["features"] = request.features

        # Process request
        result = await market_analyst.process(
            prompt=request.prompt,
            context=context,
            stream=request.stream if hasattr(request, "stream") else False,
        )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"],
            )

        return MarketAnalysisResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {e!s}",
        )


@router.post(
    "/market-analyst/competitor-analysis",
    response_model=CompetitorAnalysisResponse,
    summary="Structured competitor analysis",
    description="Get detailed feature comparison and gap analysis",
)
async def competitor_analysis(request: CompetitorAnalysisRequest) -> CompetitorAnalysisResponse:
    """Perform structured competitor analysis with feature matrix

    This endpoint provides:
    - Feature comparison matrix
    - Coverage statistics
    - Gap analysis
    - Strategic recommendations
    """
    if market_analyst is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market Analyst agent not available. Check ANTHROPIC_API_KEY.",
        )

    try:
        result = market_analyst.analyze_competitors(
            product=request.product,
            competitors=request.competitors,
            features=request.features,
        )

        return CompetitorAnalysisResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitor analysis failed: {e!s}",
        )


@router.post(
    "/market-analyst/prioritize-features",
    summary="Prioritize features",
    description="Prioritize features based on impact and effort",
)
async def prioritize_features(request: FeaturePrioritizationRequest) -> dict[str, Any]:
    """Prioritize features using impact/effort matrix

    Returns features ranked by priority with P0/P1/P2 labels.
    """
    if market_analyst is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market Analyst agent not available. Check ANTHROPIC_API_KEY.",
        )

    try:
        features_list = [feature.dict() for feature in request.features]

        prioritized = market_analyst.tools.prioritize_features(
            features=features_list,
            criteria=request.criteria,
        )

        return {
            "prioritized_features": prioritized,
            "total_features": len(prioritized),
            "p0_count": len([f for f in prioritized if f.get("priority") == "P0"]),
            "p1_count": len([f for f in prioritized if f.get("priority") == "P1"]),
            "p2_count": len([f for f in prioritized if f.get("priority") == "P2"]),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature prioritization failed: {e!s}",
        )


@router.get(
    "/market-analyst/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check Market Analyst agent health and status",
)
async def health() -> HealthResponse:
    """Health check endpoint for Market Analyst agent"""
    if market_analyst is None:
        return HealthResponse(status="unavailable", agent="market_analyst")

    return HealthResponse(
        status="healthy",
        agent="market_analyst",
        version=MARKET_ANALYST_CONFIG["version"],
        capabilities=market_analyst.get_capabilities(),
    )


@router.get(
    "/market-analyst/info",
    response_model=AgentInfo,
    summary="Agent information",
    description="Get detailed information about Market Analyst agent",
)
async def agent_info() -> AgentInfo:
    """Get Market Analyst agent information and capabilities"""
    return AgentInfo(
        name=MARKET_ANALYST_CONFIG["name"],
        version=MARKET_ANALYST_CONFIG["version"],
        description=MARKET_ANALYST_CONFIG["description"],
        capabilities=MARKET_ANALYST_CONFIG["features"],
        use_cases=MARKET_ANALYST_CONFIG["use_cases"],
        analysis_types=list(MARKET_ANALYST_CONFIG.get("analysis_frameworks", {}).keys()),
    )


@router.get(
    "/market-analyst/templates",
    summary="Get analysis templates",
    description="Get available analysis templates and frameworks",
)
async def get_templates() -> dict[str, Any]:
    """Get available analysis templates"""
    if market_analyst is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Market Analyst agent not available",
        )

    return {
        "templates": market_analyst.get_templates(),
        "available_templates": list(market_analyst.get_templates().keys()),
    }
