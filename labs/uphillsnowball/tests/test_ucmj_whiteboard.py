# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# labs/uphillsnowball/tests/test_ucmj_whiteboard.py
"""Unit tests for SwarmWhiteboard.write_state OCC logic (Item 13).

Uses fakeredis to mock Redis for deterministic testing.
"""

from __future__ import annotations

import json

import pytest

try:
    import fakeredis
except ImportError:
    fakeredis = None

from src.agents.discipline.ucmj_whiteboard import SwarmWhiteboard


@pytest.fixture
def whiteboard():
    """Create a SwarmWhiteboard with a fakeredis backend."""
    if fakeredis is None:
        pytest.skip("fakeredis not installed")
    board = SwarmWhiteboard.__new__(SwarmWhiteboard)
    board.r = fakeredis.FakeRedis(decode_responses=True)
    return board


class TestSwarmWhiteboardRead:
    """Tests for read_state."""

    def test_read_nonexistent_issue(self, whiteboard):
        """Nonexistent issue returns version 0 and empty data."""
        state = whiteboard.read_state("ISSUE-999")
        assert state["version"] == 0
        assert state["data"] == {}

    def test_read_existing_issue(self, whiteboard):
        """Pre-set state is correctly deserialized."""
        whiteboard.r.set(
            "whiteboard:ISSUE-1",
            json.dumps({"version": 3, "data": {"status": "in_progress"}}),
        )
        state = whiteboard.read_state("ISSUE-1")
        assert state["version"] == 3
        assert state["data"]["status"] == "in_progress"


class TestSwarmWhiteboardWrite:
    """Tests for write_state OCC logic."""

    def test_write_to_empty_issue(self, whiteboard):
        """First write to empty issue succeeds with version 0."""
        success = whiteboard.write_state("ISSUE-1", expected_version=0, new_data={"status": "assigned"})
        assert success is True
        state = whiteboard.read_state("ISSUE-1")
        assert state["version"] == 1
        assert state["data"]["status"] == "assigned"

    def test_write_with_correct_version(self, whiteboard):
        """Write with matching version succeeds."""
        whiteboard.write_state("ISSUE-2", expected_version=0, new_data={"v": 1})
        success = whiteboard.write_state("ISSUE-2", expected_version=1, new_data={"v": 2})
        assert success is True
        state = whiteboard.read_state("ISSUE-2")
        assert state["version"] == 2

    def test_write_with_stale_version_fails(self, whiteboard):
        """Write with stale version returns False (OCC conflict)."""
        whiteboard.write_state("ISSUE-3", expected_version=0, new_data={"v": 1})
        # Another agent increments
        whiteboard.write_state("ISSUE-3", expected_version=1, new_data={"v": 2})
        # First agent tries with stale version
        success = whiteboard.write_state("ISSUE-3", expected_version=1, new_data={"v": "STALE"})
        assert success is False
        state = whiteboard.read_state("ISSUE-3")
        assert state["data"]["v"] == 2  # Not overwritten

    def test_sequential_writes_increment_version(self, whiteboard):
        """Sequential correct writes increment version monotonically."""
        for i in range(5):
            assert whiteboard.write_state("ISSUE-SEQ", expected_version=i, new_data={"step": i})
        state = whiteboard.read_state("ISSUE-SEQ")
        assert state["version"] == 5


class TestSwarmWhiteboardClear:
    """Tests for clear_issue."""

    def test_clear_existing_issue(self, whiteboard):
        """Clearing an issue resets it to nonexistent."""
        whiteboard.write_state("ISSUE-CLR", expected_version=0, new_data={"x": 1})
        whiteboard.clear_issue("ISSUE-CLR")
        state = whiteboard.read_state("ISSUE-CLR")
        assert state["version"] == 0

    def test_clear_nonexistent_issue_no_error(self, whiteboard):
        """Clearing a nonexistent issue doesn't raise."""
        whiteboard.clear_issue("ISSUE-NONEXISTENT")  # Should not raise
