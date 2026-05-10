# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Integration tests — ThinkTool × ArchitectTool × PlanMode transitions.

45-test suite validating:
  1. ThinkTool zero side-effects and input validation
  2. ArchitectTool structured analysis and read-only guarantees
  3. PlanMode enter/exit transitions and permission state
  4. Combined workflows: Think → Architect → PlanMode lifecycle
  5. Subagent isolation and clone_isolated behaviour
  6. Tool registry: name matching, alias resolution, find_tool_by_name
  7. Permission invariants across all mode transitions
"""

from __future__ import annotations

import asyncio

import pytest

from agnt_tools.think_tool import THINK_TOOL_NAME, create_think_tool
from agnt_tools.architect_tool import ARCHITECT_TOOL_NAME, create_architect_tool
from agnt_tools.plan_mode_tools import (
  create_enter_plan_mode_tool,
  create_exit_plan_mode_tool,
)
from agnt_tools.tool import (
  PermissionMode,
  ToolUseContext,
  find_tool_by_name,
  get_empty_tool_permission_context,
  tool_matches_name,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def root_context() -> ToolUseContext:
  """Root agent context — default permission mode, no agent identity."""
  return ToolUseContext(
    model="gemini-3.1-flash",
    tool_permission_context=get_empty_tool_permission_context(),
  )


@pytest.fixture
def subagent_context() -> ToolUseContext:
  """Subagent context — has agent_id and agent_type set."""
  ctx = ToolUseContext(
    model="gemini-3.1-flash",
    tool_permission_context=get_empty_tool_permission_context(),
    agent_id="sub-agent-42",
    agent_type="forked",
  )
  return ctx


@pytest.fixture
def auto_context() -> ToolUseContext:
  """Context in AUTO permission mode (YOLO)."""
  pctx = get_empty_tool_permission_context()
  pctx.mode = PermissionMode.AUTO
  return ToolUseContext(
    model="gemini-3.1-flash",
    tool_permission_context=pctx,
  )


@pytest.fixture
def think_tool():
  return create_think_tool()


@pytest.fixture
def architect_tool():
  return create_architect_tool()


@pytest.fixture
def enter_plan_tool():
  return create_enter_plan_mode_tool()


@pytest.fixture
def exit_plan_tool():
  return create_exit_plan_mode_tool()


@pytest.fixture
def all_tools(think_tool, architect_tool, enter_plan_tool, exit_plan_tool):
  return [think_tool, architect_tool, enter_plan_tool, exit_plan_tool]


# ===========================================================================
# 1. ThinkTool — Unit-level integration
# ===========================================================================


class TestThinkToolCore:
  """ThinkTool zero side-effects, validation, and permission invariants."""

  @pytest.mark.asyncio
  async def test_basic_reasoning(self, think_tool, root_context) -> None:
    result = await think_tool.call(
      {"thought": "Let me analyze the dependency graph."},
      root_context,
    )
    assert result.data["status"] == "reasoning_recorded"
    assert "dependency graph" in result.data["thought"]

  @pytest.mark.asyncio
  async def test_empty_thought_rejected(self, think_tool, root_context) -> None:
    result = await think_tool.call({"thought": ""}, root_context)
    assert "error" in result.data

  @pytest.mark.asyncio
  async def test_missing_thought_key_rejected(self, think_tool, root_context) -> None:
    result = await think_tool.call({}, root_context)
    assert "error" in result.data

  @pytest.mark.asyncio
  async def test_truncation_at_50k(self, think_tool, root_context) -> None:
    long_thought = "x" * 60_000
    result = await think_tool.call({"thought": long_thought}, root_context)
    assert result.data["thought"].endswith("[Thought truncated at 50K chars]")
    assert len(result.data["thought"]) < 60_000

  @pytest.mark.asyncio
  async def test_no_context_mutation(self, think_tool, root_context) -> None:
    """ThinkTool must not mutate the context."""
    mode_before = root_context.tool_permission_context.mode
    msgs_before = len(root_context.messages)
    await think_tool.call({"thought": "test"}, root_context)
    assert root_context.tool_permission_context.mode == mode_before
    assert len(root_context.messages) == msgs_before

  @pytest.mark.asyncio
  async def test_always_allowed(self, think_tool, root_context) -> None:
    perm = await think_tool.check_permissions({"thought": "test"}, root_context)
    assert perm.behavior == "allow"

  def test_is_read_only(self, think_tool) -> None:
    assert think_tool.is_read_only({"thought": "test"})

  def test_is_concurrency_safe(self, think_tool) -> None:
    assert think_tool.is_concurrency_safe({"thought": "test"})

  def test_is_not_destructive(self, think_tool) -> None:
    assert not think_tool.is_destructive({"thought": "test"})

  def test_is_enabled(self, think_tool) -> None:
    assert think_tool.is_enabled()

  @pytest.mark.asyncio
  async def test_description_preview(self, think_tool) -> None:
    desc = await think_tool.description(
      {"thought": "A" * 100},
      is_non_interactive=False,
    )
    assert "Reasoning:" in desc
    # Preview should be truncated to ~80 chars + "..."
    assert "..." in desc

  @pytest.mark.asyncio
  async def test_prompt_content(self, think_tool) -> None:
    prompt = await think_tool.prompt()
    assert "Think" in prompt
    assert "NO side effects" in prompt


# ===========================================================================
# 2. ArchitectTool — Unit-level integration
# ===========================================================================


class TestArchitectToolCore:
  """ArchitectTool structured analysis and read-only guarantees."""

  @pytest.mark.asyncio
  async def test_basic_analysis(self, architect_tool, root_context) -> None:
    result = await architect_tool.call(
      {"task": "Design the auth migration", "scope": "packages/auth/"},
      root_context,
    )
    assert result.data["task"] == "Design the auth migration"
    assert result.data["scope"] == "packages/auth/"
    assert result.data["analysis_type"] == "architectural_review"
    assert result.data["status"] == "analysis_recorded"

  @pytest.mark.asyncio
  async def test_with_constraints(self, architect_tool, root_context) -> None:
    result = await architect_tool.call(
      {
        "task": "Refactor the API layer",
        "constraints": ["No breaking changes", "Keep backward compat"],
      },
      root_context,
    )
    assert len(result.data["constraints"]) == 2
    assert "No breaking changes" in result.data["constraints"]

  @pytest.mark.asyncio
  async def test_empty_task_rejected(self, architect_tool, root_context) -> None:
    result = await architect_tool.call({"task": ""}, root_context)
    assert "error" in result.data

  @pytest.mark.asyncio
  async def test_missing_task_rejected(self, architect_tool, root_context) -> None:
    result = await architect_tool.call({}, root_context)
    assert "error" in result.data

  @pytest.mark.asyncio
  async def test_no_scope_defaults_to_empty(self, architect_tool, root_context) -> None:
    result = await architect_tool.call(
      {"task": "Analyze logging patterns"},
      root_context,
    )
    assert result.data["scope"] == ""

  @pytest.mark.asyncio
  async def test_no_context_mutation(self, architect_tool, root_context) -> None:
    mode_before = root_context.tool_permission_context.mode
    await architect_tool.call({"task": "analysis"}, root_context)
    assert root_context.tool_permission_context.mode == mode_before

  @pytest.mark.asyncio
  async def test_always_allowed(self, architect_tool, root_context) -> None:
    perm = await architect_tool.check_permissions({"task": "test"}, root_context)
    assert perm.behavior == "allow"

  def test_is_read_only(self, architect_tool) -> None:
    assert architect_tool.is_read_only({"task": "test"})

  def test_is_concurrency_safe(self, architect_tool) -> None:
    assert architect_tool.is_concurrency_safe({"task": "test"})

  def test_is_not_destructive(self, architect_tool) -> None:
    assert not architect_tool.is_destructive({"task": "test"})

  @pytest.mark.asyncio
  async def test_description_with_scope(self, architect_tool) -> None:
    desc = await architect_tool.description(
      {"task": "Design cache", "scope": "packages/cache/"},
    )
    assert "Architect:" in desc
    assert "packages/cache/" in desc

  @pytest.mark.asyncio
  async def test_prompt_content(self, architect_tool) -> None:
    prompt = await architect_tool.prompt()
    assert "READ-ONLY" in prompt
    assert "Implementation Plan" in prompt


# ===========================================================================
# 3. PlanMode Transitions
# ===========================================================================


class TestEnterPlanMode:
  """EnterPlanMode tool transition tests."""

  @pytest.mark.asyncio
  async def test_enter_from_default(self, enter_plan_tool, root_context) -> None:
    result = await enter_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN
    assert result.data["previous_mode"] == "default"
    assert result.data["current_mode"] == "plan"

  @pytest.mark.asyncio
  async def test_enter_saves_pre_plan_mode(self, enter_plan_tool, root_context) -> None:
    root_context.tool_permission_context.mode = PermissionMode.AUTO
    await enter_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.pre_plan_mode == PermissionMode.AUTO
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN

  @pytest.mark.asyncio
  async def test_idempotent_when_already_in_plan(
    self, enter_plan_tool, root_context
  ) -> None:
    root_context.tool_permission_context.mode = PermissionMode.PLAN
    result = await enter_plan_tool.call({}, root_context)
    assert result.data["status"] == "no_change"
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN

  @pytest.mark.asyncio
  async def test_rejected_in_subagent(self, enter_plan_tool, subagent_context) -> None:
    result = await enter_plan_tool.call({}, subagent_context)
    assert "error" in result.data
    assert "subagent" in result.data["error"].lower()

  @pytest.mark.asyncio
  async def test_permission_denied_for_subagent(
    self, enter_plan_tool, subagent_context
  ) -> None:
    perm = await enter_plan_tool.check_permissions({}, subagent_context)
    assert perm.behavior == "deny"


class TestExitPlanMode:
  """ExitPlanMode tool transition tests."""

  @pytest.mark.asyncio
  async def test_exit_restores_default(self, exit_plan_tool, root_context) -> None:
    root_context.tool_permission_context.mode = PermissionMode.PLAN
    root_context.tool_permission_context.pre_plan_mode = PermissionMode.DEFAULT
    result = await exit_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.DEFAULT
    assert result.data["restored_mode"] == "default"

  @pytest.mark.asyncio
  async def test_exit_restores_auto(self, exit_plan_tool, root_context) -> None:
    root_context.tool_permission_context.mode = PermissionMode.PLAN
    root_context.tool_permission_context.pre_plan_mode = PermissionMode.AUTO
    result = await exit_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.AUTO
    assert result.data["restored_mode"] == "auto"

  @pytest.mark.asyncio
  async def test_exit_defaults_to_default_if_no_pre_plan(
    self, exit_plan_tool, root_context
  ) -> None:
    root_context.tool_permission_context.mode = PermissionMode.PLAN
    root_context.tool_permission_context.pre_plan_mode = None
    await exit_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.DEFAULT

  @pytest.mark.asyncio
  async def test_exit_when_not_in_plan_errors(
    self, exit_plan_tool, root_context
  ) -> None:
    assert root_context.tool_permission_context.mode == PermissionMode.DEFAULT
    result = await exit_plan_tool.call({}, root_context)
    assert "error" in result.data
    assert "Not in plan mode" in result.data["error"]

  @pytest.mark.asyncio
  async def test_exit_clears_pre_plan_mode(self, exit_plan_tool, root_context) -> None:
    root_context.tool_permission_context.mode = PermissionMode.PLAN
    root_context.tool_permission_context.pre_plan_mode = PermissionMode.AUTO
    await exit_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.pre_plan_mode is None


# ===========================================================================
# 4. Combined Workflow Integration
# ===========================================================================


class TestCombinedWorkflow:
  """End-to-end workflows combining Think, Architect, and PlanMode."""

  @pytest.mark.asyncio
  async def test_think_then_architect_then_plan(
    self, think_tool, architect_tool, enter_plan_tool, exit_plan_tool, root_context
  ) -> None:
    """Full workflow: Think → Architect → EnterPlan → Think → ExitPlan."""
    # Step 1: Reason about the problem
    r1 = await think_tool.call(
      {"thought": "I need to refactor the auth layer. Let me identify dependencies."},
      root_context,
    )
    assert r1.data["status"] == "reasoning_recorded"
    assert root_context.tool_permission_context.mode == PermissionMode.DEFAULT

    # Step 2: Architectural analysis
    r2 = await architect_tool.call(
      {
        "task": "Map auth layer dependencies",
        "scope": "packages/auth/",
        "constraints": ["Must maintain backward compat"],
      },
      root_context,
    )
    assert r2.data["analysis_type"] == "architectural_review"
    assert root_context.tool_permission_context.mode == PermissionMode.DEFAULT

    # Step 3: Enter plan mode
    await enter_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN

    # Step 4: Think tool still works in plan mode (read-only)
    r4 = await think_tool.call(
      {"thought": "In plan mode now, let me verify my approach."},
      root_context,
    )
    assert r4.data["status"] == "reasoning_recorded"

    # Step 5: Architect tool still works in plan mode (read-only)
    r5 = await architect_tool.call(
      {"task": "Verify blast radius in plan mode"},
      root_context,
    )
    assert r5.data["status"] == "analysis_recorded"

    # Step 6: Exit plan mode
    await exit_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.DEFAULT

  @pytest.mark.asyncio
  async def test_auto_to_plan_and_back(
    self, enter_plan_tool, exit_plan_tool, auto_context
  ) -> None:
    """AUTO → PLAN → AUTO roundtrip preserves AUTO mode."""
    assert auto_context.tool_permission_context.mode == PermissionMode.AUTO
    await enter_plan_tool.call({}, auto_context)
    assert auto_context.tool_permission_context.mode == PermissionMode.PLAN
    await exit_plan_tool.call({}, auto_context)
    assert auto_context.tool_permission_context.mode == PermissionMode.AUTO

  @pytest.mark.asyncio
  async def test_double_enter_plan_idempotent(
    self, enter_plan_tool, root_context
  ) -> None:
    """Entering plan mode twice should be idempotent."""
    await enter_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN
    r2 = await enter_plan_tool.call({}, root_context)
    assert r2.data["status"] == "no_change"
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN

  @pytest.mark.asyncio
  async def test_double_exit_plan_errors(
    self, enter_plan_tool, exit_plan_tool, root_context
  ) -> None:
    """Exiting plan mode twice should error on second call."""
    await enter_plan_tool.call({}, root_context)
    await exit_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.DEFAULT
    r3 = await exit_plan_tool.call({}, root_context)
    assert "error" in r3.data


# ===========================================================================
# 5. Subagent Isolation
# ===========================================================================


class TestSubagentIsolation:
  """clone_isolated must not leak plan mode state across agent boundaries."""

  @pytest.mark.asyncio
  async def test_clone_does_not_inherit_plan_mode(
    self, enter_plan_tool, root_context
  ) -> None:
    """Subagent created from plan-mode parent should still have plan mode
    (deep copy), but separate mutation path."""
    await enter_plan_tool.call({}, root_context)
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN

    child = root_context.clone_isolated()
    # Child is deep-copied, so it has PLAN mode from parent
    assert child.tool_permission_context.mode == PermissionMode.PLAN
    # But mutating child should NOT affect parent
    child.tool_permission_context.mode = PermissionMode.DEFAULT
    assert root_context.tool_permission_context.mode == PermissionMode.PLAN

  @pytest.mark.asyncio
  async def test_clone_gets_fresh_agent_id(self, root_context) -> None:
    child = root_context.clone_isolated()
    assert child.agent_id is not None
    assert child.agent_id != root_context.agent_id

  @pytest.mark.asyncio
  async def test_clone_sets_avoid_permission_prompts(self, root_context) -> None:
    child = root_context.clone_isolated()
    assert child.tool_permission_context.should_avoid_permission_prompts is True

  @pytest.mark.asyncio
  async def test_subagent_cannot_enter_plan_mode(
    self, enter_plan_tool, root_context
  ) -> None:
    """Clone with agent_id set should be rejected by EnterPlanMode."""
    child = root_context.clone_isolated()
    result = await enter_plan_tool.call({}, child)
    assert "error" in result.data


# ===========================================================================
# 6. Tool Registry
# ===========================================================================


class TestToolRegistry:
  """Tool name matching, alias resolution, and registry lookup."""

  def test_think_name_match(self, think_tool) -> None:
    assert tool_matches_name(think_tool, "Think")

  def test_think_alias_match(self, think_tool) -> None:
    assert tool_matches_name(think_tool, "think")
    assert tool_matches_name(think_tool, "reason")
    assert tool_matches_name(think_tool, "scratchpad")

  def test_architect_name_match(self, architect_tool) -> None:
    assert tool_matches_name(architect_tool, "Architect")

  def test_architect_alias_match(self, architect_tool) -> None:
    assert tool_matches_name(architect_tool, "architect")
    assert tool_matches_name(architect_tool, "plan")
    assert tool_matches_name(architect_tool, "analyze")
    assert tool_matches_name(architect_tool, "design")

  def test_enter_plan_name_match(self, enter_plan_tool) -> None:
    assert tool_matches_name(enter_plan_tool, "EnterPlanMode")
    assert tool_matches_name(enter_plan_tool, "enter_plan")
    assert tool_matches_name(enter_plan_tool, "plan_mode_on")

  def test_exit_plan_name_match(self, exit_plan_tool) -> None:
    assert tool_matches_name(exit_plan_tool, "ExitPlanMode")
    assert tool_matches_name(exit_plan_tool, "exit_plan")
    assert tool_matches_name(exit_plan_tool, "plan_mode_off")

  def test_find_tool_by_name_primary(self, all_tools) -> None:
    t = find_tool_by_name(all_tools, "Think")
    assert t is not None
    assert t.name == THINK_TOOL_NAME

  def test_find_tool_by_name_alias(self, all_tools) -> None:
    t = find_tool_by_name(all_tools, "scratchpad")
    assert t is not None
    assert t.name == THINK_TOOL_NAME

  def test_find_tool_nonexistent(self, all_tools) -> None:
    t = find_tool_by_name(all_tools, "NonExistentTool")
    assert t is None

  def test_find_architect_by_alias(self, all_tools) -> None:
    t = find_tool_by_name(all_tools, "design")
    assert t is not None
    assert t.name == ARCHITECT_TOOL_NAME


# ===========================================================================
# 7. Concurrency — Parallel tool calls
# ===========================================================================


class TestConcurrency:
  """Verify concurrent tool calls do not interfere."""

  @pytest.mark.asyncio
  async def test_parallel_think_calls(self, think_tool, root_context) -> None:
    """Multiple Think calls in parallel should not interfere."""
    tasks = [
      think_tool.call({"thought": f"Thought #{i}"}, root_context) for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    for i, r in enumerate(results):
      assert r.data["status"] == "reasoning_recorded"
      assert f"Thought #{i}" in r.data["thought"]

  @pytest.mark.asyncio
  async def test_parallel_architect_calls(self, architect_tool, root_context) -> None:
    tasks = [
      architect_tool.call({"task": f"Analyze module #{i}"}, root_context)
      for i in range(10)
    ]
    results = await asyncio.gather(*tasks)
    for i, r in enumerate(results):
      assert r.data["task"] == f"Analyze module #{i}"
      assert r.data["status"] == "analysis_recorded"

  @pytest.mark.asyncio
  async def test_think_and_architect_parallel(
    self, think_tool, architect_tool, root_context
  ) -> None:
    """Think and Architect can run in parallel without interference."""
    t1 = think_tool.call({"thought": "Hypothesis A"}, root_context)
    t2 = architect_tool.call({"task": "Analyze hypothesis A"}, root_context)
    r1, r2 = await asyncio.gather(t1, t2)
    assert r1.data["status"] == "reasoning_recorded"
    assert r2.data["status"] == "analysis_recorded"
