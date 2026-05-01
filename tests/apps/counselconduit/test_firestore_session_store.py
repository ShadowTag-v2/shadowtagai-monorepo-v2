# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for FirestoreSessionStore — Phase 4 Milestone 2.

Tests the Firestore-backed persistent session store without requiring
a live Firestore emulator. All Firestore operations are mocked.

Coverage targets:
  - create_session: Trust Level 0 enforcement, overlay persistence
  - get_session: hydration, TTL expiry detection
  - update_state: state transitions, extra field persistence
  - update_overlay: overlay sub-collection writes + state transition
  - record_decision: append-only audit trail, immutability marker
  - get_decisions: ordered retrieval
  - list_active_sessions: query filters, terminal state exclusion
  - expire_session: soft delete behavior
  - session_exists: existence check without hydration
  - Edge cases: missing docs, expired sessions, empty overlays
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from apps.counselconduit.api.sandbox.firestore_session_store import (
    FirestoreSessionStore,
    _sha256_short,
)
from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SecurityError,
    SessionConfig,
    SessionState,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture()
def mock_db() -> MagicMock:
    """Create a mock Firestore client with standard collection/document chain.

    Firestore SDK pattern:
      - Synchronous: .collection(), .document(), .order_by(), .where(), .limit(), .batch(), batch.set()
      - Async (awaitable): .get(), .set(), .update(), .add(), batch.commit()
    """
    db = MagicMock()

    # Default doc snapshot — exists with standard data
    doc_snapshot = MagicMock()
    doc_snapshot.exists = True
    doc_snapshot.to_dict.return_value = {
        "session_id": "test-session-001",
        "state": "reviewing",
        "matter_id": "matter-001",
        "attorney_uid": "attorney-001",
        "ttl_seconds": 1800,
        "max_overlay_files": 50,
        "trust_level": 0,
        "created_at": time.time(),
        "rejection_reason": "",
        "committed_files": [],
        "expire_at": datetime.now(UTC) + timedelta(days=30),
    }

    # Sub-collection (overlay_files / decisions) — sync chain, async terminal ops
    sub_collection = MagicMock()
    sub_collection.order_by.return_value = sub_collection
    sub_collection.get = AsyncMock(return_value=[])
    sub_collection.add = AsyncMock(return_value=(None, MagicMock(id="decision-001")))

    # Sub-doc ref inside sub-collection (for overlay writes)
    sub_doc_ref = MagicMock()
    sub_doc_ref.get = AsyncMock(return_value=doc_snapshot)
    sub_doc_ref.set = AsyncMock()
    sub_doc_ref.update = AsyncMock()
    sub_collection.document.return_value = sub_doc_ref

    # Primary document ref — sync .collection(), async .get()/.set()/.update()
    doc_ref = MagicMock()
    doc_ref.get = AsyncMock(return_value=doc_snapshot)
    doc_ref.set = AsyncMock()
    doc_ref.update = AsyncMock()
    doc_ref.collection.return_value = sub_collection

    # Top-level collection — sync .document()/.where()/.limit(), async .get()
    collection = MagicMock()
    collection.document.return_value = doc_ref
    collection.where.return_value = collection
    collection.limit.return_value = collection
    collection.get = AsyncMock(return_value=[])

    db.collection.return_value = collection

    # Batch mock — sync .set(), async .commit()
    batch = MagicMock()
    batch.set = MagicMock()
    batch.commit = AsyncMock()
    db.batch.return_value = batch

    return db


@pytest.fixture()
def store(mock_db: MagicMock) -> FirestoreSessionStore:
    """FirestoreSessionStore with a mocked Firestore client."""
    return FirestoreSessionStore(db=mock_db)


@pytest.fixture()
def session_config() -> SessionConfig:
    """Standard Trust Level 0 session config."""
    return SessionConfig(
        matter_id="matter-001",
        attorney_uid="attorney-001",
        trust_level=0,
    )


@pytest.fixture()
def sample_session(session_config: SessionConfig) -> SandboxSession:
    """Sample session in CREATED state."""
    return SandboxSession(
        session_id="test-session-001",
        config=session_config,
        state=SessionState.CREATED,
    )


@pytest.fixture()
def reviewing_session(session_config: SessionConfig) -> SandboxSession:
    """Session in REVIEWING state with overlay files."""
    return SandboxSession(
        session_id="test-session-002",
        config=session_config,
        state=SessionState.REVIEWING,
        overlay_files={
            "brief.md": "# Updated Brief\n\nNew content.\n",
            "memo.py": "def analyze():\n    return 'privileged'\n",
        },
    )


# ── Unit: _sha256_short ──────────────────────────────────────────────────


class TestSha256Short:
    """Tests for the short hash utility."""

    def test_deterministic(self) -> None:
        assert _sha256_short("test") == _sha256_short("test")

    def test_length_24(self) -> None:
        assert len(_sha256_short("any-content")) == 24

    def test_different_inputs(self) -> None:
        assert _sha256_short("foo") != _sha256_short("bar")

    def test_empty_string(self) -> None:
        result = _sha256_short("")
        assert len(result) == 24
        assert result.isalnum()


# ── Create Session ────────────────────────────────────────────────────────


class TestCreateSession:
    """Tests for FirestoreSessionStore.create_session."""

    @pytest.mark.asyncio()
    async def test_creates_session_document(self, store: FirestoreSessionStore, sample_session: SandboxSession, mock_db: MagicMock) -> None:
        """create_session should write a session document to Firestore."""
        result = await store.create_session(sample_session)
        assert result == "test-session-001"
        # Verify set was called on the document reference
        doc_ref = mock_db.collection.return_value.document.return_value
        doc_ref.set.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_trust_level_nonzero_rejected(self, store: FirestoreSessionStore) -> None:
        """Sessions with trust_level != 0 must be rejected."""
        config = SessionConfig(
            matter_id="m-1",
            attorney_uid="a-1",
            trust_level=1,  # NOT zero
        )
        session = SandboxSession(config=config)
        with pytest.raises(SecurityError, match="trust_level != 0"):
            await store.create_session(session)

    @pytest.mark.asyncio()
    async def test_overlay_files_written_as_subcollection(
        self, store: FirestoreSessionStore, reviewing_session: SandboxSession, mock_db: MagicMock
    ) -> None:
        """Overlay files should be written as sub-collection documents via batch."""
        # Give it overlay files and set state to CREATED for creation
        reviewing_session.state = SessionState.CREATED
        await store.create_session(reviewing_session)
        # Batch commit should be called for overlay files
        mock_db.batch.return_value.commit.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_session_data_fields(self, store: FirestoreSessionStore, sample_session: SandboxSession, mock_db: MagicMock) -> None:
        """Persisted session document should contain all required fields."""
        await store.create_session(sample_session)
        doc_ref = mock_db.collection.return_value.document.return_value
        call_args = doc_ref.set.call_args[0][0]
        assert call_args["session_id"] == "test-session-001"
        assert call_args["matter_id"] == "matter-001"
        assert call_args["attorney_uid"] == "attorney-001"
        assert call_args["trust_level"] == 0
        assert call_args["state"] == "created"
        assert "expire_at" in call_args
        assert "_source" in call_args


# ── Get Session ───────────────────────────────────────────────────────────


class TestGetSession:
    """Tests for FirestoreSessionStore.get_session."""

    @pytest.mark.asyncio()
    async def test_hydrates_session_from_doc(self, store: FirestoreSessionStore) -> None:
        """get_session should hydrate a full SandboxSession from Firestore data."""
        session = await store.get_session("test-session-001")
        assert session is not None
        assert session.session_id == "test-session-001"
        assert session.config.matter_id == "matter-001"
        assert session.config.attorney_uid == "attorney-001"
        assert session.state == SessionState.REVIEWING

    @pytest.mark.asyncio()
    async def test_returns_none_for_missing_doc(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        """get_session should return None if the document doesn't exist."""
        doc_snapshot = MagicMock()
        doc_snapshot.exists = False
        mock_db.collection.return_value.document.return_value.get = AsyncMock(return_value=doc_snapshot)
        result = await store.get_session("nonexistent-session")
        assert result is None

    @pytest.mark.asyncio()
    async def test_expired_session_returns_none(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        """get_session should return None and mark session EXPIRED if TTL exceeded."""
        expired_time = datetime.now(UTC) - timedelta(days=1)
        doc_snapshot = MagicMock()
        doc_snapshot.exists = True
        doc_snapshot.to_dict.return_value = {
            "session_id": "expired-session",
            "state": "reviewing",
            "matter_id": "m-1",
            "attorney_uid": "a-1",
            "ttl_seconds": 1800,
            "max_overlay_files": 50,
            "trust_level": 0,
            "created_at": time.time(),
            "rejection_reason": "",
            "committed_files": [],
            "expire_at": expired_time,
        }
        mock_db.collection.return_value.document.return_value.get = AsyncMock(return_value=doc_snapshot)
        result = await store.get_session("expired-session")
        assert result is None
        # Verify state was updated to EXPIRED
        mock_db.collection.return_value.document.return_value.update.assert_awaited()


# ── Session Exists ────────────────────────────────────────────────────────


class TestSessionExists:
    """Tests for FirestoreSessionStore.session_exists."""

    @pytest.mark.asyncio()
    async def test_returns_true_for_existing(self, store: FirestoreSessionStore) -> None:
        result = await store.session_exists("test-session-001")
        assert result is True

    @pytest.mark.asyncio()
    async def test_returns_false_for_missing(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        doc_snapshot = MagicMock()
        doc_snapshot.exists = False
        mock_db.collection.return_value.document.return_value.get = AsyncMock(return_value=doc_snapshot)
        result = await store.session_exists("nope")
        assert result is False


# ── Update State ──────────────────────────────────────────────────────────


class TestUpdateState:
    """Tests for FirestoreSessionStore.update_state."""

    @pytest.mark.asyncio()
    async def test_updates_state_field(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        await store.update_state("test-session-001", SessionState.COMMITTED)
        doc_ref = mock_db.collection.return_value.document.return_value
        doc_ref.update.assert_awaited_once()
        call_data = doc_ref.update.call_args[0][0]
        assert call_data["state"] == "committed"

    @pytest.mark.asyncio()
    async def test_extra_fields_merged(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        await store.update_state(
            "test-session-001",
            SessionState.REJECTED,
            extra_fields={"rejection_reason": "Client declined"},
        )
        doc_ref = mock_db.collection.return_value.document.return_value
        call_data = doc_ref.update.call_args[0][0]
        assert call_data["state"] == "rejected"
        assert call_data["rejection_reason"] == "Client declined"


# ── Update Overlay ────────────────────────────────────────────────────────


class TestUpdateOverlay:
    """Tests for FirestoreSessionStore.update_overlay."""

    @pytest.mark.asyncio()
    async def test_transitions_to_reviewing(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        overlay = {"brief.md": "# New content\n"}
        diff_summary = [{"path": "brief.md", "hunks": 1}]
        await store.update_overlay("test-session-001", overlay, diff_summary)
        doc_ref = mock_db.collection.return_value.document.return_value
        doc_ref.update.assert_awaited_once()
        call_data = doc_ref.update.call_args[0][0]
        assert call_data["state"] == "reviewing"
        assert call_data["overlay_file_count"] == 1

    @pytest.mark.asyncio()
    async def test_overlay_written_via_batch(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        overlay = {"a.py": "print('a')\n", "b.py": "print('b')\n"}
        await store.update_overlay("s-1", overlay, [])
        mock_db.batch.return_value.commit.assert_awaited_once()


# ── Decision Audit Trail ─────────────────────────────────────────────────


class TestRecordDecision:
    """Tests for FirestoreSessionStore.record_decision (append-only audit)."""

    @pytest.mark.asyncio()
    async def test_records_accept_decision(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        decision_id = await store.record_decision(
            session_id="s-1",
            action=CommitAction.ACCEPT,
            attorney_uid="a-1",
            firm_id="firm-1",
        )
        assert decision_id == "decision-001"

    @pytest.mark.asyncio()
    async def test_records_reject_with_reason(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        await store.record_decision(
            session_id="s-1",
            action=CommitAction.REJECT,
            attorney_uid="a-1",
            firm_id="firm-1",
            rejection_reason="Not approved by client",
        )
        # Verify the add call included rejection_reason
        sub_col = mock_db.collection.return_value.document.return_value.collection.return_value
        call_data = sub_col.add.call_args[0][0]
        assert call_data["action"] == "reject"
        assert call_data["rejection_reason"] == "Not approved by client"

    @pytest.mark.asyncio()
    async def test_partial_accept_with_selected_files(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        await store.record_decision(
            session_id="s-1",
            action=CommitAction.PARTIAL_ACCEPT,
            attorney_uid="a-1",
            firm_id="firm-1",
            selected_files=["brief.md"],
        )
        sub_col = mock_db.collection.return_value.document.return_value.collection.return_value
        call_data = sub_col.add.call_args[0][0]
        assert call_data["action"] == "partial_accept"
        assert call_data["selected_files"] == ["brief.md"]

    @pytest.mark.asyncio()
    async def test_immutable_flag_set(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        """Every decision must carry the _immutable marker."""
        await store.record_decision(
            session_id="s-1",
            action=CommitAction.ACCEPT,
            attorney_uid="a-1",
            firm_id="firm-1",
        )
        sub_col = mock_db.collection.return_value.document.return_value.collection.return_value
        call_data = sub_col.add.call_args[0][0]
        assert call_data["_immutable"] is True


# ── Get Decisions ─────────────────────────────────────────────────────────


class TestGetDecisions:
    """Tests for FirestoreSessionStore.get_decisions."""

    @pytest.mark.asyncio()
    async def test_returns_empty_for_no_decisions(self, store: FirestoreSessionStore) -> None:
        decisions = await store.get_decisions("s-1")
        assert decisions == []

    @pytest.mark.asyncio()
    async def test_returns_ordered_decisions(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        """Decisions should come back ordered by timestamp."""
        doc1 = MagicMock()
        doc1.id = "d-1"
        doc1.to_dict.return_value = {"action": "accept", "timestamp": "2026-05-01T00:00:00"}

        doc2 = MagicMock()
        doc2.id = "d-2"
        doc2.to_dict.return_value = {"action": "reject", "timestamp": "2026-05-01T01:00:00"}

        sub_col = mock_db.collection.return_value.document.return_value.collection.return_value
        sub_col.order_by.return_value.get = AsyncMock(return_value=[doc1, doc2])

        decisions = await store.get_decisions("s-1")
        assert len(decisions) == 2
        assert decisions[0]["id"] == "d-1"
        assert decisions[1]["id"] == "d-2"


# ── Expire Session ────────────────────────────────────────────────────────


class TestExpireSession:
    """Tests for FirestoreSessionStore.expire_session."""

    @pytest.mark.asyncio()
    async def test_soft_deletes_via_state_update(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        """expire_session should update state to EXPIRED, not delete the document."""
        await store.expire_session("s-1")
        doc_ref = mock_db.collection.return_value.document.return_value
        doc_ref.update.assert_awaited_once()
        call_data = doc_ref.update.call_args[0][0]
        assert call_data["state"] == "expired"


# ── List Active Sessions ─────────────────────────────────────────────────


class TestListActiveSessions:
    """Tests for FirestoreSessionStore.list_active_sessions."""

    @pytest.mark.asyncio()
    async def test_empty_result(self, store: FirestoreSessionStore) -> None:
        sessions = await store.list_active_sessions()
        assert sessions == []

    @pytest.mark.asyncio()
    async def test_filters_by_attorney_uid(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        await store.list_active_sessions(attorney_uid="a-1")
        collection = mock_db.collection.return_value
        # Verify where() was called with attorney_uid filter
        collection.where.assert_called()

    @pytest.mark.asyncio()
    async def test_filters_by_matter_id(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        await store.list_active_sessions(matter_id="m-1")
        collection = mock_db.collection.return_value
        collection.where.assert_called()

    @pytest.mark.asyncio()
    async def test_respects_limit(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        await store.list_active_sessions(limit=10)
        collection = mock_db.collection.return_value
        # Since where() returns itself, limit is chained
        collection.where.return_value.where.return_value.limit.assert_called()


# ── Overlay Sub-Collection Round Trip ─────────────────────────────────────


class TestOverlayRoundTrip:
    """Tests for _write_overlay_files and _read_overlay_files."""

    @pytest.mark.asyncio()
    async def test_write_uses_batch(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        overlay = {"file1.py": "content1", "file2.py": "content2"}
        await store._write_overlay_files("s-1", overlay)
        batch = mock_db.batch.return_value
        # Two files = two batch.set calls
        assert batch.set.call_count == 2
        batch.commit.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_read_returns_file_map(self, store: FirestoreSessionStore, mock_db: MagicMock) -> None:
        doc1 = MagicMock()
        doc1.to_dict.return_value = {"file_path": "a.py", "content": "print('a')"}
        doc2 = MagicMock()
        doc2.to_dict.return_value = {"file_path": "b.py", "content": "print('b')"}

        sub_col = mock_db.collection.return_value.document.return_value.collection.return_value
        sub_col.get = AsyncMock(return_value=[doc1, doc2])

        result = await store._read_overlay_files("s-1")
        assert result == {"a.py": "print('a')", "b.py": "print('b')"}

    @pytest.mark.asyncio()
    async def test_empty_overlay_returns_empty_dict(self, store: FirestoreSessionStore) -> None:
        result = await store._read_overlay_files("s-empty")
        assert result == {}
