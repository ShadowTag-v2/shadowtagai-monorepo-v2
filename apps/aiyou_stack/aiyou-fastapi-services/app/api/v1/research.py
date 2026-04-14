"""Research API Endpoint

Multi-source research orchestration via REST API.
Integrates with GeminiResearchAgent for Drive, Gmail, Web search.

Endpoints:
    POST /api/v1/research/       Execute research query
    GET  /api/v1/research/tools  Check available tools
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from shadowtagai.agents.research_agent import get_research_agent
from src.core.research_router import detect_research_intent, is_research_query
from src.core.research_tools import check_tool_availability

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class ResearchRequest(BaseModel):
    """Request model for research endpoint."""

    query: str = Field(..., description="Research query", min_length=3, max_length=1000)
    sources: list[str] | None = Field(
        None, description="Override source selection (drive, gmail, web)",
    )
    max_results_per_source: int = Field(10, description="Maximum results per source", ge=1, le=50)
    enable_synthesis: bool = Field(True, description="Use Gemini to synthesize results into report")


class ResearchResponse(BaseModel):
    """Response model for research endpoint."""

    success: bool
    query: str
    research_output: str
    sources_queried: list[str]
    sources_successful: list[str]
    total_results: int
    total_latency_ms: float
    compliance_status: str
    risk_score: int
    risk_flags: list[str]
    sla_met: bool
    timestamp: str


class ToolAvailabilityResponse(BaseModel):
    """Response model for tool availability check."""

    drive_search: bool
    gmail_search: bool
    web_search: bool
    google_apis_installed: bool
    timestamp: str


class ResearchIntentResponse(BaseModel):
    """Response model for intent detection."""

    is_research: bool
    confidence: float
    intent_type: str
    recommended_sources: list[str]
    extracted_topic: str


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/", response_model=ResearchResponse)
async def execute_research(request: ResearchRequest):
    """Execute multi-source research query.

    Workflow:
    1. Route query to determine sources (or use override)
    2. Execute parallel source queries via GeminiResearchAgent
    3. Apply ATP_519_scan for compliance validation
    4. Return structured research report

    Args:
        request: ResearchRequest with query and options

    Returns:
        ResearchResponse with findings and synthesis

    Raises:
        HTTPException: On execution errors

    """
    try:
        logger.info(f"Research request: {request.query[:50]}...")

        # Get research agent
        agent = get_research_agent()

        # Execute research
        result = await agent.research(request.query)

        return ResearchResponse(
            success=True,
            query=request.query,
            research_output=result.get("research_output", ""),
            sources_queried=result.get("sources_queried", []),
            sources_successful=result.get("sources_successful", []),
            total_results=result.get("total_results", 0),
            total_latency_ms=result.get("context_latency_ms", 0),
            compliance_status=result.get("compliance_status", "unknown"),
            risk_score=result.get("risk_score", 0),
            risk_flags=result.get("risk_flags", []),
            sla_met=result.get("sla_met", False),
            timestamp=datetime.utcnow().isoformat(),
        )

    except TimeoutError as e:
        logger.error(f"Research timeout: {e}")
        raise HTTPException(status_code=504, detail=f"Research query timed out: {e!s}")
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=500, detail=f"Research execution failed: {e!s}")


@router.get("/tools", response_model=ToolAvailabilityResponse)
async def get_tool_availability():
    """Check which research tools are available.

    Returns availability status for:
    - drive_search: Google Drive API
    - gmail_search: Gmail API
    - web_search: Web search API
    """
    availability = check_tool_availability()

    return ToolAvailabilityResponse(
        drive_search=availability.get("drive_search", False),
        gmail_search=availability.get("gmail_search", False),
        web_search=availability.get("web_search", True),
        google_apis_installed=availability.get("google_apis_installed", False),
        timestamp=datetime.utcnow().isoformat(),
    )


@router.post("/detect", response_model=ResearchIntentResponse)
async def detect_intent(query: str):
    """Detect if a query has research intent.

    Useful for routing decisions without executing full research.

    Args:
        query: User query to analyze

    Returns:
        ResearchIntentResponse with detection results

    """
    intent = detect_research_intent(query)

    return ResearchIntentResponse(
        is_research=is_research_query(query),
        confidence=intent.confidence,
        intent_type=intent.intent_type,
        recommended_sources=[s.value for s in intent.recommended_sources],
        extracted_topic=intent.extracted_topic,
    )


@router.get("/health")
async def health_check():
    """Health check for research service."""
    availability = check_tool_availability()

    return {
        "status": "healthy",
        "service": "research",
        "tools": availability,
        "timestamp": datetime.utcnow().isoformat(),
    }
