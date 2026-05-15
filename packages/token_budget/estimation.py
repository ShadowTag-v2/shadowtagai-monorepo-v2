# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Token Estimation — Vendor-agnostic rough token counting.

Ported from src/services/tokenEstimation.ts (Claude Code v2.1.91).

Provides fast, offline token estimation when API-based counting is
unavailable (e.g. rate-limited, offline dev, CI). The rough estimates
are intentionally conservative to avoid underestimating and blowing
the context window.

Architecture:
    - rough_token_count:               character-length / bytes_per_token ratio
    - bytes_per_token_for_file_type:   file-extension-specific ratio (json=2, default=4)
    - rough_token_count_for_file:      combines the above two
    - rough_token_count_for_messages:  message-level estimation (Gemini content blocks)
    - rough_token_count_for_block:     block-level estimation (text, image, tool, thinking)

Reference: Claude Code v2.1.91 tokenEstimation.ts
Reference: context_compactor pipeline for integration
"""

from __future__ import annotations

import json
import math
from typing import Any

__all__ = [
  "IMAGE_MAX_TOKEN_SIZE",
  "THINKING_BUDGET_TOKENS",
  "TOKEN_COUNT_MAX_TOKENS",
  "bytes_per_token_for_file_type",
  "rough_token_count",
  "rough_token_count_for_block",
  "rough_token_count_for_content",
  "rough_token_count_for_file",
  "rough_token_count_for_messages",
]

# ── Constants from tokenEstimation.ts ──

# Conservative upper bound for image/document tokens.
# Matches microCompact's calculateToolResultTokens and the
# formula (width_px * height_px) / 750 capped at 2000x2000 → ~5333.
# We use 2000 as a safe estimate that avoids under-counting.
IMAGE_MAX_TOKEN_SIZE: int = 2000

# Minimal values for token counting with thinking enabled.
# API constraint: max_tokens must be greater than thinking.budget_tokens.
THINKING_BUDGET_TOKENS: int = 1024
TOKEN_COUNT_MAX_TOKENS: int = 2048

# File extension → bytes-per-token ratio.
# Dense JSON has many single-character tokens ({, }, :, , ")
# which makes the real ratio closer to 2 rather than the default 4.
_FILE_TYPE_RATIOS: dict[str, int] = {
  "json": 2,
  "jsonl": 2,
  "jsonc": 2,
}
_DEFAULT_BYTES_PER_TOKEN: int = 4


# ── Core Estimation Functions ──


def rough_token_count(
  content: str, bytes_per_token: int = _DEFAULT_BYTES_PER_TOKEN
) -> int:
  """Estimate token count from string length.

  This is the most basic estimation: len(content) / bytes_per_token.
  Intentionally rounds up to be conservative.

  Args:
      content: Text content to estimate.
      bytes_per_token: Ratio of characters to tokens. Default 4.

  Returns:
      Estimated token count (always >= 0).
  """
  if not content:
    return 0
  return math.ceil(len(content) / bytes_per_token)


def bytes_per_token_for_file_type(file_extension: str) -> int:
  """Return the estimated bytes-per-token ratio for a file extension.

  Dense formats like JSON have many single-character tokens, yielding
  a lower ratio (more tokens per byte).

  Args:
      file_extension: File extension WITHOUT the dot (e.g. "json", "py").

  Returns:
      Bytes-per-token ratio (2 for JSON, 4 for everything else).
  """
  return _FILE_TYPE_RATIOS.get(
    file_extension.lower().lstrip("."), _DEFAULT_BYTES_PER_TOKEN
  )


def rough_token_count_for_file(content: str, file_extension: str) -> int:
  """Estimate token count using file-type-aware ratio.

  This matters when the API-based count is unavailable — an
  underestimate can let an oversized tool result slip into the
  conversation.

  Args:
      content: File content to estimate.
      file_extension: File extension (with or without dot).

  Returns:
      Estimated token count.
  """
  return rough_token_count(content, bytes_per_token_for_file_type(file_extension))


# ── Block-Level Estimation (Gemini / LLM content blocks) ──


def rough_token_count_for_block(block: dict[str, Any] | str) -> int:
  """Estimate token count for a single content block.

  Handles the common block types found in Gemini / Anthropic messages:
  - text: direct character counting
  - image / document: fixed conservative estimate (IMAGE_MAX_TOKEN_SIZE)
  - tool_use / functionCall: serialize input + name
  - tool_result / functionResponse: recurse into content
  - thinking / redacted_thinking: character counting on thinking text
  - fallback: JSON stringify for unknown block types

  Args:
      block: A content block dict (with 'type' or Gemini 'parts' format),
             or a plain string.

  Returns:
      Estimated token count.
  """
  if isinstance(block, str):
    return rough_token_count(block)

  block_type = block.get("type", "")

  # Text blocks (Anthropic format)
  if block_type == "text":
    return rough_token_count(block.get("text", ""))

  # Image and document blocks — use conservative fixed estimate
  if block_type in ("image", "document", "inlineData"):
    return IMAGE_MAX_TOKEN_SIZE

  # Tool use blocks (Anthropic: tool_use, Gemini: functionCall)
  if block_type == "tool_use":
    name = block.get("name", "")
    input_data = block.get("input", {})
    return rough_token_count(name + _safe_json_stringify(input_data))

  # Gemini function call format
  if block_type == "functionCall" or "functionCall" in block:
    fc = block.get("functionCall", block)
    name = fc.get("name", "")
    args = fc.get("args", {})
    return rough_token_count(name + _safe_json_stringify(args))

  # Tool result blocks — recurse into content
  if block_type in ("tool_result", "functionResponse"):
    content = block.get("content", block.get("response", ""))
    return rough_token_count_for_content(content)

  # Thinking blocks (Anthropic extended thinking)
  if block_type == "thinking":
    return rough_token_count(block.get("thinking", ""))

  # Redacted thinking blocks
  if block_type == "redacted_thinking":
    return rough_token_count(block.get("data", ""))

  # Gemini inline text parts
  if "text" in block and block_type == "":
    return rough_token_count(block["text"])

  # Fallback: stringify the entire block
  return rough_token_count(_safe_json_stringify(block))


def rough_token_count_for_content(
  content: str | list[dict[str, Any] | str] | dict[str, Any] | None,
) -> int:
  """Estimate token count for message content (string, block list, or dict).

  Args:
      content: Message content — can be a string, a list of content blocks,
               a single block dict, or None.

  Returns:
      Estimated token count.
  """
  if content is None:
    return 0
  if isinstance(content, str):
    return rough_token_count(content)
  if isinstance(content, dict):
    return rough_token_count_for_block(content)
  if isinstance(content, list):
    return sum(rough_token_count_for_block(b) for b in content)
  return 0


def rough_token_count_for_messages(
  messages: list[dict[str, Any]],
) -> int:
  """Estimate total token count for a list of messages.

  Supports both Anthropic-style messages (role + content) and
  Gemini-style messages (role + parts).

  Each message has ~4 tokens overhead for role/structure framing.

  Args:
      messages: List of message dicts.

  Returns:
      Total estimated token count across all messages.
  """
  total = 0
  message_overhead = 4  # role + structural tokens per message

  for msg in messages:
    total += message_overhead

    # Anthropic format: { role, content }
    content = msg.get("content")
    if content is not None:
      total += rough_token_count_for_content(content)
      continue

    # Gemini format: { role, parts: [...] }
    parts = msg.get("parts")
    if parts is not None and isinstance(parts, list):
      for part in parts:
        total += rough_token_count_for_block(part)
      continue

  return total


def _safe_json_stringify(obj: Any) -> str:
  """Safely serialize an object to JSON string for token estimation.

  Falls back to str() if JSON serialization fails.
  """
  try:
    return json.dumps(obj, separators=(",", ":"), default=str)
  except (TypeError, ValueError, OverflowError):
    return str(obj)
