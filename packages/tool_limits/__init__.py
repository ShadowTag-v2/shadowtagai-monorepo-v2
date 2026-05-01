"""Tool Result Size Limits — system-wide constants for context overflow prevention.

Ported from Claude Code v2.1.91 constants/toolLimits.ts + apiLimits.ts.
Dependency-free module — no imports beyond stdlib.

These constants define hard boundaries for tool output sizes to prevent
context window overflow during parallel tool execution.
"""

from packages.tool_limits.constants import (
    API_IMAGE_MAX_BASE64_SIZE,
    API_MAX_MEDIA_PER_REQUEST,
    API_PDF_MAX_PAGES,
    BYTES_PER_TOKEN,
    DEFAULT_MAX_RESULT_SIZE_CHARS,
    IMAGE_MAX_HEIGHT,
    IMAGE_MAX_WIDTH,
    IMAGE_TARGET_RAW_SIZE,
    MAX_TOOL_RESULT_BYTES,
    MAX_TOOL_RESULT_TOKENS,
    MAX_TOOL_RESULTS_PER_MESSAGE_CHARS,
    PDF_AT_MENTION_INLINE_THRESHOLD,
    PDF_EXTRACT_SIZE_THRESHOLD,
    PDF_MAX_EXTRACT_SIZE,
    PDF_MAX_PAGES_PER_READ,
    PDF_TARGET_RAW_SIZE,
    TOOL_SUMMARY_MAX_LENGTH,
    is_result_over_limit,
    is_message_over_budget,
)

__all__ = [
    "API_IMAGE_MAX_BASE64_SIZE",
    "API_MAX_MEDIA_PER_REQUEST",
    "API_PDF_MAX_PAGES",
    "BYTES_PER_TOKEN",
    "DEFAULT_MAX_RESULT_SIZE_CHARS",
    "IMAGE_MAX_HEIGHT",
    "IMAGE_MAX_WIDTH",
    "IMAGE_TARGET_RAW_SIZE",
    "MAX_TOOL_RESULT_BYTES",
    "MAX_TOOL_RESULT_TOKENS",
    "MAX_TOOL_RESULTS_PER_MESSAGE_CHARS",
    "PDF_AT_MENTION_INLINE_THRESHOLD",
    "PDF_EXTRACT_SIZE_THRESHOLD",
    "PDF_MAX_EXTRACT_SIZE",
    "PDF_MAX_PAGES_PER_READ",
    "PDF_TARGET_RAW_SIZE",
    "TOOL_SUMMARY_MAX_LENGTH",
    "is_result_over_limit",
    "is_message_over_budget",
]
