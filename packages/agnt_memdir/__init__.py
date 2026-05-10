# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""agnt_memdir — Skeptical Index Memory Directory.

Ported from Claude Code's 3-layer Memory Pointer Index:
  - Hot store: In-memory LRU cache for current-session KIs
  - Warm store: Filesystem-backed index (~/.gemini/antigravity/knowledge/)
  - Cold store: Archive of expired/superseded KIs with retention policy

The Skeptical Index maintains provenance metadata for every memory entry:
  - source_conversation_id: originating conversation
  - confidence_score: 0.0–1.0 from the consolidation engine
  - last_accessed: ISO8601 timestamp for LRU eviction
  - expires_at: optional expiry for time-bounded facts
  - superseded_by: pointer to replacement KI if deprecated

Architecture:
  Memory queries flow: Hot → Warm → Cold (with optional cold-store revival)
  Writes flow: Hot → (flush) → Warm → (dream consolidation) → Cold/Prune
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

DEFAULT_HOT_CAPACITY = 128
DEFAULT_COLD_RETENTION_DAYS = 90
DEFAULT_EXPIRY_CHECK_INTERVAL_S = 3600  # 1 hour


@dataclass(frozen=True)
class MemoryEntry:
  """A single knowledge item in the Skeptical Index."""

  key: str
  value: str
  source_conversation_id: str = ""
  confidence_score: float = 1.0
  created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
  last_accessed: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
  expires_at: str | None = None
  superseded_by: str | None = None
  tags: tuple[str, ...] = ()

  @property
  def is_expired(self) -> bool:
    """Check if entry has passed its expiry time."""
    if self.expires_at is None:
      return False
    try:
      expiry = datetime.fromisoformat(self.expires_at)
      return datetime.now(UTC) > expiry
    except ValueError, TypeError:
      return False

  @property
  def is_superseded(self) -> bool:
    """Check if entry has been replaced by a newer KI."""
    return self.superseded_by is not None

  @property
  def age_seconds(self) -> float:
    """Seconds since creation."""
    try:
      created = datetime.fromisoformat(self.created_at)
      return (datetime.now(UTC) - created).total_seconds()
    except ValueError, TypeError:
      return 0.0


class HotStore:
  """In-memory LRU cache for current-session knowledge items.

  Bounded by capacity. Evicts least-recently-accessed entries first.
  Thread-safe via the GIL for single-process use.
  """

  def __init__(self, capacity: int = DEFAULT_HOT_CAPACITY) -> None:
    self._capacity = capacity
    self._store: dict[str, MemoryEntry] = {}
    self._access_order: list[str] = []

  def get(self, key: str) -> MemoryEntry | None:
    """Retrieve entry and promote in access order."""
    entry = self._store.get(key)
    if entry is None:
      return None
    if entry.is_expired or entry.is_superseded:
      self._evict(key)
      return None
    # Promote to most-recently-accessed
    if key in self._access_order:
      self._access_order.remove(key)
    self._access_order.append(key)
    return entry

  def put(self, entry: MemoryEntry) -> None:
    """Insert or update an entry. Evict LRU if at capacity."""
    if entry.key in self._store:
      self._access_order.remove(entry.key)
    elif len(self._store) >= self._capacity:
      self._evict_lru()
    self._store[entry.key] = entry
    self._access_order.append(entry.key)

  def _evict(self, key: str) -> MemoryEntry | None:
    """Remove a specific key."""
    entry = self._store.pop(key, None)
    if key in self._access_order:
      self._access_order.remove(key)
    return entry

  def _evict_lru(self) -> MemoryEntry | None:
    """Evict the least-recently-accessed entry."""
    if not self._access_order:
      return None
    lru_key = self._access_order[0]
    return self._evict(lru_key)

  @property
  def size(self) -> int:
    return len(self._store)

  def keys(self) -> list[str]:
    return list(self._store.keys())

  def clear(self) -> None:
    self._store.clear()
    self._access_order.clear()


class WarmStore:
  """Filesystem-backed knowledge index.

  Reads from the canonical knowledge directory structure:
    knowledge/<ki-name>/metadata.json
    knowledge/<ki-name>/artifacts/

  Lazy-loaded on first access. Supports incremental refresh.
  """

  def __init__(self, knowledge_dir: str | Path | None = None) -> None:
    self._knowledge_dir = (
      Path(knowledge_dir) if knowledge_dir else self._default_knowledge_dir()
    )
    self._index: dict[str, MemoryEntry] = {}
    self._loaded = False

  @staticmethod
  def _default_knowledge_dir() -> Path:
    """Resolve the canonical knowledge directory."""
    base = os.environ.get(
      "ANTIGRAVITY_DATA_DIR", os.path.expanduser("~/.gemini/antigravity")
    )
    return Path(base) / "knowledge"

  def load(self, *, force: bool = False) -> int:
    """Scan knowledge directory and build index. Returns count loaded."""
    if self._loaded and not force:
      return len(self._index)

    count = 0
    if not self._knowledge_dir.is_dir():
      logger.debug("Knowledge directory not found: %s", self._knowledge_dir)
      self._loaded = True
      return 0

    for ki_dir in sorted(self._knowledge_dir.iterdir()):
      if not ki_dir.is_dir() or ki_dir.name.startswith((".", "_")):
        continue
      metadata_file = ki_dir / "metadata.json"
      if not metadata_file.is_file():
        continue
      try:
        meta = json.loads(metadata_file.read_text(encoding="utf-8"))
        entry = MemoryEntry(
          key=ki_dir.name,
          value=meta.get("summary", ""),
          source_conversation_id=meta.get("source_conversation_id", ""),
          confidence_score=float(meta.get("confidence_score", 1.0)),
          created_at=meta.get("created_at", datetime.now(UTC).isoformat()),
          last_accessed=meta.get("last_accessed", datetime.now(UTC).isoformat()),
          expires_at=meta.get("expires_at"),
          superseded_by=meta.get("superseded_by"),
          tags=tuple(meta.get("tags", [])),
        )
        if not entry.is_expired and not entry.is_superseded:
          self._index[ki_dir.name] = entry
          count += 1
      except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.warning("Skipping malformed KI %s: %s", ki_dir.name, exc)

    self._loaded = True
    logger.info("WarmStore loaded %d KIs from %s", count, self._knowledge_dir)
    return count

  def get(self, key: str) -> MemoryEntry | None:
    """Look up a KI by name."""
    if not self._loaded:
      self.load()
    return self._index.get(key)

  def search(self, query: str, *, limit: int = 10) -> list[MemoryEntry]:
    """Simple substring search across KI names and summaries."""
    if not self._loaded:
      self.load()
    query_lower = query.lower()
    results: list[MemoryEntry] = []
    for entry in self._index.values():
      if query_lower in entry.key.lower() or query_lower in entry.value.lower():
        results.append(entry)
        if len(results) >= limit:
          break
    return results

  @property
  def size(self) -> int:
    if not self._loaded:
      self.load()
    return len(self._index)

  def keys(self) -> list[str]:
    if not self._loaded:
      self.load()
    return list(self._index.keys())


class ColdStore:
  """Archive for expired/superseded KIs with retention policy.

  Cold storage lives at:
    knowledge/_cold_archive/<ki-name>/metadata.json

  Entries here are preserved for audit/revival but excluded from
  normal query flow. The retention policy automatically purges
  entries older than cold_retention_days.
  """

  def __init__(
    self,
    archive_dir: str | Path | None = None,
    retention_days: int = DEFAULT_COLD_RETENTION_DAYS,
  ) -> None:
    if archive_dir:
      self._archive_dir = Path(archive_dir)
    else:
      base = os.environ.get(
        "ANTIGRAVITY_DATA_DIR", os.path.expanduser("~/.gemini/antigravity")
      )
      self._archive_dir = Path(base) / "knowledge" / "_cold_archive"
    self._retention_days = retention_days
    self._checkpoint_file = self._archive_dir / ".expiry_checkpoint.json"

  def archive(self, entry: MemoryEntry, *, reason: str = "expired") -> bool:
    """Move an entry to cold storage."""
    try:
      entry_dir = self._archive_dir / entry.key
      entry_dir.mkdir(parents=True, exist_ok=True)
      metadata = {
        **asdict(entry),
        "archived_at": datetime.now(UTC).isoformat(),
        "archive_reason": reason,
        "tags": list(entry.tags),
      }
      (entry_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, default=str),
        encoding="utf-8",
      )
      logger.info("Archived KI to cold storage: %s (reason=%s)", entry.key, reason)
      return True
    except OSError as exc:
      logger.error("Failed to archive %s: %s", entry.key, exc)
      return False

  def revive(self, key: str) -> MemoryEntry | None:
    """Retrieve an entry from cold storage for revival."""
    meta_file = self._archive_dir / key / "metadata.json"
    if not meta_file.is_file():
      return None
    try:
      meta = json.loads(meta_file.read_text(encoding="utf-8"))
      return MemoryEntry(
        key=meta["key"],
        value=meta.get("value", ""),
        source_conversation_id=meta.get("source_conversation_id", ""),
        confidence_score=float(meta.get("confidence_score", 0.5)),
        created_at=meta.get("created_at", datetime.now(UTC).isoformat()),
        last_accessed=datetime.now(UTC).isoformat(),
        expires_at=None,  # Clear expiry on revival
        superseded_by=None,
        tags=tuple(meta.get("tags", [])),
      )
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
      logger.warning("Failed to revive %s: %s", key, exc)
      return None

  def purge_expired(self) -> int:
    """Remove cold entries older than retention_days. Returns count purged."""
    if not self._archive_dir.is_dir():
      return 0
    cutoff = time.time() - (self._retention_days * 86400)
    purged = 0
    for entry_dir in sorted(self._archive_dir.iterdir()):
      if not entry_dir.is_dir():
        continue
      meta_file = entry_dir / "metadata.json"
      if not meta_file.is_file():
        continue
      try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        archived_at = meta.get("archived_at", "")
        if archived_at:
          archived_dt = datetime.fromisoformat(archived_at)
          if archived_dt.timestamp() < cutoff:
            # Archive-only: rename instead of delete (RULE 00)
            purge_marker = entry_dir / ".purged"
            purge_marker.write_text(
              datetime.now(UTC).isoformat(),
              encoding="utf-8",
            )
            purged += 1
            logger.info("Marked cold entry for purge: %s", entry_dir.name)
      except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Purge check failed for %s: %s", entry_dir.name, exc)
    return purged

  def list_entries(self) -> list[dict[str, Any]]:
    """List all non-purged cold archive entries for diagnostics."""
    if not self._archive_dir.is_dir():
      return []
    entries: list[dict[str, Any]] = []
    for entry_dir in sorted(self._archive_dir.iterdir()):
      if not entry_dir.is_dir() or (entry_dir / ".purged").exists():
        continue
      meta_file = entry_dir / "metadata.json"
      if meta_file.is_file():
        try:
          meta = json.loads(meta_file.read_text(encoding="utf-8"))
          entries.append(
            {
              "key": meta.get("key", entry_dir.name),
              "archived_at": meta.get("archived_at", ""),
              "reason": meta.get("archive_reason", "unknown"),
              "confidence": meta.get("confidence_score", 0.0),
            }
          )
        except json.JSONDecodeError, ValueError:
          entries.append({"key": entry_dir.name, "error": "malformed"})
    return entries

  def save_expiry_checkpoint(self, timestamp: float) -> None:
    """Persist the last expiry sweep timestamp to survive restarts."""
    try:
      self._archive_dir.mkdir(parents=True, exist_ok=True)
      self._checkpoint_file.write_text(
        json.dumps({"last_expiry_check": timestamp}, indent=2),
        encoding="utf-8",
      )
    except OSError as exc:
      logger.warning("Failed to save expiry checkpoint: %s", exc)

  def load_expiry_checkpoint(self) -> float:
    """Load the last expiry sweep timestamp. Returns 0.0 if not found."""
    if not self._checkpoint_file.is_file():
      return 0.0
    try:
      data = json.loads(self._checkpoint_file.read_text(encoding="utf-8"))
      return float(data.get("last_expiry_check", 0.0))
    except json.JSONDecodeError, ValueError, OSError:
      return 0.0

  @property
  def size(self) -> int:
    if not self._archive_dir.is_dir():
      return 0
    return sum(
      1
      for d in self._archive_dir.iterdir()
      if d.is_dir() and not (d / ".purged").exists()
    )


class SkepticalIndex:
  """Three-tier memory index: Hot → Warm → Cold.

  Query flow:
    1. Check hot store (in-memory LRU)
    2. On miss, check warm store (filesystem KIs)
    3. On miss, optionally check cold store (archived KIs)

  Write flow:
    1. New entries go to hot store
    2. Flush promotes hot → warm (via dream consolidation)
    3. Expired/superseded warm entries → cold archive
  """

  def __init__(
    self,
    *,
    hot_capacity: int = DEFAULT_HOT_CAPACITY,
    knowledge_dir: str | Path | None = None,
    cold_archive_dir: str | Path | None = None,
    cold_retention_days: int = DEFAULT_COLD_RETENTION_DAYS,
  ) -> None:
    self.hot = HotStore(capacity=hot_capacity)
    self.warm = WarmStore(knowledge_dir=knowledge_dir)
    self.cold = ColdStore(
      archive_dir=cold_archive_dir, retention_days=cold_retention_days
    )
    # Restore expiry checkpoint from cold store persistence
    self._last_expiry_check = self.cold.load_expiry_checkpoint()

  def get(self, key: str, *, include_cold: bool = False) -> MemoryEntry | None:
    """Query the three-tier index."""
    # Tier 1: Hot
    entry = self.hot.get(key)
    if entry is not None:
      return entry

    # Tier 2: Warm
    entry = self.warm.get(key)
    if entry is not None:
      self.hot.put(entry)  # Promote to hot
      return entry

    # Tier 3: Cold (optional)
    if include_cold:
      entry = self.cold.revive(key)
      if entry is not None:
        self.hot.put(entry)
        return entry

    return None

  def put(self, entry: MemoryEntry) -> None:
    """Insert into the hot store."""
    self.hot.put(entry)

  def search(
    self, query: str, *, limit: int = 10, include_cold: bool = False
  ) -> list[MemoryEntry]:
    """Search across warm store (hot is too small for meaningful search)."""
    return self.warm.search(query, limit=limit)

  def cold_list(self) -> list[dict[str, Any]]:
    """Diagnostic listing of all cold archive entries."""
    return self.cold.list_entries()

  def run_expiry_sweep(self) -> dict[str, int]:
    """Check for expired entries and archive them. Returns stats."""
    now = time.time()
    if now - self._last_expiry_check < DEFAULT_EXPIRY_CHECK_INTERVAL_S:
      return {"skipped": True}

    self._last_expiry_check = now
    archived = 0
    purged = 0

    # Sweep warm store for expired entries
    for key in list(self.warm.keys()):
      entry = self.warm.get(key)
      if entry and (entry.is_expired or entry.is_superseded):
        reason = "superseded" if entry.is_superseded else "expired"
        if self.cold.archive(entry, reason=reason):
          archived += 1

    # Purge cold entries past retention
    purged = self.cold.purge_expired()

    # Persist checkpoint for restart resilience
    self.cold.save_expiry_checkpoint(self._last_expiry_check)

    return {"archived": archived, "purged": purged, "skipped": False}

  def stats(self) -> dict[str, Any]:
    """Return diagnostic stats for the index."""
    return {
      "hot_size": self.hot.size,
      "warm_size": self.warm.size,
      "cold_size": self.cold.size,
      "total": self.hot.size + self.warm.size + self.cold.size,
    }


# ── Module exports ─────────────────────────────────────────────────────────

__all__ = [
  "ColdStore",
  "HotStore",
  "MemoryEntry",
  "SkepticalIndex",
  "WarmStore",
]
