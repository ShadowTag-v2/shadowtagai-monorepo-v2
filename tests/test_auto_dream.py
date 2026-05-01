"""Tests for packages.auto_dream.

Validates:
- ConsolidationLock: acquire, rollback, record, stale-PID self-healing
- 3-gate cascade: time → sessions → lock
- Consolidation prompt generation (4-phase structure)
- Session scanning with mtime filtering
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from unittest import mock

import pytest

from packages.auto_dream import (
    AutoDreamConfig,
    ConsolidationLock,
    build_consolidation_prompt,
    check_dream_gates,
    record_consolidation,
)


@pytest.fixture()
def memory_dir(tmp_path: Path) -> str:
    """Create a temporary memory directory."""
    d = tmp_path / "memory"
    d.mkdir()
    return str(d)


@pytest.fixture()
def transcript_dir(tmp_path: Path) -> str:
    """Create a temporary transcript directory with sample sessions."""
    d = tmp_path / "transcripts"
    d.mkdir()
    return str(d)


def _create_sessions(transcript_dir: str, count: int, recent: bool = True) -> list[str]:
    """Create dummy transcript files, optionally with recent mtimes."""
    session_ids = []
    for i in range(count):
        sid = f"session-{i:03d}"
        filepath = os.path.join(transcript_dir, f"{sid}.jsonl")
        with open(filepath, "w") as f:
            f.write(f'{{"role": "user", "content": "test {i}"}}\n')
        if not recent:
            # Set old mtime (30 days ago)
            old_time = time.time() - 30 * 86400
            os.utime(filepath, (old_time, old_time))
        session_ids.append(sid)
    return session_ids


class TestConsolidationLock:
    """File-based lock with mtime-as-timestamp."""

    def test_read_last_consolidated_at_no_file(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        assert lock.read_last_consolidated_at() == 0.0

    def test_read_last_consolidated_at_with_file(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        lock.record()
        last_at = lock.read_last_consolidated_at()
        assert last_at > 0
        # Should be within the last few seconds (in ms)
        assert (time.time() * 1000 - last_at) < 5000

    def test_acquire_and_verify(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        prior = lock.try_acquire()
        assert prior is not None
        assert prior == 0.0  # No prior lock existed

        # Verify PID is written
        with open(lock.lock_path) as f:
            assert f.read().strip() == str(os.getpid())

    def test_acquire_blocked_by_live_process(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        # Write a lock held by a "live" PID
        os.makedirs(memory_dir, exist_ok=True)
        with open(lock.lock_path, "w") as f:
            f.write("12345")

        # Set mtime to recent
        now = time.time()
        os.utime(lock.lock_path, (now, now))

        # Mock the process as alive so lock is held
        with mock.patch(
            "packages.auto_dream.consolidation._is_process_running",
            return_value=True,
        ):
            result = lock.try_acquire()
            assert result is None  # Blocked

    def test_acquire_reclaims_dead_pid(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        os.makedirs(memory_dir, exist_ok=True)

        # Write a lock with a dead PID
        with open(lock.lock_path, "w") as f:
            f.write("999999999")

        now = time.time()
        os.utime(lock.lock_path, (now, now))

        # Mock _is_process_running to return False
        with mock.patch(
            "packages.auto_dream.consolidation._is_process_running",
            return_value=False,
        ):
            prior = lock.try_acquire()
            assert prior is not None  # Reclaimed

    def test_rollback_removes_file_when_prior_zero(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        lock.try_acquire()
        assert os.path.exists(lock.lock_path)

        lock.rollback(0.0)
        assert not os.path.exists(lock.lock_path)

    def test_rollback_restores_mtime(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        lock.try_acquire()

        # Set a known prior mtime (1 day ago in ms)
        prior_mtime = (time.time() - 86400) * 1000
        lock.rollback(prior_mtime)

        assert os.path.exists(lock.lock_path)
        actual_mtime = os.stat(lock.lock_path).st_mtime
        # Should be within 1 second of the target
        assert abs(actual_mtime - prior_mtime / 1000) < 1.0

    def test_record_stamps_current_time(self, memory_dir: str) -> None:
        lock = ConsolidationLock(memory_dir)
        before = time.time() * 1000
        lock.record()
        after = time.time() * 1000

        last_at = lock.read_last_consolidated_at()
        assert before <= last_at <= after


class TestCheckDreamGates:
    """3-gate cascade: time → sessions → lock."""

    def test_time_gate_blocks_when_recent(self, memory_dir: str, transcript_dir: str) -> None:
        # Record a recent consolidation
        record_consolidation(memory_dir)

        result = check_dream_gates(memory_dir, transcript_dir)
        assert result.should_fire is False
        assert "time_gate" in result.reason

    def test_session_gate_blocks_with_few_sessions(self, memory_dir: str, transcript_dir: str) -> None:
        # Set lock mtime to 2 days ago so time gate passes
        lock_path = os.path.join(memory_dir, ".consolidate-lock")
        with open(lock_path, "w") as f:
            f.write("")
        old_time = time.time() - 2 * 86400
        os.utime(lock_path, (old_time, old_time))

        # Only 2 sessions (need 5)
        _create_sessions(transcript_dir, 2)

        result = check_dream_gates(memory_dir, transcript_dir)
        assert result.should_fire is False
        assert "session_gate" in result.reason
        assert result.sessions_found == 2

    def test_all_gates_pass(self, memory_dir: str, transcript_dir: str) -> None:
        # Set lock mtime to 2 days ago
        lock_path = os.path.join(memory_dir, ".consolidate-lock")
        with open(lock_path, "w") as f:
            f.write("")
        old_time = time.time() - 2 * 86400
        os.utime(lock_path, (old_time, old_time))

        # Create 6 recent sessions
        _create_sessions(transcript_dir, 6)

        result = check_dream_gates(memory_dir, transcript_dir)
        assert result.should_fire is True
        assert "all_gates_passed" in result.reason
        assert result.sessions_found == 6

    def test_force_bypasses_time_and_session_gates(self, memory_dir: str, transcript_dir: str) -> None:
        record_consolidation(memory_dir)
        # No sessions at all
        result = check_dream_gates(memory_dir, transcript_dir, force=True)
        assert result.should_fire is True

    def test_current_session_excluded(self, memory_dir: str, transcript_dir: str) -> None:
        lock_path = os.path.join(memory_dir, ".consolidate-lock")
        with open(lock_path, "w") as f:
            f.write("")
        old_time = time.time() - 2 * 86400
        os.utime(lock_path, (old_time, old_time))

        sids = _create_sessions(transcript_dir, 5)
        # Exclude one session, dropping below threshold
        result = check_dream_gates(
            memory_dir,
            transcript_dir,
            current_session_id=sids[0],
        )
        assert result.should_fire is False
        assert result.sessions_found == 4

    def test_custom_config(self, memory_dir: str, transcript_dir: str) -> None:
        lock_path = os.path.join(memory_dir, ".consolidate-lock")
        with open(lock_path, "w") as f:
            f.write("")
        old_time = time.time() - 2 * 86400
        os.utime(lock_path, (old_time, old_time))

        _create_sessions(transcript_dir, 2)
        # Lower threshold to 2 sessions
        config = AutoDreamConfig(min_hours=1.0, min_sessions=2)
        result = check_dream_gates(memory_dir, transcript_dir, config=config)
        assert result.should_fire is True

    def test_old_sessions_not_counted(self, memory_dir: str, transcript_dir: str) -> None:
        """Sessions older than lastConsolidatedAt should not count."""
        record_consolidation(memory_dir)

        # Create sessions with old mtimes
        _create_sessions(transcript_dir, 10, recent=False)

        # Force bypasses time gate but sessions are still filtered
        lock_path = os.path.join(memory_dir, ".consolidate-lock")
        old_time = time.time() - 2 * 86400
        os.utime(lock_path, (old_time, old_time))

        result = check_dream_gates(memory_dir, transcript_dir)
        # Sessions are old, so they shouldn't count
        assert result.sessions_found == 0

    def test_agent_transcripts_excluded(self, memory_dir: str, transcript_dir: str) -> None:
        """agent-*.jsonl files should be excluded from session counting."""
        lock_path = os.path.join(memory_dir, ".consolidate-lock")
        with open(lock_path, "w") as f:
            f.write("")
        old_time = time.time() - 2 * 86400
        os.utime(lock_path, (old_time, old_time))

        # Create agent transcripts (should be excluded)
        for i in range(10):
            with open(os.path.join(transcript_dir, f"agent-task-{i}.jsonl"), "w") as f:
                f.write('{"test": true}\n')

        result = check_dream_gates(memory_dir, transcript_dir)
        assert result.sessions_found == 0


class TestBuildConsolidationPrompt:
    """4-phase prompt generation."""

    def test_contains_all_phases(self) -> None:
        prompt = build_consolidation_prompt("/mem", "/transcripts")
        assert "Phase 1 — Orient" in prompt
        assert "Phase 2 — Gather" in prompt
        assert "Phase 3 — Consolidate" in prompt
        assert "Phase 4 — Prune" in prompt

    def test_contains_paths(self) -> None:
        prompt = build_consolidation_prompt("/custom/mem", "/custom/transcripts")
        assert "/custom/mem" in prompt
        assert "/custom/transcripts" in prompt

    def test_extra_context_appended(self) -> None:
        prompt = build_consolidation_prompt("/mem", "/t", extra="Focus on security fixes")
        assert "Focus on security fixes" in prompt
        assert "Additional context" in prompt

    def test_no_extra_section_when_empty(self) -> None:
        prompt = build_consolidation_prompt("/mem", "/t")
        assert "Additional context" not in prompt

    def test_entrypoint_referenced(self) -> None:
        prompt = build_consolidation_prompt("/mem", "/t")
        assert "CLAUDE.md" in prompt

    def test_max_lines_documented(self) -> None:
        prompt = build_consolidation_prompt("/mem", "/t")
        assert "100 lines" in prompt
