# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""API-based Context Management — server-side context editing strategies.

Ported from: compact/apiMicrocompact.ts
Reference: AGNT STATE B Spec P1.4

This module implements the server-side context editing protocol that allows
the API to clear tool results and thinking blocks without a client-side
compaction round-trip. Currently stubbed — the Anthropic protocol is not
publicly available. The type system and strategy builder are production-ready.

Strategy types:
  - clear_tool_uses_20250919: Clears tool result content above threshold
  - clear_thinking_20251015: Preserves/clears thinking blocks

Design from upstream (apiMicrocompact.ts):
  - DEFAULT_MAX_INPUT_TOKENS = 180_000 (typical warning threshold)
  - DEFAULT_TARGET_INPUT_TOKENS = 40_000 (keep last 40k tokens)
  - Tool clearing is gated behind USER_TYPE === 'ant' in upstream
  - We implement the full capability since we own the stack
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum

logger = logging.getLogger(__name__)

# Default values matching upstream constants
DEFAULT_MAX_INPUT_TOKENS = 180_000
DEFAULT_TARGET_INPUT_TOKENS = 40_000


class StrategyType(StrEnum):
    """Context editing strategy types."""

    CLEAR_TOOL_USES = "clear_tool_uses_20250919"
    CLEAR_THINKING = "clear_thinking_20251015"


# Tools whose results can be safely cleared (read-only or ephemeral output)
TOOLS_CLEARABLE_RESULTS: frozenset[str] = frozenset(
    {
        # Shell tools
        "Bash",
        "bash",
        # Search tools
        "Glob",
        "glob",
        "Grep",
        "grep",
        # Read tools
        "Read",
        "read",
        "View",
        "view",
        # Web tools
        "WebFetch",
        "web_fetch",
        "WebSearch",
        "web_search",
        # MCP tools (read-only)
        "mcp_read",
        "search_web",
        "read_url_content",
    }
)

# Tools whose uses (inputs) can be safely cleared (write operations
# where the input diff is no longer needed after the write succeeds)
TOOLS_CLEARABLE_USES: frozenset[str] = frozenset(
    {
        "Edit",
        "edit",
        "Write",
        "write",
        "NotebookEdit",
        "notebook_edit",
        "MultiEdit",
        "multi_edit",
        "replace_file_content",
        "multi_replace_file_content",
        "write_to_file",
    }
)


@dataclass
class TriggerConfig:
    """When to trigger context clearing."""

    trigger_type: str = "input_tokens"
    value: int = DEFAULT_MAX_INPUT_TOKENS


@dataclass
class KeepConfig:
    """How many recent items to preserve."""

    keep_type: str = "tool_uses"
    value: int = 5


@dataclass
class ClearAtLeastConfig:
    """Minimum amount to clear when triggered."""

    clear_type: str = "input_tokens"
    value: int = DEFAULT_MAX_INPUT_TOKENS - DEFAULT_TARGET_INPUT_TOKENS


@dataclass
class ClearToolUsesStrategy:
    """Strategy to clear tool use results above a threshold."""

    strategy_type: str = StrategyType.CLEAR_TOOL_USES
    trigger: TriggerConfig = field(default_factory=TriggerConfig)
    keep: KeepConfig = field(default_factory=KeepConfig)
    clear_tool_inputs: list[str] | bool = field(default_factory=lambda: list(TOOLS_CLEARABLE_RESULTS))
    exclude_tools: list[str] = field(default_factory=list)
    clear_at_least: ClearAtLeastConfig = field(default_factory=ClearAtLeastConfig)


@dataclass
class ClearThinkingStrategy:
    """Strategy to manage thinking block retention."""

    strategy_type: str = StrategyType.CLEAR_THINKING
    keep: str | dict[str, int] = "all"  # 'all' or {'thinking_turns': N}


@dataclass
class ContextManagementConfig:
    """Complete context management configuration for the API."""

    edits: list[ClearToolUsesStrategy | ClearThinkingStrategy] = field(
        default_factory=list,
    )

    def to_api_dict(self) -> dict | None:
        """Serialize to API-compatible dict. Returns None if empty."""
        if not self.edits:
            return None
        result: list[dict] = []
        for edit in self.edits:
            if isinstance(edit, ClearToolUsesStrategy):
                d: dict = {"type": edit.strategy_type}
                d["trigger"] = {"type": edit.trigger.trigger_type, "value": edit.trigger.value}
                d["keep"] = {"type": edit.keep.keep_type, "value": edit.keep.value}
                d["clear_at_least"] = {"type": edit.clear_at_least.clear_type, "value": edit.clear_at_least.value}
                if isinstance(edit.clear_tool_inputs, list):
                    d["clear_tool_inputs"] = edit.clear_tool_inputs
                elif edit.clear_tool_inputs is True:
                    d["clear_tool_inputs"] = True
                if edit.exclude_tools:
                    d["exclude_tools"] = edit.exclude_tools
                result.append(d)
            elif isinstance(edit, ClearThinkingStrategy):
                d = {"type": edit.strategy_type}
                d["keep"] = edit.keep if isinstance(edit.keep, str) else edit.keep
                result.append(d)
        return {"edits": result}


def build_api_context_management(
    *,
    has_thinking: bool = False,
    clear_all_thinking: bool = False,
    enable_tool_result_clearing: bool = True,
    enable_tool_use_clearing: bool = False,
    max_input_tokens: int = DEFAULT_MAX_INPUT_TOKENS,
    target_input_tokens: int = DEFAULT_TARGET_INPUT_TOKENS,
) -> ContextManagementConfig | None:
    """Build API context management configuration.

    This mirrors getAPIContextManagement() from apiMicrocompact.ts.
    Currently returns the config structure — the actual API integration
    is stubbed until the protocol is publicly available.

    Args:
        has_thinking: Whether messages contain thinking blocks.
        clear_all_thinking: If True, keep only last thinking turn.
        enable_tool_result_clearing: Enable clearing tool results.
        enable_tool_use_clearing: Enable clearing tool use inputs.
        max_input_tokens: Token threshold to trigger clearing.
        target_input_tokens: Target token count after clearing.

    Returns:
        ContextManagementConfig or None if no strategies apply.
    """
    strategies: list[ClearToolUsesStrategy | ClearThinkingStrategy] = []

    # Thinking block management
    if has_thinking:
        if clear_all_thinking:
            strategies.append(
                ClearThinkingStrategy(keep={"thinking_turns": 1}),
            )
        else:
            strategies.append(ClearThinkingStrategy(keep="all"))

    # Tool result clearing
    if enable_tool_result_clearing:
        strategies.append(
            ClearToolUsesStrategy(
                trigger=TriggerConfig(value=max_input_tokens),
                clear_at_least=ClearAtLeastConfig(
                    value=max_input_tokens - target_input_tokens,
                ),
                clear_tool_inputs=list(TOOLS_CLEARABLE_RESULTS),
            ),
        )

    # Tool use (input) clearing
    if enable_tool_use_clearing:
        strategies.append(
            ClearToolUsesStrategy(
                trigger=TriggerConfig(value=max_input_tokens),
                clear_at_least=ClearAtLeastConfig(
                    value=max_input_tokens - target_input_tokens,
                ),
                exclude_tools=list(TOOLS_CLEARABLE_USES),
            ),
        )

    if not strategies:
        return None

    return ContextManagementConfig(edits=strategies)
