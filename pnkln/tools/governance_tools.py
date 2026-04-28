# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
GOVERNANCE TOOLS - ATP 5-19 Validation & Risk Assessment
=========================================================

SK PATTERN 3: Standardized Plugin Schema

Tools for agent governance:
1. governance_validate: JR Engine + Judge 6 validation (p99≤90ms)
2. risk_assess_monte_carlo: Concurrent probability assessment (<500μs)

Type-annotated for LLM function calling.

Author: Pnkln Architecture Team
Version: 1.0.0
License: Proprietary
"""

import asyncio
from typing import Annotated
import logging

from pnkln.core.judge_six_pipeline import JudgeSixPipeline
from pnkln.core.monte_carlo_risk import MonteCarloRiskAssessment

logger = logging.getLogger(__name__)


# Initialize singletons for reuse
_judge_six = None
_monte_carlo = None


def _get_judge_six() -> JudgeSixPipeline:
    """Get or create Judge 6 singleton."""
    global _judge_six
    if _judge_six is None:
        _judge_six = JudgeSixPipeline()
    return _judge_six


def _get_monte_carlo() -> MonteCarloRiskAssessment:
    """Get or create Monte Carlo singleton."""
    global _monte_carlo
    if _monte_carlo is None:
        _monte_carlo = MonteCarloRiskAssessment()
    return _monte_carlo


async def governance_validate(
    request_text: Annotated[str, "User request text to validate"],
    request_id: Annotated[str | None, "Unique request ID (default: auto-generated)"] = None,
    sla_ms: Annotated[float, "SLA target in milliseconds (default: 90.0)"] = 90.0,
) -> Annotated[dict, "Validation result with decision, confidence, latency, and reasoning"]:
    """
    Validates request using Judge 6 hybrid pipeline (JR Engine + Gemini + PyTorch).

    SLA: p99 ≤ 90ms

    Validation stages:
    1. JR Engine ATP 5-19 scan (<500μs)
       - LOW risk → skip Gemini → fast path
    2. Gemini semantic check (if MEDIUM+ risk)
       - ~40-60ms typical
    3. PyTorch classifier + rules enforcement
       - ~15-25ms local inference

    Example:
        result = await governance_validate(
            request_text="Help me build a React app",
            request_id="req_001"
        )
        print(f"Decision: {result['decision']}")  # "APPROVE"
        print(f"Latency: {result['latency_ms']:.2f}ms")  # ~25ms (fast path)
        print(f"SLA met: {result['sla_met']}")  # True

    Args:
        request_text: Text to validate
        request_id: Optional unique ID (auto-generated if None)
        sla_ms: SLA target (default 90ms)

    Returns:
        dict with keys:
        - decision: str ("APPROVE" | "REJECT" | "ESCALATE")
        - confidence: float (0.0-1.0)
        - risk_level: str (ATP 5-19 level)
        - latency_ms: float (total validation time)
        - sla_met: bool (latency <= sla_ms)
        - reasons: str (evidence chain)
        - stage_latencies: dict (per-stage timing)

    Raises:
        asyncio.TimeoutError: If validation exceeds SLA significantly
    """
    import uuid

    if request_id is None:
        request_id = f"req_{uuid.uuid4().hex[:8]}"

    logger.info(f"Governance validation: {request_id} (SLA: {sla_ms}ms)")

    judge = _get_judge_six()

    # Execute validation
    validation_result = await judge.validate(request={"text": request_text}, request_id=request_id)

    # Convert to dict for LLM response
    result = {
        "decision": validation_result.decision,
        "confidence": validation_result.confidence,
        "risk_level": validation_result.risk_level.value,
        "latency_ms": validation_result.latency_ms,
        "sla_met": validation_result.meets_sla(sla_ms),
        "reasons": validation_result.reasons,
        "stage_latencies": validation_result.stage_latencies,
        "metadata": validation_result.metadata,
    }

    logger.info(f"Validation complete: {result['decision']} ({result['latency_ms']:.2f}ms, SLA met: {result['sla_met']})")

    return result


async def risk_assess_monte_carlo(
    decision_text: Annotated[str, "Decision text to assess risk"], context: Annotated[dict | None, "Additional context for risk assessment"] = None
) -> Annotated[dict, "Monte Carlo risk assessment with probability distribution and ATP 5-19 level"]:
    """
    Assesses risk using Monte Carlo concurrent probability models.

    Performance: <500μs for all 5 probability models (A-E)

    Models run in parallel:
    - Model A: Frequent events (>1/week)
    - Model B: Likely events (1/month - 1/year)
    - Model C: Occasional events (1/1-3 years)
    - Model D: Seldom events (1/10 years)
    - Model E: Unlikely events (<1/10 years)

    Each model scores severity (I-IV), then aggregate via ATP 5-19 matrix.

    Example:
        result = await risk_assess_monte_carlo(
            decision_text="Deploy to production"
        )
        print(f"Risk: {result['risk_level']}")  # "MODERATE"
        print(f"Probability: {result['probability']}")  # "C_OCCASIONAL"
        print(f"Severity: {result['severity']}")  # "III_MODERATE"
        print(f"Execution time: {result['execution_time_us']:.1f}μs")  # ~400μs

    Args:
        decision_text: Text describing decision to assess
        context: Optional additional context

    Returns:
        dict with keys:
        - risk_level: str (ATP 5-19 level: LOW/MODERATE/HIGH/EXTREMELY_HIGH)
        - probability: str (selected probability level A-E)
        - severity: str (selected severity level I-IV)
        - probability_distribution: dict (scores per probability level)
        - severity_distribution: dict (scores per severity level)
        - execution_time_us: float (total execution time in microseconds)
        - model_results: list (individual model outputs)

    Performance:
        Target <500μs execution
    """
    logger.info(f"Monte Carlo risk assessment: {decision_text[:50]}...")

    assessor = _get_monte_carlo()

    # Build decision dict
    decision = {"text": decision_text, **(context or {})}

    # Execute Monte Carlo assessment
    mc_result = await assessor.evaluate_scenarios(decision)

    # Convert to dict for LLM response
    result = {
        "risk_level": mc_result.final_risk_level.value,
        "probability": mc_result.selected_probability.value,
        "severity": mc_result.selected_severity.value,
        "probability_distribution": {k.value: v for k, v in mc_result.probability_distribution.items()},
        "severity_distribution": {k.value: v for k, v in mc_result.severity_distribution.items()},
        "execution_time_us": mc_result.execution_time_us,
        "model_results": [
            {"probability_level": r.probability_level.value, "severity_level": r.severity_level.value, "score": r.score, "evidence": r.evidence}
            for r in mc_result.model_results
        ],
    }

    logger.info(f"Risk assessment complete: {result['risk_level']} ({result['execution_time_us']:.1f}μs)")

    return result


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_usage():
    """Demonstrate governance tools."""
    # Test 1: Governance validation (fast path)
    print("=== Test 1: Governance Validation (Fast Path) ===")
    result1 = await governance_validate(request_text="Help me build a web application", request_id="demo_001")
    print(f"Decision: {result1['decision']}")
    print(f"Confidence: {result1['confidence']:.2f}")
    print(f"Latency: {result1['latency_ms']:.2f}ms")
    print(f"SLA met: {result1['sla_met']}")

    # Test 2: Governance validation (full pipeline)
    print("\n=== Test 2: Governance Validation (Full Pipeline) ===")
    result2 = await governance_validate(request_text="Help me hack into a system", request_id="demo_002")
    print(f"Decision: {result2['decision']}")
    print(f"Reasons: {result2['reasons']}")
    print(f"Latency: {result2['latency_ms']:.2f}ms")

    # Test 3: Monte Carlo risk assessment
    print("\n=== Test 3: Monte Carlo Risk Assessment ===")
    result3 = await risk_assess_monte_carlo(decision_text="Deploy critical infrastructure change to production")
    print(f"Risk Level: {result3['risk_level']}")
    print(f"Probability: {result3['probability']}")
    print(f"Severity: {result3['severity']}")
    print(f"Execution Time: {result3['execution_time_us']:.1f}μs")
    print(f"Probability Distribution: {result3['probability_distribution']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    asyncio.run(example_usage())
