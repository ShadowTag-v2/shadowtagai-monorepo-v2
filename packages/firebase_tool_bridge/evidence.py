# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Evidence Logger — records every function call to .agent/evidence/.

Every function call produces an evidence record:
  - function_name
  - args_hash (SHA-256 of canonicalized args, never raw args)
  - risk_tier
  - confirmation_required / confirmation_received
  - execution_result_summary
  - duration_ms
  - timestamp

Evidence is append-only NDJSON — the authoritative mutation log.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Default evidence directory relative to repo root.
DEFAULT_EVIDENCE_DIR = Path(".agent/evidence")


@dataclass(slots=True)
class EvidenceRecord:
    """A single function call evidence record."""

    function_name: str
    args_hash: str
    risk_tier: str
    confirmation_required: bool
    confirmation_received: bool | None
    execution_result_summary: str
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict, omitting None values."""
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


def hash_args(args: dict[str, Any]) -> str:
    """Compute SHA-256 hash of canonicalized function arguments.

    NEVER log raw args — they may contain PII or secrets.
    Only the hash is stored in evidence.

    Args:
        args: The function call arguments dict.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    canonical = json.dumps(args, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


class EvidenceLogger:
    """Append-only NDJSON evidence logger.

    Usage:
        evidence = EvidenceLogger(repo_root=Path("."))
        record = evidence.log(
            function_name="fetch_weather",
            args={"city": "Boston"},
            risk_tier="low",
            confirmation_required=False,
            confirmation_received=None,
            result_summary="temperature=38",
            duration_ms=142.5,
        )
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        """Initialize the evidence logger.

        Args:
            repo_root: Path to the monorepo root. Defaults to current directory.
        """
        self._repo_root = repo_root or Path(".")
        self._evidence_dir = self._repo_root / DEFAULT_EVIDENCE_DIR
        self._evidence_file = self._evidence_dir / "function_calls.ndjson"
        self._evidence_dir.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        *,
        function_name: str,
        args: dict[str, Any],
        risk_tier: str,
        confirmation_required: bool,
        confirmation_received: bool | None,
        result_summary: str,
        duration_ms: float,
        success: bool = True,
        error: str | None = None,
    ) -> EvidenceRecord:
        """Record a function call to the evidence log.

        Args:
            function_name: Name of the called function.
            args: The function arguments (hashed, never stored raw).
            risk_tier: Risk tier string.
            confirmation_required: Whether confirmation was required.
            confirmation_received: Whether confirmation was received (None if not required).
            result_summary: Brief summary of the result (no PII).
            duration_ms: Execution duration in milliseconds.
            success: Whether the call succeeded.
            error: Error message if failed.

        Returns:
            The evidence record that was logged.
        """
        record = EvidenceRecord(
            function_name=function_name,
            args_hash=hash_args(args),
            risk_tier=risk_tier,
            confirmation_required=confirmation_required,
            confirmation_received=confirmation_received,
            execution_result_summary=result_summary,
            duration_ms=duration_ms,
            success=success,
            error=error,
        )

        line = json.dumps(record.to_dict(), separators=(",", ":"))
        with self._evidence_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

        logger.info(
            "Evidence logged: %s (risk=%s, %sms)",
            function_name,
            risk_tier,
            f"{duration_ms:.1f}",
        )
        return record

    @staticmethod
    def timer() -> float:
        """Return a high-resolution timestamp for timing function calls."""
        return time.perf_counter()

    @staticmethod
    def elapsed_ms(start: float) -> float:
        """Calculate elapsed milliseconds since start."""
        return (time.perf_counter() - start) * 1000
