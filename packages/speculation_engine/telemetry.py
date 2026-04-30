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
