"""ActiveShieldMedical API Routes
===============================

FastAPI endpoints for ActiveShieldMedical integration.

Base URL: /api/v1/activeshield

Endpoints:
- POST /scan         - Pre-hoc input validation
- POST /monitor      - Mid-hoc response check
- POST /audit        - Post-hoc session logging
- GET  /trace/{id}   - Get audit trail
- GET  /report       - Generate compliance report
- POST /sb243/check  - Direct SB 243 validation
- POST /dlp/scan     - Direct DLP scanning
- POST /clinical/evaluate - Clinical decision gateway

Pricing Tier Mapping:
- Basic ($50K/yr): /scan, /sb243/check
- Professional ($200K/yr): + /monitor, /dlp/scan
- Enterprise ($500K/yr): + /clinical/evaluate, /audit, indemnification
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.shadowtag_v4.database import get_db

from ..core.clinical_gateway import (
    ClinicalDecision,
    ClinicalDecisionGateway,
    DecisionCategory,
    EvidenceLevel,
)
from ..core.liability_shield import LiabilityShield
from ..core.medical_dlp import MedicalDLPEngine, SensitivityLevel
from ..core.sb243_compliance import SB243ComplianceEngine

router = APIRouter(prefix="/api/v1/activeshield", tags=["ActiveShieldMedical"])


# Dependency injection for components
def get_shield(db: Session = Depends(get_db)) -> LiabilityShield:
    return LiabilityShield(db=db)


def get_sb243(db: Session = Depends(get_db)) -> SB243ComplianceEngine:
    return SB243ComplianceEngine(db=db)


def get_dlp(db: Session = Depends(get_db)) -> MedicalDLPEngine:
    return MedicalDLPEngine(db=db)


def get_gateway(db: Session = Depends(get_db)) -> ClinicalDecisionGateway:
    return ClinicalDecisionGateway(db=db)


# =============================================================================
# Request/Response Models
# =============================================================================


class ScanRequest(BaseModel):
    """Pre-hoc scan request"""

    session_id: str = Field(..., description="Unique session identifier")
    user_input: str = Field(..., description="User input to validate")
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Session context (ai_disclosure_shown, user_age, etc.)",
    )


class MonitorRequest(BaseModel):
    """Mid-hoc monitor request"""

    session_id: str
    ai_response: str = Field(..., description="AI response to validate")
    decision_category: str = Field(
        default="informational",
        description="Category: informational, triage, diagnostic, therapeutic, medication, emergency, behavioral",
    )
    evidence_level: str = Field(default="E5", description="Evidence level: E1-E5")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    patient_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Patient info (current_medications, allergies, conditions)",
    )
    session_context: dict[str, Any] = Field(default_factory=dict)


class AuditRequest(BaseModel):
    """Post-hoc audit request"""

    session_id: str
    conversation_summary: str
    outcome: str = Field(default="completed")
    metadata: dict[str, Any] = Field(default_factory=dict)


class SB243CheckRequest(BaseModel):
    """Direct SB 243 check request"""

    session_id: str
    content: str
    context: dict[str, Any] = Field(default_factory=dict)
    is_ai_response: bool = Field(default=False)


class DLPScanRequest(BaseModel):
    """Direct DLP scan request"""

    text: str
    redact: bool = Field(default=True)
    sensitivity_threshold: str = Field(
        default="confidential",
        description="Minimum sensitivity to redact: public, internal, confidential, restricted, highly_restricted",
    )


class ClinicalEvaluateRequest(BaseModel):
    """Clinical decision evaluation request"""

    decision_id: str
    category: str = Field(default="informational")
    content: str
    evidence_level: str = Field(default="E5")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    patient_context: dict[str, Any] = Field(default_factory=dict)


class CertificateRequest(BaseModel):
    """Compliance certificate request"""

    session_id: str
    customer_name: str = Field(default="Client")


# =============================================================================
# Main Shield Endpoints
# =============================================================================


@router.post("/scan", response_model=dict[str, Any])
async def pre_hoc_scan(
    request: ScanRequest,
    shield: LiabilityShield = Depends(get_shield),
):
    """PRE-HOC: Validate user input before AI processing.

    Detects:
    - Crisis/self-harm indicators (triggers emergency protocol)
    - Minor users without consent
    - PHI requiring protection
    - Missing AI disclosure

    Returns action: allow, allow_with_warnings, block, or emergency
    """
    result = await shield.pre_check(
        session_id=request.session_id,
        user_input=request.user_input,
        context=request.context,
    )

    return {
        "shield_id": result.shield_id,
        "action": result.action.value,
        "passed": result.passed,
        "violations": result.violations,
        "warnings": result.warnings,
        "required_actions": result.required_actions,
        "crisis_intervention": result.crisis_intervention,
        "processing_time_ms": result.processing_time_ms,
    }


@router.post("/monitor", response_model=dict[str, Any])
async def mid_hoc_monitor(
    request: MonitorRequest,
    shield: LiabilityShield = Depends(get_shield),
):
    """MID-HOC: Validate AI response before sending to user.

    Checks:
    - Clinical decision appropriateness
    - Drug interactions / contraindications
    - AI persona deception (claiming to be human doctor)
    - PHI in response (redacts if needed)
    - Evidence level for recommendations

    Returns processed_content (potentially redacted) and action taken.
    """
    # Map string to enum
    category = DecisionCategory(request.decision_category)
    evidence = EvidenceLevel(request.evidence_level)

    result = await shield.mid_check(
        session_id=request.session_id,
        ai_response=request.ai_response,
        decision_category=category,
        evidence_level=evidence,
        confidence=request.confidence,
        patient_context=request.patient_context,
        session_context=request.session_context,
    )

    return {
        "shield_id": result.shield_id,
        "action": result.action.value,
        "passed": result.passed,
        "processed_content": result.processed_content,
        "violations": result.violations,
        "warnings": result.warnings,
        "required_actions": result.required_actions,
        "human_review_required": result.gateway_result.human_review_required
        if result.gateway_result
        else False,
        "processing_time_ms": result.processing_time_ms,
    }


@router.post("/audit", response_model=dict[str, Any])
async def post_hoc_audit(
    request: AuditRequest,
    shield: LiabilityShield = Depends(get_shield),
):
    """POST-HOC: Log session for compliance audit.

    Creates immutable audit record for:
    - Litigation defense
    - Regulatory compliance
    - Insurance claims
    """
    result = await shield.post_log(
        session_id=request.session_id,
        conversation_summary=request.conversation_summary,
        outcome=request.outcome,
        metadata=request.metadata,
    )

    return {
        "shield_id": result.shield_id,
        "logged": True,
        "warnings": result.warnings,
        "audit_trail": result.audit_trail,
    }


@router.get("/trace/{session_id}", response_model=dict[str, Any])
async def get_audit_trace(
    session_id: str,
    shield: LiabilityShield = Depends(get_shield),
):
    """Get complete audit trail for a session.

    Returns all shield events (pre-hoc, mid-hoc, post-hoc) for the session.
    """
    results = shield.get_session_audit(session_id)

    if not results:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "total_events": len(results),
        "events": [
            {
                "shield_id": r.shield_id,
                "phase": r.phase.value,
                "action": r.action.value,
                "passed": r.passed,
                "violations_count": len(r.violations),
                "warnings_count": len(r.warnings),
                "checked_at": r.checked_at.isoformat(),
            }
            for r in results
        ],
    }


@router.post("/certificate", response_model=dict[str, Any])
async def generate_certificate(
    request: CertificateRequest,
    shield: LiabilityShield = Depends(get_shield),
):
    """Generate compliance certificate for a session.

    This is the deliverable that proves due diligence for:
    - Insurance claims
    - Litigation defense
    - Regulatory audit
    """
    certificate = shield.generate_compliance_certificate(
        session_id=request.session_id,
        customer_name=request.customer_name,
    )

    if "error" in certificate:
        raise HTTPException(status_code=404, detail=certificate["error"])

    return certificate


@router.get("/report", response_model=dict[str, Any])
async def get_liability_report(
    since_days: int = Query(default=30, description="Report period in days"),
    shield: LiabilityShield = Depends(get_shield),
):
    """Generate liability exposure report.

    Summarizes:
    - Total protection events
    - Action distribution (allow, block, escalate)
    - Crisis interventions
    - Protection effectiveness
    """
    from datetime import timedelta

    since = datetime.utcnow() - timedelta(days=since_days)
    report = shield.generate_liability_report(since=since)
    return report


# =============================================================================
# Direct Component Endpoints
# =============================================================================


@router.post("/sb243/check", response_model=dict[str, Any])
async def sb243_check(
    request: SB243CheckRequest,
    engine: SB243ComplianceEngine = Depends(get_sb243),
):
    """Direct SB 243 compliance check.

    Use for:
    - Standalone transparency compliance
    - Crisis detection
    - Minor protection verification
    """
    result = await engine.check(
        session_id=request.session_id,
        content=request.content,
        context=request.context,
        is_ai_response=request.is_ai_response,
    )

    return {
        "passed": result.passed,
        "user_type": result.user_type,
        "ai_disclosure_present": result.ai_disclosure_present,
        "crisis_level": result.crisis_level.value,
        "escalation_required": result.escalation_required,
        "violations": [
            {
                "type": v.violation_type.value,
                "severity": v.severity.value,
                "description": v.description,
                "legal_reference": v.legal_reference,
                "remediation": v.remediation,
            }
            for v in result.violations
        ],
        "warnings": result.warnings,
        "audit_trail_id": result.audit_trail_id,
    }


@router.get("/sb243/disclosure", response_model=dict[str, Any])
async def get_ai_disclosure(
    platform_name: str = Query(default="this platform"),
    engine: SB243ComplianceEngine = Depends(get_sb243),
):
    """Get compliant AI disclosure statement.

    Display this to users before AI interaction begins.
    """
    disclosure = engine.generate_ai_disclosure(platform_name)
    return {
        "disclosure": disclosure,
        "framework": "SB_243",
        "required": True,
    }


@router.post("/dlp/scan", response_model=dict[str, Any])
async def dlp_scan(
    request: DLPScanRequest,
    engine: MedicalDLPEngine = Depends(get_dlp),
):
    """Scan text for PHI and clinical data.

    Returns detected PHI with optional redaction.
    """
    threshold = SensitivityLevel(request.sensitivity_threshold)

    result = await engine.scan(
        text=request.text,
        redact=request.redact,
        sensitivity_threshold=threshold,
    )

    return {
        "redacted_text": result.redacted_text,
        "phi_count": result.total_phi_count,
        "clinical_count": result.total_clinical_count,
        "highest_sensitivity": result.highest_sensitivity.value,
        "redaction_applied": result.redaction_applied,
        "phi_detected": [
            {
                "type": p.phi_type.value,
                "sensitivity": p.sensitivity.value,
                "redacted_to": p.redacted_value,
            }
            for p in result.phi_detected
        ],
        "audit_id": result.audit_id,
    }


@router.post("/clinical/evaluate", response_model=dict[str, Any])
async def clinical_evaluate(
    request: ClinicalEvaluateRequest,
    gateway: ClinicalDecisionGateway = Depends(get_gateway),
):
    """Evaluate a clinical decision through the gateway.

    Checks:
    - Risk level appropriateness
    - Drug interactions
    - Contraindications
    - Evidence level
    """
    category = DecisionCategory(request.category)
    evidence = EvidenceLevel(request.evidence_level)

    decision = ClinicalDecision(
        decision_id=request.decision_id,
        category=category,
        content=request.content,
        evidence_level=evidence,
        confidence_score=request.confidence,
    )

    result = await gateway.evaluate(
        decision=decision,
        patient_context=request.patient_context,
    )

    return {
        "approved": result.approved,
        "human_review_required": result.human_review_required,
        "escalation_reasons": [r.value for r in result.escalation_reasons],
        "warnings": result.warnings,
        "required_actions": result.required_actions,
        "safe_response_template": gateway.get_safe_response_template(category),
        "audit_trail_id": result.audit_trail_id,
    }


@router.get("/health", response_model=dict[str, Any])
async def health_check():
    """Health check endpoint.

    Returns system status and version.
    """
    return {
        "status": "healthy",
        "service": "ActiveShieldMedical",
        "version": "1.0.0",
        "frameworks": ["SB_243", "HIPAA", "CCPA"],
        "tiers": {
            "pre_hoc": "active",
            "mid_hoc": "active",
            "post_hoc": "active",
        },
        "checked_at": datetime.utcnow().isoformat(),
    }
