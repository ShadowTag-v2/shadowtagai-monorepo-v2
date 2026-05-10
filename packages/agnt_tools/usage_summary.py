"""Tool usage summary generator.

Ported from Claude Code `toolUseSummary/toolUseSummaryGenerator.ts`.
Generates human-readable git-commit-style labels for completed tool
batches using a lightweight model query.

Architecture:
  - `generate_tool_usage_summary()` → async summary generation
  - `truncate_json()` → safe JSON truncation for prompts
  - `ToolInfo` → structured tool execution record
  - `format_tool_batch_summary()` → synchronous fallback formatter
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# --- Constants ---

TOOL_USE_SUMMARY_SYSTEM_PROMPT = """Write a short summary label describing what these tool calls accomplished. \
It appears as a single-line row in a mobile app and truncates around 30 characters, \
so think git-commit-subject, not sentence.

Keep the verb in past tense and the most distinctive noun. \
Drop articles, connectors, and long location context first.

Examples:
- Searched in auth/
- Fixed NPE in UserService
- Created signup endpoint
- Read config.json
- Ran failing tests"""


@dataclass
class ToolInfo:
  """Record of a single tool execution.

  Attributes:
      name: Tool name (e.g., 'read_file', 'run_command').
      input_data: Tool input parameters.
      output_data: Tool execution result.
  """

  name: str
  input_data: Any = None
  output_data: Any = None


def truncate_json(value: Any, max_length: int = 300) -> str:
  """Safely truncate a JSON-serialized value.

  Args:
      value: Value to serialize and truncate.
      max_length: Maximum string length (default 300).

  Returns:
      JSON string, truncated with '...' if needed.
  """
  try:
    serialized = json.dumps(value, separators=(",", ":"), default=str)
    if len(serialized) <= max_length:
      return serialized
    return serialized[: max_length - 3] + "..."
  except TypeError, ValueError:
    return "[unable to serialize]"


def format_tool_batch_summary(tools: list[ToolInfo]) -> str | None:
  """Generate a synchronous rule-based summary label.

  Fallback when async model query is unavailable.
  Uses heuristic rules to produce a git-commit-style label.

  Args:
      tools: List of completed tool executions.

  Returns:
      Summary string, or None if no tools provided.
  """
  if not tools:
    return None

  if len(tools) == 1:
    tool = tools[0]
    return _single_tool_label(tool)

  # Multiple tools — group by name
  tool_names = [t.name for t in tools]
  unique_names = list(dict.fromkeys(tool_names))  # preserve order, dedupe

  if len(unique_names) == 1:
    return f"{_verb_for_tool(unique_names[0])} {len(tools)} items"

  if len(unique_names) == 2:
    return f"{_verb_for_tool(unique_names[0])} + {_verb_for_tool(unique_names[1])}"

  return f"Executed {len(tools)} tool calls"


def build_summary_prompt(
  tools: list[ToolInfo],
  last_assistant_text: str | None = None,
) -> tuple[str, str]:
  """Build system and user prompts for model-based summary generation.

  This produces the prompts suitable for sending to a lightweight model
  (e.g., Gemini Flash, Haiku) to generate a concise summary label.

  Args:
      tools: List of completed tool executions.
      last_assistant_text: Optional last assistant message for context.

  Returns:
      Tuple of (system_prompt, user_prompt).
  """
  tool_summaries = "\n\n".join(
    f"Tool: {tool.name}\nInput: {truncate_json(tool.input_data)}\nOutput: {truncate_json(tool.output_data)}"
    for tool in tools
  )

  context_prefix = ""
  if last_assistant_text:
    context_prefix = (
      f"User's intent (from assistant's last message): {last_assistant_text[:200]}\n\n"
    )

  user_prompt = f"{context_prefix}Tools completed:\n\n{tool_summaries}\n\nLabel:"

  return TOOL_USE_SUMMARY_SYSTEM_PROMPT, user_prompt


# --- Private Helpers ---


_TOOL_VERB_MAP: dict[str, str] = {
  "read_file": "Read",
  "view_file": "Viewed",
  "write_to_file": "Created",
  "replace_file_content": "Edited",
  "multi_replace_file_content": "Edited",
  "run_command": "Ran",
  "grep_search": "Searched",
  "list_dir": "Listed",
  "search_web": "Searched web",
  "browser_subagent": "Browsed",
}


def _verb_for_tool(tool_name: str) -> str:
  """Map tool name to past-tense verb.

  Args:
      tool_name: Name of the tool.

  Returns:
      Past-tense verb string.
  """
  return _TOOL_VERB_MAP.get(tool_name, f"Used {tool_name}")


def _single_tool_label(tool: ToolInfo) -> str:
  """Generate a label for a single tool execution.

  Args:
      tool: Single tool execution record.

  Returns:
      Concise label string.
  """
  verb = _verb_for_tool(tool.name)

  # Try to extract a meaningful target from input
  target = _extract_target(tool)
  if target:
    # Truncate target to fit in ~30 chars
    max_target_len = 30 - len(verb) - 1
    if len(target) > max_target_len:
      target = target[: max_target_len - 3] + "..."
    return f"{verb} {target}"

  return verb


def _extract_target(tool: ToolInfo) -> str:
  """Extract the most meaningful target identifier from tool input.

  Args:
      tool: Tool execution record.

  Returns:
      Target string (file path, search query, etc.) or empty string.
  """
  if not tool.input_data:
    return ""

  if isinstance(tool.input_data, dict):
    # Common patterns in tool inputs
    for key in (
      "AbsolutePath",
      "TargetFile",
      "SearchPath",
      "Url",
      "CommandLine",
      "Query",
      "query",
    ):
      if key in tool.input_data:
        value = str(tool.input_data[key])
        # Extract basename for file paths
        if "/" in value:
          return value.rsplit("/", 1)[-1]
        return value

  return ""
