# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Basic tests for workflow engine."""

import pytest
from app.models.workflow import (
    ActionType,
    WorkflowBlock,
    WorkflowExecutionStatus,
)
from app.services.storage_service import StorageService
from app.services.workflow_engine import WorkflowEngine


def test_workflow_registration():
    """Test registering a workflow."""
    storage = StorageService()
    engine = WorkflowEngine(storage)

    workflow = WorkflowBlock(
        block_name="Test Workflow",
        description="A test workflow",
        actions=[
            {"type": ActionType.ASK_FOR_INPUT, "title": "Test Input", "prompt": "Enter test value"},
        ],
    )

    engine.register_workflow(workflow)

    workflows = engine.get_workflows()
    assert len(workflows) == 1
    assert workflows[0].block_name == "Test Workflow"


def test_workflow_start_and_input():
    """Test starting a workflow and providing input."""
    storage = StorageService()
    engine = WorkflowEngine(storage)

    workflow = WorkflowBlock(
        block_name="Input Test",
        description="Test input workflow",
        actions=[
            {"type": ActionType.ASK_FOR_INPUT, "title": "Name", "prompt": "Enter your name"},
            {"type": ActionType.GET_DATE, "format": "YYYY-MM-DD"},
        ],
    )

    engine.register_workflow(workflow)

    # Start workflow
    execution, next_action = engine.start_workflow("Input Test")
    assert execution.status == WorkflowExecutionStatus.WAITING_INPUT
    assert next_action.title == "Name"

    # Provide input
    execution, next_action = engine.provide_input(execution.execution_id, "John Doe")
    assert execution.status == WorkflowExecutionStatus.COMPLETED
    assert execution.context.variables["Name"] == "John Doe"
    assert "Date" in execution.context.variables


def test_note_creation_in_workflow():
    """Test note creation within a workflow."""
    storage = StorageService()
    engine = WorkflowEngine(storage)

    workflow = WorkflowBlock(
        block_name="Note Creation Test",
        description="Test note creation",
        actions=[
            {"type": ActionType.ASK_FOR_INPUT, "title": "Title", "prompt": "Enter title"},
            {
                "type": ActionType.CREATE_NOTE,
                "folder": "Test",
                "noteTitle": "Test Note",
                "content": "Title: {{Title}}\nContent here",
            },
        ],
    )

    engine.register_workflow(workflow)

    # Start and provide input
    execution, _ = engine.start_workflow("Note Creation Test")
    execution, _ = engine.provide_input(execution.execution_id, "My Title")

    # Verify note was created
    note = storage.get_note_by_title("Test Note")
    assert note is not None
    assert "Title: My Title" in note.content


def test_variable_substitution():
    """Test template variable substitution."""
    storage = StorageService()
    engine = WorkflowEngine(storage)

    variables = {"Name": "Alice", "Age": "30", "City": "New York"}

    template = "Name: {{Name}}, Age: {{Age}}, City: {{City}}"
    result = engine._substitute_variables(template, variables)

    assert result == "Name: Alice, Age: 30, City: New York"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
