"""
Verdict Systems - Workplace Vertical
Employer-controlled focus, workflow enforcement, productivity tracking

Features:
- Enforced focus sessions
- Meeting preparation tasks
- Project deadline management
- Team productivity visibility (no micromanagement)
- Professional tool training
"""

from datetime import datetime

from pydantic import BaseModel, Field

from ..core.enums import LockoutMode, VerticalType
from ..models.task import TaskCreate


class WorkTask(TaskCreate):
    """Workplace task with productivity features"""

    vertical: VerticalType = Field(default=VerticalType.WORKPLACE, const=True)

    # Work fields
    project_id: str | None = None
    department: str | None = None
    manager_id: str | None = None
    billable: bool = Field(default=False)
    estimated_hours: float = Field(default=1.0)

    # Focus enforcement
    focus_mode: LockoutMode = Field(default=LockoutMode.MODERATE)
    blocked_apps: list[str] = Field(
        default_factory=lambda: [
            "facebook",
            "twitter",
            "instagram",
            "youtube",
            "reddit",
        ]
    )


class FocusSession(BaseModel):
    """Deep work focus session"""

    session_id: str
    user_id: str
    task_id: str | None = None
    duration_minutes: int = Field(..., ge=15, le=240)
    started_at: datetime
    ended_at: datetime | None = None
    interruptions: int = Field(default=0)
    productivity_score: float | None = Field(None, ge=0, le=100)


class TeamDashboard(BaseModel):
    """Team-level productivity dashboard (aggregate, not individual tracking)"""

    team_id: str
    date: datetime
    total_tasks_completed: int
    avg_completion_time_hours: float
    on_time_percentage: float
    focus_hours_total: float
