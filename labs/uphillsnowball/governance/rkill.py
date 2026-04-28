# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""RKILL — Emergency stop for Cor.autoresearch runs.

RKILL terminates unsafe or non-convergent runs immediately.
Triggered by:
  - JudgeSix-Agent Level 5 verdict
  - RuntimeWatchdog crash loop or non-convergence
  - Manual operator RKILL via API

Actions:
  1. Kill all active experiment batches
  2. Freeze whiteboard (preserve state for forensics)
  3. Generate forensic packet
  4. Notify management/operator

API endpoint: POST /v1/autoresearch/runs/:run_id/rkill
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ForensicPacket:
    """Forensic evidence packet generated on RKILL."""

    run_id: str = ""
    reason: str = ""
    triggered_by: str = ""  # "judge_agent" | "watchdog" | "operator"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    whiteboard_snapshot: dict[str, Any] = field(default_factory=dict)
    last_outputs: list[dict[str, Any]] = field(default_factory=list)
    experiment_summary: dict[str, Any] = field(default_factory=dict)
    kickback_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class RKillHandler:
    """RKILL emergency stop handler.

    Coordinates the emergency shutdown sequence:
      1. Signal all active workers to abort
      2. Freeze whiteboard state
      3. Package forensic evidence
      4. Send alerts
    """

    def __init__(self) -> None:
        self._rkill_log: list[ForensicPacket] = []

    async def execute(
        self,
        run_id: str,
        reason: str,
        triggered_by: str = "operator",
        whiteboard_state: dict[str, Any] | None = None,
        last_outputs: list[dict[str, Any]] | None = None,
    ) -> ForensicPacket:
        """Execute RKILL on a run.

        Args:
            run_id: The research run to kill.
            reason: Why RKILL was triggered.
            triggered_by: Who/what triggered it (judge_agent, watchdog, operator).
            whiteboard_state: Current whiteboard state to freeze.
            last_outputs: Last agent outputs for forensics.

        Returns:
            ForensicPacket with full evidence record.
        """
        packet = ForensicPacket(
            run_id=run_id,
            reason=reason,
            triggered_by=triggered_by,
            whiteboard_snapshot=whiteboard_state or {},
            last_outputs=last_outputs or [],
        )
        self._rkill_log.append(packet)

        logger.critical(
            "RKILL EXECUTED: run=%s reason=%s triggered_by=%s",
            run_id,
            reason,
            triggered_by,
        )

        # TODO: Signal GPU workers to abort
        # TODO: Freeze Firestore whiteboard document
        # TODO: Send management alert via Google Workspace

        return packet

    def get_rkill_log(self) -> list[ForensicPacket]:
        """Get the full RKILL event log."""
        return list(self._rkill_log)
