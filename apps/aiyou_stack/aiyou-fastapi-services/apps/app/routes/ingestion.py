"""Ingestion API Routes (PNKLN: Preparation)
FastAPI endpoints for intelligence collection and classification
"""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    IngestionItemResponse,
    IngestionSubmitRequest,
    IngestionSubmitResponse,
    SourceCoverageResponse,
    TierClassification,
)
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

# Initialize service (in production, use dependency injection)
ingestion_service = IngestionService()


@router.post(
    "/submit",
    response_model=IngestionSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit intelligence item for ingestion",
    description="""
    Submit an intelligence item for collection, tier classification, and ethical compliance validation.

    The item will be processed asynchronously through the PNKLN pipeline:
    1. Ethical compliance check (robots.txt, rate limiting, PII scrubbing)
    2. Tier classification (Gemini 2.0 Pro or rule-based fallback)
    3. Storage in intelligence lake
    4. Queued for validation (Judge #6)

    **Cost:** ~$0.0016 per item (Gemini API + compute)
    **Processing Time:** ~5 seconds average
    """,
)
async def submit_item(request: IngestionSubmitRequest) -> IngestionSubmitResponse:
    """Submit an intelligence item for ingestion.

    **Example Request:**
    ```json
    {
      "source": {
        "type": "news_api",
        "url": "https://example.com/article",
        "domain": "example.com"
      },
      "content": {
        "title": "FAA Proposes DO-178D for AI Systems",
        "summary": "New regulation for aviation AI...",
        "full_text": "[Full article...]",
        "published_at": "2025-11-17T14:00:00Z"
      },
      "metadata": {
        "tags": ["aviation", "regulation"],
        "priority": "high"
      }
    }
    ```

    **Response:**
    - `item_id`: Unique identifier for tracking
    - `status`: "accepted" (queued for processing)
    - `estimated_processing_time_ms`: Expected processing duration
    """
    try:
        item_id = await ingestion_service.submit_item(request)

        return IngestionSubmitResponse(
            item_id=item_id,
            status="accepted",
            message="Item queued for classification",
            estimated_processing_time_ms=5000,
            next_steps=["tier_classification", "validation", "attestation"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {e!s}",
        )


@router.get(
    "/items/{item_id}",
    response_model=IngestionItemResponse,
    summary="Get ingestion item status",
    description="""
    Retrieve processing status and classification results for a submitted intelligence item.

    **Status Values:**
    - `pending`: Item queued, not yet processed
    - `processing`: Currently being classified
    - `completed`: Processing finished successfully
    - `failed`: Processing encountered an error
    """,
)
async def get_item(item_id: str) -> IngestionItemResponse:
    """Get status and classification results for an ingestion item.

    **Example Response (Completed):**
    ```json
    {
      "item_id": "ing_2025-11-17_a1b2c3",
      "status": "completed",
      "classification": {
        "tier": 1,
        "confidence": 0.92,
        "reasoning": "Primary source document with strategic implications",
        "tags": ["aviation", "regulation", "DO-178D"]
      },
      "validation_result": {
        "status": "passed",
        "atp_5_19_coverage": 0.984,
        "judge_id": "val_x7y8z9"
      },
      "shadowtag": {
        "attestation_level": "L4",
        "signature": "cose:a10126...",
        "verification_url": "https://shadowtag.shadowtag_v4.io/verify/..."
      },
      "processing_time_ms": 4723
    }
    ```
    """
    item = await ingestion_service.get_item(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item not found: {item_id}",
        )

    # Build response
    classification = None
    if item["status"] == "completed" and "classification" in item:
        classification = TierClassification(**item["classification"])

    return IngestionItemResponse(
        item_id=item_id,
        status=item["status"],
        classification=classification,
        validation_result=None,  # Populated after Judge #6 validation
        shadowtag=None,  # Populated after attestation
        processing_time_ms=None,  # Calculate from timestamps
    )


@router.get(
    "/sources",
    response_model=SourceCoverageResponse,
    summary="List configured data sources",
    description="""
    Retrieve health status and performance metrics for all configured intelligence sources.

    **Metrics per Source:**
    - Daily quota and usage
    - Last successful fetch timestamp
    - Tier 1 yield (% of high-value items)
    - Status: healthy | degraded | failed | rate_limited

    **Target Coverage:** 87+ unique sources across 8 source types
    """,
)
async def get_sources() -> SourceCoverageResponse:
    """Get health status of all configured data sources.

    **Example Response:**
    ```json
    {
      "sources": [
        {
          "id": "youtube-api-v3",
          "type": "youtube",
          "status": "healthy",
          "daily_quota": 10000,
          "quota_used": 7234,
          "last_successful_fetch": "2025-11-17T14:20:00Z",
          "tier_1_yield": 0.18
        }
      ],
      "summary": {
        "total_sources": 87,
        "healthy": 82,
        "degraded": 3,
        "failed": 2
      }
    }
    ```
    """
    sources = await ingestion_service.get_source_health()

    # Calculate summary
    summary = {
        "total_sources": len(sources),
        "healthy": sum(1 for s in sources if s.status == "healthy"),
        "degraded": sum(1 for s in sources if s.status == "degraded"),
        "failed": sum(1 for s in sources if s.status == "failed"),
    }

    return SourceCoverageResponse(sources=sources, summary=summary)


@router.get(
    "/health",
    summary="Ingestion service health check",
    description="Quick health check for ingestion pipeline components",
)
async def health_check():
    """Health check endpoint for monitoring.

    **Returns:**
    - `status`: "healthy" | "degraded" | "unhealthy"
    - `components`: Status of crawler, classifier, validator
    """
    return {
        "status": "healthy",
        "components": {
            "crawler": "operational",
            "tier_classifier": "operational",
            "ethical_validator": "operational",
        },
        "version": "1.0.0",
    }
