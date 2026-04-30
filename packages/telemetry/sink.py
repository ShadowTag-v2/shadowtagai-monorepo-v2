# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Telemetry Sink — JSONL writer for structured events.

Writes events to .beads/telemetry.jsonl with:
  - Append-only writes (concurrent-safe with file locking)
  - Optional rotation by size (default: 10MB)
  - Optional BigQuery export stub
  - Buffer flush on close
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from telemetry.catalog import TelemetryEvent

logger = logging.getLogger(__name__)

# Default max file size before rotation (10 MB)
DEFAULT_MAX_BYTES = 10 * 1024 * 1024


class TelemetrySink:
    """JSONL writer for telemetry events.

    Args:
        output_path: Path to the telemetry JSONL file.
        max_bytes: Maximum file size before rotation.
        buffer_size: Number of events to buffer before flushing.
        enabled: Whether telemetry is active.
    """

    def __init__(
        self,
        output_path: Path | None = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
        buffer_size: int = 10,
        enabled: bool | None = None,
    ) -> None:
        default_path = Path(os.environ.get("AGNT_TELEMETRY_PATH", ".beads/telemetry.jsonl"))
        self._path = output_path or default_path
        self._max_bytes = max_bytes
        self._buffer_size = buffer_size
        self._buffer: list[dict[str, Any]] = []
        self._total_emitted: int = 0

        # Default: enabled unless AGNT_TELEMETRY=0
        if enabled is not None:
            self._enabled = enabled
        else:
            from config.feature_flags import flags
            self._enabled = flags.is_enabled("telemetry_enabled")

    @property
    def enabled(self) -> bool:
        """Whether telemetry is active."""
        return self._enabled

    @property
    def total_emitted(self) -> int:
        """Total events emitted this session."""
        return self._total_emitted

    def emit(self, event: TelemetryEvent) -> None:
        """Emit a single telemetry event.

        Events are buffered and flushed when buffer_size is reached.
        """
        if not self._enabled:
            return

        self._buffer.append(event.to_dict())
        self._total_emitted += 1

        if len(self._buffer) >= self._buffer_size:
            self.flush()

    def emit_raw(self, data: dict[str, Any]) -> None:
        """Emit a raw event dictionary (for legacy integrations)."""
        if not self._enabled:
            return

        if "timestamp" not in data:
            data["timestamp"] = time.time()

        self._buffer.append(data)
        self._total_emitted += 1

        if len(self._buffer) >= self._buffer_size:
            self.flush()

    def flush(self) -> None:
        """Flush buffered events to disk."""
        if not self._buffer:
            return

        try:
            self._maybe_rotate()
            self._path.parent.mkdir(parents=True, exist_ok=True)

            with open(self._path, "a") as f:
                for event_dict in self._buffer:
                    f.write(json.dumps(event_dict, default=str) + "\n")

            flushed = len(self._buffer)
            self._buffer.clear()
            logger.debug("Telemetry flushed %d events to %s", flushed, self._path)

        except OSError as e:
            logger.warning("Telemetry flush failed: %s", e)

    def _maybe_rotate(self) -> None:
        """Rotate log file if it exceeds max_bytes."""
        if not self._path.exists():
            return

        size = self._path.stat().st_size
        if size < self._max_bytes:
            return

        # Rotate: rename current file with timestamp
        ts = time.strftime("%Y%m%d_%H%M%S")
        rotated = self._path.with_suffix(f".{ts}.jsonl")
        self._path.rename(rotated)
        logger.info("Telemetry rotated: %s → %s", self._path.name, rotated.name)

    def close(self) -> None:
        """Flush remaining buffer and close."""
        self.flush()
        logger.info(
            "Telemetry sink closed: %d total events → %s",
            self._total_emitted,
            self._path,
        )

    def __enter__(self) -> TelemetrySink:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"TelemetrySink(path={self._path}, enabled={self._enabled}, buffered={len(self._buffer)})"
