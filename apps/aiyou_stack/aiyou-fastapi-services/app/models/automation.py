"""
Database models for automation system.
"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy import Enum as SQLEnum

from app.core.database import Base


class WorkflowStatus(enum.StrEnum):
    """Workflow status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class JobStatus(enum.StrEnum):
    """Job execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TriggerType(enum.StrEnum):
    """Trigger type enumeration."""

    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    EVENT = "event"
    MANUAL = "manual"


class Workflow(Base):
    """
    Workflow model representing an automation workflow.
    """

    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.ACTIVE, nullable=False)

    # Workflow definition (JSON structure)
    definition = Column(JSON, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)

    # Tags for organization
    tags = Column(JSON, default=list, nullable=True)

    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}', status='{self.status}')>"


class ScheduledJob(Base):
    """
    Scheduled job model for time-based automation.
    """

    __tablename__ = "scheduled_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Workflow reference
    workflow_id = Column(Integer, nullable=False, index=True)

    # Schedule configuration
    cron_expression = Column(String(100), nullable=True)
    interval_seconds = Column(Integer, nullable=True)

    # Job configuration
    enabled = Column(Boolean, default=True, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    timeout_seconds = Column(Integer, default=3600, nullable=False)

    # Parameters to pass to workflow
    parameters = Column(JSON, default=dict, nullable=True)

    # Scheduling metadata
    next_run_time = Column(DateTime, nullable=True)
    last_run_time = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ScheduledJob(id={self.id}, name='{self.name}', enabled={self.enabled})>"


class Trigger(Base):
    """
    Trigger model for event-based automation.
    """

    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Trigger type and configuration
    trigger_type = Column(SQLEnum(TriggerType), nullable=False, index=True)

    # Workflow reference
    workflow_id = Column(Integer, nullable=False, index=True)

    # Trigger configuration (event name, webhook URL, etc.)
    config = Column(JSON, nullable=False)

    # Conditions for trigger activation
    conditions = Column(JSON, default=dict, nullable=True)

    # Status
    enabled = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Trigger(id={self.id}, name='{self.name}', type='{self.trigger_type}')>"


class JobExecution(Base):
    """
    Job execution model tracking individual workflow runs.
    """

    __tablename__ = "job_executions"

    id = Column(Integer, primary_key=True, index=True)

    # References
    workflow_id = Column(Integer, nullable=False, index=True)
    scheduled_job_id = Column(Integer, nullable=True, index=True)
    trigger_id = Column(Integer, nullable=True, index=True)

    # Execution details
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)

    # Input/Output
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Performance metrics
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Retry information
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return (
            f"<JobExecution(id={self.id}, workflow_id={self.workflow_id}, status='{self.status}')>"
        )
