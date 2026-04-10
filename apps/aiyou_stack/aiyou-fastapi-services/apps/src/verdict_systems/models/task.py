"""
Verdict Systems - Task Models
Core task representation and urgency calculation
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from ..enums import (
    CompletionMethod,
    LockoutMode,
    PriorityLevel,
    TaskStatus,
    UrgencyLevel,
    VerticalType,
)


class TaskCompletion(BaseModel):
    """Record of task completion"""

    completed_at: datetime
    method: CompletionMethod
    proof_url: str | None = None
    verified_by: str | None = None  # Admin user ID
    notes: str | None = None


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    deadline: datetime | None = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    vertical: VerticalType = VerticalType.FAMILY

    # Metadata for vertical-specific fields
    # e.g. {"subject": "Math", "teacher": "Mr. Smith"} for School
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Lockout configuration
    lockout_mode: LockoutMode = LockoutMode.NONE
    blocked_apps: list[str] = Field(default_factory=list)

    # Completion requirements
    completion_method: CompletionMethod = CompletionMethod.CHECKBOX

    # User assignment
    assigned_to_id: str
    assigned_by_id: str | None = None  # Admin who assigned it


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    priority: PriorityLevel | None = None
    status: TaskStatus | None = None
    lockout_mode: LockoutMode | None = None
    completion_method: CompletionMethod | None = None
    metadata: dict[str, Any] | None = None


class Task(TaskBase):
    """
    Core task model with urgency tile calculation
    The Schiznit engine uses this model to orchestrate executive function
    across all verticals. Each task automatically calculates its urgency.
    """

    id: str
    created_at: datetime
    updated_at: datetime
    status: TaskStatus = TaskStatus.PENDING
    completion: TaskCompletion | None = None

    # Computed fields
    urgency: UrgencyLevel = UrgencyLevel.GREEN

    @property
    def is_locked_out(self) -> bool:
        """Check if this task is currently causing a lockout"""
        return (
            self.urgency == UrgencyLevel.CRITICAL
            and self.status not in [TaskStatus.COMPLETED, TaskStatus.ARCHIVED]
            and self.lockout_mode != LockoutMode.NONE
        )

    def calculate_urgency(self) -> UrgencyLevel:
        """
        Calculate current urgency tile based on deadline and priority.
        Logic:
        - Critical: Past deadline OR < 1 hour (if Urgent priority)
        - Red: < 6 hours remaining
        - Yellow: < 24 hours remaining
        - Green: > 24 hours remaining or No Deadline
        """
        if self.status in [TaskStatus.COMPLETED, TaskStatus.ARCHIVED]:
            return UrgencyLevel.GREEN

        if not self.deadline:
            # Urgent priority tasks without deadline decay to yellow faster
            if self.priority == PriorityLevel.URGENT:
                # TODO: Logic for creation-time based decay?
                # For now, default to Yellow for urgent tasks without deadlines
                return UrgencyLevel.YELLOW
            return UrgencyLevel.GREEN

        now = datetime.now(UTC)
        # Ensure deadline is aware
        deadline = self.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=UTC)

        time_remaining = deadline - now

        if time_remaining.total_seconds() < 0:
            return UrgencyLevel.CRITICAL

        hours_remaining = time_remaining.total_seconds() / 3600

        if hours_remaining < 1:
            if self.priority == PriorityLevel.URGENT:
                return UrgencyLevel.CRITICAL
            return UrgencyLevel.RED

        if hours_remaining < 6:
            return UrgencyLevel.RED

        if hours_remaining < 24:
            return UrgencyLevel.YELLOW

        return UrgencyLevel.GREEN

    def update_urgency(self):
        """Update the stored urgency based on calculation"""
        self.urgency = self.calculate_urgency()
