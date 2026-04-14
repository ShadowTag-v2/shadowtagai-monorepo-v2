"""API routes for scheduled job management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.scheduler import automation_scheduler
from app.core.database import get_db
from app.schemas.automation import ScheduledJobCreate, ScheduledJobResponse, ScheduledJobUpdate
from app.services.automation_service import ScheduledJobService

router = APIRouter(prefix="/jobs", tags=["scheduled-jobs"])


def get_job_service(db: AsyncSession = Depends(get_db)) -> ScheduledJobService:
    """Dependency to get ScheduledJobService instance."""
    return ScheduledJobService(db)


@router.post("/", response_model=ScheduledJobResponse, status_code=201)
async def create_scheduled_job(
    job: ScheduledJobCreate,
    service: ScheduledJobService = Depends(get_job_service),
):
    """Create a new scheduled job."""
    db_job = await service.create(job.model_dump())

    # Add to scheduler if enabled
    if db_job.enabled and automation_scheduler._initialized:
        await automation_scheduler.add_job(db_job)

    return db_job


@router.get("/", response_model=list[ScheduledJobResponse])
async def list_scheduled_jobs(
    skip: int = 0,
    limit: int = 100,
    service: ScheduledJobService = Depends(get_job_service),
):
    """List all scheduled jobs."""
    return await service.list(skip, limit)


@router.get("/{job_id}", response_model=ScheduledJobResponse)
async def get_scheduled_job(
    job_id: int,
    service: ScheduledJobService = Depends(get_job_service),
):
    """Get a specific scheduled job by ID."""
    job = await service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")
    return job


@router.put("/{job_id}", response_model=ScheduledJobResponse)
async def update_scheduled_job(
    job_id: int,
    job_update: ScheduledJobUpdate,
    service: ScheduledJobService = Depends(get_job_service),
):
    """Update a scheduled job."""
    job = await service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    update_data = job_update.model_dump(exclude_unset=True)
    job = await service.update(job, update_data)

    # Update scheduler
    if automation_scheduler._initialized:
        if job.enabled:
            await automation_scheduler.add_job(job)
        else:
            await automation_scheduler.remove_job(job.id)

    return job


@router.delete("/{job_id}", status_code=204)
async def delete_scheduled_job(
    job_id: int,
    service: ScheduledJobService = Depends(get_job_service),
):
    """Delete a scheduled job."""
    job = await service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scheduled job not found")

    # Remove from scheduler
    if automation_scheduler._initialized:
        await automation_scheduler.remove_job(job.id)

    await service.delete(job)


@router.post("/{job_id}/run", status_code=202)
async def run_scheduled_job_now(
    job_id: int,
    service: ScheduledJobService = Depends(get_job_service),
):
    """Manually trigger a scheduled job to run now."""
    job = await service.get(job_id)
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
