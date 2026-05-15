# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for packages/agnt_services/agent_summary.py — AgentSummarizer."""

from __future__ import annotations

import asyncio

import pytest

from packages.agnt_services.agent_summary import (
  AgentSummarizer,
  SummaryState,
  build_summary_prompt,
  SUMMARY_INTERVAL_S,
  MIN_TRANSCRIPT_LENGTH,
)


# ---------------------------------------------------------------------------
# Unit tests for build_summary_prompt
# ---------------------------------------------------------------------------
class TestBuildSummaryPrompt:
  def test_without_previous(self):
    prompt = build_summary_prompt()
    assert "3-5 words" in prompt
    assert "Previous:" not in prompt

  def test_with_previous(self):
    prompt = build_summary_prompt("Reading utils.py")
    assert "Previous:" in prompt
    assert "Reading utils.py" in prompt
    assert "say something NEW" in prompt


# ---------------------------------------------------------------------------
# Unit tests for SummaryState
# ---------------------------------------------------------------------------
class TestSummaryState:
  def test_defaults(self):
    state = SummaryState(task_id="t1", agent_id="a1")
    assert state.task_id == "t1"
    assert state.agent_id == "a1"
    assert state.previous_summary is None
    assert state.summary_count == 0
    assert state.is_stopped is False

  def test_stop_flag(self):
    state = SummaryState(task_id="t1", agent_id="a1")
    state.is_stopped = True
    assert state.is_stopped is True


# ---------------------------------------------------------------------------
# Integration tests for AgentSummarizer
# ---------------------------------------------------------------------------
class TestAgentSummarizer:
  @pytest.mark.asyncio
  async def test_start_and_stop(self):
    """Start creates an asyncio task, stop cancels it."""
    summarizer = AgentSummarizer(interval=0.05)
    handle = summarizer.start("task-1", "agent-1")
    assert summarizer.active_count == 1
    assert not handle.is_stopped

    summarizer.stop("task-1")
    assert handle.is_stopped
    # Allow the cancelled task to clean up
    await asyncio.sleep(0.1)

  @pytest.mark.asyncio
  async def test_stop_all(self):
    """stop_all cancels every active loop."""
    summarizer = AgentSummarizer(interval=0.05)
    summarizer.start("t1", "a1")
    summarizer.start("t2", "a2")
    assert summarizer.active_count == 2

    summarizer.stop_all()
    assert summarizer.active_count == 0
    await asyncio.sleep(0.1)

  @pytest.mark.asyncio
  async def test_callback_fires(self):
    """on_summary callback is invoked after a cycle."""
    summaries: list[tuple[str, str]] = []

    def on_summary(tid: str, text: str):
      summaries.append((tid, text))

    def get_transcript(aid: str):
      # Return a list long enough to pass MIN_TRANSCRIPT_LENGTH
      return {"messages": [{"role": "user"}] * (MIN_TRANSCRIPT_LENGTH + 1)}

    summarizer = AgentSummarizer(
      on_summary=on_summary,
      get_transcript=get_transcript,
      interval=0.05,
    )
    summarizer.start("t1", "a1")
    await asyncio.sleep(0.2)  # Wait for at least 1 cycle
    summarizer.stop_all()
    await asyncio.sleep(0.1)

    assert len(summaries) >= 1
    assert summaries[0][0] == "t1"

  @pytest.mark.asyncio
  async def test_get_latest_summary(self):
    """get_latest_summary returns the most recent text."""
    summarizer = AgentSummarizer(
      get_transcript=lambda _: {"messages": [{}] * 5},
      interval=0.05,
    )
    summarizer.start("t1", "a1")
    await asyncio.sleep(0.15)
    summarizer.stop_all()
    await asyncio.sleep(0.1)

    result = summarizer.get_latest_summary("t1")
    assert result is not None

  @pytest.mark.asyncio
  async def test_skips_short_transcript(self):
    """No summary produced if transcript is too short."""
    summaries: list[tuple[str, str]] = []

    def on_summary(tid: str, text: str):
      summaries.append((tid, text))

    def get_transcript(aid: str):
      return {"messages": [{"role": "user"}]}  # Only 1 message

    summarizer = AgentSummarizer(
      on_summary=on_summary,
      get_transcript=get_transcript,
      interval=0.05,
    )
    summarizer.start("t1", "a1")
    await asyncio.sleep(0.15)
    summarizer.stop_all()
    await asyncio.sleep(0.1)

    assert len(summaries) == 0

  @pytest.mark.asyncio
  async def test_no_transcript_provider(self):
    """Gracefully handles missing transcript provider."""
    summarizer = AgentSummarizer(interval=0.05)
    summarizer.start("t1", "a1")
    await asyncio.sleep(0.15)
    summarizer.stop_all()
    await asyncio.sleep(0.1)
    assert summarizer.get_latest_summary("t1") is None

  def test_get_latest_unknown_task(self):
    """Returns None for unknown task IDs."""
    summarizer = AgentSummarizer()
    assert summarizer.get_latest_summary("nonexistent") is None

  def test_constants(self):
    """Constants match upstream defaults."""
    assert SUMMARY_INTERVAL_S == 30.0
    assert MIN_TRANSCRIPT_LENGTH == 3
