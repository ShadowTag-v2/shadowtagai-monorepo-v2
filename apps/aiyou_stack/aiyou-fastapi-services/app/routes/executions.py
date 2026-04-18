"""API routes for job execution management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.engine import workflow_engine
from app.core.database import get_db
from app.models.automation import JobStatus
from app.schemas.automation import ExecuteWorkflowRequest, JobExecutionResponse
from app.services.automation_service import ExecutionService

router = APIRouter(prefix="/executions", tags=["executions"])


def get_execution_service(db: AsyncSession = Depends(get_db)) -> ExecutionService:
    """Dependency to get ExecutionService instance."""
    return ExecutionService(db)


@router.post("/", response_model=JobExecutionResponse, status_code=202)
async def execute_workflow(execution_request: ExecuteWorkflowRequest):
    """Manually execute a workflow."""
    execution = await workflow_engine.execute_workflow(
        workflow_id=execution_request.workflow_id,
        input_data=execution_request.input_data,
    )
    return execution


@router.get("/", response_model=list[JobExecutionResponse])
async def list_executions(
    workflow_id: int | None = Query(None, description="Filter by workflow ID"),
    status: JobStatus | None = Query(None, description="Filter by status"),
    skip: int = 0,
    limit: int = 100,
    service: ExecutionService = Depends(get_execution_service),
):
    """List job executions with optional filters."""
    return await service.list(workflow_id, status, skip, limit)


@router.get("/{execution_id}", response_model=JobExecutionResponse)
async def get_execution(
    execution_id: int,
    service: ExecutionService = Depends(get_execution_service),
):
    """Get a specific job execution by ID."""
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.post("/{execution_id}/retry", response_model=JobExecutionResponse, status_code=202)
async def retry_execution(
    execution_id: int,
    service: ExecutionService = Depends(get_execution_service),
):
    """Retry a failed job execution."""
    execution = await service.get(execution_id)
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
async def delete_execution(
    execution_id: int,
    service: ExecutionService = Depends(get_execution_service),
):
    """Delete a job execution record."""
    execution = await service.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    await service.delete(execution)
