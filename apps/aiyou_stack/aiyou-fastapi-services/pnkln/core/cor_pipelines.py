"""COR Pipelines — Sequential & Concurrent Execution Patterns
============================================================

Extracted from cor_orchestrator.py (Rich Hickey refactor).

Pattern 1: Sequential Pipeline (Judge #6 validation)
Pattern 2: Concurrent Execution (Monte Carlo decisions)

Author: Pnkln Architecture Team
Version: 2.0.0 — Rich Hickey Refactor
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from .cor_context import ExecutionContext

logger = logging.getLogger(__name__)

T = TypeVar("T")
U = TypeVar("U")


class PipelineStage(Generic[T, U]):
    """Single stage in sequential pipeline.

    SK Equivalent: KernelFunction in SequentialPlanner
    Improvement: Direct async execution without Kernel overhead
    """

    def __init__(
        self,
        name: str,
        func: Callable[[ExecutionContext, T], Awaitable[U]],
        skip_condition: Callable[[ExecutionContext], bool] | None = None,
        timeout_ms: float = 30.0,
    ):
        self.name = name
        self.func = func
        self.skip_condition = skip_condition
        self.timeout_ms = timeout_ms

    async def execute(self, context: ExecutionContext, input_data: T) -> U:
        """Execute stage with latency tracking."""
        if self.skip_condition and self.skip_condition(context):
            logger.info(f"Stage {self.name} skipped for context {context.request_id}")
            return input_data  # type: ignore

        start_time = time.perf_counter()

        try:
            result = await asyncio.wait_for(
                self.func(context, input_data), timeout=self.timeout_ms / 1000.0,
            )
            latency_ms = (time.perf_counter() - start_time) * 1000
            context.record_stage_latency(self.name, latency_ms)

            logger.debug(
                f"Stage {self.name} completed in {latency_ms:.2f}ms (context: {context.request_id})",
            )
            return result

        except TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            context.record_stage_latency(self.name, latency_ms)
            logger.error(
                f"Stage {self.name} timeout after {latency_ms:.2f}ms (limit: {self.timeout_ms}ms)",
            )
            raise


class SequentialPipeline:
    """Sequential execution pipeline with conditional stage skipping.

    SK Pattern: SequentialPlanner
    Pnkln Adaptation: Deterministic stage execution, sub-millisecond overhead.
    """

    def __init__(self, name: str = "unnamed_pipeline"):
        self.name = name
        self.stages: list[PipelineStage] = []

    def add_stage(
        self,
        name: str,
        func: Callable[[ExecutionContext, Any], Awaitable[Any]],
        skip_condition: Callable[[ExecutionContext], bool] | None = None,
        timeout_ms: float = 30.0,
    ) -> SequentialPipeline:
        """Add stage to pipeline (builder pattern)."""
        stage = PipelineStage(name, func, skip_condition, timeout_ms)
        self.stages.append(stage)
        return self

    async def execute(self, context: ExecutionContext, initial_input: Any) -> Any:
        """Execute all stages sequentially."""
        logger.info(
            f"Pipeline {self.name} starting with {len(self.stages)} stages "
            f"(context: {context.request_id})",
        )

        current_output = initial_input

        for stage in self.stages:
            current_output = await stage.execute(context, current_output)

            if context.is_over_budget():
                logger.error(
                    f"Pipeline {self.name} terminated early - budget exceeded "
                    f"({context.total_latency_ms:.2f}ms > {context.latency_budget_ms}ms)",
                )
                break

        logger.info(
            f"Pipeline {self.name} completed in {context.total_latency_ms:.2f}ms "
            f"(context: {context.request_id})",
        )

        return current_output


# ============================================================================
# CONCURRENT EXECUTION
# ============================================================================


@dataclass
class ConcurrentResult:
    """Result from concurrent execution."""

    results: list[Any]
    latency_ms: float
    errors: list[Exception] = field(default_factory=list)


class ConcurrentExecutor:
    """Parallel execution of multiple agents/functions.

    SK Pattern: Multiple agents in parallel
    Pnkln Adaptation: AsyncIO gather() for <500μs overhead.
    """

    def __init__(self, name: str = "concurrent_executor"):
        self.name = name

    async def execute(
        self,
        context: ExecutionContext,
        functions: list[Callable[[Any], Awaitable[Any]]],
        input_data: Any,
        timeout_ms: float = 100.0,
        return_exceptions: bool = True,
    ) -> ConcurrentResult:
        """Execute multiple functions concurrently."""
        start_time = time.perf_counter()

        logger.info(
            f"ConcurrentExecutor {self.name} executing {len(functions)} functions "
            f"(context: {context.request_id})",
        )

        try:
            tasks = [func(input_data) for func in functions]
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=return_exceptions),
                timeout=timeout_ms / 1000.0,
            )

            successful_results = []
            errors = []

            for result in results:
                if isinstance(result, Exception):
                    errors.append(result)
                else:
                    successful_results.append(result)

            latency_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                f"ConcurrentExecutor {self.name} completed in {latency_ms:.2f}ms "
                f"({len(successful_results)} success, {len(errors)} errors)",
            )

            return ConcurrentResult(
                results=successful_results, latency_ms=latency_ms, errors=errors,
            )

        except TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"ConcurrentExecutor {self.name} timeout after {latency_ms:.2f}ms")
            raise
