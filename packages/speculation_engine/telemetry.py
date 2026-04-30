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
