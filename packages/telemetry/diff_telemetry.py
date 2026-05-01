# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Diff Telemetry — OTel-backed diff computation instrumentation.

Integrates agnt_utils.diff_utils with the telemetry pipeline to track:
  - Patch generation latency and hunk counts
  - Lines added/removed per file edit
  - Edit application success/failure rates
  - Diff size distribution for context window optimization

Usage:
    from telemetry.diff_telemetry import DiffTelemetry

    dt = DiffTelemetry(sink=my_sink)
    hunks = dt.tracked_patch(old_content, new_content, file_path="main.py")
    result = dt.tracked_edit(content, edits, file_path="utils.py")
"""

from __future__ import annotations

import logging
import time
from typing import Any

from telemetry.catalog import TelemetryEvent

logger = logging.getLogger(__name__)


class DiffTelemetry:
    """Instrumented wrapper around agnt_utils.diff_utils.

    Emits telemetry events for every patch generation and edit application.

    Args:
        sink: The TelemetrySink to emit events to. If None, creates a default.
        enabled: Override enabled state.
    """

    def __init__(
        self,
        sink: Any | None = None,
        enabled: bool = True,
    ) -> None:
        self._sink = sink
        self._enabled = enabled

    @property
    def sink(self) -> Any:
        """Lazy init of TelemetrySink."""
        if self._sink is None:
            from telemetry.sink import TelemetrySink

            self._sink = TelemetrySink(enabled=self._enabled)
        return self._sink

    def tracked_patch(
        self,
        old_content: str,
        new_content: str,
        *,
        file_path: str = "",
        context_lines: int = 3,
    ) -> list[Any]:
        """Generate a patch and emit telemetry about the diff.

        Returns:
            List of Hunk objects from diff_utils.get_patch_from_contents.
        """
        from agnt_utils.diff_utils import count_lines_changed, get_patch_from_contents

        start = time.monotonic()
        hunks = get_patch_from_contents(
            old_content,
            new_content,
            file_path=file_path,
            context_lines=context_lines,
        )
        duration_ms = (time.monotonic() - start) * 1000

        changes = count_lines_changed(hunks)

        event = TelemetryEvent(
            name="diff.patch_generated",
            properties={
                "file_path": file_path,
                "hunk_count": len(hunks),
                "additions": changes.additions,
                "removals": changes.removals,
                "old_size_bytes": len(old_content),
                "new_size_bytes": len(new_content),
                "duration_ms": round(duration_ms, 2),
            },
        )
        self.sink.emit(event)
        logger.debug(
            "diff.patch_generated: %s — %d hunks, +%d/-%d in %.1fms",
            file_path,
            len(hunks),
            changes.additions,
            changes.removals,
            duration_ms,
        )
        return hunks

    def tracked_edit(
        self,
        content: str,
        edits: list[dict[str, str]],
        *,
        file_path: str = "",
    ) -> str:
        """Apply edits and emit telemetry about the result.

        Returns:
            The modified content string.
        """
        from agnt_utils.diff_utils import apply_edits, count_lines_changed, get_patch_from_contents

        start = time.monotonic()
        result = apply_edits(content, edits)
        duration_ms = (time.monotonic() - start) * 1000

        # Compute hunks for the edit to measure impact
        hunks = get_patch_from_contents(content, result, file_path=file_path)
        changes = count_lines_changed(hunks)

        event = TelemetryEvent(
            name="diff.edit_applied",
            properties={
                "file_path": file_path,
                "edit_count": len(edits),
                "hunk_count": len(hunks),
                "additions": changes.additions,
                "removals": changes.removals,
                "content_size_bytes": len(content),
                "result_size_bytes": len(result),
                "duration_ms": round(duration_ms, 2),
                "success": True,
            },
        )
        self.sink.emit(event)
        return result

    def tracked_unified_diff(
        self,
        old_content: str,
        new_content: str,
        *,
        file_path: str = "",
    ) -> str:
        """Generate a unified diff string with telemetry.

        Returns:
            The unified diff string.
        """
        from agnt_utils.diff_utils import get_unified_diff

        start = time.monotonic()
        diff = get_unified_diff(old_content, new_content, file_path=file_path)
        duration_ms = (time.monotonic() - start) * 1000

        event = TelemetryEvent(
            name="diff.unified_generated",
            properties={
                "file_path": file_path,
                "diff_size_bytes": len(diff),
                "old_size_bytes": len(old_content),
                "new_size_bytes": len(new_content),
                "duration_ms": round(duration_ms, 2),
            },
        )
        self.sink.emit(event)
        return diff
