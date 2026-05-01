# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""agnt_utils — ported infrastructure utilities from Claude Code v2.1.91.

Modules (original 6):
    token_budget:      Parse "+500k" / "use 2M tokens" budget directives
    circular_buffer:   Fixed-size ring buffer with O(1) add / O(k) get_recent
    activity_manager:  CLI/user activity tracking with timeout-based dedup
    memoize:           TTL + LRU memoization with write-through refresh
    token_estimate:    Heuristic token counting for context window management
    truncate:          Width-aware text truncation for terminal UI

New modules (7 — batch 2):
    sequential:        Async sequential execution wrapper (race condition guard)
    sanitization:      Unicode smuggling defense (HackerOne #3086545)
    errors:            Structured error hierarchy + stack truncation
    string_utils:      String accumulators, truncation, formatting helpers
    hash_utils:        Deterministic djb2 + SHA-256 hashing
    xml_escape:        XML/HTML entity escaping for prompt safety
    sleep_utils:       Cancellable async sleep + timeout guards
"""

from packages.agnt_utils.circular_buffer import CircularBuffer
from packages.agnt_utils.errors import (
    AbortError,
    AgntError,
    ConfigParseError,
    ShellError,
    TelemetrySafeError,
    classify_http_error,
    error_message,
    get_errno_code,
    has_exact_message,
    is_abort_error,
    is_enoent,
    is_fs_inaccessible,
    short_error_stack,
    to_error,
)
from packages.agnt_utils.hash_utils import djb2_hash, hash_content, hash_pair
from packages.agnt_utils.memoize import memoize_with_lru, memoize_with_ttl
from packages.agnt_utils.sanitization import (
    partially_sanitize_unicode,
    recursively_sanitize_unicode,
)
from packages.agnt_utils.sequential import sequential
from packages.agnt_utils.sleep_utils import cancellable_sleep, with_timeout
from packages.agnt_utils.string_utils import (
    EndTruncatingAccumulator,
    capitalize_first,
    count_char,
    first_line_of,
    normalize_fullwidth_digits,
    normalize_fullwidth_space,
    plural,
    safe_join_lines,
    truncate_to_lines,
)
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
from packages.agnt_utils.xml_escape import escape_xml, escape_xml_attr

__all__ = [
    # ── Original batch ────────────────────────────────────────────────
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
    # ── Batch 2: sequential ───────────────────────────────────────────
    "sequential",
    # ── Batch 2: sanitization ─────────────────────────────────────────
    "partially_sanitize_unicode",
    "recursively_sanitize_unicode",
    # ── Batch 2: errors ───────────────────────────────────────────────
    "AbortError",
    "AgntError",
    "ConfigParseError",
    "ShellError",
    "TelemetrySafeError",
    "classify_http_error",
    "error_message",
    "get_errno_code",
    "has_exact_message",
    "is_abort_error",
    "is_enoent",
    "is_fs_inaccessible",
    "short_error_stack",
    "to_error",
    # ── Batch 2: string_utils ─────────────────────────────────────────
    "EndTruncatingAccumulator",
    "capitalize_first",
    "count_char",
    "first_line_of",
    "normalize_fullwidth_digits",
    "normalize_fullwidth_space",
    "plural",
    "safe_join_lines",
    "truncate_to_lines",
    # ── Batch 2: hash_utils ───────────────────────────────────────────
    "djb2_hash",
    "hash_content",
    "hash_pair",
    # ── Batch 2: xml_escape ───────────────────────────────────────────
    "escape_xml",
    "escape_xml_attr",
    # ── Batch 2: sleep_utils ──────────────────────────────────────────
    "cancellable_sleep",
    "with_timeout",
]
