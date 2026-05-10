# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for packages/agnt_services/session_memory.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from packages.agnt_services.session_memory import (
  ExtractionState,
  SessionMemoryManager,
  count_tool_calls_since,
  should_extract_memory,
)


def _make_msgs(n_assistant=0, n_tool_use=0, start_uuid=1):
  msgs = []
  uid = start_uuid
  for i in range(n_assistant):
    content = []
    if i < n_tool_use:
      content.append({"type": "tool_use", "name": "bash"})
    msgs.append({"type": "assistant", "uuid": f"a-{uid}", "content": content})
    uid += 1
  return msgs


class TestCountToolCalls:
  def test_all_when_no_cursor(self):
    assert count_tool_calls_since(_make_msgs(3, 3), None) == 3

  def test_empty(self):
    assert count_tool_calls_since([], None) == 0


class TestShouldExtract:
  def test_below_init(self):
    s = ExtractionState()
    assert should_extract_memory(_make_msgs(5, 5), s, 5_000) is False

  def test_meets_init(self):
    s = ExtractionState()
    assert should_extract_memory(_make_msgs(5, 5), s, 10_000) is True


class TestExtractionState:
  def test_lifecycle(self):
    s = ExtractionState()
    assert not s.is_extracting
    s.mark_started()
    assert s.is_extracting
    s.mark_completed()
    assert not s.is_extracting

  def test_reset(self):
    s = ExtractionState()
    s.initialized = True
    s.reset()
    assert not s.initialized


class TestSessionMemoryManager:
  def test_should_extract(self):
    m = SessionMemoryManager()
    assert m.should_extract(_make_msgs(5, 5), 5_000) is False

  @pytest.mark.asyncio
  async def test_extract(self, tmp_path: Path):
    m = SessionMemoryManager(memory_dir=tmp_path)
    r = await m.extract(_make_msgs(3, 2), 15_000)
    assert r is True

  @pytest.mark.asyncio
  async def test_memory_read(self, tmp_path: Path):
    (tmp_path / "session_memory.md").write_text("notes")
    m = SessionMemoryManager(memory_dir=tmp_path)
    assert await m.get_memory_content() == "notes"
