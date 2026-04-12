"""
Verdict Systems - Schiznit Engine
Core executive function orchestration layer

The Schiznit engine is the heart of Verdict Systems, managing task
orchestration, urgency escalation, and lockout enforcement across
all verticals and devices.
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

from ..core.enums import (
    LockoutMode,
    NotificationType,
    TaskStatus,
    UrgencyLevel,
    VerticalType,
)
from ..models.task import Task, TaskCompletion


class SchiznitsEngine:
    """
    Executive Function Orchestration Engine

    Core responsibilities:
    1. Task lifecycle management
    2. Urgency escalation (green → yellow → red → critical)
    3. Lockout protocol enforcement
    4. Multi-device state synchronization
    5. Notification scheduling and delivery
    6. Vertical-specific rule application
    """

    def __init__(self):
        # In-memory task store (in production, use PostgreSQL + Redis)
        self.tasks: dict[str, Task] = {}
        self.user_tasks: dict[str, set[str]] = defaultdict(set)
        self.device_states: dict[str, dict] = {}
        self.active_lockouts: dict[str, list[str]] = defaultdict(list)

    # ========================================================================
    # Task Management
    # ========================================================================

    async def create_task(self, task: Task) -> Task:
        """
        Create and register a new task

        Automatically:
        - Calculates initial urgency level
        - Schedules urgency escalation checks
        - Registers with user's task list
        - Triggers initial notifications if needed
        """
        task.urgency_level = task.calculate_urgency()
        task.update_status()

        self.tasks[task.id] = task
        self.user_tasks[task.user_id].add(task.id)

        # Schedule urgency monitoring
        asyncio.create_task(self._monitor_task_urgency(task.id))

        return task

    async def get_task(self, task_id: str) -> Task | None:
        """Retrieve a task by ID"""
        return self.tasks.get(task_id)

    async def get_user_tasks(
        self,
        user_id: str,
        status: TaskStatus | None = None,
        urgency: UrgencyLevel | None = None,
        vertical: VerticalType | None = None,
    ) -> list[Task]:
        """
        Get all tasks for a user with optional filters

        This is the primary view for user dashboards, showing:
        - Current urgency tiles
        - Active lockouts
        - Upcoming deadlines
        """
        task_ids = self.user_tasks.get(user_id, set())
        tasks = [self.tasks[tid] for tid in task_ids if tid in self.tasks]

        # Update all task statuses and urgency
        for task in tasks:
            task.update_status()

        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if urgency:
            tasks = [t for t in tasks if t.urgency_level == urgency]
        if vertical:
            tasks = [t for t in tasks if t.vertical == vertical]

        # Sort by urgency (critical first) then deadline
        urgency_order = {
            UrgencyLevel.CRITICAL: 0,
            UrgencyLevel.RED: 1,
            UrgencyLevel.YELLOW: 2,
            UrgencyLevel.GREEN: 3,
        }

        tasks.sort(key=lambda t: (urgency_order.get(t.urgency_level, 99), t.deadline))

        return tasks

    async def complete_task(self, task_id: str, completion: TaskCompletion) -> Task:
        """
        Mark a task as completed

        Handles:
        - Status update
        - Lockout release
        - Approval workflows (if required)
        - Notifications to admins/parents/teachers
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Check if approval is required
        if task.requires_approval and completion.completion_method not in [
            CompletionMethod.TEACHER_APPROVED,
            CompletionMethod.PARENT_APPROVED,
            CompletionMethod.OVERRIDE,
        ]:
            # Queue for approval instead of immediate completion
            task.status = TaskStatus.BLOCKED
            task.metadata["pending_approval"] = {
                "submitted_at": datetime.utcnow().isoformat(),
                "submitted_by": completion.completed_by,
                "notes": completion.notes,
                "submission_url": completion.submission_url,
            }
            return task

        # Complete the task
        task.status = TaskStatus.COMPLETED
        task.completion_method = completion.completion_method
        task.completed_at = datetime.utcnow()
        task.metadata["completion"] = {
            "completed_by": completion.completed_by,
            "notes": completion.notes,
            "submission_url": completion.submission_url,
            **completion.metadata,
        }

        # Release lockout if active
        if task.user_id in self.active_lockouts:
            if task_id in self.active_lockouts[task.user_id]:
                self.active_lockouts[task.user_id].remove(task_id)

        return task

    # ========================================================================
    # Urgency Escalation
    # ========================================================================

    async def _monitor_task_urgency(self, task_id: str):
        """
        Background monitor for task urgency escalation

        Continuously checks task urgency and triggers notifications
        when urgency level changes (green → yellow → red → critical)
        """
        while True:
            task = self.tasks.get(task_id)

            if not task or task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                break

            previous_urgency = task.urgency_level
            task.update_status()
            current_urgency = task.urgency_level

            # Urgency level changed - send notifications
            if previous_urgency != current_urgency:
                await self._send_urgency_notification(task, current_urgency)

            # Check lockout threshold
            if task.should_lockout():
                await self._activate_lockout(task)

            # Check interval based on urgency
            check_intervals = {
                UrgencyLevel.GREEN: 3600,  # Check hourly
                UrgencyLevel.YELLOW: 600,  # Check every 10 minutes
                UrgencyLevel.RED: 60,  # Check every minute
                UrgencyLevel.CRITICAL: 10,  # Check every 10 seconds
            }

            await asyncio.sleep(check_intervals.get(current_urgency, 600))

    async def _send_urgency_notification(self, task: Task, urgency: UrgencyLevel):
        """
        Send notification when urgency escalates

        Notification types:
        - GREEN → YELLOW: Gentle reminder
        - YELLOW → RED: Urgent warning
        - RED → CRITICAL: Lockout imminent
        - CRITICAL: Lockout active
        """
        notification_types = {
            UrgencyLevel.YELLOW: NotificationType.REMINDER,
            UrgencyLevel.RED: NotificationType.DEADLINE_WARNING,
            UrgencyLevel.CRITICAL: NotificationType.LOCKOUT_IMMINENT,
        }

        notification_type = notification_types.get(urgency)

        if notification_type:
            # TODO: Implement actual notification delivery
            # For now, just log
            print(f"[NOTIFICATION] {notification_type.value} for task {task.id}: {task.title}")

    # ========================================================================
    # Lockout Protocol
    # ========================================================================

    async def _activate_lockout(self, task: Task):
        """
        Activate lockout protocol for overdue task

        Lockout blocks specified apps and enforces focus until
        task completion. Includes override capabilities for
        admins/parents/emergencies.
        """
        if task.id in self.active_lockouts.get(task.user_id, []):
            return  # Already locked out

        self.active_lockouts[task.user_id].append(task.id)

        # TODO: Implement actual device lockout via MDM/device APIs
        print(f"[LOCKOUT ACTIVATED] User {task.user_id}, Task {task.id}")
        print(f"  Blocked apps: {', '.join(task.blocked_apps)}")

        # Send lockout notification
        await self._send_lockout_notification(task)

    async def _send_lockout_notification(self, task: Task):
        """Send notification that lockout is now active"""
        # TODO: Implement notification delivery
        print(f"[NOTIFICATION] {NotificationType.LOCKOUT_ACTIVE.value} for task {task.id}")

    async def get_lockout_status(self, user_id: str, device_id: str) -> dict:
        """
        Get current lockout status for a user's device

        Returns:
        - Active lockout mode
        - Blocked apps
        - Tasks causing lockout
        - Override available
        """
        locked_task_ids = self.active_lockouts.get(user_id, [])

        if not locked_task_ids:
            return {
                "lockout_active": False,
                "lockout_mode": LockoutMode.NONE,
                "blocked_apps": [],
                "locked_tasks": [],
            }

        # Get all locked tasks
        locked_tasks = [self.tasks[tid] for tid in locked_task_ids if tid in self.tasks]

        # Aggregate blocked apps
        all_blocked_apps = set()
        for task in locked_tasks:
            all_blocked_apps.update(task.blocked_apps)

        # Determine lockout mode (strictest wins)
        lockout_mode = LockoutMode.STRICT  # Default for any lockout

        return {
            "lockout_active": True,
            "lockout_mode": lockout_mode,
            "blocked_apps": list(all_blocked_apps),
            "locked_tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "deadline": task.deadline,
                    "urgency": task.urgency_level,
                }
                for task in locked_tasks
            ],
        }

    async def override_lockout(
        self, user_id: str, admin_id: str, reason: str, duration_minutes: int = 60
    ) -> dict:
        """
        Admin override to temporarily disable lockout

        Use cases:
        - Emergency situations
        - Parent discretion
        - Teacher accommodation
        - Medical necessity
        """
        # Clear active lockouts temporarily
        locked_tasks = self.active_lockouts.get(user_id, []).copy()
        self.active_lockouts[user_id] = []

        # TODO: Schedule re-activation after duration
        # TODO: Log override event for audit trail

        return {
            "override_active": True,
            "admin_id": admin_id,
            "reason": reason,
            "duration_minutes": duration_minutes,
            "expires_at": (datetime.utcnow() + timedelta(minutes=duration_minutes)).isoformat(),
            "suspended_tasks": locked_tasks,
        }

    # ========================================================================
    # Dashboard & Analytics
    # ========================================================================

    async def get_dashboard(self, user_id: str) -> dict:
        """
        Get comprehensive dashboard for user

        Returns:
        - Urgency tile summary (count by color)
        - Next 5 deadlines
        - Lockout status
        - Completion stats
        """
        tasks = await self.get_user_tasks(user_id)

        # Count by urgency
        urgency_counts = defaultdict(int)
        for task in tasks:
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                urgency_counts[task.urgency_level] += 1

        # Get next deadlines
        pending_tasks = [
            t for t in tasks if t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
        ]
        next_deadlines = sorted(pending_tasks, key=lambda t: t.deadline)[:5]

        # Completion stats
        completed_today = [
            t
            for t in tasks
            if t.status == TaskStatus.COMPLETED
            and t.completed_at
            and t.completed_at.date() == datetime.utcnow().date()
        ]

        return {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "urgency_summary": {
                "green": urgency_counts.get(UrgencyLevel.GREEN, 0),
                "yellow": urgency_counts.get(UrgencyLevel.YELLOW, 0),
                "red": urgency_counts.get(UrgencyLevel.RED, 0),
                "critical": urgency_counts.get(UrgencyLevel.CRITICAL, 0),
            },
            "next_deadlines": [
                {
                    "id": t.id,
                    "title": t.title,
                    "deadline": t.deadline,
                    "urgency": t.urgency_level,
                    "time_remaining": str(t.time_until_deadline()),
                }
                for t in next_deadlines
            ],
            "lockout_status": await self.get_lockout_status(user_id, "default"),
            "completed_today": len(completed_today),
            "total_active_tasks": len(pending_tasks),
        }


# Global engine instance (in production, use dependency injection)
schiznit_engine = SchiznitsEngine()
