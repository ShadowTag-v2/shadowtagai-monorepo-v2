# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cached Session Store — Phase 4 M5.

Redis-backed read-through cache for FirestoreSessionStore. Designed for
high-frequency session hydration where the same session is read many times
during an attorney review cycle.

Architecture:
    CachedSessionStore → Redis (L1) → FirestoreSessionStore (L2)

Cache semantics:
    - READ: Redis first, Firestore on miss (read-through)
    - WRITE: Firestore first, then invalidate Redis (write-invalidate)
    - TTL: Cache entries expire independently (default: 5 minutes)
    - Serialization: msgpack for compact binary representation

Security invariants:
    - Trust Level 0 enforcement delegated to underlying Firestore store
    - Cache keys use session_id only — no PII in Redis key space
    - Cache values exclude overlay file content (too large for Redis)
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from apps.counselconduit.api.sandbox.firestore_session_store import (
  FirestoreSessionStore,
)
from apps.counselconduit.api.sandbox.session import (
  CommitAction,
  SandboxSession,
  SessionConfig,
  SessionState,
)
from apps.counselconduit.api.sandbox.telemetry import telemetry_latency

logger = logging.getLogger("counselconduit.sandbox.cache")

# Redis key prefix for namespace isolation
_CACHE_PREFIX = "cc:sandbox:session:"
_CACHE_TTL_SECONDS = 300  # 5 minutes — tuned for review cycle duration


class CachedSessionStore:
  """Redis-backed caching layer over FirestoreSessionStore.

  Implements the AbstractSessionStore protocol while adding a Redis L1
  cache for read-heavy operations (get_session, session_exists).

  Write operations always hit Firestore first, then invalidate the cache.
  This prevents stale reads at the cost of cache misses after writes.
  """

  def __init__(
    self,
    firestore_store: FirestoreSessionStore | None = None,
    redis_client: Any | None = None,
    cache_ttl: int = _CACHE_TTL_SECONDS,
  ):
    """Initialize with Firestore store and Redis client.

    Args:
        firestore_store: Underlying Firestore store (default: new instance).
        redis_client: Redis async client. If None, cache is disabled (passthrough).
        cache_ttl: Cache entry TTL in seconds.
    """
    self._store = firestore_store or FirestoreSessionStore()
    self._redis = redis_client
    self._cache_ttl = cache_ttl
    self._cache_hits = 0
    self._cache_misses = 0

  @property
  def cache_enabled(self) -> bool:
    """Whether Redis caching is active."""
    return self._redis is not None

  @property
  def cache_stats(self) -> dict[str, int]:
    """Return cache hit/miss statistics."""
    return {
      "hits": self._cache_hits,
      "misses": self._cache_misses,
      "total": self._cache_hits + self._cache_misses,
    }

  # ── Cached Reads ─────────────────────────────────────────────────────

  @telemetry_latency("cached_get_session")
  async def get_session(self, session_id: str) -> SandboxSession | None:
    """Load session with Redis read-through cache.

    Cache stores serialized session metadata (not overlay files).
    On cache hit: deserialize and return immediately.
    On cache miss: fetch from Firestore, cache result, return.
    """
    if self.cache_enabled:
      cached = await self._cache_get(session_id)
      if cached is not None:
        self._cache_hits += 1
        logger.debug("Cache HIT: %s…", session_id[:8])
        return cached

    self._cache_misses += 1
    session = await self._store.get_session(session_id)

    if session is not None and self.cache_enabled:
      await self._cache_set(session_id, session)
      logger.debug("Cache MISS → stored: %s…", session_id[:8])

    return session

  @telemetry_latency("cached_session_exists")
  async def session_exists(self, session_id: str) -> bool:
    """Check session existence with cache acceleration."""
    if self.cache_enabled:
      exists = await self._redis.exists(f"{_CACHE_PREFIX}{session_id}")
      if exists:
        self._cache_hits += 1
        return True

    self._cache_misses += 1
    return await self._store.session_exists(session_id)

  # ── Write-Through (Firestore first, then invalidate) ─────────────────

  @telemetry_latency("cached_create_session")
  async def create_session(self, session: SandboxSession) -> str:
    """Create session in Firestore, then warm cache."""
    result = await self._store.create_session(session)
    if self.cache_enabled:
      await self._cache_set(session.session_id, session)
    return result

  @telemetry_latency("cached_update_state")
  async def update_state(
    self,
    session_id: str,
    new_state: SessionState,
    *,
    extra_fields: dict[str, Any] | None = None,
  ) -> None:
    """Update state in Firestore, then invalidate cache."""
    await self._store.update_state(session_id, new_state, extra_fields=extra_fields)
    if self.cache_enabled:
      await self._cache_invalidate(session_id)

  @telemetry_latency("cached_update_overlay")
  async def update_overlay(
    self,
    session_id: str,
    overlay_files: dict[str, str],
    diff_summary: list[dict[str, Any]],
  ) -> None:
    """Update overlay in Firestore, then invalidate cache."""
    await self._store.update_overlay(session_id, overlay_files, diff_summary)
    if self.cache_enabled:
      await self._cache_invalidate(session_id)

  @telemetry_latency("cached_record_decision")
  async def record_decision(
    self,
    session_id: str,
    *,
    action: CommitAction,
    attorney_uid: str,
    firm_id: str,
    selected_files: list[str] | None = None,
    rejection_reason: str = "",
    result_summary: dict[str, Any] | None = None,
  ) -> str:
    """Record decision in Firestore, then invalidate cache."""
    result = await self._store.record_decision(
      session_id,
      action=action,
      attorney_uid=attorney_uid,
      firm_id=firm_id,
      selected_files=selected_files,
      rejection_reason=rejection_reason,
      result_summary=result_summary,
    )
    if self.cache_enabled:
      await self._cache_invalidate(session_id)
    return result

  # ── Passthrough (no caching benefit) ─────────────────────────────────

  async def get_decisions(self, session_id: str) -> list[dict[str, Any]]:
    """Passthrough to Firestore — decisions are append-only, not cached."""
    return await self._store.get_decisions(session_id)

  async def expire_session(self, session_id: str) -> None:
    """Expire in Firestore, then invalidate cache."""
    await self._store.expire_session(session_id)
    if self.cache_enabled:
      await self._cache_invalidate(session_id)

  async def list_active_sessions(
    self,
    attorney_uid: str | None = None,
    matter_id: str | None = None,
    *,
    limit: int = 50,
  ) -> list[dict[str, Any]]:
    """Passthrough to Firestore — list queries aren't cached."""
    return await self._store.list_active_sessions(
      attorney_uid=attorney_uid,
      matter_id=matter_id,
      limit=limit,
    )

  # ── Internal: Redis Cache Operations ─────────────────────────────────

  async def _cache_get(self, session_id: str) -> SandboxSession | None:
    """Deserialize a cached session from Redis."""
    try:
      raw = await self._redis.get(f"{_CACHE_PREFIX}{session_id}")
      if raw is None:
        return None
      return _deserialize_session(raw)
    except Exception:
      logger.debug("Cache read error for %s…, falling through", session_id[:8])
      return None

  async def _cache_set(self, session_id: str, session: SandboxSession) -> None:
    """Serialize and cache a session in Redis."""
    try:
      data = _serialize_session(session)
      await self._redis.setex(
        f"{_CACHE_PREFIX}{session_id}",
        self._cache_ttl,
        data,
      )
    except Exception:
      logger.debug("Cache write error for %s…, non-fatal", session_id[:8])

  async def _cache_invalidate(self, session_id: str) -> None:
    """Remove a session from the cache."""
    try:
      await self._redis.delete(f"{_CACHE_PREFIX}{session_id}")
    except Exception:
      logger.debug("Cache invalidate error for %s…, non-fatal", session_id[:8])


# ── Serialization ────────────────────────────────────────────────────────


def _serialize_session(session: SandboxSession) -> str:
  """Serialize session metadata to JSON (no overlay content)."""
  return json.dumps(
    {
      "session_id": session.session_id,
      "state": session.state.value,
      "matter_id": session.config.matter_id,
      "attorney_uid": session.config.attorney_uid,
      "ttl_seconds": session.config.ttl_seconds,
      "max_overlay_files": session.config.max_overlay_files,
      "trust_level": session.config.trust_level,
      "created_at": session.created_at,
      "rejection_reason": session.rejection_reason,
      "committed_files": session.committed_files,
      "_cached_at": time.time(),
    }
  )


def _deserialize_session(raw: str | bytes) -> SandboxSession:
  """Deserialize session from cached JSON."""
  data = json.loads(raw)
  config = SessionConfig(
    matter_id=data.get("matter_id", ""),
    attorney_uid=data.get("attorney_uid", ""),
    ttl_seconds=data.get("ttl_seconds", 1800),
    max_overlay_files=data.get("max_overlay_files", 50),
  )
  return SandboxSession(
    session_id=data["session_id"],
    config=config,
    state=SessionState(data.get("state", "created")),
    created_at=data.get("created_at", time.time()),
    rejection_reason=data.get("rejection_reason", ""),
    committed_files=data.get("committed_files", []),
  )
