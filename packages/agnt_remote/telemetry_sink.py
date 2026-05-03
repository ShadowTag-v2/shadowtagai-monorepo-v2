"""Local telemetry sink — routes events to disk, not network.

Replaces upstream Datadog/OTLP exporters with local JSON-lines
file output. Integrates with packages/telemetry catalog for
consistent event naming.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any
import contextlib

logger = logging.getLogger(__name__)

_DEFAULT_LOG_DIR = ".beads"
_DEFAULT_LOG_FILE = "telemetry.jsonl"


class LocalTelemetrySink:
    """Telemetry sink that writes to local JSONL files.

    Safe Harbor: No network egress. All telemetry stays on disk.
    Output goes to {workspace}/.beads/telemetry.jsonl by default.
    """

    __slots__ = ("_log_path", "_file")

    def __init__(self, log_dir: str | None = None) -> None:
        base = log_dir or os.path.join(os.getcwd(), _DEFAULT_LOG_DIR)
        Path(base).mkdir(parents=True, exist_ok=True)
        self._log_path = os.path.join(base, _DEFAULT_LOG_FILE)
        self._file = None

    def _ensure_file(self):
        if self._file is None:
            self._file = open(self._log_path, "a", encoding="utf-8")  # noqa: SIM115

    def emit(self, event_name: str, **properties: Any) -> None:
        """Write a telemetry event to disk."""
        record = {
            "ts": time.time(),
            "event": event_name,
            "props": properties,
        }
        try:
            self._ensure_file()
            self._file.write(json.dumps(record, default=str) + "\n")
            self._file.flush()
        except OSError as exc:
            logger.warning("Telemetry write failed: %s", exc)

    def flush(self) -> None:
        """Flush pending writes to disk."""
        if self._file:
            with contextlib.suppress(OSError):
                self._file.flush()

    def close(self) -> None:
        """Close the telemetry file."""
        if self._file:
            with contextlib.suppress(OSError):
                self._file.close()
            self._file = None
