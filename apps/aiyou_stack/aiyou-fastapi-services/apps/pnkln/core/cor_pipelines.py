"""COR PIPELINES - Sequential & Concurrent Execution Patterns
============================================================

Extracted from cor_orchestrator.py as part of the Rich Hickey refactor.

Pattern 1: Sequential Pipeline (Maps to Judge 6 validation)
Pattern 2: Concurrent Execution (Maps to Monte Carlo decisions)

Author: Pnkln Architecture Team
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


# ============================================================================
# PATTERN 1: SEQUENTIAL PIPELINE
# ============================================================================

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
        """Initialize pipeline stage.

        Args:
            name: Stage identifier
            func: Async function to execute
            skip_condition: Optional predicate to skip stage
            timeout_ms: Stage-level timeout (default 30ms)

        """
        self.name = name
        self.func = func
        self.skip_condition = skip_condition
        self.timeout_ms = timeout_ms

    async def execute(self, context: ExecutionContext, input_data: T) -> U:
        """Execute stage with latency tracking.

        Returns:
            Stage output

        Raises:
            asyncio.TimeoutError: If stage exceeds timeout

        """
        # Check skip condition
        if self.skip_condition and self.skip_condition(context):
            logger.info(f"Stage {self.name} skipped for context {context.request_id}")
            return input_data  # type: ignore

        start_time = time.perf_counter()

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self.func(context, input_data),
                timeout=self.timeout_ms / 1000.0,
            )

            # Record latency
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
    Pnkln Adaptation:
    - Deterministic stage execution (no LLM planning)
    - Sub-millisecond overhead
    - Conditional skipping for efficiency (e.g., skip Gemini if LOW risk)

    Example:
        pipeline = SequentialPipeline()
        pipeline.add_stage("risk_scan", jr_engine_scan)
        pipeline.add_stage("semantic_check", gemini_validate,
                          skip_if=lambda ctx: ctx.get_variable("risk") == "LOW")
        pipeline.add_stage("final_decision", hybrid_judge)

        result = await pipeline.execute(context, request_data)

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
        """Add stage to pipeline (builder pattern).

        Args:
            name: Stage identifier
            func: Async function to execute
            skip_condition: Optional predicate to skip stage
            timeout_ms: Stage-level timeout

        Returns:
            Self for method chaining

        """
        stage = PipelineStage(name, func, skip_condition, timeout_ms)
        self.stages.append(stage)
        return self

    async def execute(self, context: ExecutionContext, initial_input: Any) -> Any:
        """Execute all stages sequentially.

        Args:
            context: Execution context for tracking
            initial_input: Input to first stage

        Returns:
            Output of final stage

        Raises:
            asyncio.TimeoutError: If any stage times out
            Exception: If any stage raises

        """
        logger.info(
            f"Pipeline {self.name} starting with {len(self.stages)} stages "
            f"(context: {context.request_id})",
        )

        current_output = initial_input

        for stage in self.stages:
            current_output = await stage.execute(context, current_output)

            # Early termination if over budget
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
# PATTERN 2: CONCURRENT EXECUTION
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
    Pnkln Adaptation:
    - AsyncIO gather() for Python native concurrency
    - <500μs overhead for 5 parallel calls
    - Aggregation logic built-in (vs SK's external composition)

    Example:
        executor = ConcurrentExecutor()
        results = await executor.execute(
            context,
            [prob_a_func, prob_b_func, prob_c_func, prob_d_func, prob_e_func],
            decision_data
        )
        # Returns all 5 probability results in parallel

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
        """Execute multiple functions concurrently.

        Args:
            context: Execution context
            functions: List of async functions to execute
            input_data: Input passed to all functions
            timeout_ms: Total timeout for all executions
            return_exceptions: If True, return exceptions instead of raising

        Returns:
            ConcurrentResult with all results and latency

        """
        start_time = time.perf_counter()

        logger.info(
            f"ConcurrentExecutor {self.name} executing {len(functions)} functions "
            f"(context: {context.request_id})",
        )

        try:
            # Create tasks
            tasks = [func(input_data) for func in functions]

            # Execute with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=return_exceptions),
                timeout=timeout_ms / 1000.0,
            )

            # Separate results and errors
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
                results=successful_results,
                latency_ms=latency_ms,
                errors=errors,
            )

        except TimeoutError:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"ConcurrentExecutor {self.name} timeout after {latency_ms:.2f}ms")
            raise
