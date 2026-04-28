# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Verdict Systems - Workplace Vertical
Employer-controlled focus, workflow enforcement, productivity tracking

Features:
- Enforced focus sessions
- Meeting preparation tasks
- Project deadline management
- Team productivity visibility (no micromanagement)
- Professional tool training
"""

from pydantic import BaseModel

from ..enums import VerticalType
from ..models.task import TaskCreate


class WorkplaceTaskMetadata(BaseModel):
    project_id: str
    team_id: str | None = None
    billable_hours: float = 0.0
    client_id: str | None = None
    focus_session_required: bool = False
    focus_duration_minutes: int = 0


class WorkplaceTaskCreate(TaskCreate):
    vertical: VerticalType = VerticalType.WORKPLACE
    work_metadata: WorkplaceTaskMetadata

    def to_task_create(self) -> TaskCreate:
        data = self.model_dump(exclude={"work_metadata"})
        data["metadata"] = self.work_metadata.model_dump()
        return TaskCreate(**data)
