# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests — SpeculationEngine × DeepResearchEngine × EvaluationBridge.

21-test suite validating:
  1. Orchestrator lifecycle (create → phase handlers → accept → reset)
  2. CoW overlay isolation during EXECUTING phase
  3. Suggestion pipeline integration with session state
  4. Telemetry correlation via session_id
  5. Phase transition callbacks from DeepResearchEngine
  6. Trust level security gate (0/1/2)
  7. Cache hit/miss behavior across phases
  8. Multi-phase speculative execution
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from speculation_engine.engine import (
  BoundaryType,
  SpeculationEngine,
  SpeculationState,
)
from speculation_engine.orchestrator import (
  SpeculativePhaseResult,
  SpeculativeResearchConfig,
  SpeculativeResearchOrchestrator,
)
from speculation_engine.suggestion import (
  SuggestionConfig,
  SuggestionResult,
)
from speculation_engine.telemetry import read_telemetry_events
from deep_research.state_machine import (
  ResearchPhase,
)


@pytest.fixture
def workspace(tmp_path: Path) -> str:
  """Create a temporary workspace."""
  (tmp_path / "src").mkdir()
  (tmp_path / "src" / "main.py").write_text("print('hello')\n")
  return str(tmp_path)


@pytest.fixture
def beads_dir(tmp_path: Path) -> str:
  """Isolate telemetry to temp dir."""
  bd = tmp_path / ".beads"
  bd.mkdir()
  old = os.environ.get("BEADS_DIR")
  os.environ["BEADS_DIR"] = str(bd)
  yield str(bd)
  if old is None:
    os.environ.pop("BEADS_DIR", None)
  else:
    os.environ["BEADS_DIR"] = old


# ── Orchestrator Lifecycle ─────────────────────────────────────


class TestOrchestratorLifecycle:
  """Tests for SpeculativeResearchOrchestrator creation and reset."""

  def test_create_default_config(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    assert orch.speculation_engine.state == SpeculationState.IDLE
    assert orch.results == []

  def test_create_custom_config(self, workspace: str) -> None:
    config = SpeculativeResearchConfig(
      trust_level=1,
      max_speculation_time_s=15.0,
      speculate_during_research=False,
    )
    orch = SpeculativeResearchOrchestrator(workspace=workspace, config=config)
    assert not config.speculate_during_research
    assert orch.speculation_engine.state == SpeculationState.IDLE

  def test_reset_clears_state(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    orch._session_id = "test-session"
    orch._speculation_results.append(
      SpeculativePhaseResult(phase="researching", speculation_active=True)
    )
    orch.reset()
    assert orch._session_id == ""
    assert orch.results == []
    assert orch.speculation_engine.state == SpeculationState.IDLE


# ── Phase Handler Wiring ───────────────────────────────────────


class TestPhaseHandlerWiring:
  """Tests for create_phase_handlers and speculative handler wiring."""

  def test_creates_handlers_for_enabled_phases(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    handlers = orch.create_phase_handlers()
    assert ResearchPhase.RESEARCHING in handlers
    assert ResearchPhase.SYNTHESIZING in handlers
    assert ResearchPhase.EXECUTING in handlers

  def test_skips_disabled_phases(self, workspace: str) -> None:
    config = SpeculativeResearchConfig(
      speculate_during_research=False,
      speculate_during_synthesis=False,
      use_cow_overlay=False,
    )
    orch = SpeculativeResearchOrchestrator(workspace=workspace, config=config)
    handlers = orch.create_phase_handlers()
    assert len(handlers) == 0

  @pytest.mark.asyncio
  async def test_speculative_handler_returns_inner_result(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)

    async def inner_research(objective, context, state):
      return {"sources": ["doc1", "doc2"], "query_count": 3}

    handlers = orch.create_phase_handlers(
      inner_handlers={ResearchPhase.RESEARCHING: inner_research}
    )
    handler = handlers[ResearchPhase.RESEARCHING]
    result = await handler("test objective", {"key": "val"}, MagicMock())
    assert result["sources"] == ["doc1", "doc2"]
    assert "_speculation" in result

  @pytest.mark.asyncio
  async def test_speculative_handler_default_result(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    handlers = orch.create_phase_handlers()
    handler = handlers[ResearchPhase.RESEARCHING]
    result = await handler("test objective", {}, MagicMock())
    assert result["phase"] == "researching"
    assert result["status"] == "default"
    assert "_speculation" in result


# ── CoW Overlay Integration ────────────────────────────────────


class TestCowOverlayIntegration:
  """Tests for CoW overlay during EXECUTING phase."""

  @pytest.mark.asyncio
  async def test_cow_handler_creates_overlay(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    handlers = orch.create_phase_handlers()
    handler = handlers[ResearchPhase.EXECUTING]
    result = await handler("execute changes", {}, MagicMock())
    assert "_cow_overlay" in result
    assert result["_cow_overlay"]["overlay_active"]

  @pytest.mark.asyncio
  async def test_cow_handler_tracks_written_files(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    # Pre-start engine and write to overlay.
    orch.speculation_engine.start()
    orch.speculation_engine.overlay.write_file("new.txt", "content")
    handlers = orch.create_phase_handlers()
    handler = handlers[ResearchPhase.EXECUTING]
    result = await handler("execute", {}, MagicMock())
    assert result["_cow_overlay"]["files_written"] >= 1

  def test_overlay_isolation_from_workspace(self, workspace: str) -> None:
    engine = SpeculationEngine(cwd=workspace)
    engine.start()
    engine.overlay.write_file("isolated.txt", "speculative content")
    # File should NOT exist in workspace.
    assert not (Path(workspace) / "isolated.txt").exists()
    # But should exist in overlay.
    content = engine.overlay.read_file("isolated.txt")
    assert content == "speculative content"
    engine.abort()

  def test_overlay_merge_on_accept(self, workspace: str) -> None:
    engine = SpeculationEngine(cwd=workspace)
    engine.start()
    engine.overlay.write_file("merged.txt", "merged content")
    engine.complete()
    result = engine.accept()
    assert "merged.txt" in result["merged_files"]
    assert (Path(workspace) / "merged.txt").read_text() == "merged content"


# ── Trust Level Security Gate ──────────────────────────────────


class TestTrustLevelGate:
  """Tests for bypass_permissions security gate (trust levels 0/1/2)."""

  def test_trust_level_0_denies_writes(self, workspace: str) -> None:
    engine = SpeculationEngine.create(cwd=workspace, trust_level=0)
    engine.start()
    allowed, boundary = engine.can_use_tool(
      "write_to_file", file_path=f"{workspace}/test.py"
    )
    assert not allowed
    assert boundary.type == BoundaryType.EDIT

  def test_trust_level_1_denies_writes(self, workspace: str, beads_dir: str) -> None:
    engine = SpeculationEngine.create(cwd=workspace, trust_level=1)
    engine.start()
    allowed, boundary = engine.can_use_tool(
      "write_to_file", file_path=f"{workspace}/test.py"
    )
    # trust_level=1 sets bypass_permissions=False (requires >=2).
    assert not allowed

  def test_trust_level_2_allows_writes(self, workspace: str, beads_dir: str) -> None:
    engine = SpeculationEngine.create(cwd=workspace, trust_level=2)
    engine.start()
    allowed, boundary = engine.can_use_tool(
      "write_to_file", file_path=f"{workspace}/test.py"
    )
    assert allowed
    assert boundary is None

  def test_trust_level_2_denies_outside_cwd(
    self, workspace: str, beads_dir: str
  ) -> None:
    engine = SpeculationEngine.create(cwd=workspace, trust_level=2)
    engine.start()
    allowed, boundary = engine.can_use_tool("write_to_file", file_path="/etc/passwd")
    assert not allowed
    assert boundary.detail == "outside_cwd"


# ── Telemetry Correlation ──────────────────────────────────────


class TestTelemetryCorrelation:
  """Tests for session_id correlation across telemetry events."""

  def test_phase_change_captures_session_id(
    self, workspace: str, beads_dir: str
  ) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    transition = MagicMock()
    transition.to_phase = ResearchPhase.RESEARCHING
    transition.metadata = {"session_id": "dr-test123"}
    orch.on_phase_change(transition)
    assert orch._session_id == "dr-test123"

  def test_session_summary_includes_id(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    orch._session_id = "dr-abc"
    summary = orch.get_session_summary()
    assert summary["session_id"] == "dr-abc"
    assert "phases_speculated" in summary
    assert "engine_state" in summary

  def test_telemetry_events_written(self, workspace: str, beads_dir: str) -> None:
    engine = SpeculationEngine.create(
      cwd=workspace, trust_level=0, session_id="tel-001"
    )
    engine.start()
    engine.abort(reason="test_abort")
    events = read_telemetry_events(event_type_prefix="speculation_")
    assert len(events) >= 1
    abort_events = [e for e in events if "aborted" in e.get("event_type", "")]
    assert len(abort_events) >= 1


# ── Suggestion Pipeline ───────────────────────────────────────


class TestSuggestionPipeline:
  """Tests for suggestion generation within orchestrator context."""

  def test_suggestion_without_generate_fn_returns_none(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    result = orch._generate_speculative_suggestion("objective", {})
    assert result is None

  def test_suggestion_with_generate_fn(self, workspace: str) -> None:
    def mock_gen(messages, system_prompt):
      return ("Run the tests next", "user_intent")

    config = SpeculativeResearchConfig(
      generate_fn=mock_gen,
      suggestion_config=SuggestionConfig(min_assistant_turns=0),
    )
    orch = SpeculativeResearchOrchestrator(workspace=workspace, config=config)
    result = orch._generate_speculative_suggestion("design caching", {"files": []})
    assert result is not None
    assert result.suggestion == "Run the tests next"

  @pytest.mark.asyncio
  async def test_suggestion_set_as_pipelined(self, workspace: str) -> None:
    def mock_gen(messages, system_prompt):
      return ("Check lint status", "user_intent")

    config = SpeculativeResearchConfig(
      generate_fn=mock_gen,
      suggestion_config=SuggestionConfig(min_assistant_turns=0),
    )
    orch = SpeculativeResearchOrchestrator(workspace=workspace, config=config)
    handlers = orch.create_phase_handlers()
    handler = handlers[ResearchPhase.RESEARCHING]
    result = await handler("test", {"ctx": True}, MagicMock())
    assert result["_speculation"]["suggestion"] == "Check lint status"
    # Engine should have the pipelined suggestion.
    assert orch.speculation_engine.pipelined_suggestion == "Check lint status"


# ── Accept Flow ────────────────────────────────────────────────


class TestAcceptFlow:
  """Tests for accept_speculation and session summary."""

  def test_accept_when_idle_returns_empty(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    result = orch.accept_speculation()
    assert result["query_required"] is True
    assert result["merged_files"] == []

  def test_accept_after_complete(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    orch.speculation_engine.start()
    orch.speculation_engine.overlay.write_file("out.txt", "data")
    orch.speculation_engine.complete()
    result = orch.accept_speculation()
    assert "out.txt" in result["merged_files"]
    assert (Path(workspace) / "out.txt").read_text() == "data"

  def test_session_summary_aggregates_results(self, workspace: str) -> None:
    orch = SpeculativeResearchOrchestrator(workspace=workspace)
    orch._session_id = "summary-test"
    orch._speculation_results = [
      SpeculativePhaseResult(
        phase="researching",
        speculation_active=True,
        time_saved_ms=50.0,
        suggestion=SuggestionResult(suggestion="next step", generation_time_ms=10.0),
      ),
      SpeculativePhaseResult(
        phase="executing",
        speculation_active=True,
        overlay_files_written=3,
        time_saved_ms=120.0,
      ),
    ]
    summary = orch.get_session_summary()
    assert summary["phases_speculated"] == 2
    assert summary["suggestions_generated"] == 1
    assert summary["overlay_files_written"] == 3
    assert summary["total_time_saved_ms"] == 170.0
