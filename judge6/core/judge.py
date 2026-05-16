# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 - 3-Layer ATP 5-19 Risk Assessment Engine
Military-grade AI governance system

Architecture:
  Layer 1: Gemini (Policy Understanding) - Interprets Purpose/Reasons/Brakes
  Layer 2: PyTorch (Deterministic Enforcement) - Catches edge cases
  Layer 3: Rules Engine (Hard Gates) - Final enforcement

Target: p99 ≤90ms latency
"""

import time
from typing import Any
from dataclasses import dataclass
from enum import Enum

from ..models.database import RiskLevel
from .layer1_gemini import GeminiPolicyLayer
from .layer2_pytorch import PyTorchEnforcementLayer
from .layer3_rules import RulesEngineLayer


class Decision(str, Enum):
  """Final decision on request"""

  ALLOW = "allow"
  DENY = "deny"
  WARN = "warn"  # Allow but flag for review


@dataclass
class LayerResult:
  """Result from a single layer"""

  risk_level: RiskLevel
  confidence: float  # 0.0 to 1.0
  reasoning: str
  latency_ms: int
  metadata: dict[str, Any] = None


@dataclass
class JudgmentResult:
  """Final judgment from all 3 layers"""

  # Decision
  decision: Decision
  risk_level: RiskLevel
  confidence: float

  # Reasoning
  reasoning: str
  violated_rules: list[str]

  # Layer breakdown
  layer1_result: LayerResult
  layer2_result: LayerResult
  layer3_result: LayerResult

  # Performance
  total_latency_ms: int

  # Metadata
  request_id: str


class Judge:
  """
  Main ATP 5-19 Judge orchestrator
  Runs all 3 layers in sequence and aggregates results
  """

  def __init__(self):
    """Initialize all 3 layers"""
    self.layer1 = GeminiPolicyLayer()
    self.layer2 = PyTorchEnforcementLayer()
    self.layer3 = RulesEngineLayer()

  async def assess(
    self,
    prompt: str,
    context: dict[str, Any] | None = None,
    user_policies: list[dict] | None = None,
    request_id: str | None = None,
  ) -> JudgmentResult:
    """
    Perform ATP 5-19 risk assessment on AI request

    Args:
        prompt: The AI request to assess
        context: Additional context (user data, metadata, etc.)
        user_policies: Custom policies from user (overrides defaults)
        request_id: Unique request identifier for audit trail

    Returns:
        JudgmentResult with final decision and reasoning
    """
    start_time = time.perf_counter()

    if not request_id:
      import uuid

      request_id = str(uuid.uuid4())

    # LAYER 1: Gemini Policy Understanding
    layer1_result = await self._run_layer1(prompt, context, user_policies)

    # LAYER 2: PyTorch Deterministic Enforcement
    layer2_result = await self._run_layer2(prompt, context, layer1_result)

    # LAYER 3: Rules Engine (Hard Gates)
    layer3_result = await self._run_layer3(
      prompt, context, layer1_result, layer2_result
    )

    # Aggregate results
    total_latency_ms = int((time.perf_counter() - start_time) * 1000)

    # Decision logic: Most restrictive layer wins
    final_risk_level = self._aggregate_risk_levels(
      layer1_result.risk_level,
      layer2_result.risk_level,
      layer3_result.risk_level,
    )

    # Hard gate: If Layer 3 rules are violated, DENY
    if layer3_result.metadata.get("violated_rules"):
      final_decision = Decision.DENY
    elif final_risk_level in [RiskLevel.CATASTROPHIC, RiskLevel.CRITICAL]:
      final_decision = Decision.DENY
    elif final_risk_level == RiskLevel.MODERATE:
      final_decision = Decision.WARN
    else:
      final_decision = Decision.ALLOW

    # Aggregate reasoning
    reasoning = self._build_reasoning(layer1_result, layer2_result, layer3_result)

    # Calculate final confidence (weighted average)
    final_confidence = (
      layer1_result.confidence * 0.4
      + layer2_result.confidence * 0.4
      + layer3_result.confidence * 0.2
    )

    return JudgmentResult(
      decision=final_decision,
      risk_level=final_risk_level,
      confidence=final_confidence,
      reasoning=reasoning,
      violated_rules=layer3_result.metadata.get("violated_rules", []),
      layer1_result=layer1_result,
      layer2_result=layer2_result,
      layer3_result=layer3_result,
      total_latency_ms=total_latency_ms,
      request_id=request_id,
    )

  async def _run_layer1(
    self,
    prompt: str,
    context: dict[str, Any] | None,
    user_policies: list[dict] | None,
  ) -> LayerResult:
    """Run Layer 1: Gemini policy understanding"""
    start_time = time.perf_counter()

    result = await self.layer1.assess(prompt, context, user_policies)

    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return LayerResult(
      risk_level=result["risk_level"],
      confidence=result["confidence"],
      reasoning=result["reasoning"],
      latency_ms=latency_ms,
      metadata=result.get("metadata", {}),
    )

  async def _run_layer2(
    self,
    prompt: str,
    context: dict[str, Any] | None,
    layer1_result: LayerResult,
  ) -> LayerResult:
    """Run Layer 2: PyTorch deterministic enforcement"""
    start_time = time.perf_counter()

    result = await self.layer2.assess(prompt, context, layer1_result)

    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return LayerResult(
      risk_level=result["risk_level"],
      confidence=result["confidence"],
      reasoning=result["reasoning"],
      latency_ms=latency_ms,
      metadata=result.get("metadata", {}),
    )

  async def _run_layer3(
    self,
    prompt: str,
    context: dict[str, Any] | None,
    layer1_result: LayerResult,
    layer2_result: LayerResult,
  ) -> LayerResult:
    """Run Layer 3: Rules engine (hard gates)"""
    start_time = time.perf_counter()

    result = await self.layer3.assess(prompt, context, layer1_result, layer2_result)

    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return LayerResult(
      risk_level=result["risk_level"],
      confidence=result["confidence"],
      reasoning=result["reasoning"],
      latency_ms=latency_ms,
      metadata=result.get("metadata", {}),
    )

  def _aggregate_risk_levels(
    self, level1: RiskLevel, level2: RiskLevel, level3: RiskLevel
  ) -> RiskLevel:
    """
    Aggregate risk levels from all 3 layers
    Strategy: Most restrictive (highest risk) wins
    """
    risk_hierarchy = {
      RiskLevel.CATASTROPHIC: 5,
      RiskLevel.CRITICAL: 4,
      RiskLevel.MODERATE: 3,
      RiskLevel.LOW: 2,
      RiskLevel.NEGLIGIBLE: 1,
    }

    highest_risk = max(
      [level1, level2, level3],
      key=lambda x: risk_hierarchy[x],
    )

    return highest_risk

  def _build_reasoning(
    self,
    layer1: LayerResult,
    layer2: LayerResult,
    layer3: LayerResult,
  ) -> str:
    """Build human-readable reasoning from all layers"""
    parts = [
      "ATP 5-19 Risk Assessment:",
      f"\n• Layer 1 (Policy): {layer1.reasoning} (Confidence: {layer1.confidence:.2%})",
      f"• Layer 2 (Enforcement): {layer2.reasoning} (Confidence: {layer2.confidence:.2%})",
      f"• Layer 3 (Rules): {layer3.reasoning} (Confidence: {layer3.confidence:.2%})",
    ]

    if layer3.metadata.get("violated_rules"):
      parts.append(
        f"\n⚠️  Hard gates violated: {', '.join(layer3.metadata['violated_rules'])}"
      )

    return "\n".join(parts)


# Singleton instance
_judge_instance: Judge | None = None


def get_judge() -> Judge:
  """Get or create singleton Judge instance"""
  global _judge_instance
  if _judge_instance is None:
    _judge_instance = Judge()
  return _judge_instance
