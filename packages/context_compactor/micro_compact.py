# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Microcompaction — tool-result clearing and time-based staleness pruning.

Ported from: compact/microCompact.ts + timeBasedMCConfig.ts
Reference: AGNT STATE B Spec P1.1

Architecture:
  - `microcompact_messages()` → main entry point
  - `evaluate_time_based_trigger()` → check if idle gap exceeds threshold
  - `maybe_time_based_microcompact()` → execute time-based clearing
  - `collect_compactable_tool_ids()` → find compactable tool_use IDs
  - `calculate_tool_result_tokens()` → estimate tokens in tool results
  - `estimate_message_tokens()` → estimate total tokens across messages

Note: The "cached microcompact" path (cache_edits API) is ant-gated in the
original source and requires Anthropic's proprietary cache editing protocol.
That path is excluded from this port — our sovereign engine uses the
time-based microcompact path for pre-request context shrinking, and delegates
to the 4-layer pipeline (L1-L4) in compactor.py for reactive compaction.
"""

from __future__ import annotations

import copy
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from context_compactor.token_estimator import rough_token_estimate

logger = logging.getLogger(__name__)


# --- Constants ported from microCompact.ts ---

# Marker text for cleared tool results. Must match the sentinel used by
# the storage layer so downstream consumers can detect cleared results.
TIME_BASED_MC_CLEARED_MESSAGE = "[Old tool result content cleared]"

# Conservative estimate for image/document blocks (~2000 tokens regardless
# of format, matching Claude's vision pricing heuristic).
IMAGE_MAX_TOKEN_SIZE = 2000

# Tool names eligible for compaction. Only tool results from these tools
# are cleared during microcompaction. Order is irrelevant (set lookup).
COMPACTABLE_TOOLS: frozenset[str] = frozenset(
    {
        "Read",  # FILE_READ_TOOL_NAME
        "Bash",  # Bash shell
        "Terminal",  # Terminal shell
        "Grep",  # GREP_TOOL_NAME
        "Glob",  # GLOB_TOOL_NAME
        "WebSearch",  # WEB_SEARCH_TOOL_NAME
        "WebFetch",  # WEB_FETCH_TOOL_NAME
        "Edit",  # FILE_EDIT_TOOL_NAME
        "Write",  # FILE_WRITE_TOOL_NAME
        # Extended names for broader compatibility
        "file_read",
        "bash",
        "shell",
        "grep_search",
        "glob",
        "web_search",
        "web_fetch",
        "file_edit",
        "file_write",
        "read_file",
        "run_command",
        "search_files",
        "list_dir",
        "view_file",
    }
)

# Token estimation padding factor — pad by 4/3 to be conservative since
# we're approximating (matches the TS implementation exactly).
ESTIMATION_PADDING_FACTOR = 4 / 3


# --- Configuration ---


@dataclass(frozen=True)
class TimeBasedMCConfig:
    """Configuration for time-based microcompaction.

    Ported from: timeBasedMCConfig.ts (GrowthBook feature flag defaults).

    Attributes:
        enabled: Master switch. When False, time-based MC is a no-op.
        gap_threshold_minutes: Trigger when (now - last assistant timestamp)
            exceeds this many minutes. 60 is the safe choice: the server's 1h
            cache TTL is guaranteed expired for all users.
        keep_recent: Keep this many most-recent compactable tool results.
            Older results are cleared.
    """

    enabled: bool = True  # Default ON for sovereign engine (no GrowthBook)
    gap_threshold_minutes: float = 60.0
    keep_recent: int = 5


# Singleton config — can be overridden for testing
_config = TimeBasedMCConfig()


def get_time_based_mc_config() -> TimeBasedMCConfig:
    """Return the current time-based MC configuration."""
    return _config


def set_time_based_mc_config(config: TimeBasedMCConfig) -> None:
    """Override the time-based MC configuration (for testing)."""
    global _config
    _config = config


# --- Result types ---


@dataclass
class MicrocompactResult:
    """Result of a microcompaction operation.

    Attributes:
        messages: The (possibly modified) message list.
        tokens_saved: Estimated tokens reclaimed by clearing.
        tools_cleared: Count of tool results that were cleared.
        tools_kept: Count of tool results that were preserved.
        trigger_type: What triggered the compaction ('time_based' or None).
        gap_minutes: Gap in minutes since last assistant message (if triggered).
    """

    messages: list[Any] = field(default_factory=list)
    tokens_saved: int = 0
    tools_cleared: int = 0
    tools_kept: int = 0
    trigger_type: str | None = None
    gap_minutes: float = 0.0


# --- Token calculation ---


def calculate_tool_result_tokens(block: dict[str, Any]) -> int:
    """Calculate estimated token count for a tool_result block.

    Handles string content, array-of-blocks content, and image/document blocks.

    Args:
        block: A tool_result content block dict.

    Returns:
        Estimated token count.
    """
    content = block.get("content")
    if content is None:
        return 0

    if isinstance(content, str):
        return rough_token_estimate(content)

    if isinstance(content, list):
        total = 0
        for item in content:
            item_type = item.get("type", "") if isinstance(item, dict) else ""
            if item_type == "text":
                total += rough_token_estimate(item.get("text", ""))
            elif item_type in ("image", "document"):
                total += IMAGE_MAX_TOKEN_SIZE
        return total

    return 0


def estimate_message_tokens(messages: list[Any]) -> int:
    """Estimate token count for messages by extracting text content.

    Pads estimate by 4/3 to be conservative since we're approximating.
    Matches the TS ``estimateMessageTokens`` function exactly.

    Args:
        messages: List of message dicts or Message dataclass instances.

    Returns:
        Conservative estimated token count.
    """
    import math

    total_tokens = 0

    for message in messages:
        role = _get_role(message)
        if role not in ("user", "assistant"):
            continue

        content = _get_content(message)
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue

            block_type = block.get("type", "")

            if block_type == "text":
                total_tokens += rough_token_estimate(block.get("text", ""))
            elif block_type == "tool_result":
                total_tokens += calculate_tool_result_tokens(block)
            elif block_type in ("image", "document"):
                total_tokens += IMAGE_MAX_TOKEN_SIZE
            elif block_type == "thinking":
                total_tokens += rough_token_estimate(block.get("thinking", ""))
            elif block_type == "redacted_thinking":
                total_tokens += rough_token_estimate(block.get("data", ""))
            elif block_type == "tool_use":
                name = block.get("name", "")
                input_data = block.get("input", {})
                total_tokens += rough_token_estimate(name + json.dumps(input_data, separators=(",", ":")))
            else:
                # server_tool_use, web_search_tool_result, etc.
                total_tokens += rough_token_estimate(json.dumps(block, separators=(",", ":")))

    return math.ceil(total_tokens * ESTIMATION_PADDING_FACTOR)


# --- Core logic ---


def collect_compactable_tool_ids(messages: list[Any]) -> list[str]:
    """Walk messages and collect tool_use IDs whose tool name is compactable.

    Only scans assistant messages for tool_use blocks with names in
    ``COMPACTABLE_TOOLS``. Returns IDs in encounter order.

    Args:
        messages: List of message dicts or dataclass instances.

    Returns:
        List of tool_use IDs eligible for compaction.
    """
    ids: list[str] = []

    for message in messages:
        role = _get_role(message)
        if role != "assistant":
            continue

        content = _get_content(message)
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name", "") in COMPACTABLE_TOOLS:
                tool_id = block.get("id", "")
                if tool_id:
                    ids.append(tool_id)

    return ids


def evaluate_time_based_trigger(
    messages: list[Any],
    query_source: str | None = None,
) -> tuple[float, TimeBasedMCConfig] | None:
    """Check whether the time-based trigger should fire for this request.

    Returns the measured gap (minutes since last assistant message) and config
    when the trigger fires, or None when it doesn't.

    Trigger conditions (all must be true):
      - Time-based MC is enabled
      - query_source is a main-thread source (or explicitly provided)
      - Gap since last assistant message exceeds threshold
      - The gap value is finite and positive

    Args:
        messages: Conversation messages.
        query_source: The originating query source (main thread vs subagent).

    Returns:
        Tuple of (gap_minutes, config) if trigger fires, else None.
    """
    config = get_time_based_mc_config()

    if not config.enabled:
        return None

    # Require an explicit main-thread source. Several callers invoke
    # microcompact without a source for analysis-only purposes — they
    # should not trigger time-based clearing.
    if query_source is None:
        return None

    if not _is_main_thread_source(query_source):
        return None

    # Find the last assistant message
    last_assistant = _find_last_assistant(messages)
    if last_assistant is None:
        return None

    # Calculate gap
    timestamp = _get_timestamp(last_assistant)
    if timestamp <= 0:
        return None

    gap_minutes = (time.time() - timestamp) / 60.0

    if not (gap_minutes > 0 and gap_minutes < float("inf")):
        return None

    if gap_minutes < config.gap_threshold_minutes:
        return None

    return (gap_minutes, config)


def maybe_time_based_microcompact(
    messages: list[Any],
    query_source: str | None = None,
) -> MicrocompactResult | None:
    """Time-based microcompact: clear stale tool results after idle threshold.

    When the gap since the last assistant message exceeds the configured
    threshold, content-clear all but the most recent N compactable tool
    results. Unlike cached MC, this mutates message content directly — the
    cache is cold so there's no prefix to preserve.

    Args:
        messages: Conversation messages (will be deep-copied if modified).
        query_source: Originating query source.

    Returns:
        MicrocompactResult if clearing happened, else None.
    """
    trigger = evaluate_time_based_trigger(messages, query_source)
    if trigger is None:
        return None

    gap_minutes, config = trigger

    compactable_ids = collect_compactable_tool_ids(messages)
    if not compactable_ids:
        return None

    # Floor at 1: clearing ALL results leaves the model with zero working
    # context. Always keep at least the last result.
    keep_recent = max(1, config.keep_recent)
    keep_set = set(compactable_ids[-keep_recent:])
    clear_set = {tid for tid in compactable_ids if tid not in keep_set}

    if not clear_set:
        return None

    # Deep-copy messages to avoid mutating the caller's list
    result_messages = copy.deepcopy(messages)
    tokens_saved = 0

    for message in result_messages:
        role = _get_role(message)
        if role != "user":
            continue

        content = _get_content(message)
        if not isinstance(content, list):
            continue

        touched = False
        new_content = []
        for block in content:
            if not isinstance(block, dict):
                new_content.append(block)
                continue

            if (
                block.get("type") == "tool_result"
                and block.get("tool_use_id", "") in clear_set
                and block.get("content") != TIME_BASED_MC_CLEARED_MESSAGE
            ):
                tokens_saved += calculate_tool_result_tokens(block)
                new_content.append(
                    {
                        **block,
                        "content": TIME_BASED_MC_CLEARED_MESSAGE,
                    }
                )
                touched = True
            else:
                new_content.append(block)

        if touched:
            _set_content(message, new_content)

    if tokens_saved == 0:
        return None

    logger.info(
        "[TIME-BASED MC] gap %.0fmin > %.0fmin, cleared %d tool results (~%d tokens), kept last %d",
        gap_minutes,
        config.gap_threshold_minutes,
        len(clear_set),
        tokens_saved,
        len(keep_set),
    )

    return MicrocompactResult(
        messages=result_messages,
        tokens_saved=tokens_saved,
        tools_cleared=len(clear_set),
        tools_kept=len(keep_set),
        trigger_type="time_based",
        gap_minutes=gap_minutes,
    )


def microcompact_messages(
    messages: list[Any],
    query_source: str | None = None,
) -> MicrocompactResult:
    """Main entry point for microcompaction.

    Tries time-based microcompact first (for cold-cache scenarios). If that
    doesn't fire, returns messages unchanged — the 4-layer pipeline in
    compactor.py handles reactive compaction when context pressure builds.

    The cached microcompact path (cache_edits API) from the original source
    is excluded — it requires Anthropic's proprietary protocol.

    Args:
        messages: Conversation messages.
        query_source: Originating query source identifier.

    Returns:
        MicrocompactResult with possibly-modified messages.
    """
    # Time-based trigger runs first and short-circuits. If the gap since the
    # last assistant message exceeds the threshold, the server cache has expired
    # and the full prefix will be rewritten regardless — so content-clear old
    # tool results now, before the request, to shrink what gets rewritten.
    time_based_result = maybe_time_based_microcompact(messages, query_source)
    if time_based_result is not None:
        return time_based_result

    # No compaction needed — return messages unchanged
    return MicrocompactResult(messages=messages)


# --- Internal helpers ---


def _get_role(msg: Any) -> str:
    """Extract role/type from a message."""
    if isinstance(msg, dict):
        return msg.get("type", msg.get("role", ""))
    return getattr(msg, "role", getattr(msg, "type", ""))


def _get_content(msg: Any) -> Any:
    """Extract content from a message, handling nested message dict."""
    if isinstance(msg, dict):
        # Claude format: msg.message.content
        inner = msg.get("message")
        if isinstance(inner, dict):
            return inner.get("content")
        return msg.get("content")
    # Dataclass with .message.content or .content
    inner = getattr(msg, "message", None)
    if inner and hasattr(inner, "content"):
        return inner.content
    return getattr(msg, "content", None)


def _set_content(msg: Any, new_content: list[Any]) -> None:
    """Set content on a message, handling nested message dict."""
    if isinstance(msg, dict):
        inner = msg.get("message")
        if isinstance(inner, dict):
            inner["content"] = new_content
        else:
            msg["content"] = new_content
    elif hasattr(msg, "message") and hasattr(msg.message, "content"):
        msg.message.content = new_content
    elif hasattr(msg, "content"):
        msg.content = new_content


def _get_timestamp(msg: Any) -> float:
    """Extract timestamp from a message."""
    if isinstance(msg, dict):
        ts = msg.get("timestamp", 0)
    else:
        ts = getattr(msg, "timestamp", 0)

    if isinstance(ts, str):
        try:
            import datetime

            dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.timestamp()
        except ValueError, TypeError:
            return 0.0

    return float(ts) if ts else 0.0


def _find_last_assistant(messages: list[Any]) -> Any | None:
    """Find the last assistant message in the list."""
    for msg in reversed(messages):
        if _get_role(msg) == "assistant":
            return msg
    return None


def _is_main_thread_source(query_source: str) -> bool:
    """Check if query source is a main-thread source.

    Prefix-match because promptCategory.ts sets the querySource to
    'repl_main_thread:outputStyle:<style>' when a non-default output style
    is active. The bare 'repl_main_thread' is only used for the default style.
    """
    return query_source.startswith("repl_main_thread") or query_source == "main"
