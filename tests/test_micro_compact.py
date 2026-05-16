# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for context_compactor.micro_compact — microcompaction engine."""

from __future__ import annotations

import time


from context_compactor.micro_compact import (
  COMPACTABLE_TOOLS,
  IMAGE_MAX_TOKEN_SIZE,
  TIME_BASED_MC_CLEARED_MESSAGE,
  TimeBasedMCConfig,
  calculate_tool_result_tokens,
  collect_compactable_tool_ids,
  estimate_message_tokens,
  evaluate_time_based_trigger,
  maybe_time_based_microcompact,
  microcompact_messages,
  set_time_based_mc_config,
)


# --- Fixtures ---


def _tool_use_block(name: str, tool_id: str) -> dict:
  """Build a tool_use content block."""
  return {"type": "tool_use", "id": tool_id, "name": name, "input": {}}


def _tool_result_block(tool_use_id: str, content: str = "result text") -> dict:
  """Build a tool_result content block."""
  return {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}


def _assistant_msg(blocks: list[dict], msg_id: str = "a1", ts: float = 0.0) -> dict:
  """Build an assistant message."""
  return {
    "type": "assistant",
    "message": {"id": msg_id, "content": blocks},
    "timestamp": ts or time.time(),
  }


def _user_msg(blocks: list[dict], ts: float = 0.0) -> dict:
  """Build a user message."""
  return {
    "type": "user",
    "message": {"content": blocks},
    "timestamp": ts or time.time(),
  }


# --- Tests: calculate_tool_result_tokens ---


class TestCalculateToolResultTokens:
  def test_none_content(self) -> None:
    assert calculate_tool_result_tokens({"content": None}) == 0

  def test_empty_block(self) -> None:
    assert calculate_tool_result_tokens({}) == 0

  def test_string_content(self) -> None:
    block = {"content": "hello world this is a test"}
    tokens = calculate_tool_result_tokens(block)
    assert tokens > 0

  def test_array_with_text(self) -> None:
    block = {
      "content": [
        {"type": "text", "text": "hello world"},
        {"type": "text", "text": "more text here"},
      ]
    }
    tokens = calculate_tool_result_tokens(block)
    assert tokens > 0

  def test_array_with_image(self) -> None:
    block = {
      "content": [
        {"type": "image", "source": {"data": "base64data"}},
      ]
    }
    tokens = calculate_tool_result_tokens(block)
    assert tokens == IMAGE_MAX_TOKEN_SIZE

  def test_mixed_content(self) -> None:
    block = {
      "content": [
        {"type": "text", "text": "some text"},
        {"type": "image", "source": {}},
        {"type": "document", "source": {}},
      ]
    }
    tokens = calculate_tool_result_tokens(block)
    # text tokens + 2 * IMAGE_MAX_TOKEN_SIZE
    assert tokens >= 2 * IMAGE_MAX_TOKEN_SIZE


# --- Tests: collect_compactable_tool_ids ---


class TestCollectCompactableToolIds:
  def test_empty(self) -> None:
    assert collect_compactable_tool_ids([]) == []

  def test_no_assistant_messages(self) -> None:
    msgs = [_user_msg([{"type": "text", "text": "hello"}])]
    assert collect_compactable_tool_ids(msgs) == []

  def test_compactable_tools(self) -> None:
    msgs = [
      _assistant_msg(
        [
          _tool_use_block("Read", "t1"),
          _tool_use_block("Bash", "t2"),
          _tool_use_block("Grep", "t3"),
        ]
      ),
    ]
    ids = collect_compactable_tool_ids(msgs)
    assert ids == ["t1", "t2", "t3"]

  def test_non_compactable_tool(self) -> None:
    msgs = [
      _assistant_msg(
        [
          _tool_use_block("CustomTool", "t1"),
        ]
      ),
    ]
    ids = collect_compactable_tool_ids(msgs)
    assert ids == []

  def test_mixed_compactable_and_not(self) -> None:
    msgs = [
      _assistant_msg(
        [
          _tool_use_block("Read", "t1"),
          _tool_use_block("CustomTool", "t2"),
          _tool_use_block("Bash", "t3"),
        ]
      ),
    ]
    ids = collect_compactable_tool_ids(msgs)
    assert ids == ["t1", "t3"]

  def test_extended_tool_names(self) -> None:
    """Extended lowercase tool names should also be compactable."""
    msgs = [
      _assistant_msg(
        [
          _tool_use_block("view_file", "t1"),
          _tool_use_block("run_command", "t2"),
          _tool_use_block("grep_search", "t3"),
        ]
      ),
    ]
    ids = collect_compactable_tool_ids(msgs)
    assert ids == ["t1", "t2", "t3"]


# --- Tests: estimate_message_tokens ---


class TestEstimateMessageTokens:
  def test_empty(self) -> None:
    assert estimate_message_tokens([]) == 0

  def test_text_message(self) -> None:
    msgs = [_user_msg([{"type": "text", "text": "hello world this is a test"}])]
    tokens = estimate_message_tokens(msgs)
    assert tokens > 0

  def test_padding_factor(self) -> None:
    """Estimate should be padded by ~4/3."""
    msgs = [_user_msg([{"type": "text", "text": "a " * 100}])]
    tokens = estimate_message_tokens(msgs)
    # "a " * 100 = 200 chars. rough_token_estimate → 200/4 = 50.
    # Padded by 4/3 → ceil(66.7) = 67. Must exceed raw 50.
    assert tokens > 50  # Padded estimate exceeds raw

  def test_system_messages_skipped(self) -> None:
    msgs = [
      {
        "type": "system",
        "message": {"content": [{"type": "text", "text": "system prompt"}]},
        "timestamp": 0,
      },
    ]
    assert estimate_message_tokens(msgs) == 0

  def test_tool_use_counted(self) -> None:
    msgs = [
      _assistant_msg(
        [
          {"type": "tool_use", "name": "Read", "id": "t1", "input": {"path": "/foo"}},
        ]
      ),
    ]
    tokens = estimate_message_tokens(msgs)
    assert tokens > 0


# --- Tests: evaluate_time_based_trigger ---


class TestEvaluateTimeBasedTrigger:
  def setup_method(self) -> None:
    """Reset config before each test."""
    set_time_based_mc_config(
      TimeBasedMCConfig(
        enabled=True,
        gap_threshold_minutes=60.0,
        keep_recent=5,
      )
    )

  def test_disabled(self) -> None:
    set_time_based_mc_config(TimeBasedMCConfig(enabled=False))
    msgs = [_assistant_msg([], ts=time.time() - 7200)]
    assert evaluate_time_based_trigger(msgs, "repl_main_thread") is None

  def test_no_query_source(self) -> None:
    msgs = [_assistant_msg([], ts=time.time() - 7200)]
    assert evaluate_time_based_trigger(msgs, None) is None

  def test_non_main_thread(self) -> None:
    msgs = [_assistant_msg([], ts=time.time() - 7200)]
    assert evaluate_time_based_trigger(msgs, "subagent_session_memory") is None

  def test_no_assistant_messages(self) -> None:
    msgs = [_user_msg([{"type": "text", "text": "hello"}])]
    assert evaluate_time_based_trigger(msgs, "repl_main_thread") is None

  def test_gap_under_threshold(self) -> None:
    # 30 minutes ago — under 60 min threshold
    msgs = [_assistant_msg([], ts=time.time() - 1800)]
    assert evaluate_time_based_trigger(msgs, "repl_main_thread") is None

  def test_gap_over_threshold(self) -> None:
    # 90 minutes ago — over 60 min threshold
    msgs = [_assistant_msg([], ts=time.time() - 5400)]
    result = evaluate_time_based_trigger(msgs, "repl_main_thread")
    assert result is not None
    gap_minutes, config = result
    assert gap_minutes >= 89  # Allow small timing variance
    assert config.gap_threshold_minutes == 60.0

  def test_output_style_variant(self) -> None:
    """repl_main_thread:outputStyle:custom should also trigger."""
    msgs = [_assistant_msg([], ts=time.time() - 5400)]
    result = evaluate_time_based_trigger(msgs, "repl_main_thread:outputStyle:custom")
    assert result is not None

  def test_main_source_alias(self) -> None:
    """'main' should trigger."""
    msgs = [_assistant_msg([], ts=time.time() - 5400)]
    result = evaluate_time_based_trigger(msgs, "main")
    assert result is not None


# --- Tests: maybe_time_based_microcompact ---


class TestMaybeTimeBasedMicrocompact:
  def setup_method(self) -> None:
    set_time_based_mc_config(
      TimeBasedMCConfig(
        enabled=True,
        gap_threshold_minutes=5.0,  # Low threshold for testing
        keep_recent=2,
      )
    )

  def test_no_trigger(self) -> None:
    """Recent assistant → no compaction."""
    msgs = [
      _assistant_msg([_tool_use_block("Read", "t1")], ts=time.time()),
      _user_msg([_tool_result_block("t1", "data")]),
    ]
    result = maybe_time_based_microcompact(msgs, "repl_main_thread")
    assert result is None

  def test_clears_old_results(self) -> None:
    """Stale assistant + multiple tool results → clears old ones."""
    old_ts = time.time() - 600  # 10 minutes ago

    msgs = [
      _assistant_msg(
        [
          _tool_use_block("Read", "t1"),
          _tool_use_block("Read", "t2"),
          _tool_use_block("Read", "t3"),
          _tool_use_block("Read", "t4"),
        ],
        ts=old_ts,
      ),
      _user_msg(
        [
          _tool_result_block("t1", "data1"),
          _tool_result_block("t2", "data2"),
          _tool_result_block("t3", "data3"),
          _tool_result_block("t4", "data4"),
        ]
      ),
    ]

    result = maybe_time_based_microcompact(msgs, "repl_main_thread")
    assert result is not None
    assert result.trigger_type == "time_based"
    assert result.tools_cleared == 2  # t1, t2 cleared
    assert result.tools_kept == 2  # t3, t4 kept (keep_recent=2)
    assert result.tokens_saved > 0

    # Verify original messages are unchanged
    user_content = msgs[1]["message"]["content"]
    assert user_content[0]["content"] == "data1"  # Not cleared

    # Verify result messages have cleared content
    result_user = result.messages[1]
    result_content = result_user["message"]["content"]
    assert result_content[0]["content"] == TIME_BASED_MC_CLEARED_MESSAGE
    assert result_content[1]["content"] == TIME_BASED_MC_CLEARED_MESSAGE
    assert result_content[2]["content"] == "data3"  # Kept
    assert result_content[3]["content"] == "data4"  # Kept

  def test_non_compactable_tool_not_cleared(self) -> None:
    """Only compactable tools are cleared."""
    old_ts = time.time() - 600

    msgs = [
      _assistant_msg(
        [
          _tool_use_block("CustomTool", "t1"),
        ],
        ts=old_ts,
      ),
      _user_msg(
        [
          _tool_result_block("t1", "important data"),
        ]
      ),
    ]

    result = maybe_time_based_microcompact(msgs, "repl_main_thread")
    assert result is None  # CustomTool not compactable → nothing to clear

  def test_already_cleared_not_double_cleared(self) -> None:
    """Results already cleared are not double-cleared."""
    old_ts = time.time() - 600

    msgs = [
      _assistant_msg(
        [
          _tool_use_block("Read", "t1"),
          _tool_use_block("Read", "t2"),
          _tool_use_block("Read", "t3"),
        ],
        ts=old_ts,
      ),
      _user_msg(
        [
          _tool_result_block("t1", TIME_BASED_MC_CLEARED_MESSAGE),  # Already cleared
          _tool_result_block("t2", "data2"),
          _tool_result_block("t3", "data3"),
        ]
      ),
    ]

    result = maybe_time_based_microcompact(msgs, "repl_main_thread")
    # t1 already cleared, so only t2 would be cleared (t3 kept)
    # But since keep_recent=2, keep_set = {t2, t3}, clear_set = {t1}
    # t1 is already cleared → tokens_saved = 0 → returns None
    # Actually: compactable IDs are t1,t2,t3. keep_recent=2 → keep t2,t3. clear t1.
    # t1 content IS TIME_BASED_MC_CLEARED_MESSAGE → skipped → tokens_saved=0 → None
    assert result is None

  def test_keep_recent_floor_at_1(self) -> None:
    """Even with keep_recent=0 in config, at least 1 is kept."""
    set_time_based_mc_config(
      TimeBasedMCConfig(
        enabled=True,
        gap_threshold_minutes=5.0,
        keep_recent=0,  # Would clear everything
      )
    )
    old_ts = time.time() - 600

    msgs = [
      _assistant_msg(
        [
          _tool_use_block("Read", "t1"),
          _tool_use_block("Read", "t2"),
        ],
        ts=old_ts,
      ),
      _user_msg(
        [
          _tool_result_block("t1", "data1"),
          _tool_result_block("t2", "data2"),
        ]
      ),
    ]

    result = maybe_time_based_microcompact(msgs, "repl_main_thread")
    assert result is not None
    assert result.tools_kept == 1  # Floored at 1
    assert result.tools_cleared == 1


# --- Tests: microcompact_messages ---


class TestMicrocompactMessages:
  def setup_method(self) -> None:
    set_time_based_mc_config(
      TimeBasedMCConfig(
        enabled=True,
        gap_threshold_minutes=5.0,
        keep_recent=2,
      )
    )

  def test_passthrough_when_no_trigger(self) -> None:
    msgs = [_user_msg([{"type": "text", "text": "hello"}])]
    result = microcompact_messages(msgs, "repl_main_thread")
    assert result.messages is msgs  # Same reference — not copied
    assert result.tokens_saved == 0

  def test_delegates_to_time_based(self) -> None:
    old_ts = time.time() - 600

    msgs = [
      _assistant_msg(
        [
          _tool_use_block("Read", "t1"),
          _tool_use_block("Read", "t2"),
          _tool_use_block("Read", "t3"),
        ],
        ts=old_ts,
      ),
      _user_msg(
        [
          _tool_result_block("t1", "data1"),
          _tool_result_block("t2", "data2"),
          _tool_result_block("t3", "data3"),
        ]
      ),
    ]

    result = microcompact_messages(msgs, "repl_main_thread")
    assert result.trigger_type == "time_based"
    assert result.tokens_saved > 0

  def test_no_query_source_passthrough(self) -> None:
    """Without query source, time-based trigger won't fire."""
    old_ts = time.time() - 600
    msgs = [
      _assistant_msg([_tool_use_block("Read", "t1")], ts=old_ts),
      _user_msg([_tool_result_block("t1", "data")]),
    ]
    result = microcompact_messages(msgs)
    assert result.tokens_saved == 0


# --- Tests: COMPACTABLE_TOOLS coverage ---


class TestCompactableTools:
  def test_core_tool_names(self) -> None:
    """All core tool names from microCompact.ts are present."""
    core_names = {
      "Read",
      "Bash",
      "Grep",
      "Glob",
      "WebSearch",
      "WebFetch",
      "Edit",
      "Write",
    }
    assert core_names.issubset(COMPACTABLE_TOOLS)

  def test_extended_tool_names(self) -> None:
    """Extended names for broader ecosystem compatibility."""
    extended = {"view_file", "run_command", "grep_search", "list_dir", "file_read"}
    assert extended.issubset(COMPACTABLE_TOOLS)

  def test_is_frozenset(self) -> None:
    """COMPACTABLE_TOOLS should be immutable."""
    assert isinstance(COMPACTABLE_TOOLS, frozenset)
