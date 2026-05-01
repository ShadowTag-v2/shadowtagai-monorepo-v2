# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Streaming Tool Executor — Concurrent tool execution with ordering guarantees.

Ported from Claude Code v2.1.91 StreamingToolExecutor.ts.

Architecture:
  Tools are queued as they stream in from the model response. Concurrent-safe
  tools (reads, searches) execute in parallel. Non-concurrent tools (writes,
  bash) execute exclusively. Results are buffered and emitted in receipt order.

  Sibling abort: When a bash tool errors, all sibling tools are cancelled
  via the shared abort controller. This prevents cascading failures in
  implicit dependency chains (e.g., mkdir fails → subsequent writes pointless).

  Progress messages are yielded immediately regardless of tool ordering,
  enabling real-time UI updates during long-running operations.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from speculation_engine.engine import BASH_TOOLS, SAFE_READ_TOOLS

logger = logging.getLogger(__name__)


class ToolStatus(StrEnum):
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    YIELDED = "yielded"


class AbortReason(StrEnum):
    SIBLING_ERROR = "sibling_error"
    USER_INTERRUPTED = "user_interrupted"
    STREAMING_FALLBACK = "streaming_fallback"


@dataclass
class ToolResult:
    """Result message from a tool execution."""
    tool_use_id: str
    content: str
    is_error: bool = False
    role: str = "user"


@dataclass
class ProgressMessage:
    """Progress update from an executing tool."""
    tool_use_id: str
    content: str
    timestamp: float = field(default_factory=time.monotonic)


@dataclass
class MessageUpdate:
    """A message update yielded by the executor."""
    message: ToolResult | ProgressMessage | None = None
    context_modifier: Callable[..., Any] | None = None


@dataclass
class TrackedTool:
    """Internal tracking state for a queued/executing tool."""
    id: str
    name: str
    input_data: dict[str, Any]
    status: ToolStatus = ToolStatus.QUEUED
    is_concurrency_safe: bool = False
    task: asyncio.Task[None] | None = None
    results: list[ToolResult | ProgressMessage] = field(default_factory=list)
    pending_progress: list[ProgressMessage] = field(default_factory=list)
    context_modifiers: list[Callable[..., Any]] = field(default_factory=list)

    @property
    def description(self) -> str:
        summary = (
            self.input_data.get("command")
            or self.input_data.get("file_path")
            or self.input_data.get("pattern")
            or ""
        )
        if isinstance(summary, str) and len(summary) > 0:
            truncated = summary[:40] + "\u2026" if len(summary) > 40 else summary
            return f"{self.name}({truncated})"
        return self.name


# Type alias for tool execution functions.
ToolExecuteFn = Callable[
    [str, str, dict[str, Any]],
    AsyncIterator[MessageUpdate],
]


class StreamingToolExecutor:
    """Executes tools as they stream in with concurrency control.

    - Concurrent-safe tools execute in parallel with other concurrent-safe tools.
    - Non-concurrent tools execute alone (exclusive access).
    - Results are buffered and emitted in the order tools were received.
    - Bash errors cascade to abort all sibling tools.
    """

    def __init__(
        self,
        *,
        execute_fn: ToolExecuteFn | None = None,
        concurrency_check_fn: Callable[[str, dict[str, Any]], bool] | None = None,
    ) -> None:
        self._tools: list[TrackedTool] = []
        self._has_errored = False
        self._errored_tool_description = ""
        self._discarded = False
        self._abort_event = asyncio.Event()
        self._progress_event = asyncio.Event()
        self._execute_fn = execute_fn
        self._concurrency_check_fn = concurrency_check_fn or _default_concurrency_check

    def discard(self) -> None:
        """Discard all pending and in-progress tools."""
        self._discarded = True
        self._abort_event.set()

    def add_tool(self, tool_id: str, tool_name: str, input_data: dict[str, Any]) -> None:
        """Add a tool to the execution queue."""
        is_safe = self._concurrency_check_fn(tool_name, input_data)
        tracked = TrackedTool(
            id=tool_id, name=tool_name, input_data=input_data,
            is_concurrency_safe=is_safe,
        )
        self._tools.append(tracked)
        asyncio.ensure_future(self._process_queue())

    def _can_execute_tool(self, is_concurrency_safe: bool) -> bool:
        executing = [t for t in self._tools if t.status == ToolStatus.EXECUTING]
        return (
            len(executing) == 0
            or (is_concurrency_safe and all(t.is_concurrency_safe for t in executing))
        )

    async def _process_queue(self) -> None:
        for tool in self._tools:
            if tool.status != ToolStatus.QUEUED:
                continue
            if self._can_execute_tool(tool.is_concurrency_safe):
                await self._start_tool(tool)
            elif not tool.is_concurrency_safe:
                break

    def _get_abort_reason(self) -> AbortReason | None:
        if self._discarded:
            return AbortReason.STREAMING_FALLBACK
        if self._has_errored:
            return AbortReason.SIBLING_ERROR
        if self._abort_event.is_set():
            return AbortReason.USER_INTERRUPTED
        return None

    def _create_synthetic_error(self, tool_id: str, reason: AbortReason) -> ToolResult:
        if reason == AbortReason.USER_INTERRUPTED:
            return ToolResult(tool_use_id=tool_id, content="User rejected tool use", is_error=True)
        if reason == AbortReason.STREAMING_FALLBACK:
            return ToolResult(tool_use_id=tool_id, content="Streaming fallback - tool execution discarded", is_error=True)
        desc = self._errored_tool_description
        msg = f"Cancelled: parallel tool call {desc} errored" if desc else "Cancelled: parallel tool call errored"
        return ToolResult(tool_use_id=tool_id, content=msg, is_error=True)

    async def _start_tool(self, tool: TrackedTool) -> None:
        tool.status = ToolStatus.EXECUTING

        async def _run() -> None:
            abort_reason = self._get_abort_reason()
            if abort_reason:
                tool.results.append(self._create_synthetic_error(tool.id, abort_reason))
                tool.status = ToolStatus.COMPLETED
                return

            if self._execute_fn:
                this_tool_errored = False
                try:
                    async for update in self._execute_fn(tool.id, tool.name, tool.input_data):
                        reason = self._get_abort_reason()
                        if reason and not this_tool_errored:
                            tool.results.append(self._create_synthetic_error(tool.id, reason))
                            break
                        if update.message:
                            if isinstance(update.message, ProgressMessage):
                                tool.pending_progress.append(update.message)
                                self._progress_event.set()
                            else:
                                if isinstance(update.message, ToolResult) and update.message.is_error:
                                    this_tool_errored = True
                                    if tool.name in BASH_TOOLS:
                                        self._has_errored = True
                                        self._errored_tool_description = tool.description
                                        self._abort_event.set()
                                tool.results.append(update.message)
                        if update.context_modifier:
                            tool.context_modifiers.append(update.context_modifier)
                except Exception as exc:
                    logger.warning("Tool %s execution failed: %s", tool.name, exc)
                    tool.results.append(ToolResult(tool_use_id=tool.id, content=f"Error: {exc}", is_error=True))
            else:
                tool.results.append(ToolResult(tool_use_id=tool.id, content="(no executor configured)", is_error=False))

            tool.status = ToolStatus.COMPLETED
            asyncio.ensure_future(self._process_queue())

        tool.task = asyncio.ensure_future(_run())

    def get_completed_results(self) -> list[MessageUpdate]:
        """Get completed results that haven't been yielded yet (non-blocking)."""
        if self._discarded:
            return []
        updates: list[MessageUpdate] = []
        for tool in self._tools:
            while tool.pending_progress:
                updates.append(MessageUpdate(message=tool.pending_progress.pop(0)))
            if tool.status == ToolStatus.YIELDED:
                continue
            if tool.status == ToolStatus.COMPLETED:
                tool.status = ToolStatus.YIELDED
                for result in tool.results:
                    updates.append(MessageUpdate(message=result))
            elif tool.status == ToolStatus.EXECUTING and not tool.is_concurrency_safe:
                break
        return updates

    async def get_remaining_results(self) -> AsyncIterator[MessageUpdate]:
        """Wait for remaining tools and yield results as they complete."""
        if self._discarded:
            return
        while self._has_unfinished_tools():
            await self._process_queue()
            for update in self.get_completed_results():
                yield update
            if self._has_executing_tools() and not self._has_completed_results() and not self._has_pending_progress():
                executing_tasks = [t.task for t in self._tools if t.status == ToolStatus.EXECUTING and t.task]
                if executing_tasks:
                    self._progress_event.clear()
                    done, _ = await asyncio.wait(
                        [*executing_tasks, asyncio.ensure_future(self._progress_event.wait())],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for task in done:
                        if not task.done():
                            task.cancel()
        for update in self.get_completed_results():
            yield update

    def _has_pending_progress(self) -> bool:
        return any(len(t.pending_progress) > 0 for t in self._tools)

    def _has_completed_results(self) -> bool:
        return any(t.status == ToolStatus.COMPLETED for t in self._tools)

    def _has_executing_tools(self) -> bool:
        return any(t.status == ToolStatus.EXECUTING for t in self._tools)

    def _has_unfinished_tools(self) -> bool:
        return any(t.status != ToolStatus.YIELDED for t in self._tools)

    @property
    def tool_count(self) -> int:
        return len(self._tools)

    @property
    def completed_count(self) -> int:
        return sum(1 for t in self._tools if t.status in (ToolStatus.COMPLETED, ToolStatus.YIELDED))

    def abort_all(self) -> None:
        """Abort all tools by setting the abort event."""
        self._abort_event.set()

    def get_summary(self) -> dict[str, Any]:
        """Return execution summary for telemetry."""
        status_counts: dict[str, int] = {}
        for tool in self._tools:
            status_counts[tool.status.value] = status_counts.get(tool.status.value, 0) + 1
        error_count = sum(
            1 for t in self._tools
            if any(isinstance(r, ToolResult) and r.is_error for r in t.results)
        )
        return {
            "total_tools": len(self._tools),
            "status_counts": status_counts,
            "error_count": error_count,
            "has_errored": self._has_errored,
            "discarded": self._discarded,
        }


def _default_concurrency_check(tool_name: str, _input_data: dict[str, Any]) -> bool:
    """Default concurrency safety check based on tool name classification."""
    return tool_name in SAFE_READ_TOOLS
