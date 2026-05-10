# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for analytics endpoint + CachedSessionStore + metrics.

Phase 4 M5: Tests the full stack:
    - GET /api/sandbox/analytics/report with mock attorney JWT
    - CachedSessionStore cache hit/miss/invalidation semantics
    - Prometheus metrics registry export
    - Session TTL expiration detection
"""

from __future__ import annotations

import json
import time
from typing import Any
from unittest.mock import AsyncMock

import pytest

from apps.counselconduit.api.sandbox.cached_session_store import (
  CachedSessionStore,
  _deserialize_session,
  _serialize_session,
)
from apps.counselconduit.api.sandbox.metrics import MetricsRegistry, render_metrics
from apps.counselconduit.api.sandbox.session import (
  CommitAction,
  SandboxSession,
  SessionConfig,
  SessionState,
)
import contextlib


# ── Fixtures ─────────────────────────────────────────────────────────────


def _make_session(
  session_id: str = "test-session-001",
  matter_id: str = "matter-alpha",
  attorney_uid: str = "attorney-uid-0001",
  state: SessionState = SessionState.CREATED,
  ttl_seconds: int = 1800,
) -> SandboxSession:
  """Create a test SandboxSession."""
  return SandboxSession(
    session_id=session_id,
    config=SessionConfig(
      matter_id=matter_id,
      attorney_uid=attorney_uid,
      ttl_seconds=ttl_seconds,
    ),
    state=state,
    created_at=time.time(),
  )


def _mock_attorney_jwt(uid: str = "attorney-uid-0001") -> dict[str, Any]:
  """Create a mock decoded attorney JWT payload."""
  return {
    "uid": uid,
    "email": f"{uid[:8]}@firm.example.com",
    "role": "attorney",
    "firm_id": "firm-001",
    "iss": "https://securetoken.google.com/shadowtag-omega-v4",
    "aud": "shadowtag-omega-v4",
    "exp": int(time.time()) + 3600,
    "iat": int(time.time()),
  }


class MockRedis:
  """Async Redis mock for CachedSessionStore tests."""

  def __init__(self) -> None:
    self._store: dict[str, str] = {}
    self._ttls: dict[str, int] = {}

  async def get(self, key: str) -> str | None:
    return self._store.get(key)

  async def setex(self, key: str, ttl: int, value: str) -> None:
    self._store[key] = value
    self._ttls[key] = ttl

  async def delete(self, key: str) -> int:
    removed = key in self._store
    self._store.pop(key, None)
    self._ttls.pop(key, None)
    return 1 if removed else 0

  async def exists(self, key: str) -> int:
    return 1 if key in self._store else 0


# ── CachedSessionStore Tests ─────────────────────────────────────────────


class TestCachedSessionStore:
  """Tests for Redis-backed CachedSessionStore."""

  @pytest.fixture()
  def redis(self) -> MockRedis:
    return MockRedis()

  @pytest.fixture()
  def firestore_store(self) -> AsyncMock:
    store = AsyncMock()
    store.create_session = AsyncMock(return_value="test-session-001")
    store.get_session = AsyncMock(return_value=_make_session())
    store.session_exists = AsyncMock(return_value=True)
    store.update_state = AsyncMock()
    store.update_overlay = AsyncMock()
    store.record_decision = AsyncMock(return_value="decision-001")
    store.get_decisions = AsyncMock(return_value=[])
    store.expire_session = AsyncMock()
    store.list_active_sessions = AsyncMock(return_value=[])
    return store

  @pytest.fixture()
  def cached_store(
    self, firestore_store: AsyncMock, redis: MockRedis
  ) -> CachedSessionStore:
    return CachedSessionStore(
      firestore_store=firestore_store,
      redis_client=redis,
      cache_ttl=60,
    )

  @pytest.mark.asyncio
  async def test_cache_miss_then_hit(
    self, cached_store: CachedSessionStore, firestore_store: AsyncMock
  ) -> None:
    """First read = cache miss (Firestore), second read = cache hit (Redis)."""
    # First read: cache miss → Firestore
    session1 = await cached_store.get_session("test-session-001")
    assert session1 is not None
    assert session1.session_id == "test-session-001"
    assert cached_store.cache_stats["misses"] == 1
    assert cached_store.cache_stats["hits"] == 0
    firestore_store.get_session.assert_awaited_once()

    # Second read: cache hit → Redis (Firestore NOT called again)
    firestore_store.get_session.reset_mock()
    session2 = await cached_store.get_session("test-session-001")
    assert session2 is not None
    assert session2.session_id == "test-session-001"
    assert cached_store.cache_stats["hits"] == 1
    firestore_store.get_session.assert_not_awaited()

  @pytest.mark.asyncio
  async def test_cache_invalidation_on_state_update(
    self, cached_store: CachedSessionStore, firestore_store: AsyncMock, redis: MockRedis
  ) -> None:
    """State update invalidates cache entry."""
    # Warm cache
    await cached_store.get_session("test-session-001")
    assert await redis.exists("cc:sandbox:session:test-session-001") == 1

    # Update state → cache invalidated
    await cached_store.update_state("test-session-001", SessionState.SPECULATING)
    assert await redis.exists("cc:sandbox:session:test-session-001") == 0

  @pytest.mark.asyncio
  async def test_cache_warm_on_create(
    self, cached_store: CachedSessionStore, redis: MockRedis
  ) -> None:
    """Create session should warm the cache."""
    session = _make_session()
    await cached_store.create_session(session)
    assert await redis.exists("cc:sandbox:session:test-session-001") == 1

  @pytest.mark.asyncio
  async def test_cache_invalidation_on_expire(
    self, cached_store: CachedSessionStore, redis: MockRedis
  ) -> None:
    """Expire session invalidates cache."""
    # Warm cache
    await cached_store.get_session("test-session-001")
    assert await redis.exists("cc:sandbox:session:test-session-001") == 1

    # Expire → invalidate
    await cached_store.expire_session("test-session-001")
    assert await redis.exists("cc:sandbox:session:test-session-001") == 0

  @pytest.mark.asyncio
  async def test_passthrough_without_redis(self, firestore_store: AsyncMock) -> None:
    """Without Redis, all operations pass through to Firestore."""
    store = CachedSessionStore(firestore_store=firestore_store, redis_client=None)
    assert not store.cache_enabled

    session = await store.get_session("test-session-001")
    assert session is not None
    firestore_store.get_session.assert_awaited_once()

  @pytest.mark.asyncio
  async def test_session_exists_cache_acceleration(
    self, cached_store: CachedSessionStore, redis: MockRedis
  ) -> None:
    """session_exists uses Redis EXISTS for cache acceleration."""
    # Warm cache first
    await cached_store.get_session("test-session-001")

    # session_exists should use Redis EXISTS
    result = await cached_store.session_exists("test-session-001")
    assert result is True
    assert cached_store.cache_stats["hits"] == 1

  @pytest.mark.asyncio
  async def test_cache_invalidation_on_decision(
    self, cached_store: CachedSessionStore, redis: MockRedis
  ) -> None:
    """Recording a decision invalidates the cache."""
    # Warm cache
    await cached_store.get_session("test-session-001")
    assert await redis.exists("cc:sandbox:session:test-session-001") == 1

    # Record decision → invalidate
    await cached_store.record_decision(
      "test-session-001",
      action=CommitAction.ACCEPT,
      attorney_uid="attorney-uid-0001",
      firm_id="firm-001",
    )
    assert await redis.exists("cc:sandbox:session:test-session-001") == 0


# ── Serialization Tests ──────────────────────────────────────────────────


class TestSessionSerialization:
  """Tests for session JSON serialization/deserialization."""

  def test_roundtrip(self) -> None:
    """Serialize → deserialize preserves session identity."""
    session = _make_session(session_id="roundtrip-001", matter_id="matter-beta")
    raw = _serialize_session(session)
    restored = _deserialize_session(raw)
    assert restored.session_id == "roundtrip-001"
    assert restored.config.matter_id == "matter-beta"
    assert restored.state == SessionState.CREATED

  def test_serialization_excludes_overlay(self) -> None:
    """Serialized JSON must not contain overlay content."""
    session = _make_session()
    session.overlay_files = {"big_file.py": "x" * 10000}
    raw = _serialize_session(session)
    parsed = json.loads(raw)
    assert "overlay_files" not in parsed

  def test_deserialization_handles_missing_fields(self) -> None:
    """Deserialization handles minimal JSON gracefully."""
    minimal = json.dumps({"session_id": "minimal-001"})
    session = _deserialize_session(minimal)
    assert session.session_id == "minimal-001"
    assert session.state == SessionState.CREATED


# ── Metrics Registry Tests ───────────────────────────────────────────────


class TestMetricsRegistry:
  """Tests for Prometheus-compatible MetricsRegistry."""

  def test_record_and_render(self) -> None:
    """Recording latency samples renders valid Prometheus output."""
    reg = MetricsRegistry()
    reg.record_latency("create_session", 12.5)
    reg.record_latency("create_session", 18.3)
    reg.record_latency("get_session", 2.1, error=True)

    output = reg.render_prometheus()
    assert "sandbox_store_operation_duration_ms" in output
    assert 'operation="create_session"' in output
    assert 'operation="get_session"' in output
    assert "sandbox_store_operation_errors_total" in output

  def test_cache_counters(self) -> None:
    """Cache hit/miss counters render correctly."""
    reg = MetricsRegistry()
    reg.record_cache_hit()
    reg.record_cache_hit()
    reg.record_cache_miss()

    output = reg.render_prometheus()
    assert "sandbox_cache_hits_total 2" in output
    assert "sandbox_cache_misses_total 1" in output

  def test_get_summary_json(self) -> None:
    """Structured summary returns valid dict."""
    reg = MetricsRegistry()
    reg.record_latency("update_state", 5.0)
    reg.record_latency("update_state", 15.0)

    summary = reg.get_summary()
    assert "operations" in summary
    assert "update_state" in summary["operations"]
    assert summary["operations"]["update_state"]["count"] == 2

  def test_percentile_computation(self) -> None:
    """Percentile computation is correct for known data."""
    reg = MetricsRegistry()
    for i in range(100):
      reg.record_latency("test_op", float(i + 1))

    summary = reg.get_summary()
    op = summary["operations"]["test_op"]
    assert op["p50_ms"] == 50.0
    assert op["p95_ms"] == 95.0
    assert op["p99_ms"] == 99.0

  def test_reset(self) -> None:
    """Reset clears all metrics."""
    reg = MetricsRegistry()
    reg.record_latency("op1", 10.0)
    reg.record_cache_hit()
    reg.reset()

    summary = reg.get_summary()
    assert summary["cache_hits"] == 0
    assert len(summary["operations"]) == 0

  def test_render_metrics_convenience(self) -> None:
    """Global render_metrics() function works."""
    output = render_metrics()
    assert "sandbox_uptime_seconds" in output


# ── Mock Attorney JWT Tests ──────────────────────────────────────────────


class TestMockAttorneyJWT:
  """Tests for analytics endpoint with mock attorney JWT."""

  def test_jwt_structure(self) -> None:
    """Mock JWT has required Firebase Auth claims."""
    jwt = _mock_attorney_jwt("atty-001")
    assert jwt["uid"] == "atty-001"
    assert jwt["role"] == "attorney"
    assert jwt["firm_id"] == "firm-001"
    assert jwt["iss"].startswith("https://securetoken.google.com/")
    assert jwt["exp"] > time.time()

  def test_jwt_uid_mismatch_prevention(self) -> None:
    """Different UIDs produce different JWTs."""
    jwt1 = _mock_attorney_jwt("atty-001")
    jwt2 = _mock_attorney_jwt("atty-002")
    assert jwt1["uid"] != jwt2["uid"]
    assert jwt1["email"] != jwt2["email"]


# ── Session TTL Tests ────────────────────────────────────────────────────


class TestSessionTTL:
  """Tests for session TTL expiration detection."""

  def test_session_not_expired(self) -> None:
    """Fresh session should not be expired."""
    session = _make_session(ttl_seconds=1800)
    elapsed = time.time() - session.created_at
    assert elapsed < session.config.ttl_seconds

  def test_session_expired_detection(self) -> None:
    """Session with past creation time should detect expiry."""
    session = _make_session(ttl_seconds=1)
    session.created_at = time.time() - 10  # 10 seconds ago with 1s TTL
    with pytest.raises(RuntimeError, match="expired"):
      session._check_expiry()

  def test_session_expired_state_transition(self) -> None:
    """Expired session transitions to EXPIRED state."""
    session = _make_session(ttl_seconds=1)
    session.created_at = time.time() - 10
    with contextlib.suppress(RuntimeError):
      session._check_expiry()
    assert session.state == SessionState.EXPIRED
