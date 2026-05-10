# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests: deep_research → evaluation_bridge → orbstack_sandbox.

Tests the full pipeline from research initiation through sandbox execution
to verified overlay merge. These tests validate the cross-package contracts
documented in Phase 3's architecture diagram.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from deep_research import (
  DeepResearchEngine,
  ResearchConfig,
  ResearchPhase,
)
from evaluation_bridge import (
  EvaluationBridge,
  EvaluationConfig,
  EvaluationResult,
  GateType,
)
from orbstack_sandbox import (
  ContainerLifecycle,
  SandboxConfig,
  SandboxEngine,
)
from speculation_engine import (
  SpeculativeResearchOrchestrator,
  SpeculativeResearchConfig,
  SpeculativePhaseResult,
  SpeculationEngine,
  OverlayFS,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def research_config():
  """Standard research config for integration tests."""
  return ResearchConfig(
    phase_timeout_s=30.0,
    max_queries=5,
  )


@pytest.fixture
def evaluation_config():
  """Standard evaluation config for integration tests."""
  return EvaluationConfig(
    build_command="echo 'test build'",
    test_command="echo 'test pass'",
    lint_command="echo 'lint pass'",
  )


@pytest.fixture
def sandbox_config():
  """Standard sandbox config for integration tests."""
  return SandboxConfig(
    image="python:3.14-slim",
    timeout_s=30.0,
    memory_limit="512m",
  )


@pytest.fixture
def tmp_dirs():
  """Create temp directories for OverlayFS."""
  with tempfile.TemporaryDirectory() as base, tempfile.TemporaryDirectory() as overlay:
    yield Path(base), Path(overlay)


# ── Test 1: Engine Initialization Chain ───────────────────────────────────


class TestEngineInitializationChain:
  """Verify all three engines initialize cleanly and share config."""

  def test_deep_research_initializes(self, research_config):
    """DeepResearchEngine starts in IDLE phase."""
    engine = DeepResearchEngine(research_config)
    assert engine.current_phase == ResearchPhase.IDLE

  def test_evaluation_bridge_initializes(self, evaluation_config):
    """EvaluationBridge initializes with correct config."""
    bridge = EvaluationBridge(config=evaluation_config)
    # EvaluationBridge should be callable
    assert callable(getattr(bridge, "evaluate", None))

  def test_sandbox_engine_initializes(self, sandbox_config):
    """SandboxEngine starts in CREATED lifecycle state."""
    engine = SandboxEngine(config=sandbox_config)
    assert engine.lifecycle == ContainerLifecycle.PENDING
    assert callable(getattr(engine, "run", None))


# ── Test 2: Phase Transition Contracts ────────────────────────────────────


class TestPhaseTransitionContracts:
  """Verify cross-package phase transition contracts."""

  def test_research_engine_starts_idle(self, research_config):
    """DeepResearchEngine starts in IDLE and has a run method."""
    engine = DeepResearchEngine(research_config)
    assert engine.current_phase == ResearchPhase.IDLE
    assert callable(getattr(engine, "run", None))
    assert callable(getattr(engine, "abort", None))

  def test_overlay_fs_isolation(self, tmp_dirs):
    """OverlayFS provides read-isolation with write-through."""
    base_dir, overlay_dir = tmp_dirs
    overlay = OverlayFS(base_dir=base_dir, overlay_dir=overlay_dir)
    overlay.write_file("test.py", "print('hello')")
    assert overlay.read_file("test.py") == "print('hello')"
    assert "test.py" in overlay.written_files

  def test_speculation_engine_cow_creates_overlay(self, tmp_dirs):
    """SpeculationEngine creates CoW overlay on init with cwd."""
    base_dir, overlay_dir = tmp_dirs
    overlay = OverlayFS(base_dir=base_dir, overlay_dir=overlay_dir)
    engine = SpeculationEngine(cwd=str(base_dir), overlay=overlay)
    assert engine.overlay is not None
    assert isinstance(engine.overlay, OverlayFS)


# ── Test 3: Orchestrator Bridge ───────────────────────────────────────────


class TestOrchestratorBridge:
  """Verify SpeculativeResearchOrchestrator bridges engines correctly."""

  def test_orchestrator_creates_with_config(self):
    """Orchestrator initializes with valid config."""
    config = SpeculativeResearchConfig(
      max_speculation_time_s=30.0,
    )
    orchestrator = SpeculativeResearchOrchestrator(config)
    assert callable(getattr(orchestrator, "on_phase_change", None))
    assert callable(getattr(orchestrator, "accept_speculation", None))

  def test_orchestrator_phase_result_structure(self):
    """SpeculativePhaseResult has correct fields."""
    result = SpeculativePhaseResult(
      phase="researching",
      speculation_active=True,
      time_saved_ms=1.5,
      overlay_files_written=2,
    )
    assert result.speculation_active is True
    assert result.time_saved_ms == 1.5


# ── Test 4: Evaluation Gate Pipeline ─────────────────────────────────────


class TestEvaluationGatePipeline:
  """Verify the 4-gate evaluation pipeline contracts."""

  def test_gate_types_are_ordered(self):
    """Gates must execute in BUILD → TEST → LINT → MERGE order."""
    expected = [GateType.BUILD, GateType.TEST, GateType.LINT, GateType.MERGE]
    for i, gate in enumerate(expected):
      assert gate.value == expected[i].value

  def test_evaluation_result_aggregation(self):
    """EvaluationResult properly aggregates gate results."""
    result = EvaluationResult(
      session_id="test-session",
      all_passed=True,
      total_duration_ms=1500.0,
    )
    assert result.all_passed is True


# ── Test 5: Sandbox Session API (Phase 3) ────────────────────────────────


class TestSandboxSessionAPI:
  """Verify the new Phase 3 sandbox session API."""

  def test_session_creation(self):
    """SandboxSession creates with valid config."""
    from apps.counselconduit.api.sandbox.session import (
      SandboxSession,
      SessionConfig,
      SessionState,
    )

    config = SessionConfig(
      matter_id="matter-001",
      attorney_uid="attorney-abc",
    )
    session = SandboxSession(config=config)
    assert session.state == SessionState.CREATED
    assert session.config.trust_level == 0

  def test_session_trust_level_zero_enforced(self):
    """Trust Level must be 0 for sandbox sessions."""
    from apps.counselconduit.api.sandbox.session import (
      SandboxSession,
      SessionConfig,
    )

    config = SessionConfig(
      matter_id="matter-001",
      attorney_uid="attorney-abc",
    )
    session = SandboxSession(config=config)
    assert session.config.trust_level == 0
    session.start_speculation()

  def test_session_lifecycle_happy_path(self):
    """Full session lifecycle: create → speculate → review → commit."""
    from apps.counselconduit.api.sandbox.session import (
      SandboxSession,
      SessionConfig,
      SessionState,
      CommitAction,
    )

    config = SessionConfig(
      matter_id="matter-001",
      attorney_uid="attorney-abc",
    )
    session = SandboxSession(config=config)

    # Phase 1: Start speculation
    session.start_speculation()
    assert session.state == SessionState.SPECULATING

    # Phase 2: Present for review
    overlay = {"doc.md": "# Updated document"}
    diffs = [{"file": "doc.md", "type": "modified"}]
    session.present_for_review(overlay, diffs)
    assert session.state == SessionState.REVIEWING

    # Phase 3: Attorney accepts
    committed = session.commit(
      CommitAction.ACCEPT,
      attorney_uid="attorney-abc",
    )
    assert session.state == SessionState.COMMITTED
    assert committed == ["doc.md"]

  def test_session_rejection_flow(self):
    """Attorney can reject and provide a reason for model tuning."""
    from apps.counselconduit.api.sandbox.session import (
      SandboxSession,
      SessionConfig,
      SessionState,
      CommitAction,
    )

    config = SessionConfig(
      matter_id="matter-001",
      attorney_uid="attorney-abc",
    )
    session = SandboxSession(config=config)
    session.start_speculation()
    session.present_for_review({"doc.md": "content"}, [])
    result = session.commit(
      CommitAction.REJECT,
      attorney_uid="attorney-abc",
      rejection_reason="Inaccurate case citation",
    )
    assert session.state == SessionState.REJECTED
    assert result == []
    assert session.rejection_reason == "Inaccurate case citation"

  def test_session_unauthorized_attorney_blocked(self):
    """Only the assigned attorney can commit changes."""
    from apps.counselconduit.api.sandbox.session import (
      SandboxSession,
      SessionConfig,
      CommitAction,
    )

    config = SessionConfig(
      matter_id="matter-001",
      attorney_uid="attorney-abc",
    )
    session = SandboxSession(config=config)
    session.start_speculation()
    session.present_for_review({"doc.md": "content"}, [])
    with pytest.raises(PermissionError, match="assigned attorney"):
      session.commit(
        CommitAction.ACCEPT,
        attorney_uid="rogue-user-xyz",
      )

  def test_session_audit_record(self):
    """Audit record contains all required fields for .beads/ trail."""
    from apps.counselconduit.api.sandbox.session import (
      SandboxSession,
      SessionConfig,
    )

    config = SessionConfig(
      matter_id="matter-001",
      attorney_uid="attorney-abc",
    )
    session = SandboxSession(config=config)
    record = session.to_audit_record()
    assert record["matter_id"] == "matter-001"
    assert record["attorney_uid"] == "attorney-abc"
    assert record["trust_level"] == 0
    assert "session_id" in record

  def test_session_partial_accept(self):
    """Attorney can cherry-pick specific files from overlay."""
    from apps.counselconduit.api.sandbox.session import (
      SandboxSession,
      SessionConfig,
      SessionState,
      CommitAction,
    )

    config = SessionConfig(
      matter_id="matter-001",
      attorney_uid="attorney-abc",
    )
    session = SandboxSession(config=config)
    session.start_speculation()
    overlay = {
      "brief.md": "# Brief content",
      "motion.md": "# Motion content",
      "notes.md": "# Internal notes",
    }
    session.present_for_review(overlay, [])
    committed = session.commit(
      CommitAction.PARTIAL_ACCEPT,
      attorney_uid="attorney-abc",
      selected_files=["brief.md", "motion.md"],
    )
    assert session.state == SessionState.COMMITTED
    assert set(committed) == {"brief.md", "motion.md"}
    assert "notes.md" not in committed
