# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for context_compactor.grouping — API-round message grouping."""

from __future__ import annotations


from context_compactor.grouping import group_messages_by_api_round


def _msg(role: str, msg_id: str = "", text: str = "hello") -> dict:
  """Build a minimal message dict for testing."""
  return {
    "type": role,
    "message": {"id": msg_id, "content": [{"type": "text", "text": text}]},
    "timestamp": 1000.0,
  }


class TestGroupMessagesByApiRound:
  """Test suite for group_messages_by_api_round."""

  def test_empty_messages(self) -> None:
    result = group_messages_by_api_round([])
    assert result == []

  def test_single_message(self) -> None:
    msgs = [_msg("user")]
    result = group_messages_by_api_round(msgs)
    assert len(result) == 1
    assert len(result[0]) == 1

  def test_single_round_trip(self) -> None:
    """User → Assistant → User (tool result) stays in one group."""
    msgs = [
      _msg("user"),
      _msg("assistant", msg_id="a1"),
      _msg("user"),  # tool result
    ]
    result = group_messages_by_api_round(msgs)
    # All share the same assistant ID scope → one group
    assert len(result) == 1
    assert len(result[0]) == 3

  def test_two_round_trips(self) -> None:
    """Two distinct assistant IDs produce two groups."""
    msgs = [
      _msg("user"),
      _msg("assistant", msg_id="a1"),
      _msg("user"),
      _msg("assistant", msg_id="a2"),
      _msg("user"),
    ]
    result = group_messages_by_api_round(msgs)
    assert len(result) == 2
    # First group: user + assistant(a1) + user
    assert len(result[0]) == 3
    # Second group: assistant(a2) + user
    assert len(result[1]) == 2

  def test_same_assistant_id_stays_grouped(self) -> None:
    """Multiple messages with same assistant ID remain in one group."""
    msgs = [
      _msg("user"),
      _msg("assistant", msg_id="a1"),
      _msg("user"),
      _msg("assistant", msg_id="a1"),  # streaming chunk — same ID
      _msg("user"),
    ]
    result = group_messages_by_api_round(msgs)
    # Same assistant ID → no boundary fires → one group
    assert len(result) == 1
    assert len(result[0]) == 5

  def test_three_rounds(self) -> None:
    msgs = [
      _msg("user"),
      _msg("assistant", msg_id="a1"),
      _msg("user"),
      _msg("assistant", msg_id="a2"),
      _msg("user"),
      _msg("assistant", msg_id="a3"),
    ]
    result = group_messages_by_api_round(msgs)
    assert len(result) == 3

  def test_no_assistant_messages(self) -> None:
    """All user messages → single group."""
    msgs = [_msg("user"), _msg("user"), _msg("user")]
    result = group_messages_by_api_round(msgs)
    assert len(result) == 1
    assert len(result[0]) == 3

  def test_assistant_only(self) -> None:
    """Multiple assistants with different IDs."""
    msgs = [
      _msg("assistant", msg_id="a1"),
      _msg("assistant", msg_id="a2"),
      _msg("assistant", msg_id="a3"),
    ]
    result = group_messages_by_api_round(msgs)
    assert len(result) == 3

  def test_no_message_id_assistant(self) -> None:
    """Assistants without IDs — boundary fires on empty→empty transition."""
    msgs = [
      _msg("user"),
      _msg("assistant"),
      _msg("user"),
      _msg("assistant"),
    ]
    result = group_messages_by_api_round(msgs)
    # Empty ID → empty ID: msg_id != last_assistant_id is False
    # So no boundary fires → one group
    assert len(result) == 1
