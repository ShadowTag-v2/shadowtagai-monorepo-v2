# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Speculation Engine telemetry — structured event logging to .beads/ evidence trail."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


def _get_beads_path() -> Path:
    return Path(os.environ.get("BEADS_DIR", ".beads"))


def _write_event(event_type: str, payload: dict[str, Any]) -> None:
    beads = _get_beads_path()
    log_file = beads / "speculation_telemetry.jsonl"
    try:
        beads.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": time.time(),
            "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            **payload,
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass  # Fail-open: telemetry never blocks execution


def log_suggestion_event(*, event: str, **kwargs: Any) -> None:
    _write_event(f"suggestion_{event}", {k: v for k, v in kwargs.items() if v is not None})


def log_speculation_event(*, event: str, **kwargs: Any) -> None:
    _write_event(f"speculation_{event}", {k: v for k, v in kwargs.items() if v is not None})


def read_telemetry_events(
    event_type_prefix: str = "",
    session_id: str = "",
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Read telemetry events from the .beads/ evidence trail.

    Args:
        event_type_prefix: Filter by event_type prefix (e.g. 'speculation_').
        session_id: Filter by session_id.
        limit: Maximum events to return.

    Returns:
        List of telemetry events, most recent first.
    """
    beads = _get_beads_path()
    log_file = beads / "speculation_telemetry.jsonl"
    events: list[dict[str, Any]] = []
    if not log_file.exists():
        return events
    try:
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                if event_type_prefix and not entry.get("event_type", "").startswith(event_type_prefix):
                    continue
                if session_id and entry.get("session_id") != session_id:
                    continue
                events.append(entry)
    except Exception:
        pass
    return events[-limit:][::-1]


# ---------------------------------------------------------------------------
# OpenTelemetry Span Wrappers
# ---------------------------------------------------------------------------


def _get_tracer() -> Any:
    """Lazy-load OTel tracer. Returns None if opentelemetry is not installed."""
    try:
        from opentelemetry import trace

        return trace.get_tracer("speculation_engine", "1.0.0")
    except ImportError:
        return None


class SpanContext:
    """Context manager that wraps an operation in an OTel span.

    Falls back to no-op if OpenTelemetry is not available.

    Usage::

        with SpanContext("bridge.research_sweep", query=topic) as span:
            result = sweep.run(topic)
            span.set_attribute("result.length", len(result.report_text))
    """

    def __init__(self, name: str, **attributes: Any) -> None:
        self._name = name
        self._attributes = attributes
        self._span: Any = None
        self._tracer = _get_tracer()

    def __enter__(self) -> SpanContext:
        if self._tracer is not None:
            self._span = self._tracer.start_span(self._name)
            for k, v in self._attributes.items():
                self._span.set_attribute(k, str(v))
        return self

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        if self._span is not None:
            if exc_val is not None:
                self._span.set_attribute("error", True)
                self._span.set_attribute("error.message", str(exc_val))
            self._span.end()

    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute on the active span (no-op if OTel unavailable)."""
        if self._span is not None:
            self._span.set_attribute(key, str(value))


def log_bridge_call(
    *,
    operation: str,
    duration_ms: float,
    success: bool,
    **kwargs: Any,
) -> None:
    """Log a bridge call to both .beads/ telemetry and OTel spans."""
    _write_event(
        f"bridge_{operation}",
        {
            "duration_ms": round(duration_ms, 1),
            "success": success,
            **{k: v for k, v in kwargs.items() if v is not None},
        },
    )
