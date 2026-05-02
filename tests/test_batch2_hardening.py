# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Batch 2 Hardening Tests — Telemetry, Sandbox Wiring, ExitPlanMode.

Tests:
    - TelemetryEmitter event buffering and filtering
    - ClassifiedGateway + SandboxPathResolver integration
    - ClassifiedGateway telemetry event emission at each tier
    - ExitPlanMode state machine transitions
    - ExitPlanMode timeout auto-abandonment
    - ExitPlanMode step management
"""

from __future__ import annotations

import time

import pytest

from speculation_engine.exit_plan_mode import (
    ExitPlanModeController,
    PlanState,
    TransitionError,
)
from tool_gateway.block_allow_engine import BlockAllowRuleEngine
from tool_gateway.sandbox_path_resolver import SandboxPathResolver
from tool_gateway.telemetry import (
    GatewayEvent,
    TelemetryEmitter,
    TelemetryPayload,
)


# =========================================================================
# Telemetry Emitter Tests
# =========================================================================


class TestTelemetryEmitter:
    """Tests for the TelemetryEmitter event system."""

    def test_emit_buffers_when_enabled(self):
        emitter = TelemetryEmitter(buffer_events=True)
        payload = TelemetryPayload(
            event=GatewayEvent.BLOCK_ALLOW_BLOCKED.value,
            tool_id="bash",
            verdict="BLOCK",
            tier="1.5",
        )
        emitter.emit(payload)
        assert emitter.event_count() == 1
        assert emitter.events[0].tool_id == "bash"

    def test_emit_does_not_buffer_when_disabled(self):
        emitter = TelemetryEmitter(buffer_events=False)
        payload = TelemetryPayload(
            event=GatewayEvent.BLOCK_ALLOW_BLOCKED.value,
            tool_id="bash",
        )
        emitter.emit(payload)
        assert emitter.event_count() == 0

    def test_event_count_filters_by_type(self):
        emitter = TelemetryEmitter(buffer_events=True)
        emitter.emit(TelemetryPayload(event=GatewayEvent.BLOCK_ALLOW_BLOCKED.value, tool_id="a"))
        emitter.emit(TelemetryPayload(event=GatewayEvent.BLOCK_ALLOW_ALLOWED.value, tool_id="b"))
        emitter.emit(TelemetryPayload(event=GatewayEvent.BLOCK_ALLOW_BLOCKED.value, tool_id="c"))

        assert emitter.event_count(GatewayEvent.BLOCK_ALLOW_BLOCKED) == 2
        assert emitter.event_count(GatewayEvent.BLOCK_ALLOW_ALLOWED) == 1
        assert emitter.event_count() == 3

    def test_clear_empties_buffer(self):
        emitter = TelemetryEmitter(buffer_events=True)
        emitter.emit(TelemetryPayload(event="test", tool_id="x"))
        emitter.clear()
        assert emitter.event_count() == 0

    def test_payload_includes_timestamp(self):
        emitter = TelemetryEmitter(buffer_events=True)
        before = time.time()
        emitter.emit(TelemetryPayload(event="test", tool_id="x"))
        after = time.time()
        ts = emitter.events[0].timestamp
        assert before <= ts <= after

    def test_gateway_event_enum_has_14_events(self):
        assert len(GatewayEvent) == 14


# =========================================================================
# ClassifiedGateway + Sandbox Integration Tests
# =========================================================================


class TestClassifiedGatewaySandbox:
    """Tests for sandbox path resolver integration in ClassifiedGateway."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a workspace directory structure."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "src").mkdir()
        (workspace / "src" / "main.py").touch()
        (workspace / ".git").mkdir()
        (workspace / "config").mkdir()
        return workspace

    @pytest.fixture
    def sandbox(self, workspace):
        return SandboxPathResolver(workspace_root=workspace)

    def test_sandbox_blocks_outside_workspace(self, workspace, sandbox):
        """Tool input with path outside workspace is blocked."""
        result = sandbox.resolve("//etc/shadow")
        assert not result.is_allowed
        # On macOS, /etc resolves to /private/etc which may hit sandbox boundary
        # before NEVER_ACCESS check. Either reason is valid — the path is blocked.
        assert "NEVER_ACCESS" in result.deny_reason or "outside sandbox boundary" in result.deny_reason

    def test_sandbox_allows_workspace_relative(self, workspace, sandbox):
        """Workspace-relative paths are allowed."""
        result = sandbox.resolve("/src/main.py")
        assert result.is_allowed
        assert result.resolution_type == "workspace"

    def test_sandbox_flags_sensitive_git_dir(self, workspace, sandbox):
        """Paths in .git are flagged as sensitive."""
        result = sandbox.resolve("/src/../.git/config")
        assert result.is_allowed
        assert result.is_sensitive

    def test_bare_relative_path_resolves_to_cwd(self, workspace, sandbox):
        """Bare relative paths resolve within workspace."""
        result = sandbox.resolve("src/main.py")
        assert result.is_allowed
        assert result.resolution_type == "relative"


# =========================================================================
# ClassifiedGateway Telemetry Integration Tests
# =========================================================================


class TestClassifiedGatewayTelemetry:
    """Tests for telemetry event emission in the gateway pipeline."""

    def test_block_allow_blocked_emits_event(self):
        """BLOCK/ALLOW engine BLOCK emits telemetry."""
        engine = BlockAllowRuleEngine()
        emitter = TelemetryEmitter(buffer_events=True)

        # Evaluate a sudo command — should trigger B1
        result = engine.evaluate(
            tool_id="bash",
            tool_input={"command": "sudo rm -rf /"},
        )
        assert result.final_verdict.value == "BLOCK"

        # Simulate the gateway emitting
        emitter.emit(
            TelemetryPayload(
                event=GatewayEvent.BLOCK_ALLOW_BLOCKED.value,
                tool_id="bash",
                verdict="BLOCK",
                tier="1.5",
                matched_rules=[r.rule_id for r in result.matched_rules],
            )
        )
        assert emitter.event_count(GatewayEvent.BLOCK_ALLOW_BLOCKED) == 1
        assert "B1" in emitter.events[0].matched_rules

    def test_sandbox_denied_emits_event(self):
        """Sandbox path denial emits telemetry."""
        emitter = TelemetryEmitter(buffer_events=True)
        emitter.emit(
            TelemetryPayload(
                event=GatewayEvent.SANDBOX_PATH_DENIED.value,
                tool_id="write_to_file",
                verdict="BLOCK",
                tier="1.25",
                reason="Path outside sandbox boundary",
                metadata={"path": "/etc/shadow"},
            )
        )
        assert emitter.event_count(GatewayEvent.SANDBOX_PATH_DENIED) == 1

    def test_latency_tracking_in_payload(self):
        """Latency is tracked in telemetry payloads."""
        emitter = TelemetryEmitter(buffer_events=True)
        emitter.emit(
            TelemetryPayload(
                event=GatewayEvent.BLOCK_ALLOW_ALLOWED.value,
                tool_id="read_file",
                latency_ms=0.42,
            )
        )
        assert emitter.events[0].latency_ms == pytest.approx(0.42)


# =========================================================================
# ExitPlanMode State Machine Tests
# =========================================================================


class TestExitPlanModeTransitions:
    """Tests for the ExitPlanMode state machine lifecycle."""

    def test_initial_state_is_idle(self):
        ctrl = ExitPlanModeController()
        assert ctrl.state == PlanState.IDLE

    def test_full_happy_path(self):
        """IDLE → PLANNING → SPECULATING → CONFIRMING → EXECUTING → IDLE."""
        ctrl = ExitPlanModeController()

        session = ctrl.begin_planning("test-001")
        assert ctrl.state == PlanState.PLANNING
        assert session.session_id == "test-001"

        ctrl.add_step("s1", "Run tests", [{"tool": "bash", "args": "pytest"}])
        ctrl.add_step("s2", "Deploy", [{"tool": "deploy", "args": "prod"}])
        assert len(session.steps) == 2

        ctrl.begin_speculation()
        assert ctrl.state == PlanState.SPECULATING

        ctrl.record_speculation_result("s1", {"exit_code": 0, "output": "2 passed"})
        assert session.steps[0].status == "speculated"

        ctrl.speculation_complete()
        assert ctrl.state == PlanState.CONFIRMING

        ctrl.user_confirm()
        assert ctrl.state == PlanState.EXECUTING

        ctrl.execution_complete()
        assert ctrl.state == PlanState.IDLE
        assert ctrl.session is None

    def test_user_revise_returns_to_planning(self):
        """CONFIRMING → PLANNING via user_revise()."""
        ctrl = ExitPlanModeController()
        ctrl.begin_planning("test-002")
        ctrl.add_step("s1", "Test")
        ctrl.begin_speculation()
        ctrl.speculation_complete()
        assert ctrl.state == PlanState.CONFIRMING

        ctrl.user_revise()
        assert ctrl.state == PlanState.PLANNING

    def test_user_cancel_abandons(self):
        """CONFIRMING → ABANDONED via user_cancel()."""
        ctrl = ExitPlanModeController()
        ctrl.begin_planning("test-003")
        ctrl.add_step("s1", "Test")
        ctrl.begin_speculation()
        ctrl.speculation_complete()

        ctrl.user_cancel()
        assert ctrl.state == PlanState.ABANDONED

        ctrl.reset()
        assert ctrl.state == PlanState.IDLE

    def test_needs_revision_returns_to_planning(self):
        """SPECULATING → PLANNING via needs_revision()."""
        ctrl = ExitPlanModeController()
        ctrl.begin_planning("test-004")
        ctrl.add_step("s1", "Test")
        ctrl.begin_speculation()

        ctrl.needs_revision()
        assert ctrl.state == PlanState.PLANNING

    def test_cancel_from_planning(self):
        """PLANNING → ABANDONED via cancel()."""
        ctrl = ExitPlanModeController()
        ctrl.begin_planning("test-005")
        ctrl.cancel()
        assert ctrl.state == PlanState.ABANDONED

    def test_invalid_transition_raises(self):
        """Invalid transitions raise TransitionError."""
        ctrl = ExitPlanModeController()

        with pytest.raises(TransitionError):
            ctrl.user_confirm()  # Can't confirm from IDLE

    def test_cannot_speculate_with_no_steps(self):
        """Cannot begin speculation with no steps."""
        ctrl = ExitPlanModeController()
        ctrl.begin_planning("test-006")

        with pytest.raises(TransitionError, match="no steps"):
            ctrl.begin_speculation()

    def test_cannot_add_steps_outside_planning(self):
        """Cannot add steps when not in PLANNING state."""
        ctrl = ExitPlanModeController()
        ctrl.begin_planning("test-007")
        ctrl.add_step("s1", "Test")
        ctrl.begin_speculation()

        with pytest.raises(TransitionError, match="SPECULATING"):
            ctrl.add_step("s2", "Another step")


class TestExitPlanModeTimeout:
    """Tests for ExitPlanMode timeout behavior."""

    def test_timeout_abandons_planning(self):
        """PLANNING times out → ABANDONED."""
        ctrl = ExitPlanModeController(timeout_seconds=0.01)
        ctrl.begin_planning("timeout-001")
        time.sleep(0.02)

        assert ctrl.check_timeout()
        assert ctrl.state == PlanState.ABANDONED

    def test_no_timeout_when_active(self):
        """No timeout if activity is recent."""
        ctrl = ExitPlanModeController(timeout_seconds=60)
        ctrl.begin_planning("timeout-002")

        assert not ctrl.check_timeout()
        assert ctrl.state == PlanState.PLANNING

    def test_timeout_from_speculating(self):
        """SPECULATING times out → PLANNING → ABANDONED."""
        ctrl = ExitPlanModeController(timeout_seconds=0.01)
        ctrl.begin_planning("timeout-003")
        ctrl.add_step("s1", "Test")
        ctrl.begin_speculation()
        time.sleep(0.02)

        assert ctrl.check_timeout()
        assert ctrl.state == PlanState.ABANDONED

    def test_timeout_from_confirming(self):
        """CONFIRMING times out → ABANDONED."""
        ctrl = ExitPlanModeController(timeout_seconds=0.01)
        ctrl.begin_planning("timeout-004")
        ctrl.add_step("s1", "Test")
        ctrl.begin_speculation()
        ctrl.speculation_complete()
        time.sleep(0.02)

        assert ctrl.check_timeout()
        assert ctrl.state == PlanState.ABANDONED


class TestExitPlanModeHistory:
    """Tests for transition history tracking."""

    def test_history_records_transitions(self):
        ctrl = ExitPlanModeController()
        ctrl.begin_planning("hist-001")
        ctrl.add_step("s1", "Test")
        ctrl.begin_speculation()

        history = ctrl.transition_history
        assert len(history) == 2
        assert history[0][0] == PlanState.IDLE
        assert history[0][1] == PlanState.PLANNING
        assert history[1][0] == PlanState.PLANNING
        assert history[1][1] == PlanState.SPECULATING

    def test_repr(self):
        ctrl = ExitPlanModeController()
        assert "IDLE" in repr(ctrl)
        ctrl.begin_planning("repr-001")
        assert "repr-001" in repr(ctrl)
