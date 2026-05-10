# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context window visualizer — ported from utils/analyzeContext.ts.

Provides a sovereign context window analysis engine that:
  1. Breaks down token usage by category (system prompt, tools, messages, etc.)
  2. Generates a visual grid for terminal/UI rendering
  3. Tracks message-level breakdowns (tool calls, results, attachments)
  4. Computes free space and autocompact thresholds

Stripped: ant-gates, GrowthBook feature flags, Anthropic SDK coupling,
bun:bundle feature guards, reactive-compact/context-collapse guards.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from packages.agnt_utils.token_estimate import (
  rough_token_estimate,
)

# ── Constants ─────────────────────────────────────────────────────────────────

MODEL_CONTEXT_WINDOW_DEFAULT = 200_000
AUTOCOMPACT_BUFFER_TOKENS = 33_000
MANUAL_COMPACT_BUFFER_TOKENS = 3_000
TOOL_TOKEN_COUNT_OVERHEAD = 500

_RESERVED_CATEGORY_NAME = "Autocompact buffer"
_MANUAL_COMPACT_BUFFER_NAME = "Compact buffer"

# ── Context window resolution ─────────────────────────────────────────────────

# Model substring → context window size.
# Sovereign: we control what models we support. No Anthropic-specific
# logic (has1mContext, modelSupports1M, antModel resolution).
_MODEL_CONTEXT_WINDOWS: dict[str, int] = {
  "gemini-3.1-pro": 1_000_000,
  "gemini-3.1-flash": 1_000_000,
  "gemini-3-pro": 1_000_000,
  "gemini-3-flash": 1_000_000,
  "gemini-2.5-pro": 1_000_000,
  "gemini-2.5-flash": 1_000_000,
  "opus-4": 200_000,
  "sonnet-4": 200_000,
  "haiku-4": 200_000,
}


def get_context_window_for_model(model: str) -> int:
  """Resolve context window size for a model.

  Precedence:
      1. AGNT_MAX_CONTEXT_TOKENS env override
      2. Model capability table lookup
      3. Default (200k)
  """
  env_override = os.environ.get("AGNT_MAX_CONTEXT_TOKENS", "")
  if env_override:
    try:
      val = int(env_override)
      if val > 0:
        return val
    except ValueError:
      pass

  m = model.lower()
  for pattern, window in _MODEL_CONTEXT_WINDOWS.items():
    if pattern in m:
      return window

  return MODEL_CONTEXT_WINDOW_DEFAULT


def calculate_context_percentages(
  current_usage: dict[str, int] | None,
  context_window_size: int,
) -> dict[str, int | None]:
  """Calculate context window usage percentage from token usage data."""
  if not current_usage:
    return {"used": None, "remaining": None}

  total_input = (
    current_usage.get("input_tokens", 0)
    + current_usage.get("cache_creation_input_tokens", 0)
    + current_usage.get("cache_read_input_tokens", 0)
  )
  used_pct = round((total_input / context_window_size) * 100)
  clamped = min(100, max(0, used_pct))
  return {"used": clamped, "remaining": 100 - clamped}


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class ContextCategory:
  """A named slice of the context window with token count and color."""

  name: str
  tokens: int
  color: str
  is_deferred: bool = False


@dataclass
class GridSquare:
  """One cell in the visual context grid."""

  color: str
  is_filled: bool
  category_name: str
  tokens: int
  percentage: int
  square_fullness: float  # 0.0–1.0


@dataclass
class MemoryFileDetail:
  """Token breakdown for a single memory/config file."""

  path: str
  file_type: str
  tokens: int


@dataclass
class McpToolDetail:
  """Token breakdown for a single MCP tool."""

  name: str
  server_name: str
  tokens: int
  is_loaded: bool = True


@dataclass
class ToolBreakdownEntry:
  """Token usage for a single tool type in messages."""

  name: str
  call_tokens: int = 0
  result_tokens: int = 0


@dataclass
class AttachmentBreakdownEntry:
  """Token usage for a single attachment type."""

  name: str
  tokens: int = 0


@dataclass
class MessageBreakdown:
  """Detailed breakdown of how message tokens are distributed."""

  total_tokens: int = 0
  tool_call_tokens: int = 0
  tool_result_tokens: int = 0
  attachment_tokens: int = 0
  assistant_message_tokens: int = 0
  user_message_tokens: int = 0
  tool_calls_by_type: dict[str, int] = field(default_factory=dict)
  tool_results_by_type: dict[str, int] = field(default_factory=dict)
  attachments_by_type: dict[str, int] = field(default_factory=dict)


@dataclass
class ContextData:
  """Full context window analysis result."""

  categories: list[ContextCategory]
  total_tokens: int
  max_tokens: int
  raw_max_tokens: int
  percentage: int
  grid_rows: list[list[GridSquare]]
  model: str
  memory_files: list[MemoryFileDetail]
  mcp_tools: list[McpToolDetail]
  agents: list[dict[str, Any]]
  is_auto_compact_enabled: bool
  auto_compact_threshold: int | None = None
  message_breakdown: MessageBreakdown | None = None
  api_usage: dict[str, int] | None = None
  skills: dict[str, Any] | None = None
  slash_commands: dict[str, Any] | None = None


# ── Message breakdown ─────────────────────────────────────────────────────────


def _json_dumps(obj: Any) -> str:
  """Compact JSON serialization for token estimation."""
  return json.dumps(obj, separators=(",", ":"), default=str)


def _process_assistant_message(
  msg: dict[str, Any],
  breakdown: MessageBreakdown,
) -> None:
  """Account tokens in an assistant message's content blocks."""
  inner = msg.get("message", {})
  if not isinstance(inner, dict):
    return
  for block in inner.get("content", []):
    block_str = _json_dumps(block)
    block_tokens = rough_token_estimate(block_str)

    if isinstance(block, dict) and block.get("type") == "tool_use":
      breakdown.tool_call_tokens += block_tokens
      tool_name = block.get("name", "unknown")
      breakdown.tool_calls_by_type[tool_name] = (
        breakdown.tool_calls_by_type.get(tool_name, 0) + block_tokens
      )
    else:
      breakdown.assistant_message_tokens += block_tokens


def _process_user_message(
  msg: dict[str, Any],
  breakdown: MessageBreakdown,
  tool_use_id_to_name: dict[str, str],
) -> None:
  """Account tokens in a user message's content blocks."""
  inner = msg.get("message", {})
  if not isinstance(inner, dict):
    return
  content = inner.get("content")

  if isinstance(content, str):
    breakdown.user_message_tokens += rough_token_estimate(content)
    return

  if not isinstance(content, list):
    return

  for block in content:
    block_str = _json_dumps(block)
    block_tokens = rough_token_estimate(block_str)

    if isinstance(block, dict) and block.get("type") == "tool_result":
      breakdown.tool_result_tokens += block_tokens
      tool_use_id = block.get("tool_use_id")
      tool_name = (
        tool_use_id_to_name.get(tool_use_id, "unknown") if tool_use_id else "unknown"
      )
      breakdown.tool_results_by_type[tool_name] = (
        breakdown.tool_results_by_type.get(tool_name, 0) + block_tokens
      )
    else:
      breakdown.user_message_tokens += block_tokens


def _process_attachment(
  msg: dict[str, Any],
  breakdown: MessageBreakdown,
) -> None:
  """Account tokens in an attachment message."""
  attachment = msg.get("attachment", {})
  tokens = rough_token_estimate(_json_dumps(attachment))
  breakdown.attachment_tokens += tokens
  attach_type = (
    attachment.get("type", "unknown") if isinstance(attachment, dict) else "unknown"
  )
  breakdown.attachments_by_type[attach_type] = (
    breakdown.attachments_by_type.get(attach_type, 0) + tokens
  )


def approximate_message_tokens(
  messages: list[dict[str, Any]],
) -> MessageBreakdown:
  """Build a detailed token breakdown from a list of messages.

  Walks through all messages and categorizes token usage into
  tool calls, tool results, attachments, assistant text, and user text.
  """
  breakdown = MessageBreakdown()

  # Build tool_use_id → name map from assistant messages
  tool_use_id_to_name: dict[str, str] = {}
  for msg in messages:
    if msg.get("type") != "assistant":
      continue
    inner = msg.get("message", {})
    if not isinstance(inner, dict):
      continue
    for block in inner.get("content", []):
      if (
        isinstance(block, dict) and block.get("type") == "tool_use" and block.get("id")
      ):
        tool_use_id_to_name[block["id"]] = block.get("name", "unknown")

  # Process each message
  for msg in messages:
    msg_type = msg.get("type", "")
    if msg_type == "assistant":
      _process_assistant_message(msg, breakdown)
    elif msg_type == "user":
      _process_user_message(msg, breakdown, tool_use_id_to_name)
    elif msg_type == "attachment":
      _process_attachment(msg, breakdown)

  # Total = sum of all categories
  breakdown.total_tokens = (
    breakdown.tool_call_tokens
    + breakdown.tool_result_tokens
    + breakdown.attachment_tokens
    + breakdown.assistant_message_tokens
    + breakdown.user_message_tokens
  )

  return breakdown


# ── Grid generation ───────────────────────────────────────────────────────────


def _create_category_squares(
  name: str,
  tokens: int,
  color: str,
  percentage: int,
  num_squares: int,
  context_window: int,
  total_squares: int,
) -> list[GridSquare]:
  """Generate GridSquare objects for a single category.

  Computes per-square fullness so the last square of a category
  can be rendered as partially filled (e.g. using opacity or
  fractional block characters).
  """
  squares: list[GridSquare] = []
  exact = (tokens / context_window) * total_squares if context_window else 0
  whole = int(exact)
  fractional = exact - whole

  for i in range(num_squares):
    fullness = 1.0
    if i == whole and fractional > 0:
      fullness = fractional

    squares.append(
      GridSquare(
        color=color,
        is_filled=True,
        category_name=name,
        tokens=tokens,
        percentage=percentage,
        square_fullness=fullness,
      )
    )
  return squares


def generate_grid(
  categories: list[ContextCategory],
  context_window: int,
  terminal_width: int | None = None,
) -> list[list[GridSquare]]:
  """Build a 2D grid of squares representing context window usage.

  Grid dimensions adapt to context window size and terminal width:
    - 200k models: 10×10 (narrow: 5×5)
    - 1M+ models:  20×10 (narrow: 5×10)
  """
  is_narrow = terminal_width is not None and terminal_width < 80

  if context_window >= 1_000_000:
    grid_width = 5 if is_narrow else 20
  else:
    grid_width = 5 if is_narrow else 10

  grid_height = 10 if context_window >= 1_000_000 else (5 if is_narrow else 10)
  total_squares = grid_width * grid_height

  # Filter deferred categories — they don't occupy real context space
  non_deferred = [c for c in categories if not c.is_deferred]

  # Compute squares per category
  cat_info: list[dict[str, Any]] = []
  for cat in non_deferred:
    raw_squares = (cat.tokens / context_window) * total_squares if context_window else 0
    if cat.name == "Free space":
      num_sq = round(raw_squares)
    else:
      num_sq = max(1, round(raw_squares))
    pct = round((cat.tokens / context_window) * 100) if context_window else 0
    cat_info.append(
      {
        "name": cat.name,
        "tokens": cat.tokens,
        "color": cat.color,
        "squares": num_sq,
        "percentage": pct,
      }
    )

  # Separate reserved, free, and content categories
  reserved = None
  free_space = None
  content_cats = []
  for ci in cat_info:
    if ci["name"] in (_RESERVED_CATEGORY_NAME, _MANUAL_COMPACT_BUFFER_NAME):
      reserved = ci
    elif ci["name"] == "Free space":
      free_space = ci
    else:
      content_cats.append(ci)

  reserved_sq_count = reserved["squares"] if reserved else 0

  # Build flat grid: content → free space → reserved
  grid_squares: list[GridSquare] = []

  for ci in content_cats:
    sqs = _create_category_squares(
      ci["name"],
      ci["tokens"],
      ci["color"],
      ci["percentage"],
      ci["squares"],
      context_window,
      total_squares,
    )
    for sq in sqs:
      if len(grid_squares) < total_squares:
        grid_squares.append(sq)

  # Fill free space up to (total - reserved)
  free_target = total_squares - reserved_sq_count
  while len(grid_squares) < free_target:
    grid_squares.append(
      GridSquare(
        color="promptBorder",
        is_filled=True,
        category_name="Free space",
        tokens=free_space["tokens"] if free_space else 0,
        percentage=free_space["percentage"] if free_space else 0,
        square_fullness=1.0,
      )
    )

  # Append reserved at the end
  if reserved:
    sqs = _create_category_squares(
      reserved["name"],
      reserved["tokens"],
      reserved["color"],
      reserved["percentage"],
      reserved["squares"],
      context_window,
      total_squares,
    )
    for sq in sqs:
      if len(grid_squares) < total_squares:
        grid_squares.append(sq)

  # Convert to rows
  rows: list[list[GridSquare]] = []
  for i in range(grid_height):
    rows.append(grid_squares[i * grid_width : (i + 1) * grid_width])

  return rows


# ── Main analysis ─────────────────────────────────────────────────────────────


def analyze_context_usage(
  messages: list[dict[str, Any]],
  model: str,
  *,
  system_prompt_tokens: int = 0,
  builtin_tool_tokens: int = 0,
  mcp_tool_tokens: int = 0,
  mcp_tool_details: list[McpToolDetail] | None = None,
  deferred_tool_tokens: int = 0,
  agent_tokens: int = 0,
  agent_details: list[dict[str, Any]] | None = None,
  memory_tokens: int = 0,
  memory_files: list[MemoryFileDetail] | None = None,
  skill_tokens: int = 0,
  skill_info: dict[str, Any] | None = None,
  slash_command_tokens: int = 0,
  slash_command_info: dict[str, Any] | None = None,
  is_auto_compact: bool = True,
  terminal_width: int | None = None,
  api_usage: dict[str, int] | None = None,
) -> ContextData:
  """Analyze context window usage and produce a renderable breakdown.

  This is the sovereign equivalent of ``analyzeContextUsage``.
  Callers provide pre-computed token counts for each category
  (system prompt, tools, agents, memory, skills) since those
  computations are environment-specific.

  The function builds categories, computes the visual grid,
  and returns a complete ``ContextData`` for rendering.
  """
  context_window = get_context_window_for_model(model)
  msg_breakdown = approximate_message_tokens(messages)
  message_tokens = msg_breakdown.total_tokens

  # Autocompact threshold
  auto_compact_threshold: int | None = None
  if is_auto_compact:
    effective_window = context_window  # sovereign: no separate effective calc
    auto_compact_threshold = effective_window - AUTOCOMPACT_BUFFER_TOKENS

  # ── Build categories ──────────────────────────────────────────────────
  cats: list[ContextCategory] = []

  if system_prompt_tokens > 0:
    cats.append(ContextCategory("System prompt", system_prompt_tokens, "promptBorder"))

  system_tools_tokens = builtin_tool_tokens - skill_tokens
  if system_tools_tokens > 0:
    cats.append(ContextCategory("System tools", system_tools_tokens, "inactive"))

  if mcp_tool_tokens > 0:
    cats.append(ContextCategory("MCP tools", mcp_tool_tokens, "cyan"))

  if deferred_tool_tokens > 0:
    cats.append(
      ContextCategory(
        "MCP tools (deferred)", deferred_tool_tokens, "inactive", is_deferred=True
      )
    )

  if agent_tokens > 0:
    cats.append(ContextCategory("Custom agents", agent_tokens, "permission"))

  if memory_tokens > 0:
    cats.append(ContextCategory("Memory files", memory_tokens, "claude"))

  if skill_tokens > 0:
    cats.append(ContextCategory("Skills", skill_tokens, "warning"))

  if message_tokens > 0:
    cats.append(ContextCategory("Messages", message_tokens, "purple"))

  # Actual usage (non-deferred)
  actual_usage = sum(c.tokens for c in cats if not c.is_deferred)

  # Reserved buffer
  reserved_tokens = 0
  if is_auto_compact and auto_compact_threshold is not None:
    reserved_tokens = context_window - auto_compact_threshold
    cats.append(ContextCategory(_RESERVED_CATEGORY_NAME, reserved_tokens, "inactive"))
  elif not is_auto_compact:
    reserved_tokens = MANUAL_COMPACT_BUFFER_TOKENS
    cats.append(
      ContextCategory(_MANUAL_COMPACT_BUFFER_NAME, reserved_tokens, "inactive")
    )

  # Free space
  free_tokens = max(0, context_window - actual_usage - reserved_tokens)
  cats.append(ContextCategory("Free space", free_tokens, "promptBorder"))

  # Total for display (excluding free space and reserved)
  total_display = actual_usage

  # Prefer API usage total if available
  if api_usage:
    api_total = (
      api_usage.get("input_tokens", 0)
      + api_usage.get("cache_creation_input_tokens", 0)
      + api_usage.get("cache_read_input_tokens", 0)
    )
    final_total = api_total
  else:
    final_total = total_display

  # Generate grid
  grid_rows = generate_grid(cats, context_window, terminal_width)

  # Format tool breakdown for output
  tools_map: dict[str, dict[str, int]] = {}
  for name, tokens in msg_breakdown.tool_calls_by_type.items():
    tools_map.setdefault(name, {"call_tokens": 0, "result_tokens": 0})
    tools_map[name]["call_tokens"] += tokens
  for name, tokens in msg_breakdown.tool_results_by_type.items():
    tools_map.setdefault(name, {"call_tokens": 0, "result_tokens": 0})
    tools_map[name]["result_tokens"] += tokens

  return ContextData(
    categories=cats,
    total_tokens=final_total,
    max_tokens=context_window,
    raw_max_tokens=context_window,
    percentage=round((final_total / context_window) * 100) if context_window else 0,
    grid_rows=grid_rows,
    model=model,
    memory_files=memory_files or [],
    mcp_tools=mcp_tool_details or [],
    agents=agent_details or [],
    is_auto_compact_enabled=is_auto_compact,
    auto_compact_threshold=auto_compact_threshold,
    message_breakdown=msg_breakdown,
    api_usage=api_usage,
    skills=skill_info,
    slash_commands=slash_command_info,
  )
