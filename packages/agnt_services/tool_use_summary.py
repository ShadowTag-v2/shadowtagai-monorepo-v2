# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool Use Summary Generator — Batch 6 port from Claude Code v2.1.91.

Generates human-readable summaries of completed tool batches.
Used by the SDK to provide high-level progress updates to clients.

Ported from: external_repos/claude_code_services/toolUseSummary/toolUseSummaryGenerator.ts
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# System prompt for tool use summary generation
TOOL_USE_SUMMARY_SYSTEM_PROMPT = (
  "Write a short summary label describing what these tool calls accomplished. "
  "It appears as a single-line row in a mobile app and truncates around 30 characters, "
  "so think git-commit-subject, not sentence.\n\n"
  "Keep the verb in past tense and the most distinctive noun. "
  "Drop articles, connectors, and long location context first.\n\n"
  "Examples:\n"
  "- Searched in auth/\n"
  "- Fixed NPE in UserService\n"
  "- Created signup endpoint\n"
  "- Read config.json\n"
  "- Ran failing tests"
)


@dataclass(frozen=True, slots=True)
class ToolInfo:
  """Information about a single tool invocation."""

  name: str
  input: Any
  output: Any


def truncate_json(value: Any, max_length: int = 300) -> str:
  """Truncate a JSON value to a maximum length for the prompt."""
  try:
    s = json.dumps(value, default=str)
    if len(s) <= max_length:
      return s
    return s[: max_length - 3] + "..."
  except TypeError, ValueError:
    return "[unable to serialize]"


def build_tool_summary_prompt(
  tools: list[ToolInfo],
  last_assistant_text: str | None = None,
) -> str:
  """Build the prompt for tool use summary generation.

  This can be sent to any LLM backend (Gemini, etc.) for summary generation.

  Args:
      tools: List of completed tool invocations.
      last_assistant_text: Optional last assistant message for context.

  Returns:
      Formatted prompt string.
  """
  if not tools:
    return ""

  tool_summaries = "\n\n".join(
    f"Tool: {t.name}\nInput: {truncate_json(t.input)}\nOutput: {truncate_json(t.output)}"
    for t in tools
  )

  context_prefix = ""
  if last_assistant_text:
    context_prefix = (
      f"User's intent (from assistant's last message): {last_assistant_text[:200]}\n\n"
    )

  return f"{context_prefix}Tools completed:\n\n{tool_summaries}\n\nLabel:"


def generate_tool_use_summary_local(
  tools: list[ToolInfo],
  last_assistant_text: str | None = None,
) -> str | None:
  """Generate a tool use summary locally without an LLM call.

  Uses heuristic rules based on tool names and inputs.
  Falls back to the first tool's name if no pattern matches.

  Args:
      tools: List of completed tool invocations.
      last_assistant_text: Unused, kept for API compatibility.

  Returns:
      A brief summary string, or None if no tools provided.
  """
  if not tools:
    return None

  if len(tools) == 1:
    tool = tools[0]
    name = tool.name.replace("_", " ").title()
    # Extract key info from input if available
    if isinstance(tool.input, dict):
      path = tool.input.get("path") or tool.input.get("file_path")
      if path:
        # Use basename for brevity
        basename = path.rsplit("/", 1)[-1] if "/" in path else path
        return f"{name}: {basename}"
      query = tool.input.get("query") or tool.input.get("search")
      if query:
        truncated = query[:25] + "..." if len(query) > 25 else query
        return f"{name}: {truncated}"
    return name

  # Multiple tools — summarize by most common tool name
  from collections import Counter

  counts = Counter(t.name for t in tools)
  most_common_name, most_common_count = counts.most_common(1)[0]
  verb = most_common_name.replace("_", " ").rstrip("s")

  if len(counts) == 1:
    return f"{verb.title()} ({most_common_count}×)"
  return f"{verb.title()} + {len(tools) - most_common_count} other tools"
