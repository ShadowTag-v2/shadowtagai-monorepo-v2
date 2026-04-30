# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for deep_research.state_machine module.

Covers:
  - Phase transition validation (valid + invalid)
  - Circuit breaker tripping after consecutive failures
  - Abort signal propagation
  - Tool whitelisting per phase
  - Timeout enforcement
  - Full pipeline happy path
  - Phase handler retry logic
  - Session ID generation
  - Query recording limits
  - Artifact tracking
  - on_phase_change callback invocation
"""

from __future__ import annotations

import asyncio

import pytest

from deep_research.state_machine import (
    PHASE_ALLOWED_TOOLS,
    VALID_TRANSITIONS,
    DeepResearchEngine,
    PhaseTransition,
    ResearchConfig,
    ResearchPhase,
)


# ── Phase Enum ──────────────────────────────────────────────────


class TestResearchPhase:
    def test_all_phases_present(self) -> None:
        expected = {"idle", "planning", "researching", "synthesizing", "executing", "verifying", "complete", "failed"}
        assert {p.value for p in ResearchPhase} == expected

    def test_string_enum(self) -> None:
        assert ResearchPhase.IDLE == "idle"
        assert ResearchPhase.FAILED == "failed"


# ── Valid Transitions ───────────────────────────────────────────


class TestValidTransitions:
    def test_idle_can_only_go_to_planning(self) -> None:
        assert VALID_TRANSITIONS[ResearchPhase.IDLE] == {ResearchPhase.PLANNING}

    def test_complete_returns_to_idle(self) -> None:
        assert VALID_TRANSITIONS[ResearchPhase.COMPLETE] == {ResearchPhase.IDLE}

    def test_failed_returns_to_idle(self) -> None:
        assert VALID_TRANSITIONS[ResearchPhase.FAILED] == {ResearchPhase.IDLE}

    def test_every_active_phase_can_fail(self) -> None:
        active_phases = [
            ResearchPhase.PLANNING,
            ResearchPhase.RESEARCHING,
            ResearchPhase.SYNTHESIZING,
            ResearchPhase.EXECUTING,
            ResearchPhase.VERIFYING,
        ]
        for phase in active_phases:
            assert ResearchPhase.FAILED in VALID_TRANSITIONS[phase], f"{phase} should be able to transition to FAILED"

    def test_linear_pipeline_path(self) -> None:
        """Verify the happy-path linear pipeline is valid."""
        path = [
            ResearchPhase.IDLE,
            ResearchPhase.PLANNING,
            ResearchPhase.RESEARCHING,
            ResearchPhase.SYNTHESIZING,
            ResearchPhase.EXECUTING,
            ResearchPhase.VERIFYING,
            ResearchPhase.COMPLETE,
        ]
        for i in range(len(path) - 1):
            assert path[i + 1] in VALID_TRANSITIONS[path[i]], f"Transition {path[i]} → {path[i + 1]} should be valid"


# ── Tool Whitelisting ──────────────────────────────────────────


class TestPhaseAllowedTools:
    def test_planning_tools(self) -> None:
        tools = PHASE_ALLOWED_TOOLS[ResearchPhase.PLANNING]
        assert "sequential_thinking" in tools
        assert "view_file" in tools
        assert "write_to_file" not in tools

    def test_researching_includes_search(self) -> None:
        tools = PHASE_ALLOWED_TOOLS[ResearchPhase.RESEARCHING]
        assert "search_documents" in tools
        assert "search_web" in tools
        assert "write_to_file" not in tools

    def test_executing_includes_write(self) -> None:
        tools = PHASE_ALLOWED_TOOLS[ResearchPhase.EXECUTING]
        assert "write_to_file" in tools
        assert "run_command" in tools
        assert "search_web" not in tools

    def test_verifying_includes_lighthouse(self) -> None:
        tools = PHASE_ALLOWED_TOOLS[ResearchPhase.VERIFYING]
        assert "lighthouse_audit" in tools
        assert "take_screenshot" in tools

    def test_idle_has_no_tools(self) -> None:
        assert ResearchPhase.IDLE not in PHASE_ALLOWED_TOOLS


# ── ResearchConfig ──────────────────────────────────────────────


class TestResearchConfig:
    def test_defaults(self) -> None:
        cfg = ResearchConfig()
        assert cfg.phase_timeout_s == 300.0
        assert cfg.total_timeout_s == 1800.0
        assert cfg.max_consecutive_failures == 3
        assert cfg.max_queries == 50
        assert cfg.max_retries == 2
        assert cfg.auto_advance is True
        assert cfg.emit_telemetry is True


# ── PhaseTransition ─────────────────────────────────────────────


class TestPhaseTransition:
    def test_creation(self) -> None:
        t = PhaseTransition(
            from_phase=ResearchPhase.IDLE,
            to_phase=ResearchPhase.PLANNING,
        )
        assert t.success is True
        assert t.error is None

    def test_with_error(self) -> None:
        t = PhaseTransition(
            from_phase=ResearchPhase.PLANNING,
            to_phase=ResearchPhase.FAILED,
            success=False,
            error="timeout",
        )
        assert t.success is False
        assert t.error == "timeout"


# ── DeepResearchEngine ──────────────────────────────────────────


class TestDeepResearchEngine:
    def test_initial_state(self) -> None:
        engine = DeepResearchEngine()
        assert engine.current_phase == ResearchPhase.IDLE
        assert engine.session_id == ""
        assert engine.is_active is False

    def test_is_tool_allowed_in_idle(self) -> None:
        engine = DeepResearchEngine()
        assert engine.is_tool_allowed("view_file") is False

    def test_abort_sets_event(self) -> None:
        engine = DeepResearchEngine()
        engine.abort()
        assert engine._abort_event.is_set()

    def test_record_query_increments(self) -> None:
        engine = DeepResearchEngine(config=ResearchConfig(max_queries=3))
        assert engine.record_query() is True
        assert engine.record_query() is True
        assert engine.record_query() is True
        assert engine.record_query() is False  # exceeded

    def test_add_artifact(self) -> None:
        engine = DeepResearchEngine()
        engine.add_artifact("/path/to/file.py")
        assert "/path/to/file.py" in engine._state.execution_artifacts

    def test_get_phase_summary(self) -> None:
        engine = DeepResearchEngine()
        summary = engine.get_phase_summary()
        assert summary["current_phase"] == "idle"
        assert summary["total_queries"] == 0
        assert summary["transitions"] == []


class TestDeepResearchEngineAsync:
    @pytest.mark.asyncio
    async def test_happy_path_pipeline(self) -> None:
        """Run the full pipeline with default (no-op) handlers."""
        engine = DeepResearchEngine(
            config=ResearchConfig(
                phase_timeout_s=5.0,
                total_timeout_s=30.0,
                emit_telemetry=False,
            )
        )
        result = await engine.run(objective="Test pipeline execution")
        assert result.success is True
        assert result.final_phase == ResearchPhase.COMPLETE
        assert result.session_id.startswith("dr-")
        assert len(result.phases_completed) >= 6  # 5 transitions + COMPLETE
        assert result.error is None

    @pytest.mark.asyncio
    async def test_custom_phase_handler(self) -> None:
        """Verify custom handlers receive correct arguments."""
        received_args: list[tuple] = []

        def planning_handler(objective, context, state):
            received_args.append((objective, context, state))
            return {"plan": "test-plan"}

        engine = DeepResearchEngine(config=ResearchConfig(emit_telemetry=False))
        result = await engine.run(
            objective="Custom handler test",
            context={"key": "value"},
            phase_handlers={ResearchPhase.PLANNING: planning_handler},
        )
        assert result.success is True
        assert len(received_args) == 1
        assert received_args[0][0] == "Custom handler test"
        assert received_args[0][1] == {"key": "value"}
        assert result.findings.get("planning") == {"plan": "test-plan"}

    @pytest.mark.asyncio
    async def test_abort_mid_pipeline(self) -> None:
        """Abort signal should stop the pipeline and transition to FAILED."""
        engine = DeepResearchEngine(config=ResearchConfig(emit_telemetry=False))

        async def slow_planning(objective, context, state):
            await asyncio.sleep(2.0)
            return {}

        # Abort after a brief delay.
        async def abort_after():
            await asyncio.sleep(0.05)
            engine.abort()

        asyncio.create_task(abort_after())
        result = await engine.run(
            objective="Abort test",
            phase_handlers={ResearchPhase.PLANNING: slow_planning},
        )
        assert result.final_phase == ResearchPhase.FAILED
        assert result.success is False

    @pytest.mark.asyncio
    async def test_phase_timeout_triggers_failure(self) -> None:
        """A handler exceeding phase timeout should trigger failure count."""
        engine = DeepResearchEngine(
            config=ResearchConfig(
                phase_timeout_s=0.1,
                max_consecutive_failures=1,
                max_retries=1,
                emit_telemetry=False,
            )
        )

        async def timeout_handler(objective, context, state):
            await asyncio.sleep(5.0)
            return {}

        result = await engine.run(
            objective="Timeout test",
            phase_handlers={ResearchPhase.PLANNING: timeout_handler},
        )
        assert result.final_phase == ResearchPhase.FAILED
        assert result.success is False

    @pytest.mark.asyncio
    async def test_circuit_breaker_trips(self) -> None:
        """Consecutive failures should trip the circuit breaker."""
        fail_count = 0

        def failing_handler(objective, context, state):
            nonlocal fail_count
            fail_count += 1
            raise RuntimeError(f"Fail #{fail_count}")

        engine = DeepResearchEngine(
            config=ResearchConfig(
                max_consecutive_failures=2,
                max_retries=1,
                emit_telemetry=False,
            )
        )
        result = await engine.run(
            objective="Circuit breaker test",
            phase_handlers={
                ResearchPhase.PLANNING: failing_handler,
                ResearchPhase.RESEARCHING: failing_handler,
            },
        )
        assert result.final_phase == ResearchPhase.FAILED
        assert result.success is False

    @pytest.mark.asyncio
    async def test_on_phase_change_callback(self) -> None:
        """The on_phase_change callback should fire on each transition."""
        transitions_received: list[PhaseTransition] = []

        def callback(t: PhaseTransition):
            transitions_received.append(t)

        engine = DeepResearchEngine(
            config=ResearchConfig(emit_telemetry=False),
            on_phase_change=callback,
        )
        result = await engine.run(objective="Callback test")
        assert result.success is True
        assert len(transitions_received) >= 6  # 5 phases + COMPLETE

    @pytest.mark.asyncio
    async def test_invalid_transition_raises(self) -> None:
        """Attempting an invalid transition should raise ValueError."""
        engine = DeepResearchEngine(config=ResearchConfig(emit_telemetry=False))
        with pytest.raises(ValueError, match="Invalid transition"):
            await engine._transition(ResearchPhase.COMPLETE)

    @pytest.mark.asyncio
    async def test_handler_retry_logic(self) -> None:
        """Handlers should be retried up to max_retries times."""
        attempt_count = 0

        def retry_handler(objective, context, state):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise RuntimeError("transient")
            return {"recovered": True}

        engine = DeepResearchEngine(
            config=ResearchConfig(
                max_retries=3,
                max_consecutive_failures=5,
                emit_telemetry=False,
            )
        )
        result = await engine.run(
            objective="Retry test",
            phase_handlers={ResearchPhase.PLANNING: retry_handler},
        )
        assert result.success is True
        assert attempt_count == 2
        assert result.findings.get("planning") == {"recovered": True}

    @pytest.mark.asyncio
    async def test_total_timeout_enforcement(self) -> None:
        """Total session timeout should halt the pipeline."""
        engine = DeepResearchEngine(
            config=ResearchConfig(
                total_timeout_s=0.001,  # Extremely short
                emit_telemetry=False,
            )
        )

        async def slow_handler(objective, context, state):
            await asyncio.sleep(0.1)
            return {}

        result = await engine.run(
            objective="Total timeout test",
            phase_handlers={ResearchPhase.PLANNING: slow_handler},
        )
        assert result.final_phase == ResearchPhase.FAILED
        assert result.success is False
