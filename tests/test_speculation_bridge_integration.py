# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests — Speculation Engine ↔ Gemini Bridge ↔ API Clients.

Validates the full pipeline:
  orchestrator.pair_programmer → GeminiPairProgrammer → InteractionsClient
  orchestrator.research_sweep → GeminiResearchSweep → DeepResearchClient

All tests use mocked API clients to avoid live calls, but verify
the wiring path is structurally sound end-to-end.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from speculation_engine.gemini_bridge import (
  GeminiPairProgrammer,
  GeminiResearchSweep,
  PairSession,
  PipelineMode,
  SweepResult,
)
from speculation_engine.orchestrator import (
  SpeculativeResearchConfig,
  SpeculativeResearchOrchestrator,
)


# ---------------------------------------------------------------------------
# Fixture: Orchestrator with bridge access
# ---------------------------------------------------------------------------


@pytest.fixture
def orchestrator(tmp_path):
  """Create an orchestrator with a Gemini API key."""
  return SpeculativeResearchOrchestrator(
    workspace=str(tmp_path),
    config=SpeculativeResearchConfig(trust_level=0),
    gemini_api_key="test-key-12345",
  )


# ---------------------------------------------------------------------------
# Test: Bridge exports from package __init__
# ---------------------------------------------------------------------------


class TestBridgeExports:
  """Verify bridge classes are exported from the package."""

  def test_import_from_package(self):
    from speculation_engine import (
      GeminiPairProgrammer,
      GeminiResearchSweep,
      PairSession,
      PipelineMode,
      SweepResult,
    )

    assert PipelineMode.PAIR_PROGRAMMING == "pair_programming"
    assert PipelineMode.RESEARCH_SWEEP == "research_sweep"
    assert PipelineMode.HYBRID == "hybrid"
    assert PairSession is not None
    assert SweepResult is not None
    assert GeminiPairProgrammer is not None
    assert GeminiResearchSweep is not None

  def test_pipeline_mode_in_all(self):
    import speculation_engine

    assert "GeminiPairProgrammer" in speculation_engine.__all__
    assert "GeminiResearchSweep" in speculation_engine.__all__
    assert "PipelineMode" in speculation_engine.__all__
    assert "PairSession" in speculation_engine.__all__
    assert "SweepResult" in speculation_engine.__all__


# ---------------------------------------------------------------------------
# Test: Orchestrator → Bridge lazy init
# ---------------------------------------------------------------------------


class TestOrchestratorBridgeInit:
  """Verify orchestrator lazily initializes bridge components."""

  def test_pair_programmer_lazy_init(self, orchestrator):
    """pair_programmer property creates GeminiPairProgrammer on first access."""
    pp = orchestrator.pair_programmer
    assert isinstance(pp, GeminiPairProgrammer)
    # Second access returns the same instance
    assert orchestrator.pair_programmer is pp

  def test_research_sweep_lazy_init(self, orchestrator):
    """research_sweep property creates GeminiResearchSweep on first access."""
    rs = orchestrator.research_sweep
    assert isinstance(rs, GeminiResearchSweep)
    assert orchestrator.research_sweep is rs

  def test_api_key_propagated(self, orchestrator):
    """API key is passed through to the bridge clients."""
    pp = orchestrator.pair_programmer
    assert pp._api_key == "test-key-12345"

    rs = orchestrator.research_sweep
    assert rs._api_key == "test-key-12345"

  def test_no_api_key_still_initializes(self, tmp_path):
    """Bridge still initializes without an API key (will fail on call)."""
    orch = SpeculativeResearchOrchestrator(workspace=str(tmp_path))
    pp = orch.pair_programmer
    assert isinstance(pp, GeminiPairProgrammer)
    assert pp._api_key is None


# ---------------------------------------------------------------------------
# Test: Full pipeline — orchestrator → bridge → mocked client
# ---------------------------------------------------------------------------


class TestFullPipelineMocked:
  """End-to-end pipeline with mocked API clients."""

  def test_pair_programming_session(self, orchestrator):
    """orchestrator.pair_programmer.start_session → send via mocked client."""
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.id = "interaction-abc"
    mock_result.usage = {"total_tokens": 150}
    mock_result.text = "Here's the refactored code..."
    mock_client.create.return_value = mock_result

    # Inject the mock client
    orchestrator.pair_programmer._client = mock_client

    # Start session
    session = orchestrator.pair_programmer.start_session(
      system_prompt="You are a Python expert.",
      model="gemini-3-flash-preview",
    )
    assert isinstance(session, PairSession)
    assert session.model == "gemini-3-flash-preview"
    assert session.turn_count == 1
    assert "interaction-abc" in session.interaction_chain

    # Send message
    _response = orchestrator.pair_programmer.send(
      "Refactor this function.",
      session=session,
    )
    assert session.turn_count == 2
    assert mock_client.create.call_count == 2

  def test_research_sweep_run(self, orchestrator):
    """orchestrator.research_sweep.run via mocked DeepResearchClient."""
    mock_client = MagicMock()
    mock_report = MagicMock()
    mock_report.text = "# Research Report\n\nFindings..."
    mock_report.images = []
    mock_report.interaction_id = "sweep-xyz"
    mock_client.research.return_value = mock_report
    mock_client._agent = "deep-research-max"

    # Inject mock
    orchestrator.research_sweep._client = mock_client

    result = orchestrator.research_sweep.run(
      "Analyze legal AI competitive landscape",
      timeout=60.0,
    )
    assert isinstance(result, SweepResult)
    assert "Research Report" in result.report_text
    assert result.interaction_id == "sweep-xyz"
    assert result.duration_seconds > 0
    mock_client.research.assert_called_once()

  def test_research_sweep_plan_then_execute(self, orchestrator):
    """Plan → execute flow through the bridge."""
    mock_client = MagicMock()
    mock_plan = MagicMock()
    mock_plan.plan_text = "Step 1: Gather data..."
    mock_plan.agent = "deep-research-max"
    mock_client.plan.return_value = mock_plan

    mock_report = MagicMock()
    mock_report.text = "Final report content"
    mock_report.images = ["chart.png"]
    mock_report.interaction_id = "plan-exec-123"
    mock_client.execute_plan.return_value = mock_report

    orchestrator.research_sweep._client = mock_client

    plan = orchestrator.research_sweep.plan("EV battery supply chain risks")
    assert plan.plan_text == "Step 1: Gather data..."

    result = orchestrator.research_sweep.execute(plan)
    assert result.report_text == "Final report content"
    assert len(result.images) == 1

  def test_streaming_pair_programming(self, orchestrator):
    """Stream response from pair programmer."""
    mock_client = MagicMock()
    mock_events = [
      MagicMock(interaction_id="stream-1", text="def "),
      MagicMock(interaction_id="stream-1", text="refactored():"),
      MagicMock(interaction_id="stream-1", text="\n    pass"),
    ]
    mock_client.stream.return_value = iter(mock_events)

    orchestrator.pair_programmer._client = mock_client

    session = PairSession(session_id="test-stream")
    chunks = list(
      orchestrator.pair_programmer.send_stream(
        "Refactor this",
        session=session,
      )
    )
    assert chunks == ["def ", "refactored():", "\n    pass"]
    assert "stream-1" in session.interaction_chain

  def test_research_follow_up(self, orchestrator):
    """Follow-up question on a completed sweep."""
    mock_client = MagicMock()
    mock_client.follow_up.return_value = "The main risk is..."
    orchestrator.research_sweep._client = mock_client

    result = SweepResult(
      query="EV risks",
      report_text="...",
      interaction_id="sweep-follow",
    )
    answer = orchestrator.research_sweep.follow_up(result, "What's the biggest risk?")
    assert answer == "The main risk is..."
    mock_client.follow_up.assert_called_once_with(
      "sweep-follow", "What's the biggest risk?"
    )


# ---------------------------------------------------------------------------
# Test: Pipeline mode enum
# ---------------------------------------------------------------------------


class TestPipelineModeIntegration:
  """Verify PipelineMode is usable for orchestrator routing decisions."""

  def test_mode_selection(self):
    modes = list(PipelineMode)
    assert len(modes) == 4

  def test_mode_string_comparison(self):
    assert PipelineMode("pair_programming") == PipelineMode.PAIR_PROGRAMMING
    assert PipelineMode("research_sweep") == PipelineMode.RESEARCH_SWEEP
    assert PipelineMode("hybrid") == PipelineMode.HYBRID
    assert PipelineMode("suggestion") == PipelineMode.SUGGESTION

  def test_mode_iteration(self):
    """Modes are iterable for UI display."""
    labels = [m.value for m in PipelineMode]
    assert "pair_programming" in labels
    assert "research_sweep" in labels
    assert "hybrid" in labels
    assert "suggestion" in labels
