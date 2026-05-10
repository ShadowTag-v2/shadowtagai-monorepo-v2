# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Token estimation — ported from services/tokenEstimation.ts.

Provides rough (heuristic) token count estimation without needing
an API call.  Used by context_compactor, session_memory_compact,
and any module that needs to decide whether a message fits within
a token budget before calling the real tokenizer.

The canonical formula is ``len(text) / bytes_per_token``, where
``bytes_per_token`` varies by content type (JSON ≈ 2, prose ≈ 4).
"""

from __future__ import annotations

import json
from typing import Any


# ── Core estimation ───────────────────────────────────────────────────────────


def rough_token_estimate(content: str, bytes_per_token: int = 4) -> int:
  """Estimate token count from character length.

  This matches the upstream ``roughTokenCountEstimation`` exactly:
  ``Math.round(content.length / bytesPerToken)``.

  Args:
      content: Input text.
      bytes_per_token: Average chars per token. Default 4 (prose).

  Returns:
      Estimated token count.
  """
  if not content:
    return 0
  return round(len(content) / bytes_per_token)


# ── File-type-aware estimation ────────────────────────────────────────────────

_JSON_EXTENSIONS = frozenset({"json", "jsonl", "jsonc"})


def bytes_per_token_for_file_type(file_extension: str) -> int:
  """Return the appropriate bytes-per-token ratio for a file type.

  Dense JSON has many single-character tokens (``{``, ``}``, ``:``,
  ``,``, ``"``), so the real ratio is closer to 2 rather than the
  default 4.

  Args:
      file_extension: File extension without the dot (e.g. ``"json"``).

  Returns:
      Estimated bytes per token for the given file type.
  """
  return 2 if file_extension.lower() in _JSON_EXTENSIONS else 4


def rough_token_estimate_for_file_type(
  content: str,
  file_extension: str,
) -> int:
  """Like :func:`rough_token_estimate` but uses a more accurate ratio
  when the file type is known.

  This matters when the API-based token count is unavailable and we
  fall back to the rough estimate — an underestimate can let an
  oversized tool result slip into the conversation.
  """
  return rough_token_estimate(
    content,
    bytes_per_token_for_file_type(file_extension),
  )


# ── Message-level estimation ─────────────────────────────────────────────────

# Maximum tokens assumed for an image/document block.
# Matches microCompact's IMAGE_MAX_TOKEN_SIZE.
IMAGE_MAX_TOKEN_SIZE = 2000


def rough_token_estimate_for_block(block: dict[str, Any] | str) -> int:
  """Estimate token count for a single content block.

  Handles text, image, document, tool_use, tool_result, thinking,
  and redacted_thinking blocks — matching the upstream
  ``roughTokenCountEstimationForBlock`` logic.
  """
  if isinstance(block, str):
    return rough_token_estimate(block)

  block_type = block.get("type", "")

  if block_type == "text":
    return rough_token_estimate(block.get("text", ""))

  if block_type in ("image", "document"):
    return IMAGE_MAX_TOKEN_SIZE

  if block_type == "tool_result":
    content = block.get("content")
    if content is None:
      return 0
    return rough_token_estimate_for_content(content)

  if block_type == "tool_use":
    name = block.get("name", "")
    input_data = block.get("input", {})
    return rough_token_estimate(name + json.dumps(input_data, default=str))

  if block_type == "thinking":
    return rough_token_estimate(block.get("thinking", ""))

  if block_type == "redacted_thinking":
    return rough_token_estimate(block.get("data", ""))

  # Fallback — stringify the block
  return rough_token_estimate(json.dumps(block, default=str))


def rough_token_estimate_for_content(
  content: str | list[dict[str, Any] | str] | None,
) -> int:
  """Estimate token count for a message content field.

  Content can be a plain string, a list of content blocks, or None.
  """
  if content is None:
    return 0
  if isinstance(content, str):
    return rough_token_estimate(content)

  total = 0
  for block in content:
    total += rough_token_estimate_for_block(block)
  return total


def rough_token_estimate_for_message(
  message: dict[str, Any],
) -> int:
  """Estimate token count for a single Message dict.

  Expects a dict with ``type`` (``"assistant"`` | ``"user"`` |
  ``"attachment"``) and optional ``message.content``.
  """
  msg_type = message.get("type", "")

  if msg_type in ("assistant", "user"):
    inner = message.get("message", {})
    content = inner.get("content") if isinstance(inner, dict) else None
    return rough_token_estimate_for_content(content)

  # For attachment messages, estimate from the attachment's text representation
  if msg_type == "attachment":
    attachment = message.get("attachment", {})
    if isinstance(attachment, dict):
      text = attachment.get("text", "")
      if text:
        return rough_token_estimate(text)
    return 0

  return 0


def rough_token_estimate_for_messages(
  messages: list[dict[str, Any]],
) -> int:
  """Estimate total token count across a list of messages.

  This is the canonical function for estimating tokens when the
  API-based count is unavailable. Matches the upstream
  ``roughTokenCountEstimationForMessages``.
  """
  total = 0
  for msg in messages:
    total += rough_token_estimate_for_message(msg)
  return total


# ── Usage-based token counting ────────────────────────────────────────────────


def get_token_count_from_usage(usage: dict[str, int]) -> int:
  """Calculate total context window tokens from an API response's usage data.

  Includes ``input_tokens`` + cache tokens + ``output_tokens``.
  This represents the full context size at the time of that API call.
  """
  return (
    usage.get("input_tokens", 0)
    + usage.get("cache_creation_input_tokens", 0)
    + usage.get("cache_read_input_tokens", 0)
    + usage.get("output_tokens", 0)
  )


def token_count_with_estimation(
  messages: list[dict[str, Any]],
) -> int:
  """Get the current context window size in tokens.

  This is the CANONICAL function for measuring context size when
  checking thresholds (autocompact, session memory init, etc.).
  Uses the last API response's token count plus estimates for any
  messages added since.

  Walks backward through messages to find the last one with usage
  data, then estimates tokens for everything after it.

  Falls back to pure rough estimation if no usage data is found.
  """
  for i in range(len(messages) - 1, -1, -1):
    msg = messages[i]
    if msg.get("type") != "assistant":
      continue
    inner = msg.get("message", {})
    if not isinstance(inner, dict):
      continue
    usage = inner.get("usage")
    if usage and isinstance(usage, dict) and "input_tokens" in usage:
      base = get_token_count_from_usage(usage)
      remaining = messages[i + 1 :]
      return base + rough_token_estimate_for_messages(remaining)

  return rough_token_estimate_for_messages(messages)
