# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ArchitectTool — Read-only architectural analysis and planning tool.

Ported from the Architect pattern (Claude Code v2.1.91).

This tool provides structured architectural analysis without making
any changes to the codebase. It is a read-only planning instrument
that forces the agent into analysis mode before proposing changes.

Key properties:
- Read-only: NEVER modifies files, creates files, or runs commands
- Concurrency-safe: Pure analysis, no state mutation
- Always allowed: No permission prompts needed
- Structured output: Produces analysis in a standardized format

Usage:
    architect_tool = create_architect_tool()
    result = await architect_tool.call(
        {"task": "Design the auth migration", "scope": "packages/auth/"},
        context
    )
"""

from __future__ import annotations

import logging
from typing import Any

from .tool import PermissionResult, ToolResult, ToolUseContext, build_tool

logger = logging.getLogger(__name__)

__all__ = ["ARCHITECT_TOOL_NAME", "create_architect_tool"]

ARCHITECT_TOOL_NAME = "Architect"


def _architect_prompt(*, tools: list[Any] | None = None) -> str:
    """System prompt contribution for the Architect tool."""
    return """Use the Architect tool to analyze and plan before implementing changes.

The Architect tool is STRICTLY READ-ONLY. It cannot:
- Create, modify, or delete files
- Run terminal commands
- Make API calls
- Modify any state

What it CAN do:
- Analyze existing code structure and patterns
- Identify dependencies and impact zones
- Plan multi-step implementation approaches
- Evaluate trade-offs between different approaches
- Map the blast radius of proposed changes
- Recommend specific files and functions to modify

Use Architect BEFORE making changes to ensure you understand the full
impact of your modifications. This prevents regressions and missed
dependencies.

Output format:
1. Current State Analysis: What exists today
2. Proposed Changes: What needs to change and why
3. Impact Analysis: What other code will be affected
4. Risk Assessment: What could go wrong
5. Implementation Plan: Step-by-step execution order
"""


async def _architect_call(
    args: dict[str, Any],
    context: ToolUseContext,
) -> ToolResult:
    """Execute the Architect tool — produces structured analysis."""
    task = args.get("task", "")
    scope = args.get("scope", "")
    constraints = args.get("constraints", [])

    if not task:
        return ToolResult(data={"error": "Empty task — describe what to analyze."})

    # Build the structured analysis frame
    analysis = {
        "task": task,
        "scope": scope,
        "constraints": constraints,
        "analysis_type": "architectural_review",
        "status": "analysis_recorded",
        "note": ("This is a planning artifact. No files were modified. Use implementation tools to execute the plan."),
    }

    logger.debug(
        "ArchitectTool: task=%s scope=%s constraints=%d",
        task[:60],
        scope[:40] if scope else "(global)",
        len(constraints),
    )
    return ToolResult(data=analysis)


async def _architect_description(
    input_args: dict[str, Any],
    *,
    is_non_interactive: bool = False,
) -> str:
    """Human-readable description of the Architect tool call."""
    task = input_args.get("task", "")
    scope = input_args.get("scope", "")
    preview = task[:60] + "..." if len(task) > 60 else task
    scope_desc = f" in {scope}" if scope else ""
    return f"Architect: {preview}{scope_desc}"


async def _architect_check_permissions(
    input_args: dict[str, Any],
    context: ToolUseContext,
) -> PermissionResult:
    """Always allow — Architect is strictly read-only."""
    return PermissionResult(behavior="allow", updated_input=input_args)


def create_architect_tool():
    """Factory for the ArchitectTool.

    Returns a fully-constructed Tool instance.
    """
    return build_tool(
        name=ARCHITECT_TOOL_NAME,
        input_schema={
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": ("Describe the architectural analysis needed. Be specific about what you want to understand or plan."),
                },
                "scope": {
                    "type": "string",
                    "description": ("Optional directory or module scope to focus the analysis. e.g., 'packages/auth/' or 'src/services/'"),
                },
                "constraints": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": ("Optional list of constraints the plan must respect. e.g., 'No breaking changes', 'Must be backward compatible'"),
                },
            },
            "required": ["task"],
        },
        call_fn=_architect_call,
        description_fn=_architect_description,
        prompt_fn=_architect_prompt,
        max_result_size_chars=200_000,
        aliases=["architect", "plan", "analyze", "design"],
        search_hint="analyze architecture and plan changes before implementing",
        should_defer=False,
        always_load=True,
        strict=False,
        is_enabled_fn=lambda: True,
        is_concurrency_safe_fn=lambda _: True,
        is_read_only_fn=lambda _: True,
        is_destructive_fn=lambda _: False,
        check_permissions_fn=_architect_check_permissions,
    )
