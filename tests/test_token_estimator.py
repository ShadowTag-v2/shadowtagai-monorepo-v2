# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for packages/tool_gateway/token_estimator.py."""

from __future__ import annotations

import pytest

from tool_gateway.token_estimator import (
    bytes_per_token_for_file_type,
    estimate_block_tokens,
    estimate_conversation_tokens,
    estimate_message_tokens,
    rough_token_estimate,
    rough_token_estimate_for_file,
)


class TestRoughTokenEstimate:
    """Tests for rough_token_estimate."""

    def test_empty_string(self) -> None:
        assert rough_token_estimate("") == 0

    def test_basic_text(self) -> None:
        text = "a" * 100
        assert rough_token_estimate(text) == 25  # 100 / 4

    def test_custom_ratio(self) -> None:
        text = "a" * 100
        assert rough_token_estimate(text, 2) == 50  # 100 / 2


class TestBytesPerTokenForFileType:
    """Tests for bytes_per_token_for_file_type."""

    def test_json(self) -> None:
        assert bytes_per_token_for_file_type("json") == 2

    def test_jsonl(self) -> None:
        assert bytes_per_token_for_file_type("jsonl") == 2

    def test_python(self) -> None:
        assert bytes_per_token_for_file_type("py") == 4

    def test_unknown(self) -> None:
        assert bytes_per_token_for_file_type("xyz") == 4


class TestRoughTokenEstimateForFile:
    """Tests for rough_token_estimate_for_file."""

    def test_json_file(self) -> None:
        content = "a" * 100
        assert rough_token_estimate_for_file(content, "json") == 50

    def test_python_file(self) -> None:
        content = "a" * 100
        assert rough_token_estimate_for_file(content, "py") == 25


class TestEstimateBlockTokens:
    """Tests for estimate_block_tokens."""

    def test_text_block(self) -> None:
        block = {"type": "text", "text": "a" * 40}
        assert estimate_block_tokens(block) == 10

    def test_image_block(self) -> None:
        block = {"type": "image", "source": {"data": "base64..."}}
        assert estimate_block_tokens(block) == 2000

    def test_document_block(self) -> None:
        block = {"type": "document", "source": {"data": "base64..."}}
        assert estimate_block_tokens(block) == 2000

    def test_tool_use_block(self) -> None:
        block = {"type": "tool_use", "name": "grep", "input": {"query": "test"}}
        tokens = estimate_block_tokens(block)
        assert tokens > 0

    def test_tool_result_string(self) -> None:
        block = {"type": "tool_result", "content": "a" * 40}
        assert estimate_block_tokens(block) == 10

    def test_thinking_block(self) -> None:
        block = {"type": "thinking", "thinking": "a" * 80}
        assert estimate_block_tokens(block) == 20

    def test_unknown_block(self) -> None:
        block = {"type": "custom_block", "data": "something"}
        tokens = estimate_block_tokens(block)
        assert tokens > 0


class TestEstimateMessageTokens:
    """Tests for estimate_message_tokens."""

    def test_string_content(self) -> None:
        msg = {"role": "user", "content": "a" * 40}
        assert estimate_message_tokens(msg) == 10

    def test_block_content(self) -> None:
        msg = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "a" * 40},
                {"type": "text", "text": "b" * 40},
            ],
        }
        assert estimate_message_tokens(msg) == 20

    def test_none_content(self) -> None:
        msg = {"role": "user", "content": None}
        assert estimate_message_tokens(msg) == 0


class TestEstimateConversationTokens:
    """Tests for estimate_conversation_tokens."""

    def test_multi_message(self) -> None:
        messages = [
            {"role": "user", "content": "a" * 40},
            {"role": "assistant", "content": "b" * 40},
        ]
        assert estimate_conversation_tokens(messages) == 20
