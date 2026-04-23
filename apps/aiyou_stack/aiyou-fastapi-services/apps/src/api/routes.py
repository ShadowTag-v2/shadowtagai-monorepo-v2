"""FastAPI Routes for Wealth Acceleration Agent

This module defines the RESTful API endpoints for accessing the
wealth acceleration strategist agent.

Version: 1.0.0
Last Updated: 2025-11-08
"""

from collections.abc import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from ..services.wealth_acceleration_service import (
    AnalysisRequest,
    FunnelAnalysisRequest,
    LTVCalculationRequest,
    MonetizationStrategyRequest,
    OpportunityAssessmentRequest,
    PricingEvaluationRequest,
    RevenueProjectionRequest,
    WealthAccelerationService,
    get_wealth_acceleration_service,
)

# Create FastAPI app
app = FastAPI(
    title="Wealth Acceleration API",
    description="RESTful API for the Wealth Acceleration Strategist Agent",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Wealth Acceleration API",
        "version": "1.0.0",
        "description": "AI-powered wealth acceleration strategist for monetization optimization",
        "endpoints": {
            "POST /analyze": "General analysis endpoint",
            "POST /analyze/monetization": "Complete monetization strategy analysis",
            "POST /analyze/funnel": "Conversion funnel analysis",
            "POST /analyze/pricing": "Pricing strategy evaluation",
            "POST /analyze/projections": "Revenue projections",
            "POST /analyze/ltv": "Customer lifetime value calculation",
            "POST /analyze/opportunities": "Market opportunity assessment",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "wealth-acceleration-api"}


async def stream_response(iterator: AsyncIterator[str]) -> AsyncIterator[bytes]:
    """Convert string iterator to bytes for streaming response"""
    async for chunk in iterator:
        yield chunk.encode("utf-8")


@app.post("/analyze")
async def analyze(
    request: AnalysisRequest,
    service: WealthAccelerationService = Depends(get_wealth_acceleration_service),
):
    """General analysis endpoint for custom queries

    This endpoint allows you to send any custom query to the wealth acceleration agent
    along with optional business context.

    Returns a streaming response with the agent's analysis.
    """
    try:
        return StreamingResponse(
            stream_response(
                service.analyze(
                    user_prompt=request.prompt,
                    business_context=request.business_context,
                ),
            ),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}") from e


@app.post("/analyze/monetization")
async def analyze_monetization(
    request: MonetizationStrategyRequest,
    service: WealthAccelerationService = Depends(get_wealth_acceleration_service),
):
    """Analyze complete monetization strategy

    This endpoint provides a comprehensive analysis of your monetization strategy,
    including:
    - Revenue leak identification
    - Complete monetization architecture design
    - Customer journey mapping
    - 30-day implementation roadmap
    - Immediate action challenges

    Returns a streaming response with detailed strategic analysis.
    """
    try:
        return StreamingResponse(
            stream_response(service.analyze_monetization_strategy(request)),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monetization analysis failed: {e!s}") from e


@app.post("/analyze/funnel")
async def analyze_funnel(
    request: FunnelAnalysisRequest,
    service: WealthAccelerationService = Depends(get_wealth_acceleration_service),
):
    """Analyze conversion funnel

    This endpoint analyzes your conversion funnel stages to identify:
    - Biggest conversion leaks
    - Tactical fixes for each stage
    - Expected revenue impact of optimizations
    - Immediate action items

    Returns a streaming response with funnel analysis and recommendations.
    """
    try:
        return StreamingResponse(
            stream_response(service.analyze_funnel(request)),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Funnel analysis failed: {e!s}") from e


@app.post("/analyze/pricing")
async def evaluate_pricing(
    request: PricingEvaluationRequest,
    service: WealthAccelerationService = Depends(get_wealth_acceleration_service),
):
    """Evaluate pricing strategy

    This endpoint evaluates your pricing strategy and provides:
    - Assessment of current pricing vs market
    - Optimal pricing recommendations
    - Tiered pricing strategy
    - Immediate pricing experiments to run

    Returns a streaming response with pricing analysis and recommendations.
    """
    try:
        return StreamingResponse(
            stream_response(service.evaluate_pricing(request)),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pricing evaluation failed: {e!s}") from e


@app.post("/analyze/projections")
async def project_revenue(
    request: RevenueProjectionRequest,
    service: WealthAccelerationService = Depends(get_wealth_acceleration_service),
):
    """Calculate revenue projections

    This endpoint projects revenue growth based on your current metrics:
    - Baseline scenario (status quo)
    - Optimized scenario (strategic improvements)
    - Aggressive scenario (maximum execution)
    - Strategic moves to bridge the gap
    - Weekly action items

    Returns a streaming response with revenue projections and strategy.
    """
    try:
        return StreamingResponse(
            stream_response(service.project_revenue(request)),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revenue projection failed: {e!s}") from e


@app.post("/analyze/ltv")
async def calculate_ltv(
    request: LTVCalculationRequest,
    service: WealthAccelerationService = Depends(get_wealth_acceleration_service),
):
    """Calculate customer lifetime value

    This endpoint calculates and optimizes customer LTV:
    - Current LTV analysis
    - Impact of different optimization levers
    - Specific tactics to increase each lever
    - Backend monetization opportunities
    - Immediate implementation steps

    Returns a streaming response with LTV analysis and optimization strategy.
    """
    try:
        return StreamingResponse(
            stream_response(service.calculate_ltv(request)),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LTV calculation failed: {e!s}") from e


@app.post("/analyze/opportunities")
async def assess_opportunities(
    request: OpportunityAssessmentRequest,
    service: WealthAccelerationService = Depends(get_wealth_acceleration_service),
):
    """Assess market opportunities

    This endpoint evaluates different revenue stream opportunities:
    - Highest-leverage opportunities ranking
    - Realistic revenue potential for each
    - Prioritization based on ease, speed, and scale
    - Fastest path to next revenue milestone
    - Immediate validation steps

    Returns a streaming response with opportunity analysis and prioritization.
    """
    try:
        return StreamingResponse(
            stream_response(service.assess_opportunities(request)),
            media_type="text/plain",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Opportunity assessment failed: {e!s}") from e


# Export the app
__all__ = ["app"]
