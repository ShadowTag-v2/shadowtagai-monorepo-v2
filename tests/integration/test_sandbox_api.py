# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for Sandbox Session API endpoints.

Phase 4 M3: Rewritten to use AbstractSessionStore protocol.
The old _active_sessions in-memory dict has been removed.
Tests now use an InMemorySessionStore for DI-based testing.

Tests the complete flow:
  1. Session creation → diff computation → attorney commit
  2. Security boundary enforcement (Trust Level, attorney UID)
  3. Audit trail generation

Uses FastAPI TestClient with dependency_overrides for auth.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Stub dependencies before import
import sys

mock_firestore_client = MagicMock()
mock_batch = MagicMock()
mock_batch.commit = AsyncMock()
mock_db = MagicMock()
mock_db.batch = MagicMock(return_value=mock_batch)
mock_firestore_client._get_client = MagicMock(return_value=mock_db)
mock_audit_entry_instance = MagicMock()
mock_audit_entry_instance.timestamp = "2026-05-01T00:00:00Z"
mock_firestore_client.AuditEntry = MagicMock(return_value=mock_audit_entry_instance)
mock_firestore_client.write_audit_log = AsyncMock()

sys.modules.setdefault("apps.counselconduit.api.firestore_client", mock_firestore_client)

from apps.counselconduit.api.auth import get_current_attorney
from apps.counselconduit.api.sandbox import sandbox_api
from apps.counselconduit.api.sandbox.sandbox_api import router
from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SessionConfig,
    SessionState,
)


# ── In-Memory Store for Integration Testing ────────────────────────────


class _IntegrationTestStore:
    """Minimal in-memory session store implementing AbstractSessionStore.

    Used only for integration tests — provides the same interface as
    FirestoreSessionStore without needing Firestore access.
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
        decision_id = f"dec-{int(time.time())}"
        self._decisions.setdefault(session_id, []).append(
            {
                "decision_id": decision_id,
                "action": action.value,
                "attorney_uid": attorney_uid,
            }
        )
        return decision_id

    async def get_decisions(self, session_id: str) -> list[dict[str, Any]]:
        return self._decisions.get(session_id, [])

    async def expire_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id].state = SessionState.EXPIRED

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
            if attorney_uid and s.config.attorney_uid != attorney_uid:
                continue
            if matter_id and s.config.matter_id != matter_id:
                continue
            results.append(
                {
                    "session_id": s.session_id,
                    "state": s.state.value,
                    "matter_id": s.config.matter_id,
                    "attorney_uid": s.config.attorney_uid,
                    "created_at": s.created_at,
                }
            )
        return results[:limit]


# ── Helper ─────────────────────────────────────────────────────────────


def _inject(store: _IntegrationTestStore, session: SandboxSession) -> None:
    """Synchronously inject a session into the test store."""
    asyncio.run(store.create_session(session))


# ── Fixtures ───────────────────────────────────────────────────────────


def _mock_attorney(uid: str = "atty-001", firm_id: str = "firm-001") -> dict[str, Any]:
    """Return a mock attorney payload."""
    return {"uid": uid, "firm_id": firm_id, "email": "atty@firm.test"}


@pytest.fixture
def test_store() -> _IntegrationTestStore:
    """Create a fresh in-memory store for each test."""
    return _IntegrationTestStore()


@pytest.fixture
def app(test_store: _IntegrationTestStore) -> FastAPI:
    """Create a test FastAPI app with DI overrides."""
    test_app = FastAPI()
    test_app.include_router(router)

    # Override the auth dependency to bypass real Firebase auth
    test_app.dependency_overrides[get_current_attorney] = lambda: _mock_attorney()

    # Inject the test store via monkeypatch on the module-level _store
    original_store = sandbox_api._store
    sandbox_api._store = test_store

    yield test_app

    test_app.dependency_overrides.clear()
    sandbox_api._store = original_store


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_session() -> SandboxSession:
    """Create a mock sandbox session in REVIEWING state."""
    config = SessionConfig(
        matter_id="matter-001",
        attorney_uid="atty-001",
    )
    session = SandboxSession(config=config)
    session.overlay_files = {
        "research/memo.md": "# Updated Research Memo\n\nNew findings...\n",
        "contracts/draft.py": "def validate():\n    return True\n",
    }
    session.state = SessionState.REVIEWING
    return session


# ── GET /api/sandbox/{session_id}/diffs ────────────────────────────────


class TestGetDiffs:
    """Test the diff retrieval endpoint."""

    def test_returns_diffs_for_valid_session(
        self,
        client: TestClient,
        mock_session: SandboxSession,
        test_store: _IntegrationTestStore,
    ):
        """Happy path: valid session returns computed diffs."""
        _inject(test_store, mock_session)

        response = client.get(
            f"/api/sandbox/{mock_session.session_id}/diffs",
            params={"matter": "matter-001"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == mock_session.session_id
        assert data["matter_id"] == "matter-001"
        assert data["file_count"] == 2
        assert len(data["diffs"]) == 2

    def test_returns_404_for_unknown_session(self, client: TestClient):
        """Unknown session ID returns 404."""
        response = client.get(
            "/api/sandbox/nonexistent-session/diffs",
            params={"matter": "matter-001"},
        )
        assert response.status_code == 404

    def test_returns_403_for_mismatched_matter(
        self,
        client: TestClient,
        mock_session: SandboxSession,
        test_store: _IntegrationTestStore,
    ):
        """Mismatched matter ID returns 403."""
        _inject(test_store, mock_session)

        response = client.get(
            f"/api/sandbox/{mock_session.session_id}/diffs",
            params={"matter": "wrong-matter"},
        )
        assert response.status_code == 403


# ── POST /api/sandbox/{session_id}/commit ──────────────────────────────


class TestCommitSession:
    """Test the commit decision endpoint."""

    def test_accept_commits_all_files(
        self,
        client: TestClient,
        mock_session: SandboxSession,
        test_store: _IntegrationTestStore,
    ):
        """Accept action commits all overlay files."""
        _inject(test_store, mock_session)

        response = client.post(
            f"/api/sandbox/{mock_session.session_id}/commit",
            json={
                "action": "accept",
                "matter_id": "matter-001",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_reject_produces_audit_trail(
        self,
        client: TestClient,
        mock_session: SandboxSession,
        test_store: _IntegrationTestStore,
    ):
        """Reject action produces audit trail with rejection reason."""
        _inject(test_store, mock_session)

        response = client.post(
            f"/api/sandbox/{mock_session.session_id}/commit",
            json={
                "action": "reject",
                "matter_id": "matter-001",
                "rejection_reason": "Insufficient privilege classification",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_invalid_action_returns_400(
        self,
        client: TestClient,
        mock_session: SandboxSession,
        test_store: _IntegrationTestStore,
    ):
        """Invalid action string returns 400."""
        _inject(test_store, mock_session)

        response = client.post(
            f"/api/sandbox/{mock_session.session_id}/commit",
            json={
                "action": "yolo_merge",
                "matter_id": "matter-001",
            },
        )
        assert response.status_code == 400

    def test_missing_matter_returns_422(
        self,
        client: TestClient,
        mock_session: SandboxSession,
        test_store: _IntegrationTestStore,
    ):
        """Missing matter_id returns 422 via Pydantic validation."""
        _inject(test_store, mock_session)

        response = client.post(
            f"/api/sandbox/{mock_session.session_id}/commit",
            json={"action": "accept"},
        )
        assert response.status_code == 422


# ── Security Boundary Tests ────────────────────────────────────────────


class TestSecurityBoundaries:
    """Test Trust Level and attorney UID enforcement."""

    def test_trust_level_nonzero_rejected(
        self,
        client: TestClient,
        test_store: _IntegrationTestStore,
    ):
        """Sessions with trust_level > 0 are rejected at bridge init."""
        config = SessionConfig(
            matter_id="matter-001",
            attorney_uid="atty-001",
            trust_level=1,
        )
        session = SandboxSession(config=config)
        session.state = SessionState.REVIEWING
        _inject(test_store, session)

        response = client.get(
            f"/api/sandbox/{session.session_id}/diffs",
            params={"matter": "matter-001"},
        )
        assert response.status_code == 403

    def test_unauthorized_attorney_rejected(
        self,
        app: FastAPI,
        mock_session: SandboxSession,
        test_store: _IntegrationTestStore,
    ):
        """Attorney with empty UID is rejected at commit."""
        app.dependency_overrides[get_current_attorney] = lambda: _mock_attorney(uid="")
        client = TestClient(app)
        _inject(test_store, mock_session)

        response = client.post(
            f"/api/sandbox/{mock_session.session_id}/commit",
            json={
                "action": "accept",
                "matter_id": "matter-001",
            },
        )
        assert response.status_code == 401


# ── Phase 4 M3 — Firestore-Only Architecture Tests ────────────────────


class TestFirestoreOnlyArchitecture:
    """Verify the in-memory dict is truly gone from the API layer."""

    def test_no_active_sessions_dict_in_module(self):
        """The _active_sessions dict must not exist in sandbox_api module."""
        assert not hasattr(sandbox_api, "_active_sessions"), (
            "Legacy _active_sessions dict still exists in sandbox_api — Phase 4 M3 requires its complete removal."
        )

    def test_store_variable_is_abstract_typed(self):
        """The _store module variable must satisfy AbstractSessionStore protocol."""
        from apps.counselconduit.api.sandbox.session import AbstractSessionStore

        store = getattr(sandbox_api, "_store", None)
        assert store is not None, "_store not found in sandbox_api module"
        assert isinstance(store, AbstractSessionStore)

    def test_session_not_found_returns_404_not_fallback(
        self,
        client: TestClient,
    ):
        """Missing session returns 404 (no in-memory fallback)."""
        response = client.get(
            "/api/sandbox/does-not-exist/diffs",
            params={"matter": "matter-001"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
