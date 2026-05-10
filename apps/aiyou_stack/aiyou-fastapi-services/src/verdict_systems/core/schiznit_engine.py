"""Verdict Systems - Schiznit Engine
Core executive function orchestration layer

The Schiznit engine is the heart of Verdict Systems, managing task
orchestration, urgency escalation, and lockout enforcement across
all verticals and devices.
"""

import logging
import uuid
from datetime import UTC, datetime

from ..enums import LockoutMode, TaskStatus, UrgencyLevel
from ..models.task import Task, TaskCreate

# Configure logger
logger = logging.getLogger(__name__)


class SchiznitsEngine:
    def __init__(self):
        # In-memory store for MVP; production uses DB
        self._tasks: dict[str, Task] = {}

    def create_task(self, task_create: TaskCreate) -> Task:
        """Create a new task and calculate initial urgency"""
        task_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        task = Task(id=task_id, created_at=now, updated_at=now, **task_create.model_dump())
        task.update_urgency()
        self._tasks[task_id] = task
        logger.info(f"Task created: {task.id} [{task.title}] Urgency: {task.urgency}")
        return task

    def get_task(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def get_user_tasks(self, user_id: str) -> list[Task]:
        # Refresh urgency on read for MVP
        tasks = [t for t in self._tasks.values() if t.assigned_to_id == user_id]
        for t in tasks:
            t.update_urgency()
        return sorted(
            tasks,
            key=lambda x: (
                # Sort by: Critical/Red > others, then deadline
                0
                if x.urgency == UrgencyLevel.CRITICAL
                else 1
                if x.urgency == UrgencyLevel.RED
                else 2
                if x.urgency == UrgencyLevel.YELLOW
                else 3,
                x.deadline or datetime.max.replace(tzinfo=UTC),
            ),
        )

    def update_task_status(self, task_id: str, status: TaskStatus) -> Task | None:
        task = self._tasks.get(task_id)
        if not task:
            return None

        task.status = status
        task.updated_at = datetime.now(UTC)
        task.update_urgency()
        # TODO: Trigger notifications or lift lockouts
        return task

    def get_active_lockouts(self, user_id: str) -> list[Task]:
        """Get list of tasks currently causing a lockout"""
        tasks = self.get_user_tasks(user_id)
        return [t for t in tasks if t.is_locked_out]

    def check_lockout_state(self, user_id: str) -> LockoutMode:
        """Determine the aggregate lockout level for the user"""
        active_lockouts = self.get_active_lockouts(user_id)

        if not active_lockouts:
            return LockoutMode.NONE

        # Determine strictness hierarchy
        modes = [t.lockout_mode for t in active_lockouts]

        if LockoutMode.EMERGENCY_ONLY in modes:
            return LockoutMode.EMERGENCY_ONLY
        if LockoutMode.STRICT in modes:
            return LockoutMode.STRICT
        if LockoutMode.MODERATE in modes:
            return LockoutMode.MODERATE
        if LockoutMode.SOFT in modes:
            return LockoutMode.SOFT

        return LockoutMode.NONE


# Singleton instance
schiznit_engine = SchiznitsEngine()
