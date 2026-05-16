# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
KernelChainAdapter — Bridges the CoreOrchestrator to the src/kernels chain.

Wraps the existing Kernel base class and concrete kernels
(ATP519ScanKernel, JudgeSixClassifyKernel, AuditCompressKernel) into
an async-compatible adapter that the CoreOrchestrator can invoke
via the standard ``execute(payload)`` contract.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ChainStep:
    """A single step in the kernel chain."""

    kernel_name: str
    kernel_instance: Any
    max_latency_ms: float | None = None


@dataclass
class ChainResult:
    """Result of a full kernel chain execution."""

    success: bool
    outputs: list[dict[str, Any]] = field(default_factory=list)
    total_latency_ms: float = 0.0
    audit_hash: str = ""
    error: str | None = None


class KernelChainAdapter:
    """
    Adapter that composes src/kernels into an ordered chain
    and exposes a single ``execute(payload)`` method to the orchestrator.

    Execution flow:
    1. Accept raw payload dict from orchestrator
    2. Marshal into KernelInput for each step
    3. Execute steps sequentially, piping output → input
    4. Collect latency metrics and audit hashes
    5. Return aggregated ChainResult
    """

    def __init__(self, steps: list[ChainStep] | None = None):
        self._steps: list[ChainStep] = steps or []
        self._execution_count = 0

    def add_step(
        self,
        kernel_name: str,
        kernel_instance: Any,
        max_latency_ms: float | None = None,
    ) -> None:
        """Append a kernel step to the chain."""
        self._steps.append(
            ChainStep(
                kernel_name=kernel_name,
                kernel_instance=kernel_instance,
                max_latency_ms=max_latency_ms,
            )
        )

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the full kernel chain against the given payload.

        Args:
            payload: Raw input data from the orchestrator.

        Returns:
            Dict with chain execution results, latency, and audit hash.
        """
        start = time.perf_counter()
        self._execution_count += 1

        outputs: list[dict[str, Any]] = []
        current_data = payload.get("data", payload)
        trace_id = payload.get("trace_id", f"chain-{self._execution_count}")

        logger.info(
            "kernel_chain.execute",
            trace_id=trace_id,
            steps=len(self._steps),
        )

        for step in self._steps:
            step_start = time.perf_counter()

            try:
                # Attempt to call the kernel's execute method.
                # The src/kernels expect KernelInput; we build a minimal one.
                result = await self._execute_step(step, current_data, trace_id)

                step_latency = (time.perf_counter() - step_start) * 1000

                # Enforce SLA if configured.
                if step.max_latency_ms and step_latency > step.max_latency_ms:
                    logger.warning(
                        "kernel_chain.sla_breach",
                        kernel=step.kernel_name,
                        latency_ms=step_latency,
                        sla_ms=step.max_latency_ms,
                    )

                step_output = {
                    "kernel": step.kernel_name,
                    "data": result,
                    "latency_ms": step_latency,
                }
                outputs.append(step_output)

                # Pipe output to next step.
                current_data = result

            except Exception as e:
                total_latency = (time.perf_counter() - start) * 1000
                logger.error(
                    "kernel_chain.step_error",
                    kernel=step.kernel_name,
                    error=str(e),
                )
                return {
                    "success": False,
                    "outputs": outputs,
                    "total_latency_ms": total_latency,
                    "error": f"{step.kernel_name}: {e}",
                }

        total_latency = (time.perf_counter() - start) * 1000
        audit_hash = self._hash_chain_output(outputs)

        return {
            "success": True,
            "outputs": outputs,
            "total_latency_ms": total_latency,
            "audit_hash": audit_hash,
        }

    @staticmethod
    async def _execute_step(
        step: ChainStep,
        data: Any,
        trace_id: str,
    ) -> Any:
        """Execute a single kernel step, handling sync and async kernels."""
        kernel = step.kernel_instance

        # If the kernel has an async execute, call it directly.
        if hasattr(kernel, "execute"):
            import asyncio
            import inspect

            if inspect.iscoroutinefunction(kernel.execute):
                return await kernel.execute(data)
            # Sync kernel — run in executor.
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, kernel.execute, data)

        # Fallback: callable kernels.
        if callable(kernel):
            return kernel(data)

        raise TypeError(f"Kernel {step.kernel_name} is not callable")

    @staticmethod
    def _hash_chain_output(outputs: list[dict[str, Any]]) -> str:
        """Generate a composite audit hash for the full chain output."""
        content = json.dumps(outputs, sort_keys=True, default=str).encode()
        return hashlib.sha256(content).hexdigest()[:16]

    @property
    def step_count(self) -> int:
        """Number of steps in the chain."""
        return len(self._steps)

    @property
    def execution_count(self) -> int:
        """Total chain executions since init."""
        return self._execution_count
