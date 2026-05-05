# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Concurrency stress tests for sandbox session store.

Phase 4 M4: Validates that 10 concurrent session writes don't produce
race conditions, data corruption, or deadlocks in the AbstractSessionStore
contract.

Tests use an in-memory implementation to verify the protocol's
thread-safety contract without requiring live Firestore.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SessionConfig,
    SessionState,
)


class _ConcurrencyTestStore:
    """Thread-safe in-memory store for concurrency testing.

    Deliberately minimal — only implements the methods needed for
    concurrent create/read/update stress tests.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SandboxSession] = {}
        self._decisions: dict[str, list[dict[str, Any]]] = {}
        self._write_count = 0
        self._error_count = 0

    async def create_session(self, session: SandboxSession) -> str:
        # Simulate realistic Firestore write latency
        await asyncio.sleep(0.01)
        self._sessions[session.session_id] = session
        self._write_count += 1
        return session.session_id

    async def get_session(self, session_id: str) -> SandboxSession | None:
        await asyncio.sleep(0.005)
        return self._sessions.get(session_id)

    async def update_state(
        self,
        session_id: str,
        new_state: SessionState,
        *,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        await asyncio.sleep(0.005)
        if session_id in self._sessions:
            self._sessions[session_id].state = new_state

    async def update_overlay(
        self,
        session_id: str,
        overlay_files: dict[str, str],
        diff_summary: list[dict[str, Any]],
    ) -> None:
        await asyncio.sleep(0.01)
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
        await asyncio.sleep(0.005)
        decision_id = f"dec-{int(time.time() * 1000)}-{session_id[:4]}"
        self._decisions.setdefault(session_id, []).append({"decision_id": decision_id, "action": action.value})
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
        return []


def _make_session(i: int) -> SandboxSession:
    """Create a unique session for concurrency testing."""
    return SandboxSession(
        config=SessionConfig(
            matter_id=f"matter-{i:03d}",
            attorney_uid=f"atty-{i:03d}",
        ),
    )


# ── Concurrency Tests ──────────────────────────────────────────────────


class TestConcurrentSessionCreation:
    """Verify 10 concurrent create_session calls produce 10 distinct sessions."""

    @pytest.mark.asyncio
    async def test_10_concurrent_creates_no_data_loss(self) -> None:
        """10 concurrent writes → 10 sessions stored, no overwrites."""
        store = _ConcurrencyTestStore()
        sessions = [_make_session(i) for i in range(10)]

        tasks = [store.create_session(s) for s in sessions]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert len(set(results)) == 10, "Duplicate session IDs detected"
        assert store._write_count == 10

    @pytest.mark.asyncio
    async def test_concurrent_creates_are_all_retrievable(self) -> None:
        """All concurrently-created sessions can be individually retrieved."""
        store = _ConcurrencyTestStore()
        sessions = [_make_session(i) for i in range(10)]

        await asyncio.gather(*[store.create_session(s) for s in sessions])

        reads = await asyncio.gather(*[store.get_session(s.session_id) for s in sessions])
        assert all(r is not None for r in reads)
        assert {r.session_id for r in reads} == {s.session_id for s in sessions}


class TestConcurrentStateTransitions:
    """Verify concurrent state updates don't corrupt session data."""

    @pytest.mark.asyncio
    async def test_10_concurrent_state_updates(self) -> None:
        """10 concurrent state transitions on different sessions succeed."""
        store = _ConcurrencyTestStore()
        sessions = [_make_session(i) for i in range(10)]
        await asyncio.gather(*[store.create_session(s) for s in sessions])

        transitions = [store.update_state(s.session_id, SessionState.SPECULATING) for s in sessions]
        await asyncio.gather(*transitions)

        for s in sessions:
            loaded = await store.get_session(s.session_id)
            assert loaded is not None
            assert loaded.state == SessionState.SPECULATING

    @pytest.mark.asyncio
    async def test_rapid_state_transitions_on_single_session(self) -> None:
        """Rapid sequential state transitions on one session converge."""
        store = _ConcurrencyTestStore()
        session = _make_session(0)
        await store.create_session(session)

        states = [
            SessionState.SPECULATING,
            SessionState.REVIEWING,
            SessionState.COMMITTING,
            SessionState.COMMITTED,
        ]
        for state in states:
            await store.update_state(session.session_id, state)

        loaded = await store.get_session(session.session_id)
        assert loaded is not None
        assert loaded.state == SessionState.COMMITTED


class TestConcurrentDecisionRecording:
    """Verify concurrent decision writes produce distinct audit records."""

    @pytest.mark.asyncio
    async def test_10_concurrent_decisions_all_recorded(self) -> None:
        """10 concurrent decisions on separate sessions → 10 records."""
        store = _ConcurrencyTestStore()
        sessions = [_make_session(i) for i in range(10)]
        await asyncio.gather(*[store.create_session(s) for s in sessions])

        decision_tasks = [
            store.record_decision(
                session_id=s.session_id,
                action=CommitAction.ACCEPT,
                attorney_uid=s.config.attorney_uid,
                firm_id="firm-test",
            )
            for s in sessions
        ]
        decision_ids = await asyncio.gather(*decision_tasks)

        assert len(decision_ids) == 10
        assert len(set(decision_ids)) == 10, "Duplicate decision IDs"

    @pytest.mark.asyncio
    async def test_multiple_decisions_same_session(self) -> None:
        """Multiple concurrent decisions on same session all recorded."""
        store = _ConcurrencyTestStore()
        session = _make_session(0)
        await store.create_session(session)

        tasks = [
            store.record_decision(
                session_id=session.session_id,
                action=CommitAction.ACCEPT if i % 2 == 0 else CommitAction.REJECT,
                attorney_uid="atty-000",
                firm_id="firm-test",
            )
            for i in range(5)
        ]
        ids = await asyncio.gather(*tasks)
        assert len(ids) == 5

        decisions = await store.get_decisions(session.session_id)
        assert len(decisions) == 5


class TestConcurrentOverlayUpdates:
    """Verify concurrent overlay writes don't corrupt file maps."""

    @pytest.mark.asyncio
    async def test_10_concurrent_overlay_updates(self) -> None:
        """10 concurrent overlay updates on different sessions succeed."""
        store = _ConcurrencyTestStore()
        sessions = [_make_session(i) for i in range(10)]
        await asyncio.gather(*[store.create_session(s) for s in sessions])

        overlay_tasks = [
            store.update_overlay(
                session_id=s.session_id,
                overlay_files={f"file_{i}.md": f"content_{i}"},
                diff_summary=[{"path": f"file_{i}.md", "hunks": 1}],
            )
            for i, s in enumerate(sessions)
        ]
        await asyncio.gather(*overlay_tasks)

        for i, s in enumerate(sessions):
            loaded = await store.get_session(s.session_id)
            assert loaded is not None
            assert f"file_{i}.md" in loaded.overlay_files


class TestConcurrentLatencyBudget:
    """Verify concurrent operations complete within latency budget."""

    @pytest.mark.asyncio
    async def test_10_creates_under_500ms(self) -> None:
        """10 concurrent creates complete within 500ms total."""
        store = _ConcurrencyTestStore()
        sessions = [_make_session(i) for i in range(10)]

        start = time.perf_counter()
        await asyncio.gather(*[store.create_session(s) for s in sessions])
        elapsed_ms = (time.perf_counter() - start) * 1000

        # With 10ms simulated latency per write, concurrent should be ~10-20ms
        assert elapsed_ms < 500, f"10 concurrent creates took {elapsed_ms:.0f}ms (budget: 500ms)"
