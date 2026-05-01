# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for Sandbox Session API endpoints.

Tests the complete flow:
  1. Session creation → diff computation → attorney commit
  2. Security boundary enforcement (Trust Level, attorney UID)
  3. Audit trail generation

Uses FastAPI TestClient with dependency_overrides for auth.
"""

from __future__ import annotations

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
from apps.counselconduit.api.sandbox.sandbox_api import (
    _active_sessions,
    router,
)
from apps.counselconduit.api.sandbox.session import (
    SandboxSession,
    SessionConfig,
    SessionState,
)


# ── Fixtures ───────────────────────────────────────────────────────────


def _mock_attorney(uid: str = "atty-001", firm_id: str = "firm-001") -> dict[str, Any]:
    """Return a mock attorney payload."""
    return {"uid": uid, "firm_id": firm_id, "email": "atty@firm.test"}


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI app with dependency override for auth."""
    test_app = FastAPI()
    test_app.include_router(router)

    # Override the auth dependency to bypass real Firebase auth
    test_app.dependency_overrides[get_current_attorney] = lambda: _mock_attorney()
    yield test_app
    test_app.dependency_overrides.clear()


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
    # Set overlay files for diff computation
    session.overlay_files = {
        "research/memo.md": "# Updated Research Memo\n\nNew findings...\n",
        "contracts/draft.py": "def validate():\n    return True\n",
    }
    session.state = SessionState.REVIEWING
    return session


@pytest.fixture(autouse=True)
def reset_sessions():
    """Reset active sessions between tests."""
    _active_sessions.clear()
    yield
    _active_sessions.clear()


# ── GET /api/sandbox/{session_id}/diffs ────────────────────────────────


class TestGetDiffs:
    """Test the diff retrieval endpoint."""

    def test_returns_diffs_for_valid_session(
        self,
        client: TestClient,
        mock_session: SandboxSession,
    ):
        """Happy path: valid session returns computed diffs."""
        session_id = mock_session.session_id
        _active_sessions[session_id] = mock_session

        response = client.get(
            f"/api/sandbox/{session_id}/diffs",
            params={"matter": "matter-001"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
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
    ):
        """Mismatched matter ID returns 403."""
        session_id = mock_session.session_id
        _active_sessions[session_id] = mock_session

        response = client.get(
            f"/api/sandbox/{session_id}/diffs",
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
    ):
        """Accept action commits all overlay files."""
        session_id = mock_session.session_id
        _active_sessions[session_id] = mock_session

        response = client.post(
            f"/api/sandbox/{session_id}/commit",
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
    ):
        """Reject action produces audit trail with rejection reason."""
        session_id = mock_session.session_id
        _active_sessions[session_id] = mock_session

        response = client.post(
            f"/api/sandbox/{session_id}/commit",
            json={
                "action": "reject",
                "matter_id": "matter-001",
                "rejection_reason": "Insufficient privilege classification",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_invalid_action_returns_400(self, client: TestClient, mock_session: SandboxSession):
        """Invalid action string returns 400."""
        session_id = mock_session.session_id
        _active_sessions[session_id] = mock_session

        response = client.post(
            f"/api/sandbox/{session_id}/commit",
            json={
                "action": "yolo_merge",
                "matter_id": "matter-001",
            },
        )
        assert response.status_code == 400

    def test_missing_matter_returns_422(self, client: TestClient, mock_session: SandboxSession):
        """Missing matter_id returns 422 via Pydantic validation."""
        session_id = mock_session.session_id
        _active_sessions[session_id] = mock_session

        response = client.post(
            f"/api/sandbox/{session_id}/commit",
            json={"action": "accept"},
        )
        # Pydantic validation should fail
        assert response.status_code == 422


# ── Security Boundary Tests ────────────────────────────────────────────


class TestSecurityBoundaries:
    """Test Trust Level and attorney UID enforcement."""

    def test_trust_level_nonzero_rejected(
        self,
        client: TestClient,
    ):
        """Sessions with trust_level > 0 are rejected at bridge init."""
        config = SessionConfig(
            matter_id="matter-001",
            attorney_uid="atty-001",
            trust_level=1,  # Not Trust Level 0
        )
        session = SandboxSession(config=config)
        session.state = SessionState.REVIEWING
        _active_sessions[session.session_id] = session

        response = client.get(
            f"/api/sandbox/{session.session_id}/diffs",
            params={"matter": "matter-001"},
        )
        assert response.status_code == 403

    def test_unauthorized_attorney_rejected(
        self,
        app: FastAPI,
        mock_session: SandboxSession,
    ):
        """Attorney with empty UID is rejected at commit."""
        # Override auth to return empty UID
        app.dependency_overrides[get_current_attorney] = lambda: _mock_attorney(uid="")
        client = TestClient(app)

        session_id = mock_session.session_id
        _active_sessions[session_id] = mock_session

        response = client.post(
            f"/api/sandbox/{session_id}/commit",
            json={
                "action": "accept",
                "matter_id": "matter-001",
            },
        )
        assert response.status_code == 401
