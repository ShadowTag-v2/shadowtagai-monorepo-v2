# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Unit tests for Cor Orchestrator (SK-inspired patterns).
"""

import pytest
import asyncio
from pnkln.core.cor_orchestrator import (
  CorOrchestrator,
  ExecutionContext,
  SequentialPipeline,
  ConcurrentExecutor,
)


class TestExecutionContext:
  """Test suite for ExecutionContext."""

  def test_context_creation(self):
    """Test context creation with defaults."""
    ctx = ExecutionContext(request_id="test_001")

    assert ctx.request_id == "test_001"
    assert ctx.latency_budget_ms == 90.0
    assert ctx.total_latency_ms == 0.0

  def test_variable_storage(self):
    """Test variable storage and retrieval."""
    ctx = ExecutionContext(request_id="test_002")

    ctx.set_variable("risk_level", "LOW")
    assert ctx.get_variable("risk_level") == "LOW"
    assert ctx.get_variable("nonexistent", "default") == "default"

  def test_latency_tracking(self):
    """Test latency recording."""
    ctx = ExecutionContext(request_id="test_003", latency_budget_ms=100.0)

    ctx.record_stage_latency("stage_1", 25.0)
    ctx.record_stage_latency("stage_2", 50.0)

    assert ctx.stage_latencies["stage_1"] == 25.0
    assert ctx.stage_latencies["stage_2"] == 50.0
    assert ctx.total_latency_ms == 75.0

  def test_budget_exceeded(self):
    """Test budget exceeded detection."""
    ctx = ExecutionContext(request_id="test_004", latency_budget_ms=50.0)

    ctx.record_stage_latency("slow_stage", 60.0)
    assert ctx.is_over_budget()


class TestSequentialPipeline:
  """Test suite for Sequential Pipeline (SK Pattern 1)."""

  @pytest.mark.asyncio
  async def test_pipeline_execution(self):
    """Test basic pipeline execution."""
    pipeline = SequentialPipeline("test_pipeline")

    async def stage1(ctx, data):
      ctx.set_variable("stage1_ran", True)
      return data + 1

    async def stage2(ctx, data):
      ctx.set_variable("stage2_ran", True)
      return data * 2

    pipeline.add_stage("stage1", stage1)
    pipeline.add_stage("stage2", stage2)

    ctx = ExecutionContext(request_id="test_pipe")
    result = await pipeline.execute(ctx, 10)

    assert result == 22  # (10 + 1) * 2
    assert ctx.get_variable("stage1_ran") is True
    assert ctx.get_variable("stage2_ran") is True

  @pytest.mark.asyncio
  async def test_pipeline_conditional_skip(self):
    """Test conditional stage skipping."""
    pipeline = SequentialPipeline("skip_pipeline")

    async def stage1(ctx, data):
      ctx.set_variable("skip_next", True)
      return data

    async def stage2(ctx, data):
      return data + 100  # Should be skipped

    pipeline.add_stage("stage1", stage1)
    pipeline.add_stage(
      "stage2", stage2, skip_condition=lambda ctx: ctx.get_variable("skip_next", False)
    )

    ctx = ExecutionContext(request_id="test_skip")
    result = await pipeline.execute(ctx, 10)

    assert result == 10  # Stage 2 was skipped

  @pytest.mark.asyncio
  async def test_pipeline_timeout(self):
    """Test stage timeout enforcement."""
    pipeline = SequentialPipeline("timeout_pipeline")

    async def slow_stage(ctx, data):
      await asyncio.sleep(0.1)  # 100ms
      return data

    pipeline.add_stage("slow", slow_stage, timeout_ms=10.0)  # 10ms timeout

    ctx = ExecutionContext(request_id="test_timeout")

    with pytest.raises(asyncio.TimeoutError):
      await pipeline.execute(ctx, 10)


class TestConcurrentExecutor:
  """Test suite for Concurrent Executor (SK Pattern 2)."""

  @pytest.mark.asyncio
  async def test_concurrent_execution(self):
    """Test concurrent function execution."""
    executor = ConcurrentExecutor("test_executor")

    async def func1(data):
      await asyncio.sleep(0.01)
      return data + 1

    async def func2(data):
      await asyncio.sleep(0.01)
      return data * 2

    async def func3(data):
      await asyncio.sleep(0.01)
      return data - 1

    ctx = ExecutionContext(request_id="test_concurrent")
    result = await executor.execute(ctx, [func1, func2, func3], 10)

    assert len(result.results) == 3
    assert 11 in result.results  # func1
    assert 20 in result.results  # func2
    assert 9 in result.results  # func3
    assert result.latency_ms < 50  # Should be ~10ms (parallel), not 30ms (sequential)

  @pytest.mark.asyncio
  async def test_concurrent_error_handling(self):
    """Test error handling in concurrent execution."""
    executor = ConcurrentExecutor("error_executor")

    async def good_func(data):
      return data + 1

    async def bad_func(data):
      raise ValueError("Test error")

    ctx = ExecutionContext(request_id="test_errors")
    result = await executor.execute(
      ctx, [good_func, bad_func], 10, return_exceptions=True
    )

    assert len(result.results) == 1  # Only good_func succeeded
    assert len(result.errors) == 1  # bad_func raised error
    assert isinstance(result.errors[0], ValueError)


class TestCorOrchestrator:
  """Test suite for Cor Orchestrator."""

  def test_orchestrator_initialization(self):
    """Test orchestrator initialization."""
    orchestrator = CorOrchestrator("test_orchestrator")
    assert orchestrator.name == "test_orchestrator"
    assert len(orchestrator.pipelines) == 0
    assert len(orchestrator.executors) == 0

  @pytest.mark.asyncio
  async def test_pipeline_registration_and_execution(self):
    """Test pipeline registration and execution."""
    orchestrator = CorOrchestrator()

    async def simple_stage(ctx, data):
      return data * 2

    pipeline = SequentialPipeline("test")
    pipeline.add_stage("double", simple_stage)

    orchestrator.register_pipeline("test", pipeline)

    ctx = orchestrator.create_context("req_001")
    result = await orchestrator.execute_pipeline("test", ctx, 5)

    assert result == 10

  @pytest.mark.asyncio
  async def test_executor_registration_and_execution(self):
    """Test executor registration and execution."""
    orchestrator = CorOrchestrator()
    executor = ConcurrentExecutor("test_executor")

    orchestrator.register_executor("test", executor)

    async def add_one(data):
      return data + 1

    ctx = orchestrator.create_context("req_002")
    result = await orchestrator.execute_concurrent(
      "test", ctx, [add_one, add_one, add_one], 10
    )

    assert len(result.results) == 3
    assert all(r == 11 for r in result.results)


if __name__ == "__main__":
  pytest.main([__file__, "-v", "-s"])
