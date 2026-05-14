# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Dropbox-specific generation schema."""

from datetime import datetime
from pydantic import BaseModel, Field


class DropboxArtifact(BaseModel):
    """Schema for Dropbox file generation."""

    title: str = Field(description="File title")
    description: str = Field(description="File description or main content")
    token: str = Field(description="Unique token to embed in content")
    sections: list[dict[str, str]] | None = Field(default=None, description="Optional sections for documents")
    data_rows: list[str] | None = Field(default=None, description="Optional data rows for CSV files")
    metadata: dict[str, str] | None = Field(default=None, description="Optional metadata for structured files")
    created_at: datetime = Field(default_factory=datetime.now)
