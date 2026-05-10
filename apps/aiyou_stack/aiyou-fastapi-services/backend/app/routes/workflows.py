"""FastAPI routes for workflow automation."""

from fastapi import APIRouter, Depends, HTTPException

from app.models.workflow import (
    ListWorkflowsResponse,
    ProvideInputRequest,
    ProvideInputResponse,
    StartWorkflowRequest,
    StartWorkflowResponse,
    WorkflowExecutionStatus,
    WorkflowStatusResponse,
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


# Dependency to get workflow engine
def get_workflow_engine() -> WorkflowEngine:
    """Get the workflow engine instance."""
    # This will be overridden by dependency injection in main.py
    return None


@router.get("/", response_model=ListWorkflowsResponse)
async def list_workflows(engine: WorkflowEngine = Depends(get_workflow_engine)):  # noqa: B008
    """List all available workflows."""
    workflows = engine.get_workflows()
    return ListWorkflowsResponse(workflows=workflows, count=len(workflows))


@router.post("/start", response_model=StartWorkflowResponse)
async def start_workflow(
    request: StartWorkflowRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine),  # noqa: B008
):
    """Start a new workflow execution."""
    try:
        execution, next_action = engine.start_workflow(
            workflow_name=request.workflow_name,
            initial_variables=request.initial_variables,
        )

        if execution.status == WorkflowExecutionStatus.FAILED:
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {execution.error}",
            )

        return StartWorkflowResponse(
            execution_id=execution.execution_id,
            status=execution.status,
            message=_get_status_message(execution.status, next_action),
            next_action=next_action,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {e!s}") from e


@router.post("/input", response_model=ProvideInputResponse)
async def provide_input(
    request: ProvideInputRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine),  # noqa: B008
):
    """Provide user input for a waiting workflow."""
    try:
        execution, next_action = engine.provide_input(
            execution_id=request.execution_id,
            input_value=request.input_value,
        )

        if execution.status == WorkflowExecutionStatus.FAILED:
            raise HTTPException(
                status_code=500,
                detail=f"Workflow execution failed: {execution.error}",
            )

        return ProvideInputResponse(
            execution_id=execution.execution_id,
            status=execution.status,
            message=_get_status_message(execution.status, next_action),
            next_action=next_action,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to provide input: {e!s}") from e


@router.get("/status/{execution_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    execution_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine),  # noqa: B008
):
    """Get the status of a workflow execution."""
    execution = engine.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found")

    # Get the workflow to determine next action if waiting for input
    next_action = None
    if execution.status == WorkflowExecutionStatus.WAITING_INPUT:
        workflow = engine.get_workflow(execution.workflow_name)
        if workflow and execution.context.current_action_index < len(workflow.actions):
            next_action = workflow.actions[execution.context.current_action_index]

    return WorkflowStatusResponse(execution=execution, next_action=next_action)


def _get_status_message(status: WorkflowExecutionStatus, next_action) -> str:
    """Generate a user-friendly status message."""
    if status == WorkflowExecutionStatus.COMPLETED:
        return "Workflow completed successfully"
    if status == WorkflowExecutionStatus.WAITING_INPUT:
        if next_action and hasattr(next_action, "prompt"):
            return f"Waiting for input: {next_action.prompt}"
        return "Waiting for user input"
    if status == WorkflowExecutionStatus.RUNNING:
        return "Workflow is running"
    if status == WorkflowExecutionStatus.FAILED:
        return "Workflow execution failed"
    return f"Status: {status}"
