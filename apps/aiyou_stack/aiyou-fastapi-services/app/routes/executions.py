"""
API routes for job execution management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.engine import workflow_engine
from app.core.database import get_db
from app.models.automation import JobExecution, JobStatus
from app.schemas.automation import ExecuteWorkflowRequest, JobExecutionResponse

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post("/", response_model=JobExecutionResponse, status_code=202)
async def execute_workflow(
    execution_request: ExecuteWorkflowRequest, db: AsyncSession = Depends(get_db)
):
    """Manually execute a workflow."""
    execution = await workflow_engine.execute_workflow(
        workflow_id=execution_request.workflow_id, input_data=execution_request.input_data
    )

    return execution


@router.get("/", response_model=list[JobExecutionResponse])
async def list_executions(
    workflow_id: int | None = Query(None, description="Filter by workflow ID"),
    status: JobStatus | None = Query(None, description="Filter by status"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List job executions with optional filters."""
    query = select(JobExecution).order_by(desc(JobExecution.created_at))

    if workflow_id:
        query = query.where(JobExecution.workflow_id == workflow_id)

    if status:
        query = query.where(JobExecution.status == status)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    executions = result.scalars().all()
    return executions


@router.get("/{execution_id}", response_model=JobExecutionResponse)
async def get_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific job execution by ID."""
    result = await db.execute(select(JobExecution).where(JobExecution.id == execution_id))
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution


@router.post("/{execution_id}/retry", response_model=JobExecutionResponse, status_code=202)
async def retry_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Retry a failed job execution."""
    result = await db.execute(select(JobExecution).where(JobExecution.id == execution_id))
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status != JobStatus.FAILED:
        raise HTTPException(status_code=400, detail="Only failed executions can be retried")

    # Create a new execution
    new_execution = await workflow_engine.execute_workflow(
        workflow_id=execution.workflow_id,
        input_data=execution.input_data,
        scheduled_job_id=execution.scheduled_job_id,
        trigger_id=execution.trigger_id,
    )

    return new_execution


@router.delete("/{execution_id}", status_code=204)
async def delete_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a job execution record."""
    result = await db.execute(select(JobExecution).where(JobExecution.id == execution_id))
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    await db.delete(execution)
    await db.commit()
    return None
