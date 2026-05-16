# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ShadowTag OS Test Suite — Comprehensive orchestrator, adapter, and gate tests.

Covers:
- CoreOrchestrator dispatch routing (all 6 OperationTypes)
- GateAdapter pre-flight security enforcement
- KernelChainAdapter sequential execution and SLA checks
- JudgeAdapter HITL enforcement contract
- SkillsBridge discovery and invocation
- ZxRunner command execution
- Integration: full orchestrator with all subsystems wired
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from packages.shadowtag_os.core.orchestrator import (
    CoreOrchestrator,
    OperationContext,
    OperationType,
)
from packages.shadowtag_os.gates.gate_adapter import GateAdapter
from packages.shadowtag_os.kernels.chain import KernelChainAdapter

# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────


@pytest.fixture
def mock_kernel():
    """A mock async kernel with an execute method."""
    kernel = AsyncMock()
    kernel.execute = AsyncMock(return_value={"transformed": True})
    return kernel


@pytest.fixture
def kernel_chain(mock_kernel):
    """A KernelChainAdapter with one mock step."""
    adapter = KernelChainAdapter()
    adapter.add_step("mock_kernel", mock_kernel)
    return adapter


@pytest.fixture
def gate_adapter():
    """A GateAdapter with default settings."""
    return GateAdapter()


@pytest.fixture
def gate_adapter_fail_open():
    """A GateAdapter with fail-open enabled."""
    return GateAdapter(fail_open=True)


@pytest.fixture
def mock_skills_bridge():
    """A mock SkillsBridge."""
    bridge = AsyncMock()
    bridge.invoke = AsyncMock(return_value={"skill": "test-skill", "status": "ready"})
    return bridge


@pytest.fixture
def mock_zx_runner():
    """A mock ZxRunner."""
    runner = AsyncMock()
    runner.run = AsyncMock(return_value={"stdout": "hello", "stderr": "", "exit_code": 0})
    return runner


@pytest.fixture
def mock_a2ui_adapter():
    """A mock A2UIAdapter."""
    adapter = AsyncMock()
    adapter.render = AsyncMock(return_value={"components": [{"type": "Card", "id": "c1"}]})
    return adapter


@pytest.fixture
def mock_judge_factory():
    """A mock JudgeFactory for HITL enforcement."""
    factory = AsyncMock()
    factory.review = AsyncMock(
        return_value={
            "decision": "ALLOW",
            "risk_assessment": {"risk_level": "low"},
            "reasoning": "Low risk operation",
        }
    )
    return factory


@pytest.fixture
def full_orchestrator(
    kernel_chain,
    gate_adapter,
    mock_skills_bridge,
    mock_zx_runner,
    mock_a2ui_adapter,
    mock_judge_factory,
):
    """A fully wired CoreOrchestrator with all subsystems."""
    return CoreOrchestrator(
        kernel_chain=kernel_chain,
        gate_checker=gate_adapter,
        skills_bridge=mock_skills_bridge,
        zx_runner=mock_zx_runner,
        a2ui_adapter=mock_a2ui_adapter,
        judge_factory=mock_judge_factory,
    )


def _make_ctx(
    op_type: OperationType = OperationType.QUERY,
    payload: dict[str, Any] | None = None,
    operation_id: str = "test-op-001",
) -> OperationContext:
    """Helper to create OperationContext."""
    return OperationContext(
        operation_id=operation_id,
        op_type=op_type,
        payload=payload or {"data": "test"},
    )


# ─────────────────────────────────────────────────────────────
# 1. CoreOrchestrator — Dispatch Routing
# ─────────────────────────────────────────────────────────────


class TestCoreOrchestratorRouting:
    """Test that operations route to the correct subsystem."""

    @pytest.mark.asyncio
    async def test_query_routes_to_kernel_chain(self, full_orchestrator, kernel_chain):
        """QUERY and MUTATION operations route to kernel chain."""
        ctx = _make_ctx(OperationType.QUERY, {"data": "input"})
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        assert result.operation_id == "test-op-001"
        assert result.latency_ms > 0

    @pytest.mark.asyncio
    async def test_mutation_routes_to_kernel_chain(self, full_orchestrator):
        """MUTATION operations also route to kernel chain."""
        ctx = _make_ctx(OperationType.MUTATION, {"data": "mutation"})
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_shell_exec_routes_to_zx(self, full_orchestrator, mock_zx_runner):
        """SHELL_EXEC routes to ZxRunner."""
        ctx = _make_ctx(OperationType.SHELL_EXEC, {"command": "echo hello"})
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        mock_zx_runner.run.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ui_render_routes_to_a2ui(self, full_orchestrator, mock_a2ui_adapter):
        """UI_RENDER routes to A2UIAdapter."""
        ctx = _make_ctx(OperationType.UI_RENDER, {"component": "Card"})
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        mock_a2ui_adapter.render.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skill_invoke_routes_to_bridge(self, full_orchestrator, mock_skills_bridge):
        """SKILL_INVOKE routes to SkillsBridge."""
        ctx = _make_ctx(OperationType.SKILL_INVOKE, {"skill_name": "test-skill"})
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        mock_skills_bridge.invoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_judge_review_routes_to_factory(self, full_orchestrator, mock_judge_factory):
        """JUDGE_REVIEW routes to JudgeFactory."""
        ctx = _make_ctx(
            OperationType.JUDGE_REVIEW,
            {"judge_type": "FinJudge", "action_type": "wire_transfer"},
        )
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        mock_judge_factory.review.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_operation_count_increments(self, full_orchestrator):
        """Operation counter increments on each dispatch."""
        assert full_orchestrator.operation_count == 0

        ctx = _make_ctx(OperationType.QUERY)
        await full_orchestrator.dispatch(ctx)
        assert full_orchestrator.operation_count == 1

        await full_orchestrator.dispatch(ctx)
        assert full_orchestrator.operation_count == 2


# ─────────────────────────────────────────────────────────────
# 2. CoreOrchestrator — Missing Subsystems
# ─────────────────────────────────────────────────────────────


class TestMissingSubsystems:
    """Test error handling when subsystems are not configured."""

    @pytest.mark.asyncio
    async def test_shell_exec_without_zx_errors(self):
        """SHELL_EXEC without ZxRunner returns failure."""
        orchestrator = CoreOrchestrator()
        ctx = _make_ctx(OperationType.SHELL_EXEC, {"command": "ls"})
        result = await orchestrator.dispatch(ctx)

        assert result.success is False
        assert "ZxRunner not configured" in result.error

    @pytest.mark.asyncio
    async def test_ui_render_without_a2ui_errors(self):
        """UI_RENDER without A2UIAdapter returns failure."""
        orchestrator = CoreOrchestrator()
        ctx = _make_ctx(OperationType.UI_RENDER, {"component": "Card"})
        result = await orchestrator.dispatch(ctx)

        assert result.success is False
        assert "A2UIAdapter not configured" in result.error

    @pytest.mark.asyncio
    async def test_skill_invoke_without_bridge_errors(self):
        """SKILL_INVOKE without SkillsBridge returns failure."""
        orchestrator = CoreOrchestrator()
        ctx = _make_ctx(OperationType.SKILL_INVOKE, {"skill_name": "x"})
        result = await orchestrator.dispatch(ctx)

        assert result.success is False
        assert "SkillsBridge not configured" in result.error

    @pytest.mark.asyncio
    async def test_query_without_kernel_returns_fallback(self):
        """QUERY without kernel chain returns a no_kernel_chain fallback."""
        orchestrator = CoreOrchestrator()
        ctx = _make_ctx(OperationType.QUERY, {"data": "test"})
        result = await orchestrator.dispatch(ctx)

        # Should succeed with fallback response.
        assert result.success is True
        assert result.data["status"] == "no_kernel_chain"


# ─────────────────────────────────────────────────────────────
# 3. GateAdapter — Pre-flight Enforcement
# ─────────────────────────────────────────────────────────────


class TestGateAdapter:
    """Test the gate adapter pre-flight check system."""

    @pytest.mark.asyncio
    async def test_valid_context_passes(self, gate_adapter):
        """A valid operation context passes all gates."""
        ctx = _make_ctx(OperationType.QUERY, {"data": "safe"})
        result = await gate_adapter.check(ctx)

        assert result.passed is True
        assert result.severity == "ok"

    @pytest.mark.asyncio
    async def test_missing_payload_blocks(self, gate_adapter):
        """Operations with None payload are blocked."""
        ctx = OperationContext(
            operation_id="test",
            op_type=OperationType.QUERY,
            payload=None,
        )
        result = await gate_adapter.check(ctx)

        assert result.passed is False
        assert result.severity == "critical"

    @pytest.mark.asyncio
    async def test_dangerous_keyword_blocks(self, gate_adapter):
        """Dangerous shell keywords in payload are blocked."""
        ctx = _make_ctx(
            OperationType.SHELL_EXEC,
            {"command": "rm -rf /"},
        )
        result = await gate_adapter.check(ctx)

        assert result.passed is False
        assert "Dangerous keyword" in result.reason

    @pytest.mark.asyncio
    async def test_sql_injection_blocks(self, gate_adapter):
        """SQL injection keywords are caught by security gate."""
        ctx = _make_ctx(
            OperationType.QUERY,
            {"query": "DROP TABLE users"},
        )
        result = await gate_adapter.check(ctx)

        assert result.passed is False
        assert "drop table" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_fail_open_mode(self, gate_adapter_fail_open):
        """Fail-open mode passes even on gate errors."""

        # Create a gate with a broken custom gate.
        def broken_gate(ctx):
            raise RuntimeError("Boom")

        adapter = GateAdapter(fail_open=True, custom_gates=[broken_gate])
        ctx = _make_ctx(OperationType.QUERY, {"data": "test"})
        result = await adapter.check(ctx)

        # Should pass because fail_open=True.
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_custom_gate_integration(self):
        """Custom gate functions are executed."""

        def require_auth(ctx):
            payload = ctx.payload or {}
            if "auth_token" not in payload:
                return {
                    "gate": "auth",
                    "passed": False,
                    "severity": "critical",
                    "message": "Missing auth_token",
                }
            return {
                "gate": "auth",
                "passed": True,
                "severity": "ok",
                "message": "Authenticated",
            }

        adapter = GateAdapter(custom_gates=[require_auth])

        # Without token.
        ctx = _make_ctx(OperationType.QUERY, {"data": "test"})
        result = await adapter.check(ctx)
        assert result.passed is False
        assert "auth_token" in result.reason

        # With token.
        ctx = _make_ctx(OperationType.QUERY, {"data": "test", "auth_token": "abc"})
        result = await adapter.check(ctx)
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_check_count_increments(self, gate_adapter):
        """Check counter increments on each call."""
        assert gate_adapter.check_count == 0

        ctx = _make_ctx()
        await gate_adapter.check(ctx)
        assert gate_adapter.check_count == 1

        await gate_adapter.check(ctx)
        assert gate_adapter.check_count == 2


# ─────────────────────────────────────────────────────────────
# 4. KernelChainAdapter — Sequential Execution
# ─────────────────────────────────────────────────────────────


class TestKernelChainAdapter:
    """Test the kernel chain adapter."""

    @pytest.mark.asyncio
    async def test_single_step_execution(self, kernel_chain, mock_kernel):
        """A single-step chain executes and returns results."""
        result = await kernel_chain.execute({"data": "input"})

        assert result["success"] is True
        assert len(result["outputs"]) == 1
        assert result["outputs"][0]["kernel"] == "mock_kernel"
        assert result["total_latency_ms"] > 0
        assert result["audit_hash"]

    @pytest.mark.asyncio
    async def test_multi_step_chain(self):
        """Multi-step chain pipes output between steps."""
        step_a = AsyncMock()
        step_a.execute = AsyncMock(return_value={"stage": "A_done"})
        step_b = AsyncMock()
        step_b.execute = AsyncMock(return_value={"stage": "B_done"})

        adapter = KernelChainAdapter()
        adapter.add_step("step_a", step_a)
        adapter.add_step("step_b", step_b)

        result = await adapter.execute({"data": "start"})

        assert result["success"] is True
        assert len(result["outputs"]) == 2
        assert result["outputs"][0]["kernel"] == "step_a"
        assert result["outputs"][1]["kernel"] == "step_b"

        # Verify piping: step_b should receive step_a's output.
        step_b.execute.assert_awaited_once_with({"stage": "A_done"})

    @pytest.mark.asyncio
    async def test_step_failure_halts_chain(self):
        """A failing step halts the chain and returns partial results."""
        good = AsyncMock()
        good.execute = AsyncMock(return_value={"ok": True})
        bad = AsyncMock()
        bad.execute = AsyncMock(side_effect=ValueError("Kernel exploded"))

        adapter = KernelChainAdapter()
        adapter.add_step("good", good)
        adapter.add_step("bad", bad)

        result = await adapter.execute({"data": "test"})

        assert result["success"] is False
        assert "bad: Kernel exploded" in result["error"]
        assert len(result["outputs"]) == 1  # Only the good step.

    @pytest.mark.asyncio
    async def test_execution_count_tracks(self, kernel_chain):
        """Execution counter increments correctly."""
        assert kernel_chain.execution_count == 0
        await kernel_chain.execute({"data": "1"})
        await kernel_chain.execute({"data": "2"})
        assert kernel_chain.execution_count == 2

    @pytest.mark.asyncio
    async def test_sync_kernel_support(self):
        """Synchronous kernels are wrapped in executor."""

        class SyncKernel:
            def execute(self, data):
                return {"sync": True, "input": data}

        adapter = KernelChainAdapter()
        adapter.add_step("sync_kernel", SyncKernel())
        result = await adapter.execute({"data": "test"})

        assert result["success"] is True
        assert result["outputs"][0]["data"]["sync"] is True

    def test_step_count(self):
        """Step count reflects added steps."""
        adapter = KernelChainAdapter()
        assert adapter.step_count == 0
        adapter.add_step("a", MagicMock())
        adapter.add_step("b", MagicMock())
        assert adapter.step_count == 2


# ─────────────────────────────────────────────────────────────
# 5. Integration — Full Pipeline
# ─────────────────────────────────────────────────────────────


class TestIntegration:
    """End-to-end integration tests with all subsystems wired."""

    @pytest.mark.asyncio
    async def test_gate_blocks_dangerous_operation(self, full_orchestrator):
        """Gate adapter blocks dangerous payloads before routing."""
        ctx = _make_ctx(
            OperationType.SHELL_EXEC,
            {"command": "sudo rm -rf /"},
        )
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is False
        assert "Gate check failed" in result.error

    @pytest.mark.asyncio
    async def test_full_query_pipeline(self, full_orchestrator):
        """Full QUERY → gate → kernel chain pipeline."""
        ctx = _make_ctx(OperationType.QUERY, {"data": "legal brief"})
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        assert result.latency_ms > 0

    @pytest.mark.asyncio
    async def test_full_skill_pipeline(self, full_orchestrator, mock_skills_bridge):
        """Full SKILL_INVOKE → gate → skills bridge pipeline."""
        ctx = _make_ctx(
            OperationType.SKILL_INVOKE,
            {"skill_name": "deep-research"},
        )
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        assert result.data["status"] == "ready"

    @pytest.mark.asyncio
    async def test_full_judge_pipeline(self, full_orchestrator, mock_judge_factory):
        """Full JUDGE_REVIEW → gate → judge factory pipeline."""
        ctx = _make_ctx(
            OperationType.JUDGE_REVIEW,
            {
                "judge_type": "FinJudge",
                "action_type": "wire_transfer",
                "context": {"amount_usd": 75000},
                "requested_by": "cfo@company.com",
            },
        )
        result = await full_orchestrator.dispatch(ctx)

        assert result.success is True
        assert result.data["decision"] == "ALLOW"
