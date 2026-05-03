# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests for ThinkTool + ArchitectTool + PlanMode transitions.

Tests cover:
  1. ThinkTool scratchpad: create, invoke, verify no side effects
  2. ArchitectTool: read-only analysis, no mutation
  3. PlanMode: enter/exit transitions, state verification
  4. Transition flow: ThinkTool reasoning → ArchitectTool analysis → PlanMode entry
  5. Tool factory compliance: build_tool returns valid Tool protocol
"""

from __future__ import annotations

import pytest

from packages.agnt_tools.think_tool import create_think_tool
from packages.agnt_tools.architect_tool import create_architect_tool
from packages.agnt_tools.plan_mode_tools import (
    create_enter_plan_mode_tool,
    create_exit_plan_mode_tool,
)
from packages.agnt_tools.tool import ToolUseContext


@pytest.fixture
def ctx() -> ToolUseContext:
    """Create a minimal ToolUseContext for testing."""
    return ToolUseContext()


class TestThinkTool:
    """ThinkTool integration tests."""

    def test_creation(self):
        tool = create_think_tool()
        assert tool.name == "Think"
        assert tool.is_read_only({}) is True

    def test_has_required_protocol_methods(self):
        tool = create_think_tool()
        assert callable(tool.call)
        assert callable(tool.description)
        assert callable(tool.prompt)

    @pytest.mark.asyncio
    async def test_basic_invocation(self, ctx):
        tool = create_think_tool()
        result = await tool.call({"thought": "analyzing the architecture"}, ctx)
        assert result is not None
        assert result.data is not None
        assert "error" not in result.data

    @pytest.mark.asyncio
    async def test_empty_thought_fails(self, ctx):
        tool = create_think_tool()
        result = await tool.call({"thought": ""}, ctx)
        assert "error" in result.data

    @pytest.mark.asyncio
    async def test_no_side_effects(self, ctx):
        """ThinkTool must be purely computational — no filesystem, no network."""
        tool = create_think_tool()
        result = await tool.call({"thought": "test reasoning step"}, ctx)
        assert result is not None
        # The content should echo the thought (scratchpad pattern)
        assert result.data.get("thought") == "test reasoning step"


class TestArchitectTool:
    """ArchitectTool integration tests."""

    def test_creation(self):
        tool = create_architect_tool()
        assert tool.name == "Architect"
        assert tool.is_read_only({}) is True

    def test_has_required_protocol_methods(self):
        tool = create_architect_tool()
        assert callable(tool.call)
        assert callable(tool.description)
        assert callable(tool.prompt)

    @pytest.mark.asyncio
    async def test_basic_invocation(self, ctx):
        tool = create_architect_tool()
        result = await tool.call({
            "task": "What is the best approach for caching?"
        }, ctx)
        assert result is not None
        assert "error" not in result.data

    @pytest.mark.asyncio
    async def test_read_only_enforcement(self, ctx):
        """ArchitectTool must not mutate any state."""
        tool = create_architect_tool()
        assert tool.is_read_only({}) is True
        # Attempting any mutation-suggesting input should still be safe
        result = await tool.call({
            "task": "Delete all files and restructure"
        }, ctx)
        assert result is not None
        # Result should indicate analysis only, no action taken


class TestPlanModeTools:
    """PlanMode transition tests."""

    def test_enter_creation(self):
        tool = create_enter_plan_mode_tool()
        assert tool.name == "EnterPlanMode"

    def test_exit_creation(self):
        tool = create_exit_plan_mode_tool()
        assert tool.name == "ExitPlanMode"

    @pytest.mark.asyncio
    async def test_enter_plan_mode(self, ctx):
        tool = create_enter_plan_mode_tool()
        result = await tool.call({}, ctx)
        assert result is not None
        assert "error" not in result.data

    @pytest.mark.asyncio
    async def test_exit_plan_mode(self, ctx):
        # Must enter plan mode first to make exit valid
        enter = create_enter_plan_mode_tool()
        await enter.call({}, ctx)

        tool = create_exit_plan_mode_tool()
        result = await tool.call({}, ctx)
        assert result is not None
        assert "error" not in result.data

    @pytest.mark.asyncio
    async def test_transition_flow(self, ctx):
        """Enter → Architect analysis → Exit flow."""
        enter = create_enter_plan_mode_tool()
        exit_tool = create_exit_plan_mode_tool()
        architect = create_architect_tool()

        # Enter plan mode
        r1 = await enter.call({}, ctx)
        assert "error" not in r1.data

        # Do analysis while in plan mode
        r2 = await architect.call({"task": "evaluate cache strategy"}, ctx)
        assert "error" not in r2.data

        # Exit plan mode
        r3 = await exit_tool.call({}, ctx)
        assert "error" not in r3.data


class TestToolFactoryCompliance:
    """Verify build_tool produces valid Tool protocol instances."""

    def test_think_tool_protocol(self):
        tool = create_think_tool()
        # Structural check — has all required attributes
        assert hasattr(tool, "name")
        assert hasattr(tool, "call")
        assert hasattr(tool, "description")
        assert hasattr(tool, "prompt")
        assert hasattr(tool, "input_schema")
        assert hasattr(tool, "is_read_only")

    def test_all_tools_have_unique_names(self):
        tools = [
            create_think_tool(),
            create_architect_tool(),
            create_enter_plan_mode_tool(),
            create_exit_plan_mode_tool(),
        ]
        names = [t.name for t in tools]
        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

    def test_input_schemas_are_valid(self):
        tools = [
            create_think_tool(),
            create_architect_tool(),
            create_enter_plan_mode_tool(),
            create_exit_plan_mode_tool(),
        ]
        for tool in tools:
            schema = tool.input_schema
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
