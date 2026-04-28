# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Core Stack Router"""

import logging
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.pnkln import AMBriefing, GKENamespaceStatus, PNKLNStackStatus, QualityGateCheck

router = APIRouter()
logger = logging.getLogger(__name__)


class StackHealthResponse(BaseModel):
    """Overall PNKLN stack health response"""

    status: PNKLNStackStatus
    summary: str


@router.get("/status", response_model=StackHealthResponse)
async def get_stack_status():
    """Get overall PNKLN Core Stack status

    Returns health status for all 4 namespaces:
    - Ingestion
    - Validation
    - Processing
    - Delivery
    """
    from app.config import settings

    # Simulate namespace status checks
    # In production, these would query actual GKE namespaces
    ingestion = GKENamespaceStatus(
        namespace=settings.GKE_NAMESPACE_INGESTION,
        healthy=True,
        pod_count=3,
        issues=[],
    )

    validation = GKENamespaceStatus(
        namespace=settings.GKE_NAMESPACE_VALIDATION,
        healthy=True,
        pod_count=2,
        issues=[],
    )

    processing = GKENamespaceStatus(
        namespace=settings.GKE_NAMESPACE_PROCESSING,
        healthy=True,
        pod_count=5,
        issues=[],
    )

    delivery = GKENamespaceStatus(
        namespace=settings.GKE_NAMESPACE_DELIVERY,
        healthy=True,
        pod_count=2,
        issues=[],
    )

    all_healthy = all([ingestion.healthy, validation.healthy, processing.healthy, delivery.healthy])

    stack_status = PNKLNStackStatus(
        ingestion_status=ingestion,
        validation_status=validation,
        processing_status=processing,
        delivery_status=delivery,
        overall_healthy=all_healthy,
        active_alerts=[],
    )

    summary = "All systems operational" if all_healthy else "Issues detected"

    return StackHealthResponse(status=stack_status, summary=summary)


@router.get("/namespaces")
async def list_namespaces():
    """List all PNKLN GKE namespaces

    Returns configuration of the 4-namespace architecture
    """
    from app.config import settings

    return {
        "namespaces": [
            {
                "name": settings.GKE_NAMESPACE_INGESTION,
                "role": "Data collection and ingestion",
                "components": ["Gemini Ingestion Layer", "Source Crawlers"],
            },
            {
                "name": settings.GKE_NAMESPACE_VALIDATION,
                "role": "Content validation and filtering",
                "components": ["Judge 6", "Quality Gates"],
            },
            {
                "name": settings.GKE_NAMESPACE_PROCESSING,
                "role": "Data processing and enrichment",
                "components": ["Tier Classification", "Analytics"],
            },
            {
                "name": settings.GKE_NAMESPACE_DELIVERY,
                "role": "Briefing generation and delivery",
                "components": ["AM Briefing", "Distribution"],
            },
        ],
        "integration_model": "Services called by namespace consumers",
    }


@router.get("/briefing/latest")
async def get_latest_briefing():
    """Get the latest AM briefing

    Returns the most recent morning briefing with highlights
    """
    # In production, fetch from delivery namespace
    from app.config import settings
    from app.models.pnkln import IngestedItem, SourceType, TierClassification

    # Simulate briefing data
    sample_items = [
        IngestedItem(
            id="highlight_1",
            source_type=SourceType.NEWS,
            source_url="https://news.example.com/article1",
            title="Breaking: Important Development",
            content="Sample high-value content",
            tier=TierClassification.TIER_1,
            relevance_score=0.95,
            cost=0.03,
        ),
    ]

    from app.services.gemini_ingestion import GeminiIngestionService

    service = GeminiIngestionService()
    metrics = await service.run_ingestion_pipeline()

    quality_gate = QualityGateCheck(
        daily_items_met=True,
        unique_sources_met=True,
        cost_per_item_met=True,
        relevance_score_met=True,
        actual_daily_items=metrics.items_ingested,
        actual_unique_sources=metrics.unique_sources,
        actual_cost_per_item=metrics.average_cost_per_item,
        actual_relevance_score=metrics.average_relevance_score,
        all_gates_passed=True,
    )

    briefing = AMBriefing(
        format=settings.BRIEFING_FORMAT,
        new_items_count=metrics.items_ingested,
        tier_1_highlights=sample_items,
        ingestion_metrics=metrics,
        quality_gate=quality_gate,
        delivered=True,
        delivery_time=datetime.utcnow(),
    )

    return briefing


@router.get("/config")
async def get_pnkln_config():
    """Get PNKLN Core Stack configuration

    Returns key configuration parameters
    """
    from app.config import settings

    return {
        "stack_version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "gemini": {
            "model": settings.GEMINI_MODEL,
            "ingestion_runtime_target_minutes": settings.INGESTION_RUNTIME_TARGET,
            "monthly_budget": settings.INGESTION_MONTHLY_BUDGET,
            "confidence_threshold": settings.INGESTION_CONFIDENCE_THRESHOLD,
        },
        "judge": {
            "enabled": settings.JUDGE_ENABLED,
            "confidence_threshold": settings.JUDGE_CONFIDENCE_THRESHOLD,
            "fp_rate_threshold": settings.JUDGE_FP_RATE_THRESHOLD,
            "fn_rate_threshold": settings.JUDGE_FN_RATE_THRESHOLD,
        },
        "quality_gates": {
            "min_daily_items": settings.MIN_DAILY_ITEMS,
            "min_unique_sources": settings.MIN_UNIQUE_SOURCES,
            "max_cost_per_item": settings.MAX_COST_PER_ITEM,
            "min_relevance_score": settings.MIN_RELEVANCE_SCORE,
        },
        "namespaces": {
            "ingestion": settings.GKE_NAMESPACE_INGESTION,
            "validation": settings.GKE_NAMESPACE_VALIDATION,
            "processing": settings.GKE_NAMESPACE_PROCESSING,
            "delivery": settings.GKE_NAMESPACE_DELIVERY,
        },
    }
