# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cron Scheduler — File-backed task scheduling with jitter and lock ownership.

Synthesized from Claude Code v2.1.91 production patterns:
  - cronScheduler.ts: CronScheduler factory, lock ownership, jittered firing
  - cronScheduler.ts L40-44: CHECK_INTERVAL_MS, FILE_STABILITY_MS, LOCK_PROBE_INTERVAL_MS
  - cronScheduler.ts L53-60: isRecurringTaskAged — recurring max-age eviction
  - cronTasks.ts: readCronTasks, markCronTasksFired, removeCronTasks, findMissedTasks
  - cronTasksLock.ts: tryAcquireSchedulerLock, releaseSchedulerLock

Adds asyncio-native scheduling, type-safe CronTask dataclass, and proper
async file watching that CC's chokidar-based approach handles synchronously.

Usage:
    from cron_scheduler import CronScheduler, CronTask, JitterConfig

    scheduler = CronScheduler(
        tasks_dir=".claude",
        on_fire=lambda prompt: print(f"Task fired: {prompt}"),
    )
    scheduler.start()
    # ...
    scheduler.stop()
"""

from cron_scheduler.core import (
  CronScheduler,
  CronTask,
  JitterConfig,
  SchedulerLock,
  TaskState,
  is_recurring_task_aged,
)

__all__ = [
  "CronScheduler",
  "CronTask",
  "JitterConfig",
  "SchedulerLock",
  "TaskState",
  "is_recurring_task_aged",
]
