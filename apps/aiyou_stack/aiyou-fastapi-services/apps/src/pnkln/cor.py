"""Cor - Unified Execution Brain

Central orchestrator for task execution. Coordinates between:
- JR Engine for validation
- Gemini for function calling
- ShadowTag for watermarking
- NS for memory retrieval

Replaces AutoGen's complex group chat coordination with a single,
unified execution flow.
"""

import time
from dataclasses import dataclass
from typing import Any

from ..core.gemini_function_calling import GeminiFunctionCaller


@dataclass
class ExecutionPlan:
    """Plan for executing a task."""

    task: str
    estimated_latency_ms: float
    required_tools: list[str]
    steps: list[str]
    confidence: float


class CorOrchestrator:
    """Cor: The unified execution brain.

    Coordinates all PNKLN components to execute tasks efficiently.

    Example:
        ```python
        cor = CorOrchestrator(
            function_caller=caller,
            judge=judge,
            shadowtag=shadowtag,
            memory=ns
        )

        result = cor.execute("Research AI and write report")
        ```

    """

    def __init__(
        self,
        function_caller: GeminiFunctionCaller | None = None,
        judge: Any | None = None,
        shadowtag: Any | None = None,
        memory: Any | None = None,
    ):
        """Initialize Cor orchestrator.

        Args:
            function_caller: GeminiFunctionCaller instance (optional)
            judge: Optional JudgeSix instance for validation
            shadowtag: Optional ShadowTag instance for watermarking
            memory: Optional SemanticMemory (NS) instance

        """
        self.function_caller = function_caller
        self.judge = judge
        self.shadowtag = shadowtag
        self.memory = memory

        self.execution_history: list[dict[str, Any]] = []

    def plan(self, task: str, available_tools: list[str]) -> ExecutionPlan:
        """Create execution plan for a task.

        Args:
            task: Task description
            available_tools: List of available tool names

        Returns:
            ExecutionPlan

        """
        # Simple planning logic (can be enhanced with LLM)
        steps = [
            "Validate task against mission",
            "Retrieve relevant context from memory",
            f"Execute task: {task}",
            "Watermark output",
            "Return result",
        ]

        # Estimate latency (10ms per function call + 50ms Gemini)
        estimated_latency_ms = 50 + (len(available_tools) * 10)

        return ExecutionPlan(
            task=task,
            estimated_latency_ms=estimated_latency_ms,
            required_tools=available_tools,
            steps=steps,
            confidence=0.85,
        )

    def execute(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Execute a task with full PNKLN stack integration.

        Args:
            task: Task description
            context: Optional context dictionary

        Returns:
            Final result (watermarked if ShadowTag enabled)

        """
        start_time = time.time()
        context = context or {}

        # 1. Retrieve relevant memories if NS available
        if self.memory:
            memories = self.memory.retrieve(task)
            context["memories"] = memories

        # 2. Execute with Judge 6 if available
        if self.judge:
            result = self.judge.enforce(task)
        elif self.function_caller:
            result = self.function_caller.execute(task)
        else:
            raise RuntimeError("No execution backend available (judge or function_caller required)")

        # 3. Watermark output if ShadowTag available
        if self.shadowtag:
            result = self.shadowtag.watermark(
                content=result,
                metadata={
                    "task": task,
                    "timestamp": time.time(),
                    "latency_ms": (time.time() - start_time) * 1000,
                },
            )

        # Record execution
        execution_record = {
            "task": task,
            "result": result,
            "latency_ms": (time.time() - start_time) * 1000,
            "timestamp": time.time(),
            "context": context,
        }
        self.execution_history.append(execution_record)

        return result

    def get_metrics(self) -> dict[str, Any]:
        """Get execution metrics."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "average_latency_ms": 0,
                "p99_latency_ms": 0,
                "meets_sla": False,
            }

        latencies = [e["latency_ms"] for e in self.execution_history]
        latencies.sort()

        p99_index = int(len(latencies) * 0.99)
        p99_latency = latencies[p99_index] if p99_index < len(latencies) else latencies[-1]

        return {
            "total_executions": len(self.execution_history),
            "average_latency_ms": sum(latencies) / len(latencies),
            "p99_latency_ms": p99_latency,
            "meets_sla": p99_latency <= 90,
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
        }
