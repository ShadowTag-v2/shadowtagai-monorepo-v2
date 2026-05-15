"""
agents.autoresearch2 — Swarm voting primitives.

Provides ATP 5-19 heuristic voting used by:
  - api/swarm_endpoint.py  (SwarmVoter, swarm_vote, VoteDecision)
  - tools/swarm_tools.py   (execute_internal_swarm)

The AgentOrchestrator governance layer lives in pnkln.agents.
This module is the lightweight, import-safe voting kernel that
can be imported without loading the full orchestrator stack.
"""

import time
from dataclasses import dataclass
from enum import StrEnum

# =============================================================================
# ENUMS
# =============================================================================


class Decision(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


class RiskLevel(StrEnum):
    LOW = "L"
    MEDIUM = "M"
    HIGH = "H"
    EXTREMELY_HIGH = "EH"


class VoteMethod(StrEnum):
    HEURISTIC = "heuristic"
    TIEBREAKER = "tiebreaker"


# =============================================================================
# CONSTANTS (ATP 5-19)
# =============================================================================

_ATP_5_19_RISK_SCORES = {
    RiskLevel.LOW: 0.9,
    RiskLevel.MEDIUM: 0.6,
    RiskLevel.HIGH: 0.3,
    RiskLevel.EXTREMELY_HIGH: 0.0,
}
_BRAKE_PENALTY = 0.15
_APPROVE_THRESHOLD = 0.55
_REJECT_THRESHOLD = 0.40

# Agent tier weights (strategy × 3, execution × 1.5, worker × 1)
_STRATEGY_AGENTS = 20
_EXECUTION_AGENTS = 120
_WORKER_AGENTS = 60
_TOTAL_AGENTS = 200
_WEIGHTED_TOTAL = _STRATEGY_AGENTS * 3.0 + _EXECUTION_AGENTS * 1.5 + _WORKER_AGENTS * 1.0


# =============================================================================
# RESULT TYPE
# =============================================================================


@dataclass
class VoteDecision:
    """
    Result of execute_internal_swarm / SwarmVoter.vote().

    Attributes match what tools/swarm_tools.swarm_vote() reads:
        result.decision, result.confidence, result.method,
        result.strategy_votes, result.execution_votes, result.worker_votes
    """

    decision: Decision
    confidence: float
    method: VoteMethod
    strategy_votes: int
    execution_votes: int
    worker_votes: int
    consensus_ratio: float
    total_votes: int
    weighted_approve: float
    weighted_total: float
    risk_score: float
    brake_penalty: float
    approve_score: float
    latency_ms: float


# =============================================================================
# CORE FUNCTION
# =============================================================================


def execute_internal_swarm(
    intent: str,
    risk_level: RiskLevel | str = RiskLevel.MEDIUM,
    brake_count: int = 0,
) -> VoteDecision:
    """
    Execute swarm voting via ATP 5-19 heuristic (no LLM calls, $0 cost).

    Args:
        intent:      Description of the action being voted on.
        risk_level:  RiskLevel enum or string ("L", "M", "H", "EH").
        brake_count: Number of safety brakes triggered.

    Returns:
        VoteDecision with APPROVE / REJECT / ESCALATE.
    """
    start = time.perf_counter()

    if isinstance(risk_level, str):
        risk_level = RiskLevel(risk_level)

    risk_score = _ATP_5_19_RISK_SCORES[risk_level]
    brake_penalty = brake_count * _BRAKE_PENALTY
    approve_score = max(0.0, risk_score - brake_penalty)

    # Agent-level vote
    if approve_score >= 0.60:
        agent_decision = Decision.APPROVE
    elif approve_score <= 0.35:
        agent_decision = Decision.REJECT
    else:
        agent_decision = Decision.ESCALATE

    # Weighted tallies
    if agent_decision == Decision.APPROVE:
        weighted_approve = _STRATEGY_AGENTS * 3.0 + _EXECUTION_AGENTS * 1.5 + _WORKER_AGENTS * 1.0
    elif agent_decision == Decision.REJECT:
        weighted_approve = 0.0
    else:
        weighted_approve = 144.0  # ~48% → ESCALATE zone

    consensus_ratio = weighted_approve / _WEIGHTED_TOTAL
    method = VoteMethod.HEURISTIC

    # Final decision
    if consensus_ratio >= _APPROVE_THRESHOLD:
        decision = Decision.APPROVE
        confidence = consensus_ratio
    elif consensus_ratio <= _REJECT_THRESHOLD:
        decision = Decision.REJECT
        confidence = 1.0 - consensus_ratio
    else:
        method = VoteMethod.TIEBREAKER
        if risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM) and brake_count <= 1:
            decision = Decision.APPROVE
            confidence = 0.65
        elif brake_count >= 2:
            decision = Decision.REJECT
            confidence = 0.60
        else:
            decision = Decision.ESCALATE
            confidence = 0.50

    latency_ms = (time.perf_counter() - start) * 1000

    return VoteDecision(
        decision=decision,
        confidence=confidence,
        method=method,
        strategy_votes=_STRATEGY_AGENTS,
        execution_votes=_EXECUTION_AGENTS,
        worker_votes=_WORKER_AGENTS,
        consensus_ratio=consensus_ratio,
        total_votes=_TOTAL_AGENTS,
        weighted_approve=weighted_approve,
        weighted_total=_WEIGHTED_TOTAL,
        risk_score=risk_score,
        brake_penalty=brake_penalty,
        approve_score=approve_score,
        latency_ms=latency_ms,
    )


# =============================================================================
# CONVENIENCE WRAPPER
# =============================================================================


class SwarmVoter:
    """
    Thin wrapper around execute_internal_swarm for callers that prefer
    an object interface.

    Usage:
        voter = SwarmVoter()
        result = voter.vote("Deploy to production", risk_level="H", brake_count=1)
    """

    def vote(
        self,
        intent: str,
        risk_level: str = "M",
        brake_count: int = 0,
    ) -> VoteDecision:
        return execute_internal_swarm(
            intent=intent,
            risk_level=risk_level,
            brake_count=brake_count,
        )


def swarm_vote(
    intent: str,
    risk_level: str = "M",
    brake_count: int = 0,
) -> VoteDecision:
    """
    Module-level convenience alias for execute_internal_swarm.
    Imported by api/swarm_endpoint.py (optional — endpoint falls back gracefully).
    """
    return execute_internal_swarm(
        intent=intent,
        risk_level=risk_level,
        brake_count=brake_count,
    )


__all__ = [
    "Decision",
    "RiskLevel",
    "VoteMethod",
    "VoteDecision",
    "SwarmVoter",
    "swarm_vote",
    "execute_internal_swarm",
]
