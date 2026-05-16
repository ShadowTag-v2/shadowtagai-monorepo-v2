# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Base Compliance Module Class

Abstract base class for all regulation compliance modules.
Each module follows single responsibility principle:
- Defines regulation metadata
- Implements validation rules
- Generates assessment results
- Produces audit-ready documentation
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from app.models.compliance import (
  AssessmentInput,
  ComplianceStatus,
  ControlDefinition,
  ControlResult,
  ModuleMetadata,
  ModuleResult,
  RegulationId,
  RiskTier,
  ValidationRule,
  ValidationViolation,
)

logger = logging.getLogger(__name__)


class ComplianceModule(ABC):
  """
  Abstract base class for compliance regulation modules.

  Each module represents a single regulation (EU AI Act, GDPR, etc.)
  and provides:
  - Regulation metadata and version info
  - Control definitions and validation rules
  - Assessment logic
  - Report generation capabilities
  - Evidence collection templates
  """

  def __init__(self):
    """Initialize the module with its metadata."""
    self._metadata = self._define_metadata()
    self._controls = self._define_controls()
    self._validation_rules = self._define_validation_rules()
    logger.info(f"Initialized compliance module: {self._metadata.id.value}")

  # =========================================================================
  # ABSTRACT METHODS - Must be implemented by each regulation module
  # =========================================================================

  @abstractmethod
  def _define_metadata(self) -> ModuleMetadata:
    """
    Define the module's metadata.

    Returns:
        ModuleMetadata containing regulation info, jurisdiction, etc.
    """
    pass

  @abstractmethod
  def _define_controls(self) -> list[ControlDefinition]:
    """
    Define the compliance controls/requirements for this regulation.

    Returns:
        List of control definitions with validation rules
    """
    pass

  @abstractmethod
  def _define_validation_rules(self) -> list[ValidationRule]:
    """
    Define validation rules for post-generation content checking.

    Returns:
        List of validation rules for content validation
    """
    pass

  @abstractmethod
  async def assess_control(
    self, control: ControlDefinition, input_data: AssessmentInput
  ) -> ControlResult:
    """
    Assess a single control against the input data.

    Args:
        control: The control definition to assess
        input_data: Assessment input containing content and metadata

    Returns:
        ControlResult with compliance status and findings
    """
    pass

  @abstractmethod
  def determine_risk_tier(self, input_data: AssessmentInput) -> RiskTier | None:
    """
    Determine the risk tier for the input (if applicable to this regulation).

    Args:
        input_data: Assessment input

    Returns:
        RiskTier classification or None if not applicable
    """
    pass

  # =========================================================================
  # PUBLIC PROPERTIES
  # =========================================================================

  @property
  def metadata(self) -> ModuleMetadata:
    """Get module metadata."""
    return self._metadata

  @property
  def module_id(self) -> RegulationId:
    """Get the module's regulation ID."""
    return self._metadata.id

  @property
  def controls(self) -> list[ControlDefinition]:
    """Get the list of control definitions."""
    return self._controls

  @property
  def validation_rules(self) -> list[ValidationRule]:
    """Get the list of validation rules for content checking."""
    return self._validation_rules

  # =========================================================================
  # ASSESSMENT METHODS
  # =========================================================================

  async def assess(self, input_data: AssessmentInput) -> ModuleResult:
    """
    Run full assessment against all controls in this module.

    Args:
        input_data: Assessment input containing content and metadata

    Returns:
        ModuleResult with all control assessments and recommendations
    """
    logger.info(f"Running {self.module_id.value} assessment")

    control_results = []
    for control in self._controls:
      try:
        result = await self.assess_control(control, input_data)
        control_results.append(result)
      except Exception as e:
        logger.error(f"Error assessing control {control.control_id}: {e}")
        control_results.append(
          ControlResult(
            control_id=control.control_id,
            control_name=control.name,
            module_id=self.module_id,
            status=ComplianceStatus.PENDING_REVIEW,
            score=0.0,
            findings=[f"Assessment error: {str(e)}"],
            remediation="Manual review required",
          )
        )

    # Calculate aggregate stats
    compliant = sum(
      1 for r in control_results if r.status == ComplianceStatus.COMPLIANT
    )
    non_compliant = sum(
      1 for r in control_results if r.status == ComplianceStatus.NON_COMPLIANT
    )
    partial = sum(1 for r in control_results if r.status == ComplianceStatus.PARTIAL)

    total_assessed = len(control_results)
    avg_score = (
      sum(r.score for r in control_results) / total_assessed
      if total_assessed > 0
      else 0.0
    )

    # Determine overall status
    if non_compliant > 0:
      overall_status = ComplianceStatus.NON_COMPLIANT
    elif partial > 0:
      overall_status = ComplianceStatus.PARTIAL
    elif compliant == total_assessed:
      overall_status = ComplianceStatus.COMPLIANT
    else:
      overall_status = ComplianceStatus.PENDING_REVIEW

    # Generate recommendations
    recommendations = await self._generate_recommendations(control_results, input_data)

    # Determine if human review is required
    requires_human_review = self._requires_human_review(control_results, input_data)

    # Get risk tier
    risk_tier = self.determine_risk_tier(input_data)

    return ModuleResult(
      module_id=self.module_id,
      module_name=self._metadata.name,
      status=overall_status,
      compliance_score=avg_score,
      controls_assessed=total_assessed,
      controls_compliant=compliant,
      controls_non_compliant=non_compliant,
      controls_partial=partial,
      control_results=control_results,
      risk_tier=risk_tier,
      recommendations=recommendations,
      requires_human_review=requires_human_review,
    )

  async def validate_content(
    self, content: str, context: str | None = None
  ) -> list[ValidationViolation]:
    """
    Validate generated content against this module's rules.

    Used for post-generation validation (GPT Store pattern).

    Args:
        content: The generated content to validate
        context: Optional context about the original prompt

    Returns:
        List of violations found in the content
    """
    violations = []

    for rule in self._validation_rules:
      if not rule.auto_check:
        continue

      violation = await self._check_validation_rule(rule, content, context)
      if violation:
        violations.append(violation)

    return violations

  # =========================================================================
  # DOCUMENTATION GENERATION
  # =========================================================================

  def generate_checklist(self) -> list[dict[str, Any]]:
    """
    Generate a compliance checklist for this regulation.

    Returns:
        List of checklist items with control info and status placeholders
    """
    checklist = []
    for control in self._controls:
      checklist.append(
        {
          "control_id": control.control_id,
          "control_name": control.name,
          "description": control.description,
          "article_ref": control.article_ref,
          "required_evidence": control.required_evidence,
          "status": "pending",
          "evidence_provided": False,
          "notes": "",
        }
      )
    return checklist

  def generate_report_template(self) -> dict[str, Any]:
    """
    Generate an audit report template for this regulation.

    Returns:
        Report template structure with placeholders
    """
    return {
      "report_type": f"{self._metadata.short_name} Compliance Report",
      "regulation": self._metadata.name,
      "version": self._metadata.version,
      "jurisdiction": self._metadata.jurisdiction.value,
      "generated_at": datetime.utcnow().isoformat(),
      "sections": [
        {"title": "Executive Summary", "content": ""},
        {"title": "Scope and Methodology", "content": ""},
        {
          "title": "Control Assessment Results",
          "controls": self.generate_checklist(),
        },
        {"title": "Findings and Recommendations", "content": ""},
        {"title": "Evidence Summary", "artifacts": []},
        {
          "title": "Attestation",
          "signatory": "",
          "date": "",
          "signature_hash": "",
        },
      ],
    }

  def get_required_evidence(self) -> list[dict[str, Any]]:
    """
    Get list of all required evidence artifacts for compliance.

    Returns:
        List of evidence requirements with descriptions
    """
    evidence_list = []
    for control in self._controls:
      for evidence_item in control.required_evidence:
        evidence_list.append(
          {
            "control_id": control.control_id,
            "evidence_type": evidence_item,
            "description": f"Evidence for {control.name}",
          }
        )
    return evidence_list

  # =========================================================================
  # HELPER METHODS
  # =========================================================================

  async def _generate_recommendations(
    self, control_results: list[ControlResult], input_data: AssessmentInput
  ) -> list[str]:
    """Generate recommendations based on assessment results."""
    recommendations = []

    # Add recommendations for non-compliant controls
    for result in control_results:
      if result.status == ComplianceStatus.NON_COMPLIANT and result.remediation:
        recommendations.append(result.remediation)

    # Add recommendations for partial compliance
    partial_count = sum(
      1 for r in control_results if r.status == ComplianceStatus.PARTIAL
    )
    if partial_count > 0:
      recommendations.append(
        f"Complete implementation of {partial_count} partially compliant controls"
      )

    return recommendations

  def _requires_human_review(
    self, control_results: list[ControlResult], input_data: AssessmentInput
  ) -> bool:
    """Determine if human review is required."""
    # High-risk content always requires review
    if input_data.is_high_risk_decision:
      return True

    # Multiple non-compliant controls require review
    non_compliant = sum(
      1 for r in control_results if r.status == ComplianceStatus.NON_COMPLIANT
    )
    if non_compliant >= 3:
      return True

    # Low overall score requires review
    avg_score = (
      sum(r.score for r in control_results) / len(control_results)
      if control_results
      else 0
    )
    if avg_score < 0.5:
      return True

    return False

  async def _check_validation_rule(
    self, rule: ValidationRule, content: str, context: str | None
  ) -> ValidationViolation | None:
    """
    Check a single validation rule against content.

    Override in specific modules for custom validation logic.
    """
    # Default implementation - specific modules should override
    return None

  @staticmethod
  def hash_content(content: Any) -> str:
    """Generate SHA256 hash of content for audit trail."""
    if isinstance(content, (str, bytes)):
      data = content if isinstance(content, bytes) else content.encode()
    else:
      data = json.dumps(content, sort_keys=True, default=str).encode()
    return hashlib.sha256(data).hexdigest()

  def __repr__(self) -> str:
    return f"<{self.__class__.__name__} id={self.module_id.value} version={self._metadata.version}>"
