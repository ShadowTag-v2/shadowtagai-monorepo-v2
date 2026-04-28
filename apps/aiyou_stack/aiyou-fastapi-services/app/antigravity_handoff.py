# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Antigravity Handoff Router - Cross-Model Orchestration

Intelligent routing between Claude Sonnet 4.5 and Gemini 2.0 Flash based on:
- Task type (deep analysis vs fast execution)
- Cost optimization
- SLA requirements
- Model availability (fallback logic)

Author: Gemini 2.0 Flash (Antigravity)
Target: 40% Gemini, 35% Claude, 15% GPT-5, 10% Other
Cost: $60-65K/mo operational
"""

import asyncio
import os
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import google.generativeai as genai

# Import MCP bridge for compression
from app.mcp_bridge import MCPBridge


class ModelChoice(StrEnum):
    """Available LLM models"""

    GEMINI = "gemini-3.1-flash-lite-preview"
    CLAUDE = "claude-sonnet-4.5"
    GPT5 = "gpt-5"
    GROK = "grok-beta"


class TaskType(StrEnum):
    """Task classification for routing"""

    PRODUCTION_INFERENCE = "production_inference"  # Fast, cost-efficient
    DEEP_ANALYSIS = "deep_analysis"  # Superior reasoning
    CODE_REFACTORING = "code_refactoring"  # Large-scale edits
    ARTIFACT_CREATION = "artifact_creation"  # Long-form docs
    JUDGE6_BINARY = "judge6_binary"  # <35ms governance
    SPECIALIZED = "specialized"  # Specific capabilities


@dataclass
class RoutingDecision:
    """Result of routing logic"""

    model: ModelChoice
    reasoning: str
    estimated_cost_usd: float
    estimated_latency_ms: float
    use_mcp_compression: bool


@dataclass
class HandoffResult:
    """Result from model execution"""

    model_used: ModelChoice
    response: str
    latency_ms: float
    cost_usd: float
    compressed: bool
    compression_ratio: float | None = None


class AntigravityRouter:
    """Cross-model orchestration router.

    ROUTING MATRIX:
    - Production Inference    → Gemini (40%)   p99≤100ms, $0.002/1K
    - Deep Analysis           → Claude (35%)   p95≤2s, $0.015/1K
    - Code Refactoring        → Claude (35%)   p95≤3s, $0.015/1K
    - Artifact Creation       → Claude (35%)   p95≤4s, $0.015/1K
    - Judge#6 Binary          → Gemini+MCP     p99≤90ms, $0.0003
    - Specialized Tasks       → GPT-5 (15%)    p99≤500ms, $0.0  10/1K

    FALLBACK LOGIC:
    - Gemini unavailable → Claude (cost penalty)
    - Claude unavailable → Gemini (longer latency)
    - Both unavailable → GPT-5
    - All unavailable → Return error with circuit breaker
    """

    def __init__(
        self,
        gemini_api_key: str | None = None,
        claude_api_key: str | None = None,
        openai_api_key: str | None = None,
    ):
        # API keys
        self.gemini_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.claude_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Initialize Gemini
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel(ModelChoice.GEMINI.value)
        else:
            self.gemini_model = None

        # Initialize MCP Bridge
        self.mcp = MCPBridge()

        # Performance tracking
        self.routing_decisions: list[RoutingDecision] = []
        self.handoff_results: list[HandoffResult] = []

        # Circuit breakers
        self.gemini_failures = 0
        self.claude_failures = 0
        self.max_failures = 3

        print("✅ Antigravity Router initialized")
        print(f"   Gemini: {'enabled' if self.gemini_model else 'disabled'}")
        print(f"   Claude: {'enabled' if self.claude_key else 'disabled'}")
        print(f"   MCP: enabled ({self.mcp.compression_target:.0%} target)")

    def decide_routing(
        self,
        task_type: TaskType,
        context_size_bytes: int,
        sla_ms: int | None = None,
        cost_limit_usd: float | None = None,
    ) -> RoutingDecision:
        """Decide which model to route to based on task characteristics.

        Args:
            task_type: Type of task (from TaskType enum)
            context_size_bytes: Size of input context
            sla_ms: Max latency SLA (None = no constraint)
            cost_limit_usd: Max cost limit (None = no constraint)

        Returns:
            RoutingDecision with model choice and reasoning

        """
        # Default routing based on task type
        routing_map = {
            TaskType.PRODUCTION_INFERENCE: (ModelChoice.GEMINI, 100, 0.002),
            TaskType.DEEP_ANALYSIS: (ModelChoice.CLAUDE, 2000, 0.015),
            TaskType.CODE_REFACTORING: (ModelChoice.CLAUDE, 3000, 0.015),
            TaskType.ARTIFACT_CREATION: (ModelChoice.CLAUDE, 4000, 0.015),
            TaskType.JUDGE6_BINARY: (ModelChoice.GEMINI, 35, 0.0003),
            TaskType.SPECIALIZED: (ModelChoice.GPT5, 500, 0.010),
        }

        model, est_latency, est_cost = routing_map.get(
            task_type,
            (ModelChoice.GEMINI, 100, 0.002),  # Default to Gemini
        )

        # Adjust for SLA constraints
        if sla_ms and est_latency > sla_ms:
            # Need faster model
            if sla_ms < 100:
                model = ModelChoice.GEMINI  # Fastest
            elif sla_ms < 500:
                model = ModelChoice.GPT5

        # Adjust for cost constraints
        if cost_limit_usd and est_cost > cost_limit_usd:
            # Need cheaper model
            model = ModelChoice.GEMINI  # Cheapest

        # Check circuit breakers
        if model == ModelChoice.GEMINI and self.gemini_failures >= self.max_failures:
            model = ModelChoice.CLAUDE  # Fallback to Claude
            reasoning = "Gemini circuit breaker tripped, falling back to Claude"
        elif model == ModelChoice.CLAUDE and self.claude_failures >= self.max_failures:
            model = ModelChoice.GEMINI  # Fallback to Gemini
            reasoning = "Claude circuit breaker tripped, falling back to Gemini"
        else:
            reasoning = f"{task_type.value} → {model.value}"

        # Decide on MCP compression (use for large contexts)
        use_mcp = context_size_bytes > 10_000 or task_type == TaskType.JUDGE6_BINARY

        decision = RoutingDecision(
            model=model,
            reasoning=reasoning,
            estimated_cost_usd=est_cost,
            estimated_latency_ms=est_latency,
            use_mcp_compression=use_mcp,
        )

        self.routing_decisions.append(decision)

        print(f"   → Routing: {model.value} ({reasoning})")
        if use_mcp:
            print(f"   → MCP compression enabled ({context_size_bytes:,} bytes)")

        return decision

    async def execute_handoff(
        self,
        prompt: str,
        context: dict[str, Any],
        routing: RoutingDecision,
    ) -> HandoffResult:
        """Execute model handoff based on routing decision.

        Args:
            prompt: User prompt
            context: Context dict
            routing: RoutingDecision from decide_routing()

        Returns:
            HandoffResult with response and metrics

        """
        start_time = time.time()

        # Apply MCP compression if enabled
        if routing.use_mcp_compression:
            kernel = await self.mcp.atp_519_scan(context)
            # Use compressed kernel instead of full context
            compressed_context = {
                "kernel": kernel.__dict__,
                "original_hash": kernel.compressed_context_hash,
            }
            context_to_use = compressed_context
            compressed = True
            compression_ratio = self.mcp.get_avg_compression()
        else:
            context_to_use = context
            compressed = False
            compression_ratio = None

        # Route to model
        if routing.model == ModelChoice.GEMINI:
            response = await self._call_gemini(prompt, context_to_use)
        elif routing.model == ModelChoice.CLAUDE:
            response = await self._call_claude(prompt, context_to_use)
        elif routing.model == ModelChoice.GPT5:
            response = await self._call_gpt5(prompt, context_to_use)
        else:
            response = f"Model {routing.model} not implemented"

        # Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        cost_usd = routing.estimated_cost_usd  # Simplified

        result = HandoffResult(
            model_used=routing.model,
            response=response,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            compressed=compressed,
            compression_ratio=compression_ratio,
        )

        self.handoff_results.append(result)

        print(f"   ✓ Handoff complete: {latency_ms:.1f}ms, ${cost_usd:.4f}")

        return result

    async def _call_gemini(self, prompt: str, context: dict[str, Any]) -> str:
        """Call Gemini API"""
        if not self.gemini_model:
            self.gemini_failures += 1
            raise ValueError("Gemini API key not configured")

        try:
            # Build enhanced prompt with context
            enhanced_prompt = f"{prompt}\n\nContext: {context}"

            # Call Gemini
            response = await asyncio.to_thread(self.gemini_model.generate_content, enhanced_prompt)

            # Reset failures on success
            self.gemini_failures = 0

            return response.text
        except Exception as e:
            self.gemini_failures += 1
            raise RuntimeError(f"Gemini API error: {e}") from e

    async def _call_claude(self, prompt: str, context: dict[str, Any]) -> str:
        """Call Claude API"""
        if not self.claude_key:
            self.claude_failures += 1
            raise ValueError("Claude API key not configured")

        try:
            # In production, would use Anthropic SDK
            # For now, return mock response
            response = f"[Claude response to: {prompt[:50]}...]"

            # Reset failures on success
            self.claude_failures = 0

            return response
        except Exception as e:
            self.claude_failures += 1
            raise RuntimeError(f"Claude API error: {e}") from e

    async def _call_gpt5(self, prompt: str, context: dict[str, Any]) -> str:
        """Call GPT-5 API"""
        if not self.openai_key:
            raise ValueError("OpenAI API key not configured")

        try:
            # In production, would use OpenAI SDK
            response = f"[GPT-5 response to: {prompt[:50]}...]"
            return response
        except Exception as e:
            raise RuntimeError(f"GPT-5 API error: {e}") from e

    def get_stats(self) -> dict[str, Any]:
        """Get router statistics"""
        if not self.handoff_results:
            return {"message": "No handoffs yet"}

        # Model distribution
        model_counts = {}
        for result in self.handoff_results:
            model_counts[result.model_used.value] = model_counts.get(result.model_used.value, 0) + 1

        # Average metrics
        avg_latency = sum(r.latency_ms for r in self.handoff_results) / len(self.handoff_results)
        avg_cost = sum(r.cost_usd for r in self.handoff_results) / len(self.handoff_results)
        compression_rate = sum(1 for r in self.handoff_results if r.compressed) / len(
            self.handoff_results,
        )

        return {
            "total_handoffs": len(self.handoff_results),
            "model_distribution": model_counts,
            "avg_latency_ms": f"{avg_latency:.1f}",
            "avg_cost_usd": f"${avg_cost:.4f}",
            "compression_rate": f"{compression_rate:.0%}",
            "circuit_breakers": {
                "gemini_failures": self.gemini_failures,
                "claude_failures": self.claude_failures,
            },
            "mcp_stats": self.mcp.get_stats(),
        }


async def test_antigravity_router():
    """Test Antigravity Router"""
    print("\n═══ Antigravity Router Test ═══\n")

    router = AntigravityRouter()

    # Test 1: Production inference (should route to Gemini)
    print("Test 1: Production Inference")
    routing = router.decide_routing(
        task_type=TaskType.PRODUCTION_INFERENCE,
        context_size_bytes=5000,
        sla_ms=100,
    )

    result = await router.execute_handoff(
        prompt="Summarize this context",
        context={"data": "sample context"},
        routing=routing,
    )
    print(f"   Response: {result.response[:100]}...")

    # Test 2: Deep analysis with MCP compression (should route to Claude)
    print("\nTest 2: Deep Analysis with MCP")
    large_context = {"data": "x" * 50000}  # 50KB context
    routing = router.decide_routing(
        task_type=TaskType.DEEP_ANALYSIS,
        context_size_bytes=len(str(large_context)),
        sla_ms=2000,
    )

    result = await router.execute_handoff(
        prompt="Analyze this large dataset",
        context=large_context,
        routing=routing,
    )
    print(f"   Compressed: {result.compressed}, Ratio: {result.compression_ratio}")

    # Test 3: Stats
    print("\nTest 3: Router Stats")
    stats = router.get_stats()
    import json

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(test_antigravity_router())
