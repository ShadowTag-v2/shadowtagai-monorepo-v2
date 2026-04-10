"""
Pydantic schemas for automation API.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.automation import JobStatus, TriggerType, WorkflowStatus


# Workflow Schemas
class WorkflowBase(BaseModel):
    """Base workflow schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    definition: dict[str, Any] = Field(..., description="Workflow definition as JSON")
    tags: list[str] | None = None


class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow."""

    created_by: str | None = None


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: WorkflowStatus | None = None
    definition: dict[str, Any] | None = None
    tags: list[str] | None = None


class WorkflowResponse(WorkflowBase):
    """Schema for workflow response."""

    id: int
    status: WorkflowStatus
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None

    class Config:
        from_attributes = True


# Scheduled Job Schemas
class ScheduledJobBase(BaseModel):
    """Base scheduled job schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    workflow_id: int
    cron_expression: str | None = Field(None, description="Cron expression for scheduling")
    interval_seconds: int | None = Field(None, ge=1, description="Interval in seconds")
    enabled: bool = True
    max_retries: int = Field(3, ge=0)
    timeout_seconds: int = Field(3600, ge=1)
    parameters: dict[str, Any] | None = None


class ScheduledJobCreate(ScheduledJobBase):
    """Schema for creating a scheduled job."""

    pass


class ScheduledJobUpdate(BaseModel):
    """Schema for updating a scheduled job."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    cron_expression: str | None = None
    interval_seconds: int | None = Field(None, ge=1)
    enabled: bool | None = None
    max_retries: int | None = Field(None, ge=0)
    timeout_seconds: int | None = Field(None, ge=1)
    parameters: dict[str, Any] | None = None


class ScheduledJobResponse(ScheduledJobBase):
    """Schema for scheduled job response."""

    id: int
    next_run_time: datetime | None = None
    last_run_time: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Trigger Schemas
class TriggerBase(BaseModel):
    """Base trigger schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    trigger_type: TriggerType
    workflow_id: int
    config: dict[str, Any] = Field(..., description="Trigger configuration")
    conditions: dict[str, Any] | None = None
    enabled: bool = True


class TriggerCreate(TriggerBase):
    """Schema for creating a trigger."""

    pass


class TriggerUpdate(BaseModel):
    """Schema for updating a trigger."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    config: dict[str, Any] | None = None
    conditions: dict[str, Any] | None = None
    enabled: bool | None = None


class TriggerResponse(TriggerBase):
    """Schema for trigger response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Job Execution Schemas
class JobExecutionBase(BaseModel):
    """Base job execution schema."""

    workflow_id: int
    scheduled_job_id: int | None = None
    trigger_id: int | None = None
    input_data: dict[str, Any] | None = None


class JobExecutionCreate(JobExecutionBase):
    """Schema for creating a job execution."""

    pass


class JobExecutionResponse(JobExecutionBase):
    """Schema for job execution response."""

    id: int
    status: JobStatus
    output_data: dict[str, Any] | None = None
    error_message: str | None = None
    error_traceback: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = None
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Execution Request Schema
class ExecuteWorkflowRequest(BaseModel):
    """Schema for manual workflow execution."""

    workflow_id: int
    input_data: dict[str, Any] | None = None


# Trigger Event Schema
class TriggerEventRequest(BaseModel):
    """Schema for triggering an event."""

    event_name: str
    event_data: dict[str, Any] | None = None
