from unittest.mock import patch

import pytest

from agents.legal_whiteboard import whiteboard


@pytest.fixture(autouse=True)
def reset_whiteboard():
    """Reset whiteboard state before each test."""
    whiteboard.state = {
        "total_revenue_usd": 0.0,
        "current_level": 0,
        "agents": {},
        "revenue_events": [],
        "last_updated": "",
    }
    whiteboard._save_state()


def test_revenue_recording():
    whiteboard.record_revenue(100.0, "Test Source", "agent_001")
    assert whiteboard.state["total_revenue_usd"] == 100.0
    assert len(whiteboard.state["revenue_events"]) == 1
    assert whiteboard.state["agents"]["agent_001"]["revenue_generated"] == 100.0


def test_level_progression():
    # Level 1
    whiteboard.record_revenue(10_000, "Big Deal")
    assert whiteboard.state["current_level"] == 1

    # Level 2
    whiteboard.record_revenue(90_000, "Another Deal")  # Total 100k
    assert whiteboard.state["current_level"] == 2


@patch("agents.bar_exam_protocol.BarExamProtocol.spawn_first_child")
def test_spawn_trigger(mock_spawn):
    # Trigger Level 4 ($10M)
    whiteboard.record_revenue(10_000_000, "Mega Deal")
    assert whiteboard.state["current_level"] == 4
    mock_spawn.assert_called_once()


@patch("agents.bar_exam_protocol.BarExamProtocol.activate_swarm_mode")
def test_swarm_trigger(mock_swarm):
    # Trigger Level 5 ($100M)
    whiteboard.record_revenue(100_000_000, "Unicorn Status")
    assert whiteboard.state["current_level"] == 5
    mock_swarm.assert_called_once()
