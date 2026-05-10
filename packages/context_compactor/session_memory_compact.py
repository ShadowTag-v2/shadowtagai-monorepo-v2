# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session Memory Compaction — index-based message preservation.

Ported from: compact/sessionMemoryCompact.ts
Reference: AGNT STATE B Spec P3.3

This module implements the critical index calculation and API invariant
preservation logic that prevents splitting tool_use/tool_result pairs
during compaction. It is the bridge between the memory scoring system
(session_memory.py) and the auto-compact middleware (auto_compact.py).

Key invariants:
  1. tool_result blocks must always have their matching tool_use in scope
  2. Thinking blocks sharing a message.id must be kept together
  3. Compact boundary messages are filtered from the kept range
  4. Minimum token and text-block-message counts are respected
  5. Maximum token cap prevents runaway expansion

Design from upstream (sessionMemoryCompact.ts):
  - DEFAULT_MIN_TOKENS = 10_000 (minimum to preserve)
  - DEFAULT_MIN_TEXT_BLOCK_MESSAGES = 5 (minimum text interactions)
  - DEFAULT_MAX_TOKENS = 40_000 (hard cap for kept messages)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from context_compactor.token_estimator import rough_token_estimate

logger = logging.getLogger(__name__)


# ── Configuration ──────────────────────────────────────────────────────────────


@dataclass
class SessionMemoryCompactConfig:
  """Configuration for session memory compaction thresholds."""

  min_tokens: int = 10_000
  min_text_block_messages: int = 5
  max_tokens: int = 40_000


# Module-level config (matches upstream singleton pattern)
_config = SessionMemoryCompactConfig()
_config_initialized = False


def set_session_memory_compact_config(
  config: SessionMemoryCompactConfig | None = None,
  *,
  min_tokens: int | None = None,
  min_text_block_messages: int | None = None,
  max_tokens: int | None = None,
) -> None:
  """Set the session memory compact configuration.

  Can accept a full config object or keyword overrides.
  """
  global _config
  if config is not None:
    _config = config
  else:
    if min_tokens is not None and min_tokens > 0:
      _config.min_tokens = min_tokens
    if min_text_block_messages is not None and min_text_block_messages > 0:
      _config.min_text_block_messages = min_text_block_messages
    if max_tokens is not None and max_tokens > 0:
      _config.max_tokens = max_tokens


def get_session_memory_compact_config() -> SessionMemoryCompactConfig:
  """Get the current session memory compact configuration."""
  return SessionMemoryCompactConfig(
    min_tokens=_config.min_tokens,
    min_text_block_messages=_config.min_text_block_messages,
    max_tokens=_config.max_tokens,
  )


def reset_session_memory_compact_config() -> None:
  """Reset config state (useful for testing)."""
  global _config, _config_initialized
  _config = SessionMemoryCompactConfig()
  _config_initialized = False


# ── Message Introspection ──────────────────────────────────────────────────────


def has_text_blocks(message: dict[str, Any]) -> bool:
  """Check if a message contains text blocks.

  A message has text blocks if it's an assistant message with text content,
  or a user message with string/text-block content.
  """
  role = message.get("role", "")
  content = message.get("content", "")

  if role == "assistant":
    if isinstance(content, list):
      return any(
        isinstance(block, dict) and block.get("type") == "text" for block in content
      )
    return bool(content)  # string content counts

  if role == "user":
    if isinstance(content, str):
      return len(content) > 0
    if isinstance(content, list):
      return any(
        isinstance(block, dict) and block.get("type") == "text" for block in content
      )

  return False


def _get_tool_result_ids(message: dict[str, Any]) -> list[str]:
  """Extract tool_use_ids from tool_result blocks in a user message."""
  if message.get("role") != "user":
    return []
  content = message.get("content", [])
  if not isinstance(content, list):
    return []
  return [
    block["tool_use_id"]
    for block in content
    if isinstance(block, dict)
    and block.get("type") == "tool_result"
    and "tool_use_id" in block
  ]


def _has_tool_use_with_ids(
  message: dict[str, Any],
  tool_use_ids: set[str],
) -> bool:
  """Check if an assistant message contains tool_use blocks with given IDs."""
  if message.get("role") != "assistant":
    return False
  content = message.get("content", [])
  if not isinstance(content, list):
    return False
  return any(
    isinstance(block, dict)
    and block.get("type") == "tool_use"
    and block.get("id") in tool_use_ids
    for block in content
  )


def _is_compact_boundary(message: dict[str, Any]) -> bool:
  """Check if a message is a compact boundary marker."""
  return bool(message.get("compact_boundary", False)) or bool(
    message.get("compactMetadata")
  )


def _estimate_single_message_tokens(message: dict[str, Any]) -> int:
  """Estimate tokens for a single message dict."""
  content = message.get("content", "")
  if isinstance(content, str):
    return rough_token_estimate(content)
  if isinstance(content, list):
    total = 0
    for block in content:
      if isinstance(block, dict):
        text = block.get("text", "")
        if text:
          total += rough_token_estimate(str(text))
        # Tool results can be large
        tool_content = block.get("content", "")
        if tool_content and isinstance(tool_content, str):
          total += rough_token_estimate(tool_content)
    return total
  return 0


# ── Core Invariant Logic ───────────────────────────────────────────────────────


def adjust_index_to_preserve_api_invariants(
  messages: list[dict[str, Any]],
  start_index: int,
) -> int:
  """Adjust start index to ensure no tool_use/tool_result pairs are split.

  This is the critical safety function ported from
  `adjustIndexToPreserveAPIInvariants` in sessionMemoryCompact.ts.

  It handles two scenarios:

  1. **Tool pair preservation**: If any message in the kept range
     (start_index..end) contains tool_result blocks, the matching
     tool_use blocks must also be in the kept range. If they're not,
     the index is adjusted backwards to include them.

  2. **Thinking block preservation**: If an assistant message in the
     kept range shares a message_id with a preceding assistant message
     (which may contain thinking blocks), the index is adjusted to
     include those thinking blocks so they can be properly merged.

  Bug scenarios this prevents:
    - Orphan tool_result referencing non-existent tool_use → API error
    - Split thinking blocks → lost reasoning context

  Args:
      messages: Full message list.
      start_index: Proposed start index for kept messages.

  Returns:
      Adjusted start index (always <= original start_index).
  """
  if start_index <= 0 or start_index >= len(messages):
    return start_index

  adjusted = start_index

  # ── Step 1: Handle tool_use/tool_result pairs ──────────────────────────
  # Collect ALL tool_result IDs from the kept range
  all_tool_result_ids: list[str] = []
  for i in range(start_index, len(messages)):
    all_tool_result_ids.extend(_get_tool_result_ids(messages[i]))

  if all_tool_result_ids:
    # Collect tool_use IDs already in the kept range
    tool_use_ids_in_kept: set[str] = set()
    for i in range(adjusted, len(messages)):
      msg = messages[i]
      if msg.get("role") == "assistant":
        content = msg.get("content", [])
        if isinstance(content, list):
          for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
              tool_use_ids_in_kept.add(block["id"])

    # Only look for tool_uses NOT already in the kept range
    needed_ids = {tid for tid in all_tool_result_ids if tid not in tool_use_ids_in_kept}

    # Walk backwards to find assistant messages with matching tool_use blocks
    i = adjusted - 1
    while i >= 0 and needed_ids:
      msg = messages[i]
      if _has_tool_use_with_ids(msg, needed_ids):
        adjusted = i
        # Remove found IDs
        if msg.get("role") == "assistant":
          content = msg.get("content", [])
          if isinstance(content, list):
            for block in content:
              if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("id") in needed_ids
              ):
                needed_ids.discard(block["id"])
      i -= 1

  # ── Step 2: Handle thinking blocks sharing message_id ──────────────────
  # Collect message IDs from assistant messages in the kept range
  message_ids_in_kept: set[str] = set()
  for i in range(adjusted, len(messages)):
    msg = messages[i]
    if msg.get("role") == "assistant":
      msg_id = msg.get("message_id") or msg.get("id")
      if msg_id:
        message_ids_in_kept.add(msg_id)

  # Look backwards for assistant messages with the same message_id
  for i in range(adjusted - 1, -1, -1):
    msg = messages[i]
    if msg.get("role") == "assistant":
      msg_id = msg.get("message_id") or msg.get("id")
      if msg_id and msg_id in message_ids_in_kept:
        adjusted = i

  return adjusted


def calculate_messages_to_keep_index(
  messages: list[dict[str, Any]],
  last_summarized_index: int,
) -> int:
  """Calculate the starting index for messages to keep after compaction.

  Ported from `calculateMessagesToKeepIndex` in sessionMemoryCompact.ts.

  Algorithm:
    1. Start from last_summarized_index + 1
    2. Count tokens and text-block messages from there to end
    3. If already at max_tokens cap → adjust and return
    4. If both minimums met → adjust and return
    5. Otherwise expand backwards until minimums met or max reached
    6. Always adjust final index to preserve API invariants

  Args:
      messages: Full message list.
      last_summarized_index: Index of the last message already captured
          in the session memory summary. -1 if not found.

  Returns:
      Starting index for messages to keep.
  """
  if not messages:
    return 0

  config = get_session_memory_compact_config()

  # Start from the message after last_summarized_index
  start_index = (
    last_summarized_index + 1 if last_summarized_index >= 0 else len(messages)
  )

  # Calculate current tokens and text-block count from start_index to end
  total_tokens = 0
  text_block_count = 0
  for i in range(start_index, len(messages)):
    total_tokens += _estimate_single_message_tokens(messages[i])
    if has_text_blocks(messages[i]):
      text_block_count += 1

  # Already at max cap
  if total_tokens >= config.max_tokens:
    return adjust_index_to_preserve_api_invariants(messages, start_index)

  # Already meet both minimums
  if (
    total_tokens >= config.min_tokens
    and text_block_count >= config.min_text_block_messages
  ):
    return adjust_index_to_preserve_api_invariants(messages, start_index)

  # Find the compact boundary floor (don't expand past the last boundary)
  floor = 0
  for i in range(len(messages) - 1, -1, -1):
    if _is_compact_boundary(messages[i]):
      floor = i + 1
      break

  # Expand backwards until we meet both minimums or hit max cap
  for i in range(start_index - 1, floor - 1, -1):
    msg_tokens = _estimate_single_message_tokens(messages[i])
    total_tokens += msg_tokens
    if has_text_blocks(messages[i]):
      text_block_count += 1
    start_index = i

    # Stop if max cap reached
    if total_tokens >= config.max_tokens:
      break

    # Stop if both minimums met
    if (
      total_tokens >= config.min_tokens
      and text_block_count >= config.min_text_block_messages
    ):
      break

  # Final adjustment to preserve tool pairs
  return adjust_index_to_preserve_api_invariants(messages, start_index)


# ── Orchestrator ───────────────────────────────────────────────────────────────


@dataclass
class SessionMemoryCompactResult:
  """Result from session memory compaction attempt."""

  success: bool = False
  messages_kept: list[dict[str, Any]] | None = None
  messages_dropped: int = 0
  start_index: int = 0
  tokens_before: int = 0
  tokens_after: int = 0
  method: str = "session_memory"


def try_session_memory_compact(
  messages: list[dict[str, Any]],
  *,
  session_memory_content: str | None = None,
  last_summarized_message_id: str | None = None,
  auto_compact_threshold: int | None = None,
) -> SessionMemoryCompactResult | None:
  """Try to compact using session memory instead of full L1-L4 pipeline.

  This is a lightweight compaction path that uses pre-extracted session
  memory as the summary, keeping only recent messages after the summary
  boundary. Falls back to None if SM compact can't be used.

  Handles two scenarios:
    1. Normal: last_summarized_message_id is set → keep only after that ID
    2. Resumed: No ID but SM content exists → keep all, use SM as summary

  Args:
      messages: Full message list.
      session_memory_content: Pre-extracted session memory text.
      last_summarized_message_id: UUID of last summarized message.
      auto_compact_threshold: Token threshold for auto-compact guard.

  Returns:
      SessionMemoryCompactResult or None if SM compact can't be used.
  """
  if not session_memory_content:
    logger.debug("No session memory content — skipping SM compact")
    return None

  if not session_memory_content.strip():
    logger.debug("Empty session memory template — skipping SM compact")
    return None

  # Find the last summarized index
  if last_summarized_message_id:
    last_summarized_index = -1
    for i, msg in enumerate(messages):
      msg_uuid = msg.get("uuid") or msg.get("id")
      if msg_uuid == last_summarized_message_id:
        last_summarized_index = i
        break

    if last_summarized_index == -1:
      logger.warning(
        "Summarized message ID %s not found — falling back",
        last_summarized_message_id,
      )
      return None
  else:
    # Resumed session: no boundary known
    last_summarized_index = len(messages) - 1
    logger.info("Resumed session — SM compact with no boundary")

  # Calculate which messages to keep
  start_index = calculate_messages_to_keep_index(
    messages,
    last_summarized_index,
  )

  # Filter out old compact boundaries from kept range
  messages_to_keep = [
    msg for msg in messages[start_index:] if not _is_compact_boundary(msg)
  ]

  # Estimate post-compact tokens
  post_tokens = sum(_estimate_single_message_tokens(msg) for msg in messages_to_keep)
  # Add session memory summary tokens
  post_tokens += rough_token_estimate(session_memory_content)

  # Threshold guard: if post-compact is still too large, bail
  if auto_compact_threshold is not None and post_tokens >= auto_compact_threshold:
    logger.info(
      "SM compact would exceed threshold: %d >= %d — falling back",
      post_tokens,
      auto_compact_threshold,
    )
    return None

  pre_tokens = sum(_estimate_single_message_tokens(msg) for msg in messages)

  return SessionMemoryCompactResult(
    success=True,
    messages_kept=messages_to_keep,
    messages_dropped=len(messages) - len(messages_to_keep),
    start_index=start_index,
    tokens_before=pre_tokens,
    tokens_after=post_tokens,
    method="session_memory",
  )
