# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Microcompact — tool-result clearing + time-based eviction.

Ported from microCompact.ts.  This is Layer 0 of the compaction pipeline:
it runs BEFORE the API call and clears old tool-result content that the
model is unlikely to reference.

Two modes:
  1. **Count-based**: Clear all but the N most recent compactable results.
  2. **Time-based**: Clear when the gap since the last assistant message
     exceeds a configured threshold (server cache TTL expired).

The cleared content is replaced with the sentinel string
``[Old tool result content cleared]``; the tool_use/tool_result pair
structure is preserved so the API contract is maintained.
"""

from __future__ import annotations

import copy
import json
import time
from typing import Any

from packages.agnt_utils.compact.time_based_mc_config import get_time_based_mc_config
from packages.agnt_utils.compact.types import (
    CLEARED_CONTENT_SENTINEL,
    COMPACTABLE_TOOLS,
    Message,
)

# ── Module-level state (matches upstream's module globals) ────────────────────
# Track compactable tool_use IDs we have already cleared, so re-running
# microcompact on the same messages is idempotent.
_cleared_tool_ids: set[str] = set()

# Timestamp (epoch seconds) of the last assistant message seen by
# the main loop.  Updated externally via ``record_assistant_timestamp``.
_last_assistant_ts: float = 0.0

# Maximum tokens assumed for an image content block.
IMAGE_MAX_TOKEN_SIZE = 2000


def reset_microcompact_state() -> None:
    """Reset all module-level tracking state.

    Called by ``run_post_compact_cleanup`` after compaction, since all
    old message IDs are invalidated.
    """
    global _cleared_tool_ids, _last_assistant_ts
    _cleared_tool_ids = set()
    _last_assistant_ts = 0.0


def record_assistant_timestamp(ts: float | None = None) -> None:
    """Record the timestamp of a main-loop assistant message.

    Args:
        ts: Epoch seconds.  Defaults to ``time.time()``.
    """
    global _last_assistant_ts
    _last_assistant_ts = ts if ts is not None else time.time()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _is_compactable_tool_result(msg: Message) -> bool:
    """Return True if *msg* is a tool_result whose content can be cleared."""
    if msg.get("type") != "user":
        return False
    inner = msg.get("message", {})
    if not isinstance(inner, dict):
        return False
    content = inner.get("content")
    if not isinstance(content, list):
        return False
    # A compactable tool_result has a tool_result block whose paired
    # tool_use name is in COMPACTABLE_TOOLS.
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_result":
            # The tool name is not directly on the tool_result — it's on
            # the preceding assistant's tool_use block.  We store a
            # metadata hint ``_tool_name`` when building messages.  If
            # absent, default to compactable (safe over-clearing).
            tool_name = block.get("_tool_name", "")
            if not tool_name or tool_name in COMPACTABLE_TOOLS:
                return True
    return False


def _is_already_cleared(msg: Message) -> bool:
    """Return True if the tool result content is already the sentinel."""
    inner = msg.get("message", {})
    if not isinstance(inner, dict):
        return False
    content = inner.get("content")
    if not isinstance(content, list):
        return content == CLEARED_CONTENT_SENTINEL
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_result":
            result_content = block.get("content")
            if isinstance(result_content, str) and result_content == CLEARED_CONTENT_SENTINEL:
                return True
            if isinstance(result_content, list):
                for sub in result_content:
                    if isinstance(sub, dict) and sub.get("text") == CLEARED_CONTENT_SENTINEL:
                        return True
    return False


def _clear_tool_result_content(msg: Message) -> Message:
    """Return a copy of *msg* with tool-result content replaced by sentinel."""
    cleared = copy.deepcopy(msg)
    inner = cleared.get("message", {})
    if not isinstance(inner, dict):
        return cleared
    content = inner.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                block["content"] = CLEARED_CONTENT_SENTINEL
    return cleared


def _rough_token_estimate(content: Any) -> int:
    """Quick token estimate without importing the full module."""
    if content is None:
        return 0
    if isinstance(content, str):
        return round(len(content) / 4)
    if isinstance(content, list):
        total = 0
        for block in content:
            if isinstance(block, str):
                total += round(len(block) / 4)
            elif isinstance(block, dict):
                if block.get("type") in ("image", "document"):
                    total += IMAGE_MAX_TOKEN_SIZE
                elif block.get("type") == "text":
                    total += round(len(block.get("text", "")) / 4)
                else:
                    total += round(len(json.dumps(block, default=str)) / 4)
        return total
    return round(len(json.dumps(content, default=str)) / 4)


# ── Main entry point ─────────────────────────────────────────────────────────


def microcompact_messages(
    messages: list[Message],
    *,
    keep_recent: int = 3,
    query_source: str | None = None,
) -> tuple[list[Message], int]:
    """Run microcompaction on *messages*, returning (new_messages, tokens_freed).

    This is a non-destructive operation — it returns a new list with
    cleared content.  The caller decides whether to use the result.

    Args:
        messages:     Ordered conversation messages.
        keep_recent:  Number of most-recent compactable results to keep.
        query_source: The query source; subagents are skipped for
                      time-based MC.

    Returns:
        Tuple of (microcompacted messages, estimated tokens freed).
    """
    # Time-based override: if the gap since last assistant exceeds
    # the threshold, use a tighter keep_recent from config.
    effective_keep = keep_recent
    if query_source is None or query_source.startswith("repl_main_thread"):
        mc_config = get_time_based_mc_config()
        if mc_config.enabled and _last_assistant_ts > 0:
            gap_minutes = (time.time() - _last_assistant_ts) / 60
            if gap_minutes >= mc_config.gap_threshold_minutes:
                effective_keep = mc_config.keep_recent

    # Identify compactable indices (excluding already-cleared)
    compactable_indices: list[int] = []
    for i, msg in enumerate(messages):
        if _is_compactable_tool_result(msg) and not _is_already_cleared(msg):
            compactable_indices.append(i)

    # Nothing to do if we have fewer compactable results than the keep threshold
    if len(compactable_indices) <= effective_keep:
        return messages, 0

    # Clear all but the most recent `effective_keep`
    indices_to_clear = compactable_indices[: len(compactable_indices) - effective_keep]

    tokens_freed = 0
    result = list(messages)  # shallow copy
    for idx in indices_to_clear:
        msg = result[idx]
        inner = msg.get("message", {})
        content = inner.get("content") if isinstance(inner, dict) else None
        tokens_freed += _rough_token_estimate(content)
        result[idx] = _clear_tool_result_content(msg)

    return result, tokens_freed
