"""Unified Orchestrator: Best of Both Worlds

Combines Gemini's native function calling with Anthropic's superior reasoning:
- Gemini: Fast function calling (12x faster, 70% cheaper)
- Anthropic: Deep reasoning, Chain-of-Thought, extended thinking
- Automatic routing based on task complexity

Architecture:
┌─────────────────────────────────────────────────────────┐
│ UnifiedOrchestrator                                     │
│ ├─ Simple tasks → Gemini function calling              │
│ ├─ Complex reasoning → Anthropic CoT                   │
│ ├─ Hybrid → Anthropic plans, Gemini executes           │
│ └─ Judge 6 validates all operations                   │
└─────────────────────────────────────────────────────────┘
"""

import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from .gemini_function_calling import GeminiFunctionCaller
from .multi_provider import MultiProviderExecutor, Provider


class TaskComplexity(StrEnum):
    """Task complexity levels."""

    SIMPLE = "simple"  # Single function call
    MODERATE = "moderate"  # Multiple related function calls
    COMPLEX = "complex"  # Requires reasoning + planning
    HYBRID = "hybrid"  # Anthropic plans, Gemini executes


@dataclass
class UnifiedResult:
    """Result from unified orchestrator execution."""

    content: str
    task_complexity: TaskComplexity
    primary_provider: Provider
    secondary_provider: Provider | None = None

    # Execution metrics
    total_latency_ms: float = 0.0
    function_calls: int = 0
    llm_calls: int = 0

    # Cost tracking
    total_cost_usd: float = 0.0
    cost_breakdown: dict[str, float] = field(default_factory=dict)

    # Tokens
    total_tokens_input: int = 0
    total_tokens_output: int = 0

    # Execution trace
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class UnifiedOrchestrator:
    """Unified orchestrator combining Gemini + Anthropic.

    Routing strategy:
    1. SIMPLE tasks → Gemini function calling only
    2. COMPLEX reasoning → Anthropic CoT only
    3. HYBRID tasks → Anthropic plans, Gemini executes
    4. MODERATE tasks → Auto-detect best provider

    Example:
        ```python
        orchestrator = UnifiedOrchestrator()

        # Simple function calling (Gemini)
        result = orchestrator.execute(
            "Calculate 2+2",
            complexity="simple"
        )

        # Complex reasoning (Anthropic)
        result = orchestrator.execute(
            "Explain quantum entanglement and its implications",
            complexity="complex"
        )

        # Hybrid (Anthropic plans, Gemini executes)
        result = orchestrator.execute(
            "Research AI trends, analyze data, write report",
            complexity="hybrid"
        )
        ```

    """

    def __init__(
        self,
        function_caller: GeminiFunctionCaller | None = None,
        llm_executor: MultiProviderExecutor | None = None,
        enable_judge: bool = True,
        judge_validator: Callable | None = None,
        enable_auto_routing: bool = True,
        default_complexity: TaskComplexity = TaskComplexity.MODERATE,
    ):
        """Initialize unified orchestrator.

        Args:
            function_caller: Optional GeminiFunctionCaller instance
            llm_executor: Optional MultiProviderExecutor instance
            enable_judge: Enable Judge 6 validation
            judge_validator: Optional custom validation function
            enable_auto_routing: Automatically detect task complexity
            default_complexity: Default complexity if not specified

        """
        self.function_caller = function_caller
        self.llm_executor = llm_executor or MultiProviderExecutor()
        self.enable_judge = enable_judge
        self.judge_validator = judge_validator
        self.enable_auto_routing = enable_auto_routing
        self.default_complexity = default_complexity

        # Execution history
        self.execution_history: list[UnifiedResult] = []

    def execute(
        self,
        task: str,
        complexity: TaskComplexity | str | None = None,
        provider: Provider | str = Provider.AUTO,
        system: str | None = None,
        context: dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> UnifiedResult:
        """Execute task with automatic provider routing.

        Args:
            task: Task description
            complexity: Task complexity (auto-detected if None)
            provider: Preferred provider (AUTO for automatic)
            system: Optional system prompt
            context: Optional context dictionary
            temperature: Sampling temperature
            max_tokens: Max tokens to generate

        Returns:
            UnifiedResult with content, metrics, costs

        """
        start_time = time.time()
        context = context or {}

        # Detect complexity if auto-routing enabled
        if complexity is None and self.enable_auto_routing:
            complexity = self._detect_complexity(task)
        elif complexity is None:
            complexity = self.default_complexity
        elif isinstance(complexity, str):
            complexity = TaskComplexity(complexity)

        # Route based on complexity
        if complexity == TaskComplexity.SIMPLE:
            result = self._execute_simple(task, provider, system, temperature, max_tokens)
        elif complexity == TaskComplexity.COMPLEX:
            result = self._execute_complex(task, provider, system, temperature, max_tokens)
        elif complexity == TaskComplexity.HYBRID:
            result = self._execute_hybrid(task, provider, system, temperature, max_tokens)
        else:  # MODERATE
            result = self._execute_moderate(task, provider, system, temperature, max_tokens)

        # Calculate total latency
        result.total_latency_ms = (time.time() - start_time) * 1000
        result.task_complexity = complexity

        # Record execution
        self.execution_history.append(result)

        return result

    def _detect_complexity(self, task: str) -> TaskComplexity:
        """Detect task complexity from task description.

        Uses heuristics:
        - Simple: Single action, simple verbs
        - Complex: Reasoning words, explanations, analysis
        - Hybrid: Multiple steps, workflows
        - Moderate: Default
        """
        task_lower = task.lower()

        # Simple indicators
        simple_patterns = [
            r"calculate\s+\d+",  # "calculate 2+2"
            r"what is\s+\d+",  # "what is 5*5"
            r"(add|subtract|multiply|divide)\s",  # Basic math
            r"^(get|fetch|retrieve)\s",  # Simple retrieval
        ]
        if any(re.search(pattern, task_lower) for pattern in simple_patterns):
            return TaskComplexity.SIMPLE

        # Complex reasoning indicators
        complex_keywords = [
            "explain",
            "analyze",
            "compare",
            "evaluate",
            "critique",
            "reasoning",
            "why",
            "how does",
            "implications",
            "philosophical",
            "ethical",
            "theoretical",
        ]
        if any(keyword in task_lower for keyword in complex_keywords):
            return TaskComplexity.COMPLEX

        # Hybrid indicators (multi-step)
        hybrid_keywords = [
            "and then",
            "after that",
            "followed by",
            "first",
            "second",
            "finally",
            "research and",
            "analyze and",
            "create and",
        ]
        if any(keyword in task_lower for keyword in hybrid_keywords):
            return TaskComplexity.HYBRID

        # Check for multiple sentences (likely complex)
        sentences = task.split(".")
        if len(sentences) > 2:
            return TaskComplexity.COMPLEX

        # Default to moderate
        return TaskComplexity.MODERATE

    def _execute_simple(
        self,
        task: str,
        provider: Provider | str,
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> UnifiedResult:
        """Execute simple task (prefer Gemini for speed/cost).

        Strategy: Single LLM call or simple function calling.
        """
        # If function caller available, use it
        if self.function_caller:
            try:
                content = self.function_caller.execute(task)
                metrics = self.function_caller.get_metrics()

                return UnifiedResult(
                    content=content,
                    task_complexity=TaskComplexity.SIMPLE,
                    primary_provider=Provider.GEMINI,
                    total_latency_ms=metrics["total_latency_ms"],
                    function_calls=metrics["function_calls"],
                    llm_calls=1,
                    execution_trace=[{"type": "gemini_function_calling", "metrics": metrics}],
                )
            except Exception:
                # Fallback to LLM
                pass

        # Fallback: Direct LLM call (prefer Gemini)
        selected_provider = Provider.GEMINI if provider == Provider.AUTO else provider

        response = self.llm_executor.execute(
            prompt=task,
            provider=selected_provider,
            system=system,
            temperature=temperature or 0.3,  # Lower temp for simple tasks
            max_tokens=max_tokens or 1024,
            task_type="general",
        )

        return UnifiedResult(
            content=response.content,
            task_complexity=TaskComplexity.SIMPLE,
            primary_provider=response.provider,
            total_latency_ms=response.latency_ms,
            function_calls=0,
            llm_calls=1,
            total_cost_usd=response.cost_usd,
            total_tokens_input=response.tokens_input,
            total_tokens_output=response.tokens_output,
            cost_breakdown={response.provider.value: response.cost_usd},
            execution_trace=[
                {
                    "type": "llm_call",
                    "provider": response.provider.value,
                    "model": response.model,
                    "latency_ms": response.latency_ms,
                    "cost_usd": response.cost_usd,
                },
            ],
        )

    def _execute_complex(
        self,
        task: str,
        provider: Provider | str,
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> UnifiedResult:
        """Execute complex reasoning task (prefer Anthropic).

        Strategy: Use Anthropic's superior CoT and reasoning capabilities.
        """
        # Force Anthropic for complex reasoning
        selected_provider = Provider.ANTHROPIC if provider == Provider.AUTO else provider

        # Enhanced system prompt for reasoning
        reasoning_system = (
            "You are an expert reasoning engine. Think step-by-step, "
            "consider multiple perspectives, and provide detailed analysis.\n\n"
        )
        if system:
            reasoning_system += system

        response = self.llm_executor.execute(
            prompt=task,
            provider=selected_provider,
            system=reasoning_system,
            temperature=temperature or 0.7,  # Higher temp for creativity
            max_tokens=max_tokens or 4096,  # More tokens for detailed reasoning
            task_type="reasoning",
        )

        return UnifiedResult(
            content=response.content,
            task_complexity=TaskComplexity.COMPLEX,
            primary_provider=response.provider,
            total_latency_ms=response.latency_ms,
            function_calls=0,
            llm_calls=1,
            total_cost_usd=response.cost_usd,
            total_tokens_input=response.tokens_input,
            total_tokens_output=response.tokens_output,
            cost_breakdown={response.provider.value: response.cost_usd},
            execution_trace=[
                {
                    "type": "reasoning",
                    "provider": response.provider.value,
                    "model": response.model,
                    "latency_ms": response.latency_ms,
                    "cost_usd": response.cost_usd,
                },
            ],
        )

    def _execute_hybrid(
        self,
        task: str,
        provider: Provider | str,
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> UnifiedResult:
        """Execute hybrid task (Anthropic plans, Gemini executes).

        Strategy:
        1. Use Anthropic to create execution plan
        2. Use Gemini to execute plan steps with function calling
        3. Use Anthropic to synthesize final result
        """
        execution_trace = []
        total_cost = 0.0
        cost_breakdown = {}
        total_tokens_in = 0
        total_tokens_out = 0

        # Step 1: Anthropic creates plan
        planning_prompt = f"""Create a step-by-step execution plan for this task:

{task}

Format your response as:
STEP 1: [action]
STEP 2: [action]
...
FINAL: [synthesis]"""

        plan_response = self.llm_executor.execute(
            prompt=planning_prompt,
            provider=Provider.ANTHROPIC,
            system=system,
            temperature=0.3,
            max_tokens=1024,
            task_type="reasoning",
        )

        execution_trace.append(
            {
                "type": "planning",
                "provider": "anthropic",
                "model": plan_response.model,
                "latency_ms": plan_response.latency_ms,
                "cost_usd": plan_response.cost_usd,
                "content": plan_response.content,
            },
        )

        total_cost += plan_response.cost_usd
        cost_breakdown["anthropic_planning"] = plan_response.cost_usd
        total_tokens_in += plan_response.tokens_input
        total_tokens_out += plan_response.tokens_output

        # Step 2: Execute plan (use Gemini if function caller available)
        if self.function_caller:
            try:
                execution_result = self.function_caller.execute(task)
                metrics = self.function_caller.get_metrics()

                execution_trace.append(
                    {
                        "type": "execution",
                        "provider": "gemini",
                        "function_calls": metrics["function_calls"],
                        "latency_ms": metrics["total_latency_ms"],
                        "content": execution_result,
                    },
                )
            except Exception:
                # Fallback to direct LLM call
                exec_response = self.llm_executor.execute(
                    prompt=f"Execute this plan:\n\n{plan_response.content}\n\nOriginal task: {task}",
                    provider=Provider.GEMINI,
                    temperature=0.5,
                    max_tokens=2048,
                    task_type="function_calling",
                )

                execution_result = exec_response.content
                total_cost += exec_response.cost_usd
                cost_breakdown["gemini_execution"] = exec_response.cost_usd
                total_tokens_in += exec_response.tokens_input
                total_tokens_out += exec_response.tokens_output

                execution_trace.append(
                    {
                        "type": "execution",
                        "provider": "gemini",
                        "model": exec_response.model,
                        "latency_ms": exec_response.latency_ms,
                        "cost_usd": exec_response.cost_usd,
                    },
                )
        else:
            # No function caller, use Gemini LLM
            exec_response = self.llm_executor.execute(
                prompt=f"Execute this plan:\n\n{plan_response.content}\n\nOriginal task: {task}",
                provider=Provider.GEMINI,
                temperature=0.5,
                max_tokens=2048,
                task_type="function_calling",
            )

            execution_result = exec_response.content
            total_cost += exec_response.cost_usd
            cost_breakdown["gemini_execution"] = exec_response.cost_usd
            total_tokens_in += exec_response.tokens_input
            total_tokens_out += exec_response.tokens_output

            execution_trace.append(
                {
                    "type": "execution",
                    "provider": "gemini",
                    "model": exec_response.model,
                    "latency_ms": exec_response.latency_ms,
                    "cost_usd": exec_response.cost_usd,
                },
            )

        # Step 3: Anthropic synthesizes final result
        synthesis_prompt = f"""Synthesize the final result from this execution:

Original task: {task}
Plan: {plan_response.content}
Execution result: {execution_result}

Provide a clear, concise final answer."""

        final_response = self.llm_executor.execute(
            prompt=synthesis_prompt,
            provider=Provider.ANTHROPIC,
            temperature=0.7,
            max_tokens=2048,
            task_type="reasoning",
        )

        execution_trace.append(
            {
                "type": "synthesis",
                "provider": "anthropic",
                "model": final_response.model,
                "latency_ms": final_response.latency_ms,
                "cost_usd": final_response.cost_usd,
                "content": final_response.content,
            },
        )

        total_cost += final_response.cost_usd
        cost_breakdown["anthropic_synthesis"] = final_response.cost_usd
        total_tokens_in += final_response.tokens_input
        total_tokens_out += final_response.tokens_output

        return UnifiedResult(
            content=final_response.content,
            task_complexity=TaskComplexity.HYBRID,
            primary_provider=Provider.ANTHROPIC,
            secondary_provider=Provider.GEMINI,
            function_calls=self.function_caller.get_metrics()["function_calls"]
            if self.function_caller
            else 0,
            llm_calls=3,  # planning + execution + synthesis
            total_cost_usd=total_cost,
            cost_breakdown=cost_breakdown,
            total_tokens_input=total_tokens_in,
            total_tokens_output=total_tokens_out,
            execution_trace=execution_trace,
        )

    def _execute_moderate(
        self,
        task: str,
        provider: Provider | str,
        system: str | None,
        temperature: float | None,
        max_tokens: int | None,
    ) -> UnifiedResult:
        """Execute moderate task (auto-select provider).

        Strategy: Let MultiProviderExecutor choose based on task type.
        """
        response = self.llm_executor.execute(
            prompt=task,
            provider=provider,
            system=system,
            temperature=temperature or 0.5,
            max_tokens=max_tokens or 2048,
            task_type="general",
        )

        return UnifiedResult(
            content=response.content,
            task_complexity=TaskComplexity.MODERATE,
            primary_provider=response.provider,
            total_latency_ms=response.latency_ms,
            function_calls=0,
            llm_calls=1,
            total_cost_usd=response.cost_usd,
            total_tokens_input=response.tokens_input,
            total_tokens_output=response.tokens_output,
            cost_breakdown={response.provider.value: response.cost_usd},
            execution_trace=[
                {
                    "type": "llm_call",
                    "provider": response.provider.value,
                    "model": response.model,
                    "latency_ms": response.latency_ms,
                    "cost_usd": response.cost_usd,
                },
            ],
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get aggregated execution metrics."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "total_cost_usd": 0.0,
                "average_latency_ms": 0.0,
                "provider_distribution": {},
                "complexity_distribution": {},
            }

        total_cost = sum(r.total_cost_usd for r in self.execution_history)
        avg_latency = sum(r.total_latency_ms for r in self.execution_history) / len(
            self.execution_history,
        )

        # Provider distribution
        provider_counts = {}
        for result in self.execution_history:
            provider = result.primary_provider.value
            provider_counts[provider] = provider_counts.get(provider, 0) + 1

        # Complexity distribution
        complexity_counts = {}
        for result in self.execution_history:
            complexity = result.task_complexity.value
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1

        return {
            "total_executions": len(self.execution_history),
            "total_cost_usd": total_cost,
            "average_latency_ms": avg_latency,
            "total_function_calls": sum(r.function_calls for r in self.execution_history),
            "total_llm_calls": sum(r.llm_calls for r in self.execution_history),
            "provider_distribution": provider_counts,
            "complexity_distribution": complexity_counts,
            "total_tokens_input": sum(r.total_tokens_input for r in self.execution_history),
            "total_tokens_output": sum(r.total_tokens_output for r in self.execution_history),
        }

    def __repr__(self) -> str:
        return (
            f"UnifiedOrchestrator("
            f"function_caller={'enabled' if self.function_caller else 'disabled'}, "
            f"providers={self.llm_executor}, "
            f"auto_routing={self.enable_auto_routing})"
        )
