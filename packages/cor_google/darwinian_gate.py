# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Darwinian Gate — Fitness-gated mutation pipeline.

Wires the Vulture Triad through AG-UI events → GCP Substrate → Judge 6 Sentinel.
Replaces the legacy file-based gate with cloud-native event-driven architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from packages.cor_google.ag_ui import AGUIEvent, AGUIEventBus, AGUIEventPayload


@dataclass
class MutationCandidate:
  """A code mutation proposed by the Vulture Triad."""

  mutation_id: str
  source_file: str
  description: str
  fitness_before: float = 0.0
  fitness_after: float = 0.0
  benchmark_ms: float = 0.0
  metadata: dict[str, Any] = field(default_factory=dict)

  @property
  def fitness_delta(self) -> float:
    return self.fitness_after - self.fitness_before

  @property
  def is_improvement(self) -> bool:
    return self.fitness_delta > 0


class DarwinianGate:
  """
  Fitness-gated mutation pipeline.

  Flow:
    1. Triad proposes mutation → emits TRIAD_MUTATION_SPIN
    2. Gate evaluates fitness delta → emits SPEED_DELTA_COMPUTED
    3. If delta > threshold → emits DARWINIAN_GATE_OPEN
    4. Judge 6 audits the RC → emits JUDGE6_AUDIT_PASS/FAIL
    5. If Judge 6 passes → mutation is committed
  """

  def __init__(
    self,
    event_bus: AGUIEventBus,
    fitness_threshold: float = 0.05,
  ) -> None:
    self.event_bus = event_bus
    self.fitness_threshold = fitness_threshold
    self._mutations: list[MutationCandidate] = []
    self._accepted: list[str] = []
    self._rejected: list[str] = []

  def propose_mutation(self, candidate: MutationCandidate) -> bool:
    """
    Evaluate a mutation candidate against the fitness threshold.

    Returns True if the gate opens (mutation passes fitness check).
    """
    self._mutations.append(candidate)

    # Emit Triad spin event
    self.event_bus.emit_triad_spin(
      mutation_id=candidate.mutation_id,
      fitness_before=candidate.fitness_before,
      fitness_after=candidate.fitness_after,
    )

    # Emit speed delta
    if candidate.benchmark_ms > 0:
      self.event_bus.emit_speed_delta(
        component=candidate.source_file,
        before_ms=candidate.benchmark_ms,
        after_ms=candidate.benchmark_ms * (1.0 - candidate.fitness_delta),
      )

    # Gate decision
    if candidate.is_improvement and candidate.fitness_delta >= self.fitness_threshold:
      self.event_bus.emit(
        AGUIEventPayload(
          event_type=AGUIEvent.DARWINIAN_GATE_OPEN,
          source_agent="darwinian_gate",
          data={"mutation_id": candidate.mutation_id, "delta": candidate.fitness_delta},
        )
      )
      self._accepted.append(candidate.mutation_id)
      return True
    else:
      self.event_bus.emit(
        AGUIEventPayload(
          event_type=AGUIEvent.DARWINIAN_GATE_CLOSED,
          source_agent="darwinian_gate",
          data={
            "mutation_id": candidate.mutation_id,
            "delta": candidate.fitness_delta,
            "threshold": self.fitness_threshold,
          },
        )
      )
      self._rejected.append(candidate.mutation_id)
      return False

  @property
  def accepted_count(self) -> int:
    return len(self._accepted)

  @property
  def rejected_count(self) -> int:
    return len(self._rejected)

  @property
  def stats(self) -> dict[str, Any]:
    return {
      "total_mutations": len(self._mutations),
      "accepted": self.accepted_count,
      "rejected": self.rejected_count,
      "fitness_threshold": self.fitness_threshold,
      "acceptance_rate": (
        self.accepted_count / len(self._mutations) if self._mutations else 0.0
      ),
    }
