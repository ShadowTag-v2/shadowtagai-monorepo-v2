# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
CoreOrchestrator — Central dispatch for the ShadowTag OS.

Responsibilities:
1. Route incoming requests to the appropriate kernel chain
2. Integrate google/skills for dynamic capability discovery
3. Delegate shell automation to google/zx via ZxRunner
4. Render agent responses through google/A2UI adapter
5. Enforce Judge #6 HITL gates on all high-risk operations
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class OperationType(Enum):
    """Classification of incoming operations for routing."""

    QUERY = "query"
    MUTATION = "mutation"
    SHELL_EXEC = "shell_exec"
    UI_RENDER = "ui_render"
    SKILL_INVOKE = "skill_invoke"
    JUDGE_REVIEW = "judge_review"


@dataclass
class OperationContext:
    """Context for a single operation flowing through the orchestrator."""

    operation_id: str
    op_type: OperationType
    payload: dict[str, Any]
    trace_id: str | None = None
    user_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class OperationResult:
    """Result from an orchestrated operation."""

    operation_id: str
    success: bool
    data: Any = None
    error: str | None = None
    latency_ms: float = 0.0
    audit_hash: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CoreOrchestrator:
    """
    Central dispatch for the ShadowTag OS.

    Routes operations through the appropriate subsystems:
    - Kernel chain for data transformations
    - Judge factory for HITL enforcement
    - Skills bridge for dynamic capability discovery
    - ZxRunner for shell automation
    - A2UI adapter for declarative UI rendering
    """

    def __init__(
        self,
        *,
        skills_bridge: Any | None = None,
        zx_runner: Any | None = None,
        a2ui_adapter: Any | None = None,
        kernel_chain: Any | None = None,
        judge_factory: Any | None = None,
        gate_checker: Any | None = None,
    ):
        self._skills_bridge = skills_bridge
        self._zx_runner = zx_runner
        self._a2ui_adapter = a2ui_adapter
        self._kernel_chain = kernel_chain
        self._judge_factory = judge_factory
        self._gate_checker = gate_checker
        self._operation_count = 0

        logger.info(
            "core_orchestrator.init",
            skills_bridge=skills_bridge is not None,
            zx_runner=zx_runner is not None,
            a2ui_adapter=a2ui_adapter is not None,
            kernel_chain=kernel_chain is not None,
        )

    async def dispatch(self, ctx: OperationContext) -> OperationResult:
        """
        Dispatch an operation through the appropriate subsystem.

        Args:
            ctx: Operation context with type, payload, and metadata.

        Returns:
            OperationResult with data, timing, and audit hash.
        """
        start = time.perf_counter()
        self._operation_count += 1

        logger.info(
            "core_orchestrator.dispatch",
            operation_id=ctx.operation_id,
            op_type=ctx.op_type.value,
            count=self._operation_count,
        )

        try:
            # Pre-flight gate check
            if self._gate_checker:
                gate_result = await self._gate_checker.check(ctx)
                if not gate_result.passed:
                    return OperationResult(
                        operation_id=ctx.operation_id,
                        success=False,
                        error=f"Gate check failed: {gate_result.reason}",
                        latency_ms=(time.perf_counter() - start) * 1000,
                    )

            # Route to subsystem
            result_data = await self._route(ctx)

            latency_ms = (time.perf_counter() - start) * 1000
            return OperationResult(
                operation_id=ctx.operation_id,
                success=True,
                data=result_data,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "core_orchestrator.error",
                operation_id=ctx.operation_id,
                error=str(e),
                latency_ms=latency_ms,
            )
            return OperationResult(
                operation_id=ctx.operation_id,
                success=False,
                error=str(e),
                latency_ms=latency_ms,
            )

    async def _route(self, ctx: OperationContext) -> Any:
        """Route operation to the appropriate subsystem."""
        match ctx.op_type:
            case OperationType.QUERY | OperationType.MUTATION:
                if self._kernel_chain:
                    return await self._kernel_chain.execute(ctx.payload)
                return {"status": "no_kernel_chain", "payload": ctx.payload}

            case OperationType.SHELL_EXEC:
                if self._zx_runner:
                    return await self._zx_runner.run(ctx.payload)
                raise RuntimeError("ZxRunner not configured for shell_exec")

            case OperationType.UI_RENDER:
                if self._a2ui_adapter:
                    return await self._a2ui_adapter.render(ctx.payload)
                raise RuntimeError("A2UIAdapter not configured for ui_render")

            case OperationType.SKILL_INVOKE:
                if self._skills_bridge:
                    return await self._skills_bridge.invoke(ctx.payload)
                raise RuntimeError("SkillsBridge not configured for skill_invoke")

            case OperationType.JUDGE_REVIEW:
                if self._judge_factory:
                    return await self._judge_factory.review(ctx.payload)
                raise RuntimeError("JudgeFactory not configured for judge_review")

            case _:
                raise ValueError(f"Unknown operation type: {ctx.op_type}")

    @property
    def operation_count(self) -> int:
        """Total operations dispatched since init."""
        return self._operation_count
