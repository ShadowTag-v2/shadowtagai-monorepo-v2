# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Conversation-level compaction orchestrators.

Ported from Claude Code v2.1.91 services/compact/compact.ts (L122-L1706).

This module contains the Layer 2 full-conversation compaction logic:

  - strip_images_from_messages   — remove images before summarization
  - strip_reinjected_attachments — remove skill attachments that get re-injected
  - truncate_head_for_ptl_retry  — drop oldest API-round groups for PTL retry
  - build_post_compact_messages  — consistent message ordering after compaction
  - merge_hook_instructions      — combine user + hook instructions
  - compact_conversation         — full conversation summarization orchestrator
  - partial_compact_conversation — directional partial compaction orchestrator

Internal helpers:
  - truncate_to_tokens           — token-budget-aware content truncation
  - collect_read_tool_file_paths — dedup file restoration against preserved tail
  - should_exclude_from_restore  — plan/memory file exclusion filter

These orchestrators sit ABOVE the 4-layer reactive pipeline (ContextCompactor)
and handle the LLM-based summarization path with PTL retry logic.
"""

from __future__ import annotations

import logging
import re
import uuid
from enum import StrEnum
from typing import Any

from context_compactor.compact_prompts import (
  get_compact_prompt,
  get_compact_user_summary_message,
  get_partial_compact_prompt,
)
from context_compactor.grouping import group_messages_by_api_round
from context_compactor.token_estimator import rough_token_estimate

logger = logging.getLogger(__name__)

# ── Type alias ────────────────────────────────────────────────────────────────
# Messages use flat dict format matching the canonical context_compactor contract.
Message = dict[str, Any]

# ── Constants ─────────────────────────────────────────────────────────────────

POST_COMPACT_MAX_FILES_TO_RESTORE = 5
POST_COMPACT_TOKEN_BUDGET = 50_000
POST_COMPACT_MAX_TOKENS_PER_FILE = 5_000
POST_COMPACT_MAX_TOKENS_PER_SKILL = 5_000
POST_COMPACT_SKILLS_TOKEN_BUDGET = 25_000
MAX_COMPACT_STREAMING_RETRIES = 2
MAX_PTL_RETRIES = 3
PTL_RETRY_MARKER = "[earlier conversation truncated for compaction retry]"

SKILL_TRUNCATION_MARKER = "\n\n[... skill content truncated for compaction; use Read on the skill path if you need the full text]"

# ── Error messages ────────────────────────────────────────────────────────────

ERROR_MESSAGE_NOT_ENOUGH_MESSAGES = "Not enough messages to compact."
ERROR_MESSAGE_PROMPT_TOO_LONG = (
  "Conversation too long. Press esc twice to go up a few messages and try again."
)
ERROR_MESSAGE_USER_ABORT = "API Error: Request was aborted."
ERROR_MESSAGE_INCOMPLETE_RESPONSE = (
  "Compaction interrupted · This may be due to network issues — please try again."
)


# ── CompactDirection enum ─────────────────────────────────────────────────────


class CompactDirection(StrEnum):
  """Direction for partial compaction."""

  FROM = "from"
  UP_TO = "up_to"


# ── CompactionResult dataclass ────────────────────────────────────────────────


class ConversationCompactionResult:
  """Result of a conversation-level compaction operation.

  Attributes:
      messages: Post-compact message list.
      summary: Generated summary text.
      tokens_before: Token count before compaction.
      tokens_after: Token count after compaction.
      is_partial: Whether this was a partial compaction.
      rounds_preserved: Number of API rounds preserved (partial only).
  """

  __slots__ = (
    "messages",
    "summary",
    "tokens_before",
    "tokens_after",
    "is_partial",
    "rounds_preserved",
  )

  def __init__(
    self,
    messages: list[Message] | None = None,
    summary: str = "",
    tokens_before: int = 0,
    tokens_after: int = 0,
    is_partial: bool = False,
    rounds_preserved: int = 0,
  ) -> None:
    self.messages = messages or []
    self.summary = summary
    self.tokens_before = tokens_before
    self.tokens_after = tokens_after
    self.is_partial = is_partial
    self.rounds_preserved = rounds_preserved

  @property
  def savings_pct(self) -> float:
    """Percentage of tokens saved."""
    if self.tokens_before == 0:
      return 0.0
    return ((self.tokens_before - self.tokens_after) / self.tokens_before) * 100


# ── PromptTooLongError ────────────────────────────────────────────────────────


class PromptTooLongError(Exception):
  """Raised when the API returns a prompt-too-long error.

  Callers of ``summarize_fn`` should raise this when they detect a
  PTL response so the retry loop can truncate and retry.
  """

  def __init__(self, message: str = "", response: Message | None = None) -> None:
    super().__init__(message)
    self.response: Message = response or {}


# ── Message utilities ─────────────────────────────────────────────────────────


def _create_user_message(
  content: str,
  *,
  is_meta: bool = False,
  is_compact_summary: bool = False,
  is_visible_in_transcript_only: bool = False,
  summarize_metadata: dict[str, Any] | None = None,
) -> Message:
  """Create a minimal user message dict."""
  msg: Message = {
    "role": "user",
    "content": content,
    "uuid": str(uuid.uuid4()),
  }
  if is_meta:
    msg["isMeta"] = True
  if is_compact_summary:
    msg["isCompactSummary"] = True
  if is_visible_in_transcript_only:
    msg["isVisibleInTranscriptOnly"] = True
  if summarize_metadata is not None:
    msg["summarizeMetadata"] = summarize_metadata
  return msg


def _create_compact_boundary_message(
  trigger: str,
  pre_compact_token_count: int,
  last_pre_compact_uuid: str | None = None,
  user_feedback: str | None = None,
  messages_summarized: int | None = None,
) -> Message:
  """Create a compact boundary marker message."""
  metadata: dict[str, Any] = {
    "trigger": trigger,
    "preCompactTokenCount": pre_compact_token_count,
  }
  if last_pre_compact_uuid:
    metadata["lastPreCompactUuid"] = last_pre_compact_uuid
  if user_feedback:
    metadata["userFeedback"] = user_feedback
  if messages_summarized is not None:
    metadata["messagesSummarized"] = messages_summarized

  return {
    "role": "system",
    "content": "",
    "uuid": str(uuid.uuid4()),
    "compactBoundary": True,
    "compactMetadata": metadata,
  }


def is_compact_boundary_message(msg: Message) -> bool:
  """Return True if *msg* is a compact boundary marker."""
  return msg.get("compactBoundary", False) is True


def get_messages_after_compact_boundary(messages: list[Message]) -> list[Message]:
  """Return messages after the last compact boundary, or all if none found."""
  for i in range(len(messages) - 1, -1, -1):
    if is_compact_boundary_message(messages[i]):
      return messages[i + 1 :]
  return messages


def get_assistant_message_text(msg: Message) -> str | None:
  """Extract text content from an assistant message."""
  if msg.get("role") != "assistant":
    return None
  content = msg.get("content", [])
  if isinstance(content, str):
    return content
  if isinstance(content, list):
    texts = [b.get("text", "") for b in content if b.get("type") == "text"]
    return "".join(texts) or None
  return None


# ── Token helpers ─────────────────────────────────────────────────────────────


def _rough_token_estimate_for_messages(messages: list[Message]) -> int:
  """Estimate total tokens for a list of flat message dicts."""
  total = 0
  for msg in messages:
    content = msg.get("content", "")
    if isinstance(content, str):
      total += rough_token_estimate(content) + 4  # +4 for role framing
    elif isinstance(content, list):
      for block in content:
        text = block.get("text", "") or block.get("content", "")
        if isinstance(text, str):
          total += rough_token_estimate(text)
      total += 4
    else:
      total += 4
  return total


def _token_count_with_estimation(messages: list[Message]) -> int:
  """Token count using rough estimation for flat message dicts."""
  return _rough_token_estimate_for_messages(messages)


# ── Strip helpers ─────────────────────────────────────────────────────────────


def strip_images_from_messages(messages: list[Message]) -> list[Message]:
  """Strip image/document blocks from user messages before summarization.

  Images are not needed for generating a conversation summary and can
  cause the compaction API call itself to hit the prompt-too-long limit.
  Replaces image blocks with a text marker so the summary still notes
  that an image was shared.

  Ported from compact.ts:stripImagesFromMessages (L145-L200).
  """
  out: list[Message] = []
  for message in messages:
    if message.get("role") != "user":
      out.append(message)
      continue

    content = message.get("content")
    if not isinstance(content, list):
      out.append(message)
      continue

    has_media_block = False
    new_content: list[dict[str, Any]] = []

    for block in content:
      block_type = block.get("type", "")

      if block_type == "image":
        has_media_block = True
        new_content.append({"type": "text", "text": "[image]"})
      elif block_type == "document":
        has_media_block = True
        new_content.append({"type": "text", "text": "[document]"})
      elif block_type == "tool_result" and isinstance(block.get("content"), list):
        tool_has_media = False
        new_tool_content = []
        for item in block["content"]:
          item_type = item.get("type", "")
          if item_type == "image":
            tool_has_media = True
            new_tool_content.append({"type": "text", "text": "[image]"})
          elif item_type == "document":
            tool_has_media = True
            new_tool_content.append({"type": "text", "text": "[document]"})
          else:
            new_tool_content.append(item)
        if tool_has_media:
          has_media_block = True
          new_content.append({**block, "content": new_tool_content})
        else:
          new_content.append(block)
      else:
        new_content.append(block)

    if not has_media_block:
      out.append(message)
    else:
      new_msg: Message = {
        **message,
        "content": new_content,
      }
      out.append(new_msg)

  return out


def strip_reinjected_attachments(messages: list[Message]) -> list[Message]:
  """Strip attachment types that are re-injected post-compaction anyway.

  Ported from compact.ts:stripReinjectedAttachments (L211-L223).
  """
  return [
    m
    for m in messages
    if not (
      m.get("role") == "attachment"
      and m.get("attachment", {}).get("type") in ("skill_discovery", "skill_listing")
    )
  ]


# ── PTL retry ─────────────────────────────────────────────────────────────────


def _get_prompt_too_long_token_gap(response: Message) -> int | None:
  """Extract token gap from a prompt-too-long error response."""
  text = get_assistant_message_text(response) or ""
  match = re.search(r"by\s+(\d[\d,]*)\s+tokens?", text)
  if match:
    try:
      return int(match.group(1).replace(",", ""))
    except ValueError:
      pass
  return None


def truncate_head_for_ptl_retry(
  messages: list[Message],
  ptl_response: Message,
) -> list[Message] | None:
  """Drop the oldest API-round groups until the token gap is covered.

  Falls back to dropping 20% of groups when the gap is unparseable.
  Returns None when nothing can be dropped.

  Ported from compact.ts:truncateHeadForPTLRetry (L243-L291).
  """
  inp = messages
  if (
    inp
    and inp[0].get("role") == "user"
    and inp[0].get("isMeta")
    and inp[0].get("content") == PTL_RETRY_MARKER
  ):
    inp = inp[1:]

  groups = group_messages_by_api_round(inp)
  if len(groups) < 2:
    return None

  token_gap = _get_prompt_too_long_token_gap(ptl_response)
  if token_gap is not None:
    acc = 0
    drop_count = 0
    for g in groups:
      acc += _rough_token_estimate_for_messages(g)
      drop_count += 1
      if acc >= token_gap:
        break
  else:
    drop_count = max(1, len(groups) // 5)

  drop_count = min(drop_count, len(groups) - 1)
  if drop_count < 1:
    return None

  sliced: list[Message] = []
  for g in groups[drop_count:]:
    sliced.extend(g)

  if sliced and sliced[0].get("role") == "assistant":
    return [
      _create_user_message(PTL_RETRY_MARKER, is_meta=True),
      *sliced,
    ]
  return sliced


# ── Post-compact message assembly ─────────────────────────────────────────────


def build_post_compact_messages(result: ConversationCompactionResult) -> list[Message]:
  """Build the post-compact message array from a CompactionResult."""
  return list(result.messages)


def merge_hook_instructions(
  user_instructions: str | None,
  hook_instructions: str | None,
) -> str | None:
  """Merge user-supplied custom instructions with hook-provided ones."""
  if not hook_instructions:
    return user_instructions or None
  if not user_instructions:
    return hook_instructions
  return f"{user_instructions}\n\n{hook_instructions}"


# ── Token truncation ──────────────────────────────────────────────────────────


def truncate_to_tokens(content: str, max_tokens: int) -> str:
  """Truncate *content* to roughly *max_tokens*, keeping the head."""
  if rough_token_estimate(content) <= max_tokens:
    return content
  char_budget = max_tokens * 4 - len(SKILL_TRUNCATION_MARKER)
  return content[:char_budget] + SKILL_TRUNCATION_MARKER


# ── File path collection ──────────────────────────────────────────────────────


FILE_READ_TOOL_NAME = "Read"
FILE_UNCHANGED_STUB = "[File content unchanged"


def collect_read_tool_file_paths(messages: list[Message]) -> set[str]:
  """Scan messages for Read tool_use blocks and collect their file paths.

  Ported from compact.ts:collectReadToolFilePaths (L1610-L1655).
  """
  stub_ids: set[str] = set()
  for message in messages:
    if message.get("role") != "user":
      continue
    content = message.get("content")
    if not isinstance(content, list):
      continue
    for block in content:
      if (
        block.get("type") == "tool_result"
        and isinstance(block.get("content"), str)
        and block["content"].startswith(FILE_UNCHANGED_STUB)
      ):
        stub_ids.add(block.get("tool_use_id", ""))

  paths: set[str] = set()
  for message in messages:
    if message.get("role") != "assistant":
      continue
    content = message.get("content")
    if not isinstance(content, list):
      continue
    for block in content:
      if block.get("type") != "tool_use":
        continue
      if block.get("name") != FILE_READ_TOOL_NAME:
        continue
      if block.get("id") in stub_ids:
        continue
      inp = block.get("input")
      if (
        isinstance(inp, dict)
        and "file_path" in inp
        and isinstance(inp["file_path"], str)
      ):
        paths.add(inp["file_path"])
  return paths


def should_exclude_from_restore(
  filename: str,
  *,
  plan_file_path: str | None = None,
  memory_paths: set[str] | None = None,
) -> bool:
  """Return True if *filename* should not be restored post-compact."""
  if plan_file_path and filename == plan_file_path:
    return True
  return bool(memory_paths and filename in memory_paths)


# ── Compact orchestrator ──────────────────────────────────────────────────────


def compact_conversation(
  messages: list[Message],
  *,
  suppress_follow_up_questions: bool = False,
  custom_instructions: str | None = None,
  is_auto_compact: bool = False,
  summarize_fn: Any | None = None,
) -> ConversationCompactionResult:
  """Create a compact version of a conversation by summarizing messages.

  This is the Layer 2 orchestrator — it coordinates:
    1. Image/attachment stripping
    2. PTL retry loop (truncating oldest groups on prompt-too-long)
    3. Summary generation via ``summarize_fn``
    4. Boundary marker + summary message construction

  The ``summarize_fn`` parameter accepts a callable with signature::

      summarize_fn(messages: list[Message], prompt: str) -> str

  When ``summarize_fn`` is None, raises NotImplementedError.

  Args:
      messages: The full conversation to compact.
      suppress_follow_up_questions: Omit follow-up question suggestions.
      custom_instructions: User-supplied compaction instructions.
      is_auto_compact: Whether this was triggered automatically.
      summarize_fn: Callable that generates the summary text.

  Returns:
      ConversationCompactionResult with the summarized messages and token counts.

  Raises:
      ValueError: If messages are empty or summarization fails.
      NotImplementedError: If summarize_fn is None.
      PromptTooLongError: If PTL retries are exhausted (re-raised as ValueError).
  """
  if not messages:
    raise ValueError(ERROR_MESSAGE_NOT_ENOUGH_MESSAGES)

  pre_compact_token_count = _token_count_with_estimation(messages)

  compact_prompt = get_compact_prompt(custom_instructions)

  cleaned = strip_reinjected_attachments(
    strip_images_from_messages(
      get_messages_after_compact_boundary(messages),
    )
  )

  messages_to_summarize = cleaned
  summary: str | None = None
  ptl_attempts = 0

  if summarize_fn is None:
    raise NotImplementedError(
      "compact_conversation requires a summarize_fn callable "
      "for LLM-based summarization. The utility library does not "
      "ship a default — pass your API integration as summarize_fn."
    )

  for _ in range(MAX_PTL_RETRIES + 1):
    try:
      summary = summarize_fn(messages_to_summarize, compact_prompt)
    except PromptTooLongError as e:
      ptl_attempts += 1
      if ptl_attempts > MAX_PTL_RETRIES:
        logger.error(
          "compact: PTL retry exhausted after %d attempts",
          ptl_attempts,
        )
        raise ValueError(ERROR_MESSAGE_PROMPT_TOO_LONG) from e
      truncated = truncate_head_for_ptl_retry(
        messages_to_summarize,
        e.response,
      )
      if truncated is None:
        raise ValueError(ERROR_MESSAGE_PROMPT_TOO_LONG) from e
      logger.info(
        "compact: PTL retry %d — dropped %d messages, %d remaining",
        ptl_attempts,
        len(messages_to_summarize) - len(truncated),
        len(truncated),
      )
      messages_to_summarize = truncated
      continue
    except Exception as e:
      logger.error("compact: summarize_fn raised: %s", e)
      raise ValueError(ERROR_MESSAGE_INCOMPLETE_RESPONSE) from e
    break

  if not summary:
    raise ValueError(
      "Failed to generate conversation summary — response did not contain valid text content"
    )

  trigger = "auto" if is_auto_compact else "manual"
  last_uuid = messages[-1].get("uuid") if messages else None
  boundary = _create_compact_boundary_message(
    trigger, pre_compact_token_count, last_uuid
  )
  summary_msg = _create_user_message(
    get_compact_user_summary_message(
      summary,
      suppress_follow_up=suppress_follow_up_questions,
      transcript_path=None,
    ),
    is_compact_summary=True,
    is_visible_in_transcript_only=True,
  )

  result_messages = [boundary, summary_msg]
  post_compact_token_count = _rough_token_estimate_for_messages(result_messages)

  logger.info(
    "compact: %d → %d tokens (trigger=%s, ptl_attempts=%d)",
    pre_compact_token_count,
    post_compact_token_count,
    trigger,
    ptl_attempts,
  )

  return ConversationCompactionResult(
    messages=result_messages,
    summary=summary,
    tokens_before=pre_compact_token_count,
    tokens_after=post_compact_token_count,
    is_partial=False,
    rounds_preserved=0,
  )


# ── Partial compact orchestrator ──────────────────────────────────────────────


def partial_compact_conversation(
  all_messages: list[Message],
  pivot_index: int,
  *,
  user_feedback: str | None = None,
  direction: CompactDirection = CompactDirection.FROM,
  summarize_fn: Any | None = None,
) -> ConversationCompactionResult:
  """Perform a partial compaction around the selected message index.

  Direction ``FROM``:   summarize messages after the index, keep earlier.
  Direction ``UP_TO``:  summarize messages before the index, keep later.

  Args:
      all_messages: The full conversation.
      pivot_index: The message index to pivot around.
      user_feedback: Optional context from the user about the compaction.
      direction: Which segment to summarize.
      summarize_fn: Callable ``(messages, prompt) -> str``.

  Returns:
      ConversationCompactionResult with both summarized and preserved messages.
  """
  if direction == CompactDirection.UP_TO:
    messages_to_summarize = all_messages[:pivot_index]
    messages_to_keep = [
      m
      for m in all_messages[pivot_index:]
      if not is_compact_boundary_message(m)
      and not (m.get("role") == "user" and m.get("isCompactSummary"))
    ]
  else:
    messages_to_summarize = all_messages[pivot_index:]
    messages_to_keep = list(all_messages[:pivot_index])

  if not messages_to_summarize:
    if direction == CompactDirection.UP_TO:
      raise ValueError("Nothing to summarize before the selected message.")
    raise ValueError("Nothing to summarize after the selected message.")

  pre_compact_token_count = _token_count_with_estimation(all_messages)

  ci = user_feedback
  partial_prompt = get_partial_compact_prompt(ci, direction=direction.value)

  cleaned_to_summarize = strip_reinjected_attachments(
    strip_images_from_messages(messages_to_summarize)
  )

  if summarize_fn is None:
    raise NotImplementedError(
      "partial_compact_conversation requires a summarize_fn callable."
    )

  api_messages = (
    cleaned_to_summarize
    if direction == CompactDirection.UP_TO
    else strip_reinjected_attachments(strip_images_from_messages(all_messages))
  )

  summary: str | None = None
  ptl_attempts = 0
  for _ in range(MAX_PTL_RETRIES + 1):
    try:
      summary = summarize_fn(api_messages, partial_prompt)
    except PromptTooLongError as e:
      ptl_attempts += 1
      if ptl_attempts > MAX_PTL_RETRIES:
        raise ValueError(ERROR_MESSAGE_PROMPT_TOO_LONG) from e
      truncated = truncate_head_for_ptl_retry(
        api_messages,
        e.response,
      )
      if truncated is None:
        raise ValueError(ERROR_MESSAGE_PROMPT_TOO_LONG) from e
      api_messages = truncated
      continue
    except Exception as e:
      logger.error("partial_compact: summarize_fn raised: %s", e)
      raise ValueError(ERROR_MESSAGE_INCOMPLETE_RESPONSE) from e
    break

  if not summary:
    raise ValueError(
      "Failed to generate conversation summary — response did not contain valid text content"
    )

  if direction == CompactDirection.UP_TO:
    pre_segment = all_messages[:pivot_index]
    last_pre_uuid = None
    for m in reversed(pre_segment):
      last_pre_uuid = m.get("uuid")
      if last_pre_uuid:
        break
  else:
    last_pre_uuid = messages_to_keep[-1].get("uuid") if messages_to_keep else None

  boundary = _create_compact_boundary_message(
    "manual",
    pre_compact_token_count,
    last_pre_uuid,
    user_feedback,
    len(messages_to_summarize),
  )

  summary_msg = _create_user_message(
    get_compact_user_summary_message(
      summary, suppress_follow_up=False, transcript_path=None
    ),
    is_compact_summary=True,
    is_visible_in_transcript_only=(len(messages_to_keep) == 0),
    summarize_metadata={
      "messagesSummarized": len(messages_to_summarize),
      "userContext": user_feedback,
      "direction": direction.value,
    }
    if messages_to_keep
    else None,
  )

  result_messages = [boundary, summary_msg, *messages_to_keep]
  post_compact_token_count = _rough_token_estimate_for_messages(result_messages)

  logger.info(
    "partial_compact: %d → %d tokens (direction=%s, kept=%d, summarized=%d)",
    pre_compact_token_count,
    post_compact_token_count,
    direction.value,
    len(messages_to_keep),
    len(messages_to_summarize),
  )

  return ConversationCompactionResult(
    messages=result_messages,
    summary=summary,
    tokens_before=pre_compact_token_count,
    tokens_after=post_compact_token_count,
    is_partial=True,
    rounds_preserved=len(messages_to_keep),
  )
