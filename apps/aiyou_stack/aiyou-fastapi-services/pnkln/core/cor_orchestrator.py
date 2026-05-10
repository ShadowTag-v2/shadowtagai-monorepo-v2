"""COR ORCHESTRATOR - Backward-Compatibility Barrel File
======================================================

Original monolith (908 lines) decomposed into domain-specific modules:
- cor_context.py   → ExecutionContext
- cor_tools.py     → Tool, ToolRegistry
- cor_pipelines.py → PipelineStage, SequentialPipeline, ConcurrentResult, ConcurrentExecutor
- cor_memory.py    → OrchestratorMemory

This file re-exports ALL public symbols for backward compatibility.
New code should import from the specific submodules directly.

Author: Pnkln Architecture Team
Version: 2.0.0 — Rich Hickey Refactor (barrel re-export)
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from .cor_context import ExecutionContext
from .cor_memory import OrchestratorMemory
from .cor_pipelines import (
    ConcurrentExecutor,
    ConcurrentResult,
    PipelineStage,
    SequentialPipeline,
)
from .cor_tools import Tool, ToolRegistry

logger = logging.getLogger(__name__)


class CorOrchestrator:
    """Core orchestration engine for Pnkln multi-agent system.

    REPLACES: Semantic Kernel's Kernel + Planner
    PERFORMANCE: <1ms p99 coordination overhead
    ARCHITECTURE: Event-driven, single-CPU efficient

    Combines:
    - Sequential pipelines (Pattern 1) via cor_pipelines
    - Concurrent execution (Pattern 2) via cor_pipelines
    - Standardized tools (Pattern 3) via cor_tools
    - Dynamic tool retrieval (DeepAgent Pattern) via cor_tools
    - Memory persistence (DeepAgent Pattern) via cor_memory
    """

    def __init__(self, name: str = "cor_orchestrator"):
        self.name = name
        self.pipelines: dict[str, SequentialPipeline] = {}
        self.executors: dict[str, ConcurrentExecutor] = {}
        self.tool_registry = ToolRegistry()
        self.memory = OrchestratorMemory()

        logger.info(f"CorOrchestrator {self.name} initialized with DeepAgent enhancements")

    def register_pipeline(self, name: str, pipeline: SequentialPipeline) -> None:
        """Register named pipeline for execution."""
        self.pipelines[name] = pipeline
        logger.info(f"Registered pipeline: {name} ({len(pipeline.stages)} stages)")

    def register_executor(self, name: str, executor: ConcurrentExecutor) -> None:
        """Register named concurrent executor."""
        self.executors[name] = executor
        logger.info(f"Registered executor: {name}")

    async def execute_pipeline(
        self,
        pipeline_name: str,
        context: ExecutionContext,
        input_data: Any,
    ) -> Any:
        """Execute registered pipeline by name."""
        if pipeline_name not in self.pipelines:
            raise KeyError(f"Pipeline {pipeline_name} not registered")

        pipeline = self.pipelines[pipeline_name]
        return await pipeline.execute(context, input_data)

    async def execute_concurrent(
        self,
        executor_name: str,
        context: ExecutionContext,
        functions: list[Callable],
        input_data: Any,
        timeout_ms: float = 100.0,
    ) -> ConcurrentResult:
        """Execute functions concurrently using registered executor."""
        if executor_name not in self.executors:
            raise KeyError(f"Executor {executor_name} not registered")

        executor = self.executors[executor_name]
        return await executor.execute(context, functions, input_data, timeout_ms)

    def create_context(
        self,
        request_id: str,
        latency_budget_ms: float = 90.0,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionContext:
        """Create execution context for request."""
        return ExecutionContext(
            request_id=request_id,
            latency_budget_ms=latency_budget_ms,
            metadata=metadata or {},
        )

    # ========================================================================
    # DEEPAGENT ENHANCEMENTS
    # ========================================================================

    def register_tool(self, name: str, description: str, func: Callable) -> None:
        """Register tool for dynamic retrieval."""
        self.tool_registry.register_tool(name, description, func)

    async def execute_with_tool_selection(
        self,
        context: ExecutionContext,
        query: str,
        input_data: Any,
        top_k: int = 3,
    ) -> Any:
        """Execute using dynamically selected tools (DeepAgent pattern)."""
        tools = self.tool_registry.retrieve_tools(query, top_k=top_k)

        if not tools:
            raise ValueError(f"No tools found for query: {query}")

        logger.info(f"Selected {len(tools)} tools for query: {query}")

        best_tool_name, score = tools[0]
        result, latency_ms = await self.tool_registry.execute_tool(
            best_tool_name,
            context,
            input_data,
        )

        importance = score
        self.memory.store(context, result, importance)

        return result

    async def execute_pipeline_with_memory(
        self,
        pipeline_name: str,
        context: ExecutionContext,
        input_data: Any,
    ) -> Any:
        """Execute pipeline and store result in memory."""
        result = await self.execute_pipeline(pipeline_name, context, input_data)

        if context.total_latency_ms < context.latency_budget_ms * 0.5:
            importance = 0.9
        elif context.total_latency_ms < context.latency_budget_ms:
            importance = 0.6
        else:
            importance = 0.3

        self.memory.store(context, result, importance)

        return result

    def get_memory_context(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve relevant memories for context."""
        return self.memory.retrieve_context(query, top_k)

    def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics including DeepAgent metrics."""
        return {
            "name": self.name,
            "pipelines": list(self.pipelines.keys()),
            "executors": list(self.executors.keys()),
            "tools": len(self.tool_registry.tools),
            "memory": self.memory.get_summary(),
        }


# ============================================================================
# EXAMPLE: JUDGE #6 PIPELINE REGISTRATION
# ============================================================================


async def example_usage():
    """Example: Judge 6 validation pipeline using Cor Orchestrator.

    This demonstrates Pattern 1 (Sequential Pipeline) with conditional
    stage skipping to maintain p99≤90ms SLA.
    """
    orchestrator = CorOrchestrator("judge_six_orchestrator")

    async def jr_engine_scan(ctx: ExecutionContext, request: dict) -> dict:
        """Stage 1: ATP 5-19 risk scan (<500μs)."""
        await asyncio.sleep(0.0005)
        risk_level = "LOW"
        ctx.set_variable("risk_level", risk_level)
        return {"risk_level": risk_level, "request": request}

    async def gemini_semantic_check(ctx: ExecutionContext, data: dict) -> dict:
        """Stage 2: Gemini semantic validation (if risk > LOW)."""
        await asyncio.sleep(0.050)
        semantic_score = 0.95
        ctx.set_variable("semantic_score", semantic_score)
        return {**data, "semantic_score": semantic_score}

    async def hybrid_judge_decision(ctx: ExecutionContext, data: dict) -> dict:
        """Stage 3: PyTorch + rules enforcement."""
        await asyncio.sleep(0.020)
        decision = "APPROVED"
        return {**data, "decision": decision}

    pipeline = SequentialPipeline("judge_six_validation")
    pipeline.add_stage("jr_engine_scan", jr_engine_scan, timeout_ms=5.0)
    pipeline.add_stage(
        "gemini_semantic_check",
        gemini_semantic_check,
        skip_condition=lambda ctx: ctx.get_variable("risk_level") == "LOW",
        timeout_ms=60.0,
    )
    pipeline.add_stage("hybrid_judge_decision", hybrid_judge_decision, timeout_ms=25.0)

    orchestrator.register_pipeline("judge_six", pipeline)

    context = orchestrator.create_context("req_001", latency_budget_ms=90.0)
    result = await orchestrator.execute_pipeline(
        "judge_six",
        context,
        {"user_query": "example request"},
    )

    print(f"Result: {result}")
    print(f"Total latency: {context.total_latency_ms:.2f}ms")
    print(f"Stage latencies: {context.stage_latencies}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(example_usage())


# ============================================================================
# Backward-compatible re-exports
# ============================================================================

__all__ = [
    # Context
    "ExecutionContext",
    # Tools
    "Tool",
    "ToolRegistry",
    # Pipelines
    "PipelineStage",
    "SequentialPipeline",
    "ConcurrentResult",
    "ConcurrentExecutor",
    # Memory
    "OrchestratorMemory",
    # Orchestrator
    "CorOrchestrator",
    # Example
    "example_usage",
]
