# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
AG-UI Event Protocol — Typed event bus for the Vulture Triad and Judge 6 Sentinel.

Events flow: Triad mutates → AG-UI emits → Judge 6 audits the Release Candidate.
Judge 6 operates OUTSIDE the Triad loop per canonical doctrine.

Event Types:
  - MEMORY_GATE_LOCKED: Pre-action invariant assertion
  - TRIAD_MUTATION_SPIN: Vulture Triad mutation cycle
  - SPEED_DELTA_COMPUTED: Performance delta after mutation
  - JUDGE6_AUDIT_PASS: Judge 6 release candidate approval
  - JUDGE6_AUDIT_FAIL: Judge 6 release candidate rejection
  - DARWINIAN_GATE_OPEN: Gate opened after fitness threshold met
  - DARWINIAN_GATE_CLOSED: Gate closed — mutation rejected
  - EPISTEMIC_SYNC: Knowledge synchronization event
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AGUIEvent(Enum):
  """Canonical AG-UI event types."""

  MEMORY_GATE_LOCKED = "ag_ui_memory_gate_locked"
  TRIAD_MUTATION_SPIN = "ag_ui_triad_mutation_spin"
  SPEED_DELTA_COMPUTED = "ag_ui_speed_delta_computed"
  JUDGE6_AUDIT_PASS = "ag_ui_judge6_audit_pass"
  JUDGE6_AUDIT_FAIL = "ag_ui_judge6_audit_fail"
  DARWINIAN_GATE_OPEN = "ag_ui_darwinian_gate_open"
  DARWINIAN_GATE_CLOSED = "ag_ui_darwinian_gate_closed"
  EPISTEMIC_SYNC = "ag_ui_epistemic_sync"
  A2A_AGENT_REGISTERED = "ag_ui_a2a_agent_registered"
  A2A_TASK_DISPATCHED = "ag_ui_a2a_task_dispatched"
  A2A_TASK_COMPLETED = "ag_ui_a2a_task_completed"
  SUBSTRATE_WRITE = "ag_ui_substrate_write"
  SUBSTRATE_READ = "ag_ui_substrate_read"
  CACHED_CONTENT_SLAB_HIT = "ag_ui_cached_content_slab_hit"
  CACHED_CONTENT_SLAB_MISS = "ag_ui_cached_content_slab_miss"


@dataclass(frozen=True, slots=True)
class AGUIEventPayload:
  """Immutable event payload — append-only ledger entry."""

  event_type: AGUIEvent
  event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
  timestamp_ns: int = field(default_factory=time.time_ns)
  source_agent: str = ""
  target_agent: str = ""
  data: dict[str, Any] = field(default_factory=dict)
  correlation_id: str = ""

  def to_dict(self) -> dict[str, Any]:
    """Serialize to dict for Firestore/BigQuery ingestion."""
    return {
      "event_type": self.event_type.value,
      "event_id": self.event_id,
      "timestamp_ns": self.timestamp_ns,
      "source_agent": self.source_agent,
      "target_agent": self.target_agent,
      "data": self.data,
      "correlation_id": self.correlation_id,
    }


# Type alias for event handlers
EventHandler = Callable[[AGUIEventPayload], None]


class AGUIEventBus:
  """
  In-process event bus for AG-UI protocol.

  Decoupled pub/sub: Triad components emit events,
  Judge 6 and substrate consumers subscribe independently.

  Thread-safe via append-only ledger (no mutation of published events).
  """

  def __init__(self) -> None:
    self._subscribers: dict[AGUIEvent, list[EventHandler]] = {}
    self._ledger: list[AGUIEventPayload] = []
    self._max_ledger_size: int = 10_000

  def subscribe(self, event_type: AGUIEvent, handler: EventHandler) -> None:
    """Register a handler for a specific event type."""
    if event_type not in self._subscribers:
      self._subscribers[event_type] = []
    self._subscribers[event_type].append(handler)

  def emit(self, payload: AGUIEventPayload) -> None:
    """
    Emit an event to all subscribers and append to ledger.

    Events are immutable (frozen dataclass) — no mutation risk.
    Ledger is bounded to prevent unbounded memory growth.
    """
    # Append to O(1) ledger
    if len(self._ledger) >= self._max_ledger_size:
      # Evict oldest 20% (FIFO)
      evict_count = self._max_ledger_size // 5
      self._ledger = self._ledger[evict_count:]
    self._ledger.append(payload)

    # Dispatch to subscribers
    handlers = self._subscribers.get(payload.event_type, [])
    for handler in handlers:
      try:
        handler(payload)
      except Exception:
        # Non-blocking: event bus must never crash the pipeline
        pass

  def emit_memory_gate(self, invariants: dict[str, Any]) -> AGUIEventPayload:
    """Convenience: emit a MEMORY_GATE_LOCKED event."""
    payload = AGUIEventPayload(
      event_type=AGUIEvent.MEMORY_GATE_LOCKED,
      source_agent="memory_gate",
      data={"invariants": invariants},
    )
    self.emit(payload)
    return payload

  def emit_triad_spin(
    self,
    mutation_id: str,
    fitness_before: float,
    fitness_after: float,
    agent: str = "vulture_triad",
  ) -> AGUIEventPayload:
    """Convenience: emit a TRIAD_MUTATION_SPIN event."""
    payload = AGUIEventPayload(
      event_type=AGUIEvent.TRIAD_MUTATION_SPIN,
      source_agent=agent,
      data={
        "mutation_id": mutation_id,
        "fitness_before": fitness_before,
        "fitness_after": fitness_after,
        "delta": fitness_after - fitness_before,
      },
    )
    self.emit(payload)
    return payload

  def emit_judge6_verdict(
    self,
    verdict: bool,
    confidence: float,
    mutation_id: str,
  ) -> AGUIEventPayload:
    """Convenience: emit Judge 6 audit result."""
    event_type = AGUIEvent.JUDGE6_AUDIT_PASS if verdict else AGUIEvent.JUDGE6_AUDIT_FAIL
    payload = AGUIEventPayload(
      event_type=event_type,
      source_agent="judge_6_sentinel",
      data={
        "verdict": verdict,
        "confidence": confidence,
        "mutation_id": mutation_id,
      },
    )
    self.emit(payload)
    return payload

  def emit_speed_delta(
    self,
    component: str,
    before_ms: float,
    after_ms: float,
  ) -> AGUIEventPayload:
    """Convenience: emit performance delta measurement."""
    payload = AGUIEventPayload(
      event_type=AGUIEvent.SPEED_DELTA_COMPUTED,
      source_agent=component,
      data={
        "before_ms": before_ms,
        "after_ms": after_ms,
        "delta_ms": after_ms - before_ms,
        "improvement_pct": (
          ((before_ms - after_ms) / before_ms * 100.0) if before_ms > 0 else 0.0
        ),
      },
    )
    self.emit(payload)
    return payload

  def get_ledger(self, last_n: int = 100) -> list[dict[str, Any]]:
    """Return the last N ledger entries as dicts."""
    entries = self._ledger[-last_n:]
    return [e.to_dict() for e in entries]

  @property
  def ledger_size(self) -> int:
    """Current ledger depth."""
    return len(self._ledger)


# Module-level singleton for process-wide event bus
_global_bus: AGUIEventBus | None = None


def get_event_bus() -> AGUIEventBus:
  """Get or create the global AG-UI event bus singleton."""
  global _global_bus  # noqa: PLW0603
  if _global_bus is None:
    _global_bus = AGUIEventBus()
  return _global_bus
