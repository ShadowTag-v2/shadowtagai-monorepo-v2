# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Checkpoint database models."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text

from src.models.database import Base


class CheckpointStatus(StrEnum):
    """Checkpoint status enumeration."""

    ACTIVE = "active"
    RESTORED = "restored"
    EXPIRED = "expired"


class CheckpointType(StrEnum):
    """Checkpoint type enumeration."""

    AUTO = "auto"
    MANUAL = "manual"


class Checkpoint(Base):
    """Checkpoint database model."""

    __tablename__ = "checkpoints"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_message = Column(Text, nullable=True)
    checkpoint_type = Column(String, default=CheckpointType.AUTO.value)
    status = Column(String, default=CheckpointStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    restored_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    file_count = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    metadata = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False)


class FileSnapshot(Base):
    """File snapshot database model."""

    __tablename__ = "file_snapshots"

    id = Column(String, primary_key=True, index=True)
    checkpoint_id = Column(String, index=True, nullable=False)
    file_path = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    storage_path = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)


# Pydantic schemas for API


class CheckpointCreate(BaseModel):
    """Schema for creating a checkpoint."""

    session_id: str = Field(..., description="Session identifier")
    user_message: str | None = Field(None, description="User message associated with checkpoint")
    checkpoint_type: CheckpointType = Field(CheckpointType.AUTO, description="Type of checkpoint")
    file_paths: list[str] = Field(
        default_factory=list,
        description="List of file paths to checkpoint",
    )
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class CheckpointRestore(BaseModel):
    """Schema for restoring a checkpoint."""

    restore_code: bool = Field(True, description="Restore code changes")
    restore_conversation: bool = Field(False, description="Restore conversation state")


class CheckpointResponse(BaseModel):
    """Schema for checkpoint response."""

    id: str
    session_id: str
    user_message: str | None
    checkpoint_type: str
    status: str
    created_at: datetime
    restored_at: datetime | None
    expires_at: datetime | None
    file_count: int
    total_size_bytes: int
    metadata: dict[str, Any] | None

    class Config:
        from_attributes = True


class FileSnapshotResponse(BaseModel):
    """Schema for file snapshot response."""

    id: str
    checkpoint_id: str
    file_path: str
    content_hash: str
    size_bytes: int
    created_at: datetime
    metadata: dict[str, Any] | None

    class Config:
        from_attributes = True


class CheckpointListResponse(BaseModel):
    """Schema for listing checkpoints."""

    checkpoints: list[CheckpointResponse]
    total: int
    session_id: str
