"""Tool Result Size Limits & API Limits — dependency-free constants.

Ported from Claude Code v2.1.91:
  - constants/toolLimits.ts
  - constants/apiLimits.ts

Design invariant: This file MUST remain dependency-free to prevent
circular imports. No imports beyond Python stdlib.

Last verified against source: 2026-05-01
"""

from __future__ import annotations

# =============================================================================
# TOOL RESULT LIMITS (from toolLimits.ts)
# =============================================================================

# Default maximum size in characters for tool results before they get persisted
# to disk. When exceeded, the result is saved to a file and the model receives
# a preview with the file path instead of the full content.
#
# Individual tools may declare a lower max_result_size_chars, but this constant
# acts as a system-wide cap regardless of what tools declare.
DEFAULT_MAX_RESULT_SIZE_CHARS: int = 50_000

# Maximum size for tool results in tokens.
# Based on analysis of tool result sizes, set to a reasonable upper bound
# to prevent excessively large tool results from consuming too much context.
# This is approximately 400KB of text (assuming ~4 bytes per token).
MAX_TOOL_RESULT_TOKENS: int = 100_000

# Bytes per token estimate for calculating token count from byte size.
# This is a conservative estimate — actual token count may vary.
BYTES_PER_TOKEN: int = 4

# Maximum size for tool results in bytes (derived from token limit).
MAX_TOOL_RESULT_BYTES: int = MAX_TOOL_RESULT_TOKENS * BYTES_PER_TOKEN

# Default maximum aggregate size in characters for tool_result blocks within
# a SINGLE user message (one turn's batch of parallel tool results). When a
# message's blocks together exceed this, the largest blocks in that message
# are persisted to disk and replaced with previews until under budget.
# Messages are evaluated independently — a 150K result in one turn and a
# 150K result in the next are both untouched.
#
# This prevents N parallel tools from each hitting the per-tool max and
# collectively producing e.g. 10 × 40K = 400K in one turn's user message.
MAX_TOOL_RESULTS_PER_MESSAGE_CHARS: int = 200_000

# Maximum character length for tool summary strings in compact views.
# Used by get_tool_use_summary() implementations to truncate long inputs
# for display in grouped agent rendering.
TOOL_SUMMARY_MAX_LENGTH: int = 50


# =============================================================================
# IMAGE LIMITS (from apiLimits.ts)
# =============================================================================

# Maximum base64-encoded image size (API enforced).
# The API rejects images where the base64 string length exceeds this value.
# Note: This is the base64 length, NOT raw bytes. Base64 increases size by ~33%.
API_IMAGE_MAX_BASE64_SIZE: int = 5 * 1024 * 1024  # 5 MB

# Target raw image size to stay under base64 limit after encoding.
# Base64 encoding increases size by 4/3, so we derive the max raw size:
# raw_size * 4/3 = base64_size → raw_size = base64_size * 3/4
IMAGE_TARGET_RAW_SIZE: int = (API_IMAGE_MAX_BASE64_SIZE * 3) // 4  # 3.75 MB

# Client-side maximum dimensions for image resizing.
# The API internally resizes images larger than 1568px, but these client-side
# limits are slightly larger to preserve quality when beneficial.
IMAGE_MAX_WIDTH: int = 2000
IMAGE_MAX_HEIGHT: int = 2000


# =============================================================================
# PDF LIMITS (from apiLimits.ts)
# =============================================================================

# Maximum raw PDF file size that fits within the API request limit after encoding.
# The API has a 32MB total request size limit. Base64 encoding increases size by
# ~33% (4/3), so 20MB raw → ~27MB base64, leaving room for conversation context.
PDF_TARGET_RAW_SIZE: int = 20 * 1024 * 1024  # 20 MB

# Maximum number of pages in a PDF accepted by the API.
API_PDF_MAX_PAGES: int = 100

# Size threshold above which PDFs are extracted into page images
# instead of being sent as base64 document blocks.
PDF_EXTRACT_SIZE_THRESHOLD: int = 3 * 1024 * 1024  # 3 MB

# Maximum PDF file size for the page extraction path. PDFs larger than
# this are rejected to avoid processing extremely large files.
PDF_MAX_EXTRACT_SIZE: int = 100 * 1024 * 1024  # 100 MB

# Max pages the Read tool will extract in a single call with the pages parameter.
PDF_MAX_PAGES_PER_READ: int = 20

# PDFs with more pages than this get the reference treatment on @ mention
# instead of being inlined into context.
PDF_AT_MENTION_INLINE_THRESHOLD: int = 10


# =============================================================================
# MEDIA LIMITS (from apiLimits.ts)
# =============================================================================

# Maximum number of media items (images + PDFs) allowed per API request.
# The API rejects requests exceeding this limit with a confusing error.
# We validate client-side to provide a clear error message.
API_MAX_MEDIA_PER_REQUEST: int = 100


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def is_result_over_limit(
  result_chars: int,
  *,
  custom_limit: int | None = None,
) -> bool:
  """Check if a single tool result exceeds the character limit.

  Args:
      result_chars: Length of the tool result in characters.
      custom_limit: Optional per-tool limit (must be <= system cap).

  Returns:
      True if the result should be persisted to disk.
  """
  effective_limit = min(
    custom_limit or DEFAULT_MAX_RESULT_SIZE_CHARS,
    DEFAULT_MAX_RESULT_SIZE_CHARS,
  )
  return result_chars > effective_limit


def is_message_over_budget(
  total_result_chars: int,
  *,
  budget_override: int | None = None,
) -> bool:
  """Check if aggregate tool results in a message exceed the per-message budget.

  Args:
      total_result_chars: Total characters across all tool results in one message.
      budget_override: Runtime override (e.g., from feature flags).

  Returns:
      True if the message needs result trimming.
  """
  budget = budget_override or MAX_TOOL_RESULTS_PER_MESSAGE_CHARS
  return total_result_chars > budget
