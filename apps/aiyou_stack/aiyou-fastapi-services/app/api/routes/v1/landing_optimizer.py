"""API routes for Landing Page Optimizer"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import AgentException, ValidationException
from app.services.landing_page_optimizer.schemas import (
    GenerateCTARequest,
    GenerateCTAResponse,
    GenerateHeadlinesRequest,
    GenerateHeadlinesResponse,
    GenerateSocialProofRequest,
    GenerateSocialProofResponse,
    OptimizePageRequest,
    OptimizePageResponse,
)
from app.services.landing_page_optimizer.service import LandingPageOptimizerService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/landing-optimizer", tags=["landing-optimizer"])


def get_optimizer_service() -> LandingPageOptimizerService:
    """Dependency to get optimizer service instance"""
    return LandingPageOptimizerService()


@router.get("/")
async def service_info():
    """Get information about the Landing Page Optimizer service"""
    return {
        "service": "Landing Page Optimizer",
        "version": "1.0.0",
        "description": "AI-powered landing page optimization service using Claude",
        "capabilities": [
            "Landing page analysis and optimization",
            "Headline generation and testing",
            "CTA optimization",
            "Social proof suggestions",
            "Conversion rate improvement recommendations",
        ],
        "endpoints": {
            "analyze": "POST /analyze - Analyze and optimize a landing page",
            "headlines": "POST /headlines - Generate headline variations",
            "ctas": "POST /ctas - Generate CTA variations",
            "social_proof": "POST /social-proof - Generate social proof suggestions",
        },
    }


@router.post(
    "/analyze",
    response_model=OptimizePageResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze landing page",
    description="Analyze a landing page and provide comprehensive optimization recommendations",
)
async def analyze_landing_page(
    request: OptimizePageRequest,
    service: LandingPageOptimizerService = Depends(get_optimizer_service),
) -> OptimizePageResponse:
    """Analyze a landing page for optimization opportunities

    This endpoint performs a comprehensive analysis of your landing page content,
    identifying strengths, weaknesses, and providing actionable recommendations
    to improve conversion rates.

    Args:
        request: Landing page content and analysis parameters

    Returns:
        Detailed analysis with recommendations, headline variations, CTA suggestions, etc.

    Raises:
        HTTPException: If analysis fails

    """
    try:
        logger.info(f"Analyzing landing page - Focus: {request.focus_areas}")

        # Perform optimization analysis
        analysis = await service.optimize_page(request)

        response = OptimizePageResponse(
            status="success",
            analysis=analysis,
            metadata={
                "focus_areas": [area.value for area in request.focus_areas],
                "has_conversion_data": request.current_conversion_rate is not None,
            },
        )

        logger.info(f"Analysis completed - Score: {analysis.overall_score}")
        return response

    except AgentException as e:
        logger.error(f"Agent error during analysis: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Agent error", "message": e.message, "details": e.details},
        )
    except ValidationException as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Validation error", "message": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception(f"Unexpected error during analysis: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred during analysis",
            },
        )


@router.post(
    "/headlines",
    response_model=GenerateHeadlinesResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate headline variations",
    description="Generate compelling headline variations for your landing page",
)
async def generate_headlines(
    request: GenerateHeadlinesRequest,
    service: LandingPageOptimizerService = Depends(get_optimizer_service),
) -> GenerateHeadlinesResponse:
    """Generate headline variations

    Creates multiple headline variations optimized for conversion,
    each with reasoning and target emotion.

    Args:
        request: Headline generation parameters

    Returns:
        List of headline variations with explanations

    Raises:
        HTTPException: If generation fails

    """
    try:
        logger.info(f"Generating {request.count} headline variations")

        headlines = await service.generate_headlines(request)

        response = GenerateHeadlinesResponse(status="success", headlines=headlines)

        logger.info(f"Generated {len(headlines)} headline variations")
        return response

    except AgentException as e:
        logger.error(f"Agent error generating headlines: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Agent error", "message": e.message},
        )
    except Exception as e:
        logger.exception(f"Error generating headlines: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        )


@router.post(
    "/ctas",
    response_model=GenerateCTAResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate CTA variations",
    description="Generate call-to-action variations optimized for conversions",
)
async def generate_ctas(
    request: GenerateCTARequest,
    service: LandingPageOptimizerService = Depends(get_optimizer_service),
) -> GenerateCTAResponse:
    """Generate CTA (Call-to-Action) variations

    Creates multiple CTA variations with color and placement suggestions,
    optimized for the specified action type and urgency level.

    Args:
        request: CTA generation parameters

    Returns:
        List of CTA variations with explanations

    Raises:
        HTTPException: If generation fails

    """
    try:
        logger.info(f"Generating {request.count} CTA variations for action: {request.action_type}")

        ctas = await service.generate_ctas(request)

        response = GenerateCTAResponse(status="success", ctas=ctas)

        logger.info(f"Generated {len(ctas)} CTA variations")
        return response

    except AgentException as e:
        logger.error(f"Agent error generating CTAs: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Agent error", "message": e.message},
        )
    except Exception as e:
        logger.exception(f"Error generating CTAs: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        )


@router.post(
    "/social-proof",
    response_model=GenerateSocialProofResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate social proof suggestions",
    description="Generate social proof elements to build trust and credibility",
)
async def generate_social_proof(
    request: GenerateSocialProofRequest,
    service: LandingPageOptimizerService = Depends(get_optimizer_service),
) -> GenerateSocialProofResponse:
    """Generate social proof suggestions

    Creates suggestions for social proof elements like testimonials,
    statistics, trust badges, and more.

    Args:
        request: Social proof generation parameters

    Returns:
        List of social proof suggestions with placement recommendations

    Raises:
        HTTPException: If generation fails

    """
    try:
        logger.info(f"Generating social proof for: {request.product_service}")

        suggestions = await service.generate_social_proof(request)

        response = GenerateSocialProofResponse(status="success", suggestions=suggestions)

        logger.info(f"Generated {len(suggestions)} social proof suggestions")
        return response

    except AgentException as e:
        logger.error(f"Agent error generating social proof: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Agent error", "message": e.message},
        )
    except Exception as e:
        logger.exception(f"Error generating social proof: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "message": str(e)},
        )
