# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Autoresearch Triad Orchestrator — Kosmos → BioAgents → n-autoresearch.

Replaces the 28-line stub. Orchestrates the 3-stage pipeline:
  Stage 1: Kosmos (web-grounded research via google-developer-knowledge)
  Stage 2: BioAgents (mutation proposals from research)
  Stage 3: n-autoresearch (Darwinian fitness + promotion)

CRITICAL: Judge 6 is SEPARATE. The Triad feeds INTO Judge 6 after each
cycle. Judge 6 does NOT sit inside the Triad.

References:
    - src/agents/kosmos_agent.py (Stage 1)
    - src/agents/bioagents_agent.py (Stage 2)
    - src/agents/darwinian_engine.py (Fitness scoring)
    - src/agents/judge6_sentinel.py (Post-triad gating)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agents.bioagents_agent import BioAgentsAgent, FitnessVerdict
from agents.darwinian_engine import DarwinianEngine
from agents.kosmos_agent import (
  KosmosAgent,
  ResearchDomain,
  ResearchQuery,
  ResearchResult,
)

logger = logging.getLogger("autoresearch-triad")


@dataclass
class TriadCycleResult:
  """Result of one complete Triad cycle."""

  cycle_id: str
  research_plan: dict[str, Any] = field(default_factory=dict)
  mutation_count: int = 0
  promoted_count: int = 0
  regressed_count: int = 0
  elapsed_ms: float = 0.0
  timestamp: float = field(default_factory=time.time)

  @property
  def promotion_rate(self) -> float:
    if self.mutation_count == 0:
      return 0.0
    return self.promoted_count / self.mutation_count


class AutoresearchTriad:
  """3-stage autoresearch pipeline orchestrator.

  Usage::
      triad = AutoresearchTriad()
      result = triad.execute_cycle(
          question="How to optimize Cloud Run cold starts?",
          domain=ResearchDomain.GOOGLE_CLOUD,
          target_files=["src/server/cloudrun.py"],
      )
      # result fed to Judge6Sentinel.gate_triad_output()
  """

  def __init__(self) -> None:
    self.kosmos = KosmosAgent()
    self.bioagents = BioAgentsAgent()
    self.darwinian = DarwinianEngine()
    self._cycle_history: list[TriadCycleResult] = []
    logger.info("🔬 Autoresearch Triad initialized (3-stage pipeline)")

  def execute_cycle(
    self,
    question: str,
    domain: ResearchDomain = ResearchDomain.GENERAL,
    target_files: list[str] | None = None,
    depth: int = 2,
  ) -> TriadCycleResult:
    """Execute one complete Triad cycle.

    Stage 1: Kosmos plans research queries
    Stage 2: BioAgents proposes mutations from research
    Stage 3: Darwinian Engine scores mutations

    NOTE: This produces PLANS, not side effects. The Antigravity
    orchestrator executes MCP calls from the plans.
    """
    start = time.time()
    cycle_id = f"triad_{int(start * 1000)}"

    # Stage 1: Kosmos — Research Planning
    query = ResearchQuery(question=question, domain=domain, depth=depth)
    research_plan = self.kosmos.plan_research(query)

    # Simulate research completion (in production, orchestrator executes MCP calls)
    self.kosmos.record_result(
      ResearchResult(
        query=query,
        grounded_answer=f"Research plan generated for: {question}",
        confidence=0.8,
        sources=["google-developer-knowledge"],
      )
    )

    # Stage 2: BioAgents — Mutation Proposals
    kosmos_payload = self.kosmos.get_handoff_payload()
    mutation_batch = self.bioagents.propose_mutations(
      kosmos_payload=kosmos_payload,
      target_files=target_files,
    )

    # Stage 3: Darwinian — Fitness Evaluation
    fitness_report = self.darwinian.evaluate_batch(mutation_batch)

    # Compile result
    result = TriadCycleResult(
      cycle_id=cycle_id,
      research_plan=research_plan,
      mutation_count=len(mutation_batch.mutations),
      promoted_count=sum(
        1 for v in fitness_report.verdicts.values() if v == FitnessVerdict.PROMOTE
      ),
      regressed_count=sum(
        1 for v in fitness_report.verdicts.values() if v == FitnessVerdict.REGRESS
      ),
      elapsed_ms=(time.time() - start) * 1000,
    )

    self._cycle_history.append(result)
    logger.info(
      "🔬 Triad cycle %s: %d mutations, %d promoted, %d regressed (%.0fms)",
      cycle_id,
      result.mutation_count,
      result.promoted_count,
      result.regressed_count,
      result.elapsed_ms,
    )
    return result

  def get_j6_handoff(self, result: TriadCycleResult) -> dict[str, Any]:
    """Produce handoff payload for Judge 6 Sentinel gating.

    Judge 6 is SEPARATE from the Triad — it receives the Triad's
    output and applies governance/risk gating before promotion.
    """
    return {
      "source": "autoresearch_triad",
      "cycle_id": result.cycle_id,
      "promotion_rate": result.promotion_rate,
      "mutations_promoted": result.promoted_count,
      "mutations_regressed": result.regressed_count,
      "total_mutations": result.mutation_count,
      "research_plan": result.research_plan,
      "risk_assessment": "LOW" if result.regressed_count == 0 else "ELEVATED",
    }

  def get_diagnostics(self) -> dict[str, Any]:
    return {
      "orchestrator": "autoresearch_triad",
      "total_cycles": len(self._cycle_history),
      "kosmos": self.kosmos.get_diagnostics(),
      "bioagents": self.bioagents.get_diagnostics(),
      "darwinian": self.darwinian.get_diagnostics(),
    }
