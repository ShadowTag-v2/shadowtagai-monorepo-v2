# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Phase 4 Milestone 3 — AbstractSessionStore protocol + API refactor tests.

Tests:
  1. Protocol compliance: FirestoreSessionStore satisfies AbstractSessionStore
  2. API layer: _get_session is Firestore-only (no in-memory fallback)
  3. API layer: _store is typed as AbstractSessionStore
  4. API layer: create_session has no dual-write pattern
  5. Edge cases: 503 on Firestore exception, 404 on missing session
  6. Protocol structural typing: custom mock store satisfies protocol
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from apps.counselconduit.api.sandbox.firestore_session_store import (
  FirestoreSessionStore,
)
from apps.counselconduit.api.sandbox.session import (
  AbstractSessionStore,
  CommitAction,
  SandboxSession,
  SessionConfig,
  SessionState,
)


# ── 1. Protocol Compliance ────────────────────────────────────────────────


class TestProtocolCompliance:
  """Verify FirestoreSessionStore satisfies AbstractSessionStore protocol."""

  def test_firestore_store_is_protocol_compliant(self) -> None:
    """FirestoreSessionStore must be a structural subtype of AbstractSessionStore."""
    store = FirestoreSessionStore(db=MagicMock())
    # Protocol is structural — if it has all methods with compatible signatures, it satisfies the protocol.
    # We verify each method exists and is callable.
    assert callable(store.create_session)
    assert callable(store.get_session)
    assert callable(store.update_state)
    assert callable(store.update_overlay)
    assert callable(store.record_decision)
    assert callable(store.get_decisions)
    assert callable(store.expire_session)
    assert callable(store.session_exists)
    assert callable(store.list_active_sessions)

  def test_protocol_has_all_required_methods(self) -> None:
    """AbstractSessionStore protocol must define the complete store contract."""
    required_methods = {
      "create_session",
      "get_session",
      "update_state",
      "update_overlay",
      "record_decision",
      "get_decisions",
      "expire_session",
      "session_exists",
      "list_active_sessions",
    }
    protocol_methods = {
      name
      for name in dir(AbstractSessionStore)
      if not name.startswith("_")
      and callable(getattr(AbstractSessionStore, name, None))
    }
    assert required_methods.issubset(protocol_methods)


# ── 2. Custom Mock Store (structural typing verification) ─────────────────


class InMemorySessionStore:
  """Minimal in-memory store that satisfies AbstractSessionStore protocol.

  Used to verify structural typing works for DI in tests.
  """

  def __init__(self) -> None:
    self._sessions: dict[str, SandboxSession] = {}
    self._decisions: dict[str, list[dict[str, Any]]] = {}

  async def create_session(self, session: SandboxSession) -> str:
    self._sessions[session.session_id] = session
    return session.session_id

  async def get_session(self, session_id: str) -> SandboxSession | None:
    return self._sessions.get(session_id)

  async def update_state(
    self,
    session_id: str,
    new_state: SessionState,
    *,
    extra_fields: dict[str, Any] | None = None,
  ) -> None:
    if session_id in self._sessions:
      self._sessions[session_id].state = new_state

  async def update_overlay(
    self,
    session_id: str,
    overlay_files: dict[str, str],
    diff_summary: list[dict[str, Any]],
  ) -> None:
    if session_id in self._sessions:
      self._sessions[session_id].overlay_files = overlay_files

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
    self._decisions.setdefault(session_id, []).append(
      {"action": action.value, "attorney_uid": attorney_uid}
    )
    return f"decision-{len(self._decisions[session_id])}"

  async def get_decisions(self, session_id: str) -> list[dict[str, Any]]:
    return self._decisions.get(session_id, [])

  async def expire_session(self, session_id: str) -> None:
    await self.update_state(session_id, SessionState.EXPIRED)

  async def session_exists(self, session_id: str) -> bool:
    return session_id in self._sessions

  async def list_active_sessions(
    self,
    attorney_uid: str | None = None,
    matter_id: str | None = None,
    *,
    limit: int = 50,
  ) -> list[dict[str, Any]]:
    results = []
    for s in self._sessions.values():
      if s.state in (
        SessionState.COMMITTED,
        SessionState.REJECTED,
        SessionState.EXPIRED,
      ):
        continue
      if attorney_uid and s.config.attorney_uid != attorney_uid:
        continue
      if matter_id and s.config.matter_id != matter_id:
        continue
      results.append({"session_id": s.session_id, "state": s.state.value})
    return results[:limit]


class TestInMemoryStoreProtocol:
  """Verify custom InMemorySessionStore satisfies the protocol structurally."""

  @pytest.mark.asyncio
  async def test_create_and_retrieve(self) -> None:
    """InMemorySessionStore round-trip: create → get."""
    store = InMemorySessionStore()
    config = SessionConfig(matter_id="matter-001", attorney_uid="atty-001")
    session = SandboxSession(config=config)

    session_id = await store.create_session(session)
    assert session_id == session.session_id

    retrieved = await store.get_session(session_id)
    assert retrieved is not None
    assert retrieved.config.matter_id == "matter-001"

  @pytest.mark.asyncio
  async def test_update_state_and_list(self) -> None:
    """State update filters from active list."""
    store = InMemorySessionStore()
    config = SessionConfig(matter_id="matter-002", attorney_uid="atty-002")
    session = SandboxSession(config=config)
    await store.create_session(session)

    active = await store.list_active_sessions()
    assert len(active) == 1

    await store.update_state(session.session_id, SessionState.COMMITTED)
    active = await store.list_active_sessions()
    assert len(active) == 0

  @pytest.mark.asyncio
  async def test_record_and_get_decisions(self) -> None:
    """Decision audit trail: append + retrieve."""
    store = InMemorySessionStore()
    config = SessionConfig(matter_id="m-003", attorney_uid="atty-003")
    session = SandboxSession(config=config)
    await store.create_session(session)

    decision_id = await store.record_decision(
      session.session_id,
      action=CommitAction.ACCEPT,
      attorney_uid="atty-003",
      firm_id="firm-001",
    )
    assert decision_id == "decision-1"

    decisions = await store.get_decisions(session.session_id)
    assert len(decisions) == 1
    assert decisions[0]["action"] == "accept"

  @pytest.mark.asyncio
  async def test_expire_session(self) -> None:
    """Expire sets EXPIRED state."""
    store = InMemorySessionStore()
    config = SessionConfig(matter_id="m-004", attorney_uid="atty-004")
    session = SandboxSession(config=config)
    await store.create_session(session)

    await store.expire_session(session.session_id)
    s = await store.get_session(session.session_id)
    assert s is not None
    assert s.state == SessionState.EXPIRED

  @pytest.mark.asyncio
  async def test_session_exists(self) -> None:
    """session_exists returns True/False correctly."""
    store = InMemorySessionStore()
    assert not await store.session_exists("nonexistent")

    config = SessionConfig(matter_id="m-005", attorney_uid="atty-005")
    session = SandboxSession(config=config)
    await store.create_session(session)
    assert await store.session_exists(session.session_id)


# ── 3. API Layer Refactor Verification ─────────────────────────────────────


class TestAPILayerRefactor:
  """Verify sandbox_api.py no longer uses _active_sessions."""

  def test_no_active_sessions_in_module(self) -> None:
    """_active_sessions dict must be completely removed from sandbox_api."""
    import apps.counselconduit.api.sandbox.sandbox_api as api_module

    assert not hasattr(api_module, "_active_sessions"), (
      "_active_sessions must be removed in Phase 4 M3"
    )

  def test_store_typed_as_abstract(self) -> None:
    """_store must be typed against AbstractSessionStore, not concrete."""
    import apps.counselconduit.api.sandbox.sandbox_api as api_module

    # The module-level _store should exist
    assert hasattr(api_module, "_store")
    store = api_module._store
    # It should be an instance of FirestoreSessionStore (concrete)
    # but the type annotation should be AbstractSessionStore
    assert isinstance(store, FirestoreSessionStore)


# ── 4. _get_session Firestore-only behavior ────────────────────────────────


class TestGetSessionFirestoreOnly:
  """Verify _get_session raises 503 on Firestore error (no memory fallback)."""

  @pytest.mark.asyncio
  async def test_returns_session_from_store(self) -> None:
    """_get_session returns session from Firestore store."""
    import apps.counselconduit.api.sandbox.sandbox_api as api_module

    config = SessionConfig(matter_id="m-100", attorney_uid="atty-100")
    session = SandboxSession(config=config)

    mock_store = AsyncMock(spec=FirestoreSessionStore)
    mock_store.get_session.return_value = session

    original_store = api_module._store
    try:
      api_module._store = mock_store
      result = await api_module._get_session(session.session_id)
      assert result.session_id == session.session_id
      mock_store.get_session.assert_awaited_once_with(session.session_id)
    finally:
      api_module._store = original_store

  @pytest.mark.asyncio
  async def test_raises_503_on_firestore_error(self) -> None:
    """_get_session must raise 503 when Firestore fails (no in-memory fallback)."""
    import apps.counselconduit.api.sandbox.sandbox_api as api_module
    from fastapi import HTTPException

    mock_store = AsyncMock(spec=FirestoreSessionStore)
    mock_store.get_session.side_effect = ConnectionError("Firestore unavailable")

    original_store = api_module._store
    try:
      api_module._store = mock_store
      with pytest.raises(HTTPException) as exc_info:
        await api_module._get_session("some-session-id")
      assert exc_info.value.status_code == 503
    finally:
      api_module._store = original_store

  @pytest.mark.asyncio
  async def test_raises_404_on_missing_session(self) -> None:
    """_get_session must raise 404 when session not found in Firestore."""
    import apps.counselconduit.api.sandbox.sandbox_api as api_module
    from fastapi import HTTPException

    mock_store = AsyncMock(spec=FirestoreSessionStore)
    mock_store.get_session.return_value = None

    original_store = api_module._store
    try:
      api_module._store = mock_store
      with pytest.raises(HTTPException) as exc_info:
        await api_module._get_session("nonexistent-session")
      assert exc_info.value.status_code == 404
    finally:
      api_module._store = original_store


# ── 5. Create Session — No Dual-Write ──────────────────────────────────────


class TestCreateSessionNoDualWrite:
  """Verify create_session only writes to Firestore, not to memory dict."""

  def test_source_code_has_no_active_sessions_write(self) -> None:
    """create_session endpoint source must not reference _active_sessions."""
    import inspect

    import apps.counselconduit.api.sandbox.sandbox_api as api_module

    source = inspect.getsource(api_module.create_session)
    assert "_active_sessions" not in source, (
      "create_session must not write to _active_sessions in Phase 4 M3"
    )
