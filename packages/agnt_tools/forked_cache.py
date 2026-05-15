# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Forked Agent Cache-Hit — P1 #9. Caches speculative pre-computation results.

Supports namespace isolation (spec/compact/kairos) with per-namespace TTL,
structural fingerprinting for fuzzy matches, and bulk eviction.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("agnt.forked_cache")

# Base cache directory — namespaces create subdirectories
CACHE_BASE_DIR = (
  Path.home()
  / ".gemini"
  / "antigravity"
  / "Monorepo-Uphillsnowball"
  / ".beads"
  / "spec_cache"
)

# Legacy alias for backward compatibility
CACHE_DIR = CACHE_BASE_DIR

# Per-namespace default TTLs (seconds)
NAMESPACE_TTLS: dict[str, int] = {
  "spec": 3600,  # 1 hour — speculation engine pre-computation
  "compact": 1800,  # 30 min — compaction pipeline results stale faster
  "kairos": 900,  # 15 min — suggestions expire quickly
}


@dataclass
class CacheEntry:
  key: str
  value: str
  created_at: str
  namespace: str = "spec"
  hit_count: int = 0
  ttl_seconds: int = 3600
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStats:
  total_entries: int = 0
  hits: int = 0
  misses: int = 0
  hit_rate: float = 0
  entries_by_namespace: dict[str, int] = field(default_factory=dict)


class ForkedAgentCache:
  """Cache for speculative pre-computation (P1 #9).

  When the speculation engine pre-computes a suggestion, the result is
  cached here. If the user's actual request matches, it's a cache hit
  and the response is nearly instant.

  Namespaces:
    - "spec"    — speculation engine pre-computation (default, backward compat)
    - "compact" — compaction pipeline results
    - "kairos"  — KAIROS suggestion pre-fills
  """

  def __init__(self, max_entries: int = 100, default_ttl: int = 3600):
    self.max_entries = max_entries
    self.default_ttl = default_ttl
    self._hits = 0
    self._misses = 0
    CACHE_BASE_DIR.mkdir(parents=True, exist_ok=True)

  def _namespace_dir(self, namespace: str) -> Path:
    """Get or create the directory for a given namespace."""
    if namespace == "spec":
      # Legacy: spec namespace uses the base directory for backward compat
      return CACHE_BASE_DIR
    ns_dir = CACHE_BASE_DIR / namespace
    ns_dir.mkdir(parents=True, exist_ok=True)
    return ns_dir

  def put(
    self,
    prompt: str,
    result: str,
    ttl: int | None = None,
    namespace: str = "spec",
    metadata: dict[str, Any] | None = None,
  ) -> str:
    """Store a cache entry.

    Args:
      prompt: The prompt text (hashed for key generation).
      result: The cached result value.
      ttl: Time-to-live in seconds. Defaults to namespace TTL.
      namespace: Cache namespace ("spec", "compact", "kairos").
      metadata: Optional metadata dict stored alongside the entry.

    Returns:
      The cache key (hex digest).
    """
    key = self._hash(prompt)
    effective_ttl = ttl or NAMESPACE_TTLS.get(namespace, self.default_ttl)
    ns_dir = self._namespace_dir(namespace)

    entry_data = {
      "key": key,
      "value": result,
      "created_at": datetime.now(UTC).isoformat(),
      "hit_count": 0,
      "ttl_seconds": effective_ttl,
      "namespace": namespace,
      "metadata": metadata or {},
    }
    (ns_dir / f"{key}.json").write_text(json.dumps(entry_data))
    self._evict_if_needed(namespace)
    return key

  def get(
    self,
    prompt: str,
    namespace: str = "spec",
  ) -> str | None:
    """Retrieve a cache entry by exact prompt match.

    Args:
      prompt: The prompt text to look up.
      namespace: Cache namespace to search.

    Returns:
      Cached value string, or None on miss/expiry.
    """
    key = self._hash(prompt)
    ns_dir = self._namespace_dir(namespace)
    path = ns_dir / f"{key}.json"
    if not path.exists():
      self._misses += 1
      return None
    try:
      data = json.loads(path.read_text())
      created = datetime.fromisoformat(data["created_at"])
      age = (datetime.now(UTC) - created).total_seconds()
      effective_ttl = data.get(
        "ttl_seconds",
        NAMESPACE_TTLS.get(namespace, self.default_ttl),
      )
      if age > effective_ttl:
        path.unlink()
        self._misses += 1
        return None
      data["hit_count"] = data.get("hit_count", 0) + 1
      path.write_text(json.dumps(data))
      self._hits += 1
      return data["value"]
    except (json.JSONDecodeError, KeyError, OSError):
      self._misses += 1
      return None

  def put_structural(
    self,
    fingerprint: str,
    result: str,
    namespace: str = "compact",
    metadata: dict[str, Any] | None = None,
    ttl: int | None = None,
  ) -> str:
    """Store a cache entry using a pre-computed structural fingerprint.

    Unlike put(), this does NOT hash the input — the fingerprint is used
    directly as the key. Use this for compaction pipeline caching where
    the fingerprint is computed from message structure.
    """
    key = fingerprint[:16]
    effective_ttl = ttl or NAMESPACE_TTLS.get(namespace, self.default_ttl)
    ns_dir = self._namespace_dir(namespace)

    entry_data = {
      "key": key,
      "value": result,
      "created_at": datetime.now(UTC).isoformat(),
      "hit_count": 0,
      "ttl_seconds": effective_ttl,
      "namespace": namespace,
      "metadata": metadata or {},
      "fingerprint": fingerprint,
    }
    (ns_dir / f"{key}.json").write_text(json.dumps(entry_data))
    self._evict_if_needed(namespace)
    return key

  def get_structural(
    self,
    fingerprint: str,
    namespace: str = "compact",
  ) -> str | None:
    """Retrieve a cache entry by structural fingerprint."""
    key = fingerprint[:16]
    ns_dir = self._namespace_dir(namespace)
    path = ns_dir / f"{key}.json"
    if not path.exists():
      self._misses += 1
      return None
    try:
      data = json.loads(path.read_text())
      created = datetime.fromisoformat(data["created_at"])
      age = (datetime.now(UTC) - created).total_seconds()
      effective_ttl = data.get(
        "ttl_seconds",
        NAMESPACE_TTLS.get(namespace, self.default_ttl),
      )
      if age > effective_ttl:
        path.unlink()
        self._misses += 1
        return None
      data["hit_count"] = data.get("hit_count", 0) + 1
      path.write_text(json.dumps(data))
      self._hits += 1
      return data["value"]
    except (json.JSONDecodeError, KeyError, OSError):
      self._misses += 1
      return None

  def evict_namespace(self, namespace: str) -> int:
    """Remove all entries in a namespace. Returns count evicted."""
    ns_dir = self._namespace_dir(namespace)
    files = list(ns_dir.glob("*.json"))
    count = 0
    for f in files:
      try:
        f.unlink()
        count += 1
      except OSError:
        pass
    return count

  def warm_from_directory(self, directory: Path, namespace: str = "spec") -> int:
    """Load existing cache files from a directory into this namespace.

    Returns count of entries warmed.
    """
    if not directory.exists():
      return 0
    ns_dir = self._namespace_dir(namespace)
    count = 0
    for src in directory.glob("*.json"):
      dest = ns_dir / src.name
      if not dest.exists():
        try:
          dest.write_text(src.read_text())
          count += 1
        except OSError:
          pass
    return count

  def stats(self) -> CacheStats:
    """Return cache statistics across all namespaces."""
    entries_by_ns: dict[str, int] = {}

    # Count base directory (spec namespace)
    spec_count = len(list(CACHE_BASE_DIR.glob("*.json")))
    entries_by_ns["spec"] = spec_count

    # Count subdirectory namespaces
    for ns_dir in CACHE_BASE_DIR.iterdir():
      if ns_dir.is_dir() and ns_dir.name != "__pycache__":
        ns_count = len(list(ns_dir.glob("*.json")))
        if ns_count > 0:
          entries_by_ns[ns_dir.name] = ns_count

    total = sum(entries_by_ns.values())
    total_attempts = self._hits + self._misses
    return CacheStats(
      total_entries=total,
      hits=self._hits,
      misses=self._misses,
      hit_rate=self._hits / total_attempts if total_attempts > 0 else 0,
      entries_by_namespace=entries_by_ns,
    )

  def _hash(self, prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]

  def _evict_if_needed(self, namespace: str = "spec") -> None:
    ns_dir = self._namespace_dir(namespace)
    files = sorted(ns_dir.glob("*.json"), key=lambda f: f.stat().st_mtime)
    while len(files) > self.max_entries:
      files[0].unlink()
      files.pop(0)
