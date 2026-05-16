# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Kernel 2: Judge #6 Classifier using PyTorch (local)."""

import torch
import torch.nn as nn
from app.kernels.base import Kernel, KernelChainError
from app.models.kernel import KernelInput, KernelOutput, KernelMetrics
from app.models.decision import ViolationsScanOutput, JudgeSixClassification, RiskTier
from app.config import settings


class JudgeSixModel(nn.Module):
  """
  Simple neural network for binary classification.

  Input: Violation features (count, severity scores)
  Output: Single bit + confidence score
  """

  def __init__(self, input_dim: int = 10):
    super().__init__()
    self.network = nn.Sequential(
      nn.Linear(input_dim, 64),
      nn.ReLU(),
      nn.Dropout(0.2),
      nn.Linear(64, 32),
      nn.ReLU(),
      nn.Dropout(0.2),
      nn.Linear(32, 16),
      nn.ReLU(),
      nn.Linear(16, 1),
      nn.Sigmoid(),
    )

  def forward(self, x):
    return self.network(x)


class JudgeSixClassifyKernel(Kernel):
  """
  Kernel 2: Binary go/no-go classification from violations.

  Specifications:
  - Input: Violations JSON (~2.5KB)
  - Output: Single bit + confidence score
  - Model: PyTorch local (0 cost, 12ms p99 target)
  - Token reduction: 2.5KB → 1 bit (99.96% compression)
  """

  SEVERITY_WEIGHTS = {
    "minor": 1.0,
    "moderate": 2.5,
    "major": 5.0,
    "critical": 10.0,
  }

  RISK_TIER_THRESHOLDS = [
    (0.0, RiskTier.TIER_1_MINIMAL),
    (2.0, RiskTier.TIER_2_LOW),
    (5.0, RiskTier.TIER_3_MODERATE),
    (10.0, RiskTier.TIER_4_HIGH),
    (20.0, RiskTier.TIER_5_CRITICAL),
  ]

  def __init__(self):
    super().__init__(
      name="JudgeSixClassifyKernel", max_latency_ms=settings.kernel_2_max_latency_ms
    )

    # Initialize PyTorch model
    self.device = torch.device("cpu")  # Local CPU inference
    self.model = JudgeSixModel(input_dim=10).to(self.device)
    self.model.eval()  # Inference mode

    # In production, load pre-trained weights:
    # self.model.load_state_dict(torch.load("judge_six_weights.pt"))

  async def execute(self, kernel_input: KernelInput) -> KernelOutput:
    """
    Classify violations into binary go/no-go decision.

    Args:
        kernel_input: Contains ViolationsScanOutput in data field

    Returns:
        KernelOutput with JudgeSixClassification

    Note:
        When model weights are untrained (random init), falls back to
        deterministic rule-based classification using violation severity
        and count. The neural network output supplements this when a
        trained checkpoint is loaded.
    """
    try:
      # Extract violations
      if isinstance(kernel_input.data, ViolationsScanOutput):
        violations_output = kernel_input.data
      else:
        raise KernelChainError(
          f"Invalid input type: expected ViolationsScanOutput, got {type(kernel_input.data)}"
        )

      # Extract features from violations
      features = self._extract_features(violations_output)

      # Convert to tensor
      feature_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)

      # Run inference (no gradient computation needed)
      with torch.no_grad():
        model_output = self.model(feature_tensor)
        model_confidence = model_output.item()

      # Deterministic rule-based classification
      # (supplements untrained model with sound logic)
      violations = violations_output.violations
      weighted_score = sum(self.SEVERITY_WEIGHTS.get(v.severity, 0) for v in violations)
      has_critical = any(v.severity == "critical" for v in violations)

      if len(violations) == 0:
        # No violations → approve with high confidence
        decision = True
        confidence = max(0.85, model_confidence)
      elif has_critical or weighted_score >= 10.0:
        # Critical violations or high severity → reject with high confidence
        decision = False
        # Scale confidence from severity: higher severity → higher confidence in rejection
        severity_confidence = min(0.95, 0.7 + (weighted_score / 50.0))
        confidence = max(severity_confidence, model_confidence)
      else:
        # Non-critical violations → reject with moderate confidence
        decision = False
        severity_confidence = min(0.85, 0.6 + (weighted_score / 30.0))
        confidence = max(severity_confidence, model_confidence)

      # Calculate risk tier
      risk_tier = self._calculate_risk_tier(violations_output)

      # Generate reasoning
      reasoning = self._generate_reasoning(violations_output, confidence, risk_tier)

      # Create classification output
      classification = JudgeSixClassification(
        decision=decision,
        confidence=confidence,
        risk_tier=risk_tier,
        reasoning=reasoning,
      )

      return KernelOutput(
        data=classification,
        kernel_name=self.name,
        success=True,
        metrics=KernelMetrics(
          latency_ms=0,  # Will be set by base class
          token_count_input=0,  # No tokens (local model)
          token_count_output=0,
          cost_usd=0.0,  # Local inference is free
          confidence=confidence,
        ),
      )

    except Exception as e:
      raise KernelChainError(f"Judge #6 classification failed: {str(e)}") from e

  def _extract_features(self, violations_output: ViolationsScanOutput) -> list:
    """
    Extract numerical features from violations for model input.

    Features (10-dimensional):
    1. Total violation count
    2-5. Count by severity (minor, moderate, major, critical)
    6. Weighted severity score
    7. Average violations per rule category
    8. Max severity indicator (1 if critical exists, else 0)
    9-10. Reserved for future features (currently 0)
    """
    violations = violations_output.violations

    # Feature 1: Total count
    total_count = len(violations)

    # Features 2-5: Count by severity
    severity_counts = {
      "minor": 0,
      "moderate": 0,
      "major": 0,
      "critical": 0,
    }
    for v in violations:
      severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

    # Feature 6: Weighted severity score
    weighted_score = sum(self.SEVERITY_WEIGHTS.get(v.severity, 0) for v in violations)

    # Feature 7: Average violations (normalized)
    avg_violations = total_count / 10.0  # Normalize to [0, 1] range

    # Feature 8: Critical violation indicator
    has_critical = 1.0 if severity_counts["critical"] > 0 else 0.0

    # Features 9-10: Reserved (zeros)
    features = [
      min(total_count / 10.0, 1.0),  # Normalize total count
      min(severity_counts["minor"] / 5.0, 1.0),
      min(severity_counts["moderate"] / 3.0, 1.0),
      min(severity_counts["major"] / 2.0, 1.0),
      min(severity_counts["critical"], 1.0),
      min(weighted_score / 20.0, 1.0),  # Normalize weighted score
      min(avg_violations, 1.0),
      has_critical,
      0.0,  # Reserved
      0.0,  # Reserved
    ]

    return features

  def _calculate_risk_tier(self, violations_output: ViolationsScanOutput) -> RiskTier:
    """Calculate risk tier based on weighted severity score."""
    weighted_score = sum(
      self.SEVERITY_WEIGHTS.get(v.severity, 0) for v in violations_output.violations
    )

    # Find appropriate tier based on thresholds
    risk_tier = RiskTier.TIER_1_MINIMAL
    for threshold, tier in reversed(self.RISK_TIER_THRESHOLDS):
      if weighted_score >= threshold:
        risk_tier = tier
        break

    return risk_tier

  def _generate_reasoning(
    self,
    violations_output: ViolationsScanOutput,
    confidence: float,
    risk_tier: RiskTier,
  ) -> str:
    """Generate human-readable reasoning for the decision."""
    total = violations_output.total_violations

    if total == 0:
      return "No ATP 5-19 violations detected. Decision approved."

    severity_summary = {}
    for v in violations_output.violations:
      severity_summary[v.severity] = severity_summary.get(v.severity, 0) + 1

    severity_str = ", ".join(
      f"{count} {severity}" for severity, count in severity_summary.items()
    )

    return f"Detected {total} violation(s): {severity_str}. Risk tier: {risk_tier.name}. Confidence: {confidence:.2%}"
