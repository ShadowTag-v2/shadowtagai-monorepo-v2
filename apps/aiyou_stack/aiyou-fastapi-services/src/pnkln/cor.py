"""Cor - Unified Execution Brain

Central orchestrator for task execution. Coordinates between:
- JR Engine for validation
- Multi-provider LLM (Gemini + Anthropic)
- ShadowTag for watermarking
- NS for memory retrieval

Replaces AutoGen's complex group chat coordination with a single,
unified execution flow. Now supports both Gemini (function calling)
and Anthropic (reasoning) for optimal performance.
"""

import time
from dataclasses import dataclass
from typing import Any

from ..core.gemini_function_calling import GeminiFunctionCaller
from ..core.multi_provider import Provider
from ..core.unified_orchestrator import TaskComplexity, UnifiedOrchestrator


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
    Now supports multi-provider orchestration (Gemini + Anthropic).

    Example:
        ```python
        # Legacy mode (Gemini only)
        cor = CorOrchestrator(
            function_caller=caller,
            judge=judge,
            shadowtag=shadowtag,
            memory=ns
        )

        # Multi-provider mode (Gemini + Anthropic)
        cor = CorOrchestrator(
            unified_orchestrator=unified_orch,
            judge=judge,
            shadowtag=shadowtag,
            memory=ns,
            enable_multi_provider=True
        )

        result = cor.execute("Research AI and write report")
        ```

    """

    def __init__(
        self,
        function_caller: GeminiFunctionCaller | None = None,
        unified_orchestrator: UnifiedOrchestrator | None = None,
        judge: Any | None = None,
        shadowtag: Any | None = None,
        memory: Any | None = None,
        enable_multi_provider: bool = False,
        default_provider: Provider = Provider.AUTO,
    ):
        """Initialize Cor orchestrator.

        Args:
            function_caller: Optional GeminiFunctionCaller instance (legacy)
            unified_orchestrator: Optional UnifiedOrchestrator (multi-provider)
            judge: Optional JudgeSix instance for validation
            shadowtag: Optional ShadowTag instance for watermarking
            memory: Optional SemanticMemory (NS) instance
            enable_multi_provider: Use multi-provider mode
            default_provider: Default LLM provider

        """
        self.function_caller = function_caller
        self.unified_orchestrator = unified_orchestrator
        self.judge = judge
        self.shadowtag = shadowtag
        self.memory = memory
        self.enable_multi_provider = enable_multi_provider
        self.default_provider = default_provider

        # Auto-create unified orchestrator if multi-provider enabled
        if enable_multi_provider and not self.unified_orchestrator:
            self.unified_orchestrator = UnifiedOrchestrator(
                function_caller=function_caller,
                enable_judge=False,  # JR validation handled by Cor
            )

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

    def execute(
        self,
        task: str,
        context: dict[str, Any] | None = None,
        complexity: TaskComplexity | str | None = None,
        provider: Provider | str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Execute a task with full PNKLN stack integration.

        Args:
            task: Task description
            context: Optional context dictionary
            complexity: Optional task complexity (auto-detected if None)
            provider: Optional provider override
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            Final result (watermarked if ShadowTag enabled)

        """
        start_time = time.time()
        context = context or {}
        provider = provider or self.default_provider

        # 1. Retrieve relevant memories if NS available
        if self.memory:
            memories = self.memory.retrieve(task)
            context["memories"] = memories

        # 2. Execute based on mode
        if self.enable_multi_provider and self.unified_orchestrator:
            # Multi-provider mode: Use UnifiedOrchestrator
            if self.judge:
                # Execute with Judge #6 validation
                # Note: UnifiedOrchestrator handles this internally
                result = self.judge.enforce(task)
            else:
                # Direct execution with complexity detection
                unified_result = self.unified_orchestrator.execute(
                    task=task,
                    complexity=complexity,
                    provider=provider,
                    context=context,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                result = unified_result.content
                context["execution_metrics"] = {
                    "complexity": unified_result.task_complexity.value,
                    "primary_provider": unified_result.primary_provider.value,
                    "cost_usd": unified_result.total_cost_usd,
                    "tokens_in": unified_result.total_tokens_input,
                    "tokens_out": unified_result.total_tokens_output,
                    "function_calls": unified_result.function_calls,
                }
        # Legacy mode: Gemini function calling only
        elif self.judge:
            result = self.judge.enforce(task)
        elif self.function_caller:
            result = self.function_caller.execute(task)
        else:
            raise ValueError(
                "No execution backend available (need function_caller or unified_orchestrator)",
            )

        # 3. Watermark output if ShadowTag available
        if self.shadowtag:
            result = self.shadowtag.watermark(
                content=result,
                metadata={
                    "task": task,
                    "timestamp": time.time(),
                    "latency_ms": (time.time() - start_time) * 1000,
                    "provider": provider if isinstance(provider, str) else provider.value,
                    "context": context,
                },
            )

        # Record execution
        execution_record = {
            "task": task,
            "result": result,
            "latency_ms": (time.time() - start_time) * 1000,
            "timestamp": time.time(),
            "context": context,
            "mode": "multi_provider" if self.enable_multi_provider else "legacy",
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
