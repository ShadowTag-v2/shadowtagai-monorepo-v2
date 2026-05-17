"""MONTE CARLO RISK ASSESSMENT - Concurrent Execution Pattern
===========================================================

SK PATTERN 2: Concurrent Execution

Runs 5 ATP 5-19 probability models in parallel:
- Probability A (Frequent)
- Probability B (Likely)
- Probability C (Occasional)
- Probability D (Seldom)
- Probability E (Unlikely)

Each model scores severity (I-IV), then aggregate via ATP 5-19 matrix.

PERFORMANCE TARGET: <500μs total (parallel execution)
BENEFIT: Parallel execution vs sequential saves ~400μs

ARCHITECTURE:
------------
┌────────────────────────────────────────┐
│  Monte Carlo Risk Assessment           │
└────┬───────────────────────────────────┘
     │
     ├─► Model A (Frequent)    │
     ├─► Model B (Likely)      │ AsyncIO
     ├─► Model C (Occasional)  │ gather()
     ├─► Model D (Seldom)      │ <500μs
     ├─► Model E (Unlikely)    │
     │
     └─► Aggregate → Risk Level

Author: Pnkln Architecture Team
Version: 1.0.0
License: Proprietary
"""

import asyncio
import logging
import time
from dataclasses import dataclass

from pnkln.core.jr_engine import JREngine, ProbabilityLevel, RiskLevel, SeverityLevel

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class ProbabilityModelResult:
  """Result from single probability model."""

  probability_level: ProbabilityLevel
  severity_level: SeverityLevel
  score: float  # 0.0-1.0 confidence
  evidence: str


@dataclass
class MonteCarloResult:
  """Aggregated Monte Carlo risk assessment."""

  final_risk_level: RiskLevel
  probability_distribution: dict[ProbabilityLevel, float]
  severity_distribution: dict[SeverityLevel, float]
  selected_probability: ProbabilityLevel
  selected_severity: SeverityLevel
  execution_time_us: float
  model_results: list[ProbabilityModelResult]
  metadata: dict = None

  def __post_init__(self):
    if self.metadata is None:
      self.metadata = {}


# ============================================================================
# PROBABILITY MODELS
# ============================================================================


class ProbabilityModelA:
  """Model A: Frequent events (>1 per week).

  Evaluates if decision could lead to frequent negative outcomes.
  """

  async def evaluate(self, decision: dict) -> ProbabilityModelResult:
    """Evaluate frequency probability."""
    await asyncio.sleep(0.0001)  # 100μs simulation

    decision_text = decision.get("text", "").lower()

    # Simple heuristic: certain keywords indicate high frequency risk
    high_freq_keywords = ["always", "constantly", "repeatedly", "every time"]
    score = sum(1 for kw in high_freq_keywords if kw in decision_text) / len(
      high_freq_keywords
    )

    if score > 0.5:
      severity = SeverityLevel.III_MODERATE
      evidence = "Decision likely to cause frequent moderate issues"
    else:
      severity = SeverityLevel.IV_NEGLIGIBLE
      evidence = "Low frequency risk detected"

    return ProbabilityModelResult(
      probability_level=ProbabilityLevel.A_FREQUENT,
      severity_level=severity,
      score=score,
      evidence=evidence,
    )


class ProbabilityModelB:
  """Model B: Likely events (1 per month - 1 per year)."""

  async def evaluate(self, decision: dict) -> ProbabilityModelResult:
    """Evaluate likely probability."""
    await asyncio.sleep(0.0001)  # 100μs simulation

    decision_text = decision.get("text", "").lower()

    # Heuristic: moderate risk keywords
    likely_keywords = ["sometimes", "occasionally", "often"]
    score = sum(1 for kw in likely_keywords if kw in decision_text) / max(
      len(likely_keywords),
      1,
    )

    severity = (
      SeverityLevel.III_MODERATE if score > 0.3 else SeverityLevel.IV_NEGLIGIBLE
    )
    evidence = f"Likely probability score: {score:.2f}"

    return ProbabilityModelResult(
      probability_level=ProbabilityLevel.B_LIKELY,
      severity_level=severity,
      score=score,
      evidence=evidence,
    )


class ProbabilityModelC:
  """Model C: Occasional events (1 per 1-3 years)."""

  async def evaluate(self, decision: dict) -> ProbabilityModelResult:
    """Evaluate occasional probability."""
    await asyncio.sleep(0.0001)  # 100μs simulation

    decision_text = decision.get("text", "").lower()

    # Heuristic: rare but possible
    occasional_keywords = ["maybe", "possible", "could"]
    score = sum(1 for kw in occasional_keywords if kw in decision_text) / max(
      len(occasional_keywords),
      1,
    )

    severity = (
      SeverityLevel.III_MODERATE if score > 0.4 else SeverityLevel.IV_NEGLIGIBLE
    )
    evidence = f"Occasional probability score: {score:.2f}"

    return ProbabilityModelResult(
      probability_level=ProbabilityLevel.C_OCCASIONAL,
      severity_level=severity,
      score=score,
      evidence=evidence,
    )


class ProbabilityModelD:
  """Model D: Seldom events (1 per 10 years)."""

  async def evaluate(self, decision: dict) -> ProbabilityModelResult:
    """Evaluate seldom probability."""
    await asyncio.sleep(0.0001)  # 100μs simulation

    decision_text = decision.get("text", "").lower()

    # Heuristic: very rare indicators
    seldom_keywords = ["rarely", "unlikely", "uncommon"]
    score = sum(1 for kw in seldom_keywords if kw in decision_text) / max(
      len(seldom_keywords),
      1,
    )

    severity = SeverityLevel.IV_NEGLIGIBLE
    evidence = f"Seldom probability score: {score:.2f}"

    return ProbabilityModelResult(
      probability_level=ProbabilityLevel.D_SELDOM,
      severity_level=severity,
      score=score,
      evidence=evidence,
    )


class ProbabilityModelE:
  """Model E: Unlikely events (<1 per 10 years)."""

  async def evaluate(self, decision: dict) -> ProbabilityModelResult:
    """Evaluate unlikely probability."""
    await asyncio.sleep(0.0001)  # 100μs simulation

    decision_text = decision.get("text", "").lower()

    # Heuristic: extremely rare
    unlikely_keywords = ["never", "impossible", "won't happen"]
    score = sum(1 for kw in unlikely_keywords if kw in decision_text) / max(
      len(unlikely_keywords),
      1,
    )

    severity = SeverityLevel.IV_NEGLIGIBLE
    evidence = f"Unlikely probability score: {score:.2f}"

    return ProbabilityModelResult(
      probability_level=ProbabilityLevel.E_UNLIKELY,
      severity_level=severity,
      score=score,
      evidence=evidence,
    )


# ============================================================================
# MONTE CARLO RISK ASSESSMENT
# ============================================================================


class MonteCarloRiskAssessment:
  """Concurrent probability assessment using 5 parallel models.

  SK Pattern: Concurrent Execution
  Performance: <500μs for all 5 models via AsyncIO gather()

  Decision Flow:
  1. Run 5 probability models in parallel
  2. Each model scores severity (I-IV)
  3. Aggregate scores to select most likely probability
  4. Combine with severity via ATP 5-19 matrix
  5. Return final risk level
  """

  def __init__(self):
    """Initialize Monte Carlo assessment."""
    self.jr_engine = JREngine()
    self.models = {
      ProbabilityLevel.A_FREQUENT: ProbabilityModelA(),
      ProbabilityLevel.B_LIKELY: ProbabilityModelB(),
      ProbabilityLevel.C_OCCASIONAL: ProbabilityModelC(),
      ProbabilityLevel.D_SELDOM: ProbabilityModelD(),
      ProbabilityLevel.E_UNLIKELY: ProbabilityModelE(),
    }

    logger.info("Monte Carlo Risk Assessment initialized (5 models)")

  async def evaluate_scenarios(self, decision: dict) -> MonteCarloResult:
    """Run all 5 probability models in parallel.

    Args:
        decision: Decision to assess

    Returns:
        MonteCarloResult with aggregated risk level

    Performance:
        Target <500μs total execution

    """
    start_time = time.perf_counter()

    # Execute all models concurrently
    tasks = [model.evaluate(decision) for model in self.models.values()]

    model_results = await asyncio.gather(*tasks)

    # Calculate probability distribution
    probability_dist = {}
    for result in model_results:
      probability_dist[result.probability_level] = result.score

    # Calculate severity distribution
    severity_dist = {}
    for result in model_results:
      severity_level = result.severity_level
      if severity_level not in severity_dist:
        severity_dist[severity_level] = 0.0
      severity_dist[severity_level] += result.score

    # Select most likely probability (highest score)
    selected_probability = max(
      probability_dist.keys(), key=lambda p: probability_dist[p]
    )

    # Select most severe severity (weighted)
    selected_severity = max(severity_dist.keys(), key=lambda s: severity_dist[s])

    # Get final risk level from ATP 5-19 matrix
    final_risk_level = self.jr_engine.assess_risk(
      selected_probability, selected_severity
    )

    execution_time_us = (time.perf_counter() - start_time) * 1_000_000

    result = MonteCarloResult(
      final_risk_level=final_risk_level,
      probability_distribution=probability_dist,
      severity_distribution=severity_dist,
      selected_probability=selected_probability,
      selected_severity=selected_severity,
      execution_time_us=execution_time_us,
      model_results=model_results,
      metadata={"num_models": len(model_results), "target_us": 500},
    )

    # Performance tracking
    if execution_time_us > 500:
      logger.warning(f"Monte Carlo exceeded 500μs target: {execution_time_us:.1f}μs")
    else:
      logger.info(
        f"Monte Carlo completed in {execution_time_us:.1f}μs: "
        f"{final_risk_level.value} "
        f"({selected_probability.value} × {selected_severity.value})",
      )

    return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_usage():
  """Demonstrate Monte Carlo risk assessment."""
  assessor = MonteCarloRiskAssessment()

  # Test case 1: Low risk decision
  print("\n=== Test 1: Low risk decision ===")
  decision1 = {"text": "Deploy code change to staging environment for testing"}
  result1 = await assessor.evaluate_scenarios(decision1)
  print(f"Risk Level: {result1.final_risk_level.value}")
  print(f"Probability: {result1.selected_probability.value}")
  print(f"Severity: {result1.selected_severity.value}")
  print(f"Execution Time: {result1.execution_time_us:.1f}μs")
  print(f"Probability Distribution: {result1.probability_distribution}")

  # Test case 2: Higher risk decision
  print("\n=== Test 2: Higher risk decision ===")
  decision2 = {
    "text": "This change will constantly affect production systems repeatedly every time",
  }
  result2 = await assessor.evaluate_scenarios(decision2)
  print(f"Risk Level: {result2.final_risk_level.value}")
  print(f"Probability: {result2.selected_probability.value}")
  print(f"Severity: {result2.selected_severity.value}")
  print(f"Execution Time: {result2.execution_time_us:.1f}μs")

  # Test case 3: Batch evaluation (demonstrate parallel efficiency)
  print("\n=== Test 3: Batch evaluation (5 decisions) ===")
  decisions = [{"text": f"Decision {i} with various risk levels"} for i in range(5)]

  batch_start = time.perf_counter()
  batch_results = await asyncio.gather(
    *[assessor.evaluate_scenarios(d) for d in decisions]
  )
  batch_time_us = (time.perf_counter() - batch_start) * 1_000_000

  print(f"Batch of 5 completed in {batch_time_us:.1f}μs")
  print(f"Average per decision: {batch_time_us / 5:.1f}μs")
  for i, result in enumerate(batch_results):
    print(
      f"  Decision {i}: {result.final_risk_level.value} ({result.execution_time_us:.1f}μs)"
    )


if __name__ == "__main__":
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  )

  asyncio.run(example_usage())
