# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for FirestoreSessionStore (Phase 4 Milestone 1).

Tests the Firestore-backed session persistence layer:
  1. CRUD lifecycle: create → read → update → list → expire
  2. TTL enforcement and expiry detection
  3. Overlay sub-collection read/write
  4. Immutable decision audit trail
  5. Security invariants (Trust Level 0 only)
  6. Query filters (attorney_uid, matter_id)

Uses mock Firestore client to avoid live database dependency.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SecurityError,
    SessionConfig,
    SessionState,
)
from apps.counselconduit.api.sandbox.firestore_session_store import (
    FirestoreSessionStore,
    SESSION_TTL_DAYS,
    _sha256_short,
)


# ── Mock Firestore Helpers ─────────────────────────────────────────────


class MockDocSnapshot:
    """Simulates a Firestore document snapshot."""

    def __init__(self, doc_id: str, data: dict[str, Any] | None = None, exists: bool = True):
        self.id = doc_id
        self._data = data or {}
        self.exists = exists

    def to_dict(self) -> dict[str, Any]:
        return self._data


class MockDocRef:
    """Simulates a Firestore document reference."""

    def __init__(self, doc_id: str, data: dict[str, Any] | None = None, exists: bool = True):
        self.id = doc_id
        self._data = data or {}
        self._exists = exists
        self.set = AsyncMock()
        self.update = AsyncMock()
        self.delete = AsyncMock()

    async def get(self) -> MockDocSnapshot:
        return MockDocSnapshot(self.id, self._data, self._exists)

    def collection(self, name: str) -> MockCollectionRef:
        return MockCollectionRef(name)


class MockCollectionRef:
    """Simulates a Firestore collection reference."""

    def __init__(self, name: str, docs: list[MockDocSnapshot] | None = None):
        self.name = name
        self._docs = docs or []
        self._filters: list[tuple[str, str, Any]] = []
        self._limit: int | None = None
        self._order_field: str | None = None
        self.add = AsyncMock(return_value=(datetime.now(UTC), MagicMock(id="decision-001")))

    def document(self, doc_id: str) -> MockDocRef:
        for doc in self._docs:
            if doc.id == doc_id:
                return MockDocRef(doc_id, doc._data, doc.exists)
        return MockDocRef(doc_id, exists=False)

    def where(self, field: str, op: str, value: Any) -> MockCollectionRef:
        self._filters.append((field, op, value))
        return self

    def limit(self, n: int) -> MockCollectionRef:
        self._limit = n
        return self

    def order_by(self, field: str) -> MockCollectionRef:
        self._order_field = field
        return self

    async def get(self) -> list[MockDocSnapshot]:
        return self._docs


def _make_mock_db(
    session_data: dict[str, Any] | None = None,
    session_exists: bool = True,
    overlay_docs: list[MockDocSnapshot] | None = None,
    decision_docs: list[MockDocSnapshot] | None = None,
) -> MagicMock:
    """Build a mock Firestore client with configurable sub-collections."""
    db = MagicMock()
    mock_batch = MagicMock()
    mock_batch.set = MagicMock()
    mock_batch.commit = AsyncMock()
    db.batch = MagicMock(return_value=mock_batch)

    # Session document
    session_doc_ref = MockDocRef("test-session", session_data, session_exists)

    # Wire up overlay sub-collection on the doc_ref
    overlay_col = MockCollectionRef("overlay_files", overlay_docs or [])
    decisions_col = MockCollectionRef("decisions", decision_docs or [])

    original_collection = session_doc_ref.collection

    def mock_doc_collection(name: str):
        if name == "overlay_files":
            return overlay_col
        if name == "decisions":
            return decisions_col
        return original_collection(name)

    session_doc_ref.collection = mock_doc_collection

    # Wire collection -> document chain
    session_col = MagicMock()
    session_col.document = MagicMock(return_value=session_doc_ref)
    session_col.where = MagicMock(return_value=session_col)
    session_col.limit = MagicMock(return_value=session_col)
    session_col.get = AsyncMock(return_value=[])

    db.collection = MagicMock(return_value=session_col)

    return db


# ── Fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
def store() -> FirestoreSessionStore:
    """Create a store with a mock db."""
    db = _make_mock_db()
    return FirestoreSessionStore(db=db)


@pytest.fixture
def sample_config() -> SessionConfig:
    """Standard test session config."""
    return SessionConfig(
        matter_id="matter-001",
        attorney_uid="atty-001",
        ttl_seconds=1800,
        max_overlay_files=50,
    )


@pytest.fixture
def sample_session(sample_config: SessionConfig) -> SandboxSession:
    """Standard test session."""
    return SandboxSession(
        session_id="test-session-001",
        config=sample_config,
        state=SessionState.CREATED,
        overlay_files={"memo.md": "# Test Memo\n"},
    )


# ── Create Tests ───────────────────────────────────────────────────────


class TestCreateSession:
    """Test session creation in Firestore."""

    @pytest.mark.asyncio
    async def test_create_persists_session(
        self,
        store: FirestoreSessionStore,
        sample_session: SandboxSession,
    ):
        """Session is written to Firestore with correct fields."""
        session_id = await store.create_session(sample_session)
        assert session_id == sample_session.session_id

        # Verify .set() was called on the document
        doc_ref = store.db.collection("sandbox_sessions").document(sample_session.session_id)
        doc_ref.set.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_sets_ttl_expiry(
        self,
        store: FirestoreSessionStore,
        sample_session: SandboxSession,
    ):
        """Session document includes expire_at field."""
        await store.create_session(sample_session)

        doc_ref = store.db.collection("sandbox_sessions").document(sample_session.session_id)
        call_args = doc_ref.set.call_args
        assert call_args is not None
        data = call_args[0][0]
        assert "expire_at" in data

    @pytest.mark.asyncio
    async def test_create_rejects_nonzero_trust(
        self,
        store: FirestoreSessionStore,
    ):
        """Sessions with trust_level != 0 are rejected."""
        config = SessionConfig(
            matter_id="matter-001",
            attorney_uid="atty-001",
            trust_level=1,
        )
        session = SandboxSession(config=config)

        with pytest.raises(SecurityError, match="trust_level != 0"):
            await store.create_session(session)

    @pytest.mark.asyncio
    async def test_create_writes_overlay_subcollection(
        self,
        store: FirestoreSessionStore,
        sample_session: SandboxSession,
    ):
        """Overlay files are written to sub-collection via batch."""
        await store.create_session(sample_session)

        # Batch should have been committed for overlay files
        batch = store.db.batch()
        batch.commit.assert_awaited()


# ── Read Tests ─────────────────────────────────────────────────────────


class TestGetSession:
    """Test session retrieval from Firestore."""

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing(self):
        """Non-existent session returns None."""
        db = _make_mock_db(session_exists=False)
        store = FirestoreSessionStore(db=db)
        result = await store.get_session("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_hydrates_session(self):
        """Existing session is properly hydrated from Firestore data."""
        session_data = {
            "session_id": "test-session",
            "state": "reviewing",
            "matter_id": "matter-001",
            "attorney_uid": "atty-001",
            "ttl_seconds": 1800,
            "max_overlay_files": 50,
            "created_at": time.time(),
            "rejection_reason": "",
            "committed_files": [],
            "expire_at": datetime.now(UTC) + timedelta(days=30),
        }
        db = _make_mock_db(session_data=session_data)
        store = FirestoreSessionStore(db=db)

        result = await store.get_session("test-session")
        assert result is not None
        assert result.session_id == "test-session"
        assert result.state == SessionState.REVIEWING

    @pytest.mark.asyncio
    async def test_get_detects_expired_session(self):
        """Expired sessions are detected and return None."""
        expire_time = datetime.now(UTC) - timedelta(days=1)

        session_data = {
            "session_id": "expired-session",
            "state": "reviewing",
            "matter_id": "matter-001",
            "attorney_uid": "atty-001",
            "ttl_seconds": 1800,
            "max_overlay_files": 50,
            "created_at": time.time() - 86400,
            "rejection_reason": "",
            "committed_files": [],
            "expire_at": expire_time,
        }
        db = _make_mock_db(session_data=session_data)
        store = FirestoreSessionStore(db=db)

        result = await store.get_session("expired-session")
        assert result is None


class TestSessionExists:
    """Test the lightweight existence check."""

    @pytest.mark.asyncio
    async def test_exists_returns_true(self):
        """Existing session returns True."""
        db = _make_mock_db(session_data={"session_id": "exists"})
        store = FirestoreSessionStore(db=db)
        assert await store.session_exists("exists") is True

    @pytest.mark.asyncio
    async def test_exists_returns_false(self):
        """Missing session returns False."""
        db = _make_mock_db(session_exists=False)
        store = FirestoreSessionStore(db=db)
        assert await store.session_exists("missing") is False


# ── Update Tests ───────────────────────────────────────────────────────


class TestUpdateState:
    """Test session state updates."""

    @pytest.mark.asyncio
    async def test_update_state_calls_firestore(self):
        """State update writes new state to Firestore."""
        db = _make_mock_db(session_data={"state": "created"})
        store = FirestoreSessionStore(db=db)

        await store.update_state("test-session", SessionState.SPECULATING)

        doc_ref = store.db.collection("sandbox_sessions").document("test-session")
        doc_ref.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_state_with_extra_fields(self):
        """Extra fields are merged into the update."""
        db = _make_mock_db(session_data={"state": "created"})
        store = FirestoreSessionStore(db=db)

        await store.update_state(
            "test-session",
            SessionState.ERROR,
            extra_fields={"error_message": "Something failed"},
        )

        doc_ref = store.db.collection("sandbox_sessions").document("test-session")
        call_args = doc_ref.update.call_args
        assert call_args is not None
        data = call_args[0][0]
        assert data["state"] == "error"
        assert data["error_message"] == "Something failed"


# ── Decision Audit Trail Tests ─────────────────────────────────────────


class TestDecisionAuditTrail:
    """Test the immutable decision recording system."""

    @pytest.mark.asyncio
    async def test_record_decision_returns_id(self):
        """Decision recording returns a document ID."""
        db = _make_mock_db(session_data={"session_id": "test-session"})
        store = FirestoreSessionStore(db=db)

        decision_id = await store.record_decision(
            "test-session",
            action=CommitAction.ACCEPT,
            attorney_uid="atty-001",
            firm_id="firm-001",
        )

        assert decision_id == "decision-001"

    @pytest.mark.asyncio
    async def test_record_decision_includes_metadata(self):
        """Decision data includes all required fields."""
        db = _make_mock_db(session_data={"session_id": "test-session"})

        # Track what gets written
        decisions_col = MockCollectionRef("decisions")
        decisions_col.add = AsyncMock(return_value=(datetime.now(UTC), MagicMock(id="dec-002")))

        # Wire the mock
        doc_ref = db.collection("sandbox_sessions").document("test-session")
        original_collection = doc_ref.collection

        def mock_collection(name: str):
            if name == "decisions":
                return decisions_col
            return original_collection(name)

        doc_ref.collection = mock_collection

        store = FirestoreSessionStore(db=db)

        await store.record_decision(
            "test-session",
            action=CommitAction.REJECT,
            attorney_uid="atty-001",
            firm_id="firm-001",
            rejection_reason="Privilege violation",
        )

        # Verify data written
        decisions_col.add.assert_awaited_once()
        written_data = decisions_col.add.call_args[0][0]
        assert written_data["action"] == "reject"
        assert written_data["attorney_uid"] == "atty-001"
        assert written_data["rejection_reason"] == "Privilege violation"
        assert written_data["_immutable"] is True

    @pytest.mark.asyncio
    async def test_get_decisions_returns_ordered_list(self):
        """Decisions are returned ordered by timestamp."""
        decision_docs = [
            MockDocSnapshot(
                "dec-1",
                {
                    "action": "reject",
                    "attorney_uid": "atty-001",
                    "timestamp": "2026-05-01T00:00:00Z",
                },
            ),
            MockDocSnapshot(
                "dec-2",
                {
                    "action": "accept",
                    "attorney_uid": "atty-001",
                    "timestamp": "2026-05-01T01:00:00Z",
                },
            ),
        ]

        db = _make_mock_db(
            session_data={"session_id": "test-session"},
            decision_docs=decision_docs,
        )
        store = FirestoreSessionStore(db=db)

        decisions = await store.get_decisions("test-session")
        assert len(decisions) == 2
        assert decisions[0]["action"] == "reject"
        assert decisions[1]["action"] == "accept"


# ── Expiry Tests ───────────────────────────────────────────────────────


class TestExpiry:
    """Test session expiry mechanics."""

    @pytest.mark.asyncio
    async def test_expire_session_updates_state(self):
        """Expiring a session sets state to EXPIRED."""
        db = _make_mock_db(session_data={"state": "reviewing"})
        store = FirestoreSessionStore(db=db)

        await store.expire_session("test-session")

        doc_ref = store.db.collection("sandbox_sessions").document("test-session")
        doc_ref.update.assert_awaited_once()
        call_args = doc_ref.update.call_args[0][0]
        assert call_args["state"] == "expired"


# ── Utility Tests ──────────────────────────────────────────────────────


class TestUtilities:
    """Test utility functions."""

    def test_sha256_short_deterministic(self):
        """SHA-256 short hash is deterministic and 24 chars."""
        h1 = _sha256_short("test/file.md")
        h2 = _sha256_short("test/file.md")
        assert h1 == h2
        assert len(h1) == 24

    def test_sha256_short_different_inputs(self):
        """Different inputs produce different hashes."""
        h1 = _sha256_short("file_a.md")
        h2 = _sha256_short("file_b.md")
        assert h1 != h2

    def test_ttl_days_constant(self):
        """TTL is set to 30 days for GDPR compliance."""
        assert SESSION_TTL_DAYS == 30
