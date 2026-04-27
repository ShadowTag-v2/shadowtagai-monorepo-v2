"""Evidence Logger — Appends structured audit entries to .beads/issues.jsonl.

Every tool gateway decision is logged as a structured JSON line for
observability (Pillar 4 of the Control Plane). This creates a durable
evidence trail that answers: "What did the agent try, why was it allowed
or blocked, and what existing patterns were surfaced?"
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.tool_gateway.gateway import Decision

logger = logging.getLogger(__name__)


class EvidenceLogger:
    """Appends gateway decision records to .beads/issues.jsonl.

    Args:
        beads_dir: Path to the .beads directory.
    """

    def __init__(self, beads_dir: Path) -> None:
        self._beads_dir = beads_dir
        self._issues_file = beads_dir / "issues.jsonl"

    def log_check(
        self,
        tool_id: str,
        context: dict[str, Any],
        decision: Decision,
    ) -> None:
        """Log a gateway decision to the evidence file.

        Args:
            tool_id: The tool identifier that was checked.
            context: The runtime context provided to the check.
            decision: The gateway's decision.
        """
        self._beads_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize context: remove anything not JSON-serializable
        safe_context = {}
        for k, v in context.items():
            try:
                json.dumps(v)
                safe_context[k] = v
            except TypeError, ValueError:
                safe_context[k] = str(v)

        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "type": "tool_gateway_check",
            "tool_id": tool_id,
            "allowed": decision.allowed,
            "reason": decision.reason,
            "contract_id": decision.contract_id,
            "reuse_hints": decision.reuse_hints,
            "preconditions_met": decision.preconditions_met,
            "context_keys": list(safe_context.keys()),
        }

        try:
            with self._issues_file.open("a") as f:
                f.write(json.dumps(entry) + "\n")
            logger.debug("Evidence logged for %s: %s", tool_id, decision.allowed)
        except OSError:
            logger.exception("Failed to write evidence for %s", tool_id)

    def log_execution(
        self,
        tool_id: str,
        success: bool,
        detail: str = "",
    ) -> None:
        """Log the result of a tool execution (post-action evidence).

        Args:
            tool_id: The tool identifier that was executed.
            success: Whether the execution succeeded.
            detail: Optional detail string.
        """
        self._beads_dir.mkdir(parents=True, exist_ok=True)

        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "type": "tool_gateway_execution",
            "tool_id": tool_id,
            "success": success,
            "detail": detail[:500],
        }

        try:
            with self._issues_file.open("a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            logger.exception("Failed to write execution evidence for %s", tool_id)
