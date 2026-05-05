# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for session_memory_compact — API invariant preservation.

Tests focus on the critical safety functions:
  - adjust_index_to_preserve_api_invariants (tool pair + thinking block)
  - calculate_messages_to_keep_index (min/max thresholds, boundary floor)
  - try_session_memory_compact (orchestrator integration)
"""

from __future__ import annotations

import pytest

from context_compactor.session_memory_compact import (
    SessionMemoryCompactConfig,
    adjust_index_to_preserve_api_invariants,
    calculate_messages_to_keep_index,
    has_text_blocks,
    reset_session_memory_compact_config,
    set_session_memory_compact_config,
    try_session_memory_compact,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────


def _user_msg(content: str = "hello") -> dict:
    return {"role": "user", "content": content}


def _assistant_msg(
    content: str = "world",
    *,
    message_id: str | None = None,
) -> dict:
    msg: dict = {"role": "assistant", "content": content}
    if message_id:
        msg["message_id"] = message_id
    return msg


def _tool_use_msg(tool_use_id: str, *, message_id: str | None = None) -> dict:
    msg: dict = {
        "role": "assistant",
        "content": [{"type": "tool_use", "id": tool_use_id, "name": "bash", "input": {}}],
    }
    if message_id:
        msg["message_id"] = message_id
    return msg


def _tool_result_msg(*tool_use_ids: str) -> dict:
    return {
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": tid, "content": "ok"} for tid in tool_use_ids],
    }


def _thinking_msg(message_id: str) -> dict:
    return {
        "role": "assistant",
        "content": [{"type": "thinking", "thinking": "hmm..."}],
        "message_id": message_id,
    }


def _boundary_msg() -> dict:
    return {"role": "user", "content": "boundary", "compact_boundary": True}


def _big_msg(approx_tokens: int = 5000) -> dict:
    """Create a message with roughly `approx_tokens` worth of content."""
    # ~4 chars per token is a rough estimate
    return {"role": "assistant", "content": "word " * approx_tokens}


# ── has_text_blocks ────────────────────────────────────────────────────────────


class TestHasTextBlocks:
    def test_user_string_content(self) -> None:
        assert has_text_blocks(_user_msg("hello")) is True

    def test_user_empty_string(self) -> None:
        assert has_text_blocks(_user_msg("")) is False

    def test_assistant_text_block(self) -> None:
        msg = {"role": "assistant", "content": [{"type": "text", "text": "hi"}]}
        assert has_text_blocks(msg) is True

    def test_assistant_tool_use_only(self) -> None:
        assert has_text_blocks(_tool_use_msg("t1")) is False

    def test_user_tool_result_only(self) -> None:
        assert has_text_blocks(_tool_result_msg("t1")) is False


# ── adjust_index_to_preserve_api_invariants ────────────────────────────────────


class TestAdjustIndex:
    def test_no_adjustment_needed(self) -> None:
        messages = [_user_msg(), _assistant_msg(), _user_msg()]
        assert adjust_index_to_preserve_api_invariants(messages, 1) == 1

    def test_boundary_indices(self) -> None:
        messages = [_user_msg(), _assistant_msg()]
        assert adjust_index_to_preserve_api_invariants(messages, 0) == 0
        assert adjust_index_to_preserve_api_invariants(messages, 2) == 2

    def test_tool_pair_basic(self) -> None:
        """Start index that would orphan a tool_result must be adjusted."""
        messages = [
            _user_msg(),  # 0
            _tool_use_msg("t1"),  # 1 - tool_use
            _tool_result_msg("t1"),  # 2 - tool_result
            _user_msg(),  # 3
        ]
        # Start at 2 would include tool_result but not tool_use
        assert adjust_index_to_preserve_api_invariants(messages, 2) == 1

    def test_tool_pair_already_in_range(self) -> None:
        """If tool_use is already in kept range, no adjustment."""
        messages = [
            _user_msg(),
            _tool_use_msg("t1"),
            _tool_result_msg("t1"),
            _user_msg(),
        ]
        assert adjust_index_to_preserve_api_invariants(messages, 1) == 1

    def test_multiple_tool_pairs(self) -> None:
        """Multiple orphan tool_results → adjust to include all uses."""
        messages = [
            _user_msg(),  # 0
            _tool_use_msg("t1"),  # 1
            _tool_use_msg("t2"),  # 2
            _tool_result_msg("t1", "t2"),  # 3
            _user_msg(),  # 4
        ]
        # Start at 3 needs both t1 and t2 tool_uses
        assert adjust_index_to_preserve_api_invariants(messages, 3) == 1

    def test_thinking_block_same_message_id(self) -> None:
        """Thinking blocks sharing message_id must be kept together."""
        messages = [
            _user_msg(),  # 0
            _thinking_msg("msg-1"),  # 1 - thinking
            _tool_use_msg("t1", message_id="msg-1"),  # 2 - tool_use, same id
            _tool_result_msg("t1"),  # 3
            _user_msg(),  # 4
        ]
        # Start at 2: has tool_use, but msg-1 thinking at index 1 shares message_id
        # Tool result at 3 also needs tool_use at 2, but 2 is already in range.
        # Thinking at 1 shares message_id with 2 → adjust to 1
        assert adjust_index_to_preserve_api_invariants(messages, 2) == 1

    def test_upstream_bug_scenario(self) -> None:
        """Reproduces the exact upstream bug scenario from the docstring."""
        messages = [
            _user_msg(),  # 0
            {"role": "assistant", "content": [{"type": "thinking", "thinking": "..."}], "message_id": "X"},  # 1
            {"role": "assistant", "content": [{"type": "tool_use", "id": "ORPHAN", "name": "bash", "input": {}}], "message_id": "X"},  # 2
            {"role": "assistant", "content": [{"type": "tool_use", "id": "VALID", "name": "bash", "input": {}}], "message_id": "X"},  # 3
            {
                "role": "user",
                "content": [  # 4
                    {"type": "tool_result", "tool_use_id": "ORPHAN", "content": "ok"},
                    {"type": "tool_result", "tool_use_id": "VALID", "content": "ok"},
                ],
            },
        ]
        # Start at 3 should expand to 1 (thinking at 1 shares message_id X)
        result = adjust_index_to_preserve_api_invariants(messages, 3)
        assert result == 1


# ── calculate_messages_to_keep_index ───────────────────────────────────────────


class TestCalculateMessagesToKeepIndex:
    @pytest.fixture(autouse=True)
    def _reset_config(self) -> None:
        reset_session_memory_compact_config()
        yield
        reset_session_memory_compact_config()

    def test_empty_messages(self) -> None:
        assert calculate_messages_to_keep_index([], -1) == 0

    def test_all_after_last_summarized(self) -> None:
        """With huge messages after summary, keep from last_summarized + 1."""
        # Set low thresholds so minimums are easily met
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=10,
                min_text_block_messages=1,
                max_tokens=100_000,
            )
        )
        messages = [
            _user_msg(),  # 0 - summarized
            _big_msg(200),  # 1
            _user_msg(),  # 2
        ]
        result = calculate_messages_to_keep_index(messages, 0)
        assert result == 1

    def test_expands_backwards_for_min_tokens(self) -> None:
        """Expands backwards when min_tokens not met."""
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=50_000,
                min_text_block_messages=1,
                max_tokens=200_000,
            )
        )
        messages = [
            _big_msg(20000),  # 0
            _big_msg(20000),  # 1
            _big_msg(20000),  # 2 - last summarized
            _user_msg("small"),  # 3 - only ~1 token
        ]
        result = calculate_messages_to_keep_index(messages, 2)
        # Should expand backwards from 3 to include more tokens
        assert result < 3

    def test_stops_at_max_tokens(self) -> None:
        """Stops expanding once max_tokens reached."""
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=1,
                min_text_block_messages=1,
                max_tokens=100,
            )
        )
        messages = [
            _big_msg(5000),  # 0
            _big_msg(5000),  # 1
            _user_msg(),  # 2 - last summarized
            _big_msg(5000),  # 3 - already over max_tokens
        ]
        result = calculate_messages_to_keep_index(messages, 2)
        # Should not expand backwards since we're already over max
        assert result == 3

    def test_respects_boundary_floor(self) -> None:
        """Does not expand past the last compact boundary."""
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=100_000,
                min_text_block_messages=1,
                max_tokens=500_000,
            )
        )
        messages = [
            _big_msg(10000),  # 0
            _boundary_msg(),  # 1 - boundary
            _big_msg(10000),  # 2
            _user_msg(),  # 3 - last summarized
            _user_msg("x"),  # 4
        ]
        result = calculate_messages_to_keep_index(messages, 3)
        # Floor is 2 (boundary at 1 + 1), shouldn't go below 2
        assert result >= 2

    def test_no_summarized_index(self) -> None:
        """When last_summarized is -1, starts from end (no messages kept)."""
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=1,
                min_text_block_messages=1,
                max_tokens=100,
            )
        )
        messages = [_user_msg(), _assistant_msg()]
        result = calculate_messages_to_keep_index(messages, -1)
        # Should expand backwards from len(messages) to meet minimums
        assert result <= len(messages)


# ── try_session_memory_compact ─────────────────────────────────────────────────


class TestTrySessionMemoryCompact:
    @pytest.fixture(autouse=True)
    def _reset_config(self) -> None:
        reset_session_memory_compact_config()
        yield
        reset_session_memory_compact_config()

    def test_no_session_memory(self) -> None:
        result = try_session_memory_compact([_user_msg()])
        assert result is None

    def test_empty_session_memory(self) -> None:
        result = try_session_memory_compact(
            [_user_msg()],
            session_memory_content="   ",
        )
        assert result is None

    def test_missing_summarized_id(self) -> None:
        result = try_session_memory_compact(
            [_user_msg()],
            session_memory_content="session summary here",
            last_summarized_message_id="nonexistent-uuid",
        )
        assert result is None

    def test_basic_sm_compact(self) -> None:
        messages = [
            {**_user_msg(), "uuid": "msg-1"},
            {**_assistant_msg(), "uuid": "msg-2"},
            {**_user_msg(), "uuid": "msg-3"},
        ]
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=1,
                min_text_block_messages=1,
                max_tokens=100_000,
            )
        )
        result = try_session_memory_compact(
            messages,
            session_memory_content="Summary of conversation so far",
            last_summarized_message_id="msg-1",
        )
        assert result is not None
        assert result.success is True
        assert result.messages_kept is not None
        assert result.method == "session_memory"

    def test_threshold_guard(self) -> None:
        """SM compact should bail if post-compact tokens exceed threshold."""
        messages = [
            {**_big_msg(50000), "uuid": "msg-1"},
            {**_big_msg(50000), "uuid": "msg-2"},
        ]
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=1,
                min_text_block_messages=1,
                max_tokens=500_000,
            )
        )
        result = try_session_memory_compact(
            messages,
            session_memory_content="Summary",
            last_summarized_message_id="msg-1",
            auto_compact_threshold=100,  # Very low threshold
        )
        assert result is None  # Should bail due to threshold

    def test_resumed_session(self) -> None:
        """Resumed session (no summarized ID) should still work."""
        messages = [
            {**_user_msg(), "uuid": "msg-1"},
            {**_assistant_msg(), "uuid": "msg-2"},
        ]
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=1,
                min_text_block_messages=1,
                max_tokens=100_000,
            )
        )
        result = try_session_memory_compact(
            messages,
            session_memory_content="Resumed session memory content",
        )
        assert result is not None
        assert result.success is True

    def test_filters_compact_boundaries(self) -> None:
        """Compact boundary messages should be filtered from kept messages."""
        messages = [
            {**_user_msg(), "uuid": "msg-1"},
            {**_boundary_msg(), "uuid": "msg-2"},
            {**_user_msg(), "uuid": "msg-3"},
        ]
        set_session_memory_compact_config(
            SessionMemoryCompactConfig(
                min_tokens=1,
                min_text_block_messages=1,
                max_tokens=100_000,
            )
        )
        result = try_session_memory_compact(
            messages,
            session_memory_content="Summary",
            last_summarized_message_id="msg-1",
        )
        assert result is not None
        assert result.success is True
        # The boundary message should be filtered out
        for msg in result.messages_kept:
            assert not msg.get("compact_boundary", False)
