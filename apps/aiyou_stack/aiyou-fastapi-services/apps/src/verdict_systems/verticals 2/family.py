"""
Verdict Systems - Family Vertical
Family scheduling, parental oversight, and accountability

Features:
- Chore assignment and tracking
- Allowance tied to task completion
- Screen time management
- Family goal tracking
- Mandatory check-ins
- Encouraging messages
"""

from datetime import datetime

from pydantic import BaseModel, Field

from ..core.enums import VerticalType
from ..models.task import TaskCreate


class FamilyTask(TaskCreate):
    """Family-specific task (chores, homework, family goals)"""

    vertical: VerticalType = Field(default=VerticalType.FAMILY, const=True)

    # Family fields
    task_category: str = Field(..., description="chore|homework|goal|checkin|screen_time")
    allowance_value: float = Field(default=0.0, description="Allowance earned for completion")
    requires_photo_proof: bool = Field(default=False)
    encouragement_message: str | None = Field(None, max_length=500)

    # Parental oversight
    parent_id: str = Field(..., description="Parent/guardian ID")
    requires_approval: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Clean your room",
                "description": "Make bed, vacuum, organize desk",
                "deadline": "2025-11-17T18:00:00Z",
                "estimated_duration_minutes": 30,
                "user_id": "child_001",
                "parent_id": "parent_001",
                "task_category": "chore",
                "allowance_value": 5.00,
                "requires_photo_proof": True,
                "encouragement_message": "Great job keeping your space clean! 🌟",
            }
        }


class FamilyCheckIn(BaseModel):
    """Mandatory family check-in (e.g., daily parent call for seniors)"""

    checkin_id: str
    user_id: str
    family_member_id: str
    checkin_type: str = Field(..., description="daily_call|weekly_video|emergency")
    due_at: datetime
    completed_at: datetime | None = None
    duration_seconds: int | None = None
    notes: str | None = None


class ScreenTimeControl(BaseModel):
    """Screen time management and limits"""

    user_id: str
    daily_limit_minutes: int = Field(default=120, description="Daily screen time limit")
    blocked_during: list[dict[str, str]] = Field(
        default_factory=list, description="Time ranges when screens are blocked"
    )
    earn_time_by_tasks: bool = Field(
        default=True, description="Earn additional screen time by completing tasks"
    )
    minutes_per_task: int = Field(default=15, description="Extra minutes earned per task")


class FamilyGoal(BaseModel):
    """Shared family goal tracking"""

    goal_id: str
    family_id: str
    title: str
    target_date: datetime
    participants: list[str] = Field(..., description="Family member IDs")
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    reward: str | None = None
