# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Telemetry Events — Structured event emission for the Tool Gateway.

Defines the 14 Datadog-compatible telemetry events that fire at each
tier transition point in the ClassifiedGateway pipeline.

Events are emitted as structured JSON log lines (JSON Lines format)
compatible with Datadog Log Management, Google Cloud Logging, and
any structured log aggregator.

Reference: Claude Code 34-event telemetry spec (adapted to 14 gateway events)
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import StrEnum

logger = logging.getLogger(__name__)

# Dedicated telemetry logger — routes to structured log handler
_telemetry_logger = logging.getLogger("tool_gateway.telemetry")


class GatewayEvent(StrEnum):
  """Telemetry events emitted by the ClassifiedGateway pipeline."""

  # Tier 0: Consequential gate
  CONSEQUENTIAL_GATE_TRIGGERED = "gateway.consequential.triggered"
  CONSEQUENTIAL_GATE_CONFIRMED = "gateway.consequential.confirmed"

  # Tier 1: Always-blocked
  ALWAYS_BLOCKED_REJECTED = "gateway.always_blocked.rejected"

  # Tier 1.25: Sandbox path validation
  SANDBOX_PATH_DENIED = "gateway.sandbox.path_denied"
  SANDBOX_PATH_SENSITIVE = "gateway.sandbox.path_sensitive"

  # Tier 1.5: Block/Allow engine
  BLOCK_ALLOW_BLOCKED = "gateway.block_allow.blocked"
  BLOCK_ALLOW_ESCALATED = "gateway.block_allow.escalated"
  BLOCK_ALLOW_ALLOWED = "gateway.block_allow.allowed"

  # Anti-rationalization
  ANTI_RATIONALIZATION_TRIGGERED = "gateway.anti_rationalization.triggered"

  # Tier 2: Classifier
  CLASSIFIER_BLOCKED = "gateway.classifier.blocked"
  CLASSIFIER_ALLOWED = "gateway.classifier.allowed"
  CLASSIFIER_ERROR = "gateway.classifier.error"

  # Tier 3: Contract
  CONTRACT_BLOCKED = "gateway.contract.blocked"
  CONTRACT_ALLOWED = "gateway.contract.allowed"


@dataclass
class TelemetryPayload:
  """Structured payload for a gateway telemetry event.

  Attributes:
      event: The event type.
      tool_id: Which tool triggered the event.
      verdict: ALLOW, BLOCK, or ESCALATE.
      tier: Which tier emitted the event (0, 1, 1.25, 1.5, 2, 3).
      reason: Human-readable explanation.
      matched_rules: List of rule IDs that matched (for block/allow engine).
      latency_ms: Time spent in this tier (milliseconds).
      metadata: Additional key-value metadata.
      timestamp: Unix timestamp of the event.
  """

  event: str
  tool_id: str
  verdict: str = ""
  tier: str = ""
  reason: str = ""
  matched_rules: list[str] = field(default_factory=list)
  latency_ms: float = 0.0
  metadata: dict[str, str] = field(default_factory=dict)
  timestamp: float = field(default_factory=time.time)


class TelemetryEmitter:
  """Emits structured telemetry events.

  Events are logged as JSON lines to the `tool_gateway.telemetry` logger
  and optionally to an in-memory buffer for testing.

  Args:
      buffer_events: If True, store events in memory for inspection.
  """

  def __init__(self, buffer_events: bool = False) -> None:
    self._buffer_events = buffer_events
    self._event_buffer: list[TelemetryPayload] = []

  def emit(self, payload: TelemetryPayload) -> None:
    """Emit a telemetry event.

    Args:
        payload: The structured event payload.
    """
    event_dict = asdict(payload)

    # Structured JSON log line
    _telemetry_logger.info(json.dumps(event_dict, default=str))

    if self._buffer_events:
      self._event_buffer.append(payload)

  @property
  def events(self) -> list[TelemetryPayload]:
    """Return buffered events (for testing)."""
    return list(self._event_buffer)

  def clear(self) -> None:
    """Clear the event buffer."""
    self._event_buffer.clear()

  def event_count(self, event_type: GatewayEvent | None = None) -> int:
    """Count buffered events, optionally filtered by type.

    Args:
        event_type: If provided, count only events of this type.

    Returns:
        Number of matching events.
    """
    if event_type is None:
      return len(self._event_buffer)
    return sum(1 for e in self._event_buffer if e.event == event_type.value)
