# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Plan Mode Tools — Enter and exit structured planning mode.

Ported from src/tools/EnterPlanModeTool/ and ExitPlanModeTool/
(Claude Code v2.1.91).

Plan mode restricts the agent to read-only tools, preventing mutations
while the agent analyzes and designs an approach. Integrates with the
existing plan_mode.orchestrator for state management.

EnterPlanModeTool:
- Transitions agent to plan mode (read-only)
- Saves pre-plan permission mode for restoration
- Cannot be used from subagent contexts

ExitPlanModeTool:
- Restores pre-plan permission mode
- Re-enables write tools
- Only callable when already in plan mode
"""

from __future__ import annotations

import logging
from typing import Any

from .tool import (
    PermissionMode,
    PermissionResult,
    ToolResult,
    ToolUseContext,
    build_tool,
)

logger = logging.getLogger(__name__)

__all__ = [
    "ENTER_PLAN_MODE_TOOL_NAME",
    "EXIT_PLAN_MODE_TOOL_NAME",
    "create_enter_plan_mode_tool",
    "create_exit_plan_mode_tool",
]

ENTER_PLAN_MODE_TOOL_NAME = "EnterPlanMode"
EXIT_PLAN_MODE_TOOL_NAME = "ExitPlanMode"


# ---------------------------------------------------------------------------
# EnterPlanMode
# ---------------------------------------------------------------------------


def _enter_plan_prompt(*, tools: list[Any] | None = None) -> str:
    """System prompt for EnterPlanMode."""
    return """Use EnterPlanMode when you need to design an approach before implementing.

Plan mode restricts you to read-only tools. You can:
- Read files and directories
- Search code with grep/glob
- Analyze architecture with Architect/Think
- Use web search for research

You CANNOT:
- Edit or create files
- Run terminal commands
- Make API calls

Use plan mode for complex, multi-step tasks where upfront analysis
prevents wasted effort and regressions. Exit plan mode with
ExitPlanMode when your analysis is complete and you're ready to implement.
"""


async def _enter_plan_call(
    args: dict[str, Any],
    context: ToolUseContext,
) -> ToolResult:
    """Transition agent into plan mode."""
    # Guard: subagents cannot enter plan mode
    if context.agent_id and context.agent_type:
        return ToolResult(data={"error": "EnterPlanMode cannot be used in subagent contexts. Only the root agent can enter plan mode."})

    current_mode = context.tool_permission_context.mode

    # Already in plan mode?
    if current_mode == PermissionMode.PLAN:
        return ToolResult(data={"message": "Already in plan mode.", "status": "no_change"})

    # Save pre-plan mode for restoration
    context.tool_permission_context.pre_plan_mode = current_mode

    # Transition to plan mode
    context.tool_permission_context.mode = PermissionMode.PLAN

    logger.info(
        "EnterPlanMode: %s → PLAN (pre_plan=%s)",
        current_mode.value,
        current_mode.value,
    )

    return ToolResult(
        data={
            "message": (
                "Entered plan mode. All write tools are now disabled. "
                "Use read-only tools to analyze the codebase. "
                "Call ExitPlanMode when ready to implement."
            ),
            "previous_mode": current_mode.value,
            "current_mode": "plan",
        },
        context_modifier=lambda ctx: ctx,  # Context already mutated above
    )


async def _enter_plan_description(
    input_args: dict[str, Any],
    *,
    is_non_interactive: bool = False,
) -> str:
    return "Entering plan mode — restricting to read-only tools"


async def _enter_plan_check_permissions(
    input_args: dict[str, Any],
    context: ToolUseContext,
) -> PermissionResult:
    """Allow unless in subagent context."""
    if context.agent_id and context.agent_type:
        return PermissionResult(
            behavior="deny",
            message="Plan mode is only available in root agent context.",
        )
    return PermissionResult(behavior="allow", updated_input=input_args)


def create_enter_plan_mode_tool():
    """Factory for EnterPlanModeTool."""
    return build_tool(
        name=ENTER_PLAN_MODE_TOOL_NAME,
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        call_fn=_enter_plan_call,
        description_fn=_enter_plan_description,
        prompt_fn=_enter_plan_prompt,
        aliases=["enter_plan", "plan_mode_on"],
        search_hint="switch to plan mode to design an approach before coding",
        should_defer=True,
        is_concurrency_safe_fn=lambda _: True,
        is_read_only_fn=lambda _: True,
        check_permissions_fn=_enter_plan_check_permissions,
    )


# ---------------------------------------------------------------------------
# ExitPlanMode
# ---------------------------------------------------------------------------


def _exit_plan_prompt(*, tools: list[Any] | None = None) -> str:
    """System prompt for ExitPlanMode."""
    return """Use ExitPlanMode when your analysis is complete and you're ready to implement.

This restores the permission mode that was active before you entered
plan mode. All write tools become available again.

Only call ExitPlanMode when you have:
1. Fully analyzed the problem
2. Identified all files that need changes
3. Planned the implementation order
4. Assessed the blast radius
"""


async def _exit_plan_call(
    args: dict[str, Any],
    context: ToolUseContext,
) -> ToolResult:
    """Exit plan mode and restore previous permission mode."""
    current_mode = context.tool_permission_context.mode

    if current_mode != PermissionMode.PLAN:
        return ToolResult(
            data={
                "error": "Not in plan mode. Nothing to exit.",
                "current_mode": current_mode.value,
            }
        )

    # Restore pre-plan mode
    restore_to = context.tool_permission_context.pre_plan_mode or PermissionMode.DEFAULT
    context.tool_permission_context.mode = restore_to
    context.tool_permission_context.pre_plan_mode = None

    logger.info("ExitPlanMode: PLAN → %s", restore_to.value)

    return ToolResult(
        data={
            "message": f"Exited plan mode. Restored to '{restore_to.value}' mode. Write tools are now available.",
            "restored_mode": restore_to.value,
        },
        context_modifier=lambda ctx: ctx,
    )


async def _exit_plan_description(
    input_args: dict[str, Any],
    *,
    is_non_interactive: bool = False,
) -> str:
    return "Exiting plan mode — re-enabling write tools"


def create_exit_plan_mode_tool():
    """Factory for ExitPlanModeTool."""
    return build_tool(
        name=EXIT_PLAN_MODE_TOOL_NAME,
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        call_fn=_exit_plan_call,
        description_fn=_exit_plan_description,
        prompt_fn=_exit_plan_prompt,
        aliases=["exit_plan", "plan_mode_off"],
        search_hint="exit plan mode and resume normal implementation",
        should_defer=True,
        is_concurrency_safe_fn=lambda _: True,
        is_read_only_fn=lambda _: True,
    )
