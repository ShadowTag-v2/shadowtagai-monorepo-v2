# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Reasons Validator - JR Engine Component 2.

Validates the REASONS for an action:
- Why is this action justified?
- What evidence supports this decision?
- What is the risk/reward analysis?
- What is the stakeholder impact?
"""

from ..models import Action, ReasonsVerdict, VerdictStatus


class ReasonsValidator:
  """
  Validates the REASONS dimension of an action.
  """

  def __init__(self):
    self.evidence_keywords = {
      "data",
      "analysis",
      "research",
      "benchmark",
      "test",
      "measurement",
      "metric",
      "result",
      "finding",
      "report",
    }

  def validate(self, action: Action) -> ReasonsVerdict:
    """
    Validate the reasons for an action.

    Args:
        action: The action to validate

    Returns:
        ReasonsVerdict with status and scoring
    """
    # Assess evidence quality
    evidence_quality = self._assess_evidence_quality(action)

    # Calculate risk/reward ratio
    risk_reward_ratio = self._calculate_risk_reward(action)

    # Assess stakeholder impact
    stakeholder_impact = self._assess_stakeholder_impact(action)

    # Calculate justification score (0-10)
    score = self._calculate_score(
      evidence_quality, risk_reward_ratio, stakeholder_impact
    )

    # Determine status
    if score >= 7.0:
      status = VerdictStatus.APPROVED
    elif score >= 5.0:
      status = VerdictStatus.FLAGGED
    elif score >= 3.0:
      status = VerdictStatus.REQUIRES_REVIEW
    else:
      status = VerdictStatus.REJECTED

    explanation = self._generate_explanation(
      status, score, evidence_quality, risk_reward_ratio
    )

    return ReasonsVerdict(
      status=status,
      score=score,
      evidence_quality=evidence_quality,
      risk_reward_ratio=risk_reward_ratio,
      stakeholder_impact=stakeholder_impact,
      explanation=explanation,
      confidence=0.80,
    )

  def _assess_evidence_quality(self, action: Action) -> str:
    """Assess the quality of evidence supporting the action."""
    # Check for explicit evidence in context
    if "evidence" in action.context:
      evidence = str(action.context["evidence"]).lower()

      # Count evidence keywords
      evidence_count = sum(
        1 for keyword in self.evidence_keywords if keyword in evidence
      )

      if evidence_count >= 3:
        return "strong"
      elif evidence_count >= 1:
        return "medium"
      else:
        return "weak"

    # Check description for evidence keywords
    description = action.description.lower()
    evidence_count = sum(
      1 for keyword in self.evidence_keywords if keyword in description
    )

    if evidence_count >= 2:
      return "medium"
    elif evidence_count >= 1:
      return "weak"
    else:
      return "none"

  def _calculate_risk_reward(self, action: Action) -> float:
    """Calculate risk/reward ratio (higher = better)."""
    # Check for explicit risk/reward in context
    if "risk" in action.context and "reward" in action.context:
      try:
        risk = float(action.context["risk"])
        reward = float(action.context["reward"])
        if risk > 0:
          return reward / risk
      except (ValueError, ZeroDivisionError):
        pass

    # Default heuristic: assume moderate risk, moderate reward
    # In production, this would be ML-based or policy-based
    return 1.5  # Slightly positive ratio

  def _assess_stakeholder_impact(self, action: Action) -> str:
    """Assess the impact on stakeholders."""
    if "stakeholders" in action.context:
      stakeholders = action.context["stakeholders"]

      if isinstance(stakeholders, list):
        count = len(stakeholders)
        if count > 10:
          return "high_impact"
        elif count > 3:
          return "medium_impact"
        else:
          return "low_impact"

    # Check description for stakeholder keywords
    description = action.description.lower()
    stakeholder_keywords = ["user", "customer", "team", "organization", "public"]

    if any(keyword in description for keyword in stakeholder_keywords):
      return "medium_impact"

    return "low_impact"

  def _calculate_score(
    self,
    evidence_quality: str,
    risk_reward_ratio: float,
    stakeholder_impact: str,
  ) -> float:
    """Calculate reasons justification score (0-10)."""
    score = 5.0  # Baseline

    # Evidence quality: +0 to +3.0
    evidence_scores = {
      "strong": 3.0,
      "medium": 2.0,
      "weak": 1.0,
      "none": 0.0,
    }
    score += evidence_scores.get(evidence_quality, 0.0)

    # Risk/reward ratio: -1.0 to +2.0
    if risk_reward_ratio >= 3.0:
      score += 2.0
    elif risk_reward_ratio >= 1.5:
      score += 1.0
    elif risk_reward_ratio >= 1.0:
      score += 0.5
    elif risk_reward_ratio >= 0.5:
      score -= 0.5
    else:
      score -= 1.0

    # Stakeholder impact: +0 to +1.0 (positive impact is good)
    impact_scores = {
      "high_impact": 1.0,
      "medium_impact": 0.5,
      "low_impact": 0.0,
    }
    score += impact_scores.get(stakeholder_impact, 0.0)

    return min(10.0, max(0.0, score))

  def _generate_explanation(
    self,
    status: VerdictStatus,
    score: float,
    evidence_quality: str,
    risk_reward_ratio: float,
  ) -> str:
    """Generate human-readable explanation."""
    if status == VerdictStatus.APPROVED:
      return f"Reasons are well-justified (score: {score}/10). Evidence quality: {evidence_quality}. Risk/reward ratio: {risk_reward_ratio:.2f}."
    elif status == VerdictStatus.REJECTED:
      return f"Reasons are insufficient (score: {score}/10). Weak evidence ({evidence_quality}) and/or poor risk/reward ({risk_reward_ratio:.2f})."
    elif status == VerdictStatus.FLAGGED:
      return f"Reasons require attention (score: {score}/10). Evidence: {evidence_quality}, Risk/reward: {risk_reward_ratio:.2f}."
    else:  # REQUIRES_REVIEW
      return f"Reasons require human review (score: {score}/10). Insufficient justification for action."
