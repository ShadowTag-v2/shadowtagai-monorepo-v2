# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for packages/tool_gateway/tool_orchestrator.py."""

from __future__ import annotations

import asyncio

import pytest

from tool_gateway.tool_orchestrator import (
    Batch,
    ToolCall,
    ToolResult,
    partition_tool_calls,
    run_tools,
)


class TestPartitionToolCalls:
    """Tests for partition_tool_calls."""

    def test_empty_list(self) -> None:
        assert partition_tool_calls([]) == []

    def test_all_read_only(self) -> None:
        calls = [
            ToolCall(tool_id="1", name="view_file", is_read_only=True),
            ToolCall(tool_id="2", name="grep", is_read_only=True),
            ToolCall(tool_id="3", name="list_dir", is_read_only=True),
        ]
        batches = partition_tool_calls(calls)
        assert len(batches) == 1
        assert batches[0].is_concurrent is True
        assert len(batches[0].calls) == 3

    def test_all_mutating(self) -> None:
        calls = [
            ToolCall(tool_id="1", name="write_file", is_read_only=False),
            ToolCall(tool_id="2", name="run_command", is_read_only=False),
        ]
        batches = partition_tool_calls(calls)
        assert len(batches) == 2
        assert all(not b.is_concurrent for b in batches)

    def test_mixed_partitioning(self) -> None:
        calls = [
            ToolCall(tool_id="1", name="view_file", is_read_only=True),
            ToolCall(tool_id="2", name="grep", is_read_only=True),
            ToolCall(tool_id="3", name="write_file", is_read_only=False),
            ToolCall(tool_id="4", name="view_file", is_read_only=True),
        ]
        batches = partition_tool_calls(calls)
        assert len(batches) == 3
        assert batches[0].is_concurrent is True
        assert len(batches[0].calls) == 2
        assert batches[1].is_concurrent is False
        assert len(batches[1].calls) == 1
        assert batches[2].is_concurrent is True
        assert len(batches[2].calls) == 1

    def test_single_call(self) -> None:
        calls = [ToolCall(tool_id="1", name="grep", is_read_only=True)]
        batches = partition_tool_calls(calls)
        assert len(batches) == 1
        assert batches[0].is_concurrent is True


class TestRunTools:
    """Tests for run_tools async execution."""

    @pytest.mark.asyncio
    async def test_serial_execution(self) -> None:
        execution_order: list[str] = []

        async def executor(call: ToolCall) -> str:
            execution_order.append(call.tool_id)
            return f"result-{call.tool_id}"

        calls = [
            ToolCall(tool_id="1", name="write", is_read_only=False),
            ToolCall(tool_id="2", name="write", is_read_only=False),
        ]
        results: list[ToolResult] = []
        async for result in run_tools(calls, executor):
            results.append(result)

        assert len(results) == 2
        assert execution_order == ["1", "2"]

    @pytest.mark.asyncio
    async def test_concurrent_batch(self) -> None:
        async def executor(call: ToolCall) -> str:
            await asyncio.sleep(0.01)
            return f"result-{call.tool_id}"

        calls = [
            ToolCall(tool_id="1", name="view", is_read_only=True),
            ToolCall(tool_id="2", name="grep", is_read_only=True),
            ToolCall(tool_id="3", name="list", is_read_only=True),
        ]
        results: list[ToolResult] = []
        async for result in run_tools(calls, executor):
            results.append(result)

        assert len(results) == 3
        tool_ids = {r.tool_id for r in results}
        assert tool_ids == {"1", "2", "3"}

    @pytest.mark.asyncio
    async def test_error_handling(self) -> None:
        async def executor(call: ToolCall) -> str:
            if call.tool_id == "2":
                raise ValueError("Simulated failure")
            return f"result-{call.tool_id}"

        calls = [
            ToolCall(tool_id="1", name="view", is_read_only=True),
            ToolCall(tool_id="2", name="grep", is_read_only=True),
        ]
        results: list[ToolResult] = []
        async for result in run_tools(calls, executor):
            results.append(result)

        assert len(results) == 2
        error_results = [r for r in results if r.error]
        assert len(error_results) == 1
        assert "Simulated failure" in error_results[0].error
