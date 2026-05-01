# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""agnt_utils — ported infrastructure utilities from Claude Code v2.1.91.

Modules:
    token_budget:      Parse "+500k" / "use 2M tokens" budget directives
    circular_buffer:   Fixed-size ring buffer with O(1) add / O(k) get_recent
    activity_manager:  CLI/user activity tracking with timeout-based dedup
    memoize:           TTL + LRU memoization with write-through refresh
    token_estimate:    Heuristic token counting for context window management
    truncate:          Width-aware text truncation for terminal UI
"""

from packages.agnt_utils.circular_buffer import CircularBuffer
from packages.agnt_utils.memoize import memoize_with_lru, memoize_with_ttl
from packages.agnt_utils.token_budget import (
    get_budget_continuation_message,
    parse_token_budget,
)
from packages.agnt_utils.token_estimate import (
    rough_token_estimate,
    rough_token_estimate_for_block,
    rough_token_estimate_for_content,
    rough_token_estimate_for_message,
    rough_token_estimate_for_messages,
    token_count_with_estimation,
)
from packages.agnt_utils.truncate import (
    string_width,
    truncate,
    truncate_path_middle,
    truncate_to_width,
    wrap_text,
)

__all__ = [
    "CircularBuffer",
    "get_budget_continuation_message",
    "memoize_with_lru",
    "memoize_with_ttl",
    "parse_token_budget",
    "rough_token_estimate",
    "rough_token_estimate_for_block",
    "rough_token_estimate_for_content",
    "rough_token_estimate_for_message",
    "rough_token_estimate_for_messages",
    "string_width",
    "token_count_with_estimation",
    "truncate",
    "truncate_path_middle",
    "truncate_to_width",
    "wrap_text",
]
