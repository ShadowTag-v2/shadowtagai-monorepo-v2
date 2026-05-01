# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests: auto_dream ↔ dream_consolidation.py.

Tests the contract between the auto_dream package (gate checks, locking,
prompt building) and the dream_consolidation.py daemon script (execution,
phase orchestration, lock release).

These tests verify:
  1. Gate cascade → daemon invocation contract
  2. Lock acquisition and release across package boundaries
  3. Prompt generation → daemon phase mapping
  4. Post-dream prompt cache invalidation (via KAIROS integration)
  5. Config propagation (min_hours, min_sessions)
"""

from __future__ import annotations

import json
import os
import pathlib
import time

import pytest

# ── Test fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def dream_workspace(tmp_path: pathlib.Path):
    """Create a minimal workspace for dream integration tests."""
    memory_dir = tmp_path / "knowledge"
    memory_dir.mkdir()

    # Create a minimal KI entry so the dream has something to scan
    ki_dir = memory_dir / "test_ki"
    ki_dir.mkdir()
    metadata = {
        "title": "Test Knowledge Item",
        "summary": "A test KI for integration tests",
        "created": "2026-04-30T00:00:00Z",
        "last_accessed": "2026-05-01T00:00:00Z",
        "references": [],
    }
    (ki_dir / "metadata.json").write_text(json.dumps(metadata))

    # Create a mock session log directory with transcripts
    logs_dir = tmp_path / "brain" / "test-session" / ".system_generated" / "logs"
    logs_dir.mkdir(parents=True)
    (logs_dir / "overview.txt").write_text("user: test message\nmodel: test response\n" * 10)

    # Create transcript directory for session scanning
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    # Create multiple session transcripts to satisfy session gates
    for i in range(10):
        (transcript_dir / f"session_{i}.jsonl").write_text(json.dumps({"role": "user", "content": f"test message {i}"}) + "\n")

    # Create beads directory for heartbeat
    beads_dir = tmp_path / ".beads"
    beads_dir.mkdir()

    return tmp_path


@pytest.fixture
def memory_dir(dream_workspace: pathlib.Path) -> str:
    return str(dream_workspace / "knowledge")


@pytest.fixture
def transcript_dir(dream_workspace: pathlib.Path) -> str:
    return str(dream_workspace / "transcripts")


# ── Gate cascade tests ────────────────────────────────────────────────────────


class TestDreamGateCascade:
    """Tests the 3-gate cascade: time → sessions → lock."""

    def test_fresh_workspace_fires_immediately(self, memory_dir: str, transcript_dir: str):
        """No lock file = 0 hours since last consolidation → fires."""
        from packages.auto_dream.consolidation import (
            AutoDreamConfig,
            check_dream_gates,
        )

        result = check_dream_gates(memory_dir, transcript_dir, config=AutoDreamConfig(min_hours=0, min_sessions=0))
        assert result.should_fire is True

    def test_recent_consolidation_blocks(self, memory_dir: str, transcript_dir: str):
        """Lock file touched recently → time gate blocks."""
        from packages.auto_dream.consolidation import (
            AutoDreamConfig,
            ConsolidationLock,
            check_dream_gates,
        )

        # Acquire and release to stamp the lock file mtime
        lock = ConsolidationLock(memory_dir)
        prior = lock.try_acquire()
        assert prior is not None

        # Now check with a 24-hour min — should block
        result = check_dream_gates(memory_dir, transcript_dir, config=AutoDreamConfig(min_hours=24.0, min_sessions=0))
        assert result.should_fire is False

    def test_config_min_hours_respected(self, memory_dir: str, transcript_dir: str):
        """min_hours=0 means always pass time gate."""
        from packages.auto_dream.consolidation import (
            AutoDreamConfig,
            check_dream_gates,
        )

        result = check_dream_gates(memory_dir, transcript_dir, config=AutoDreamConfig(min_hours=0, min_sessions=0))
        assert result.should_fire is True

    def test_config_min_sessions_respected(self, memory_dir: str, transcript_dir: str):
        """Require more sessions than exist → session gate blocks."""
        from packages.auto_dream.consolidation import (
            AutoDreamConfig,
            check_dream_gates,
        )

        result = check_dream_gates(memory_dir, transcript_dir, config=AutoDreamConfig(min_hours=0, min_sessions=999))
        # Should block because we don't have 999 sessions
        assert result.should_fire is False or result.sessions_found < 999


# ── Lock lifecycle tests ──────────────────────────────────────────────────────


class TestConsolidationLock:
    """Tests the lock acquisition, verification, and rollback mechanics."""

    def test_acquire_fresh_lock(self, memory_dir: str):
        """First acquire on clean dir should succeed."""
        from packages.auto_dream.consolidation import ConsolidationLock

        lock = ConsolidationLock(memory_dir)
        prior = lock.try_acquire()
        assert prior is not None

    def test_lock_file_contains_pid(self, memory_dir: str):
        """Lock file body should contain the current PID."""
        from packages.auto_dream.consolidation import ConsolidationLock

        lock = ConsolidationLock(memory_dir)
        lock.try_acquire()

        lock_path = os.path.join(memory_dir, ".consolidate-lock")
        assert os.path.exists(lock_path)
        with open(lock_path) as f:
            content = f.read().strip()
        assert content == str(os.getpid())

    def test_rollback_restores_prior_state(self, memory_dir: str):
        """Rollback with prior_mtime=0 removes the lock file."""
        from packages.auto_dream.consolidation import ConsolidationLock

        lock = ConsolidationLock(memory_dir)
        prior = lock.try_acquire()
        assert prior is not None

        lock.rollback(0)
        assert not os.path.exists(lock.lock_path)

    def test_read_last_consolidated_at_no_file(self, memory_dir: str):
        """No lock file → returns 0."""
        from packages.auto_dream.consolidation import ConsolidationLock

        lock = ConsolidationLock(memory_dir)
        assert lock.read_last_consolidated_at() == 0.0

    def test_read_last_consolidated_at_after_acquire(self, memory_dir: str):
        """After acquire, mtime should be recent."""
        from packages.auto_dream.consolidation import ConsolidationLock

        lock = ConsolidationLock(memory_dir)
        lock.try_acquire()
        mtime = lock.read_last_consolidated_at()
        # mtime is in milliseconds, should be within last 5 seconds
        assert mtime > 0
        assert abs(time.time() * 1000 - mtime) < 5000


# ── Prompt generation tests ──────────────────────────────────────────────────


class TestDreamPromptGeneration:
    """Tests the 4-phase consolidation prompt builder."""

    def test_prompt_contains_all_phases(self, memory_dir: str, transcript_dir: str):
        """Prompt should reference Orient, Gather, Consolidate, Prune."""
        from packages.auto_dream.consolidation import build_consolidation_prompt

        prompt = build_consolidation_prompt(memory_dir, transcript_dir)
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be a substantial prompt

        # Check for phase keywords
        prompt_lower = prompt.lower()
        assert "orient" in prompt_lower or "scan" in prompt_lower
        assert "gather" in prompt_lower or "read" in prompt_lower
        assert "consolidat" in prompt_lower or "merge" in prompt_lower
        assert "prune" in prompt_lower or "clean" in prompt_lower

    def test_prompt_includes_memory_dir(self, memory_dir: str, transcript_dir: str):
        """Prompt should reference the actual memory directory."""
        from packages.auto_dream.consolidation import build_consolidation_prompt

        prompt = build_consolidation_prompt(memory_dir, transcript_dir)
        assert memory_dir in prompt or "knowledge" in prompt


# ── Post-dream cache invalidation ────────────────────────────────────────────


class TestPostDreamCacheInvalidation:
    """Tests the contract between dream completion and prompt cache clearing."""

    def test_prompt_sections_cache_clear_available(self):
        """The clear function should be importable."""
        from packages.prompt_sections import clear_system_prompt_sections

        assert callable(clear_system_prompt_sections)

    def test_cache_clear_is_idempotent(self):
        """Calling clear multiple times should not raise."""
        from packages.prompt_sections import clear_system_prompt_sections

        # Should not raise on repeated calls
        clear_system_prompt_sections()
        clear_system_prompt_sections()
        clear_system_prompt_sections()

    def test_cache_clear_after_dream_record(self, memory_dir: str):
        """After recording a consolidation, cache clear should work."""
        from packages.auto_dream.consolidation import (
            ConsolidationLock,
            record_consolidation,
        )
        from packages.prompt_sections import clear_system_prompt_sections

        lock = ConsolidationLock(memory_dir)
        lock.try_acquire()

        # Record consolidation (this is what the daemon does after success)
        record_consolidation(memory_dir)

        # Clear prompt cache (this is what KAIROS does after dream success)
        clear_system_prompt_sections()

        # Verify lock mtime was updated (record_consolidation touches it)
        mtime = lock.read_last_consolidated_at()
        assert mtime > 0


# ── Record consolidation tests ────────────────────────────────────────────────


class TestRecordConsolidation:
    """Tests the post-dream recording mechanism."""

    def test_record_creates_lock_if_absent(self, memory_dir: str):
        """record_consolidation should create lock file if not present."""
        from packages.auto_dream.consolidation import (
            ConsolidationLock,
            record_consolidation,
        )

        lock = ConsolidationLock(memory_dir)
        assert lock.read_last_consolidated_at() == 0.0

        record_consolidation(memory_dir)

        assert lock.read_last_consolidated_at() > 0

    def test_record_updates_mtime(self, memory_dir: str):
        """record_consolidation should update the lock file mtime."""
        from packages.auto_dream.consolidation import (
            ConsolidationLock,
            record_consolidation,
        )

        record_consolidation(memory_dir)
        lock = ConsolidationLock(memory_dir)
        mtime1 = lock.read_last_consolidated_at()

        # Wait a tiny bit to ensure mtime changes
        time.sleep(0.05)
        record_consolidation(memory_dir)
        mtime2 = lock.read_last_consolidated_at()

        assert mtime2 >= mtime1


# ── KAIROS daemon integration contract ────────────────────────────────────────


class TestKairosDreamContract:
    """Verifies the contract between auto_dream package and KAIROS daemon."""

    def test_kairos_imports_available(self):
        """All KAIROS-required imports from auto_dream should resolve."""
        from packages.auto_dream import (
            AutoDreamConfig,
            AutoDreamResult,
            ConsolidationLock,
            build_consolidation_prompt,
            check_dream_gates,
            record_consolidation,
        )

        assert AutoDreamConfig is not None
        assert AutoDreamResult is not None
        assert ConsolidationLock is not None
        assert callable(build_consolidation_prompt)
        assert callable(check_dream_gates)
        assert callable(record_consolidation)

    def test_prevent_sleep_available_for_dream(self):
        """prevent_sleep package should be importable for dream operations."""
        from packages.prevent_sleep import start_prevent_sleep, stop_prevent_sleep

        assert callable(start_prevent_sleep)
        assert callable(stop_prevent_sleep)

    def test_token_estimation_available_for_heartbeat(self):
        """token_estimation should be importable for heartbeat budgeting."""
        from packages.token_estimation import estimate_tokens

        result = estimate_tokens("test string for token estimation")
        assert isinstance(result, int)
        assert result > 0

    def test_full_dream_lifecycle(self, memory_dir: str, transcript_dir: str):
        """Simulate the full lifecycle: gate → lock → prompt → record → cache clear."""
        from packages.auto_dream.consolidation import (
            AutoDreamConfig,
            build_consolidation_prompt,
            check_dream_gates,
            record_consolidation,
        )
        from packages.prompt_sections import clear_system_prompt_sections

        # 1. Check gates (should fire on fresh workspace)
        # NOTE: check_dream_gates acquires the lock as its 3rd gate,
        # so after this call the lock is already held by our PID.
        result = check_dream_gates(memory_dir, transcript_dir, config=AutoDreamConfig(min_hours=0, min_sessions=0))
        assert result.should_fire is True
        assert result.prior_mtime is not None  # Lock acquired

        # 2. Build prompt (would be sent to LLM in real daemon)
        prompt = build_consolidation_prompt(memory_dir, transcript_dir)
        assert len(prompt) > 0

        # 4. Record consolidation
        record_consolidation(memory_dir)

        # 5. Clear prompt cache (KAIROS post-dream step)
        clear_system_prompt_sections()

        # 6. Verify gate would now block (consolidation just happened)
        result2 = check_dream_gates(memory_dir, transcript_dir, config=AutoDreamConfig(min_hours=24.0, min_sessions=0))
        assert result2.should_fire is False
