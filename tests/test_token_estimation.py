# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Test suite for the Token Estimation package (CP-13).

Validates rough token estimation parity with Claude Code v2.1.91
services/tokenEstimation.ts, covering string estimation, file-type-aware
ratios, content block handling, and message-level aggregation.
"""

from __future__ import annotations


import pytest

from packages.token_estimation.estimator import (
  DEFAULT_BYTES_PER_TOKEN,
  IMAGE_MAX_TOKEN_SIZE,
  bytes_per_token_for_file_type,
  rough_token_estimate,
  rough_token_estimate_for_block,
  rough_token_estimate_for_content,
  rough_token_estimate_for_file_type,
  rough_token_estimate_for_messages,
)


# ── Core estimation ──────────────────────────────────────────────────────


class TestRoughTokenEstimate:
  """Basic string-to-token estimation."""

  def test_empty_string(self) -> None:
    assert rough_token_estimate("") == 0

  def test_short_string(self) -> None:
    result = rough_token_estimate("Hello")
    assert result >= 1
    # "Hello" is 5 chars / 4 bytes-per-token = 1.25 → round(1.25) = 1
    assert result == 1

  def test_longer_string(self) -> None:
    text = "a" * 100
    assert rough_token_estimate(text) == 25  # 100 / 4

  def test_custom_bytes_per_token(self) -> None:
    text = "a" * 100
    assert rough_token_estimate(text, bytes_per_token=2) == 50

  def test_minimum_one_token(self) -> None:
    """Non-empty content should return at least 1 token."""
    assert rough_token_estimate("x") == 1

  def test_exact_division(self) -> None:
    text = "a" * 400
    assert rough_token_estimate(text) == 100  # 400 / 4


# ── File-type aware estimation ───────────────────────────────────────────


class TestBytesPerTokenForFileType:
  """File type ratio parity with TS switch statement."""

  @pytest.mark.parametrize("ext", ["json", "jsonl", "jsonc"])
  def test_json_extensions_use_2(self, ext: str) -> None:
    assert bytes_per_token_for_file_type(ext) == 2

  @pytest.mark.parametrize("ext", ["py", "ts", "md", "txt", "rs", "go", ""])
  def test_other_extensions_use_default(self, ext: str) -> None:
    assert bytes_per_token_for_file_type(ext) == DEFAULT_BYTES_PER_TOKEN

  def test_file_type_estimate(self) -> None:
    text = "a" * 100
    # JSON: 100/2 = 50; Python: 100/4 = 25
    assert rough_token_estimate_for_file_type(text, "json") == 50
    assert rough_token_estimate_for_file_type(text, "py") == 25


# ── Block-level estimation ───────────────────────────────────────────────


class TestRoughTokenEstimateForBlock:
  """Content block estimation matching TS roughTokenCountEstimationForBlock."""

  def test_string_block(self) -> None:
    result = rough_token_estimate_for_block("Hello world test string")
    assert result == rough_token_estimate("Hello world test string")

  def test_text_block(self) -> None:
    block = {"type": "text", "text": "a" * 100}
    assert rough_token_estimate_for_block(block) == 25

  def test_image_block(self) -> None:
    block = {"type": "image", "source": {"data": "base64..."}}
    assert rough_token_estimate_for_block(block) == IMAGE_MAX_TOKEN_SIZE

  def test_document_block(self) -> None:
    block = {"type": "document", "source": {"data": "base64..."}}
    assert rough_token_estimate_for_block(block) == IMAGE_MAX_TOKEN_SIZE

  def test_tool_result_string(self) -> None:
    block = {"type": "tool_result", "content": "a" * 200}
    assert rough_token_estimate_for_block(block) == 50  # 200 / 4

  def test_tool_result_blocks(self) -> None:
    block = {
      "type": "tool_result",
      "content": [
        {"type": "text", "text": "a" * 40},  # 10 tokens
        {"type": "text", "text": "b" * 80},  # 20 tokens
      ],
    }
    assert rough_token_estimate_for_block(block) == 30

  def test_tool_result_none(self) -> None:
    block = {"type": "tool_result", "content": None}
    assert rough_token_estimate_for_block(block) == 0

  def test_tool_use_block(self) -> None:
    block = {
      "type": "tool_use",
      "name": "read_file",
      "input": {"path": "/tmp/test.py"},
    }
    result = rough_token_estimate_for_block(block)
    assert result > 0

  def test_thinking_block(self) -> None:
    block = {"type": "thinking", "thinking": "a" * 400}
    assert rough_token_estimate_for_block(block) == 100

  def test_redacted_thinking_block(self) -> None:
    block = {"type": "redacted_thinking", "data": "b" * 200}
    assert rough_token_estimate_for_block(block) == 50

  def test_unknown_block_falls_through(self) -> None:
    block = {
      "type": "web_search_result",
      "url": "https://example.com",
      "text": "result",
    }
    result = rough_token_estimate_for_block(block)
    assert result > 0


# ── Content-level estimation ─────────────────────────────────────────────


class TestRoughTokenEstimateForContent:
  def test_none_content(self) -> None:
    assert rough_token_estimate_for_content(None) == 0

  def test_string_content(self) -> None:
    assert rough_token_estimate_for_content("a" * 40) == 10

  def test_block_list_content(self) -> None:
    content = [
      {"type": "text", "text": "a" * 40},
      {"type": "text", "text": "b" * 40},
    ]
    assert rough_token_estimate_for_content(content) == 20


# ── Message-level estimation ────────────────────────────────────────────


class TestRoughTokenEstimateForMessages:
  def test_empty_messages(self) -> None:
    assert rough_token_estimate_for_messages([]) == 0

  def test_user_message(self) -> None:
    messages = [
      {"type": "user", "message": {"content": "a" * 100}},
    ]
    assert rough_token_estimate_for_messages(messages) == 25

  def test_assistant_message(self) -> None:
    messages = [
      {"type": "assistant", "message": {"content": "a" * 200}},
    ]
    assert rough_token_estimate_for_messages(messages) == 50

  def test_mixed_messages(self) -> None:
    messages = [
      {"type": "user", "message": {"content": "a" * 100}},  # 25
      {"type": "assistant", "message": {"content": "b" * 200}},  # 50
    ]
    assert rough_token_estimate_for_messages(messages) == 75

  def test_attachment_message(self) -> None:
    messages = [
      {"type": "attachment", "attachment": {"content": "a" * 80}},
    ]
    assert rough_token_estimate_for_messages(messages) == 20

  def test_unknown_message_type(self) -> None:
    messages = [{"type": "system", "content": "ignored"}]
    assert rough_token_estimate_for_messages(messages) == 0

  def test_message_with_block_content(self) -> None:
    messages = [
      {
        "type": "assistant",
        "message": {
          "content": [
            {"type": "text", "text": "a" * 40},
            {"type": "text", "text": "b" * 40},
          ],
        },
      },
    ]
    assert rough_token_estimate_for_messages(messages) == 20
