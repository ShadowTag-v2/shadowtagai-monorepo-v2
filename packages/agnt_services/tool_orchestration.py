# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool Orchestration Service — Ported from Claude Code v2.1.91 tools/.

Partitions tool calls into serial/concurrent batches and executes them
with proper context propagation.

Reference: Claude Code v2.1.91 src/services/tools/toolOrchestration.ts (189 lines)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any
from collections.abc import AsyncIterator, Callable

logger = logging.getLogger(__name__)

DEFAULT_MAX_CONCURRENCY = 10


@dataclass
class ToolUseBlock:
  id: str
  name: str
  input: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolUseContext:
  options: dict[str, Any] = field(default_factory=dict)
  in_progress_ids: set[str] = field(default_factory=set)


@dataclass
class ToolResult:
  tool_use_id: str
  output: Any = None
  error: str | None = None
  context_modifier: Callable[[ToolUseContext], ToolUseContext] | None = None


@dataclass
class Batch:
  is_concurrency_safe: bool
  blocks: list[ToolUseBlock] = field(default_factory=list)


def get_max_tool_use_concurrency() -> int:
  import os

  val = os.environ.get("AGNT_MAX_TOOL_USE_CONCURRENCY", "")
  try:
    return int(val) if val else DEFAULT_MAX_CONCURRENCY
  except ValueError:
    return DEFAULT_MAX_CONCURRENCY


def partition_tool_calls(
  tool_blocks: list[ToolUseBlock],
  is_concurrency_safe_fn: Callable[[ToolUseBlock], bool] | None = None,
) -> list[Batch]:
  """Partition tool calls into serial/concurrent batches.

  Consecutive concurrency-safe tools are grouped; others run serially.
  """
  batches: list[Batch] = []
  for block in tool_blocks:
    safe = is_concurrency_safe_fn(block) if is_concurrency_safe_fn else False
    if safe and batches and batches[-1].is_concurrency_safe:
      batches[-1].blocks.append(block)
    else:
      batches.append(Batch(is_concurrency_safe=safe, blocks=[block]))
  return batches


async def run_tools_serially(
  blocks: list[ToolUseBlock],
  execute_fn: Callable[[ToolUseBlock, ToolUseContext], Any],
  context: ToolUseContext,
) -> AsyncIterator[ToolResult]:
  """Execute tool blocks serially, propagating context changes."""
  for block in blocks:
    context.in_progress_ids.add(block.id)
    try:
      result = await asyncio.to_thread(execute_fn, block, context)
      yield ToolResult(tool_use_id=block.id, output=result)
    except Exception as exc:
      yield ToolResult(tool_use_id=block.id, error=str(exc))
    finally:
      context.in_progress_ids.discard(block.id)


async def run_tools_concurrently(
  blocks: list[ToolUseBlock],
  execute_fn: Callable[[ToolUseBlock, ToolUseContext], Any],
  context: ToolUseContext,
  max_concurrency: int | None = None,
) -> list[ToolResult]:
  """Execute tool blocks concurrently with bounded parallelism."""
  sem = asyncio.Semaphore(max_concurrency or get_max_tool_use_concurrency())
  results: list[ToolResult] = []

  async def _run_one(block: ToolUseBlock) -> ToolResult:
    async with sem:
      context.in_progress_ids.add(block.id)
      try:
        result = await asyncio.to_thread(execute_fn, block, context)
        return ToolResult(tool_use_id=block.id, output=result)
      except Exception as exc:
        return ToolResult(tool_use_id=block.id, error=str(exc))
      finally:
        context.in_progress_ids.discard(block.id)

  tasks = [asyncio.create_task(_run_one(b)) for b in blocks]
  results = await asyncio.gather(*tasks)
  return list(results)
