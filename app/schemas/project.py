# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Project schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    memory_enabled: bool = True


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: str | None = None
    description: str | None = None
    memory_enabled: bool | None = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    id: int
    user_id: int
    memory_enabled: bool
    summary: str | None = None
    last_synthesis_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectStats(BaseModel):
    """Schema for project statistics."""

    project_id: int
    conversation_count: int
    message_count: int
    memory_count: int
    last_activity: datetime | None = None
