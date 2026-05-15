"""Tests for DeepAgent pattern enhancements.

Tests dynamic tool retrieval, RL rewards, and memory persistence.
"""

import asyncio
import time

import pytest

from pnkln.core.cor_orchestrator import (
    CorOrchestrator,
    ExecutionContext,
    OrchestratorMemory,
    ToolRegistry,
)
from src.agents.base import AgentPerformance


class TestToolRegistry:
    """Tests for dynamic tool retrieval."""

    def test_tool_registration(self):
        """Test basic tool registration."""
        registry = ToolRegistry()

        def sample_tool(x):
            return x * 2

        registry.register_tool("multiplier", "Multiplies input by 2", sample_tool)

        assert "multiplier" in registry.tools
        assert registry.tools["multiplier"].usage_count == 0

    def test_tool_retrieval(self):
        """Test semantic tool retrieval."""
        registry = ToolRegistry()

        # Register multiple tools
        registry.register_tool("calculator", "Performs math operations", lambda x: x)
        registry.register_tool("translator", "Translates text between languages", lambda x: x)
        registry.register_tool("summarizer", "Summarizes long text", lambda x: x)

        # Retrieve tools
        results = registry.retrieve_tools("calculate sum", top_k=2)

        assert len(results) <= 2
        assert all(isinstance(r, tuple) for r in results)

    @pytest.mark.asyncio
    async def test_tool_execution_metrics(self):
        """Test that tool execution updates metrics."""
        registry = ToolRegistry()

        async def slow_tool(x):
            await asyncio.sleep(0.01)
            return x

        registry.register_tool("slow", "A slow tool", slow_tool)

        result, latency = await registry.execute_tool("slow", 42)

        assert result == 42
        assert latency > 10  # At least 10ms
        assert registry.tools["slow"].usage_count == 1
        assert registry.tools["slow"].avg_latency_ms > 0


class TestRLRewards:
    """Tests for RL reward signal enhancements."""

    def test_reward_computation_success(self):
        """Test reward for successful execution."""
        perf = AgentPerformance(agent_name="test")

        # Fast successful execution
        reward = perf.compute_reward(
            success=True,
            latency_ms=45.0,  # Half of 90ms budget
            cost_usd=0.0001,
        )

        assert reward > 1.0  # Success + latency bonus

    def test_reward_computation_failure(self):
        """Test reward for failed execution."""
        perf = AgentPerformance(agent_name="test")

        reward = perf.compute_reward(success=False, latency_ms=100.0, cost_usd=0.001)

        assert reward < 0  # Failure penalty

    def test_q_value_update(self):
        """Test Q-value updates with executions."""
        perf = AgentPerformance(agent_name="test")

        # Multiple successful executions
        for _ in range(10):
            perf.update_metrics(success=True, latency_ms=30.0, cost_usd=0.0001)

        assert perf.q_value > 0
        assert len(perf.reward_history) == 10

    def test_ucb_score(self):
        """Test UCB score calculation."""
        perf = AgentPerformance(agent_name="test")

        # Initial UCB should have high exploration bonus
        perf.get_ucb_score()

        # After many executions, exploration bonus should decrease
        for _ in range(100):
            perf.update_metrics(True, 30.0, 0.0001)

        perf.get_ucb_score()

        # Q-value should dominate after many samples
        assert perf.exploration_bonus < 1.0


class TestOrchestratorMemory:
    """Tests for orchestrator memory system."""

    def test_memory_store(self):
        """Test storing execution in memory."""
        memory = OrchestratorMemory()
        context = ExecutionContext(request_id="test-1")
        context.total_latency_ms = 50.0

        memory.store(context, {"result": "success"}, importance=0.5)

        assert len(memory.short_term) == 1
        assert memory.short_term[0]["request_id"] == "test-1"

    def test_episodic_memory(self):
        """Test high-importance items go to episodic memory."""
        memory = OrchestratorMemory()
        context = ExecutionContext(request_id="important-1")

        memory.store(context, {"result": "critical"}, importance=0.9)

        assert "important-1" in memory.episodic

    def test_memory_compression(self):
        """Test compression from short-term to long-term."""
        memory = OrchestratorMemory(max_short_term=5)

        # Fill short-term memory
        for i in range(5):
            context = ExecutionContext(request_id=f"test-{i}")
            context.total_latency_ms = 50.0 + i * 10
            memory.store(context, {"i": i})

        # Should trigger compression
        assert len(memory.short_term) == 0
        assert len(memory.long_term) == 1
        assert memory.long_term[0]["execution_count"] == 5

    def test_memory_retrieval(self):
        """Test retrieving memories by query."""
        memory = OrchestratorMemory()

        context = ExecutionContext(request_id="validation-test")
        context.set_variable("task", "validate user input")
        memory.store(context, {"valid": True})

        results = memory.retrieve_context("validation")
        assert len(results) >= 1


class TestCorOrchestratorDeepAgent:
    """Tests for DeepAgent-enhanced orchestrator."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with DeepAgent components."""
        orchestrator = CorOrchestrator("test")

        assert orchestrator.tool_registry is not None
        assert orchestrator.memory is not None

    def test_tool_registration_via_orchestrator(self):
        """Test registering tools through orchestrator."""
        orchestrator = CorOrchestrator("test")

        orchestrator.register_tool("validator", "Validates input data", lambda x: True)

        assert "validator" in orchestrator.tool_registry.tools

    @pytest.mark.asyncio
    async def test_pipeline_with_memory(self):
        """Test pipeline execution stores results in memory."""
        orchestrator = CorOrchestrator("test")

        # Create simple pipeline
        from pnkln.core.cor_orchestrator import SequentialPipeline

        async def simple_stage(ctx, data):
            return {"processed": data}

        pipeline = SequentialPipeline("test_pipeline")
        pipeline.add_stage("process", simple_stage)

        orchestrator.register_pipeline("test", pipeline)

        # Execute with memory
        context = orchestrator.create_context("req-1")
        result = await orchestrator.execute_pipeline_with_memory("test", context, {"input": "data"})

        assert result["processed"]["input"] == "data"
        assert len(orchestrator.memory.short_term) == 1

    def test_get_stats(self):
        """Test getting orchestrator statistics."""
        orchestrator = CorOrchestrator("test")

        orchestrator.register_tool("t1", "Tool 1", lambda x: x)
        orchestrator.register_tool("t2", "Tool 2", lambda x: x)

        stats = orchestrator.get_stats()

        assert stats["name"] == "test"
        assert stats["tools"] == 2
        assert "memory" in stats


class TestBenchmarks:
    """Performance benchmarks for DeepAgent enhancements."""

    @pytest.mark.asyncio
    async def test_tool_retrieval_latency(self):
        """Benchmark tool retrieval latency."""
        registry = ToolRegistry()

        # Register 100 tools
        for i in range(100):
            registry.register_tool(
                f"tool_{i}",
                f"Tool number {i} for various operations",
                lambda x: x,
            )

        # Measure retrieval time
        start = time.perf_counter()
        for _ in range(100):
            registry.retrieve_tools("operation processing", top_k=5)
        elapsed_ms = (time.perf_counter() - start) * 1000

        avg_latency = elapsed_ms / 100
        print(f"Tool retrieval avg latency: {avg_latency:.3f}ms")

        # Should be sub-millisecond
        assert avg_latency < 1.0

    def test_memory_compression_ratio(self):
        """Test memory achieves target compression ratio."""
        memory = OrchestratorMemory(max_short_term=100)

        # Store 100 executions
        for i in range(100):
            context = ExecutionContext(request_id=f"req-{i}")
            context.total_latency_ms = 50.0
            context.stage_latencies = {"stage1": 30.0, "stage2": 20.0}
            memory.store(context, {"data": "x" * 100})

        # Check compression
        assert len(memory.long_term) == 1
        assert memory.long_term[0]["compression_ratio"] == 100

    def test_rl_reward_computation_speed(self):
        """Benchmark RL reward computation."""
        perf = AgentPerformance(agent_name="bench")

        start = time.perf_counter()
        for i in range(10000):
            perf.update_metrics(
                success=i % 10 != 0,  # 90% success rate
                latency_ms=30.0 + (i % 60),
                cost_usd=0.0001,
            )
        elapsed_ms = (time.perf_counter() - start) * 1000

        avg_latency = elapsed_ms / 10000
        print(f"RL reward update avg latency: {avg_latency:.6f}ms")

        # Should be sub-microsecond
        assert avg_latency < 0.01  # 10 microseconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
