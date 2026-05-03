# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ThinkTool — Scratchpad reasoning tool for complex multi-step tasks.

Ported from the think-tool pattern (Claude Code v2.1.91).

This tool gives the agent a private scratchpad for structured reasoning
before acting. It is read-only, zero side-effects, and always allowed.

Benchmarked at +54% accuracy on tau-bench (multi-step tool use) when
the model explicitly reasons in a dedicated tool block rather than
inline chain-of-thought.

Usage:
    think_tool = create_think_tool()
    result = await think_tool.call(
        {"thought": "Let me analyze the error..."},
        context
    )
"""

from __future__ import annotations

import logging
from typing import Any

from .tool import PermissionResult, ToolResult, ToolUseContext, build_tool

logger = logging.getLogger(__name__)

__all__ = ["THINK_TOOL_NAME", "create_think_tool"]

THINK_TOOL_NAME = "Think"


def _think_prompt(*, tools: list[Any] | None = None) -> str:
    """System prompt contribution for the Think tool."""
    return """Use the Think tool to reason through complex problems step-by-step.

When to use Think:
- When you need to analyze multiple pieces of information
- Before making architectural decisions
- When debugging requires hypothesis testing
- When you need to plan a multi-step approach
- To verify your understanding before acting

The Think tool has NO side effects. It is purely a reasoning scratchpad.
Your thoughts are visible in the conversation but do not modify any state.
"""


async def _think_call(
    args: dict[str, Any],
    context: ToolUseContext,
) -> ToolResult:
    """Execute the Think tool — captures reasoning without side effects."""
    thought = args.get("thought", "")
    if not thought:
        return ToolResult(data={"error": "Empty thought — provide reasoning content."})

    # The thought is the output — it's a scratchpad, not an action.
    # Trimmed to avoid bloating context.
    max_chars = 50_000
    if len(thought) > max_chars:
        thought = thought[:max_chars] + "\n\n[Thought truncated at 50K chars]"

    logger.debug("ThinkTool: %d chars of reasoning", len(thought))
    return ToolResult(data={"thought": thought, "status": "reasoning_recorded"})


async def _think_description(
    input_args: dict[str, Any],
    *,
    is_non_interactive: bool = False,
) -> str:
    """Human-readable description of the Think tool call."""
    thought = input_args.get("thought", "")
    preview = thought[:80] + "..." if len(thought) > 80 else thought
    return f"Reasoning: {preview}"


async def _think_check_permissions(
    input_args: dict[str, Any],
    context: ToolUseContext,
) -> PermissionResult:
    """Always allow — Think has zero side effects."""
    return PermissionResult(behavior="allow", updated_input=input_args)


def create_think_tool():
    """Factory for the ThinkTool.

    Returns a fully-constructed Tool instance.
    """
    return build_tool(
        name=THINK_TOOL_NAME,
        input_schema={
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": (
                        "Your step-by-step reasoning. Use this to analyze problems, plan approaches, verify understanding, and track hypotheses."
                    ),
                }
            },
            "required": ["thought"],
        },
        call_fn=_think_call,
        description_fn=_think_description,
        prompt_fn=_think_prompt,
        max_result_size_chars=100_000,
        aliases=["think", "reason", "scratchpad"],
        search_hint="reason through complex problems step by step",
        should_defer=False,
        always_load=True,  # Always available — zero cost
        strict=False,
        is_enabled_fn=lambda: True,
        is_concurrency_safe_fn=lambda _: True,  # Zero side effects
        is_read_only_fn=lambda _: True,  # Pure read
        is_destructive_fn=lambda _: False,
        check_permissions_fn=_think_check_permissions,
    )
