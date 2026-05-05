# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for packages/token_budget/estimation.py.

Validates the vendor-agnostic token estimation logic ported from
Claude Code v2.1.91 tokenEstimation.ts.
"""

from __future__ import annotations


from token_budget.estimation import (
    IMAGE_MAX_TOKEN_SIZE,
    THINKING_BUDGET_TOKENS,
    TOKEN_COUNT_MAX_TOKENS,
    bytes_per_token_for_file_type,
    rough_token_count,
    rough_token_count_for_block,
    rough_token_count_for_content,
    rough_token_count_for_file,
    rough_token_count_for_messages,
)


# ── Constants ──


class TestConstants:
    """Verify ported constants match source values."""

    def test_image_max_token_size(self) -> None:
        assert IMAGE_MAX_TOKEN_SIZE == 2000

    def test_thinking_budget_tokens(self) -> None:
        assert THINKING_BUDGET_TOKENS == 1024

    def test_token_count_max_tokens(self) -> None:
        assert TOKEN_COUNT_MAX_TOKENS == 2048


# ── rough_token_count ──


class TestRoughTokenCount:
    """Core character-ratio estimation."""

    def test_empty_string(self) -> None:
        assert rough_token_count("") == 0

    def test_short_text(self) -> None:
        # "Hello" = 5 chars, 5/4 = 1.25 → ceil = 2
        assert rough_token_count("Hello") == 2

    def test_exact_divisor(self) -> None:
        # 8 chars / 4 = exactly 2
        assert rough_token_count("abcdefgh") == 2

    def test_custom_bytes_per_token(self) -> None:
        # 8 chars / 2 = 4
        assert rough_token_count("abcdefgh", bytes_per_token=2) == 4

    def test_large_text(self) -> None:
        text = "x" * 10000
        result = rough_token_count(text)
        assert result == 2500  # 10000 / 4

    def test_unicode(self) -> None:
        # Python len() counts codepoints, not bytes
        text = "こんにちは"  # 5 chars
        assert rough_token_count(text) == 2

    def test_always_non_negative(self) -> None:
        assert rough_token_count("") >= 0
        assert rough_token_count("a") >= 0


# ── bytes_per_token_for_file_type ──


class TestBytesPerTokenForFileType:
    """File-type-specific ratio lookup."""

    def test_json_files(self) -> None:
        assert bytes_per_token_for_file_type("json") == 2

    def test_jsonl_files(self) -> None:
        assert bytes_per_token_for_file_type("jsonl") == 2

    def test_jsonc_files(self) -> None:
        assert bytes_per_token_for_file_type("jsonc") == 2

    def test_python_default(self) -> None:
        assert bytes_per_token_for_file_type("py") == 4

    def test_typescript_default(self) -> None:
        assert bytes_per_token_for_file_type("ts") == 4

    def test_case_insensitive(self) -> None:
        assert bytes_per_token_for_file_type("JSON") == 2
        assert bytes_per_token_for_file_type("Json") == 2

    def test_dot_prefix_stripped(self) -> None:
        assert bytes_per_token_for_file_type(".json") == 2
        assert bytes_per_token_for_file_type(".py") == 4


# ── rough_token_count_for_file ──


class TestRoughTokenCountForFile:
    """Combined file-type-aware estimation."""

    def test_json_file_higher_count(self) -> None:
        content = '{"key": "value"}'  # 16 chars
        json_count = rough_token_count_for_file(content, "json")
        py_count = rough_token_count_for_file(content, "py")
        # json should produce higher count (more tokens per byte)
        assert json_count > py_count

    def test_empty_content(self) -> None:
        assert rough_token_count_for_file("", "json") == 0


# ── rough_token_count_for_block ──


class TestRoughTokenCountForBlock:
    """Content block estimation."""

    def test_string_block(self) -> None:
        assert rough_token_count_for_block("Hello world") > 0

    def test_text_block(self) -> None:
        block = {"type": "text", "text": "Hello world"}
        assert rough_token_count_for_block(block) > 0

    def test_image_block_fixed(self) -> None:
        block = {"type": "image", "source": {"data": "base64..."}}
        assert rough_token_count_for_block(block) == IMAGE_MAX_TOKEN_SIZE

    def test_document_block_fixed(self) -> None:
        block = {"type": "document", "source": {"data": "pdf_base64..."}}
        assert rough_token_count_for_block(block) == IMAGE_MAX_TOKEN_SIZE

    def test_gemini_inline_data(self) -> None:
        block = {"type": "inlineData", "data": "base64..."}
        assert rough_token_count_for_block(block) == IMAGE_MAX_TOKEN_SIZE

    def test_tool_use_block(self) -> None:
        block = {
            "type": "tool_use",
            "name": "edit_file",
            "input": {"path": "/foo/bar.py", "content": "print('hello')"},
        }
        result = rough_token_count_for_block(block)
        assert result > 0
        # Should count name + serialized input
        assert result > rough_token_count("edit_file")

    def test_gemini_function_call(self) -> None:
        block = {
            "type": "functionCall",
            "functionCall": {
                "name": "get_weather",
                "args": {"city": "London"},
            },
        }
        assert rough_token_count_for_block(block) > 0

    def test_tool_result_block(self) -> None:
        block = {
            "type": "tool_result",
            "content": "File saved successfully",
        }
        assert rough_token_count_for_block(block) > 0

    def test_thinking_block(self) -> None:
        block = {"type": "thinking", "thinking": "Let me consider..."}
        assert rough_token_count_for_block(block) > 0

    def test_redacted_thinking_block(self) -> None:
        block = {"type": "redacted_thinking", "data": "abc123"}
        assert rough_token_count_for_block(block) > 0

    def test_unknown_block_fallback(self) -> None:
        block = {"type": "custom_widget", "payload": {"data": "test"}}
        result = rough_token_count_for_block(block)
        assert result > 0  # Falls back to JSON stringify


# ── rough_token_count_for_content ──


class TestRoughTokenCountForContent:
    """Content-level estimation (string, list, dict, None)."""

    def test_none_content(self) -> None:
        assert rough_token_count_for_content(None) == 0

    def test_string_content(self) -> None:
        assert rough_token_count_for_content("Hello world") > 0

    def test_list_content(self) -> None:
        content = [
            {"type": "text", "text": "Part 1"},
            {"type": "text", "text": "Part 2"},
        ]
        result = rough_token_count_for_content(content)
        assert result > rough_token_count("Part 1")

    def test_dict_content(self) -> None:
        content = {"type": "text", "text": "Single block"}
        assert rough_token_count_for_content(content) > 0


# ── rough_token_count_for_messages ──


class TestRoughTokenCountForMessages:
    """Message-level estimation."""

    def test_empty_messages(self) -> None:
        assert rough_token_count_for_messages([]) == 0

    def test_anthropic_format(self) -> None:
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        result = rough_token_count_for_messages(messages)
        # At least message overhead (4 per msg) + content tokens
        assert result >= 8

    def test_gemini_format(self) -> None:
        messages = [
            {"role": "user", "parts": [{"text": "Hello"}]},
            {"role": "model", "parts": [{"text": "Hi there"}]},
        ]
        result = rough_token_count_for_messages(messages)
        assert result >= 8

    def test_message_overhead_counted(self) -> None:
        # Even empty-content messages should have overhead
        messages = [{"role": "system", "content": ""}]
        result = rough_token_count_for_messages(messages)
        assert result >= 4

    def test_mixed_content_messages(self) -> None:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Look at this image"},
                    {"type": "image", "source": {"data": "base64..."}},
                ],
            },
        ]
        result = rough_token_count_for_messages(messages)
        # Should include image constant + text tokens + overhead
        assert result >= IMAGE_MAX_TOKEN_SIZE + 4
