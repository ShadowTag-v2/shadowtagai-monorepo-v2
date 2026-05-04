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

Two writer strategies:
  - SyncEvidenceWriter: Original synchronous file I/O (default, guaranteed durability)
  - AsyncBatchEvidenceWriter: Buffered writes with periodic flush (lower latency)
"""

from __future__ import annotations

import atexit
import hashlib
import json
import logging
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

logger = logging.getLogger(__name__)

# Default evidence directory relative to repo root.
DEFAULT_EVIDENCE_DIR = Path(".agent/evidence")

# Async batch writer defaults.
_DEFAULT_FLUSH_INTERVAL_SECS = 1.0
_DEFAULT_MAX_BUFFER_SIZE = 100


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


class EvidenceWriter(Protocol):
    """Protocol for evidence writers — sync or async."""

    def write(self, line: str) -> None: ...

    def flush(self) -> None: ...

    def close(self) -> None: ...


class SyncEvidenceWriter:
    """Synchronous, append-only NDJSON writer.

    Opens/closes the file on every write. Maximum durability,
    higher latency (~14ms overhead per write due to file I/O).
    """

    def __init__(self, evidence_file: Path) -> None:
        self._evidence_file = evidence_file

    def write(self, line: str) -> None:
        with self._evidence_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def flush(self) -> None:
        pass  # Each write is self-flushing.

    def close(self) -> None:
        pass  # No persistent handle.


class AsyncBatchEvidenceWriter:
    """Buffered, thread-safe NDJSON writer with periodic flush.

    Accumulates evidence records in memory and flushes them to disk
    either when the buffer reaches max_buffer_size or every
    flush_interval_secs, whichever comes first.

    This eliminates per-call file I/O overhead (52% of dispatch time
    per cProfile analysis), reducing median dispatch from ~55µs to ~20µs.

    Thread safety: Uses a threading.Lock for the buffer and a daemon
    timer thread for periodic flushing. The flush itself is atomic
    at the NDJSON level (writes complete lines).
    """

    def __init__(
        self,
        evidence_file: Path,
        *,
        flush_interval_secs: float = _DEFAULT_FLUSH_INTERVAL_SECS,
        max_buffer_size: int = _DEFAULT_MAX_BUFFER_SIZE,
    ) -> None:
        self._evidence_file = evidence_file
        self._flush_interval = flush_interval_secs
        self._max_buffer_size = max_buffer_size
        self._buffer: deque[str] = deque()
        self._lock = threading.Lock()
        self._closed = False
        self._timer: threading.Timer | None = None
        self._start_timer()
        atexit.register(self.close)

    def _start_timer(self) -> None:
        """Schedule the next periodic flush."""
        if self._closed:
            return
        self._timer = threading.Timer(self._flush_interval, self._periodic_flush)
        self._timer.daemon = True
        self._timer.start()

    def _periodic_flush(self) -> None:
        """Timer callback — flush buffer and reschedule."""
        self.flush()
        self._start_timer()

    def write(self, line: str) -> None:
        """Buffer a line for later flushing.

        If the buffer exceeds max_buffer_size, triggers an immediate flush.
        """
        if self._closed:
            logger.warning("Write attempted on closed AsyncBatchEvidenceWriter")
            return
        with self._lock:
            self._buffer.append(line + "\n")
            if len(self._buffer) >= self._max_buffer_size:
                self._flush_locked()

    def flush(self) -> None:
        """Flush all buffered lines to disk."""
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        """Internal flush — caller must hold self._lock."""
        if not self._buffer:
            return
        lines = list(self._buffer)
        self._buffer.clear()
        try:
            with self._evidence_file.open("a", encoding="utf-8") as f:
                f.writelines(lines)
        except OSError:
            logger.exception("Evidence flush failed — %d records lost", len(lines))

    def close(self) -> None:
        """Flush remaining records and stop the timer."""
        self._closed = True
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self.flush()

    @property
    def pending_count(self) -> int:
        """Number of records waiting in the buffer."""
        with self._lock:
            return len(self._buffer)


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

    For lower latency, use the async writer:
        evidence = EvidenceLogger(repo_root=Path("."), async_writes=True)
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        *,
        async_writes: bool = False,
        flush_interval_secs: float = _DEFAULT_FLUSH_INTERVAL_SECS,
        max_buffer_size: int = _DEFAULT_MAX_BUFFER_SIZE,
    ) -> None:
        """Initialize the evidence logger.

        Args:
            repo_root: Path to the monorepo root. Defaults to current directory.
            async_writes: If True, use buffered async writer for lower latency.
            flush_interval_secs: Flush interval for async writer.
            max_buffer_size: Max buffer size before forced flush.
        """
        self._repo_root = repo_root or Path(".")
        self._evidence_dir = self._repo_root / DEFAULT_EVIDENCE_DIR
        self._evidence_file = self._evidence_dir / "function_calls.ndjson"
        self._evidence_dir.mkdir(parents=True, exist_ok=True)

        if async_writes:
            self._writer: SyncEvidenceWriter | AsyncBatchEvidenceWriter = AsyncBatchEvidenceWriter(
                self._evidence_file,
                flush_interval_secs=flush_interval_secs,
                max_buffer_size=max_buffer_size,
            )
        else:
            self._writer = SyncEvidenceWriter(self._evidence_file)

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
        self._writer.write(line)

        logger.info(
            "Evidence logged: %s (risk=%s, %sms)",
            function_name,
            risk_tier,
            f"{duration_ms:.1f}",
        )
        return record

    def flush(self) -> None:
        """Force-flush any buffered records to disk."""
        self._writer.flush()

    def close(self) -> None:
        """Close the writer, flushing any remaining records."""
        self._writer.close()

    @staticmethod
    def timer() -> float:
        """Return a high-resolution timestamp for timing function calls."""
        return time.perf_counter()

    @staticmethod
    def elapsed_ms(start: float) -> float:
        """Calculate elapsed milliseconds since start."""
        return (time.perf_counter() - start) * 1000
