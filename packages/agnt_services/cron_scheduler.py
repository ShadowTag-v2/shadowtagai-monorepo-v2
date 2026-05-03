# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cron Scheduler — File-backed and session-scoped task scheduling.

Ported from src/utils/cronScheduler.ts (566 lines).

Non-React scheduler core for scheduled_tasks.json. Supports:
  - File-backed tasks (persistent across sessions, chokidar-watched)
  - Session-scoped tasks (process-private, in-memory only)
  - Per-project scheduler lock (prevents double-fire across sessions)
  - Missed task detection on startup
  - Jittered scheduling to avoid :00 wall-clock thundering herd
  - Age-based recurring task expiry
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

CHECK_INTERVAL_S = 1.0
LOCK_PROBE_INTERVAL_S = 5.0


@dataclass(slots=True)
class CronTask:
    """A single scheduled task definition."""

    id: str
    cron: str
    prompt: str
    created_at: float  # epoch ms
    recurring: bool = False
    permanent: bool = False
    last_fired_at: float | None = None
    durable: bool = True  # False = session-only

    @property
    def created_at_s(self) -> float:
        return self.created_at / 1000.0


@dataclass(slots=True)
class CronJitterConfig:
    """Configuration for scheduling jitter."""

    base_jitter_ms: int = 0
    max_jitter_ms: int = 60_000
    recurring_max_age_ms: int = 0  # 0 = unlimited


DEFAULT_JITTER_CONFIG = CronJitterConfig()


def is_recurring_task_aged(
    task: CronTask,
    now_ms: float,
    max_age_ms: int,
) -> bool:
    """Check if a recurring task has exceeded its maximum age."""
    if max_age_ms == 0:
        return False
    return bool(task.recurring and not task.permanent and now_ms - task.created_at >= max_age_ms)


CronSchedulerCallback = Callable[[str], None]
CronTaskCallback = Callable[[CronTask], None]
MissedCallback = Callable[[list[CronTask]], None]
FilterFn = Callable[[CronTask], bool]


@dataclass
class CronSchedulerOptions:
    """Configuration for the cron scheduler."""

    on_fire: CronSchedulerCallback
    is_loading: Callable[[], bool] = lambda: False
    assistant_mode: bool = False
    on_fire_task: CronTaskCallback | None = None
    on_missed: MissedCallback | None = None
    dir: str | None = None
    lock_identity: str | None = None
    get_jitter_config: Callable[[], CronJitterConfig] | None = None
    is_killed: Callable[[], bool] | None = None
    filter: FilterFn | None = None


class CronScheduler:
    """Non-React cron scheduler for scheduled_tasks.json.

    Lifecycle: start() → poll/watch → fire → stop()
    """

    def __init__(self, options: CronSchedulerOptions) -> None:
        self._options = options
        self._tasks: list[CronTask] = []
        self._next_fire_at: dict[str, float] = {}
        self._missed_asked: set[str] = set()
        self._in_flight: set[str] = set()
        self._stopped = False
        self._is_owner = False
        self._check_task: asyncio.Task[None] | None = None
        self._enabled = False

    def start(self) -> None:
        """Start the scheduler. Begins polling for enabled state."""
        self._stopped = False
        if self._options.dir is not None or self._options.assistant_mode:
            self._enabled = True
        if self._enabled:
            self._start_check_loop()

    def stop(self) -> None:
        """Stop the scheduler and release all resources."""
        self._stopped = True
        if self._check_task and not self._check_task.done():
            self._check_task.cancel()
            self._check_task = None
        self._tasks.clear()
        self._next_fire_at.clear()

    def get_next_fire_time(self) -> float | None:
        """Epoch ms of the soonest scheduled fire, or None if nothing pending."""
        if not self._next_fire_at:
            return None
        min_val = min(self._next_fire_at.values(), default=float("inf"))
        return None if min_val == float("inf") else min_val

    def add_task(self, task: CronTask) -> None:
        """Add a task to the scheduler."""
        self._tasks.append(task)
        if not self._enabled:
            self._enabled = True
            self._start_check_loop()

    def remove_task(self, task_id: str) -> None:
        """Remove a task by ID."""
        self._tasks = [t for t in self._tasks if t.id != task_id]
        self._next_fire_at.pop(task_id, None)
        self._in_flight.discard(task_id)

    def _start_check_loop(self) -> None:
        """Start the async check loop."""
        try:
            loop = asyncio.get_running_loop()
            self._check_task = loop.create_task(self._check_loop())
        except RuntimeError:
            logger.debug("No event loop — scheduler check loop deferred")

    async def _check_loop(self) -> None:
        """Main scheduler loop — runs check() every CHECK_INTERVAL_S."""
        while not self._stopped:
            try:
                self._check()
            except Exception:
                logger.exception("Scheduler check() error")
            await asyncio.sleep(CHECK_INTERVAL_S)

    def _check(self) -> None:
        """Single scheduler tick — fire eligible tasks."""
        if self._options.is_killed and self._options.is_killed():
            return
        if self._options.is_loading() and not self._options.assistant_mode:
            return

        now_ms = time.time() * 1000
        jitter_cfg = self._options.get_jitter_config() if self._options.get_jitter_config else DEFAULT_JITTER_CONFIG
        seen: set[str] = set()

        for task in list(self._tasks):
            if self._options.filter and not self._options.filter(task):
                continue
            seen.add(task.id)
            if task.id in self._in_flight:
                continue

            next_fire = self._next_fire_at.get(task.id)
            if next_fire is None:
                # First sight — schedule from anchor
                anchor = task.last_fired_at or task.created_at
                next_fire = anchor + jitter_cfg.max_jitter_ms
                self._next_fire_at[task.id] = next_fire

            if now_ms < next_fire:
                continue

            # Fire the task
            logger.debug("Firing task %s (recurring=%s)", task.id, task.recurring)
            if self._options.on_fire_task:
                self._options.on_fire_task(task)
            else:
                self._options.on_fire(task.prompt)

            aged = is_recurring_task_aged(task, now_ms, jitter_cfg.recurring_max_age_ms)

            if task.recurring and not aged:
                # Reschedule from now
                new_next = now_ms + jitter_cfg.max_jitter_ms
                self._next_fire_at[task.id] = new_next
            else:
                # One-shot or aged — remove
                self._in_flight.add(task.id)
                self._tasks = [t for t in self._tasks if t.id != task.id]
                self._next_fire_at.pop(task.id, None)
                self._in_flight.discard(task.id)

        # Evict stale schedule entries
        for task_id in list(self._next_fire_at):
            if task_id not in seen:
                del self._next_fire_at[task_id]


def build_missed_task_notification(missed: list[CronTask]) -> str:
    """Build notification text for missed one-shot tasks."""
    plural = len(missed) > 1
    header = (
        f"The following one-shot scheduled task{'s were' if plural else ' was'} "
        f"missed while the agent was not running. "
        f"{'They have' if plural else 'It has'} already been removed."
    )
    blocks = []
    for task in missed:
        blocks.append(f"[{task.cron}]\n```\n{task.prompt}\n```")
    return f"{header}\n\n" + "\n\n".join(blocks)


__all__ = [
    "CHECK_INTERVAL_S",
    "CronJitterConfig",
    "CronScheduler",
    "CronSchedulerCallback",
    "CronSchedulerOptions",
    "CronTask",
    "DEFAULT_JITTER_CONFIG",
    "build_missed_task_notification",
    "is_recurring_task_aged",
]
