# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FastAPI routes for Gemini AI analysis."""

from fastapi import APIRouter, Depends, HTTPException

from app.models.gemini import (
    ComparisonAnalysisRequest,
    ComparisonAnalysisResponse,
    GeminiAnalysisRequest,
    GeminiAnalysisResponse,
)
from app.services.gemini_service import GeminiService

router = APIRouter(prefix="/api/gemini", tags=["gemini-analysis"])


# Dependency to get Gemini service
def get_gemini_service() -> GeminiService:
    """Get the Gemini service instance."""
    return None


@router.get("/status")
async def get_gemini_status(service: GeminiService = Depends(get_gemini_service)):  # noqa: B008
    """Check if Gemini AI is available."""
    available = service.is_available()
    return {
        "available": available,
        "model": service.model_name if available else None,
        "message": "Gemini AI is ready" if available else "Gemini AI not configured",
    }


@router.post("/analyze", response_model=GeminiAnalysisResponse)
async def analyze_system(
    request: GeminiAnalysisRequest,
    service: GeminiService = Depends(get_gemini_service),  # noqa: B008
):
    """Perform AI-powered analysis of a system using Gemini.

    This endpoint can analyze:
    - Ingestion Layer architecture and performance
    - Compliance and ethical adherence
    - Multi-source coverage
    - Custom system analysis
    """
    if not service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Gemini AI is not available. Please configure API key.",
        )

    try:
        response = await service.analyze(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}") from e


@router.post("/compare", response_model=ComparisonAnalysisResponse)
async def compare_systems(
    request: ComparisonAnalysisRequest,
    service: GeminiService = Depends(get_gemini_service),  # noqa: B008
):
    """Compare two systems (e.g., Judge 6 vs Ingestion Layer).

    Provides comparative analysis across:
    - Architecture
    - Key Metrics
    - Integration approaches
    - Unique features
    - Cost models
    - Quality focus

    Returns synergies, conflicts, and integration recommendations.
    """
    if not service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Gemini AI is not available. Please configure API key.",
        )

    try:
        response = await service.compare_systems(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e!s}") from e


@router.post("/analyze/ingestion-layer")
async def analyze_ingestion_layer(
    architecture_specs: str,
    metrics_data: dict = None,
    documentation: str = None,
    service: GeminiService = Depends(get_gemini_service),  # noqa: B008
):
    """Specialized endpoint for Gemini Ingestion Layer Analysis.

    Analyzes:
    - GKE CronJob Multi-Container architecture
    - Runtime efficiency (~45 min/night target)
    - Quality gates (items, sources, costs, scores)
    - Ethical compliance (robots.txt, rate limiting)
    - Multi-source coverage (YouTube, Twitter, News, etc.)
    - Tier classification (1/2/3 distribution)
    - AM Briefing delivery effectiveness
    - Monthly operational cost (~$77 target)
    """
    if not service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Gemini AI is not available. Please configure API key.",
        )

    request = GeminiAnalysisRequest(
        analysis_type="ingestion_layer",
        target="Gemini Ingestion Layer",
        architecture_specs=architecture_specs,
        metrics_data=metrics_data,
        documentation=documentation,
        confidence_threshold=0.6,  # Pre-prod threshold
        include_recommendations=True,
        detailed_analysis=True,
    )

    try:
        response = await service.analyze(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e!s}") from e
