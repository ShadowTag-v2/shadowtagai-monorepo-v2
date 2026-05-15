# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""AG-UI Bridge — SSE Transport Adapter for Real-Time Agent State.

Provides Server-Sent Events (SSE) transport for the AG-UI protocol,
enabling real-time streaming of agent state to frontend components.

Endpoints:
  /ag-ui/events   — SSE stream of agent lifecycle events
  /ag-ui/state    — Current agent state snapshot (JSON)

Event types:
  triad.cycle.start   — Triad cycle begins
  triad.cycle.end     — Triad cycle completes with results
  j6.decision         — Judge 6 sentinel verdict
  darwinian.report    — Fitness evaluation report
  kosmos.research     — Research plan generated
  bioagents.mutation  — Mutation batch proposed

References:
    - AG-UI Protocol: SSE Transport specification
    - src/agents/autoresearch_triad.py
    - src/agents/judge6_sentinel.py
"""

from __future__ import annotations

import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("ag-ui-bridge")


class AGUIEventType(str, Enum):
  TRIAD_CYCLE_START = "triad.cycle.start"
  TRIAD_CYCLE_END = "triad.cycle.end"
  J6_DECISION = "j6.decision"
  DARWINIAN_REPORT = "darwinian.report"
  KOSMOS_RESEARCH = "kosmos.research"
  BIOAGENTS_MUTATION = "bioagents.mutation"
  SYSTEM_HEALTH = "system.health"


@dataclass
class AGUIEvent:
  event_type: AGUIEventType
  data: dict[str, Any]
  event_id: str = ""
  timestamp: float = field(default_factory=time.time)

  def to_sse(self) -> str:
    """Serialize to SSE wire format."""
    lines = []
    if self.event_id:
      lines.append(f"id: {self.event_id}")
    lines.append(f"event: {self.event_type.value}")
    lines.append(f"data: {json.dumps(self.data)}")
    lines.append("")
    return "\n".join(lines) + "\n"


class AGUIBridge:
  """SSE transport adapter for AG-UI protocol.

  Collects events from agent subsystems and serves them as
  Server-Sent Events for frontend consumption.

  Usage::
      bridge = AGUIBridge()
      bridge.emit(AGUIEventType.TRIAD_CYCLE_START, {"cycle_id": "..."})
      # Frontend connects to SSE endpoint and receives events
      for event in bridge.stream():
          yield event.to_sse()
  """

  def __init__(self, max_buffer: int = 500) -> None:
    self._buffer: deque[AGUIEvent] = deque(maxlen=max_buffer)
    self._event_counter = 0
    self._subscribers: list[str] = []
    logger.info("🌐 AG-UI Bridge initialized (buffer=%d)", max_buffer)

  def emit(self, event_type: AGUIEventType, data: dict[str, Any]) -> AGUIEvent:
    """Emit an event to the SSE buffer."""
    self._event_counter += 1
    event = AGUIEvent(
      event_type=event_type,
      data=data,
      event_id=str(self._event_counter),
    )
    self._buffer.append(event)
    logger.debug("📡 AG-UI event: %s (#%d)", event_type.value, self._event_counter)
    return event

  def emit_triad_start(self, cycle_id: str, question: str) -> AGUIEvent:
    return self.emit(
      AGUIEventType.TRIAD_CYCLE_START,
      {
        "cycle_id": cycle_id,
        "question": question,
        "status": "running",
      },
    )

  def emit_triad_end(
    self, cycle_id: str, promoted: int, regressed: int, elapsed_ms: float
  ) -> AGUIEvent:
    return self.emit(
      AGUIEventType.TRIAD_CYCLE_END,
      {
        "cycle_id": cycle_id,
        "promoted": promoted,
        "regressed": regressed,
        "elapsed_ms": elapsed_ms,
        "status": "completed",
      },
    )

  def emit_j6_decision(self, decision_id: str, verdict: str, risk: str) -> AGUIEvent:
    return self.emit(
      AGUIEventType.J6_DECISION,
      {
        "decision_id": decision_id,
        "verdict": verdict,
        "risk": risk,
      },
    )

  def stream(self, since_id: int = 0) -> list[AGUIEvent]:
    """Get all events since a given event ID."""
    return [e for e in self._buffer if int(e.event_id) > since_id]

  def get_state_snapshot(self) -> dict[str, Any]:
    """Current state snapshot for /ag-ui/state endpoint."""
    return {
      "total_events": self._event_counter,
      "buffer_size": len(self._buffer),
      "latest_event": self._buffer[-1].to_sse() if self._buffer else None,
      "subscribers": len(self._subscribers),
    }

  def get_diagnostics(self) -> dict[str, Any]:
    event_counts: dict[str, int] = {}
    for e in self._buffer:
      event_counts[e.event_type.value] = event_counts.get(e.event_type.value, 0) + 1
    return {
      "bridge": "ag-ui",
      "total_events_emitted": self._event_counter,
      "buffer_size": len(self._buffer),
      "event_type_counts": event_counts,
    }
