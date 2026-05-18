# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""SleepTool + ScheduleCronTool — Ported from Claude Code (Notebook 3 gap).

SleepTool: Pauses agent execution for a specified duration.
ScheduleCronTool: Registers a cron-like schedule for deferred task execution.

Both integrate with the shadowtag_os gate system for audit logging.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

# Maximum sleep duration to prevent runaway waits
MAX_SLEEP_SECONDS = 300  # 5 minutes


@dataclass
class SleepResult:
    """Result from a SleepTool invocation.

    Attributes:
        requested_seconds: Requested sleep duration.
        actual_seconds: Actual time slept.
        reason: Why the sleep was requested.
        truncated: Whether the sleep was capped at MAX_SLEEP_SECONDS.
    """

    requested_seconds: float
    actual_seconds: float
    reason: str = ""
    truncated: bool = False


async def sleep_tool(seconds: float, reason: str = "agent-requested pause") -> SleepResult:
    """Pause execution for the specified duration.

    Args:
        seconds: Duration to sleep in seconds.
        reason: Human-readable reason for the pause.

    Returns:
        SleepResult with actual duration.
    """
    truncated = False
    actual = seconds

    if seconds <= 0:
        return SleepResult(
            requested_seconds=seconds,
            actual_seconds=0,
            reason=reason,
        )

    if seconds > MAX_SLEEP_SECONDS:
        logger.warning(
            "Sleep request of %.1fs truncated to %ds",
            seconds,
            MAX_SLEEP_SECONDS,
        )
        actual = MAX_SLEEP_SECONDS
        truncated = True

    logger.info("SleepTool: sleeping %.1fs — %s", actual, reason)
    await asyncio.sleep(actual)

    return SleepResult(
        requested_seconds=seconds,
        actual_seconds=actual,
        reason=reason,
        truncated=truncated,
    )


@dataclass
class CronSchedule:
    """A registered cron schedule.

    Attributes:
        schedule_id: Unique identifier for this schedule.
        cron_expr: Cron expression (e.g., "0 */6 * * *").
        task_name: Name of the task to execute.
        handler: Cloud Tasks handler path.
        created_at: When the schedule was registered.
        enabled: Whether the schedule is active.
    """

    schedule_id: str
    cron_expr: str
    task_name: str
    handler: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True


# In-memory schedule registry (production: Cloud Scheduler)
_schedules: dict[str, CronSchedule] = {}


def register_cron(
    schedule_id: str,
    cron_expr: str,
    task_name: str,
    handler: str = "",
) -> CronSchedule:
    """Register a new cron schedule.

    Args:
        schedule_id: Unique ID for this schedule.
        cron_expr: Standard cron expression.
        task_name: Human-readable task name.
        handler: Cloud Tasks handler path for production.

    Returns:
        The created CronSchedule.
    """
    schedule = CronSchedule(
        schedule_id=schedule_id,
        cron_expr=cron_expr,
        task_name=task_name,
        handler=handler,
    )
    _schedules[schedule_id] = schedule
    logger.info(
        "ScheduleCronTool: registered '%s' (%s) → %s",
        task_name,
        cron_expr,
        handler or "local",
    )
    return schedule


def list_schedules() -> list[CronSchedule]:
    """List all registered cron schedules."""
    return list(_schedules.values())


def remove_schedule(schedule_id: str) -> bool:
    """Remove a cron schedule by ID."""
    if schedule_id in _schedules:
        del _schedules[schedule_id]
        logger.info("ScheduleCronTool: removed schedule %s", schedule_id)
        return True
    return False
