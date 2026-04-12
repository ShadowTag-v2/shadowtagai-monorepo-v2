"""
Workflow engine service for executing workflow automation blocks.
"""

import re
import uuid
from datetime import datetime
from typing import Any

from app.models.workflow import (
    AppendToNoteAction,
    AskForInputAction,
    CreateNoteAction,
    GetDateAction,
    OpenAppAction,
    WorkflowAction,
    WorkflowBlock,
    WorkflowExecution,
    WorkflowExecutionContext,
    WorkflowExecutionStatus,
)
from app.services.storage_service import StorageService


class WorkflowEngine:
    """
    Engine for executing workflow automation blocks.
    Manages workflow state, variable substitution, and action execution.
    """

    def __init__(self, storage_service: StorageService):
        """Initialize the workflow engine."""
        self.storage_service = storage_service
        self.executions: dict[str, WorkflowExecution] = {}
        self.workflows: dict[str, WorkflowBlock] = {}

    def register_workflow(self, workflow: WorkflowBlock) -> None:
        """Register a workflow block."""
        self.workflows[workflow.block_name] = workflow

    def get_workflows(self) -> list[WorkflowBlock]:
        """Get all registered workflows."""
        return list(self.workflows.values())

    def get_workflow(self, workflow_name: str) -> WorkflowBlock | None:
        """Get a specific workflow by name."""
        return self.workflows.get(workflow_name)

    def start_workflow(
        self, workflow_name: str, initial_variables: dict[str, Any] | None = None
    ) -> tuple[WorkflowExecution, WorkflowAction | None]:
        """
        Start a new workflow execution.

        Returns:
            Tuple of (WorkflowExecution, next_action or None)
        """
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        # Create execution context
        execution_id = str(uuid.uuid4())
        context = WorkflowExecutionContext(
            variables=initial_variables or {}, current_action_index=0
        )

        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_name=workflow_name,
            status=WorkflowExecutionStatus.RUNNING,
            context=context,
        )

        self.executions[execution_id] = execution

        # Start executing
        return self._execute_next_action(execution)

    def provide_input(
        self, execution_id: str, input_value: str
    ) -> tuple[WorkflowExecution, WorkflowAction | None]:
        """
        Provide user input for a waiting workflow.

        Returns:
            Tuple of (WorkflowExecution, next_action or None)
        """
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution '{execution_id}' not found")

        if execution.status != WorkflowExecutionStatus.WAITING_INPUT:
            raise ValueError(
                f"Execution is not waiting for input. Current status: {execution.status}"
            )

        workflow = self.workflows.get(execution.workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{execution.workflow_name}' not found")

        # Get the current action (should be AskForInput)
        current_action = workflow.actions[execution.context.current_action_index]
        if not isinstance(current_action, AskForInputAction):
            raise ValueError("Current action is not AskForInput")

        # Store the input value with the title as the variable name
        variable_name = current_action.title
        execution.context.variables[variable_name] = input_value

        # Move to next action
        execution.context.current_action_index += 1
        execution.status = WorkflowExecutionStatus.RUNNING
        execution.updated_at = datetime.utcnow()

        # Execute next action
        return self._execute_next_action(execution)

    def get_execution(self, execution_id: str) -> WorkflowExecution | None:
        """Get execution by ID."""
        return self.executions.get(execution_id)

    def _execute_next_action(
        self, execution: WorkflowExecution
    ) -> tuple[WorkflowExecution, WorkflowAction | None]:
        """
        Execute the next action in the workflow.

        Returns:
            Tuple of (WorkflowExecution, next_action or None)
        """
        workflow = self.workflows.get(execution.workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{execution.workflow_name}' not found")

        # Check if we've completed all actions
        if execution.context.current_action_index >= len(workflow.actions):
            execution.status = WorkflowExecutionStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.updated_at = datetime.utcnow()
            return execution, None

        # Get current action
        action = workflow.actions[execution.context.current_action_index]

        try:
            # Execute action based on type
            if isinstance(action, AskForInputAction):
                # Wait for user input
                execution.status = WorkflowExecutionStatus.WAITING_INPUT
                execution.updated_at = datetime.utcnow()
                return execution, action

            elif isinstance(action, GetDateAction):
                # Get current date
                date_value = self._format_date(action.format)
                execution.context.variables["Date"] = date_value

                # Move to next action
                execution.context.current_action_index += 1
                return self._execute_next_action(execution)

            elif isinstance(action, OpenAppAction):
                # Note: In a real implementation, this would interact with a system
                # For now, we just log it
                execution.context.variables[f"Opened_{action.appName}"] = True

                # Move to next action
                execution.context.current_action_index += 1
                return self._execute_next_action(execution)

            elif isinstance(action, CreateNoteAction):
                # Create note with variable substitution
                content = self._substitute_variables(action.content, execution.context.variables)
                note_id = self.storage_service.create_note(
                    folder=action.folder, title=action.noteTitle, content=content
                )
                execution.context.variables[f"Note_{action.noteTitle}_ID"] = note_id

                # Move to next action
                execution.context.current_action_index += 1
                return self._execute_next_action(execution)

            elif isinstance(action, AppendToNoteAction):
                # Append to note with variable substitution
                content = self._substitute_variables(action.content, execution.context.variables)
                self.storage_service.append_to_note(title=action.noteTitle, content=content)

                # Move to next action
                execution.context.current_action_index += 1
                return self._execute_next_action(execution)

            else:
                raise ValueError(f"Unknown action type: {type(action)}")

        except Exception as e:
            execution.status = WorkflowExecutionStatus.FAILED
            execution.error = str(e)
            execution.updated_at = datetime.utcnow()
            return execution, None

    def _substitute_variables(self, template: str, variables: dict[str, Any]) -> str:
        """
        Substitute template variables in the format {{VariableName}}.

        Args:
            template: Template string with {{VariableName}} placeholders
            variables: Dictionary of variable values

        Returns:
            String with variables substituted
        """

        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r"\{\{([^}]+)\}\}", replace_var, template)

    def _format_date(self, format_string: str) -> str:
        """
        Format current date according to the format string.

        Supports simple format tokens:
        - YYYY: 4-digit year
        - MM: 2-digit month
        - DD: 2-digit day
        - HH: 2-digit hour (24h)
        - mm: 2-digit minute
        - ss: 2-digit second
        """
        now = datetime.now()

        result = format_string
        result = result.replace("YYYY", f"{now.year:04d}")
        result = result.replace("MM", f"{now.month:02d}")
        result = result.replace("DD", f"{now.day:02d}")
        result = result.replace("HH", f"{now.hour:02d}")
        result = result.replace("mm", f"{now.minute:02d}")
        result = result.replace("ss", f"{now.second:02d}")

        return result
