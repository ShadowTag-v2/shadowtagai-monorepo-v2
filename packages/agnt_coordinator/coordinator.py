# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Sub-Agent Coordinator — bounded-concurrency dispatch pool.

Manages parallel sub-agent execution with:
1. Bounded concurrency via asyncio.Semaphore
2. Task result aggregation with timeout enforcement
3. Error isolation (one sub-agent failure doesn't cascade)
4. Structured task lifecycle: PENDING → RUNNING → DONE/FAILED

Safe Harbor constraints:
- Sub-agents are local asyncio tasks, NOT remote processes.
- No network dispatch. All execution is in-process.
- Task payloads are not persisted to disk (ephemeral).
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_MAX_CONCURRENCY = 4
_DEFAULT_TASK_TIMEOUT_S = 300.0  # 5 minutes


class TaskState(StrEnum):
  """Sub-agent task lifecycle states."""

  PENDING = "pending"
  RUNNING = "running"
  DONE = "done"
  FAILED = "failed"
  CANCELLED = "cancelled"


@dataclass
class TaskResult:
  """Result of a completed sub-agent task."""

  task_id: str
  state: TaskState
  result: Any = None
  error: str | None = None
  elapsed_s: float = 0.0
  created_at: float = field(default_factory=time.time)


class SubAgentCoordinator:
  """Bounded-concurrency sub-agent dispatch pool.

  Executes async callables as sub-agent tasks with:
  - Semaphore-bounded concurrency (default: 4)
  - Per-task timeout enforcement
  - Error isolation per task
  - Structured result aggregation

  Example:
      coordinator = SubAgentCoordinator(max_concurrency=4)

      async def research_task(query: str) -> str:
          return f"Result for {query}"

      results = await coordinator.dispatch_batch([
          ("search_1", research_task, {"query": "topic A"}),
          ("search_2", research_task, {"query": "topic B"}),
      ])
  """

  __slots__ = ("_semaphore", "_max_concurrency", "_timeout_s", "_results")

  def __init__(
    self,
    max_concurrency: int = _DEFAULT_MAX_CONCURRENCY,
    timeout_s: float = _DEFAULT_TASK_TIMEOUT_S,
  ) -> None:
    self._max_concurrency = max_concurrency
    self._semaphore = asyncio.Semaphore(max_concurrency)
    self._timeout_s = timeout_s
    self._results: dict[str, TaskResult] = {}

  @property
  def max_concurrency(self) -> int:
    """Maximum parallel sub-agents."""
    return self._max_concurrency

  @property
  def completed_tasks(self) -> dict[str, TaskResult]:
    """All completed task results from the current session."""
    return dict(self._results)

  async def dispatch(
    self,
    task_fn: Callable[..., Awaitable[Any]],
    *,
    task_id: str | None = None,
    kwargs: dict[str, Any] | None = None,
    timeout_s: float | None = None,
  ) -> TaskResult:
    """Dispatch a single sub-agent task.

    Args:
        task_fn: Async callable to execute.
        task_id: Optional identifier (auto-generated if omitted).
        kwargs: Keyword arguments for task_fn.
        timeout_s: Per-task timeout override.

    Returns:
        TaskResult with outcome.
    """
    tid = task_id or uuid.uuid4().hex[:12]
    effective_timeout = timeout_s or self._timeout_s
    kw = kwargs or {}
    start = time.monotonic()

    async with self._semaphore:
      logger.debug("Sub-agent %s: RUNNING", tid)
      try:
        result = await asyncio.wait_for(
          task_fn(**kw),
          timeout=effective_timeout,
        )
        elapsed = time.monotonic() - start
        task_result = TaskResult(
          task_id=tid,
          state=TaskState.DONE,
          result=result,
          elapsed_s=elapsed,
        )
        logger.debug("Sub-agent %s: DONE (%.2fs)", tid, elapsed)
      except TimeoutError:
        elapsed = time.monotonic() - start
        task_result = TaskResult(
          task_id=tid,
          state=TaskState.FAILED,
          error=f"Timeout after {effective_timeout:.1f}s",
          elapsed_s=elapsed,
        )
        logger.warning("Sub-agent %s: TIMEOUT (%.2fs)", tid, elapsed)
      except Exception as exc:
        elapsed = time.monotonic() - start
        task_result = TaskResult(
          task_id=tid,
          state=TaskState.FAILED,
          error=str(exc),
          elapsed_s=elapsed,
        )
        logger.warning("Sub-agent %s: FAILED (%s)", tid, exc)

    self._results[tid] = task_result
    return task_result

  async def dispatch_batch(
    self,
    tasks: list[tuple[str, Callable[..., Awaitable[Any]], dict[str, Any]]],
    *,
    timeout_s: float | None = None,
  ) -> list[TaskResult]:
    """Dispatch multiple sub-agent tasks in parallel.

    Args:
        tasks: List of (task_id, task_fn, kwargs) tuples.
        timeout_s: Per-task timeout override for all tasks.

    Returns:
        List of TaskResult in input order.
    """
    coros = [
      self.dispatch(
        fn,
        task_id=tid,
        kwargs=kw,
        timeout_s=timeout_s,
      )
      for tid, fn, kw in tasks
    ]
    return list(await asyncio.gather(*coros))

  def summary(self) -> dict[str, Any]:
    """Return an aggregate summary of all dispatched tasks."""
    done = sum(1 for r in self._results.values() if r.state == TaskState.DONE)
    failed = sum(1 for r in self._results.values() if r.state == TaskState.FAILED)
    total_elapsed = sum(r.elapsed_s for r in self._results.values())
    return {
      "total_tasks": len(self._results),
      "done": done,
      "failed": failed,
      "success_rate": done / max(len(self._results), 1),
      "total_elapsed_s": round(total_elapsed, 2),
      "max_concurrency": self._max_concurrency,
    }

  def clear(self) -> None:
    """Clear completed task results."""
    self._results.clear()
