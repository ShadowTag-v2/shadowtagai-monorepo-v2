"""
API routes for scheduled job management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.scheduler import automation_scheduler
from app.core.database import get_db
from app.models.automation import ScheduledJob
from app.schemas.automation import ScheduledJobCreate, ScheduledJobResponse, ScheduledJobUpdate

router = APIRouter(prefix="/jobs", tags=["scheduled-jobs"])


@router.post("/", response_model=ScheduledJobResponse, status_code=201)
async def create_scheduled_job(job: ScheduledJobCreate, db: AsyncSession = Depends(get_db)):
    """Create a new scheduled job."""
    db_job = ScheduledJob(**job.model_dump())
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    # Add to scheduler if enabled
    if db_job.enabled and automation_scheduler._initialized:
        await automation_scheduler.add_job(db_job)

    return db_job


@router.get("/", response_model=list[ScheduledJobResponse])
async def list_scheduled_jobs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all scheduled jobs."""
    result = await db.execute(select(ScheduledJob).offset(skip).limit(limit))
    jobs = result.scalars().all()
    return jobs


@router.get("/{job_id}", response_model=ScheduledJobResponse)
async def get_scheduled_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific scheduled job by ID."""
    result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    return job


@router.put("/{job_id}", response_model=ScheduledJobResponse)
async def update_scheduled_job(
    job_id: int, job_update: ScheduledJobUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a scheduled job."""
    result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    # Update fields
    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.commit()
    await db.refresh(job)

    # Update scheduler
    if automation_scheduler._initialized:
        if job.enabled:
            await automation_scheduler.add_job(job)
        else:
            await automation_scheduler.remove_job(job.id)

    return job


@router.delete("/{job_id}", status_code=204)
async def delete_scheduled_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a scheduled job."""
    result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    # Remove from scheduler
    if automation_scheduler._initialized:
        await automation_scheduler.remove_job(job.id)

    await db.delete(job)
    await db.commit()
    return None


@router.post("/{job_id}/run", status_code=202)
async def run_scheduled_job_now(job_id: int, db: AsyncSession = Depends(get_db)):
    """Manually trigger a scheduled job to run now."""
    result = await db.execute(select(ScheduledJob).where(ScheduledJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    # Execute immediately
    from app.automation.engine import workflow_engine

    execution = await workflow_engine.execute_workflow(
        workflow_id=job.workflow_id,
        input_data=job.parameters,
        scheduled_job_id=job.id,
    )

    return {
        "message": "Job execution started",
        "execution_id": execution.id,
        "status": execution.status,
    }
