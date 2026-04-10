"""
Compliance API Router

REST API endpoints for the ActiveShield Modular Compliance Framework.
Implements the Phase 1 API as defined in the MCF architecture.

Endpoints:
- POST /blueprint - Generate compliance blueprint from selections
- POST /assess - Run assessment against selected modules
- GET /modules - List available regulation modules
- GET /modules/{id} - Get module details
- POST /validate - Post-generation validation (GPT Store pattern)
- GET /audit/{id} - Retrieve ShadowTag audit proof
- POST /batch - Batch assessment (MCP efficiency)
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.models.compliance import (
    AssessmentInput,
    ComplianceAssessmentResult,
    ComplianceBlueprintRequest,
    ComplianceBlueprintResponse,
    ModuleMetadata,
    RegulationId,
    ValidationRequest,
    ValidationResult,
)
from app.services.compliance_engine import get_compliance_engine

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class ModuleListResponse(BaseModel):
    """Response model for listing available modules"""

    modules: list[ModuleMetadata]
    total_count: int


class ModuleDetailResponse(BaseModel):
    """Detailed module information"""

    metadata: ModuleMetadata
    controls_count: int
    controls: list[dict[str, Any]]
    validation_rules_count: int
    required_evidence: list[dict[str, Any]]


class BatchAssessmentRequest(BaseModel):
    """Request for batch assessment"""

    inputs: list[AssessmentInput] = Field(
        ..., max_length=100, description="List of assessment inputs (max 100)"
    )
    max_concurrent: int = Field(
        default=10, ge=1, le=50, description="Maximum concurrent assessments"
    )


class BatchAssessmentResponse(BaseModel):
    """Response for batch assessment"""

    batch_id: str
    total_submitted: int
    total_completed: int
    total_failed: int
    results: list[ComplianceAssessmentResult]


class AuditTrailResponse(BaseModel):
    """Audit trail retrieval response"""

    assessment_id: str
    audit_hash: str
    timestamp: datetime
    access_type: str = "temporary_signed_url"
    expires_in: str = "15 minutes"
    url: str | None = None


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    initialized: bool
    modules_registered: int
    timestamp: datetime


# ============================================================================
# API ENDPOINTS
# ============================================================================


@router.post(
    "/blueprint",
    response_model=ComplianceBlueprintResponse,
    summary="Generate Compliance Blueprint",
    description="Generate a compliance blueprint based on selected regulations and jurisdictions.",
)
async def generate_blueprint(
    request: ComplianceBlueprintRequest,
    x_api_key: str = Header(..., description="API authentication key"),
) -> ComplianceBlueprintResponse:
    """
    Generate a compliance blueprint based on user's selections.

    Returns:
    - List of selected modules with metadata
    - Total controls to implement
    - Estimated monthly cost
    - API endpoints for SDK integration
    - SDK configuration
    """
    engine = get_compliance_engine()

    try:
        blueprint = await engine.generate_blueprint(request)
        logger.info(
            f"Blueprint generated with {len(blueprint.selected_modules)} modules, "
            f"cost: ${blueprint.estimated_monthly_cost_usd}/mo"
        )
        return blueprint
    except Exception as e:
        logger.error(f"Blueprint generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Blueprint generation failed", "message": str(e)},
        )


@router.post(
    "/assess",
    response_model=ComplianceAssessmentResult,
    summary="Run Compliance Assessment",
    description="Assess content against selected compliance modules.",
)
async def run_assessment(
    input_data: AssessmentInput, x_api_key: str = Header(..., description="API authentication key")
) -> ComplianceAssessmentResult:
    """
    Run a comprehensive compliance assessment.

    Executes assessments against all selected modules in parallel.

    Returns:
    - Overall compliance status and score
    - Per-module assessment results
    - Critical findings and recommendations
    - ShadowTag audit hash
    """
    engine = get_compliance_engine()

    try:
        result = await engine.assess(input_data)
        logger.info(
            f"Assessment {result.assessment_id} completed: "
            f"status={result.overall_status.value}, score={result.overall_score:.2%}"
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid request", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Assessment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Assessment failed", "message": str(e)},
        )


@router.get(
    "/modules",
    response_model=ModuleListResponse,
    summary="List Available Modules",
    description="Get list of all available compliance regulation modules.",
)
async def list_modules(
    jurisdiction: str | None = Query(
        None, description="Filter by jurisdiction (us, eu, uk, apac, global)"
    ),
) -> ModuleListResponse:
    """
    List all available compliance modules.

    Optionally filter by jurisdiction.
    """
    engine = get_compliance_engine()
    await engine.initialize()

    modules = engine.get_available_modules()

    # Filter by jurisdiction if specified
    if jurisdiction:
        modules = [m for m in modules if m.jurisdiction.value == jurisdiction.lower()]

    return ModuleListResponse(modules=modules, total_count=len(modules))


@router.get(
    "/modules/{regulation_id}",
    response_model=ModuleDetailResponse,
    summary="Get Module Details",
    description="Get detailed information about a specific regulation module.",
)
async def get_module(regulation_id: str) -> ModuleDetailResponse:
    """
    Get detailed information about a specific module.

    Returns:
    - Module metadata
    - Control definitions and checklist
    - Validation rules
    - Required evidence list
    """
    engine = get_compliance_engine()
    await engine.initialize()

    try:
        reg_id = RegulationId(regulation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Module not found", "available": [r.value for r in RegulationId]},
        )

    info = engine.get_module_info(reg_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": f"Module {regulation_id} not registered"},
        )

    return ModuleDetailResponse(**info)


@router.post(
    "/validate",
    response_model=ValidationResult,
    summary="Post-Generation Validation",
    description="Validate LLM-generated content against compliance rules (GPT Store pattern).",
)
async def validate_content(
    request: ValidationRequest, x_api_key: str = Header(..., description="API authentication key")
) -> ValidationResult:
    """
    Validate generated content against compliance rules.

    Used for post-generation validation in GPT Store and similar integrations.

    Returns:
    - Compliance status (pass/fail)
    - List of violations with severity
    - Suggested remediation
    - Remediated content (if auto-fix available)
    """
    engine = get_compliance_engine()

    try:
        result = await engine.validate_response(request)
        logger.info(
            f"Validation {result.validation_id}: "
            f"compliant={result.is_compliant}, violations={len(result.violations)}"
        )
        return result
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Validation failed", "message": str(e)},
        )


@router.post(
    "/batch",
    response_model=BatchAssessmentResponse,
    summary="Batch Assessment",
    description="Run compliance assessments on multiple inputs with MCP efficiency patterns.",
)
async def batch_assessment(
    request: BatchAssessmentRequest,
    x_api_key: str = Header(..., description="API authentication key"),
) -> BatchAssessmentResponse:
    """
    Batch assessment with MCP efficiency patterns.

    Processes multiple assessments in parallel with configurable concurrency.
    Implements progressive disclosure for token efficiency.

    Returns:
    - Batch ID for tracking
    - Success/failure counts
    - All assessment results
    """
    engine = get_compliance_engine()
    batch_id = str(uuid4())

    try:
        results = await engine.assess_batch(request.inputs, max_concurrent=request.max_concurrent)

        return BatchAssessmentResponse(
            batch_id=batch_id,
            total_submitted=len(request.inputs),
            total_completed=len(results),
            total_failed=len(request.inputs) - len(results),
            results=results,
        )
    except Exception as e:
        logger.error(f"Batch assessment failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Batch assessment failed", "message": str(e)},
        )


@router.get(
    "/audit/{assessment_id}",
    response_model=AuditTrailResponse,
    summary="Get Audit Trail",
    description="Retrieve ShadowTag audit proof for an assessment.",
)
async def get_audit_trail(
    assessment_id: str, x_api_key: str = Header(..., description="API authentication key")
) -> AuditTrailResponse:
    """
    Retrieve audit trail for a completed assessment.

    Returns signed URL for accessing the full audit log.
    Requires Pro tier or higher.
    """
    # In production, this would:
    # 1. Verify API key tier
    # 2. Look up assessment in ShadowTag ledger
    # 3. Generate signed URL for audit access

    # Placeholder implementation
    return AuditTrailResponse(
        assessment_id=assessment_id,
        audit_hash=f"sha256:{assessment_id[:16]}...",
        timestamp=datetime.utcnow(),
        access_type="temporary_signed_url",
        expires_in="15 minutes",
        url=f"https://audit.activeshield.ai/v1/{assessment_id}",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check compliance engine health status.",
)
async def health_check() -> HealthResponse:
    """
    Get compliance engine health status.
    """
    engine = get_compliance_engine()
    health = engine.health_check()

    return HealthResponse(
        status=health["status"],
        initialized=health["initialized"],
        modules_registered=health["registry"]["registered_modules"],
        timestamp=datetime.utcnow(),
    )


# ============================================================================
# MODULE-SPECIFIC ENDPOINTS
# ============================================================================


@router.post(
    "/modules/{regulation_id}/assess",
    response_model=ComplianceAssessmentResult,
    summary="Module-Specific Assessment",
    description="Run assessment against a single specific module.",
)
async def assess_single_module(
    regulation_id: str,
    input_data: AssessmentInput,
    x_api_key: str = Header(..., description="API authentication key"),
) -> ComplianceAssessmentResult:
    """
    Run assessment against a single specific module.

    Useful for focused assessments or testing.
    """
    try:
        reg_id = RegulationId(regulation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Module not found"}
        )

    # Override modules in input
    input_data.modules = [reg_id]

    engine = get_compliance_engine()
    return await engine.assess(input_data)


@router.get(
    "/modules/{regulation_id}/checklist",
    summary="Get Module Checklist",
    description="Get a compliance checklist for a specific regulation.",
)
async def get_module_checklist(regulation_id: str) -> dict[str, Any]:
    """
    Get a compliance checklist template for a module.

    Useful for manual compliance reviews and documentation.
    """
    engine = get_compliance_engine()
    await engine.initialize()

    try:
        reg_id = RegulationId(regulation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Module not found"}
        )

    info = engine.get_module_info(reg_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": f"Module {regulation_id} not registered"},
        )

    return {
        "regulation": regulation_id,
        "generated_at": datetime.utcnow().isoformat(),
        "checklist": info["controls"],
    }
