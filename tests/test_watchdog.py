# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for packages/agnt_services/watchdog.py — StreamingWatchdog."""

from __future__ import annotations

import asyncio

import pytest

from packages.agnt_services.watchdog import StreamingWatchdog, WatchdogStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _fast_stream(chunks: list[str], delay: float = 0.0):
  """Yields chunks with an optional inter-chunk delay."""
  for c in chunks:
    if delay:
      await asyncio.sleep(delay)
    yield c


async def _stalling_stream(chunks: list[str], stall_at: int, stall_for: float):
  """Yields chunks, stalling at a specific index."""
  for i, c in enumerate(chunks):
    if i == stall_at:
      await asyncio.sleep(stall_for)
    yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
class TestStreamingWatchdog:
  """Unit tests for StreamingWatchdog."""

  @pytest.mark.asyncio
  async def test_basic_passthrough(self):
    """Chunks are yielded unchanged."""
    wd = StreamingWatchdog()
    chunks = ["a", "b", "c"]
    result = [c async for c in wd.watch(_fast_stream(chunks), timeout=10.0)]
    assert result == chunks

  @pytest.mark.asyncio
  async def test_stats_tracking(self):
    """Stats are accumulated correctly."""
    wd = StreamingWatchdog()
    chunks = ["x", "y", "z"]
    _ = [c async for c in wd.watch(_fast_stream(chunks), timeout=10.0)]
    assert wd.stats.chunks_yielded == 3
    assert wd.stats.timed_out is False
    assert wd.stats.total_elapsed > 0

  @pytest.mark.asyncio
  async def test_timeout_raises(self):
    """TimeoutError raised when stream exceeds total timeout."""
    wd = StreamingWatchdog()
    with pytest.raises(TimeoutError, match="total timeout"):
      _ = [
        c
        async for c in wd.watch(
          _fast_stream(["a", "b", "c"], delay=0.2),
          timeout=0.1,
        )
      ]
    assert wd.stats.timed_out is True

  @pytest.mark.asyncio
  async def test_stall_callback_fires(self):
    """Stall callback is invoked when gap exceeds threshold."""
    stall_gaps: list[float] = []

    def on_stall(gap: float):
      stall_gaps.append(gap)

    wd = StreamingWatchdog(on_stall=on_stall)
    _ = [
      c
      async for c in wd.watch(
        _stalling_stream(["a", "b", "c"], stall_at=1, stall_for=0.2),
        timeout=10.0,
        stall_threshold=0.1,
      )
    ]
    assert len(stall_gaps) >= 1
    assert stall_gaps[0] >= 0.1

  @pytest.mark.asyncio
  async def test_timeout_callback_fires(self):
    """Timeout callback is invoked on expiry."""
    elapsed_values: list[float] = []

    def on_timeout(elapsed: float):
      elapsed_values.append(elapsed)

    wd = StreamingWatchdog(on_timeout=on_timeout)
    with pytest.raises(TimeoutError):
      _ = [
        c
        async for c in wd.watch(
          _fast_stream(["a", "b", "c"], delay=0.2),
          timeout=0.1,
        )
      ]
    assert len(elapsed_values) == 1

  @pytest.mark.asyncio
  async def test_empty_stream(self):
    """Empty stream yields nothing, stats are clean."""
    wd = StreamingWatchdog()
    result = [c async for c in wd.watch(_fast_stream([]), timeout=10.0)]
    assert result == []
    assert wd.stats.chunks_yielded == 0

  @pytest.mark.asyncio
  async def test_stats_max_gap(self):
    """Max gap is tracked correctly."""
    wd = StreamingWatchdog()
    _ = [
      c
      async for c in wd.watch(
        _stalling_stream(["a", "b", "c"], stall_at=1, stall_for=0.15),
        timeout=10.0,
        stall_threshold=10.0,  # High threshold so no callback
      )
    ]
    assert wd.stats.max_gap >= 0.1

  @pytest.mark.asyncio
  async def test_callback_exception_suppressed(self):
    """Exceptions in callbacks are caught, not propagated."""

    def bad_stall(gap: float):
      raise ValueError("bad callback")

    wd = StreamingWatchdog(on_stall=bad_stall)
    result = [
      c
      async for c in wd.watch(
        _stalling_stream(["a", "b"], stall_at=0, stall_for=0.2),
        timeout=10.0,
        stall_threshold=0.1,
      )
    ]
    assert len(result) == 2  # All chunks still yielded


class TestWatchdogStats:
  """Unit tests for WatchdogStats dataclass."""

  def test_defaults(self):
    s = WatchdogStats()
    assert s.chunks_yielded == 0
    assert s.total_elapsed == 0.0
    assert s.max_gap == 0.0
    assert s.stall_count == 0
    assert s.timed_out is False

  def test_slots(self):
    s = WatchdogStats()
    with pytest.raises(AttributeError):
      s.nonexistent = True  # type: ignore[attr-defined]
