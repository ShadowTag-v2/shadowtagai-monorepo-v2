# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 Validation Router"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.pnkln import IngestedItem, ValidationMetrics, ValidationStatus
from app.services.Claude_Code_6 import JudgeSixService

router = APIRouter()
logger = logging.getLogger(__name__)


class ValidateItemRequest(BaseModel):
    """Request to validate a single item"""

    item: IngestedItem
    use_hybrid: bool = True


class ValidateItemResponse(BaseModel):
    """Response from single item validation"""

    status: ValidationStatus
    confidence: float
    item_id: str


class ValidateBatchRequest(BaseModel):
    """Request to validate multiple items"""

    items: list[IngestedItem]


class ValidateBatchResponse(BaseModel):
    """Response from batch validation"""

    metrics: ValidationMetrics
    performance_gates: dict[str, bool]


@router.post("/validate-item", response_model=ValidateItemResponse)
async def validate_single_item(request: ValidateItemRequest):
    """Validate a single ingested item using Judge 6

    - **item**: The ingested item to validate
    - **use_hybrid**: Whether to use hybrid Gemini+PyTorch approach (default: true)

    Returns validation status and confidence score
    """
    try:
        service = JudgeSixService()
        status, confidence = await service.validate_item(
            item=request.item,
            use_hybrid=request.use_hybrid,
        )

        return ValidateItemResponse(status=status, confidence=confidence, item_id=request.item.id)

    except Exception as e:
        logger.error(f"Error validating item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/validate-batch", response_model=ValidateBatchResponse)
async def validate_item_batch(request: ValidateBatchRequest):
    """Validate a batch of items using Judge 6

    - **items**: List of ingested items to validate

    Returns validation metrics and performance gate results
    """
    try:
        service = JudgeSixService()
        metrics = await service.validate_batch(items=request.items)

        # Check performance gates
        gates = service.check_performance_gates(metrics)

        return ValidateBatchResponse(metrics=metrics, performance_gates=gates)

    except Exception as e:
        logger.error(f"Error validating batch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/metrics", response_model=ValidationMetrics)
async def get_validation_metrics():
    """Get latest validation metrics from Judge 6

    Returns performance metrics including latency, error rates, and confidence
    """
    # In production, fetch from metrics store
    # For now, return simulated metrics
    from datetime import datetime

    return ValidationMetrics(
        date=datetime.utcnow(),
        items_validated=1000,
        approved_count=950,
        rejected_count=30,
        review_required_count=20,
        false_positive_rate=0.015,
        false_negative_rate=0.012,
        average_latency_ms=45.0,
        p99_latency_ms=87.0,
        average_confidence=0.89,
    )


@router.get("/gates")
async def get_performance_gates():
    """Get Judge 6 performance gate configuration

    Returns thresholds for FP/FN rates and confidence
    """
    from app.config import settings

    return {
        "enabled": settings.JUDGE_ENABLED,
        "confidence_threshold": settings.JUDGE_CONFIDENCE_THRESHOLD,
        "fp_rate_threshold": settings.JUDGE_FP_RATE_THRESHOLD,
        "fn_rate_threshold": settings.JUDGE_FN_RATE_THRESHOLD,
    }


@router.get("/status")
async def get_judge_status():
    """Get Judge 6 service status

    Returns health and configuration info
    """
    from app.config import settings

    service = JudgeSixService()

    return {
        "enabled": service.enabled,
        "model": settings.GEMINI_MODEL,
        "hybrid_mode": True,
        "confidence_threshold": settings.JUDGE_CONFIDENCE_THRESHOLD,
        "healthy": True,
    }
