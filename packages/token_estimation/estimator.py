"""Local-first token estimation engine.

Ported from Claude Code ``src/services/tokenEstimation.ts``.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_BYTES_PER_TOKEN = 4
IMAGE_MAX_TOKEN_SIZE = 2000


def rough_token_estimate(
  content: str, bytes_per_token: int = DEFAULT_BYTES_PER_TOKEN
) -> int:
  """Estimate token count from raw string content."""
  if not content:
    return 0
  return max(1, round(len(content) / bytes_per_token))


def bytes_per_token_for_file_type(file_extension: str) -> int:
  """Return a file-type-aware bytes-per-token ratio."""
  if file_extension in ("json", "jsonl", "jsonc"):
    return 2
  return DEFAULT_BYTES_PER_TOKEN


def rough_token_estimate_for_file_type(content: str, file_extension: str) -> int:
  """Estimate tokens using a file-type-aware bytes-per-token ratio."""
  return rough_token_estimate(content, bytes_per_token_for_file_type(file_extension))


def rough_token_estimate_for_block(block: dict[str, Any] | str) -> int:
  """Estimate tokens for a single content block."""
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
    if isinstance(content, str):
      return rough_token_estimate(content)
    if isinstance(content, list):
      return sum(rough_token_estimate_for_block(b) for b in content)
    return 0

  if block_type == "tool_use":
    name = block.get("name", "")
    input_data = block.get("input", {})
    try:
      serialized = name + json.dumps(input_data, separators=(",", ":"))
    except (TypeError, ValueError):
      serialized = name + str(input_data)
    return rough_token_estimate(serialized)

  if block_type == "thinking":
    return rough_token_estimate(block.get("thinking", ""))

  if block_type == "redacted_thinking":
    return rough_token_estimate(block.get("data", ""))

  try:
    serialized = json.dumps(block, separators=(",", ":"))
  except (TypeError, ValueError):
    serialized = str(block)
  return rough_token_estimate(serialized)


def rough_token_estimate_for_content(
  content: str | list[dict[str, Any]] | None,
) -> int:
  """Estimate tokens for message content (string or block list)."""
  if content is None:
    return 0
  if isinstance(content, str):
    return rough_token_estimate(content)
  return sum(rough_token_estimate_for_block(b) for b in content)


def rough_token_estimate_for_messages(messages: list[dict[str, Any]]) -> int:
  """Estimate total tokens across a list of messages."""
  total = 0
  for msg in messages:
    msg_type = msg.get("type", "")
    if msg_type in ("assistant", "user"):
      inner = msg.get("message", {})
      content = inner.get("content") if isinstance(inner, dict) else None
      total += rough_token_estimate_for_content(content)
    elif msg_type == "attachment":
      attachment = msg.get("attachment", {})
      if isinstance(attachment, dict):
        att_content = attachment.get("content", "")
        if isinstance(att_content, str):
          total += rough_token_estimate(att_content)
  return total
