# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
NIST AI Risk Management Framework Module

Implements the NIST AI RMF 1.0 requirements.
Focus areas:
- GOVERN: Policies, processes, and accountability
- MAP: Context and risk identification
- MEASURE: Risk analysis and assessment
- MANAGE: Risk prioritization and response

Reference: NIST AI RMF 1.0 (January 2023)
"""

from datetime import datetime

from app.compliance.modules.base import ComplianceModule
from app.compliance.registry import register_module
from app.models.compliance import (
  AssessmentInput,
  ComplianceStatus,
  ControlDefinition,
  ControlResult,
  Jurisdiction,
  ModuleMetadata,
  RegulationId,
  RiskTier,
  ValidationRule,
  ValidationViolation,
)


@register_module(RegulationId.NIST_RMF)
class NISTRMFModule(ComplianceModule):
  """
  NIST AI Risk Management Framework Module

  Implements the four core functions of the AI RMF:
  1. GOVERN - Cultivate a culture of risk management
  2. MAP - Contextualize risks within the AI lifecycle
  3. MEASURE - Analyze and assess AI risks
  4. MANAGE - Prioritize and act upon risks
  """

  # AI RMF Characteristics for Trustworthy AI
  TRUSTWORTHY_CHARACTERISTICS = [
    "valid_reliable",
    "safe",
    "secure_resilient",
    "accountable_transparent",
    "explainable_interpretable",
    "privacy_enhanced",
    "fair_bias_managed",
  ]

  def _define_metadata(self) -> ModuleMetadata:
    return ModuleMetadata(
      id=RegulationId.NIST_RMF,
      name="NIST AI Risk Management Framework",
      short_name="NIST AI RMF",
      version="1.0",
      jurisdiction=Jurisdiction.GLOBAL,
      description=(
        "Voluntary framework for managing risks in the design, development, "
        "deployment, and use of AI systems. Provides a structured approach "
        "to trustworthy AI across the AI lifecycle."
      ),
      effective_date=datetime(2023, 1, 26),
      articles=[
        "GOVERN 1 - Policies, processes, procedures",
        "GOVERN 2 - Accountability structures",
        "GOVERN 3 - Workforce diversity and culture",
        "GOVERN 4 - Organizational commitment",
        "MAP 1 - Context establishment",
        "MAP 2 - AI categorization",
        "MAP 3 - Benefits and costs",
        "MEASURE 1 - Risk identification",
        "MEASURE 2 - Risk estimation",
        "MEASURE 3 - Continuous monitoring",
        "MANAGE 1 - Risk prioritization",
        "MANAGE 2 - Risk treatment",
        "MANAGE 3 - Risk documentation",
      ],
      official_url="https://www.nist.gov/itl/ai-risk-management-framework",
      pricing_addon_usd=55.0,
    )

  def _define_controls(self) -> list[ControlDefinition]:
    return [
      # GOVERN Function
      ControlDefinition(
        control_id="NIST-GOV-1.1",
        name="AI Risk Management Policy",
        description="Establish policies for AI risk management aligned with org values",
        article_ref="GOVERN 1.1",
        required_evidence=[
          "AI risk management policy",
          "Policy review schedule",
          "Stakeholder input documentation",
        ],
      ),
      ControlDefinition(
        control_id="NIST-GOV-1.2",
        name="AI Risk Management Processes",
        description="Define processes for AI risk assessment and mitigation",
        article_ref="GOVERN 1.2",
        required_evidence=[
          "Risk assessment procedures",
          "Mitigation workflows",
        ],
      ),
      ControlDefinition(
        control_id="NIST-GOV-2.1",
        name="Accountability Structures",
        description="Establish roles and responsibilities for AI risk management",
        article_ref="GOVERN 2.1",
        required_evidence=[
          "RACI matrix",
          "Role definitions",
          "Reporting structure",
        ],
      ),
      ControlDefinition(
        control_id="NIST-GOV-3.1",
        name="AI Literacy and Culture",
        description="Foster AI risk awareness across the organization",
        article_ref="GOVERN 3",
        required_evidence=["Training programs", "Awareness initiatives"],
      ),
      # MAP Function
      ControlDefinition(
        control_id="NIST-MAP-1.1",
        name="AI System Context",
        description="Document intended purpose, users, and deployment context",
        article_ref="MAP 1.1",
        required_evidence=[
          "System description",
          "Use case documentation",
          "User profiles",
        ],
      ),
      ControlDefinition(
        control_id="NIST-MAP-1.2",
        name="Stakeholder Identification",
        description="Identify all stakeholders and their interests",
        article_ref="MAP 1.2",
        required_evidence=["Stakeholder register", "Impact assessment"],
      ),
      ControlDefinition(
        control_id="NIST-MAP-2.1",
        name="AI Categorization",
        description="Categorize AI system based on risk and impact",
        article_ref="MAP 2",
        required_evidence=["Risk categorization", "Impact assessment"],
      ),
      ControlDefinition(
        control_id="NIST-MAP-3.1",
        name="Benefits and Costs Analysis",
        description="Analyze benefits, costs, and tradeoffs of AI deployment",
        article_ref="MAP 3",
        required_evidence=["Benefit-cost analysis", "Tradeoff documentation"],
      ),
      # MEASURE Function
      ControlDefinition(
        control_id="NIST-MEA-1.1",
        name="Risk Identification Methods",
        description="Apply methods to identify AI risks",
        article_ref="MEASURE 1",
        required_evidence=["Risk identification methodology", "Risk register"],
      ),
      ControlDefinition(
        control_id="NIST-MEA-2.1",
        name="Trustworthiness Assessment",
        description="Assess AI system against trustworthy characteristics",
        article_ref="MEASURE 2",
        required_evidence=[
          "Trustworthiness assessment",
          "Characteristic scores",
        ],
      ),
      ControlDefinition(
        control_id="NIST-MEA-2.2",
        name="Bias and Fairness Testing",
        description="Test for bias and assess fairness across groups",
        article_ref="MEASURE 2.6",
        required_evidence=["Bias testing results", "Fairness metrics"],
      ),
      ControlDefinition(
        control_id="NIST-MEA-3.1",
        name="Continuous Monitoring",
        description="Monitor AI system performance and risks over time",
        article_ref="MEASURE 3",
        required_evidence=[
          "Monitoring dashboard",
          "Alert thresholds",
          "Incident logs",
        ],
      ),
      # MANAGE Function
      ControlDefinition(
        control_id="NIST-MAN-1.1",
        name="Risk Prioritization",
        description="Prioritize identified risks for treatment",
        article_ref="MANAGE 1",
        required_evidence=[
          "Risk prioritization matrix",
          "Treatment priorities",
        ],
      ),
      ControlDefinition(
        control_id="NIST-MAN-2.1",
        name="Risk Treatment Plans",
        description="Develop and implement risk treatment plans",
        article_ref="MANAGE 2",
        required_evidence=["Treatment plans", "Implementation status"],
      ),
      ControlDefinition(
        control_id="NIST-MAN-3.1",
        name="Risk Documentation",
        description="Document risks, decisions, and residual risks",
        article_ref="MANAGE 3",
        required_evidence=["Risk documentation", "Decision logs"],
      ),
    ]

  def _define_validation_rules(self) -> list[ValidationRule]:
    return [
      ValidationRule(
        rule_id="NIST-VAL-001",
        name="Transparency Check",
        description="Check for transparency in AI decision explanations",
        category="transparency",
        severity="medium",
        auto_check=True,
      ),
      ValidationRule(
        rule_id="NIST-VAL-002",
        name="Bias Indicator Detection",
        description="Detect potential bias indicators in AI outputs",
        category="fairness",
        severity="high",
        auto_check=True,
      ),
      ValidationRule(
        rule_id="NIST-VAL-003",
        name="Safety Concern Detection",
        description="Detect potential safety concerns in AI recommendations",
        category="safety",
        severity="critical",
        auto_check=True,
      ),
    ]

  async def assess_control(
    self, control: ControlDefinition, input_data: AssessmentInput
  ) -> ControlResult:
    """Assess a single NIST AI RMF control."""
    metadata = input_data.metadata

    # GOVERN - Policy
    if control.control_id == "NIST-GOV-1.1":
      has_policy = metadata.get("ai_risk_policy", False)
      if has_policy:
        return ControlResult(
          control_id=control.control_id,
          control_name=control.name,
          module_id=self.module_id,
          status=ComplianceStatus.COMPLIANT,
          score=1.0,
          evidence="AI risk management policy established",
        )
      else:
        return ControlResult(
          control_id=control.control_id,
          control_name=control.name,
          module_id=self.module_id,
          status=ComplianceStatus.NON_COMPLIANT,
          score=0.0,
          findings=["AI risk management policy not established"],
          remediation="Develop and document AI risk management policy",
        )

    # MAP - Context
    if control.control_id == "NIST-MAP-1.1":
      has_context = metadata.get("system_context_documented", False)
      if has_context:
        return ControlResult(
          control_id=control.control_id,
          control_name=control.name,
          module_id=self.module_id,
          status=ComplianceStatus.COMPLIANT,
          score=1.0,
          evidence="AI system context documented",
        )
      else:
        return ControlResult(
          control_id=control.control_id,
          control_name=control.name,
          module_id=self.module_id,
          status=ComplianceStatus.PARTIAL,
          score=0.5,
          findings=["System context documentation incomplete"],
          remediation="Document intended purpose, users, and deployment context",
        )

    # MEASURE - Trustworthiness
    if control.control_id == "NIST-MEA-2.1":
      trustworthiness_scores = metadata.get("trustworthiness_scores", {})
      if trustworthiness_scores:
        avg_score = sum(trustworthiness_scores.values()) / len(trustworthiness_scores)
        if avg_score >= 0.8:
          status = ComplianceStatus.COMPLIANT
        elif avg_score >= 0.6:
          status = ComplianceStatus.PARTIAL
        else:
          status = ComplianceStatus.NON_COMPLIANT
        return ControlResult(
          control_id=control.control_id,
          control_name=control.name,
          module_id=self.module_id,
          status=status,
          score=avg_score,
          evidence=f"Trustworthiness assessment completed: {avg_score:.0%}",
        )

    # MANAGE - Monitoring
    if control.control_id == "NIST-MEA-3.1":
      monitoring_enabled = metadata.get("continuous_monitoring", False)
      if monitoring_enabled:
        return ControlResult(
          control_id=control.control_id,
          control_name=control.name,
          module_id=self.module_id,
          status=ComplianceStatus.COMPLIANT,
          score=1.0,
          evidence="Continuous monitoring implemented",
        )

    # Default
    return ControlResult(
      control_id=control.control_id,
      control_name=control.name,
      module_id=self.module_id,
      status=ComplianceStatus.PARTIAL,
      score=0.5,
      findings=["Assessment evidence required"],
      remediation=f"Provide evidence for {control.name}",
    )

  def determine_risk_tier(self, input_data: AssessmentInput) -> RiskTier | None:
    """Determine risk tier based on NIST AI RMF approach."""
    metadata = input_data.metadata

    # Check trustworthiness scores
    scores = metadata.get("trustworthiness_scores", {})
    if scores:
      avg_score = sum(scores.values()) / len(scores)
      if avg_score < 0.4:
        return RiskTier.HIGH
      elif avg_score < 0.7:
        return RiskTier.LIMITED
      else:
        return RiskTier.MINIMAL

    # High-impact decisions
    if input_data.is_high_risk_decision:
      return RiskTier.HIGH

    # Check system impact level
    impact_level = metadata.get("impact_level", "low")
    if impact_level == "high":
      return RiskTier.HIGH
    elif impact_level == "moderate":
      return RiskTier.LIMITED

    return RiskTier.MINIMAL

  async def _check_validation_rule(
    self, rule: ValidationRule, content: str, context: str | None
  ) -> ValidationViolation | None:
    """Check NIST AI RMF validation rules."""
    content_lower = content.lower()

    if rule.rule_id == "NIST-VAL-002":
      # Bias Indicator Detection
      bias_indicators = [
        "always",
        "never",
        "all people",
        "no one ever",
        "men are",
        "women are",
        "old people",
        "young people",
      ]
      for indicator in bias_indicators:
        if indicator in content_lower:
          return ValidationViolation(
            module_id=self.module_id,
            rule_id=rule.rule_id,
            severity="high",
            description=f"Potential bias indicator detected: '{indicator}'",
            location=indicator,
            suggested_fix="Review for potential bias and ensure fair treatment across groups",
            article_reference="NIST AI RMF - MEASURE 2.6",
          )

    if rule.rule_id == "NIST-VAL-003":
      # Safety Concern Detection
      safety_concerns = [
        "could harm",
        "may cause injury",
        "dangerous",
        "risk of death",
        "life-threatening",
        "critical failure",
      ]
      for concern in safety_concerns:
        if concern in content_lower:
          return ValidationViolation(
            module_id=self.module_id,
            rule_id=rule.rule_id,
            severity="critical",
            description=f"Safety concern detected: '{concern}'",
            location=concern,
            suggested_fix="Apply additional safety controls and human oversight",
            article_reference="NIST AI RMF - Safe characteristic",
          )

    return None

  def calculate_maturity_level(self, scores: dict[str, float]) -> str:
    """Calculate overall AI RMF maturity level."""
    if not scores:
      return "initial"

    avg = sum(scores.values()) / len(scores)
    if avg >= 0.90:
      return "optimizing"
    elif avg >= 0.75:
      return "managed"
    elif avg >= 0.60:
      return "defined"
    elif avg >= 0.40:
      return "developing"
    else:
      return "initial"
