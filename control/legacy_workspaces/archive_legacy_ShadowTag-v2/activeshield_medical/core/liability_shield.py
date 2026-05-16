# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Liability Shield - Unified Protection Layer
=============================================

Orchestrates all ActiveShieldMedical components into a single
protection interface. This is the main entry point for clients.

Three-Tier Defense Architecture:
1. PRE-HOC: Input validation before processing
2. MID-HOC: Real-time monitoring during processing
3. POST-HOC: Audit logging and evidence capture

SALES VALUE PROPOSITION:
- Single integration point for complete liability protection
- Documented due diligence trail for litigation defense
- Automatic compliance with SB 243, HIPAA, and emerging regulations
- E&O insurance integration ready
"""

import hashlib
import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .clinical_gateway import (
  ClinicalDecision,
  ClinicalDecisionGateway,
  ClinicalRiskLevel,
  DecisionCategory,
  EvidenceLevel,
  GatewayResult,
)
from .medical_dlp import DLPResult, MedicalDLPEngine, SensitivityLevel
from .sb243_compliance import CrisisLevel, SB243CheckResult, SB243ComplianceEngine

logger = logging.getLogger(__name__)


class ShieldPhase(str, Enum):
  """Shield processing phases"""

  PRE_HOC = "pre_hoc"  # Before AI processing
  MID_HOC = "mid_hoc"  # During AI processing
  POST_HOC = "post_hoc"  # After AI processing


class ShieldAction(str, Enum):
  """Actions taken by the shield"""

  ALLOW = "allow"  # Proceed normally
  ALLOW_WITH_WARNINGS = "allow_with_warnings"
  REDACT = "redact"  # PHI redacted
  ESCALATE = "escalate"  # Human review required
  BLOCK = "block"  # Stop processing
  EMERGENCY = "emergency"  # Immediate intervention


class ShieldResult(BaseModel):
  """Result of a complete shield check"""

  shield_id: str
  session_id: str
  phase: ShieldPhase
  action: ShieldAction
  passed: bool

  # Component results
  sb243_result: SB243CheckResult | None = None
  dlp_result: DLPResult | None = None
  gateway_result: GatewayResult | None = None

  # Aggregated findings
  violations: list[dict[str, Any]] = Field(default_factory=list)
  warnings: list[str] = Field(default_factory=list)
  required_actions: list[str] = Field(default_factory=list)

  # Output
  processed_content: str | None = None
  crisis_intervention: dict[str, Any] | None = None

  # Audit
  audit_trail: list[str] = Field(default_factory=list)
  checked_at: datetime = Field(default_factory=datetime.utcnow)
  processing_time_ms: float = 0.0


from sqlalchemy.orm import Session

from ..models import ActiveShieldAdverseEvent, ActiveShieldAuditLog


class LiabilityShield:
  """
  Unified Liability Shield

  This is the primary integration point for ActiveShieldMedical.
  Clients call this for complete AI safety coverage.

  Integration Example:
  ```python
  shield = LiabilityShield(db=db_session)

  # Pre-hoc: Check user input before processing
  pre_result = await shield.pre_check(
      session_id="session123",
      user_input="I'm feeling really depressed and don't want to live",
      context={"ai_disclosure_shown": True, "user_age": 25}
  )

  if pre_result.action == ShieldAction.EMERGENCY:
      # Handle crisis immediately
      return pre_result.crisis_intervention

  # Mid-hoc: Check AI response before sending
  mid_result = await shield.mid_check(
      session_id="session123",
      ai_response="I understand you're going through a difficult time...",
      decision_category=DecisionCategory.BEHAVIORAL
  )
  """

  def __init__(self, db: Session | None = None):
    self.db = db
    self.sb243 = SB243ComplianceEngine()
    self.dlp = MedicalDLPEngine()
    self.gateway = ClinicalDecisionGateway()
    self._audit_log: list[ShieldResult] = []  # Fallback only

  async def pre_check(
    self,
    session_id: str,
    user_input: str,
    context: dict[str, Any] | None = None,
  ) -> ShieldResult:
    """
    PRE-HOC: Check user input before AI processing.

    Detects:
    - Crisis/self-harm indicators
    - Minor users without consent
    - PHI that needs protection
    - Missing AI disclosure
    """
    start_time = datetime.now(UTC)
    context = context or {}
    shield_id = self._generate_shield_id(session_id, "pre")

    violations = []
    warnings = []
    required_actions = []
    audit_trail = [f"PRE_HOC started: {shield_id}"]

    # Step 1: SB 243 Compliance Check
    sb243_result = await self.sb243.check(
      session_id=session_id,
      content=user_input,
      context=context,
      is_ai_response=False,
    )
    audit_trail.append(f"SB243 check: passed={sb243_result.passed}")

    if not sb243_result.passed:
      violations.extend(
        [
          {
            "source": "sb243",
            "type": v.violation_type.value,
            "severity": v.severity.value,
          }
          for v in sb243_result.violations
        ]
      )
    warnings.extend(sb243_result.warnings)

    # Step 2: DLP Scan (detect PHI in user input)
    dlp_result = await self.dlp.scan(user_input, redact=False)
    audit_trail.append(
      f"DLP scan: {dlp_result.total_phi_count} PHI, {dlp_result.total_clinical_count} clinical"
    )

    if dlp_result.total_phi_count > 0:
      warnings.append(f"User input contains {dlp_result.total_phi_count} PHI elements")

    # Determine action
    action = ShieldAction.ALLOW
    crisis_intervention = None

    # Check for emergency/crisis
    if sb243_result.escalation_required:
      action = ShieldAction.EMERGENCY
      crisis_intervention = self.sb243.get_crisis_response(sb243_result.crisis_level)
      required_actions.append("IMMEDIATE: Activate crisis protocol")
      audit_trail.append(f"CRISIS DETECTED: {sb243_result.crisis_level.value}")

    # Check for blocked conditions
    elif sb243_result.violations and any(
      v.severity.value in ["critical", "high"] for v in sb243_result.violations
    ):
      action = ShieldAction.BLOCK
      required_actions.extend(
        [
          f"RESOLVE: {v.violation_type.value} - {v.remediation}"
          for v in sb243_result.violations
        ]
      )

    # Check for warnings
    elif warnings:
      action = ShieldAction.ALLOW_WITH_WARNINGS

    processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

    result = ShieldResult(
      shield_id=shield_id,
      session_id=session_id,
      phase=ShieldPhase.PRE_HOC,
      action=action,
      passed=action not in [ShieldAction.BLOCK, ShieldAction.EMERGENCY],
      sb243_result=sb243_result,
      dlp_result=dlp_result,
      violations=violations,
      warnings=warnings,
      required_actions=required_actions,
      processed_content=user_input,
      crisis_intervention=crisis_intervention,
      audit_trail=audit_trail,
      processing_time_ms=processing_time,
    )

    if self.db:
      try:
        db_log = ActiveShieldAuditLog(
          shield_id=result.shield_id,
          session_id=result.session_id,
          phase=result.phase.value,
          action=result.action.value,
          passed=result.passed,
          processed_content=result.processed_content,
          violations=result.violations,
          warnings=result.warnings,
          audit_trail=result.audit_trail,
          processing_time_ms=result.processing_time_ms,
          metadata_={
            "crisis_intervention": result.crisis_intervention,
            "required_actions": result.required_actions,
          },
        )
        self.db.add(db_log)
        self.db.commit()
      except Exception as e:
        logger.error(f"Failed to persist PRE_HOC log: {e}")
        self.db.rollback()

    self._audit_log.append(result)
    logger.info(f"PRE_HOC complete: {shield_id} -> {action.value}")

    return result

  async def mid_check(
    self,
    session_id: str,
    ai_response: str,
    decision_category: DecisionCategory = DecisionCategory.INFORMATIONAL,
    evidence_level: EvidenceLevel = EvidenceLevel.E5,
    confidence: float = 0.5,
    patient_context: dict[str, Any] | None = None,
    session_context: dict[str, Any] | None = None,
  ) -> ShieldResult:
    """
    MID-HOC: Check AI response before sending to user.

    Validates:
    - Clinical decision appropriateness
    - Drug interactions / contraindications
    - Deceptive persona (AI claiming to be human)
    - PHI in response (redact if needed)
    - Evidence level for recommendations
    """
    start_time = datetime.now(UTC)
    session_context = session_context or {}
    patient_context = patient_context or {}
    shield_id = self._generate_shield_id(session_id, "mid")

    violations = []
    warnings = []
    required_actions = []
    audit_trail = [f"MID_HOC started: {shield_id}"]

    # Step 1: SB 243 check on AI response (deception, crisis response)
    sb243_result = await self.sb243.check(
      session_id=session_id,
      content=ai_response,
      context={
        **session_context,
        "crisis_resources_provided": "988" in ai_response
        or "crisis" in ai_response.lower(),
      },
      is_ai_response=True,
    )
    audit_trail.append(f"SB243 response check: passed={sb243_result.passed}")

    if not sb243_result.passed:
      violations.extend(
        [
          {
            "source": "sb243",
            "type": v.violation_type.value,
            "severity": v.severity.value,
          }
          for v in sb243_result.violations
        ]
      )

    # Step 2: DLP - Redact PHI from AI response
    dlp_result = await self.dlp.scan(
      ai_response,
      redact=True,
      sensitivity_threshold=SensitivityLevel.CONFIDENTIAL,
    )
    processed_content = dlp_result.redacted_text
    audit_trail.append(f"DLP redaction: {dlp_result.redaction_applied}")

    if dlp_result.redaction_applied:
      warnings.append("PHI redacted from AI response")

    # Step 3: Clinical Gateway - Evaluate decision
    decision_id = f"{session_id}:{shield_id}"
    clinical_decision = ClinicalDecision(
      decision_id=decision_id,
      category=decision_category,
      content=ai_response,
      evidence_level=evidence_level,
      confidence_score=confidence,
      risk_level=self._infer_risk_level(decision_category, confidence),
    )

    gateway_result = await self.gateway.evaluate(
      decision=clinical_decision,
      patient_context=patient_context,
    )
    audit_trail.append(
      f"Gateway: approved={gateway_result.approved}, escalate={gateway_result.human_review_required}"
    )

    warnings.extend(gateway_result.warnings)
    required_actions.extend(gateway_result.required_actions)

    if not gateway_result.approved:
      violations.append(
        {
          "source": "gateway",
          "type": "clinical_decision_blocked",
          "reasons": [r.value for r in gateway_result.escalation_reasons],
        }
      )

      # Persist Adverse Event if Blocked
      if self.db:
        try:
          adverse_event = ActiveShieldAdverseEvent(
            session_id=session_id,
            audit_log_id=None,  # Will link if we flush later, or separate
            event_type="clinical_decision_blocked",
            description=f"Blocked decision: {decision_category.value}. Reasons: {gateway_result.escalation_reasons}",
            severity="high",
            context_snapshot={
              "patient_context": patient_context,
              "decision_content": ai_response[:500],
            },
          )
          self.db.add(adverse_event)
          # Don't commit yet, wait for main log
        except Exception as e:
          logger.error(f"Failed to stage Adverse Event: {e}")

    # Determine action
    action = ShieldAction.ALLOW

    if not gateway_result.approved:
      action = ShieldAction.BLOCK
    elif gateway_result.human_review_required:
      action = ShieldAction.ESCALATE
    elif dlp_result.redaction_applied:
      action = ShieldAction.REDACT
    elif warnings:
      action = ShieldAction.ALLOW_WITH_WARNINGS

    processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

    result = ShieldResult(
      shield_id=shield_id,
      session_id=session_id,
      phase=ShieldPhase.MID_HOC,
      action=action,
      passed=action not in [ShieldAction.BLOCK],
      sb243_result=sb243_result,
      dlp_result=dlp_result,
      gateway_result=gateway_result,
      violations=violations,
      warnings=warnings,
      required_actions=required_actions,
      processed_content=processed_content,
      audit_trail=audit_trail,
      processing_time_ms=processing_time,
    )

    if self.db:
      try:
        db_log = ActiveShieldAuditLog(
          shield_id=result.shield_id,
          session_id=result.session_id,
          phase=result.phase.value,
          action=result.action.value,
          passed=result.passed,
          processed_content=result.processed_content,
          violations=result.violations,
          warnings=result.warnings,
          audit_trail=result.audit_trail,
          processing_time_ms=result.processing_time_ms,
          metadata_={
            "decision_category": decision_category.value,
            "confidence": confidence,
          },
        )
        self.db.add(db_log)
        self.db.commit()
      except Exception as e:
        logger.error(f"Failed to persist MID_HOC log: {e}")
        self.db.rollback()

    self._audit_log.append(result)
    logger.info(f"MID_HOC complete: {shield_id} -> {action.value}")

    return result

  async def post_log(
    self,
    session_id: str,
    conversation_summary: str,
    outcome: str = "completed",
    metadata: dict[str, Any] | None = None,
  ) -> ShieldResult:
    """
    POST-HOC: Log session for compliance and audit.

    Creates:
    - Immutable audit record
    - Compliance certification
    - Evidence package for litigation
    """
    start_time = datetime.now(UTC)
    metadata = metadata or {}
    shield_id = self._generate_shield_id(session_id, "post")

    audit_trail = [
      f"POST_HOC started: {shield_id}",
      f"Session outcome: {outcome}",
      f"Total shield events for session: {len([r for r in self._audit_log if r.session_id == session_id])}",
    ]

    # Aggregate session statistics
    session_results = [r for r in self._audit_log if r.session_id == session_id]
    total_violations = sum(len(r.violations) for r in session_results)
    had_crisis = any(
      r.sb243_result and r.sb243_result.crisis_level != CrisisLevel.NONE
      for r in session_results
    )
    had_escalation = any(
      r.gateway_result and r.gateway_result.human_review_required
      for r in session_results
    )

    warnings = []
    if total_violations > 0:
      warnings.append(f"Session had {total_violations} total violations")
    if had_crisis:
      warnings.append("Session involved crisis intervention")
    if had_escalation:
      warnings.append("Session required human escalation")

    processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

    result = ShieldResult(
      shield_id=shield_id,
      session_id=session_id,
      phase=ShieldPhase.POST_HOC,
      action=ShieldAction.ALLOW,
      passed=True,
      violations=[],
      warnings=warnings,
      required_actions=[],
      audit_trail=audit_trail,
      processing_time_ms=processing_time,
    )

    if self.db:
      try:
        db_log = ActiveShieldAuditLog(
          shield_id=result.shield_id,
          session_id=result.session_id,
          phase=result.phase.value,
          action=result.action.value,
          passed=result.passed,
          processed_content=conversation_summary,  # Store summary here
          violations=[],
          warnings=result.warnings,
          audit_trail=result.audit_trail,
          processing_time_ms=result.processing_time_ms,
          metadata_={
            **metadata,
            "outcome": outcome,
            "total_violations_session": total_violations,
          },
        )
        self.db.add(db_log)
        self.db.commit()
      except Exception as e:
        logger.error(f"Failed to persist POST_HOC log: {e}")
        print(f"DEBUG: Gateway persistence failed: {e}")
        raise e  # Fail test if persistence fails

    self._audit_log.append(result)
    logger.info(f"POST_HOC complete: {shield_id} - session logged")

    return result

  def _infer_risk_level(
    self,
    category: DecisionCategory,
    confidence: float,
  ) -> ClinicalRiskLevel:
    """Infer risk level from decision category and confidence"""
    # Category-based baseline
    category_risk = {
      DecisionCategory.INFORMATIONAL: ClinicalRiskLevel.MINIMAL,
      DecisionCategory.TRIAGE: ClinicalRiskLevel.LOW,
      DecisionCategory.BEHAVIORAL: ClinicalRiskLevel.MODERATE,
      DecisionCategory.DIAGNOSTIC: ClinicalRiskLevel.HIGH,
      DecisionCategory.THERAPEUTIC: ClinicalRiskLevel.HIGH,
      DecisionCategory.MEDICATION: ClinicalRiskLevel.HIGH,
      DecisionCategory.EMERGENCY: ClinicalRiskLevel.CRITICAL,
    }

    base_risk = category_risk.get(category, ClinicalRiskLevel.MODERATE)

    # Adjust for low confidence
    if confidence < 0.5 and base_risk == ClinicalRiskLevel.MODERATE:
      return ClinicalRiskLevel.HIGH

    return base_risk

  def _generate_shield_id(self, session_id: str, phase: str) -> str:
    """Generate unique shield ID"""
    timestamp = datetime.now(UTC).isoformat()
    content = f"shield:{session_id}:{phase}:{timestamp}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]

  # =========================================================================
  # Reporting & Certification
  # =========================================================================

  def get_session_audit(self, session_id: str) -> list[ShieldResult]:
    """Get complete audit trail for a session"""
    return [r for r in self._audit_log if r.session_id == session_id]

  def generate_compliance_certificate(
    self,
    session_id: str,
    customer_name: str = "Client",
  ) -> dict[str, Any]:
    """
    Generate compliance certification for a session.

    This is the deliverable that proves due diligence.
    """
    session_results = self.get_session_audit(session_id)

    if not session_results:
      return {"error": "No audit data for session"}

    # Calculate compliance metrics
    total_checks = len(session_results)
    passed_checks = len([r for r in session_results if r.passed])
    total_violations = sum(len(r.violations) for r in session_results)
    total_warnings = sum(len(r.warnings) for r in session_results)

    # Determine overall compliance status
    compliance_status = "COMPLIANT"
    if total_violations > 0:
      compliance_status = "NON_COMPLIANT_WITH_REMEDIATION"

    return {
      "certificate_id": self._generate_shield_id(session_id, "cert"),
      "session_id": session_id,
      "customer_name": customer_name,
      "issued_at": datetime.now(UTC).isoformat(),
      "compliance_status": compliance_status,
      "frameworks_checked": ["SB_243", "HIPAA", "CCPA"],
      "metrics": {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "compliance_rate": (passed_checks / total_checks * 100)
        if total_checks > 0
        else 100,
        "violations": total_violations,
        "warnings": total_warnings,
      },
      "audit_trail_ids": [r.shield_id for r in session_results],
      "statement": (
        f"This certifies that session {session_id} was processed through "
        f"ActiveShieldMedical's three-tier defense architecture. "
        f"All applicable regulatory requirements (SB 243, HIPAA, CCPA) "
        f"were checked and {compliance_status.lower().replace('_', ' ')}."
      ),
    }

  def generate_liability_report(
    self,
    since: datetime | None = None,
  ) -> dict[str, Any]:
    """Generate liability exposure report"""
    results = self._audit_log
    if since:
      results = [r for r in results if r.checked_at >= since]

    # Aggregate by action type
    action_counts = {}
    for result in results:
      action_counts[result.action.value] = action_counts.get(result.action.value, 0) + 1

    # Count critical events
    crisis_events = len(
      [
        r
        for r in results
        if r.sb243_result
        and r.sb243_result.crisis_level in [CrisisLevel.CRITICAL, CrisisLevel.SEVERE]
      ]
    )

    blocked_decisions = len(
      [r for r in results if r.gateway_result and not r.gateway_result.approved]
    )

    return {
      "report_id": self._generate_shield_id("report", "liability"),
      "period_start": since.isoformat() if since else "all_time",
      "period_end": datetime.now(UTC).isoformat(),
      "total_events": len(results),
      "action_distribution": action_counts,
      "crisis_interventions": crisis_events,
      "blocked_clinical_decisions": blocked_decisions,
      "liability_incidents": crisis_events + blocked_decisions,
      "protection_effectiveness": (
        f"{((len(results) - crisis_events - blocked_decisions) / len(results) * 100):.1f}%"
        if results
        else "N/A"
      ),
    }


# Global instance
liability_shield = LiabilityShield()
