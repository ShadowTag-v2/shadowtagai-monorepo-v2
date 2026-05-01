"""Token estimation heuristics.

Ported from Claude Code's ``tokenEstimation.ts`` — provides fast,
local-first token count estimation for messages and content blocks
without requiring API calls.

Architecture
~~~~~~~~~~~~
- **Rough estimation**: Default 4 bytes per token with file-type-aware
  overrides (JSON uses 2 bytes/token due to dense single-character tokens).
- **Block-aware**: Handles text, tool_use, tool_result, thinking,
  image/document blocks (fixed 2000 token estimate matching microCompact).
- **Message-level**: Aggregate estimation across conversation message lists.

Usage::

    from packages.token_estimation import rough_token_estimate

    tokens = rough_token_estimate("Hello, world!")  # ~3 tokens
    json_tokens = rough_token_estimate('{"key": "value"}', file_ext="json")  # ~8 tokens
"""

from packages.token_estimation.estimator import (
    bytes_per_token_for_file_type,
    rough_token_estimate,
    rough_token_estimate_for_block,
    rough_token_estimate_for_file_type,
    rough_token_estimate_for_messages,
)


def estimate_tokens(content: str, *, model: str | None = None) -> int:
    """High-level token estimation with optional model hint.

    Delegates to ``rough_token_estimate`` for the actual counting.
    The *model* parameter is accepted for API compatibility but does not
    currently alter the heuristic (all models use 4-bytes-per-token).
    """
    return rough_token_estimate(content)


__all__ = [
    "bytes_per_token_for_file_type",
    "estimate_tokens",
    "rough_token_estimate",
    "rough_token_estimate_for_block",
    "rough_token_estimate_for_file_type",
    "rough_token_estimate_for_messages",
]
