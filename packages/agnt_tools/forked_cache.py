# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Forked Agent Cache-Hit — P1 #9. Caches speculative pre-computation results."""

from __future__ import annotations
import hashlib, json, logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger("agnt.forked_cache")
CACHE_DIR = Path.home() / ".gemini" / "antigravity" / "Monorepo-Uphillsnowball" / ".beads" / "spec_cache"


@dataclass
class CacheEntry:
    key: str
    value: str
    created_at: str
    hit_count: int = 0
    ttl_seconds: int = 3600


@dataclass
class CacheStats:
    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0


class ForkedAgentCache:
    """Cache for speculative pre-computation (P1 #9).
    When the speculation engine pre-computes a suggestion, the result is
    cached here. If the user's actual request matches, it's a cache hit
    and the response is nearly instant.
    """

    def __init__(self, max_entries: int = 100, default_ttl: int = 3600):
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def put(self, prompt: str, result: str, ttl: int | None = None) -> str:
        key = self._hash(prompt)
        entry = CacheEntry(key=key, value=result, created_at=datetime.now(UTC).isoformat(), ttl_seconds=ttl or self.default_ttl)
        (CACHE_DIR / f"{key}.json").write_text(
            json.dumps({"key": entry.key, "value": entry.value, "created_at": entry.created_at, "hit_count": 0, "ttl_seconds": entry.ttl_seconds})
        )
        self._evict_if_needed()
        return key

    def get(self, prompt: str) -> str | None:
        key = self._hash(prompt)
        path = CACHE_DIR / f"{key}.json"
        if not path.exists():
            self._misses += 1
            return None
        try:
            data = json.loads(path.read_text())
            created = datetime.fromisoformat(data["created_at"])
            age = (datetime.now(UTC) - created).total_seconds()
            if age > data.get("ttl_seconds", self.default_ttl):
                path.unlink()
                self._misses += 1
                return None
            data["hit_count"] = data.get("hit_count", 0) + 1
            path.write_text(json.dumps(data))
            self._hits += 1
            return data["value"]
        except json.JSONDecodeError, KeyError, OSError:
            self._misses += 1
            return None

    def stats(self) -> CacheStats:
        total = len(list(CACHE_DIR.glob("*.json")))
        total_attempts = self._hits + self._misses
        return CacheStats(
            total_entries=total, hits=self._hits, misses=self._misses, hit_rate=self._hits / total_attempts if total_attempts > 0 else 0
        )

    def _hash(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]

    def _evict_if_needed(self):
        files = sorted(CACHE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime)
        while len(files) > self.max_entries:
            files[0].unlink()
            files.pop(0)
