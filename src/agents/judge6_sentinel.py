# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Judge 6 Sentinel — Post-Triad Governance Gate.

Judge 6 is SEPARATE from the Autoresearch Triad. It receives the
Triad's output and applies governance/risk gating:

  1. ATP 5-19 Risk Classification (CATASTROPHIC → MARGINAL)
  2. 8-Agent Board Synthesis (STATE B decisions only)
  3. ZTA handoff enforcement via Tengu gates
  4. Compliance attestation logging

Judge 6 does NOT modify code. It produces ALLOW/DENY verdicts
with structured rationale for the audit trail.

References:
    - src/governance/j6_csrmc_cato.py (ZTA enforcement)
    - src/gates/tengu_j6_bridge.py (gate integration)
    - TACSOP 6: 8-Agent Board Synthesis
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("judge6-sentinel")


class RiskSeverity(str, Enum):
  """ATP 5-19 Risk Classification levels."""

  CATASTROPHIC = "CATASTROPHIC"
  CRITICAL = "CRITICAL"
  SERIOUS = "SERIOUS"
  MODERATE = "MODERATE"
  MARGINAL = "MARGINAL"


class SentinelVerdict(str, Enum):
  """Judge 6 governance verdict."""

  ALLOW = "ALLOW"
  DENY = "DENY"
  ESCALATE = "ESCALATE"  # Requires human review (STATE B)


@dataclass
class SentinelDecision:
  """A Judge 6 governance decision with full audit trail."""

  decision_id: str
  source: str
  verdict: SentinelVerdict
  risk_severity: RiskSeverity
  rationale: str
  board_synthesis: dict[str, str] | None = None  # 8-agent board (STATE B only)
  metadata: dict[str, Any] = field(default_factory=dict)
  timestamp: float = field(default_factory=time.time)


# ─── Risk Classification Rules ──────────────────────────────────────

_RISK_RULES: list[tuple[str, RiskSeverity]] = [
  ("database migration", RiskSeverity.CATASTROPHIC),
  ("auth change", RiskSeverity.CATASTROPHIC),
  ("payment", RiskSeverity.CATASTROPHIC),
  ("force push", RiskSeverity.CRITICAL),
  ("history rewrite", RiskSeverity.CRITICAL),
  ("architecture shift", RiskSeverity.SERIOUS),
  ("dependency update", RiskSeverity.MODERATE),
  ("refactor", RiskSeverity.MODERATE),
  ("dead code", RiskSeverity.MARGINAL),
  ("type annotation", RiskSeverity.MARGINAL),
]

# ─── 8-Agent Board Roles (STATE B only) ─────────────────────────────

BOARD_ROLES = ("CTO", "DX", "Security", "Finance", "Infra", "QA", "Legal", "UX")


class Judge6Sentinel:
  """Post-Triad governance gate.

  Usage::
      sentinel = Judge6Sentinel()
      decision = sentinel.gate_triad_output(triad_handoff)
      if decision.verdict == SentinelVerdict.ALLOW:
          # Promote mutations to production
      elif decision.verdict == SentinelVerdict.ESCALATE:
          # Enter STATE B — human review required
  """

  def __init__(self) -> None:
    self._decisions: list[SentinelDecision] = []
    self._max_decisions = 200
    logger.info("⚖️ Judge 6 Sentinel initialized")

  def classify_risk(self, description: str) -> RiskSeverity:
    """Classify risk severity using ATP 5-19 rules."""
    desc_lower = description.lower()
    for keyword, severity in _RISK_RULES:
      if keyword in desc_lower:
        return severity
    return RiskSeverity.MARGINAL

  def gate_triad_output(self, handoff: dict[str, Any]) -> SentinelDecision:
    """Apply governance gate to Autoresearch Triad output.

    Args:
        handoff: Output from AutoresearchTriad.get_j6_handoff()
    """
    decision_id = f"j6_{int(time.time() * 1000)}"
    source = handoff.get("source", "unknown")
    # Classify risk from research plan description
    plan = handoff.get("research_plan", {})
    query = plan.get("query", "")
    risk_severity = self.classify_risk(query)

    # Override if Triad flagged regressions
    regressed = handoff.get("mutations_regressed", 0)
    if regressed > 0:
      risk_severity = max(
        risk_severity, RiskSeverity.MODERATE, key=lambda x: list(RiskSeverity).index(x)
      )

    # Determine verdict
    verdict, rationale, board = self._apply_verdict_logic(
      risk_severity, handoff, regressed
    )

    decision = SentinelDecision(
      decision_id=decision_id,
      source=source,
      verdict=verdict,
      risk_severity=risk_severity,
      rationale=rationale,
      board_synthesis=board,
      metadata={"cycle_id": handoff.get("cycle_id"), "query": query},
    )

    if len(self._decisions) >= self._max_decisions:
      self._decisions.pop(0)
    self._decisions.append(decision)

    logger.info(
      "⚖️ J6 Decision %s: %s (risk=%s) — %s",
      decision_id,
      verdict.value,
      risk_severity.value,
      rationale[:80],
    )
    return decision

  def _apply_verdict_logic(
    self,
    risk: RiskSeverity,
    handoff: dict[str, Any],
    regressed: int,
  ) -> tuple[SentinelVerdict, str, dict[str, str] | None]:
    """Core verdict logic."""
    # CATASTROPHIC/CRITICAL → always ESCALATE (STATE B)
    if risk in (RiskSeverity.CATASTROPHIC, RiskSeverity.CRITICAL):
      board = self._synthesize_board(handoff)
      return (
        SentinelVerdict.ESCALATE,
        f"Risk {risk.value} triggers STATE B. 8-Agent Board convened.",
        board,
      )

    # Regressions detected → DENY
    if regressed > 0:
      return (
        SentinelVerdict.DENY,
        f"{regressed} mutations regressed. Rejected per Darwinian fitness gate.",
        None,
      )

    # SERIOUS → ALLOW with warning
    if risk == RiskSeverity.SERIOUS:
      return (
        SentinelVerdict.ALLOW,
        "Risk SERIOUS but no regressions. Proceeding with monitoring.",
        None,
      )

    # MODERATE/MARGINAL → ALLOW
    promoted = handoff.get("mutations_promoted", 0)
    return (
      SentinelVerdict.ALLOW,
      f"{promoted} mutations promoted. Risk {risk.value}. Clean passage.",
      None,
    )

  def _synthesize_board(self, handoff: dict[str, Any]) -> dict[str, str]:
    """8-Agent Board Synthesis for STATE B decisions (TACSOP 6)."""
    query = handoff.get("research_plan", {}).get("query", "")
    return {
      role: f"[{role}] Assessment pending for: {query[:60]}" for role in BOARD_ROLES
    }

  def get_diagnostics(self) -> dict[str, Any]:
    total = len(self._decisions)
    allowed = sum(1 for d in self._decisions if d.verdict == SentinelVerdict.ALLOW)
    denied = sum(1 for d in self._decisions if d.verdict == SentinelVerdict.DENY)
    escalated = sum(1 for d in self._decisions if d.verdict == SentinelVerdict.ESCALATE)
    return {
      "sentinel": "judge6",
      "total_decisions": total,
      "allowed": allowed,
      "denied": denied,
      "escalated": escalated,
      "allow_rate": allowed / total if total > 0 else 0.0,
    }
