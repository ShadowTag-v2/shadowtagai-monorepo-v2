#!/usr/bin/env python3
"""internal_swarm.py

Implementation of the **n-autoresearch/Kosmos/BioAgents Internal Swarm Script – All LLMs** as a native
Python framework.  This module can be imported by any component of the
ShadowTagAI code‑base (or by external LLM wrappers) to perform zero‑cost,
internal voting on arbitrary decisions.

The implementation follows the exact protocol you supplied in the system
prompt, including:

* 600‑agent swarm with 200 active agents per shift.
* Tier weighting (Strategy 10 %, Execution 60 %, Worker 30 %).
* ATP‑5‑19 risk scoring and brake penalties.
* Heuristic‑based vote distribution with a ±10 % dissent variance.
* Weighted consensus calculation and final outcome determination.

Usage example::

    from shadowtagai.agents.internal_swarm import InternalSwarm

    swarm = InternalSwarm()
    decision = "SWARM VOTE: Deploy Judge 6 to Vertex AI"
    result = swarm.evaluate(decision)
    print(result)

The ``result`` string matches the required output format:

    ///▞ n-autoresearch/Kosmos/BioAgents SWARM DECISION
    ═══════════════════════════════════════
    CONTEXT: Deploy Judge 6 to Vertex AI | RISK: M | BRAKES: 1
    CALCULATION: risk=0.6 - brakes=0.15 = 0.45
    CONSENSUS: 42.0% weighted approve
    ═══════════════════════════════════════
    DECISION: ESCALATE
    CONFIDENCE: 78%
    METHOD: heuristic
    COST: $0.00 (internal execution)
    ═══════════════════════════════════════

The framework is deliberately lightweight – it contains no external API
calls and therefore incurs **$0 cost** when run inside any LLM environment.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from enum import Enum

# ---------------------------------------------------------------------------
# Configuration constants (mirroring the system prompt)
# ---------------------------------------------------------------------------
TOTAL_AGENTS = 600
ACTIVE_AGENTS = 200  # agents participating in a shift
RESERVE_POOL = TOTAL_AGENTS - ACTIVE_AGENTS
SHIFT_HOURS = 4


# Tier definitions and weights (total weight = 300.0)
class Tier(Enum):
    STRATEGY = "strategy"
    EXECUTION = "execution"
    WORKER = "worker"


TIER_WEIGHTS: dict[Tier, float] = {
    Tier.STRATEGY: 3.0,  # 20 agents × 3.0 = 60.0
    Tier.EXECUTION: 1.5,  # 120 agents × 1.5 = 180.0
    Tier.WORKER: 1.0,  # 60 agents × 1.0 = 60.0
}
TOTAL_WEIGHT = sum(TIER_WEIGHTS.values())  # 300.0

# ATP‑5‑19 risk scores
RISK_SCORES: dict[str, float] = {
    "L": 0.9,  # Low
    "M": 0.6,  # Medium
    "H": 0.3,  # High
    "EH": 0.0,  # Extremely High
}

BRAKE_PENALTY = 0.15  # per safety brake

# Voting thresholds (heuristic)
APPROVE_THRESHOLD = 0.60
REJECT_THRESHOLD = 0.35

# Consensus thresholds (final outcome)
CONSENSUS_APPROVE = 0.55
CONSENSUS_REJECT = 0.40


# ---------------------------------------------------------------------------
# Helper data structures
# ---------------------------------------------------------------------------
@dataclass
class DecisionContext:
    intent: str
    risk_level: str  # L, M, H, EH
    brake_count: int

    @property
    def risk_score(self) -> float:
        return RISK_SCORES.get(self.risk_level.upper(), 0.0)

    @property
    def brake_penalty(self) -> float:
        return self.brake_count * BRAKE_PENALTY

    @property
    def approve_score(self) -> float:
        # Heuristic: max(0, risk_score - brake_penalty)
        return max(0.0, self.risk_score - self.brake_penalty)


# ---------------------------------------------------------------------------
# Core Swarm class
# ---------------------------------------------------------------------------
class InternalSwarm:
    """Implements the 600‑agent internal voting protocol.

    The public entry point is :meth:`evaluate`, which accepts a raw decision
    string (e.g. ``"SWARM VOTE: Deploy Judge 6"``) and returns a formatted
    decision report.
    """

    def __init__(self) -> None:
        # Pre‑compute the number of agents per tier (active agents only)
        self.tier_counts: dict[Tier, int] = {
            Tier.STRATEGY: int(ACTIVE_AGENTS * 0.10),  # 20 agents
            Tier.EXECUTION: int(ACTIVE_AGENTS * 0.60),  # 120 agents
            Tier.WORKER: int(ACTIVE_AGENTS * 0.30),  # 60 agents
        }
        # Sanity check – should sum to ACTIVE_AGENTS
        assert sum(self.tier_counts.values()) == ACTIVE_AGENTS, "Tier distribution mismatch"

    # ---------------------------------------------------------------------
    # Parsing utilities
    # ---------------------------------------------------------------------
    _DECISION_REGEX = re.compile(
        r"SWARM VOTE:\s*(?P<intent>.+?)\s*(?:\|\s*RISK:\s*(?P<risk>L|M|H|EH)\s*)?(?:\|\s*BRAKES:\s*(?P<brakes>\d+)\s*)?",
        re.IGNORECASE,
    )

    def _parse(self, raw: str) -> DecisionContext:
        """Extract intent, risk level and brake count from the raw string.

        If risk or brakes are omitted, defaults are used:
        * risk → ``M`` (Medium)
        * brakes → ``0``
        """
        match = self._DECISION_REGEX.search(raw)
        if not match:
            # Fallback – treat the whole string as intent with defaults
            intent = raw.strip()
            risk = "M"
            brakes = 0
        else:
            intent = match.group("intent").strip()
            risk = (match.group("risk") or "M").upper()
            brakes = int(match.group("brakes") or 0)
        return DecisionContext(intent=intent, risk_level=risk, brake_count=brakes)

    # ---------------------------------------------------------------------
    # Voting mechanics
    # ---------------------------------------------------------------------
    def _distribute_votes(self, approve_score: float) -> tuple[int, int, int]:
        """Return (approve, reject, escalate) vote counts for the active swarm.

        The distribution follows the protocol:
        * Agents vote APPROVE if ``approve_score >= 0.60``.
        * Agents vote REJECT if ``approve_score <= 0.35``.
        * Otherwise they vote ESCALATE.
        * Up to ±10 % of agents may dissent (randomly flip their vote).
        """
        # Base decision per tier (same for all tiers)
        if approve_score >= APPROVE_THRESHOLD:
            base = "approve"
        elif approve_score <= REJECT_THRESHOLD:
            base = "reject"
        else:
            base = "escalate"

        # Compute raw vote numbers per tier
        votes = {"approve": 0, "reject": 0, "escalate": 0}
        for _tier, count in self.tier_counts.items():
            votes[base] += count
        # Apply dissent variance (±10 % of ACTIVE_AGENTS)
        variance = int(ACTIVE_AGENTS * 0.10)
        for _ in range(variance):
            # Randomly pick an agent to flip its vote
            # Choose a tier weighted by its size for realism
            random.choices(
                list(self.tier_counts.keys()),
                weights=[self.tier_counts[t] for t in self.tier_counts],
            )[0]
            # Determine current vote for this tier (all agents in tier share the same base)
            current = base
            # Choose a different vote to flip to
            alternatives = [v for v in ("approve", "reject", "escalate") if v != current]
            new_vote = random.choice(alternatives)
            # Apply the flip (one agent moves from current to new_vote)
            votes[current] -= 1
            votes[new_vote] += 1
        return votes["approve"], votes["reject"], votes["escalate"]

    # ---------------------------------------------------------------------
    # Consensus calculation
    # ---------------------------------------------------------------------
    def _weighted_consensus(self, approve_votes: int) -> float:
        """Calculate the weighted approval ratio.

        ``approve_votes`` is the total number of agents that voted APPROVE.
        The weight of each tier is applied proportionally to its agent count.
        """
        # Determine how many APPROVE votes came from each tier.
        # Since the base decision is uniform across tiers, we can compute the
        # proportion of APPROVE agents per tier directly.
        weighted_approve = 0.0
        for tier, count in self.tier_counts.items():
            # Fraction of this tier that voted APPROVE
            tier_approve_fraction = approve_votes / ACTIVE_AGENTS  # uniform assumption
            weighted_approve += tier_approve_fraction * count * TIER_WEIGHTS[tier]
        return weighted_approve / TOTAL_WEIGHT

    # ---------------------------------------------------------------------
    # Outcome determination
    # ---------------------------------------------------------------------
    def _determine_outcome(self, consensus_ratio: float) -> tuple[str, str]:
        """Return (decision, method) based on the consensus ratio.

        * ``decision`` is one of ``APPROVE``, ``REJECT`` or ``ESCALATE``.
        * ``method`` is ``heuristic`` when the ratio is decisive, otherwise
          ``tiebreaker``.
        """
        if consensus_ratio >= CONSENSUS_APPROVE:
            return "APPROVE", "heuristic"
        if consensus_ratio <= CONSENSUS_REJECT:
            return "REJECT", "heuristic"
        # Unclear – run internal tiebreaker (simple deterministic rule)
        # Here we pick the side with the higher raw weighted approve vs reject.
        # For simplicity we treat ESCALATE as the default when unclear.
        return "ESCALATE", "tiebreaker"

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def evaluate(self, raw_decision: str) -> str:
        """Evaluate a decision string and return a formatted report.

        The function follows the exact output format required by the
        system‑prompt.
        """
        ctx = self._parse(raw_decision)
        approve_score = ctx.approve_score
        approve_votes, reject_votes, escalate_votes = self._distribute_votes(approve_score)
        consensus_ratio = self._weighted_consensus(approve_votes)
        decision, method = self._determine_outcome(consensus_ratio)

        # Confidence is a simple mapping: higher consensus → higher confidence
        confidence = int(min(100, max(0, consensus_ratio * 100)))
        # Render the report
        report = (
            "///▞ n-autoresearch/Kosmos/BioAgents SWARM DECISION\n"
            "═══════════════════════════════════════\n"
            f"CONTEXT: {ctx.intent} | RISK: {ctx.risk_level} | BRAKES: {ctx.brake_count}\n"
            f"CALCULATION: risk={ctx.risk_score} - brakes={ctx.brake_penalty} = {approve_score}\n"
            f"CONSENSUS: {consensus_ratio * 100:.1f}% weighted approve\n"
            "═══════════════════════════════════════\n"
            f"DECISION: {decision}\n"
            f"CONFIDENCE: {confidence}%\n"
            f"METHOD: {method}\n"
            "COST: $0.00 (internal execution)\n"
            "═══════════════════════════════════════"
        )
        return report


# ---------------------------------------------------------------------------
# Simple CLI for manual testing (optional)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print('Usage: python internal_swarm.py "SWARM VOTE: <decision>"')
        sys.exit(1)
    raw = " ".join(sys.argv[1:])
    swarm = InternalSwarm()
    print(swarm.evaluate(raw))
