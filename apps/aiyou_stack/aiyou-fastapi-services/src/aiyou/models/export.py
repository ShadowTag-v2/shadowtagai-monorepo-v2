# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Export Models - Pydantic schemas for thread export functionality.

Provides request/response models for exporting AI conversation threads
in various formats (JSON, Markdown, Text compilation).
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ExportFormat(StrEnum):
    """Supported export formats."""

    JSON = "json"
    MARKDOWN = "markdown"
    TEXT = "text"  # Full-text compilation format


class ThreadExportRequest(BaseModel):
    """Request model for exporting threads."""

    format: ExportFormat = Field(
        ExportFormat.JSON,
        description="Export format: json, markdown, or text (compilation)",
    )
    thread_ids: list[int] | None = Field(
        None,
        description="Specific thread/OPORD IDs to export. If None, exports based on filters.",
    )
    date_from: str | None = Field(
        None,
        description="Start date for filtering (ISO format: YYYY-MM-DD)",
    )
    date_to: str | None = Field(None, description="End date for filtering (ISO format: YYYY-MM-DD)")
    tags: list[str] | None = Field(None, description="Filter by tags")
    agent_id: str | None = Field(None, description="Filter by agent ID")
    shift_number: int | None = Field(None, ge=0, le=2, description="Filter by shift number (0-2)")
    status: str | None = Field(None, description="Filter by status (active, completed, archived)")
    include_metadata: bool = Field(
        True,
        description="Include metadata in export (timestamps, stats, etc.)",
    )
    limit: int = Field(1000, ge=1, le=10000, description="Maximum number of threads to export")


class ThreadMetadata(BaseModel):
    """Metadata for an exported thread."""

    opord_number: int = Field(..., description="OPORD number (thread ID)")
    task_title: str = Field(..., description="Thread title")
    agent_id: str = Field(..., description="Agent that created the thread")
    shift_number: int = Field(..., description="Shift number (0-2)")
    status: str = Field(..., description="Thread status")
    created_at: str = Field(..., description="Creation timestamp (ISO)")
    updated_at: str | None = Field(None, description="Last update timestamp")
    tags: list[str] = Field(default_factory=list, description="Thread tags")


class ThreadContent(BaseModel):
    """Full content of an exported thread."""

    metadata: ThreadMetadata
    mission: dict[str, str] = Field(..., description="5W mission: who, what, when, where, why")
    situation: dict[str, str] | None = Field(None, description="Situation analysis")
    execution: dict[str, Any] | None = Field(None, description="Execution plan")
    service_support: dict[str, Any] | None = Field(None, description="Service/support details")
    command_signal: dict[str, Any] | None = Field(None, description="Command and signal")
    summary: str | None = Field(None, description="Thread summary (if completed)")
    decisions: list[str] | None = Field(None, description="Key decisions made")


class ExportStats(BaseModel):
    """Statistics about the export."""

    total_threads: int = Field(..., description="Total threads exported")
    date_range: dict[str, str] | None = Field(None, description="Date range of exported threads")
    export_format: str = Field(..., description="Format used for export")
    character_count: int = Field(..., description="Total characters in export")
    generated_at: str = Field(..., description="Export generation timestamp")


class ThreadExportResponse(BaseModel):
    """Response model for thread export."""

    success: bool = Field(True, description="Whether export succeeded")
    stats: ExportStats = Field(..., description="Export statistics")
    content: Any = Field(
        ...,
        description="Export content (JSON array, markdown string, or text compilation)",
    )


class SingleThreadExportResponse(BaseModel):
    """Response model for single thread export."""

    success: bool = Field(True, description="Whether export succeeded")
    format: str = Field(..., description="Export format used")
    thread: ThreadContent = Field(..., description="Exported thread content")


class BulkExportRequest(BaseModel):
    """Request model for bulk export with advanced options."""

    format: ExportFormat = Field(ExportFormat.JSON, description="Export format")
    filters: dict[str, Any] | None = Field(None, description="Advanced filter criteria")
    include_raw_json: bool = Field(False, description="Include raw JSON data in export")
    compilation_title: str | None = Field(None, description="Title for text compilation format")
    compilation_description: str | None = Field(
        None,
        description="Description for text compilation header",
    )


class ExportErrorResponse(BaseModel):
    """Error response for export operations."""

    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code for programmatic handling")
    details: dict[str, Any] | None = Field(None, description="Additional error details")
