# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Compact orchestrator — ported from compact.ts (lines 122–1706).

This module contains the core compaction orchestrators and supporting
helpers that were previously missing from the Python port:

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

Upstream source: Claude Code v2.1.91 services/compact/compact.ts
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from packages.agnt_utils.compact.grouping import group_messages_by_api_round
from packages.agnt_utils.compact.prompt import (
    get_compact_prompt,
    get_compact_user_summary_message,
    get_partial_compact_prompt,
)
from packages.agnt_utils.compact.types import (
    CompactionResult,
    CompactDirection,
    Message,
    RecompactionInfo,
)
from packages.agnt_utils.token_estimate import (
    rough_token_estimate,
    rough_token_estimate_for_messages,
    token_count_with_estimation,
)

logger = logging.getLogger(__name__)

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
ERROR_MESSAGE_PROMPT_TOO_LONG = "Conversation too long. Press esc twice to go up a few messages and try again."
ERROR_MESSAGE_USER_ABORT = "API Error: Request was aborted."
ERROR_MESSAGE_INCOMPLETE_RESPONSE = "Compaction interrupted · This may be due to network issues — please try again."


# ── Message utilities ─────────────────────────────────────────────────────────


def _create_user_message(
    content: str,
    *,
    is_meta: bool = False,
    is_compact_summary: bool = False,
    is_visible_in_transcript_only: bool = False,
    summarize_metadata: dict[str, Any] | None = None,
) -> Message:
    """Create a minimal user message dict.

    Mirrors the upstream ``createUserMessage`` factory, using a UUID
    for identity and the type-discriminated dict contract from types.py.
    """
    msg: Message = {
        "type": "user",
        "uuid": str(uuid.uuid4()),
        "message": {"role": "user", "content": content},
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
    """Create a compact boundary marker message.

    This is the sentinel that separates pre-compact from post-compact
    context.  Downstream code uses ``is_compact_boundary_message`` to
    find it and ``get_messages_after_compact_boundary`` to slice.
    """
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
        "type": "system",
        "uuid": str(uuid.uuid4()),
        "message": {"role": "system", "content": ""},
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
    if msg.get("type") != "assistant":
        return None
    content = msg.get("message", {}).get("content", [])
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = [b.get("text", "") for b in content if b.get("type") == "text"]
        return "".join(texts) or None
    return None


# ── Strip helpers ─────────────────────────────────────────────────────────────


def strip_images_from_messages(messages: list[Message]) -> list[Message]:
    """Strip image/document blocks from user messages before summarization.

    Images are not needed for generating a conversation summary and can
    cause the compaction API call itself to hit the prompt-too-long limit,
    especially in sessions where users frequently attach images.

    Replaces image blocks with a text marker so the summary still notes
    that an image was shared.

    Ported from compact.ts:stripImagesFromMessages (L145-L200).
    """
    out: list[Message] = []
    for message in messages:
        if message.get("type") != "user":
            out.append(message)
            continue

        content = message.get("message", {}).get("content")
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
                # Strip images/documents nested inside tool_result content
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
                "message": {
                    **message["message"],
                    "content": new_content,
                },
            }
            out.append(new_msg)

    return out


def strip_reinjected_attachments(messages: list[Message]) -> list[Message]:
    """Strip attachment types that are re-injected post-compaction anyway.

    skill_discovery/skill_listing are re-surfaced by resetSentSkillNames()
    and the next turn's discovery signal, so feeding them to the summarizer
    wastes tokens and pollutes the summary with stale skill suggestions.

    Ported from compact.ts:stripReinjectedAttachments (L211-L223).
    """
    return [
        m for m in messages if not (m.get("type") == "attachment" and m.get("attachment", {}).get("type") in ("skill_discovery", "skill_listing"))
    ]


# ── PTL retry ─────────────────────────────────────────────────────────────────


def _get_prompt_too_long_token_gap(response: Message) -> int | None:
    """Extract token gap from a prompt-too-long error response.

    Returns None when the gap cannot be parsed (some Vertex/Bedrock
    error formats don't include it).
    """
    text = get_assistant_message_text(response) or ""
    # Try to extract a number after "exceeds" or similar patterns.
    # The upstream parses this from the API error message structure;
    # here we do a best-effort extraction.
    import re

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

    Falls back to dropping 20% of groups when the gap is unparseable
    (some Vertex/Bedrock error formats).  Returns None when nothing can
    be dropped without leaving an empty summarize set.

    This is the last-resort escape hatch for CC-1180 — when the compact
    request itself hits prompt-too-long, the user is otherwise stuck.

    Ported from compact.ts:truncateHeadForPTLRetry (L243-L291).
    """
    # Strip our own synthetic marker from a previous retry before grouping.
    inp = messages
    if inp and inp[0].get("type") == "user" and inp[0].get("isMeta") and inp[0].get("message", {}).get("content") == PTL_RETRY_MARKER:
        inp = inp[1:]

    groups = group_messages_by_api_round(inp)
    if len(groups) < 2:
        return None

    token_gap = _get_prompt_too_long_token_gap(ptl_response)
    if token_gap is not None:
        acc = 0
        drop_count = 0
        for g in groups:
            acc += rough_token_estimate_for_messages(g)
            drop_count += 1
            if acc >= token_gap:
                break
    else:
        drop_count = max(1, len(groups) // 5)

    # Keep at least one group so there's something to summarize
    drop_count = min(drop_count, len(groups) - 1)
    if drop_count < 1:
        return None

    sliced: list[Message] = []
    for g in groups[drop_count:]:
        sliced.extend(g)

    # If first message is assistant, prepend synthetic user marker
    # (API requires first message to be role=user)
    if sliced and sliced[0].get("type") == "assistant":
        return [
            _create_user_message(PTL_RETRY_MARKER, is_meta=True),
            *sliced,
        ]
    return sliced


# ── Post-compact message assembly ─────────────────────────────────────────────


def build_post_compact_messages(result: CompactionResult) -> list[Message]:
    """Build the post-compact message array from a CompactionResult.

    Ensures consistent ordering: boundary marker → summary messages →
    messages-to-keep → attachments → hook results.

    Ported from compact.ts:buildPostCompactMessages (L330-L338).
    """
    out: list[Message] = list(result.messages)
    return out


def merge_hook_instructions(
    user_instructions: str | None,
    hook_instructions: str | None,
) -> str | None:
    """Merge user-supplied custom instructions with hook-provided ones.

    User instructions come first; hook instructions are appended.
    Empty strings normalize to None.

    Ported from compact.ts:mergeHookInstructions (L374-L381).
    """
    if not hook_instructions:
        return user_instructions or None
    if not user_instructions:
        return hook_instructions
    return f"{user_instructions}\n\n{hook_instructions}"


# ── Token truncation ──────────────────────────────────────────────────────────


def truncate_to_tokens(content: str, max_tokens: int) -> str:
    """Truncate *content* to roughly *max_tokens*, keeping the head.

    Uses ~4 chars/token estimation.  Appends a truncation marker so the
    model knows it can Read the full file if needed.

    Ported from compact.ts:truncateToTokens (L1666-L1672).
    """
    if rough_token_estimate(content) <= max_tokens:
        return content
    char_budget = max_tokens * 4 - len(SKILL_TRUNCATION_MARKER)
    return content[:char_budget] + SKILL_TRUNCATION_MARKER


# ── File path collection ──────────────────────────────────────────────────────


FILE_READ_TOOL_NAME = "Read"
FILE_UNCHANGED_STUB = "[File content unchanged"


def collect_read_tool_file_paths(messages: list[Message]) -> set[str]:
    """Scan messages for Read tool_use blocks and collect their file paths.

    Skips Reads whose tool_result is a dedup stub — the stub points at an
    earlier full Read that may have been compacted away, so we want to
    re-inject the real content.

    Ported from compact.ts:collectReadToolFilePaths (L1610-L1655).
    """
    stub_ids: set[str] = set()
    for message in messages:
        if message.get("type") != "user":
            continue
        content = message.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "tool_result" and isinstance(block.get("content"), str) and block["content"].startswith(FILE_UNCHANGED_STUB):
                stub_ids.add(block.get("tool_use_id", ""))

    paths: set[str] = set()
    for message in messages:
        if message.get("type") != "assistant":
            continue
        content = message.get("message", {}).get("content")
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
            if isinstance(inp, dict) and "file_path" in inp and isinstance(inp["file_path"], str):
                paths.add(inp["file_path"])
    return paths


def should_exclude_from_restore(
    filename: str,
    *,
    plan_file_path: str | None = None,
    memory_paths: set[str] | None = None,
) -> bool:
    """Return True if *filename* should not be restored post-compact.

    Excludes plan files and memory files (CLAUDE.md variants) since
    they are re-injected through dedicated paths.

    Ported from compact.ts:shouldExcludeFromPostCompactRestore (L1674-L1705).
    """
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
    recompaction_info: RecompactionInfo | None = None,
    summarize_fn: Any | None = None,
) -> CompactionResult:
    """Create a compact version of a conversation by summarizing messages.

    This is the Layer 2 orchestrator — it coordinates:
      1. Pre-compact hook execution
      2. Image/attachment stripping
      3. PTL retry loop (truncating oldest groups on prompt-too-long)
      4. Summary generation via ``summarize_fn``
      5. Post-compact cleanup (cache clearing, file restoration)
      6. Boundary marker + summary message construction

    The ``summarize_fn`` parameter accepts a callable with signature::

        summarize_fn(messages: list[Message], prompt: str) -> str

    When ``summarize_fn`` is None, raises NotImplementedError (the full
    LLM streaming path requires an API integration that lives outside
    the utility library).

    Ported from compact.ts:compactConversation (L387-L763).

    Args:
        messages: The full conversation to compact.
        suppress_follow_up_questions: Omit follow-up question suggestions.
        custom_instructions: User-supplied compaction instructions.
        is_auto_compact: Whether this was triggered automatically.
        recompaction_info: Diagnosis context for telemetry.
        summarize_fn: Callable that generates the summary text.

    Returns:
        CompactionResult with the summarized messages and token counts.
    """
    if not messages:
        raise ValueError(ERROR_MESSAGE_NOT_ENOUGH_MESSAGES)

    pre_compact_token_count = token_count_with_estimation(messages)

    # ── Build prompt ──────────────────────────────────────────────────
    compact_prompt = get_compact_prompt(custom_instructions)

    # ── Strip media for summarization ─────────────────────────────────
    cleaned = strip_reinjected_attachments(
        strip_images_from_messages(
            get_messages_after_compact_boundary(messages),
        )
    )

    # ── PTL retry loop ────────────────────────────────────────────────
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
        except _PromptTooLongError as e:
            ptl_attempts += 1
            if ptl_attempts > MAX_PTL_RETRIES:
                logger.error(
                    "compact: PTL retry exhausted after %d attempts",
                    ptl_attempts,
                )
                raise ValueError(ERROR_MESSAGE_PROMPT_TOO_LONG) from e
            truncated = truncate_head_for_ptl_retry(
                messages_to_summarize,
                e.response if hasattr(e, "response") else {},
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
        break

    if not summary:
        raise ValueError("Failed to generate conversation summary — response did not contain valid text content")

    # ── Build result ──────────────────────────────────────────────────
    trigger = "auto" if is_auto_compact else "manual"
    last_uuid = messages[-1].get("uuid") if messages else None
    boundary = _create_compact_boundary_message(trigger, pre_compact_token_count, last_uuid)
    summary_msg = _create_user_message(
        get_compact_user_summary_message(
            summary,
            suppress_follow_up_questions,
            transcript_path=None,
        ),
        is_compact_summary=True,
        is_visible_in_transcript_only=True,
    )

    result_messages = [boundary, summary_msg]
    post_compact_token_count = rough_token_estimate_for_messages(result_messages)

    logger.info(
        "compact: %d → %d tokens (trigger=%s, ptl_attempts=%d)",
        pre_compact_token_count,
        post_compact_token_count,
        trigger,
        ptl_attempts,
    )

    return CompactionResult(
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
) -> CompactionResult:
    """Perform a partial compaction around the selected message index.

    Direction ``FROM``:   summarize messages after the index, keep earlier.
                          Prompt cache for kept (earlier) messages is preserved.
    Direction ``UP_TO``:  summarize messages before the index, keep later.
                          Prompt cache is invalidated since summary precedes kept.

    Ported from compact.ts:partialCompactConversation (L772-L1106).

    Args:
        all_messages: The full conversation.
        pivot_index: The message index to pivot around.
        user_feedback: Optional context from the user about the compaction.
        direction: Which segment to summarize.
        summarize_fn: Callable ``(messages, prompt) -> str``.

    Returns:
        CompactionResult with both summarized and preserved messages.
    """
    if direction == CompactDirection.UP_TO:
        messages_to_summarize = all_messages[:pivot_index]
        messages_to_keep = [
            m
            for m in all_messages[pivot_index:]
            if m.get("type") != "progress" and not is_compact_boundary_message(m) and not (m.get("type") == "user" and m.get("isCompactSummary"))
        ]
    else:
        messages_to_summarize = all_messages[pivot_index:]
        messages_to_keep = [m for m in all_messages[:pivot_index] if m.get("type") != "progress"]

    if not messages_to_summarize:
        if direction == CompactDirection.UP_TO:
            raise ValueError("Nothing to summarize before the selected message.")
        raise ValueError("Nothing to summarize after the selected message.")

    pre_compact_token_count = token_count_with_estimation(all_messages)

    # ── Build instructions ────────────────────────────────────────────
    ci = user_feedback
    partial_prompt = get_partial_compact_prompt(ci, direction.value)

    # ── Strip media ───────────────────────────────────────────────────
    cleaned_to_summarize = strip_reinjected_attachments(strip_images_from_messages(messages_to_summarize))

    # ── Summarize ─────────────────────────────────────────────────────
    if summarize_fn is None:
        raise NotImplementedError("partial_compact_conversation requires a summarize_fn callable.")

    api_messages = (
        cleaned_to_summarize if direction == CompactDirection.UP_TO else strip_reinjected_attachments(strip_images_from_messages(all_messages))
    )

    summary: str | None = None
    ptl_attempts = 0
    for _ in range(MAX_PTL_RETRIES + 1):
        try:
            summary = summarize_fn(api_messages, partial_prompt)
        except _PromptTooLongError as e:
            ptl_attempts += 1
            if ptl_attempts > MAX_PTL_RETRIES:
                raise ValueError(ERROR_MESSAGE_PROMPT_TOO_LONG) from e
            truncated = truncate_head_for_ptl_retry(
                api_messages,
                e.response if hasattr(e, "response") else {},
            )
            if truncated is None:
                raise ValueError(ERROR_MESSAGE_PROMPT_TOO_LONG) from e
            api_messages = truncated
            continue
        break

    if not summary:
        raise ValueError("Failed to generate conversation summary — response did not contain valid text content")

    # ── Build result ──────────────────────────────────────────────────
    # Find last non-progress UUID for the boundary marker
    if direction == CompactDirection.UP_TO:
        pre_segment = all_messages[:pivot_index]
        last_pre_uuid = None
        for m in reversed(pre_segment):
            if m.get("type") != "progress":
                last_pre_uuid = m.get("uuid")
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
        get_compact_user_summary_message(summary, False, transcript_path=None),
        is_compact_summary=True,
        **{
            "is_visible_in_transcript_only": len(messages_to_keep) == 0,
            **(
                {
                    "summarize_metadata": {
                        "messagesSummarized": len(messages_to_summarize),
                        "userContext": user_feedback,
                        "direction": direction.value,
                    },
                }
                if messages_to_keep
                else {}
            ),
        },
    )

    result_messages = [boundary, summary_msg, *messages_to_keep]
    post_compact_token_count = rough_token_estimate_for_messages(result_messages)

    logger.info(
        "partial_compact: %d → %d tokens (direction=%s, kept=%d, summarized=%d)",
        pre_compact_token_count,
        post_compact_token_count,
        direction.value,
        len(messages_to_keep),
        len(messages_to_summarize),
    )

    return CompactionResult(
        messages=result_messages,
        summary=summary,
        tokens_before=pre_compact_token_count,
        tokens_after=post_compact_token_count,
        is_partial=True,
        rounds_preserved=len(messages_to_keep),
    )


# ── Internal exception ────────────────────────────────────────────────────────


class _PromptTooLongError(Exception):
    """Raised when the API returns a prompt-too-long error.

    Callers of ``summarize_fn`` should raise this when they detect a
    PTL response so the retry loop can truncate and retry.
    """

    def __init__(self, message: str = "", response: Message | None = None) -> None:
        super().__init__(message)
        self.response: Message = response or {}


# Public alias for consumers to raise from their summarize_fn
PromptTooLongError = _PromptTooLongError
