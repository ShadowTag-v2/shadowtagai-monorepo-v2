"""
Automation Service Layer

Encapsulates all database operations for the automation subsystem:
scheduled jobs, workflows, triggers, and job executions.
"""

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation import (
    JobExecution,
    JobStatus,
    ScheduledJob,
    Trigger,
    Workflow,
)


class ScheduledJobService:
    """Service layer for scheduled job operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> ScheduledJob:
        """Create a new scheduled job from validated data."""
        job = ScheduledJob(**data)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get(self, job_id: int) -> ScheduledJob | None:
        """Get a scheduled job by ID."""
        result = await self.db.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[ScheduledJob]:
        """List scheduled jobs with pagination."""
        result = await self.db.execute(
            select(ScheduledJob).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, job: ScheduledJob, update_data: dict) -> ScheduledJob:
        """Update a scheduled job with the given fields."""
        for field, value in update_data.items():
            setattr(job, field, value)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def delete(self, job: ScheduledJob) -> None:
        """Delete a scheduled job."""
        await self.db.delete(job)
        await self.db.commit()


class WorkflowService:
    """Service layer for workflow operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Workflow:
        """Create a new workflow from validated data."""
        workflow = Workflow(**data)
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def get(self, workflow_id: int) -> Workflow | None:
        """Get a workflow by ID."""
        result = await self.db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[Workflow]:
        """List workflows with pagination."""
        result = await self.db.execute(
            select(Workflow).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, workflow: Workflow, update_data: dict) -> Workflow:
        """Update a workflow with the given fields."""
        for field, value in update_data.items():
            setattr(workflow, field, value)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete(self, workflow: Workflow) -> None:
        """Delete a workflow."""
        await self.db.delete(workflow)
        await self.db.commit()


class TriggerService:
    """Service layer for trigger operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Trigger:
        """Create a new trigger from validated data."""
        trigger = Trigger(**data)
        self.db.add(trigger)
        await self.db.commit()
        await self.db.refresh(trigger)
        return trigger

    async def get(self, trigger_id: int) -> Trigger | None:
        """Get a trigger by ID."""
        result = await self.db.execute(
            select(Trigger).where(Trigger.id == trigger_id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[Trigger]:
        """List triggers with pagination."""
        result = await self.db.execute(
            select(Trigger).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, trigger: Trigger, update_data: dict) -> Trigger:
        """Update a trigger with the given fields."""
        for field, value in update_data.items():
            setattr(trigger, field, value)
        await self.db.commit()
        await self.db.refresh(trigger)
        return trigger

    async def delete(self, trigger: Trigger) -> None:
        """Delete a trigger."""
        await self.db.delete(trigger)
        await self.db.commit()


class ExecutionService:
    """Service layer for job execution operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, execution_id: int) -> JobExecution | None:
        """Get a job execution by ID."""
        result = await self.db.execute(
            select(JobExecution).where(JobExecution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        workflow_id: int | None = None,
        status: JobStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[JobExecution]:
        """List executions with optional filters and pagination."""
        query = select(JobExecution).order_by(desc(JobExecution.created_at))
        if workflow_id:
            query = query.where(JobExecution.workflow_id == workflow_id)
        if status:
            query = query.where(JobExecution.status == status)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete(self, execution: JobExecution) -> None:
        """Delete a job execution record."""
        await self.db.delete(execution)
        await self.db.commit()
