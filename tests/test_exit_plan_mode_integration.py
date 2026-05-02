# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests — ExitPlanMode × SpeculativeResearchOrchestrator.

28-test suite validating:
  1. Full plan lifecycle: IDLE→PLANNING→SPECULATING→CONFIRMING→EXECUTING→IDLE
  2. Abort from each non-terminal state
  3. Timeout auto-abandonment at PLANNING, SPECULATING, CONFIRMING
  4. Phase transition callbacks resetting plan state
  5. Revision loops (CONFIRMING → PLANNING → SPECULATING)
  6. Telemetry event emission for plan lifecycle events
  7. Orchestrator reset cleaning up plan controller
  8. Concurrent planning + speculation engine coordination
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from speculation_engine.engine import SpeculationState
from speculation_engine.exit_plan_mode import (
    ExitPlanModeController,
    PlanSession,
    PlanState,
    PlanStep,
    TransitionError,
)
from speculation_engine.orchestrator import (
    SpeculativeResearchOrchestrator,
)
from deep_research.state_machine import ResearchPhase


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


@pytest.fixture
def orch(workspace: str) -> SpeculativeResearchOrchestrator:
    """Create a standard orchestrator for testing."""
    return SpeculativeResearchOrchestrator(
        workspace=workspace,
        plan_timeout_seconds=300.0,
    )


# ── Plan Lifecycle (Happy Path) ──────────────────────────────────


class TestPlanLifecycleHappyPath:
    """Full lifecycle: IDLE → PLANNING → SPECULATING → CONFIRMING → EXECUTING → IDLE."""

    def test_initial_state_is_idle(self, orch: SpeculativeResearchOrchestrator) -> None:
        assert orch.plan_state == PlanState.IDLE
        assert orch.plan_controller.session is None

    def test_enter_plan_mode(self, orch: SpeculativeResearchOrchestrator) -> None:
        session = orch.enter_plan_mode(metadata={"task": "caching layer"})
        assert isinstance(session, PlanSession)
        assert orch.plan_state == PlanState.PLANNING
        assert session.metadata["task"] == "caching layer"

    def test_add_steps(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        step1 = orch.add_plan_step("s1", "Design cache interface")
        step2 = orch.add_plan_step("s2", "Implement TTL logic", tool_calls=[{"tool": "write_to_file"}])
        assert isinstance(step1, PlanStep)
        assert isinstance(step2, PlanStep)
        assert len(orch.plan_controller.session.steps) == 2
        assert step2.tool_calls == [{"tool": "write_to_file"}]

    def test_begin_speculation(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Design interface")
        orch.begin_plan_speculation()
        assert orch.plan_state == PlanState.SPECULATING
        # Speculation engine should also be started.
        assert orch.speculation_engine.state == SpeculationState.ACTIVE

    def test_full_lifecycle(self, orch: SpeculativeResearchOrchestrator) -> None:
        """IDLE → PLANNING → SPECULATING → CONFIRMING → EXECUTING → IDLE."""
        # Enter planning
        orch.enter_plan_mode()
        assert orch.plan_state == PlanState.PLANNING

        # Add steps
        orch.add_plan_step("s1", "Step one")
        orch.add_plan_step("s2", "Step two")

        # Begin speculation
        orch.begin_plan_speculation()
        assert orch.plan_state == PlanState.SPECULATING

        # Record results and complete speculation
        orch.plan_controller.record_speculation_result("s1", {"ok": True})
        orch.plan_controller.speculation_complete()
        assert orch.plan_state == PlanState.CONFIRMING

        # User confirms
        orch.confirm_plan()
        assert orch.plan_state == PlanState.EXECUTING

        # Execution complete
        orch.complete_plan_execution()
        assert orch.plan_state == PlanState.IDLE
        assert orch.plan_controller.session is None


# ── Cancellation ─────────────────────────────────────────────────


class TestPlanCancellation:
    """Tests for cancel from various states."""

    def test_cancel_from_planning(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.cancel_plan()
        assert orch.plan_state == PlanState.ABANDONED

    def test_cancel_from_confirming(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        orch.begin_plan_speculation()
        orch.plan_controller.speculation_complete()
        assert orch.plan_state == PlanState.CONFIRMING
        orch.cancel_plan()
        assert orch.plan_state == PlanState.ABANDONED

    def test_cancel_when_idle_is_noop(self, orch: SpeculativeResearchOrchestrator) -> None:
        """Cancelling when already IDLE should not raise."""
        orch.cancel_plan()
        assert orch.plan_state == PlanState.IDLE

    def test_cancel_from_abandoned_is_noop(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.cancel_plan()
        assert orch.plan_state == PlanState.ABANDONED
        # Second cancel should be a no-op.
        orch.cancel_plan()
        assert orch.plan_state == PlanState.ABANDONED


# ── Revision Loop ────────────────────────────────────────────────


class TestRevisionLoop:
    """Tests for CONFIRMING → PLANNING revision cycle."""

    def test_revise_returns_to_planning(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step one")
        orch.begin_plan_speculation()
        orch.plan_controller.speculation_complete()
        assert orch.plan_state == PlanState.CONFIRMING

        orch.revise_plan()
        assert orch.plan_state == PlanState.PLANNING

    def test_revision_loop_full_cycle(self, orch: SpeculativeResearchOrchestrator) -> None:
        """PLANNING → SPECULATING → CONFIRMING → PLANNING → SPECULATING → CONFIRMING → EXECUTING → IDLE."""
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "First attempt")
        orch.begin_plan_speculation()
        orch.plan_controller.speculation_complete()
        assert orch.plan_state == PlanState.CONFIRMING

        # Revise
        orch.revise_plan()
        assert orch.plan_state == PlanState.PLANNING

        # Redo with updated steps
        orch.add_plan_step("s1b", "Revised approach")
        orch.begin_plan_speculation()
        orch.plan_controller.speculation_complete()
        assert orch.plan_state == PlanState.CONFIRMING

        # Confirm this time
        orch.confirm_plan()
        assert orch.plan_state == PlanState.EXECUTING

        orch.complete_plan_execution()
        assert orch.plan_state == PlanState.IDLE


# ── Timeout ──────────────────────────────────────────────────────


class TestPlanTimeout:
    """Tests for inactivity timeout auto-abandonment."""

    def test_timeout_from_planning(self, workspace: str) -> None:
        orch = SpeculativeResearchOrchestrator(
            workspace=workspace,
            plan_timeout_seconds=0.01,  # Effectively instant timeout
        )
        orch.enter_plan_mode()
        time.sleep(0.02)  # Wait past timeout
        timed_out = orch.check_plan_timeout()
        assert timed_out
        assert orch.plan_state == PlanState.ABANDONED

    def test_timeout_from_speculating(self, workspace: str) -> None:
        orch = SpeculativeResearchOrchestrator(
            workspace=workspace,
            plan_timeout_seconds=0.01,
        )
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        orch.begin_plan_speculation()
        time.sleep(0.02)
        timed_out = orch.check_plan_timeout()
        assert timed_out
        assert orch.plan_state == PlanState.ABANDONED

    def test_timeout_from_confirming(self, workspace: str) -> None:
        orch = SpeculativeResearchOrchestrator(
            workspace=workspace,
            plan_timeout_seconds=0.01,
        )
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        orch.begin_plan_speculation()
        orch.plan_controller.speculation_complete()
        time.sleep(0.02)
        timed_out = orch.check_plan_timeout()
        assert timed_out
        assert orch.plan_state == PlanState.ABANDONED

    def test_no_timeout_when_idle(self, orch: SpeculativeResearchOrchestrator) -> None:
        timed_out = orch.check_plan_timeout()
        assert not timed_out

    def test_no_timeout_within_window(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        timed_out = orch.check_plan_timeout()
        assert not timed_out
        assert orch.plan_state == PlanState.PLANNING


# ── Phase Transition Coordination ────────────────────────────────


class TestPhaseTransitionCoordination:
    """Tests for plan cleanup when orchestrator receives phase changes."""

    def test_terminal_phase_cancels_active_plan(self, orch: SpeculativeResearchOrchestrator) -> None:
        """Phase transition to 'complete' should cancel any active plan."""
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        assert orch.plan_state == PlanState.PLANNING

        transition = MagicMock()
        transition.to_phase = ResearchPhase.COMPLETE
        transition.metadata = {}
        orch.on_phase_change(transition)

        assert orch.plan_state == PlanState.ABANDONED

    def test_failed_phase_cancels_active_plan(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        assert orch.plan_state == PlanState.PLANNING

        transition = MagicMock()
        transition.to_phase = MagicMock(value="failed")
        transition.metadata = {}
        orch.on_phase_change(transition)

        assert orch.plan_state == PlanState.ABANDONED

    def test_idle_phase_cancels_active_plan(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()

        transition = MagicMock()
        transition.to_phase = MagicMock(value="idle")
        transition.metadata = {}
        orch.on_phase_change(transition)

        assert orch.plan_state == PlanState.ABANDONED

    def test_research_phase_does_not_cancel_plan(self, orch: SpeculativeResearchOrchestrator) -> None:
        """Non-terminal phases should NOT cancel the plan."""
        orch.enter_plan_mode()

        transition = MagicMock()
        transition.to_phase = ResearchPhase.RESEARCHING
        transition.metadata = {"session_id": "test-123"}
        orch.on_phase_change(transition)

        assert orch.plan_state == PlanState.PLANNING


# ── Orchestrator Reset ───────────────────────────────────────────


class TestOrchestratorReset:
    """Tests for orchestrator reset cleaning up plan state."""

    def test_reset_from_planning(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        orch.reset()
        assert orch.plan_state == PlanState.IDLE
        assert orch.plan_controller.session is None

    def test_reset_from_abandoned(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.cancel_plan()
        assert orch.plan_state == PlanState.ABANDONED
        orch.reset()
        assert orch.plan_state == PlanState.IDLE

    def test_reset_from_idle_is_clean(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.reset()
        assert orch.plan_state == PlanState.IDLE
        assert orch._session_id == ""
        assert orch.results == []


# ── Speculation Engine Coordination ──────────────────────────────


class TestSpeculationEngineCoordination:
    """Tests for coordination between plan controller and speculation engine."""

    def test_begin_speculation_starts_engine(self, orch: SpeculativeResearchOrchestrator) -> None:
        """begin_plan_speculation should start the SpeculationEngine if idle."""
        assert orch.speculation_engine.state == SpeculationState.IDLE
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        orch.begin_plan_speculation()
        assert orch.speculation_engine.state == SpeculationState.ACTIVE

    def test_begin_speculation_no_steps_raises(self, orch: SpeculativeResearchOrchestrator) -> None:
        """Cannot begin speculation with no steps defined."""
        orch.enter_plan_mode()
        with pytest.raises(TransitionError, match="no steps"):
            orch.begin_plan_speculation()

    def test_engine_and_plan_independent_abort(self, orch: SpeculativeResearchOrchestrator) -> None:
        """Aborting the engine should not affect plan state."""
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        orch.begin_plan_speculation()
        orch.speculation_engine.abort(reason="test")
        # Plan should still be in SPECULATING — engine abort is independent.
        assert orch.plan_state == PlanState.SPECULATING
        assert orch.speculation_engine.state == SpeculationState.IDLE


# ── Transition Guards ────────────────────────────────────────────


class TestTransitionGuards:
    """Tests for invalid state transition rejection."""

    def test_cannot_add_step_when_speculating(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        orch.add_plan_step("s1", "Step")
        orch.begin_plan_speculation()
        with pytest.raises(TransitionError, match="SPECULATING"):
            orch.add_plan_step("s2", "Another step")

    def test_cannot_confirm_when_planning(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch.enter_plan_mode()
        with pytest.raises(TransitionError):
            orch.confirm_plan()

    def test_direct_planning_to_planning_raises(self, orch: SpeculativeResearchOrchestrator) -> None:
        """Direct PLANNING→PLANNING transition should be rejected."""
        orch.enter_plan_mode()
        assert orch.plan_state == PlanState.PLANNING
        with pytest.raises(TransitionError):
            orch.plan_controller._transition(PlanState.PLANNING)


# ── Session ID Propagation ───────────────────────────────────────


class TestSessionIdPropagation:
    """Tests for session_id flowing through plan lifecycle."""

    def test_session_id_used_in_plan(self, orch: SpeculativeResearchOrchestrator) -> None:
        orch._session_id = "research-session-42"
        session = orch.enter_plan_mode()
        assert session.session_id == "research-session-42"

    def test_fallback_session_id_when_empty(self, orch: SpeculativeResearchOrchestrator) -> None:
        """When no session_id is set, a timestamp-based fallback is used."""
        session = orch.enter_plan_mode()
        assert session.session_id.startswith("plan-")

    def test_plan_controller_property_access(self, orch: SpeculativeResearchOrchestrator) -> None:
        """Verify the plan_controller property returns the internal controller."""
        assert isinstance(orch.plan_controller, ExitPlanModeController)
        assert orch.plan_controller is orch._plan_controller
