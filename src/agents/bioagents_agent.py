# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""BioAgents Agent — Self-Improving Code Mutation Engine.

Stage 2 of the Autoresearch Triad (Kosmos → BioAgents → n-autoresearch).

BioAgents receives grounded research from Kosmos and produces code
mutations: refactoring proposals, performance patches, and dead-code
elimination targets. Each mutation is scored by the Darwinian Fitness
Engine before being promoted to the n-autoresearch stage.

The 'bio' metaphor is deliberate: mutations compete for survival based
on measurable fitness (bench_ms, test pass rate, lint score). Only the
fittest survive to production.

References:
    - TACSOP 5: Autoresearch Mutation Fitness (5% threshold)
    - Rich Hickey Doctrine: Simple Made Easy, DELETION first
    - ruff check --select F401,F841 --fix (dead code elimination)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("bioagents")


class MutationType(str, Enum):
  """Types of code mutations BioAgents can propose."""

  DEAD_CODE_REMOVAL = "dead_code_removal"
  PERFORMANCE_PATCH = "performance_patch"
  REFACTOR = "refactor"
  DEPENDENCY_UPDATE = "dependency_update"
  SECURITY_HARDENING = "security_hardening"
  TYPE_ANNOTATION = "type_annotation"


class FitnessVerdict(str, Enum):
  """Darwinian fitness verdict for a mutation."""

  PROMOTE = "promote"  # Better fitness → promote to n-autoresearch
  NEUTRAL = "neutral"  # No measurable change → log and skip
  REGRESS = "regress"  # Worse fitness → reject and revert


@dataclass
class Mutation:
  """A proposed code mutation with fitness metadata."""

  mutation_id: str
  mutation_type: MutationType
  target_file: str
  description: str
  diff_preview: str = ""
  confidence: float = 0.0

  # Fitness metrics (populated after Darwinian Engine evaluation)
  bench_ms_before: float | None = None
  bench_ms_after: float | None = None
  lint_score_before: int | None = None
  lint_score_after: int | None = None
  test_pass_rate_before: float | None = None
  test_pass_rate_after: float | None = None
  verdict: FitnessVerdict = FitnessVerdict.NEUTRAL
  timestamp: float = field(default_factory=time.time)

  @property
  def fitness_delta_pct(self) -> float | None:
    """Compute percentage improvement in bench_ms (negative = faster = better)."""
    if self.bench_ms_before is None or self.bench_ms_after is None:
      return None
    if self.bench_ms_before == 0:
      return 0.0
    return ((self.bench_ms_after - self.bench_ms_before) / self.bench_ms_before) * 100

  @property
  def passes_threshold(self) -> bool:
    """Check if mutation meets the 5% improvement threshold (TACSOP 5)."""
    delta = self.fitness_delta_pct
    if delta is None:
      return False
    return delta <= -5.0  # 5% faster


@dataclass
class MutationBatch:
  """A batch of mutations for a single research-to-code cycle."""

  batch_id: str
  kosmos_payload: list[dict[str, Any]]
  mutations: list[Mutation] = field(default_factory=list)
  created_at: float = field(default_factory=time.time)


class BioAgentsAgent:
  """Self-improving code mutation engine.

  Receives Kosmos research results and produces mutation proposals.
  Does NOT apply mutations directly — produces plans for the
  Darwinian Fitness Engine to evaluate.

  Usage::

      bio = BioAgentsAgent()
      batch = bio.propose_mutations(
          kosmos_payload=kosmos.get_handoff_payload(),
          target_files=["src/agents/autoresearch_triad.py"],
      )
      # batch.mutations fed to DarwinianEngine.evaluate_batch()
  """

  def __init__(self) -> None:
    self._mutation_history: list[MutationBatch] = []
    self._max_history = 50
    logger.info("🧬 BioAgents Agent initialized")

  def propose_mutations(
    self,
    kosmos_payload: list[dict[str, Any]],
    target_files: list[str] | None = None,
  ) -> MutationBatch:
    """Generate mutation proposals from Kosmos research results.

    This method analyzes the research payload and identifies
    potential improvements to the target codebase.

    Args:
        kosmos_payload: Grounded research results from Kosmos agent.
        target_files: Optional list of files to focus mutations on.

    Returns:
        MutationBatch with proposed mutations ready for fitness evaluation.
    """
    batch_id = f"bio_{int(time.time() * 1000)}"
    batch = MutationBatch(
      batch_id=batch_id,
      kosmos_payload=kosmos_payload,
    )

    # Mutation strategy 1: Dead code elimination (always first — Rich Hickey)
    if target_files:
      for target in target_files:
        batch.mutations.append(
          Mutation(
            mutation_id=f"{batch_id}_deadcode_{target}",
            mutation_type=MutationType.DEAD_CODE_REMOVAL,
            target_file=target,
            description=f"ruff check --select F401,F841 --fix on {target}",
            confidence=0.95,  # ruff is deterministic
          )
        )

    # Mutation strategy 2: Research-informed improvements
    for item in kosmos_payload:
      domain = item.get("domain", "general")
      question = item.get("question", "")

      if "performance" in question.lower() or "optimize" in question.lower():
        batch.mutations.append(
          Mutation(
            mutation_id=f"{batch_id}_perf_{domain}",
            mutation_type=MutationType.PERFORMANCE_PATCH,
            target_file=target_files[0] if target_files else "unknown",
            description=f"Performance optimization from research: {question[:80]}",
            confidence=item.get("confidence", 0.5),
          )
        )

      if "security" in question.lower() or "vulnerability" in question.lower():
        batch.mutations.append(
          Mutation(
            mutation_id=f"{batch_id}_sec_{domain}",
            mutation_type=MutationType.SECURITY_HARDENING,
            target_file=target_files[0] if target_files else "unknown",
            description=f"Security hardening from research: {question[:80]}",
            confidence=item.get("confidence", 0.5),
          )
        )

    # Record batch
    if len(self._mutation_history) >= self._max_history:
      self._mutation_history.pop(0)
    self._mutation_history.append(batch)

    logger.info(
      "🧬 Mutation batch %s: %d mutations proposed from %d research items",
      batch_id,
      len(batch.mutations),
      len(kosmos_payload),
    )
    return batch

  def get_handoff_payload(self, batch: MutationBatch) -> list[dict[str, Any]]:
    """Produce the handoff payload for n-autoresearch (Triad stage 3).

    Only includes mutations that passed Darwinian fitness evaluation.
    """
    return [
      {
        "mutation_id": m.mutation_id,
        "type": m.mutation_type.value,
        "target": m.target_file,
        "description": m.description,
        "fitness_delta_pct": m.fitness_delta_pct,
        "verdict": m.verdict.value,
      }
      for m in batch.mutations
      if m.verdict == FitnessVerdict.PROMOTE
    ]

  def get_diagnostics(self) -> dict[str, Any]:
    """Return agent diagnostics."""
    total_mutations = sum(len(b.mutations) for b in self._mutation_history)
    promoted = sum(
      1
      for b in self._mutation_history
      for m in b.mutations
      if m.verdict == FitnessVerdict.PROMOTE
    )
    return {
      "agent": "bioagents",
      "total_batches": len(self._mutation_history),
      "total_mutations": total_mutations,
      "promoted": promoted,
      "promotion_rate": promoted / total_mutations if total_mutations > 0 else 0.0,
    }
