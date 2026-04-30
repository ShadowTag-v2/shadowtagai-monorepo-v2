"""Gemini Ingestion Layer Router"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.pnkln import EthicalComplianceReport, IngestionMetrics, SourceType
from app.services.gemini_ingestion import GeminiIngestionService

router = APIRouter()
logger = logging.getLogger(__name__)


class RunIngestionRequest(BaseModel):
    """Request to run ingestion pipeline"""

    sources: list[SourceType] | None = None


class RunIngestionResponse(BaseModel):
    """Response from ingestion pipeline run"""

    success: bool
    metrics: IngestionMetrics
    runtime_within_target: bool
    cost_within_budget: bool


@router.post("/run", response_model=RunIngestionResponse)
async def run_ingestion_pipeline(request: RunIngestionRequest):
    """Run the Gemini Ingestion Layer pipeline

    - **sources**: Optional list of sources to ingest from (defaults to all enabled)

    Returns metrics and quality gate results
    """
    try:
        service = GeminiIngestionService()
        metrics = await service.run_ingestion_pipeline(sources=request.sources)

        # Check against targets
        from app.config import settings

        runtime_ok = metrics.runtime_minutes <= settings.INGESTION_RUNTIME_TARGET

        # Estimate monthly cost
        daily_cost = metrics.average_cost_per_item * metrics.items_ingested
        monthly_cost = daily_cost * 30
        cost_ok = monthly_cost <= settings.INGESTION_MONTHLY_BUDGET

        return RunIngestionResponse(
            success=True,
            metrics=metrics,
            runtime_within_target=runtime_ok,
            cost_within_budget=cost_ok,
        )

    except Exception as e:
        logger.error(f"Error running ingestion pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/metrics", response_model=IngestionMetrics)
async def get_latest_metrics():
    """Get latest ingestion metrics

    Returns the most recent metrics from the ingestion pipeline
    """
    # In production, this would fetch from a database or metrics store
    # For now, return a simulated run
    service = GeminiIngestionService()
    metrics = await service.run_ingestion_pipeline()
    return metrics


@router.get("/compliance", response_model=EthicalComplianceReport)
async def get_compliance_report():
    """Get ethical crawling compliance report

    Returns metrics on robots.txt adherence, rate limiting, and flagged domains
    """
    try:
        service = GeminiIngestionService()
        report = await service.get_compliance_report()
        return report

    except Exception as e:
        logger.error(f"Error fetching compliance report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sources")
async def get_enabled_sources():
    """Get list of enabled ingestion sources

    Returns configuration of which source types are currently enabled
    """
    service = GeminiIngestionService()
    return {
        "enabled_sources": [source.value for source in service.enabled_sources],
        "available_sources": [source.value for source in SourceType],
    }


@router.get("/quality-gates")
async def get_quality_gate_config():
    """Get quality gate configuration

    Returns the current quality gate thresholds
    """
    from app.config import settings

    return {
        "min_daily_items": settings.MIN_DAILY_ITEMS,
        "min_unique_sources": settings.MIN_UNIQUE_SOURCES,
        "max_cost_per_item": settings.MAX_COST_PER_ITEM,
        "min_relevance_score": settings.MIN_RELEVANCE_SCORE,
        "tier_1_threshold": settings.TIER_1_THRESHOLD,
        "tier_2_threshold": settings.TIER_2_THRESHOLD,
    }
