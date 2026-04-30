# Copyright 2026 ShadowTag-v2. All rights reserved.
# SPDX-License-Identifier: Proprietary
#
# Session Ingress — Filesystem-Backed Persistence Layer
#
# Ported from Claude Code's sessionIngress.ts (515 LOC).
# Architectural patterns preserved:
#   - Sequential per-session execution (prevents concurrent writes)
#   - Optimistic concurrency via UUID chaining (Last-UUID header → file chain)
#   - 409 conflict resolution (adopt server UUID or re-fetch)
#   - Exponential backoff with retry cap
#   - Paginated cursor-based retrieval with infinite-loop guard
#
# Adaptations:
#   - HTTP → filesystem (JSONL append logs)
#   - Axios/Spanner → pathlib + fcntl advisory locks
#   - JWT auth → filesystem ACL (local-only)
#   - Teleport events → log hydration from file

from __future__ import annotations

import asyncio
import fcntl
import json
import logging
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration constants (mirroring sessionIngress.ts)
# ---------------------------------------------------------------------------

MAX_RETRIES: int = 10
BASE_DELAY_MS: int = 500
MAX_DELAY_MS: int = 8000
MAX_PAGES: int = 100
DEFAULT_PAGE_SIZE: int = 500

# ---------------------------------------------------------------------------
# Data Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TranscriptEntry:
    """A single log entry in the session transcript.

    Mirrors Claude Code's TranscriptMessage type. The ``uuid`` field
    enables optimistic concurrency — each append references the UUID of
    the previous entry, forming a forward-linked chain. The server (here:
    filesystem) rejects writes whose ``last_uuid`` doesn't match the
    stored head, returning a 409-equivalent.
    """

    entry_uuid: str
    timestamp: float
    role: str  # 'user' | 'assistant' | 'system' | 'tool'
    content: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        d: dict[str, Any] = {
            "uuid": self.entry_uuid,
            "timestamp": self.timestamp,
            "role": self.role,
            "content": self.content,
        }
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscriptEntry:
        """Deserialize from a JSON dict."""
        return cls(
            entry_uuid=data["uuid"],
            timestamp=data.get("timestamp", 0.0),
            role=data.get("role", "system"),
            content=data.get("content", ""),
            metadata=data.get("metadata"),
        )


# ---------------------------------------------------------------------------
# Session Lock — Per-Session Sequential Execution
# ---------------------------------------------------------------------------
#
# Claude Code uses a ``sequential()`` wrapper per session to prevent
# concurrent log writes. We replicate this with asyncio.Lock keyed by
# session ID + filesystem advisory locking (fcntl) for cross-process
# safety.

_session_locks: dict[str, asyncio.Lock] = {}
_last_uuid_map: dict[str, str] = {}


def _get_session_lock(session_id: str) -> asyncio.Lock:
    """Get or create an asyncio.Lock for sequential per-session access."""
    if session_id not in _session_locks:
        _session_locks[session_id] = asyncio.Lock()
    return _session_locks[session_id]


def _session_log_path(base_dir: Path, session_id: str) -> Path:
    """Canonical path for a session's JSONL transcript log."""
    session_dir = base_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / "transcript.jsonl"


def _session_head_path(base_dir: Path, session_id: str) -> Path:
    """Path for the session's UUID chain head pointer."""
    session_dir = base_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / ".head_uuid"


# ---------------------------------------------------------------------------
# Core Write — Optimistic Concurrency with UUID Chaining
# ---------------------------------------------------------------------------


def _read_head_uuid(head_path: Path) -> str | None:
    """Read the current chain head UUID from the head pointer file."""
    if not head_path.exists():
        return None
    content = head_path.read_text().strip()
    return content if content else None


def _write_head_uuid(head_path: Path, entry_uuid: str) -> None:
    """Atomically update the chain head UUID."""
    # Write to temp file then rename for atomic update
    tmp_path = head_path.with_suffix(".tmp")
    tmp_path.write_text(entry_uuid)
    tmp_path.rename(head_path)


def _append_entry_with_lock(
    log_path: Path,
    head_path: Path,
    entry: TranscriptEntry,
    expected_last_uuid: str | None,
) -> tuple[bool, str | None]:
    """Append an entry to the JSONL log with filesystem advisory locking.

    Returns:
        (success, server_head_uuid) — On conflict (409-equivalent),
        ``success`` is False and ``server_head_uuid`` is the current
        chain head so the caller can adopt and retry.
    """
    # Open the log file for appending with an exclusive lock
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Use fcntl advisory lock for cross-process safety
    with open(log_path, "a+") as f:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            # Lock contention — treat as a transient error (retryable)
            logger.warning("Lock contention on %s, will retry", log_path)
            return False, None

        try:
            # Check the chain head — 409-equivalent
            current_head = _read_head_uuid(head_path)

            if current_head != expected_last_uuid:
                # Check if our entry is already the head (stale state recovery)
                if current_head == entry.entry_uuid:
                    logger.info(
                        "Entry %s already present on disk, recovering from stale state",
                        entry.entry_uuid,
                    )
                    return True, current_head

                # Conflict: another writer advanced the chain
                logger.warning(
                    "UUID chain conflict: expected=%s, actual=%s",
                    expected_last_uuid,
                    current_head,
                )
                return False, current_head

            # Write the entry
            line = json.dumps(entry.to_dict(), separators=(",", ":"))
            f.write(line + "\n")
            f.flush()

            # Advance the chain head
            _write_head_uuid(head_path, entry.entry_uuid)

            return True, entry.entry_uuid
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


# ---------------------------------------------------------------------------
# Public API — Append with Retry (mirrors appendSessionLog)
# ---------------------------------------------------------------------------


async def append_session_log(
    base_dir: Path,
    session_id: str,
    entry: TranscriptEntry,
) -> bool:
    """Append a transcript entry to a session's log.

    Uses sequential per-session locking and optimistic concurrency with
    exponential backoff. Mirrors Claude Code's ``appendSessionLog()``
    behavior including 409 conflict resolution via UUID chain adoption.

    Args:
        base_dir: Root directory for session logs.
        session_id: Unique session identifier.
        entry: The transcript entry to append.

    Returns:
        True if the entry was successfully persisted.
    """
    lock = _get_session_lock(session_id)

    async with lock:
        log_path = _session_log_path(base_dir, session_id)
        head_path = _session_head_path(base_dir, session_id)

        for attempt in range(1, MAX_RETRIES + 1):
            expected_last_uuid = _last_uuid_map.get(session_id)

            success, server_head = await asyncio.to_thread(
                _append_entry_with_lock,
                log_path,
                head_path,
                entry,
                expected_last_uuid,
            )

            if success:
                _last_uuid_map[session_id] = entry.entry_uuid
                logger.debug(
                    "Successfully persisted entry %s for session %s",
                    entry.entry_uuid,
                    session_id,
                )
                return True

            if server_head is not None:
                # 409-equivalent: adopt the disk head and retry
                if server_head == entry.entry_uuid:
                    # Already stored — success
                    _last_uuid_map[session_id] = entry.entry_uuid
                    return True

                _last_uuid_map[session_id] = server_head
                logger.info(
                    "Adopting disk head UUID=%s, retrying entry %s (attempt %d/%d)",
                    server_head,
                    entry.entry_uuid,
                    attempt,
                    MAX_RETRIES,
                )
                continue

            # Transient error (lock contention, etc.)
            if attempt == MAX_RETRIES:
                logger.error(
                    "Persistence failed after %d attempts for session %s",
                    MAX_RETRIES,
                    session_id,
                )
                return False

            # Exponential backoff (mirroring sessionIngress.ts L178)
            delay_s = (
                min(
                    BASE_DELAY_MS * (2 ** (attempt - 1)),
                    MAX_DELAY_MS,
                )
                / 1000.0
            )
            logger.debug(
                "Attempt %d/%d failed, retrying in %.1fs",
                attempt,
                MAX_RETRIES,
                delay_s,
            )
            await asyncio.sleep(delay_s)

    return False


# ---------------------------------------------------------------------------
# Public API — Read (mirrors getSessionLogs)
# ---------------------------------------------------------------------------


async def get_session_logs(
    base_dir: Path,
    session_id: str,
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_pages: int = MAX_PAGES,
    after_last_compact: bool = False,
) -> list[TranscriptEntry] | None:
    """Retrieve all transcript entries for a session.

    Mirrors Claude Code's ``getSessionLogs()`` + ``getTeleportEvents()``
    with paginated reading and an infinite-loop guard.

    Args:
        base_dir: Root directory for session logs.
        session_id: Unique session identifier.
        page_size: Number of entries per page (for memory efficiency).
        max_pages: Maximum pages to read (infinite-loop guard).
        after_last_compact: If True, only return entries after the last
            compaction marker.

    Returns:
        List of transcript entries, or None if session doesn't exist.
    """
    log_path = _session_log_path(base_dir, session_id)

    if not log_path.exists():
        logger.debug("No existing logs for session %s", session_id)
        return None

    entries: list[TranscriptEntry] = []
    pages_read = 0
    compaction_marker_seen = False

    def _read_entries() -> list[TranscriptEntry]:
        nonlocal pages_read, compaction_marker_seen
        result: list[TranscriptEntry] = []

        with open(log_path) as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning(
                        "Skipping malformed JSON at line %d in %s",
                        line_num + 1,
                        log_path,
                    )
                    continue

                # Check for compaction markers
                if after_last_compact and data.get("role") == "compaction":
                    compaction_marker_seen = True
                    result.clear()
                    continue

                result.append(TranscriptEntry.from_dict(data))

                # Page size guard
                if len(result) >= page_size:
                    pages_read += 1
                    if pages_read >= max_pages:
                        logger.warning(
                            "Hit page cap (%d) for session %s, returning partial",
                            max_pages,
                            session_id,
                        )
                        break
                    # Continue reading (accumulating into result)

        return result

    entries = await asyncio.to_thread(_read_entries)

    if entries:
        # Update our lastUuid to the last entry's UUID (mirrors L233-236)
        last_entry = entries[-1]
        _last_uuid_map[session_id] = last_entry.entry_uuid

    logger.debug(
        "Fetched %d entries for session %s (%d pages)",
        len(entries),
        session_id,
        pages_read + 1,
    )
    return entries


# ---------------------------------------------------------------------------
# Public API — Session Lifecycle
# ---------------------------------------------------------------------------


def create_entry(
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> TranscriptEntry:
    """Create a new transcript entry with a fresh UUID and timestamp.

    Convenience factory that generates uuid7 (time-ordered) when available,
    falling back to uuid4.
    """
    try:
        # Prefer uuid7 for time-ordered UUIDs (monorepo pattern)
        from apps.counselconduit.api.uuid7 import uuid7  # type: ignore[import-untyped]

        entry_uuid = str(uuid7())
    except ImportError:
        try:
            from api.uuid7 import uuid7  # type: ignore[import-untyped]

            entry_uuid = str(uuid7())
        except ImportError:
            entry_uuid = str(uuid.uuid4())

    return TranscriptEntry(
        entry_uuid=entry_uuid,
        timestamp=time.time(),
        role=role,
        content=content,
        metadata=metadata,
    )


def clear_session(session_id: str) -> None:
    """Clear cached state for a session (mirrors clearSession).

    Does NOT delete the on-disk logs — only clears in-memory caches
    (UUID chain head + asyncio lock). Follows RULE_00 immutable
    infrastructure: archive, never delete.
    """
    _last_uuid_map.pop(session_id, None)
    _session_locks.pop(session_id, None)
    logger.debug("Cleared cached state for session %s", session_id)


def clear_all_sessions() -> None:
    """Clear all cached session state (mirrors clearAllSessions).

    Use this on context reset (/clear) to free sub-agent session
    entries from memory. On-disk logs are preserved per RULE_00.
    """
    _last_uuid_map.clear()
    _session_locks.clear()
    logger.debug("Cleared all cached session state")


# ---------------------------------------------------------------------------
# Compaction Integration
# ---------------------------------------------------------------------------


async def write_compaction_marker(
    base_dir: Path,
    session_id: str,
    summary: str,
) -> bool:
    """Write a compaction marker entry to the session log.

    After context compaction runs, this inserts a marker so that
    ``get_session_logs(after_last_compact=True)`` can skip
    pre-compaction history. This mirrors Claude Code's
    ``CLAUDE_AFTER_LAST_COMPACT`` env var behavior.
    """
    marker = create_entry(
        role="compaction",
        content=summary,
        metadata={"type": "compaction_marker", "compacted_at": time.time()},
    )
    return await append_session_log(base_dir, session_id, marker)


# ---------------------------------------------------------------------------
# Session Statistics
# ---------------------------------------------------------------------------


async def get_session_stats(
    base_dir: Path,
    session_id: str,
) -> dict[str, Any] | None:
    """Get statistics for a session's transcript log.

    Returns entry count, size on disk, role distribution, and time span.
    Useful for the telemetry/diagnostics layer.
    """
    log_path = _session_log_path(base_dir, session_id)
    if not log_path.exists():
        return None

    entries = await get_session_logs(base_dir, session_id)
    if entries is None:
        return None

    role_counts: dict[str, int] = {}
    for entry in entries:
        role_counts[entry.role] = role_counts.get(entry.role, 0) + 1

    timestamps = [e.timestamp for e in entries if e.timestamp > 0]
    time_span_s = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0.0

    return {
        "session_id": session_id,
        "entry_count": len(entries),
        "size_bytes": log_path.stat().st_size,
        "role_distribution": role_counts,
        "time_span_seconds": round(time_span_s, 2),
        "first_entry": entries[0].timestamp if entries else None,
        "last_entry": entries[-1].timestamp if entries else None,
        "head_uuid": _last_uuid_map.get(session_id),
    }
