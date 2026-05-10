# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for typed inter-daemon messaging module.

Validates the ECC2 comms/mod.rs port: send, parse, preview,
priority extraction, truncation, and message lifecycle.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

import importlib
import sys

# packages/aiyou-core has a hyphen — not a valid Python identifier.
# Import via importlib to handle this.
_messaging_path = Path(__file__).parent.parent / "packages" / "aiyou-core"
sys.path.insert(0, str(_messaging_path))
_mod = importlib.import_module("messaging")
sys.path.pop(0)

Completed = _mod.Completed
Conflict = _mod.Conflict
DaemonMessage = _mod.DaemonMessage
MessageType = _mod.MessageType
Query = _mod.Query
Response = _mod.Response
TaskHandoff = _mod.TaskHandoff
TaskPriority = _mod.TaskPriority
cleanup_old_messages = _mod.cleanup_old_messages
handoff_priority = _mod.handoff_priority
list_messages = _mod.list_messages
parse = _mod.parse
preview = _mod.preview
send = _mod.send
truncate = _mod.truncate


@pytest.fixture
def msg_dir(tmp_path: Path) -> Path:
  """Temp directory for message persistence."""
  d = tmp_path / "messages"
  d.mkdir()
  return d


# --- TestSend ---


class TestSend:
  """Tests for send() — message serialization and dispatch."""

  def test_send_returns_id(self, msg_dir: Path) -> None:
    """send() should return a non-empty message ID."""
    msg = TaskHandoff(task="Run tests", context="CI pipeline")
    msg_id = send("kairos", "dream", msg, msg_dir=msg_dir)
    assert len(msg_id) > 0

  def test_send_creates_file(self, msg_dir: Path) -> None:
    """send() should persist the message as a JSON file."""
    msg = Query(question="What is the current task?")
    send("loop", "kairos", msg, msg_dir=msg_dir)
    files = list(msg_dir.glob("*.json"))
    assert len(files) == 1

  def test_send_rejects_oversized(self, msg_dir: Path) -> None:
    """send() should reject payloads exceeding MAX_MESSAGE_SIZE."""
    msg = TaskHandoff(task="x" * 70000, context="overflow")
    with pytest.raises(ValueError, match="exceeds"):
      send("kairos", "dream", msg, msg_dir=msg_dir)


# --- TestParse ---


class TestParse:
  """Tests for parse() — safe deserialization."""

  def test_parse_task_handoff(self) -> None:
    """parse() should deserialize TaskHandoff JSON."""
    data = '{"task": "Deploy", "context": "staging", "priority": "high"}'
    result = parse(data)
    assert isinstance(result, TaskHandoff)
    assert result.priority == TaskPriority.HIGH

  def test_parse_query(self) -> None:
    """parse() should deserialize Query JSON."""
    result = parse('{"question": "Status?"}')
    assert isinstance(result, Query)

  def test_parse_completed(self) -> None:
    """parse() should deserialize Completed JSON."""
    data = '{"summary": "Done", "files_changed": ["a.py", "b.py"]}'
    result = parse(data)
    assert isinstance(result, Completed)
    assert len(result.files_changed) == 2

  def test_parse_conflict(self) -> None:
    """parse() should deserialize Conflict JSON."""
    data = '{"file": "main.py", "description": "Concurrent edit"}'
    result = parse(data)
    assert isinstance(result, Conflict)

  def test_parse_invalid_json(self) -> None:
    """parse() should return None for invalid JSON."""
    assert parse("not json") is None

  def test_parse_none_input(self) -> None:
    """parse() should return None for None input."""
    assert parse(None) is None  # type: ignore[arg-type]

  def test_parse_empty_object(self) -> None:
    """parse() should return None for empty JSON object."""
    assert parse("{}") is None


# --- TestPreview ---


class TestPreview:
  """Tests for preview() — human-readable summaries."""

  def _make_envelope(self, msg_type: MessageType, payload: str) -> DaemonMessage:
    return DaemonMessage(
      from_daemon="kairos",
      to_daemon="dream",
      msg_type=msg_type,
      payload=payload,
    )

  def test_preview_handoff_normal(self) -> None:
    """preview() should format TaskHandoff without priority label."""
    envelope = self._make_envelope(
      MessageType.TASK_HANDOFF,
      TaskHandoff(task="Run lint").model_dump_json(),
    )
    result = preview(envelope)
    assert result.startswith("handoff ")
    assert "Run lint" in result

  def test_preview_handoff_critical(self) -> None:
    """preview() should show priority label for non-normal."""
    envelope = self._make_envelope(
      MessageType.TASK_HANDOFF,
      TaskHandoff(
        task="Emergency fix", priority=TaskPriority.CRITICAL
      ).model_dump_json(),
    )
    result = preview(envelope)
    assert "[critical]" in result

  def test_preview_query(self) -> None:
    """preview() should format Query."""
    envelope = self._make_envelope(
      MessageType.QUERY,
      Query(question="What task?").model_dump_json(),
    )
    assert preview(envelope).startswith("query ")

  def test_preview_completed_with_files(self) -> None:
    """preview() should show file count."""
    envelope = self._make_envelope(
      MessageType.COMPLETED,
      Completed(summary="Done", files_changed=["a.py", "b.py"]).model_dump_json(),
    )
    result = preview(envelope)
    assert "2 files" in result

  def test_preview_conflict(self) -> None:
    """preview() should show file and description."""
    envelope = self._make_envelope(
      MessageType.CONFLICT,
      Conflict(file="main.py", description="Both editing").model_dump_json(),
    )
    result = preview(envelope)
    assert "conflict" in result
    assert "main.py" in result


# --- TestPriority ---


class TestPriority:
  """Tests for handoff_priority() — priority extraction."""

  def _make_envelope(self, payload: str) -> DaemonMessage:
    return DaemonMessage(
      from_daemon="a",
      to_daemon="b",
      msg_type=MessageType.TASK_HANDOFF,
      payload=payload,
    )

  def test_normal_priority(self) -> None:
    """Default priority should be NORMAL."""
    envelope = self._make_envelope(TaskHandoff(task="x").model_dump_json())
    assert handoff_priority(envelope) == TaskPriority.NORMAL

  def test_critical_priority(self) -> None:
    """Explicit critical priority should be returned."""
    envelope = self._make_envelope(
      TaskHandoff(task="x", priority=TaskPriority.CRITICAL).model_dump_json()
    )
    assert handoff_priority(envelope) == TaskPriority.CRITICAL

  def test_legacy_json_fallback(self) -> None:
    """Legacy untyped JSON should extract priority."""
    envelope = self._make_envelope('{"priority": "high", "other": "data"}')
    assert handoff_priority(envelope) == TaskPriority.HIGH


# --- TestTruncate ---


class TestTruncate:
  """Tests for truncate() — Unicode-safe string truncation."""

  def test_short_string(self) -> None:
    """Short strings should not be truncated."""
    assert truncate("hello", 10) == "hello"

  def test_long_string(self) -> None:
    """Long strings should be truncated with ellipsis."""
    result = truncate("a" * 100, 10)
    assert len(result) == 10
    assert result.endswith("…")

  def test_unicode_string(self) -> None:
    """Unicode strings should truncate correctly."""
    result = truncate("日本語テスト文字列です", 5)
    assert len(result) == 5
    assert result.endswith("…")


# --- TestLifecycle ---


class TestLifecycle:
  """Tests for message list and cleanup lifecycle."""

  def test_list_messages_empty(self, msg_dir: Path) -> None:
    """list_messages() should return empty for new directory."""
    result = list_messages(msg_dir)
    assert result == []

  def test_list_messages_after_send(self, msg_dir: Path) -> None:
    """list_messages() should return sent messages."""
    send("kairos", "dream", TaskHandoff(task="test"), msg_dir=msg_dir)
    result = list_messages(msg_dir)
    assert len(result) == 1
    assert result[0].from_daemon == "kairos"

  def test_cleanup_old_messages(self, msg_dir: Path) -> None:
    """cleanup_old_messages() should remove expired messages."""
    # Create a message with old timestamp
    old_msg = DaemonMessage(
      from_daemon="old",
      to_daemon="old",
      msg_type=MessageType.QUERY,
      payload='{"question": "stale"}',
      timestamp=time.time() - (8 * 86400),  # 8 days ago
    )
    filepath = msg_dir / "old_message.json"
    filepath.write_text(old_msg.model_dump_json(indent=2))

    removed = cleanup_old_messages(msg_dir, max_age_days=7)
    assert removed == 1
