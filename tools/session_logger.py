#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session Logger — Append-Only Structured Logging.

Writes structured JSON logs to `.beads/sessions/` during every active
conversation. Provides audit trail for all agent actions.

Usage:
    from tools.session_logger import SessionLogger

    logger = SessionLogger(session_id="d799d9c1")
    logger.log_action("file_edit", {"file": "main.py", "lines_changed": 15})
    logger.log_decision("Used ruff over black for formatting")
    logger.log_risk("Modifying auth module without full test coverage")
    logger.close()
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any


class LogLevel(StrEnum):
    """Structured log severity levels."""

    ACTION = "action"
    DECISION = "decision"
    RISK = "risk"
    CHECKPOINT = "checkpoint"
    ERROR = "error"


class SessionLogger:
    """Append-only session logger writing to .beads/sessions/."""

    def __init__(
        self,
        session_id: str,
        beads_dir: str | Path | None = None,
    ) -> None:
        """Initialize session logger.

        Args:
            session_id: Unique session/conversation identifier.
            beads_dir: Override for .beads directory location.
        """
        self.session_id = session_id
        self.beads_dir = Path(beads_dir or os.getenv("BEADS_DIR", ".beads"))
        self.sessions_dir = self.beads_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.log_file = self.sessions_dir / f"{date_str}_{session_id[:8]}.jsonl"
        self._entry_count = 0

        # Write session start marker
        self._write_entry(
            {
                "level": "checkpoint",
                "event": "session_start",
                "session_id": session_id,
            }
        )

    def _write_entry(self, entry: dict[str, Any]) -> None:
        """Write a single JSON line to the log file (append-only)."""
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        entry["seq"] = self._entry_count
        self._entry_count += 1

        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    def log_action(self, action: str, details: dict[str, Any] | None = None) -> None:
        """Log an agent action (file edit, command run, tool call).

        Args:
            action: Action type (e.g., "file_edit", "command_run", "mcp_call").
            details: Additional context for the action.
        """
        self._write_entry(
            {
                "level": LogLevel.ACTION,
                "action": action,
                "details": details or {},
            }
        )

    def log_decision(self, rationale: str, alternatives: list[str] | None = None) -> None:
        """Log a design decision with rationale.

        Args:
            rationale: Why this decision was made.
            alternatives: What other approaches were considered.
        """
        self._write_entry(
            {
                "level": LogLevel.DECISION,
                "rationale": rationale,
                "alternatives": alternatives or [],
            }
        )

    def log_risk(self, description: str, severity: str = "medium") -> None:
        """Log a risk observation.

        Args:
            description: What the risk is.
            severity: low, medium, high, critical.
        """
        self._write_entry(
            {
                "level": LogLevel.RISK,
                "description": description,
                "severity": severity,
            }
        )

    def log_error(self, error: str, context: dict[str, Any] | None = None) -> None:
        """Log an error encountered during the session.

        Args:
            error: Error message or type.
            context: Additional error context.
        """
        self._write_entry(
            {
                "level": LogLevel.ERROR,
                "error": error,
                "context": context or {},
            }
        )

    def checkpoint(self, message: str) -> None:
        """Log a checkpoint (phase boundary, milestone).

        Args:
            message: Checkpoint description.
        """
        self._write_entry(
            {
                "level": LogLevel.CHECKPOINT,
                "message": message,
            }
        )

    def close(self) -> str:
        """Close the session and return the log file path.

        Returns:
            Absolute path to the session log file.
        """
        self._write_entry(
            {
                "level": "checkpoint",
                "event": "session_end",
                "session_id": self.session_id,
                "total_entries": self._entry_count,
            }
        )
        return str(self.log_file.resolve())

    @staticmethod
    def read_session(log_path: str | Path) -> list[dict[str, Any]]:
        """Read and parse a session log file.

        Args:
            log_path: Path to the .jsonl session log.

        Returns:
            List of log entries as dicts.
        """
        entries = []
        path = Path(log_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        return entries


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "read":
        log_path = sys.argv[2] if len(sys.argv) > 2 else ".beads/sessions/"
        path = Path(log_path)
        if path.is_dir():
            for f in sorted(path.glob("*.jsonl")):
                entries = SessionLogger.read_session(f)
                print(f"\n=== {f.name} ({len(entries)} entries) ===")
                for e in entries[:5]:
                    print(json.dumps(e, indent=2))
                if len(entries) > 5:
                    print(f"  ... and {len(entries) - 5} more entries")
        elif path.is_file():
            entries = SessionLogger.read_session(path)
            for e in entries:
                print(json.dumps(e, indent=2))
    else:
        # Demo mode
        logger = SessionLogger(session_id="demo-session-001")
        logger.log_action("file_edit", {"file": "main.py", "lines": 42})
        logger.log_decision("Used dataclass over dict for type safety")
        logger.log_risk("No unit tests for new module", severity="medium")
        logger.checkpoint("Phase 1 complete")
        log_path = logger.close()
        print(f"Session log written to: {log_path}")
