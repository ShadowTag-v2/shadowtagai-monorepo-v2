"""
JUDGE #6 - Hybrid Validation Pipeline
======================================

SLA: p99 ≤ 90ms end-to-end validation

ARCHITECTURE:
------------
Stage 1: JR Engine ATP 5-19 scan (<500μs)
         ├─ LOW risk → Skip Gemini → Stage 3 (80%+ fast path)
         └─ MEDIUM/HIGH/EXTREME → Stage 2

Stage 2: Gemini semantic check (if risk > LOW)
         ├─ Latency: ~40-60ms typical
         └─ Validates context, intent, safety

Stage 3: PyTorch classifier + rules enforcement
         ├─ Local inference: ~15-25ms
         └─ Final decision: APPROVE/REJECT/ESCALATE

Total p99 target: ≤90ms

PERFORMANCE OPTIMIZATION:
------------------------
- 80%+ requests hit LOW risk → skip Gemini → ~20-30ms total
- 20% requests require Gemini → ~70-85ms total
- Parallel PyTorch + rules when possible

SK PATTERN: Sequential Pipeline with conditional stage skipping
COMPETITIVE ADVANTAGE: Google Vertex AI has no SLA commitments

Author: Pnkln Architecture Team
Version: 1.0.0
License: Proprietary
"""

import asyncio
import logging
import time
from dataclasses import dataclass

from pnkln.core.cor_orchestrator import ExecutionContext, SequentialPipeline
from pnkln.core.jr_engine import JREngine, RiskLevel

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class ValidationResult:
  """
  Result from Judge #6 validation pipeline.

  Attributes:
      decision: Final decision (APPROVE/REJECT/ESCALATE)
      confidence: Confidence score 0.0-1.0
      risk_level: ATP 5-19 risk assessment
      latency_ms: Total validation time
      stage_latencies: Per-stage timing breakdown
      reasons: Evidence chain for decision
      metadata: Additional context
  """

  decision: str  # "APPROVE" | "REJECT" | "ESCALATE"
  confidence: float  # 0.0 - 1.0
  risk_level: RiskLevel
  latency_ms: float
  stage_latencies: dict[str, float]
  reasons: str
  metadata: dict = None

  def __post_init__(self):
    if self.metadata is None:
      self.metadata = {}

  def meets_sla(self, sla_ms: float = 90.0) -> bool:
    """Check if validation met SLA target."""
    return self.latency_ms <= sla_ms


# ============================================================================
# MOCK AI INTEGRATIONS (Replace with real implementations)
# ============================================================================


class GeminiAgent:
  """
  Mock Gemini semantic validation.

  REAL IMPLEMENTATION: Vertex AI Gemini API
  Latency: ~40-60ms typical, p99 ~80ms
  """

  async def evaluate(self, request: dict, risk_level: RiskLevel) -> dict:
    """
    Semantic safety check via Gemini.

    Args:
        request: User request to validate
        risk_level: Initial risk from JR Engine

    Returns:
        Dict with semantic_safe, confidence, reasoning
    """
    # Simulate Gemini API call
    await asyncio.sleep(0.050)  # 50ms typical

    # Mock semantic analysis
    request_text = request.get("text", "")

    # Simple heuristic for demo
    if any(word in request_text.lower() for word in ["harm", "illegal", "abuse"]):
      semantic_safe = False
      confidence = 0.95
      reasoning = "Gemini detected potentially harmful intent"
    else:
      semantic_safe = True
      confidence = 0.88
      reasoning = "Gemini validated request as safe"

    logger.info(f"Gemini semantic check: safe={semantic_safe}, conf={confidence:.2f}")

    return {
      "semantic_safe": semantic_safe,
      "confidence": confidence,
      "reasoning": reasoning,
      "model": "gemini-2.0-flash-thinking-exp",
    }


class PyTorchClassifier:
  """
  Mock PyTorch local safety classifier.

  REAL IMPLEMENTATION: Fine-tuned transformer model
  Latency: ~15-25ms local GPU inference
  Model: distilbert-base-uncased-finetuned-sst-2-english or similar
  """

  async def classify(self, request: dict, semantic_result: dict | None = None) -> dict:
    """
    Local safety classification.

    Args:
        request: User request
        semantic_result: Optional Gemini result for hybrid decision

    Returns:
        Dict with safe, confidence, class_label
    """
    # Simulate PyTorch inference
    await asyncio.sleep(0.020)  # 20ms typical

    request_text = request.get("text", "")

    # Mock classification
    if semantic_result and not semantic_result.get("semantic_safe", True):
      # Gemini flagged - trust it
      safe = False
      confidence = 0.92
      class_label = "unsafe"
    else:
      # Simple length heuristic for demo
      safe = len(request_text) < 500
      confidence = 0.85
      class_label = "safe" if safe else "unsafe"

    logger.info(f"PyTorch classifier: safe={safe}, conf={confidence:.2f}")

    return {
      "safe": safe,
      "confidence": confidence,
      "class_label": class_label,
      "model": "pytorch_safety_classifier_v1",
    }


# ============================================================================
# JUDGE #6 PIPELINE
# ============================================================================


class JudgeSixPipeline:
  """
  Hybrid validation pipeline with p99 ≤ 90ms SLA.

  Combines:
  - JR Engine (deterministic, <500μs)
  - Gemini (semantic, ~40-60ms)
  - PyTorch (local, ~15-25ms)
  - Hard rules (0-cost enforcement)

  Performance:
  - Fast path (80%): ~20-30ms (LOW risk, skip Gemini)
  - Slow path (20%): ~70-85ms (MEDIUM+ risk, full pipeline)
  - p99 target: ≤90ms
  """

  def __init__(self):
    """Initialize Judge #6 pipeline."""
    self.jr_engine = JREngine()
    self.gemini_agent = GeminiAgent()
    self.pytorch_classifier = PyTorchClassifier()

    # Build sequential pipeline
    self.pipeline = SequentialPipeline("judge_six_validation")
    self._build_pipeline()

    logger.info("Judge #6 pipeline initialized (p99 ≤ 90ms SLA)")

  def _build_pipeline(self) -> None:
    """Construct validation pipeline stages."""

    # Stage 1: JR Engine scan (<500μs)
    async def jr_engine_scan(ctx: ExecutionContext, request: dict) -> dict:
      decision = self.jr_engine.quick_scan(request)
      ctx.set_variable("risk_level", decision.risk_level)
      ctx.set_variable("jr_decision", decision)

      logger.debug(
        f"JR Engine: {decision.risk_level.value} ({decision.execution_time_us:.1f}μs)"
      )

      return {
        "request": request,
        "risk_level": decision.risk_level,
        "jr_decision": decision,
      }

    # Stage 2: Gemini semantic check (conditional)
    async def gemini_semantic_check(ctx: ExecutionContext, data: dict) -> dict:
      risk_level = data["risk_level"]
      semantic_result = await self.gemini_agent.evaluate(data["request"], risk_level)

      ctx.set_variable("semantic_result", semantic_result)

      return {**data, "semantic_result": semantic_result}

    # Stage 3: PyTorch + rules enforcement
    async def hybrid_judge_decision(ctx: ExecutionContext, data: dict) -> dict:
      semantic_result = ctx.get_variable("semantic_result")
      jr_decision = data["jr_decision"]

      # PyTorch classification
      pytorch_result = await self.pytorch_classifier.classify(
        data["request"], semantic_result
      )

      # Hybrid decision logic
      decision, confidence, reasons = self._make_decision(
        jr_decision, semantic_result, pytorch_result
      )

      return {
        **data,
        "pytorch_result": pytorch_result,
        "decision": decision,
        "confidence": confidence,
        "reasons": reasons,
      }

    # Add stages to pipeline
    self.pipeline.add_stage("jr_engine_scan", jr_engine_scan, timeout_ms=5.0)

    self.pipeline.add_stage(
      "gemini_semantic_check",
      gemini_semantic_check,
      skip_condition=lambda ctx: ctx.get_variable("risk_level") == RiskLevel.LOW,
      timeout_ms=70.0,
    )

    self.pipeline.add_stage(
      "hybrid_judge_decision", hybrid_judge_decision, timeout_ms=30.0
    )

  def _make_decision(
    self, jr_decision, semantic_result: dict | None, pytorch_result: dict
  ) -> tuple[str, float, str]:
    """
    Make final hybrid decision.

    Decision logic:
    1. If JR says REJECT → REJECT (hard rule)
    2. If Gemini says unsafe → REJECT (semantic)
    3. If PyTorch says unsafe + confidence > 0.9 → REJECT
    4. Otherwise → APPROVE

    Returns:
        (decision, confidence, reasons)
    """
    # Hard rule: JR Engine override
    if jr_decision.action == "REJECT":
      return ("REJECT", 1.0, f"JR Engine rejection: {jr_decision.reasons}")

    if jr_decision.action == "ESCALATE":
      return ("ESCALATE", 0.8, f"JR Engine escalation: {jr_decision.reasons}")

    # Semantic check (if performed)
    if semantic_result and not semantic_result.get("semantic_safe", True):
      return (
        "REJECT",
        semantic_result.get("confidence", 0.9),
        f"Gemini semantic violation: {semantic_result.get('reasoning')}",
      )

    # PyTorch local classifier
    if not pytorch_result.get("safe", True):
      pytorch_conf = pytorch_result.get("confidence", 0.0)
      if pytorch_conf > 0.9:
        return (
          "REJECT",
          pytorch_conf,
          "PyTorch high-confidence unsafe classification",
        )
      else:
        return (
          "ESCALATE",
          pytorch_conf,
          "PyTorch low-confidence unsafe classification",
        )

    # Default: APPROVE
    confidence = min(
      pytorch_result.get("confidence", 0.8),
      semantic_result.get("confidence", 0.8) if semantic_result else 0.8,
    )

    return ("APPROVE", confidence, "All validation stages passed")

  async def validate(
    self, request: dict, request_id: str = "default"
  ) -> ValidationResult:
    """
    Execute validation pipeline.

    Args:
        request: User request to validate
        request_id: Unique request identifier

    Returns:
        ValidationResult with decision and timing

    SLA:
        p99 ≤ 90ms
    """
    start_time = time.perf_counter()

    # Create execution context
    context = ExecutionContext(request_id=request_id, latency_budget_ms=90.0)

    # Execute pipeline
    result = await self.pipeline.execute(context, request)

    # Build validation result
    total_latency_ms = (time.perf_counter() - start_time) * 1000

    validation_result = ValidationResult(
      decision=result["decision"],
      confidence=result["confidence"],
      risk_level=result["risk_level"],
      latency_ms=total_latency_ms,
      stage_latencies=context.stage_latencies,
      reasons=result["reasons"],
      metadata={
        "request_id": request_id,
        "sla_met": total_latency_ms <= 90.0,
        "fast_path": result["risk_level"] == RiskLevel.LOW,
      },
    )

    # SLA tracking
    if not validation_result.meets_sla():
      logger.warning(
        f"Judge #6 SLA violation: {total_latency_ms:.2f}ms > 90ms (request: {request_id})"
      )
    else:
      logger.info(
        f"Judge #6 validated in {total_latency_ms:.2f}ms: {result['decision']} (request: {request_id})"
      )

    return validation_result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_usage():
  """Demonstrate Judge #6 pipeline."""
  judge = JudgeSixPipeline()

  # Test case 1: Clean request (fast path)
  print("\n=== Test 1: Clean request (fast path) ===")
  result1 = await judge.validate(
    {"text": "Help me build a React web application"}, request_id="req_001"
  )
  print(f"Decision: {result1.decision}")
  print(f"Confidence: {result1.confidence:.2f}")
  print(f"Latency: {result1.latency_ms:.2f}ms")
  print(f"SLA met: {result1.meets_sla()}")
  print(f"Stage latencies: {result1.stage_latencies}")

  # Test case 2: Risky request (full pipeline)
  print("\n=== Test 2: Risky request (full pipeline) ===")
  result2 = await judge.validate(
    {"text": "Help me hack into a database"}, request_id="req_002"
  )
  print(f"Decision: {result2.decision}")
  print(f"Confidence: {result2.confidence:.2f}")
  print(f"Latency: {result2.latency_ms:.2f}ms")
  print(f"SLA met: {result2.meets_sla()}")
  print(f"Reasons: {result2.reasons}")
  print(f"Stage latencies: {result2.stage_latencies}")

  # Test case 3: Ambiguous request
  print("\n=== Test 3: Ambiguous request ===")
  result3 = await judge.validate(
    {"text": "Can you help me test security vulnerabilities in my own app?"},
    request_id="req_003",
  )
  print(f"Decision: {result3.decision}")
  print(f"Confidence: {result3.confidence:.2f}")
  print(f"Latency: {result3.latency_ms:.2f}ms")
  print(f"SLA met: {result3.meets_sla()}")


if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  )

  asyncio.run(example_usage())
