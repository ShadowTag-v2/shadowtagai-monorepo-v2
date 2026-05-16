# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
FraudJudge - Fraud Detection & Risk Scoring
Binary ALLOW/BLOCK decisions for fraud prevention and anomaly detection.

Primary Use Cases:
- Payment fraud detection
- Account takeover prevention
- Identity verification
- Transaction pattern anomalies
- Vendor fraud screening
"""

from typing import Any

from src.judges.base_judge import BaseJudge
from src.judges.models import JudgeDecision, JudgeRequest, JudgeType
from src.risk_matrix import Probability, Severity


class FraudJudge(BaseJudge):
  """
  Fraud detection judge.

  Evaluates:
  - Payment fraud indicators
  - Account security anomalies
  - Identity verification failures
  - Transaction pattern deviations
  - Vendor fraud risk
  """

  def __init__(self):
    super().__init__(JudgeType.FRAUD)
    self.high_fraud_score_threshold = 0.7
    self.medium_fraud_score_threshold = 0.4

  def evaluate_action(self, request: JudgeRequest) -> dict[str, Any]:
    """
    Evaluate fraud risk.

    Decision logic:
    1. Fraud score assessment (ML-based in production)
    2. Behavioral anomaly detection
    3. Geographic risk factors
    4. Velocity checks
    5. Identity verification status
    """
    context = request.context
    action_type = request.action_type

    # Extract fraud parameters
    fraud_score = context.get("fraud_score", 0.0)  # 0.0-1.0
    identity_verified = context.get("identity_verified", False)
    geo_mismatch = context.get("geo_location_mismatch", False)
    velocity_exceeded = context.get("velocity_check_failed", False)
    device_fingerprint_match = context.get("device_fingerprint_match", True)
    amount_usd = context.get("amount_usd", 0)
    is_new_payee = context.get("is_new_payee", False)
    time_since_account_creation_days = context.get("account_age_days", 365)

    # Decision rules
    decision = JudgeDecision.ALLOW
    reasoning_parts = []
    risk_flags = []

    # Rule 1: High fraud score - immediate block
    if fraud_score >= self.high_fraud_score_threshold:
      decision = JudgeDecision.BLOCK
      reasoning_parts.append(f"High fraud score ({fraud_score:.2f}) - BLOCK")
      risk_flags.append("high_fraud_score")

    # Rule 2: Identity verification failure
    elif not identity_verified and amount_usd > 1000:
      decision = JudgeDecision.BLOCK
      reasoning_parts.append("Identity not verified for transaction >$1K - BLOCK")
      risk_flags.append("identity_unverified")

    # Rule 3: Multiple fraud indicators
    fraud_indicator_count = sum(
      [
        geo_mismatch,
        velocity_exceeded,
        not device_fingerprint_match,
        is_new_payee and amount_usd > 5000,
        time_since_account_creation_days < 30,
      ]
    )

    if fraud_indicator_count >= 3:
      decision = JudgeDecision.BLOCK
      reasoning_parts.append(
        f"Multiple fraud indicators ({fraud_indicator_count}) detected - BLOCK"
      )
      risk_flags.append("multiple_indicators")

    # Rule 4: Medium fraud score with risk factors
    elif fraud_score >= self.medium_fraud_score_threshold:
      reasoning_parts.append(
        f"Medium fraud score ({fraud_score:.2f}) - requires additional verification"
      )
      risk_flags.append("medium_fraud_score")

      if geo_mismatch:
        decision = JudgeDecision.BLOCK
        reasoning_parts.append("Geographic mismatch detected")
        risk_flags.append("geo_mismatch")

    # Rule 5: New account with high-value transaction
    elif time_since_account_creation_days < 7 and amount_usd > 10_000:
      decision = JudgeDecision.BLOCK
      reasoning_parts.append(
        "New account (<7 days) with high-value transaction - BLOCK"
      )
      risk_flags.append("new_account_high_value")

    # Rule 6: Velocity check failure
    elif velocity_exceeded:
      decision = JudgeDecision.BLOCK
      reasoning_parts.append(
        "Transaction velocity exceeded - possible account takeover"
      )
      risk_flags.append("velocity_exceeded")

    # Rule 7: Low fraud score - allow with monitoring
    elif fraud_score < self.medium_fraud_score_threshold and identity_verified:
      reasoning_parts.append(
        f"Low fraud score ({fraud_score:.2f}), identity verified - approved with monitoring"
      )

    # Build reasoning
    if not reasoning_parts:
      reasoning = f"{action_type} - no fraud indicators detected"
    else:
      reasoning = "; ".join(reasoning_parts)

    return {
      "decision": decision,
      "reasoning": reasoning,
      "metadata": {
        "fraud_score": fraud_score,
        "risk_flags": risk_flags,
        "fraud_indicator_count": fraud_indicator_count,
        "identity_verified": identity_verified,
        "amount_usd": amount_usd,
      },
    }

  def extract_risk_factors(
    self, request: JudgeRequest, evaluation: dict[str, Any]
  ) -> tuple[Probability, Severity, str, list[str]]:
    """
    Extract ATP 5-19 risk factors for fraud detection.

    Probability factors:
    - Fraud score (ML model output)
    - Number of fraud indicators
    - Historical fraud patterns
    - Account age and history

    Severity factors:
    - Transaction amount
    - Account takeover impact
    - Identity theft consequences
    - Financial loss potential
    """
    context = request.context
    fraud_score = context.get("fraud_score", 0.0)
    amount_usd = context.get("amount_usd", 0)
    fraud_indicator_count = evaluation["metadata"].get("fraud_indicator_count", 0)

    # Determine probability based on fraud score and indicators
    if fraud_score >= 0.7 or fraud_indicator_count >= 3:
      probability = Probability.A  # Almost certain (>90%)
    elif fraud_score >= 0.5 or fraud_indicator_count >= 2:
      probability = Probability.B  # Likely (70-90%)
    elif fraud_score >= 0.3 or fraud_indicator_count >= 1:
      probability = Probability.C  # Possible (30-70%)
    elif fraud_score >= 0.1:
      probability = Probability.D  # Unlikely (10-30%)
    else:
      probability = Probability.E  # Rare (<10%)

    # Determine severity based on impact
    is_account_takeover = context.get("account_takeover_suspected", False)
    is_identity_theft = not context.get("identity_verified", True)

    if is_account_takeover or is_identity_theft:
      severity = Severity.I  # Catastrophic (identity theft, account loss)
    elif amount_usd >= 100_000:
      severity = Severity.II  # Critical (major financial loss)
    elif amount_usd >= 10_000:
      severity = Severity.III  # Moderate (significant loss)
    else:
      severity = Severity.IV  # Negligible (minor loss)

    # Rationale
    risk_flags = evaluation["metadata"].get("risk_flags", [])
    rationale = (
      f"Fraud detection: score {fraud_score:.2f}, "
      f"{fraud_indicator_count} indicators, "
      f"${amount_usd:,.0f} transaction. "
      f"Flags: {', '.join(risk_flags) if risk_flags else 'none'}. "
      f"Risk of fraud, account takeover, or identity theft."
    )

    # Mitigations
    mitigations = []
    if fraud_score >= self.medium_fraud_score_threshold:
      mitigations.append("Trigger step-up authentication (MFA)")
      mitigations.append("Contact account holder via verified channel")
    if not context.get("identity_verified", False):
      mitigations.append("Require identity verification (KYC)")
    if context.get("geo_location_mismatch", False):
      mitigations.append("Verify transaction via out-of-band communication")
    if context.get("velocity_check_failed", False):
      mitigations.append("Implement transaction delay/cooling-off period")
    if amount_usd > 10_000:
      mitigations.append("Route to manual fraud review queue")
    mitigations.append("Monitor account for 48 hours post-transaction")
    mitigations.append("Flag for behavioral analytics system")

    return probability, severity, rationale, mitigations


__all__ = ["FraudJudge"]
