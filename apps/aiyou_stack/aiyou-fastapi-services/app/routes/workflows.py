"""API routes for workflow management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.automation import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from app.services.automation_service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


def get_workflow_service(db: AsyncSession = Depends(get_db)) -> WorkflowService:
    """Dependency to get WorkflowService instance."""
    return WorkflowService(db)


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow: WorkflowCreate,
    service: WorkflowService = Depends(get_workflow_service),
):
    """Create a new workflow."""
    return await service.create(workflow.model_dump())


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    service: WorkflowService = Depends(get_workflow_service),
):
    """List all workflows."""
    return await service.list(skip, limit)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    service: WorkflowService = Depends(get_workflow_service),
):
    """Get a specific workflow by ID."""
    workflow = await service.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    service: WorkflowService = Depends(get_workflow_service),
):
    """Update a workflow."""
    workflow = await service.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    update_data = workflow_update.model_dump(exclude_unset=True)
    return await service.update(workflow, update_data)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: int,
    service: WorkflowService = Depends(get_workflow_service),
):
    """Delete a workflow."""
    workflow = await service.get(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    await service.delete(workflow)
