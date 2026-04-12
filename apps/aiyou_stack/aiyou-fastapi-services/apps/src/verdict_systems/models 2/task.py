"""
Verdict Systems - Task Models
Core task representation and urgency calculation
"""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from ..core.enums import (
    CompletionMethod,
    PriorityLevel,
    TaskStatus,
    UrgencyLevel,
    VerticalType,
)


class Task(BaseModel):
    """
    Core task model with urgency tile calculation

    The Schiznit engine uses this model to orchestrate executive function
    across all verticals. Each task automatically calculates its urgency
    level based on deadline proximity and priority.
    """

    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=2000, description="Detailed description")

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: datetime = Field(..., description="Task deadline (UTC)")
    estimated_duration_minutes: int = Field(
        default=30, ge=1, description="Estimated completion time"
    )

    # Urgency calculation
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Base priority")
    urgency_level: UrgencyLevel | None = Field(None, description="Auto-calculated urgency tile")

    # Status
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    completion_method: CompletionMethod | None = Field(None)
    completed_at: datetime | None = Field(None)

    # Assignment and ownership
    user_id: str = Field(..., description="Assigned user ID")
    vertical: VerticalType = Field(..., description="Which vertical this task belongs to")
    group_id: str | None = Field(None, description="Group/family/class/team ID")

    # Lockout configuration
    enable_lockout: bool = Field(default=False, description="Enable app lockout when overdue")
    lockout_grace_minutes: int = Field(default=15, ge=0, description="Grace period before lockout")
    blocked_apps: list[str] = Field(
        default_factory=list, description="Apps to block during lockout"
    )

    # Assistance
    ai_tutor_enabled: bool = Field(default=False, description="Enable AI assistance")
    requires_approval: bool = Field(
        default=False, description="Requires admin/parent/teacher approval"
    )
    approver_id: str | None = Field(None, description="Who needs to approve completion")

    # Metadata
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Notifications sent
    notifications_sent: list[str] = Field(default_factory=list, description="Notification IDs sent")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "task_20251117_001",
                "title": "Complete Math Assignment Ch. 5",
                "description": "Finish problems 1-20, show all work",
                "deadline": "2025-11-18T14:00:00Z",
                "estimated_duration_minutes": 45,
                "priority": 4,
                "user_id": "student_12345",
                "vertical": "school",
                "group_id": "class_math_101",
                "enable_lockout": True,
                "lockout_grace_minutes": 30,
                "blocked_apps": ["instagram", "tiktok", "youtube"],
                "ai_tutor_enabled": True,
                "requires_approval": True,
                "approver_id": "teacher_67890",
                "tags": ["homework", "math", "priority"],
            }
        }

    def calculate_urgency(self) -> UrgencyLevel:
        """
        Calculate urgency tile color based on time to deadline

        Logic:
        - GREEN: >24 hours remaining OR priority <= LOW
        - YELLOW: 6-24 hours remaining OR priority = HIGH
        - RED: 1-6 hours remaining OR priority = HIGHEST
        - CRITICAL: Past deadline OR priority = CRITICAL
        """
        now = datetime.utcnow()
        time_remaining = self.deadline - now
        hours_remaining = time_remaining.total_seconds() / 3600

        # Past deadline
        if hours_remaining < 0:
            return UrgencyLevel.CRITICAL

        # Priority override for critical tasks
        if self.priority == PriorityLevel.CRITICAL:
            return UrgencyLevel.CRITICAL

        # Calculate based on time + priority
        if hours_remaining <= 1 or self.priority == PriorityLevel.HIGHEST:
            return UrgencyLevel.RED
        elif (
            hours_remaining <= 6
            or self.priority == PriorityLevel.HIGH
            or hours_remaining <= 24
            and self.priority >= PriorityLevel.MEDIUM
        ):
            return UrgencyLevel.YELLOW
        else:
            return UrgencyLevel.GREEN

    def should_lockout(self) -> bool:
        """
        Determine if lockout should be active

        Returns True if:
        - Lockout is enabled for this task
        - Task is overdue (past deadline + grace period)
        - Task is not completed
        """
        if not self.enable_lockout:
            return False

        if self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return False

        now = datetime.utcnow()
        lockout_threshold = self.deadline + timedelta(minutes=self.lockout_grace_minutes)

        return now > lockout_threshold

    def time_until_deadline(self) -> timedelta:
        """Calculate time remaining until deadline"""
        return self.deadline - datetime.utcnow()

    def is_overdue(self) -> bool:
        """Check if task is past deadline"""
        return datetime.utcnow() > self.deadline

    def update_status(self):
        """Auto-update status based on deadline"""
        if self.status == TaskStatus.COMPLETED:
            return

        if self.is_overdue():
            self.status = TaskStatus.OVERDUE

        # Update urgency level
        self.urgency_level = self.calculate_urgency()


class TaskCreate(BaseModel):
    """Request model for creating tasks"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    deadline: datetime
    estimated_duration_minutes: int = Field(default=30, ge=1)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    user_id: str
    vertical: VerticalType
    group_id: str | None = None
    enable_lockout: bool = Field(default=False)
    lockout_grace_minutes: int = Field(default=15, ge=0)
    blocked_apps: list[str] = Field(default_factory=list)
    ai_tutor_enabled: bool = Field(default=False)
    requires_approval: bool = Field(default=False)
    approver_id: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    """Request model for updating tasks"""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    deadline: datetime | None = None
    estimated_duration_minutes: int | None = Field(None, ge=1)
    priority: PriorityLevel | None = None
    status: TaskStatus | None = None
    enable_lockout: bool | None = None
    lockout_grace_minutes: int | None = Field(None, ge=0)
    blocked_apps: list[str] | None = None
    ai_tutor_enabled: bool | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class TaskCompletion(BaseModel):
    """Request model for marking task complete"""

    completion_method: CompletionMethod
    completed_by: str = Field(..., description="User ID who marked complete")
    notes: str | None = Field(None, max_length=1000)
    submission_url: str | None = Field(None, description="URL to submission (for school tasks)")
    metadata: dict[str, Any] = Field(default_factory=dict)
