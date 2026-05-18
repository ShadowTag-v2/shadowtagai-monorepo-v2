# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Concurrent Tool Orchestrator — Read/Write partitioned execution.

Ported from Monorepo-Uphillsnowball/packages/tool_gateway/tool_orchestrator.py.
Architecture adopted from claude_code_services/src/services/tools/toolOrchestration.ts.

Partitions tool calls into batches:
    1. Consecutive read-only tools → run concurrently (up to MAX_CONCURRENCY)
    2. Single non-read-only tool → run serially

This ensures mutating operations never race while read-only operations
maximize throughput. Integrates with shadowtag_os GateAdapter for
26-keyword security classification.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import os
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_MAX_CONCURRENCY = 10

# Tools classified as read-only by shadowtag_os GateAdapter
READ_ONLY_TOOLS = frozenset(
    {
        "view_file",
        "list_dir",
        "grep_search",
        "read_url_content",
        "search_web",
        "read_resource",
        "list_resources",
        "command_status",
    }
)


@dataclass(frozen=True)
class ToolCall:
    """A single tool invocation request.

    Attributes:
        tool_id: Unique identifier for this tool call.
        name: Tool name (e.g., "view_file", "run_command").
        input_data: The tool's input parameters.
        is_read_only: Whether this tool is safe for concurrent execution.
    """

    tool_id: str
    name: str
    input_data: dict[str, Any] = field(default_factory=dict)
    is_read_only: bool = False


@dataclass
class ToolResult:
    """Result from executing a single tool.

    Attributes:
        tool_id: The tool call ID this result corresponds to.
        name: Tool name.
        output: The tool's output (string, dict, etc.).
        error: Optional error message if execution failed.
    """

    tool_id: str
    name: str
    output: Any = None
    error: str | None = None


@dataclass
class Batch:
    """A batch of tool calls to execute together.

    Attributes:
        is_concurrent: If True, all tools in this batch can run in parallel.
        calls: The tool calls in this batch.
    """

    is_concurrent: bool
    calls: list[ToolCall]


def get_max_concurrency() -> int:
    """Get the maximum tool use concurrency from environment or default."""
    env_val = os.environ.get("TOOL_MAX_CONCURRENCY", "")
    try:
        return int(env_val) if env_val else DEFAULT_MAX_CONCURRENCY
    except ValueError:
        return DEFAULT_MAX_CONCURRENCY


def classify_read_only(name: str) -> bool:
    """Classify a tool as read-only based on the shadowtag_os gate registry."""
    return name in READ_ONLY_TOOLS


def partition_tool_calls(calls: list[ToolCall]) -> list[Batch]:
    """Partition tool calls into concurrent and serial batches.

    Consecutive read-only tools are grouped into a single concurrent batch.
    Each non-read-only tool gets its own serial batch.

    Args:
        calls: Ordered list of tool calls to partition.

    Returns:
        List of Batch objects maintaining the original ordering.
    """
    batches: list[Batch] = []

    for call in calls:
        if call.is_read_only and batches and batches[-1].is_concurrent:
            # Extend the current concurrent batch
            batches[-1].calls.append(call)
        else:
            batches.append(Batch(is_concurrent=call.is_read_only, calls=[call]))

    return batches


# Type alias for the tool executor function
ToolExecutor = Callable[[ToolCall], Any]


async def _run_single(executor: ToolExecutor, call: ToolCall) -> ToolResult:
    """Execute a single tool call and wrap the result."""
    try:
        if inspect.iscoroutinefunction(executor):
            output = await executor(call)
        else:
            output = executor(call)
        return ToolResult(tool_id=call.tool_id, name=call.name, output=output)
    except Exception as exc:
        logger.error("Tool %s (%s) failed: %s", call.name, call.tool_id, exc)
        return ToolResult(
            tool_id=call.tool_id,
            name=call.name,
            error=str(exc),
        )


async def run_tools(
    calls: list[ToolCall],
    executor: ToolExecutor,
) -> AsyncIterator[ToolResult]:
    """Execute tool calls with automatic concurrent/serial partitioning.

    Read-only tools run concurrently (up to MAX_CONCURRENCY).
    Non-read-only tools run serially to prevent race conditions.

    Args:
        calls: Ordered list of tool calls.
        executor: Async or sync callable that executes a single ToolCall.

    Yields:
        ToolResult for each completed tool call.
    """
    max_concurrency = get_max_concurrency()

    for batch in partition_tool_calls(calls):
        if batch.is_concurrent:
            # Run read-only batch concurrently with semaphore
            semaphore = asyncio.Semaphore(max_concurrency)

            async def _bounded(call: ToolCall) -> ToolResult:
                async with semaphore:
                    return await _run_single(executor, call)

            tasks = [asyncio.create_task(_bounded(c)) for c in batch.calls]
            for coro in asyncio.as_completed(tasks):
                result = await coro
                yield result
        else:
            # Run non-read-only batch serially
            for call in batch.calls:
                result = await _run_single(executor, call)
                yield result
