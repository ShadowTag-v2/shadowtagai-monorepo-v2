# Copyright 2026 ShadowTag-v2. All rights reserved.
# SPDX-License-Identifier: Proprietary
#
# Tests for session_ingress.py — Filesystem-Backed Persistence Layer

from __future__ import annotations

import asyncio
import importlib
import json
import sys
import time
from pathlib import Path

import pytest

# packages/aiyou-core has a hyphen — not a valid Python identifier.
# Import via importlib to handle this (matches test_typed_messaging.py).
_session_ingress_path = Path(__file__).parent.parent / "packages" / "aiyou-core"
sys.path.insert(0, str(_session_ingress_path))
_mod = importlib.import_module("session_ingress")
sys.path.pop(0)

TranscriptEntry = _mod.TranscriptEntry
append_session_log = _mod.append_session_log
clear_all_sessions = _mod.clear_all_sessions
clear_session = _mod.clear_session
create_entry = _mod.create_entry
get_session_logs = _mod.get_session_logs
get_session_stats = _mod.get_session_stats
write_compaction_marker = _mod.write_compaction_marker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_sessions(tmp_path: Path) -> Path:
    """Temporary directory for session logs."""
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    return sessions_dir


@pytest.fixture(autouse=True)
def _clean_session_state():
    """Clear all in-memory session state before each test."""
    clear_all_sessions()
    yield
    clear_all_sessions()


def _make_entry(
    role: str = "user",
    content: str = "test",
    entry_uuid: str | None = None,
) -> TranscriptEntry:
    """Create a TranscriptEntry with predictable defaults."""
    return TranscriptEntry(
        entry_uuid=entry_uuid or f"uuid-{time.monotonic_ns()}",
        timestamp=time.time(),
        role=role,
        content=content,
    )


# ---------------------------------------------------------------------------
# TranscriptEntry Tests
# ---------------------------------------------------------------------------


class TestTranscriptEntry:
    def test_roundtrip(self):
        entry = _make_entry(content="hello world")
        d = entry.to_dict()
        restored = TranscriptEntry.from_dict(d)
        assert restored.entry_uuid == entry.entry_uuid
        assert restored.content == "hello world"
        assert restored.role == "user"

    def test_metadata(self):
        entry = _make_entry(content="with meta")
        entry_with_meta = TranscriptEntry(
            entry_uuid=entry.entry_uuid,
            timestamp=entry.timestamp,
            role=entry.role,
            content=entry.content,
            metadata={"tool": "grep", "status": "success"},
        )
        d = entry_with_meta.to_dict()
        assert d["metadata"]["tool"] == "grep"
        restored = TranscriptEntry.from_dict(d)
        assert restored.metadata is not None
        assert restored.metadata["status"] == "success"

    def test_from_dict_defaults(self):
        """Minimal dict should produce valid entry with defaults."""
        minimal = {"uuid": "test-uuid"}
        entry = TranscriptEntry.from_dict(minimal)
        assert entry.entry_uuid == "test-uuid"
        assert entry.role == "system"
        assert entry.content == ""
        assert entry.timestamp == 0.0


# ---------------------------------------------------------------------------
# Append Tests
# ---------------------------------------------------------------------------


class TestAppendSessionLog:
    @pytest.mark.asyncio
    async def test_single_append(self, tmp_sessions: Path):
        entry = _make_entry(content="first entry")
        result = await append_session_log(tmp_sessions, "sess-1", entry)
        assert result is True

        # Verify on disk
        log_path = tmp_sessions / "sess-1" / "transcript.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["content"] == "first entry"

    @pytest.mark.asyncio
    async def test_sequential_appends(self, tmp_sessions: Path):
        entries = [_make_entry(content=f"entry-{i}") for i in range(5)]
        for entry in entries:
            result = await append_session_log(tmp_sessions, "sess-2", entry)
            assert result is True

        # Verify chain
        log_path = tmp_sessions / "sess-2" / "transcript.jsonl"
        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 5

        # Head UUID should be the last entry's UUID
        head_path = tmp_sessions / "sess-2" / ".head_uuid"
        assert head_path.read_text().strip() == entries[-1].entry_uuid

    @pytest.mark.asyncio
    async def test_uuid_chain_integrity(self, tmp_sessions: Path):
        """Verify that the UUID chain head advances correctly."""
        e1 = _make_entry(content="first", entry_uuid="uuid-001")
        e2 = _make_entry(content="second", entry_uuid="uuid-002")

        await append_session_log(tmp_sessions, "sess-chain", e1)
        head = (tmp_sessions / "sess-chain" / ".head_uuid").read_text().strip()
        assert head == "uuid-001"

        await append_session_log(tmp_sessions, "sess-chain", e2)
        head = (tmp_sessions / "sess-chain" / ".head_uuid").read_text().strip()
        assert head == "uuid-002"


# ---------------------------------------------------------------------------
# Read Tests
# ---------------------------------------------------------------------------


class TestGetSessionLogs:
    @pytest.mark.asyncio
    async def test_read_empty_session(self, tmp_sessions: Path):
        result = await get_session_logs(tmp_sessions, "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_read_after_writes(self, tmp_sessions: Path):
        entries = [_make_entry(content=f"log-{i}") for i in range(3)]
        for entry in entries:
            await append_session_log(tmp_sessions, "sess-read", entry)

        logs = await get_session_logs(tmp_sessions, "sess-read")
        assert logs is not None
        assert len(logs) == 3
        assert logs[0].content == "log-0"
        assert logs[2].content == "log-2"

    @pytest.mark.asyncio
    async def test_malformed_json_skipped(self, tmp_sessions: Path):
        """Malformed lines should be skipped, not crash the reader."""
        # Write a valid entry first
        entry = _make_entry(content="valid")
        await append_session_log(tmp_sessions, "sess-malformed", entry)

        # Manually inject a malformed line
        log_path = tmp_sessions / "sess-malformed" / "transcript.jsonl"
        with open(log_path, "a") as f:
            f.write("NOT_VALID_JSON\n")

        logs = await get_session_logs(tmp_sessions, "sess-malformed")
        assert logs is not None
        assert len(logs) == 1  # Only the valid entry


# ---------------------------------------------------------------------------
# Compaction Tests
# ---------------------------------------------------------------------------


class TestCompaction:
    @pytest.mark.asyncio
    async def test_compaction_marker_written(self, tmp_sessions: Path):
        entry = _make_entry(content="pre-compact")
        await append_session_log(tmp_sessions, "sess-compact", entry)

        result = await write_compaction_marker(tmp_sessions, "sess-compact", "Summary of compacted content")
        assert result is True

        # Post-compaction entry
        post = _make_entry(content="post-compact")
        await append_session_log(tmp_sessions, "sess-compact", post)

        # Full read should include all entries
        all_logs = await get_session_logs(tmp_sessions, "sess-compact")
        assert all_logs is not None
        assert len(all_logs) == 3  # pre + compaction + post

        # After-compact read should only include post-compaction entries
        after_compact = await get_session_logs(tmp_sessions, "sess-compact", after_last_compact=True)
        assert after_compact is not None
        assert len(after_compact) == 1
        assert after_compact[0].content == "post-compact"


# ---------------------------------------------------------------------------
# Session Lifecycle Tests
# ---------------------------------------------------------------------------


class TestSessionLifecycle:
    def test_create_entry(self):
        entry = create_entry("user", "test message")
        assert entry.entry_uuid
        assert entry.timestamp > 0
        assert entry.role == "user"
        assert entry.content == "test message"

    def test_create_entry_with_metadata(self):
        entry = create_entry("tool", "ran grep", metadata={"tool_name": "grep"})
        assert entry.metadata is not None
        assert entry.metadata["tool_name"] == "grep"

    @pytest.mark.asyncio
    async def test_clear_session(self, tmp_sessions: Path):
        entry = _make_entry(content="before clear")
        await append_session_log(tmp_sessions, "sess-clear", entry)

        clear_session("sess-clear")

        # Logs on disk should still exist (RULE_00: immutable)
        log_path = tmp_sessions / "sess-clear" / "transcript.jsonl"
        assert log_path.exists()

    @pytest.mark.asyncio
    async def test_clear_all_sessions(self, tmp_sessions: Path):
        for i in range(3):
            entry = _make_entry(content=f"session-{i}")
            await append_session_log(tmp_sessions, f"sess-{i}", entry)

        clear_all_sessions()

        # Disk data preserved per RULE_00
        for i in range(3):
            log_path = tmp_sessions / f"sess-{i}" / "transcript.jsonl"
            assert log_path.exists()


# ---------------------------------------------------------------------------
# Stats Tests
# ---------------------------------------------------------------------------


class TestSessionStats:
    @pytest.mark.asyncio
    async def test_stats_nonexistent(self, tmp_sessions: Path):
        stats = await get_session_stats(tmp_sessions, "no-such-session")
        assert stats is None

    @pytest.mark.asyncio
    async def test_stats_populated(self, tmp_sessions: Path):
        for role in ["user", "assistant", "user", "tool"]:
            entry = _make_entry(role=role, content=f"from {role}")
            await append_session_log(tmp_sessions, "sess-stats", entry)

        stats = await get_session_stats(tmp_sessions, "sess-stats")
        assert stats is not None
        assert stats["entry_count"] == 4
        assert stats["role_distribution"]["user"] == 2
        assert stats["role_distribution"]["assistant"] == 1
        assert stats["role_distribution"]["tool"] == 1
        assert stats["size_bytes"] > 0


# ---------------------------------------------------------------------------
# Concurrency Tests
# ---------------------------------------------------------------------------


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_appends_same_session(self, tmp_sessions: Path):
        """Multiple coroutines writing to the same session should serialize."""
        entries = [_make_entry(content=f"concurrent-{i}") for i in range(10)]

        # Fire all appends concurrently
        results = await asyncio.gather(*[append_session_log(tmp_sessions, "sess-concurrent", entry) for entry in entries])

        # All should succeed (sequential lock ensures no conflicts)
        assert all(results)

        # Verify all entries persisted
        logs = await get_session_logs(tmp_sessions, "sess-concurrent")
        assert logs is not None
        assert len(logs) == 10
