"""
Pydantic models for workflow automation system.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, Union

from pydantic import BaseModel, Field


class ActionType(StrEnum):
    """Supported workflow action types."""

    ASK_FOR_INPUT = "AskForInput"
    GET_DATE = "GetDate"
    OPEN_APP = "OpenApp"
    CREATE_NOTE = "CreateNote"
    APPEND_TO_NOTE = "AppendToNote"


class BaseAction(BaseModel):
    """Base class for all workflow actions."""

    type: ActionType


class AskForInputAction(BaseAction):
    """Action to request input from the user."""

    type: Literal[ActionType.ASK_FOR_INPUT] = ActionType.ASK_FOR_INPUT
    title: str = Field(..., description="Title of the input request")
    prompt: str = Field(..., description="Prompt text to display to the user")


class GetDateAction(BaseAction):
    """Action to get the current date/time."""

    type: Literal[ActionType.GET_DATE] = ActionType.GET_DATE
    format: str = Field(default="YYYY-MM-DD HH:mm", description="Date format string")


class OpenAppAction(BaseAction):
    """Action to open an application."""

    type: Literal[ActionType.OPEN_APP] = ActionType.OPEN_APP
    appName: str = Field(..., description="Name of the application to open")


class CreateNoteAction(BaseAction):
    """Action to create a new note."""

    type: Literal[ActionType.CREATE_NOTE] = ActionType.CREATE_NOTE
    folder: str = Field(..., description="Folder where the note should be created")
    noteTitle: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note (can include template variables)")


class AppendToNoteAction(BaseAction):
    """Action to append content to an existing note."""

    type: Literal[ActionType.APPEND_TO_NOTE] = ActionType.APPEND_TO_NOTE
    noteTitle: str = Field(..., description="Title of the note to append to")
    content: str = Field(..., description="Content to append (can include template variables)")


# Union type for all action types
WorkflowAction = Union[
    AskForInputAction, GetDateAction, OpenAppAction, CreateNoteAction, AppendToNoteAction
]


class WorkflowBlock(BaseModel):
    """Definition of a workflow automation block."""

    block_name: str = Field(..., description="Name of the workflow block")
    description: str = Field(..., description="Description of what this workflow does")
    actions: list[WorkflowAction] = Field(..., description="List of actions to execute")

    class Config:
        json_schema_extra = {
            "example": {
                "block_name": "New AI Issue Chat",
                "description": "Starts a new atomic context chat for a new issue",
                "actions": [
                    {
                        "type": "AskForInput",
                        "title": "Issue Title",
                        "prompt": "Enter a short title or description for this issue",
                    },
                    {"type": "GetDate", "format": "YYYY-MM-DD HH:mm"},
                ],
            }
        }


class WorkflowExecutionStatus(StrEnum):
    """Status of workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowExecutionContext(BaseModel):
    """Execution context containing variables collected during workflow execution."""

    variables: dict[str, Any] = Field(default_factory=dict, description="Template variables")
    current_action_index: int = Field(
        default=0, description="Index of current action being executed"
    )


class WorkflowExecution(BaseModel):
    """Represents a running or completed workflow execution."""

    execution_id: str = Field(..., description="Unique execution ID")
    workflow_name: str = Field(..., description="Name of the workflow being executed")
    status: WorkflowExecutionStatus = Field(..., description="Current execution status")
    context: WorkflowExecutionContext = Field(default_factory=WorkflowExecutionContext)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error: str | None = None


class StartWorkflowRequest(BaseModel):
    """Request to start a workflow execution."""

    workflow_name: str = Field(..., description="Name of the workflow to execute")
    initial_variables: dict[str, Any] | None = Field(
        default_factory=dict, description="Optional initial variables to populate the context"
    )


class StartWorkflowResponse(BaseModel):
    """Response when starting a workflow."""

    execution_id: str = Field(..., description="Unique execution ID")
    status: WorkflowExecutionStatus = Field(..., description="Current execution status")
    message: str = Field(..., description="Status message")
    next_action: WorkflowAction | None = Field(
        None, description="Next action to perform if waiting for input"
    )


class ProvideInputRequest(BaseModel):
    """Request to provide input for a waiting workflow."""

    execution_id: str = Field(..., description="Execution ID")
    input_value: str = Field(..., description="User input value")


class ProvideInputResponse(BaseModel):
    """Response after providing input."""

    execution_id: str = Field(..., description="Execution ID")
    status: WorkflowExecutionStatus = Field(..., description="Current execution status")
    message: str = Field(..., description="Status message")
    next_action: WorkflowAction | None = Field(
        None, description="Next action to perform if waiting for input"
    )


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status query."""

    execution: WorkflowExecution = Field(..., description="Current execution state")
    next_action: WorkflowAction | None = Field(None, description="Next action if waiting for input")


class ListWorkflowsResponse(BaseModel):
    """Response listing available workflows."""

    workflows: list[WorkflowBlock] = Field(..., description="List of available workflows")
    count: int = Field(..., description="Total number of workflows")
