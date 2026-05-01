# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Session-memory-based compaction — ported from sessionMemoryCompact.ts.

An experimental alternative to LLM-based compaction that prunes messages
directly using the session memory as the retained context.  Faster and
cheaper than the LLM path, but only works when session memory is active
and the token savings are sufficient.

The key insight: if session memory captures the essential context from
older messages, we can simply drop those messages and rely on the
session memory to provide continuity.

Upstream source: Claude Code v2.1.91 services/compact/sessionMemoryCompact.ts

Port fidelity notes:
  - adjustIndexToPreserveAPIInvariants: Full 2-step algorithm ported
    (tool_use/tool_result pairing + thinking-block message.id correlation).
  - calculateMessagesToKeepIndex: Token + text-block dual-minimum expansion
    with maxTokens hard cap and compact-boundary floor.
  - trySessionMemoryCompaction: Handles normal and resumed-session cases,
    builds CompactionResult with boundary markers.
  - Remote config (GrowthBook) replaced with local defaults + env overrides.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from packages.agnt_utils.compact.micro_compact import _rough_token_estimate
from packages.agnt_utils.compact.orchestrator import (
    _create_compact_boundary_message,
    _create_user_message,
    is_compact_boundary_message,
)
from packages.agnt_utils.compact.prompt import get_compact_user_summary_message
from packages.agnt_utils.compact.types import CompactionResult, Message

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────


@dataclass
class SessionMemoryCompactConfig:
    """Configuration for session memory compaction thresholds.

    Mirrors the upstream ``SessionMemoryCompactConfig`` type.
    """

    min_tokens: int = 10_000
    """Minimum tokens to preserve after compaction."""

    min_text_block_messages: int = 5
    """Minimum number of messages with text blocks to keep."""

    max_tokens: int = 40_000
    """Maximum tokens to preserve after compaction (hard cap)."""


DEFAULT_SM_COMPACT_CONFIG = SessionMemoryCompactConfig()

# Module-level mutable config — starts with defaults.
_sm_compact_config = SessionMemoryCompactConfig()
_config_initialized = False


def set_session_memory_compact_config(
    *,
    min_tokens: int | None = None,
    min_text_block_messages: int | None = None,
    max_tokens: int | None = None,
) -> None:
    """Merge partial overrides into the current config."""
    global _sm_compact_config
    if min_tokens is not None and min_tokens > 0:
        _sm_compact_config.min_tokens = min_tokens
    if min_text_block_messages is not None and min_text_block_messages > 0:
        _sm_compact_config.min_text_block_messages = min_text_block_messages
    if max_tokens is not None and max_tokens > 0:
        _sm_compact_config.max_tokens = max_tokens


def get_session_memory_compact_config() -> SessionMemoryCompactConfig:
    """Return a copy of the current config."""
    return SessionMemoryCompactConfig(
        min_tokens=_sm_compact_config.min_tokens,
        min_text_block_messages=_sm_compact_config.min_text_block_messages,
        max_tokens=_sm_compact_config.max_tokens,
    )


def reset_session_memory_compact_config() -> None:
    """Reset to defaults (useful for testing)."""
    global _sm_compact_config, _config_initialized
    _sm_compact_config = SessionMemoryCompactConfig()
    _config_initialized = False


def _init_session_memory_compact_config() -> None:
    """Initialize config from environment overrides (once per session).

    The upstream fetches from GrowthBook; we use env vars as the
    local equivalent.
    """
    global _config_initialized
    if _config_initialized:
        return
    _config_initialized = True

    env_min_tokens = os.environ.get("SM_COMPACT_MIN_TOKENS")
    env_min_text = os.environ.get("SM_COMPACT_MIN_TEXT_BLOCK_MESSAGES")
    env_max_tokens = os.environ.get("SM_COMPACT_MAX_TOKENS")

    set_session_memory_compact_config(
        min_tokens=int(env_min_tokens) if env_min_tokens else None,
        min_text_block_messages=int(env_min_text) if env_min_text else None,
        max_tokens=int(env_max_tokens) if env_max_tokens else None,
    )


# ── Message inspection helpers ────────────────────────────────────────────────


def has_text_blocks(message: Message) -> bool:
    """Check if a message contains text blocks (user/assistant text content).

    Ported from sessionMemoryCompact.ts:hasTextBlocks (L135-L150).
    """
    msg_type = message.get("type", "")
    inner = message.get("message", {})
    if not isinstance(inner, dict):
        return False
    content = inner.get("content")

    if msg_type == "assistant":
        if isinstance(content, list):
            return any(isinstance(block, dict) and block.get("type") == "text" for block in content)
        return False

    if msg_type == "user":
        if isinstance(content, str):
            return len(content) > 0
        if isinstance(content, list):
            return any(isinstance(block, dict) and block.get("type") == "text" for block in content)
    return False


def _get_tool_result_ids(message: Message) -> list[str]:
    """Extract tool_use_ids from tool_result blocks in a user message.

    Ported from sessionMemoryCompact.ts:getToolResultIds (L155-L170).
    """
    if message.get("type") != "user":
        return []
    inner = message.get("message", {})
    if not isinstance(inner, dict):
        return []
    content = inner.get("content")
    if not isinstance(content, list):
        return []

    ids: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_result":
            tool_use_id = block.get("tool_use_id")
            if tool_use_id:
                ids.append(tool_use_id)
    return ids


def _has_tool_use_with_ids(message: Message, tool_use_ids: set[str]) -> bool:
    """Check if an assistant message has tool_use blocks matching any given IDs.

    Ported from sessionMemoryCompact.ts:hasToolUseWithIds (L175-L186).
    """
    if message.get("type") != "assistant":
        return False
    inner = message.get("message", {})
    if not isinstance(inner, dict):
        return False
    content = inner.get("content")
    if not isinstance(content, list):
        return False
    return any(isinstance(block, dict) and block.get("type") == "tool_use" and block.get("id") in tool_use_ids for block in content)


# ── Token estimation (re-uses micro_compact's rough estimator) ───────────────


def _estimate_message_tokens(messages: list[Message]) -> int:
    """Rough token estimate for a list of messages."""
    total = 0
    for msg in messages:
        inner = msg.get("message", {})
        if isinstance(inner, dict):
            content = inner.get("content")
            total += _rough_token_estimate(content)
    return total


# ── Index adjustment ──────────────────────────────────────────────────────────


def adjust_index_to_preserve_api_invariants(
    messages: list[Message],
    start_index: int,
) -> int:
    """Adjust start_index to preserve tool_use/tool_result pairs and
    thinking-block message.id correlation.

    This is the **full 2-step algorithm** from the upstream TS source
    (sessionMemoryCompact.ts L232-L314):

    Step 1 — Tool pairing:
      Collect ALL tool_result IDs from the kept range (start_index → end).
      Identify which tool_use IDs are NOT already in the kept range.
      Walk backwards to include the assistant messages containing those
      missing tool_use blocks.

    Step 2 — Thinking block preservation:
      Collect message.ids from assistant messages in the kept range.
      Walk backwards to include preceding assistant messages with the
      same message.id (these may contain thinking blocks that need to
      be merged by normalizeMessagesForAPI).

    Bug scenarios this fixes (from upstream comments):
      - Streaming yields separate messages per content block (thinking,
        tool_use) with the same message.id but different uuids.
      - If start_index lands in the middle of such a group, the old
        naive walk-forward algorithm leaves orphan tool_results or
        drops thinking blocks.

    Args:
        messages:    Full message list.
        start_index: Desired split point (messages before this are dropped).

    Returns:
        Adjusted index that preserves API invariants.
    """
    if start_index <= 0 or start_index >= len(messages):
        return start_index

    adjusted_index = start_index

    # ── Step 1: Handle tool_use/tool_result pairs ──────────────────────
    # Collect tool_result IDs from ALL messages in the kept range
    all_tool_result_ids: list[str] = []
    for i in range(start_index, len(messages)):
        all_tool_result_ids.extend(_get_tool_result_ids(messages[i]))

    if all_tool_result_ids:
        # Collect tool_use IDs already in the kept range
        tool_use_ids_in_kept: set[str] = set()
        for i in range(adjusted_index, len(messages)):
            msg = messages[i]
            if msg.get("type") != "assistant":
                continue
            inner = msg.get("message", {})
            if not isinstance(inner, dict):
                continue
            content = inner.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    block_id = block.get("id")
                    if block_id:
                        tool_use_ids_in_kept.add(block_id)

        # Only look for tool_uses NOT already in the kept range
        needed_tool_use_ids = {tid for tid in all_tool_result_ids if tid not in tool_use_ids_in_kept}

        # Walk backwards to find matching tool_use assistant messages
        i = adjusted_index - 1
        while i >= 0 and needed_tool_use_ids:
            msg = messages[i]
            if _has_tool_use_with_ids(msg, needed_tool_use_ids):
                adjusted_index = i
                # Remove found IDs from needed set
                inner = msg.get("message", {})
                if isinstance(inner, dict):
                    content = inner.get("content")
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("id") in needed_tool_use_ids:
                                needed_tool_use_ids.discard(block.get("id"))
            i -= 1

    # ── Step 2: Handle thinking blocks sharing message.id ──────────────
    # Collect message.ids from assistant messages in the kept range
    message_ids_in_kept: set[str] = set()
    for i in range(adjusted_index, len(messages)):
        msg = messages[i]
        if msg.get("type") != "assistant":
            continue
        inner = msg.get("message", {})
        if isinstance(inner, dict) and inner.get("id"):
            message_ids_in_kept.add(inner["id"])

    # Walk backwards for assistant messages with the same message.id
    for i in range(adjusted_index - 1, -1, -1):
        msg = messages[i]
        if msg.get("type") != "assistant":
            continue
        inner = msg.get("message", {})
        if isinstance(inner, dict) and inner.get("id") and inner["id"] in message_ids_in_kept:
            adjusted_index = i

    return adjusted_index


# ── Message-to-keep index calculation ─────────────────────────────────────────


def calculate_messages_to_keep_index(
    messages: list[Message],
    last_summarized_index: int,
) -> int:
    """Calculate the starting index for messages to keep after compaction.

    Starts from lastSummarizedIndex + 1, then expands backwards to meet:
      - At least config.min_tokens tokens
      - At least config.min_text_block_messages with text blocks

    Stops expanding if config.max_tokens is reached.
    Also ensures tool_use/tool_result pairs are not split.
    Respects a compact-boundary floor so preserved-segment chains
    are not broken.

    Ported from sessionMemoryCompact.ts:calculateMessagesToKeepIndex (L324-L397).

    Args:
        messages:              Full message list.
        last_summarized_index: Index of the last message covered by session memory.

    Returns:
        Starting index for the kept message range.
    """
    if not messages:
        return 0

    config = get_session_memory_compact_config()

    # Start from the message after last_summarized_index
    start_index = last_summarized_index + 1 if last_summarized_index >= 0 else len(messages)

    # Calculate current tokens and text-block message count
    total_tokens = 0
    text_block_count = 0
    for i in range(start_index, len(messages)):
        total_tokens += _estimate_message_tokens([messages[i]])
        if has_text_blocks(messages[i]):
            text_block_count += 1

    # Already at or above max cap → don't expand
    if total_tokens >= config.max_tokens:
        return adjust_index_to_preserve_api_invariants(messages, start_index)

    # Already meet both minimums → don't expand
    if total_tokens >= config.min_tokens and text_block_count >= config.min_text_block_messages:
        return adjust_index_to_preserve_api_invariants(messages, start_index)

    # Find compact-boundary floor: never expand past the last boundary
    floor = 0
    for i in range(len(messages) - 1, -1, -1):
        if is_compact_boundary_message(messages[i]):
            floor = i + 1
            break

    # Expand backwards until meeting both minimums or hitting max
    for i in range(start_index - 1, floor - 1, -1):
        msg_tokens = _estimate_message_tokens([messages[i]])
        total_tokens += msg_tokens
        if has_text_blocks(messages[i]):
            text_block_count += 1
        start_index = i

        # Stop if max cap hit
        if total_tokens >= config.max_tokens:
            break

        # Stop if both minimums met
        if total_tokens >= config.min_tokens and text_block_count >= config.min_text_block_messages:
            break

    return adjust_index_to_preserve_api_invariants(messages, start_index)


# ── Feature gate ──────────────────────────────────────────────────────────────


def should_use_session_memory_compaction() -> bool:
    """Check if session memory compaction is enabled.

    The upstream checks GrowthBook feature flags; we use env vars.

    Env vars:
      ENABLE_SM_COMPACT=1   → force enable
      DISABLE_SM_COMPACT=1  → force disable
    """
    if os.environ.get("ENABLE_SM_COMPACT", "").strip().lower() in ("1", "true"):
        return True
    if os.environ.get("DISABLE_SM_COMPACT", "").strip().lower() in ("1", "true"):
        return False
    # Default: enabled when session memory content is available
    # (caller is responsible for passing session_memory_content)
    return True


# ── Main entry point ──────────────────────────────────────────────────────────


def try_session_memory_compaction(
    messages: list[Message],
    agent_id: str | None = None,
    auto_compact_threshold: int = 0,
    *,
    session_memory_content: str | None = None,
    last_summarized_message_id: str | None = None,
    transcript_path: str | None = None,
) -> CompactionResult | None:
    """Attempt session-memory-based compaction.

    Returns a ``CompactionResult`` if compaction succeeded, or ``None``
    if this path isn't viable (session memory not active, insufficient
    savings, etc.).

    Handles two scenarios (matching upstream):
      1. Normal case: last_summarized_message_id is set, keep only
         messages after that ID, expanded to meet token minimums.
      2. Resumed session: last_summarized_message_id is not set but
         session memory has content; keep all messages but use session
         memory as the summary.

    Ported from sessionMemoryCompact.ts:trySessionMemoryCompaction (L514-L630).

    Args:
        messages:                     Full conversation messages.
        agent_id:                     Agent identifier (subagents skip SM compact).
        auto_compact_threshold:       Token threshold that triggered compaction.
        session_memory_content:       The session memory text to use as summary.
        last_summarized_message_id:   UUID of the last message covered by SM.
        transcript_path:              Path to the conversation transcript.

    Returns:
        CompactionResult if successful, None otherwise.
    """
    if not should_use_session_memory_compaction():
        return None

    if not messages:
        return None

    # Subagents don't have session memory
    if agent_id and not agent_id.startswith("main"):
        return None

    # Initialize config from env overrides (once)
    _init_session_memory_compact_config()

    # No session memory content → cannot use this path
    if not session_memory_content:
        logger.debug("sm_compact: no session memory content, skipping")
        return None

    # Session memory is empty template → fall back to LLM compact
    if session_memory_content.strip() == "":
        logger.debug("sm_compact: empty session memory template, skipping")
        return None

    try:
        # Determine last_summarized_index
        if last_summarized_message_id:
            # Normal case: find the message by UUID
            last_summarized_index = -1
            for i, msg in enumerate(messages):
                if msg.get("uuid") == last_summarized_message_id:
                    last_summarized_index = i
                    break

            if last_summarized_index == -1:
                # UUID not found — messages may have been modified
                logger.debug("sm_compact: summarized message ID not found in messages")
                return None
        else:
            # Resumed session: session memory exists but no boundary marker
            last_summarized_index = len(messages) - 1
            logger.debug("sm_compact: resumed session mode")

        # Calculate which messages to keep
        start_index = calculate_messages_to_keep_index(messages, last_summarized_index)

        # Filter out old compact boundary messages from kept range
        messages_to_keep = [m for m in messages[start_index:] if not is_compact_boundary_message(m)]

        # Estimate pre-compact tokens
        pre_compact_tokens = _estimate_message_tokens(messages)

        # Build boundary marker
        last_uuid = messages[-1].get("uuid") if messages else None
        boundary = _create_compact_boundary_message("auto", pre_compact_tokens, last_uuid)

        # Build summary message using session memory content
        summary_text = get_compact_user_summary_message(
            session_memory_content,
            suppress_follow_up_questions=True,
            transcript_path=transcript_path,
            recent_messages_preserved=True,
        )
        summary_msg = _create_user_message(
            summary_text,
            is_compact_summary=True,
            is_visible_in_transcript_only=True,
        )

        # Assemble post-compact messages
        post_compact_messages = [boundary, summary_msg, *messages_to_keep]
        post_compact_tokens = _estimate_message_tokens(post_compact_messages)

        # Check if we actually saved enough tokens
        if auto_compact_threshold > 0 and post_compact_tokens >= auto_compact_threshold:
            logger.debug(
                "sm_compact: post-compact tokens (%d) >= threshold (%d), skipping",
                post_compact_tokens,
                auto_compact_threshold,
            )
            return None

        logger.info(
            "sm_compact: %d → %d tokens (kept %d messages)",
            pre_compact_tokens,
            post_compact_tokens,
            len(messages_to_keep),
        )

        return CompactionResult(
            messages=post_compact_messages,
            summary=session_memory_content,
            tokens_before=pre_compact_tokens,
            tokens_after=post_compact_tokens,
            is_partial=True,
            rounds_preserved=len(messages_to_keep),
        )

    except Exception:
        logger.exception("sm_compact: error during session memory compaction")
        return None
