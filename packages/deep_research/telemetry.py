# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Deep Research Telemetry — Phase-level event emission.

Emits structured events for every state transition, research query,
and metric sample.  Events are appended to the session telemetry log
(`.beads/telemetry.jsonl`) and can optionally be forwarded to an
external collector.

Event schema follows the Claude Code analytics pattern:
  generationRequestId → session_id mapping for downstream RL joins.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default telemetry sink (relative to workspace root).
_TELEMETRY_PATH = Path(".beads/telemetry.jsonl")


def _write_event(event: dict[str, Any]) -> None:
    """Append a JSON-lines event to the telemetry log."""
    try:
        _TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _TELEMETRY_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, default=str) + "\n")
    except OSError:
        logger.debug("[Telemetry] Could not write event: %s", event.get("type"))


def emit_phase_event(transition: Any) -> None:
    """Emit a phase-transition telemetry event.

    Args:
        transition: A PhaseTransition dataclass instance.
    """
    event = {
        "type": "deep_research.phase_transition",
        "ts": time.time(),
        "session_id": getattr(transition, "metadata", {}).get("session_id", ""),
        "from_phase": getattr(transition, "from_phase", "").value
        if hasattr(getattr(transition, "from_phase", ""), "value")
        else str(getattr(transition, "from_phase", "")),
        "to_phase": getattr(transition, "to_phase", "").value
        if hasattr(getattr(transition, "to_phase", ""), "value")
        else str(getattr(transition, "to_phase", "")),
        "duration_ms": getattr(transition, "duration_ms", 0.0),
        "success": getattr(transition, "success", True),
        "error": getattr(transition, "error", None),
    }
    logger.debug("[Telemetry] phase_transition: %s → %s", event["from_phase"], event["to_phase"])
    _write_event(event)


def emit_research_metric(
    session_id: str,
    metric_name: str,
    value: float,
    labels: dict[str, str] | None = None,
) -> None:
    """Emit a numeric research metric.

    Args:
        session_id: The deep research session ID.
        metric_name: Name of the metric (e.g. 'queries_routed', 'confidence').
        value: Numeric value.
        labels: Optional key-value labels for the metric.
    """
    event = {
        "type": "deep_research.metric",
        "ts": time.time(),
        "session_id": session_id,
        "metric": metric_name,
        "value": value,
        "labels": labels or {},
    }
    logger.debug("[Telemetry] metric: %s=%s", metric_name, value)
    _write_event(event)


def emit_sandbox_event(
    session_id: str,
    action: str,
    container_id: str = "",
    duration_ms: float = 0.0,
    success: bool = True,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Emit a sandbox lifecycle event.

    Args:
        session_id: Parent deep research session.
        action: Lifecycle action (create, execute, verify, destroy).
        container_id: OrbStack container identifier.
        duration_ms: Duration of the action.
        success: Whether the action succeeded.
        metadata: Additional event metadata.
    """
    event = {
        "type": "deep_research.sandbox",
        "ts": time.time(),
        "session_id": session_id,
        "action": action,
        "container_id": container_id,
        "duration_ms": duration_ms,
        "success": success,
        "metadata": metadata or {},
    }
    logger.debug("[Telemetry] sandbox: %s (container=%s)", action, container_id[:12])
    _write_event(event)


def emit_evaluation_event(
    session_id: str,
    step: str,
    passed: bool,
    details: dict[str, Any] | None = None,
) -> None:
    """Emit an evaluation bridge gate event.

    Args:
        session_id: Parent deep research session.
        step: Evaluation step (build, test, lint, merge).
        passed: Whether the gate passed.
        details: Additional gate result details.
    """
    event = {
        "type": "deep_research.evaluation",
        "ts": time.time(),
        "session_id": session_id,
        "step": step,
        "passed": passed,
        "details": details or {},
    }
    logger.debug("[Telemetry] evaluation: %s passed=%s", step, passed)
    _write_event(event)
