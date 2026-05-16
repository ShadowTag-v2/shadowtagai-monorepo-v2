# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ATP 5-19 Risk Assessment Matrix
Army Techniques Publication 5-19 compliant risk matrix implementation.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Probability(str, Enum):
  """Risk probability levels (ATP 5-19 compliant)."""

  A = "A"  # Almost Certain (>90% likely)
  B = "B"  # Likely (70-90%)
  C = "C"  # Possible (30-70%)
  D = "D"  # Unlikely (10-30%)
  E = "E"  # Rare (<10%)


class Severity(str, Enum):
  """Risk severity levels (ATP 5-19 compliant)."""

  I = "I"  # Catastrophic (mission failure, death, >$10M loss)
  II = "II"  # Critical (degraded mission, severe injury, $1-10M loss)
  III = "III"  # Moderate (degraded performance, minor injury, $100K-1M loss)
  IV = "IV"  # Negligible (minimal impact, no injury, <$100K loss)


class RiskLevel(str, Enum):
  """Overall risk assessment levels."""

  EH = "extremely_high"  # Requires immediate action, highest authority approval
  H = "high"  # Requires action, senior authority approval
  M = "medium"  # Monitor closely, moderate authority approval
  L = "low"  # Accept with monitoring


# ATP 5-19 Risk Matrix Lookup Table
# Probability (rows) × Severity (columns) → Risk Level
RISK_MATRIX = {
  (Probability.A, Severity.I): RiskLevel.EH,
  (Probability.A, Severity.II): RiskLevel.EH,
  (Probability.A, Severity.III): RiskLevel.H,
  (Probability.A, Severity.IV): RiskLevel.M,
  (Probability.B, Severity.I): RiskLevel.EH,
  (Probability.B, Severity.II): RiskLevel.H,
  (Probability.B, Severity.III): RiskLevel.H,
  (Probability.B, Severity.IV): RiskLevel.M,
  (Probability.C, Severity.I): RiskLevel.EH,
  (Probability.C, Severity.II): RiskLevel.H,
  (Probability.C, Severity.III): RiskLevel.M,
  (Probability.C, Severity.IV): RiskLevel.L,
  (Probability.D, Severity.I): RiskLevel.H,
  (Probability.D, Severity.II): RiskLevel.M,
  (Probability.D, Severity.III): RiskLevel.M,
  (Probability.D, Severity.IV): RiskLevel.L,
  (Probability.E, Severity.I): RiskLevel.M,
  (Probability.E, Severity.II): RiskLevel.M,
  (Probability.E, Severity.III): RiskLevel.L,
  (Probability.E, Severity.IV): RiskLevel.L,
}


class RiskAssessment(BaseModel):
  """Risk assessment result."""

  probability: Probability = Field(..., description="Event probability (A-E)")
  severity: Severity = Field(..., description="Impact severity (I-IV)")
  risk_level: RiskLevel = Field(..., description="Overall risk level (EH/H/M/L)")
  rationale: str = Field(..., description="Risk assessment rationale")
  mitigations: list[str] = Field(
    default_factory=list, description="Risk mitigation measures"
  )
  residual_risk: RiskLevel = Field(..., description="Risk after mitigations")
  requires_approval: bool = Field(..., description="Requires human approval")
  approval_authority: str = Field(..., description="Required approval authority level")


def calculate_risk_level(probability: Probability, severity: Severity) -> RiskLevel:
  """
  Calculate risk level from probability and severity using ATP 5-19 matrix.

  Args:
      probability: Event probability (A-E)
      severity: Impact severity (I-IV)

  Returns:
      Risk level (EH/H/M/L)
  """
  return RISK_MATRIX.get((probability, severity), RiskLevel.M)


def determine_approval_authority(
  risk_level: RiskLevel, amount_usd: float = 0
) -> tuple[str, bool]:
  """
  Determine required approval authority based on risk level and amount.

  Args:
      risk_level: Assessed risk level
      amount_usd: Transaction amount (if financial)

  Returns:
      Tuple of (authority_level, requires_approval)
  """
  # Financial thresholds
  if amount_usd >= 50_000:
    return ("CFO", True)
  elif amount_usd >= 10_000:
    return ("Finance Director", True)

  # Risk-based approval
  if risk_level == RiskLevel.EH:
    return ("C-Suite + Board", True)
  elif risk_level == RiskLevel.H:
    return ("Senior Executive", True)
  elif risk_level == RiskLevel.M:
    return ("Department Head", True)
  else:
    return ("Automated", False)


def assess_risk(
  probability: Probability,
  severity: Severity,
  rationale: str,
  mitigations: list[str] = None,
  amount_usd: float = 0,
) -> RiskAssessment:
  """
  Perform complete risk assessment.

  Args:
      probability: Event probability
      severity: Impact severity
      rationale: Assessment reasoning
      mitigations: Risk mitigation measures
      amount_usd: Transaction amount (if applicable)

  Returns:
      Complete risk assessment
  """
  risk_level = calculate_risk_level(probability, severity)

  # Calculate residual risk after mitigations
  # Simple heuristic: mitigations reduce severity by one level
  residual_severity = severity
  if mitigations and len(mitigations) > 0:
    severity_order = [Severity.I, Severity.II, Severity.III, Severity.IV]
    current_idx = severity_order.index(severity)
    if current_idx < len(severity_order) - 1:
      residual_severity = severity_order[current_idx + 1]

  residual_risk = calculate_risk_level(probability, residual_severity)
  authority, requires_approval = determine_approval_authority(residual_risk, amount_usd)

  return RiskAssessment(
    probability=probability,
    severity=severity,
    risk_level=risk_level,
    rationale=rationale,
    mitigations=mitigations or [],
    residual_risk=residual_risk,
    requires_approval=requires_approval,
    approval_authority=authority,
  )


__all__ = [
  "Probability",
  "Severity",
  "RiskLevel",
  "RiskAssessment",
  "calculate_risk_level",
  "determine_approval_authority",
  "assess_risk",
]
