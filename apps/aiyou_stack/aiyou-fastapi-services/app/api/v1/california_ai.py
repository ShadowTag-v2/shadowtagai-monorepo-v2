# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""California AI Compliance API Endpoints
======================================
REST API endpoints for California AI regulation compliance.

Endpoints:
- POST /california-ai/assess - Single content assessment
- POST /california-ai/batch - Batch content assessment
- GET /california-ai/violations/{id} - Get violation details
- GET /california-ai/report - Generate compliance report
- POST /california-ai/certify - Generate compliance certificate
- GET /california-ai/usage - Get usage metrics
- GET /california-ai/stats - Get engine statistics
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.models.california_ai import (
    BatchAssessmentRequest,
    BatchAssessmentResult,
    CaliforniaAIAssessmentRequest,
    CaliforniaAIAssessmentResult,
    ComplianceAttestation,
    ComplianceReport,
    ComplianceReportRequest,
    UsageMetrics,
    UsageTier,
)
from app.services.california_ai_engine import (
    get_california_ai_engine,
)

router = APIRouter()


# =============================================================================
# API Key Tiers (Simple implementation)
# =============================================================================

# In production, use proper auth system
API_KEY_TIERS = {
    "free-demo-key": UsageTier.FREE,
    "starter-key-001": UsageTier.STARTER,
    "growth-key-001": UsageTier.GROWTH,
    "enterprise-key-001": UsageTier.ENTERPRISE,
}


def get_tier_from_key(api_key: str | None) -> UsageTier:
    """Get usage tier from API key"""
    if not api_key:
        return UsageTier.FREE
    return API_KEY_TIERS.get(api_key, UsageTier.FREE)


# =============================================================================
# Request/Response Models
# =============================================================================


class QuickAssessRequest(BaseModel):
    """Simple assessment request"""

    content: str = Field(..., min_length=1, max_length=50000)
    user_age: int | None = Field(None, ge=0, le=150)
    platform_id: str = Field(default="default")


class QuickAssessResponse(BaseModel):
    """Simple assessment response"""

    is_compliant: bool
    go_decision: bool
    risk_tier: int
    required_actions: list[str]
    self_harm_detected: bool
    disclosure_required: bool
    disclosure_text: str
    latency_ms: float


class CertifyRequest(BaseModel):
    """Certification request"""

    content: str = Field(..., min_length=1)
    content_id: str | None = None
    platform_id: str = Field(default="default")


class StatsResponse(BaseModel):
    """Engine statistics response"""

    total_assessments: int
    compliant: int
    non_compliant: int
    compliance_rate: float
    cache_hit_rate: float
    avg_latency_ms: float


# =============================================================================
# Endpoints
# =============================================================================


@router.post(
    "/assess",
    response_model=CaliforniaAIAssessmentResult,
    summary="Assess content for California AI compliance",
    description="""
    Assess content against California AI chatbot regulations.

    Checks for:
    - Self-harm detection and crisis response
    - AI disclosure requirements
    - Minor protection (explicit content, break reminders)
    - Medical impersonation prevention

    Returns compliance decision with required actions.
    """,
)
async def assess_endpoint(
    request: CaliforniaAIAssessmentRequest,
    x_api_key: str | None = Header(None),
) -> CaliforniaAIAssessmentResult:
    """Assess content for California AI compliance"""
    try:
        engine = get_california_ai_engine()
        tier = get_tier_from_key(x_api_key)

        result = await engine.assess(request, api_key=x_api_key, tier=tier)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {e!s}") from e


@router.post(
    "/quick",
    response_model=QuickAssessResponse,
    summary="Quick compliance check",
    description="Simple endpoint for quick compliance checks with minimal input.",
)
async def quick_assess(
    request: QuickAssessRequest,
    x_api_key: str | None = Header(None),
) -> QuickAssessResponse:
    """Quick compliance check"""
    try:
        engine = get_california_ai_engine()
        tier = get_tier_from_key(x_api_key)

        full_request = CaliforniaAIAssessmentRequest(
            content=request.content,
            user_age=request.user_age,
            platform_id=request.platform_id,
        )

        result = await engine.assess(full_request, tier=tier)

        return QuickAssessResponse(
            is_compliant=result.is_compliant,
            go_decision=result.go_decision,
            risk_tier=result.risk_tier.value,
            required_actions=[a.value for a in result.required_actions],
            self_harm_detected=result.self_harm_detected,
            disclosure_required=result.disclosure_required,
            disclosure_text=result.disclosure_text,
            latency_ms=result.total_latency_ms,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {e!s}") from e


@router.post(
    "/batch",
    response_model=BatchAssessmentResult,
    summary="Batch content assessment",
    description="""
    Assess multiple content items in batch.

    Requires STARTER tier or higher.
    Up to 100 items per batch.
    """,
)
async def batch_assess(
    request: BatchAssessmentRequest,
    x_api_key: str | None = Header(None),
) -> BatchAssessmentResult:
    """Batch content assessment"""
    try:
        engine = get_california_ai_engine()
        tier = get_tier_from_key(x_api_key)

        if tier == UsageTier.FREE:
            raise HTTPException(
                status_code=402,
                detail="Batch assessment requires STARTER tier or higher",
            )

        result = await engine.batch_assess(request, tier=tier)
        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch assessment failed: {e!s}") from e


@router.get(
    "/report",
    response_model=ComplianceReport,
    summary="Generate compliance report",
    description="Generate compliance report for a time period.",
)
async def get_report(
    start_date: datetime = Query(..., description="Report period start"),  # noqa: B008
    end_date: datetime = Query(default=None, description="Report period end"),  # noqa: B008
    platform_id: str | None = Query(None, description="Filter by platform"),
    x_api_key: str | None = Header(None),
) -> ComplianceReport:
    """Generate compliance report"""
    try:
        tier = get_tier_from_key(x_api_key)

        if tier not in [UsageTier.GROWTH, UsageTier.ENTERPRISE]:
            raise HTTPException(status_code=402, detail="Reports require GROWTH tier or higher")

        engine = get_california_ai_engine()

        if end_date is None:
            end_date = datetime.utcnow()

        request = ComplianceReportRequest(
            start_date=start_date,
            end_date=end_date,
            platform_id=platform_id,
        )

        report = engine.generate_report(request)
        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e!s}") from e


@router.post(
    "/certify",
    response_model=ComplianceAttestation,
    summary="Generate compliance certificate",
    description="Generate a signed compliance attestation for content.",
)
async def certify_content(
    request: CertifyRequest,
    x_api_key: str | None = Header(None),
) -> ComplianceAttestation:
    """Generate compliance certificate"""
    try:
        tier = get_tier_from_key(x_api_key)

        if tier not in [UsageTier.GROWTH, UsageTier.ENTERPRISE]:
            raise HTTPException(
                status_code=402,
                detail="Certification requires GROWTH tier or higher",
            )

        engine = get_california_ai_engine()

        # Run assessment with attestation
        assess_request = CaliforniaAIAssessmentRequest(
            content=request.content,
            content_id=request.content_id,
            platform_id=request.platform_id,
            include_attestation=True,
        )

        result = await engine.assess(assess_request, tier=tier)

        if not result.attestation:
            raise HTTPException(status_code=500, detail="Failed to generate attestation")

        return result.attestation

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Certification failed: {e!s}") from e


@router.get(
    "/usage",
    response_model=UsageMetrics,
    summary="Get usage metrics",
    description="Get usage metrics for billing and monitoring.",
)
async def get_usage(
    platform_id: str = Query(default="default"),
    x_api_key: str | None = Header(None),
) -> UsageMetrics:
    """Get usage metrics"""
    try:
        engine = get_california_ai_engine()
        usage = engine.get_usage(platform_id)
        return usage

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage: {e!s}") from e


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get engine statistics",
    description="Get overall engine statistics and performance metrics.",
)
async def get_stats(
    x_api_key: str | None = Header(None),
) -> StatsResponse:
    """Get engine statistics"""
    try:
        engine = get_california_ai_engine()
        stats = engine.get_stats()

        return StatsResponse(
            total_assessments=stats.get("total_assessments", 0),
            compliant=stats.get("compliant", 0),
            non_compliant=stats.get("non_compliant", 0),
            compliance_rate=stats.get("compliance_rate", 1.0),
            cache_hit_rate=stats.get("cache_hit_rate", 0.0),
            avg_latency_ms=stats.get("avg_latency_ms", 0.0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e!s}") from e


@router.get(
    "/health",
    summary="Health check",
    description="Check if the California AI compliance service is healthy.",
)
async def health_check() -> dict[str, Any]:
    """Health check endpoint"""
    try:
        engine = get_california_ai_engine()
        stats = engine.get_stats()

        return {
            "status": "healthy",
            "service": "california-ai-compliance",
            "version": "1.0.0",
            "total_assessments": stats.get("total_assessments", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "california-ai-compliance",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


# =============================================================================
# Crisis Response Webhook (Optional)
# =============================================================================


@router.post(
    "/webhook/crisis",
    summary="Crisis response webhook",
    description="Internal webhook for crisis response notifications.",
    include_in_schema=False,
)
async def crisis_webhook(
    content_id: str,
    severity: str,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Handle crisis response (internal)"""
    # In production, this would notify appropriate parties
    # Log for now
    background_tasks.add_task(lambda: print(f"CRISIS ALERT: {content_id} - {severity}"))

    return {"status": "acknowledged", "content_id": content_id}
