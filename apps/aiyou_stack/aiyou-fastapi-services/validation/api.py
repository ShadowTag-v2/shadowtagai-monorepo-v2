"""PNKLN Core Stack - Judge 6 Validation API

FastAPI service exposing validation endpoints across 4 namespaces:
- ingestion (validates items from ingestion layer)
- shadowtag (validates authentication requests)
- shadowtag_v4 (validates content for platform)
- ShadowTagjr (validates governance decisions)
"""

from datetime import datetime

import structlog
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, make_asgi_app
from pydantic import BaseModel

from ingestion.classification.tier_classifier import IngestedItem, TierScore
from validation.judge6 import Judge6Validator, ValidationResult, ValidationStatus

logger = structlog.get_logger(__name__)


# Prometheus metrics
validation_requests = Counter(
    "judge6_validation_requests_total",
    "Total validation requests",
    ["namespace", "status"],
)
validation_latency = Histogram(
    "judge6_validation_latency_seconds",
    "Validation latency",
    ["namespace"],
)


# Pydantic models for API
class ValidationRequest(BaseModel):
    """Request to validate an item."""

    item: IngestedItem
    tier_score: TierScore
    namespace: str = "ingestion"  # ingestion, shadowtag, shadowtag_v4, ShadowTagjr


class ValidationResponse(BaseModel):
    """Response from validation."""

    item_id: str
    status: str
    risk_level: str
    confidence_score: float
    validation_checks: dict
    failure_reasons: list[str]
    latency_ms: float
    timestamp: datetime

    # ATP 5-19
    severity: int
    probability: int
    risk_score: int

    # ShadowTagJR
    jr_compliant: bool
    jr_reasoning: str


class BatchValidationRequest(BaseModel):
    """Request to validate multiple items."""

    items: list[ValidationRequest]
    max_concurrent: int = 10


class BatchValidationResponse(BaseModel):
    """Response for batch validation."""

    results: list[ValidationResponse]
    total: int
    passed: int
    failed: int
    flagged: int
    blocked: int
    avg_latency_ms: float


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    validator_ready: bool
    total_validations: int
    avg_latency_ms: float


# Create FastAPI app
app = FastAPI(
    title="Judge 6 Validation API",
    description="PNKLN Core Stack validation layer with ATP 5-19 risk assessment",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Global validator instance
_validator: Judge6Validator | None = None


def get_validator() -> Judge6Validator:
    """Dependency injection for validator."""
    global _validator

    if _validator is None:
        _validator = Judge6Validator()

    return _validator


@app.on_event("startup")
async def startup_event():
    """Initialize validator on startup."""
    global _validator
    _validator = Judge6Validator()
    logger.info("judge6_api_started")


@app.get("/health", response_model=HealthResponse)
async def health_check(validator: Judge6Validator = Depends(get_validator)):
    """Health check endpoint."""
    stats = validator.get_stats()

    return HealthResponse(
        status="healthy",
        validator_ready=True,
        total_validations=stats["total_validations"],
        avg_latency_ms=stats["avg_latency_ms"],
    )


@app.post("/validate", response_model=ValidationResponse)
async def validate_item(
    request: ValidationRequest,
    validator: Judge6Validator = Depends(get_validator),
):
    """Validate a single item.

    Performs multi-stage validation including:
    - PyTorch safety screening
    - Metadata validation
    - ATP 5-19 risk assessment
    - Gemini deep analysis (if needed)
    - ShadowTagJR compliance check
    """
    try:
        with validation_latency.labels(namespace=request.namespace).time():
            result = await validator.validate(request.item, request.tier_score)

        # Track metrics
        validation_requests.labels(namespace=request.namespace, status=result.status.value).inc()

        return _result_to_response(result)

    except Exception as e:
        logger.error("validation_error", item_id=request.item.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Validation failed: {e!s}")


@app.post("/validate/batch", response_model=BatchValidationResponse)
async def validate_batch(
    request: BatchValidationRequest,
    validator: Judge6Validator = Depends(get_validator),
):
    """Validate multiple items in batch.

    Processes items concurrently up to max_concurrent limit.
    """
    import asyncio

    results = []
    status_counts = {
        ValidationStatus.PASSED: 0,
        ValidationStatus.FAILED: 0,
        ValidationStatus.FLAGGED: 0,
        ValidationStatus.BLOCKED: 0,
    }

    async def validate_one(req: ValidationRequest) -> ValidationResult:
        return await validator.validate(req.item, req.tier_score)

    # Process batch with concurrency limit
    semaphore = asyncio.Semaphore(request.max_concurrent)

    async def validate_with_semaphore(req: ValidationRequest):
        async with semaphore:
            return await validate_one(req)

    validation_results = await asyncio.gather(
        *[validate_with_semaphore(req) for req in request.items],
        return_exceptions=True,
    )

    # Process results
    total_latency = 0.0

    for result in validation_results:
        if isinstance(result, Exception):
            logger.error("batch_validation_item_failed", error=str(result))
            continue

        results.append(_result_to_response(result))
        status_counts[result.status] += 1
        total_latency += result.latency_ms

    avg_latency = total_latency / len(results) if results else 0.0

    return BatchValidationResponse(
        results=results,
        total=len(results),
        passed=status_counts[ValidationStatus.PASSED],
        failed=status_counts[ValidationStatus.FAILED],
        flagged=status_counts[ValidationStatus.FLAGGED],
        blocked=status_counts[ValidationStatus.BLOCKED],
        avg_latency_ms=round(avg_latency, 2),
    )


@app.get("/stats")
async def get_stats(validator: Judge6Validator = Depends(get_validator)):
    """Get validation statistics."""
    return validator.get_stats()


def _result_to_response(result: ValidationResult) -> ValidationResponse:
    """Convert ValidationResult to API response."""
    return ValidationResponse(
        item_id=result.item_id,
        status=result.status.value,
        risk_level=result.risk_level.value,
        confidence_score=result.confidence_score,
        validation_checks=result.validation_checks,
        failure_reasons=result.failure_reasons,
        latency_ms=result.latency_ms,
        timestamp=result.timestamp,
        severity=result.severity,
        probability=result.probability,
        risk_score=result.risk_score,
        jr_compliant=result.jr_compliant,
        jr_reasoning=result.jr_reasoning,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("validation.api:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
