# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Verdict Systems - Family Vertical
Family scheduling, parental oversight, and accountability

Features:
- Chore assignment and tracking
- Allowance tied to task completion
- Screen time management
- Family goal tracking
- Mandatory check-ins
- Encouraging messages
"""

from pydantic import BaseModel

from ..enums import VerticalType
from ..models.task import TaskCreate


class FamilyChoreMetadata(BaseModel):
    allowance_value: float = 0.0
    requires_photo_proof: bool = False
    is_recurring: bool = False
    recurrence_pattern: str | None = None  # cron-like or simple
    assigned_by_parent_id: str


class FamilyTaskCreate(TaskCreate):
    vertical: VerticalType = VerticalType.FAMILY
    family_metadata: FamilyChoreMetadata

    def to_task_create(self) -> TaskCreate:
        data = self.model_dump(exclude={"family_metadata"})
        data["metadata"] = self.family_metadata.model_dump()
        return TaskCreate(**data)
