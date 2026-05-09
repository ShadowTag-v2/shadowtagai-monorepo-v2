# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Token Estimator — Heuristic token counting for context budget management.

Architecture adopted from claude_code_services/src/services/tokenEstimation.ts.

Key heuristics:
    - Text: ~4 bytes per token (general prose/code)
    - JSON: ~2 bytes per token (dense single-char tokens)
    - Images/Documents: flat 2000 tokens (conservative)
    - Tool use: name + JSON-serialized input
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

_IMAGE_TOKEN_ESTIMATE = 2000
_DEFAULT_BYTES_PER_TOKEN = 4
_JSON_BYTES_PER_TOKEN = 2


def rough_token_estimate(content: str, bytes_per_token: float = _DEFAULT_BYTES_PER_TOKEN) -> int:
    """Estimate token count from raw text using a bytes-per-token ratio."""
    if not content:
        return 0
    return round(len(content) / bytes_per_token)


def bytes_per_token_for_file_type(file_extension: str) -> float:
    """Return estimated bytes-per-token ratio for a file extension."""
    if file_extension in ("json", "jsonl", "jsonc"):
        return _JSON_BYTES_PER_TOKEN
    return _DEFAULT_BYTES_PER_TOKEN


def rough_token_estimate_for_file(content: str, file_extension: str) -> int:
    """Estimate token count using a file-type-aware ratio."""
    return rough_token_estimate(content, bytes_per_token_for_file_type(file_extension))


def estimate_block_tokens(block: dict[str, Any]) -> int:
    """Estimate token count for a single content block."""
    block_type = block.get("type", "unknown")

    if block_type == "text":
        return rough_token_estimate(block.get("text", ""))

    if block_type in ("image", "document"):
        return _IMAGE_TOKEN_ESTIMATE

    if block_type == "tool_use":
        name = block.get("name", "")
        input_data = block.get("input", {})
        try:
            serialized = name + json.dumps(input_data, separators=(",", ":"))
        except TypeError, ValueError:
            serialized = name + str(input_data)
        return rough_token_estimate(serialized)

    if block_type == "tool_result":
        content = block.get("content")
        if isinstance(content, str):
            return rough_token_estimate(content)
        if isinstance(content, list):
            return sum(estimate_block_tokens(b) for b in content if isinstance(b, dict))
        return 0

    if block_type == "thinking":
        return rough_token_estimate(block.get("thinking", ""))

    if block_type == "redacted_thinking":
        return rough_token_estimate(block.get("data", ""))

    try:
        return rough_token_estimate(json.dumps(block, separators=(",", ":")))
    except TypeError, ValueError:
        return rough_token_estimate(str(block))


def estimate_message_tokens(message: dict[str, Any]) -> int:
    """Estimate token count for a single API message."""
    content = message.get("content")
    if content is None:
        return 0
    if isinstance(content, str):
        return rough_token_estimate(content)
    if isinstance(content, list):
        return sum(estimate_block_tokens(b) for b in content if isinstance(b, dict))
    return 0


def estimate_conversation_tokens(messages: list[dict[str, Any]]) -> int:
    """Estimate total token count for a conversation."""
    return sum(estimate_message_tokens(m) for m in messages)


def estimate_tools_tokens(tools: list[dict[str, Any]]) -> int:
    """Estimate token count for tool definitions."""
    try:
        serialized = json.dumps(tools, separators=(",", ":"))
    except TypeError, ValueError:
        serialized = str(tools)
    return rough_token_estimate(serialized)
