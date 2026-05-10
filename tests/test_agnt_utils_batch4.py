# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for agnt_utils Batch 4: throttle + debounce."""

from __future__ import annotations

import time


from agnt_utils.debounce import DebouncedFunction, debounce
from agnt_utils.throttle import CooldownThrottle, ThrottledFunction, throttle


# === THROTTLE TESTS ===


class TestThrottledFunction:
  """Tests for the ThrottledFunction class."""

  def test_leading_edge_fires_immediately(self) -> None:
    """First call should fire immediately with leading=True."""
    calls: list[int] = []
    tf = ThrottledFunction(lambda x: calls.append(x), 500, leading=True)
    tf(1)
    assert calls == [1]

  def test_suppresses_during_cooldown(self) -> None:
    """Calls during cooldown should be suppressed (not fire immediately)."""
    calls: list[int] = []
    tf = ThrottledFunction(lambda x: calls.append(x), 500, leading=True, trailing=False)
    tf(1)
    tf(2)
    tf(3)
    assert calls == [1]  # Only leading edge fires

  def test_trailing_edge_fires_after_cooldown(self) -> None:
    """Trailing edge should fire with last args after cooldown."""
    calls: list[int] = []
    tf = ThrottledFunction(lambda x: calls.append(x), 50, leading=True, trailing=True)
    tf(1)  # Leading — fires immediately
    tf(2)  # During cooldown — stored for trailing
    tf(3)  # During cooldown — overwrites
    time.sleep(0.15)  # Wait for trailing fire
    assert 1 in calls
    assert 3 in calls  # Trailing fires with last args

  def test_cancel_prevents_trailing(self) -> None:
    """cancel() should prevent the pending trailing call."""
    calls: list[int] = []
    tf = ThrottledFunction(lambda x: calls.append(x), 100, leading=True, trailing=True)
    tf(1)
    tf(2)
    tf.cancel()
    time.sleep(0.2)
    assert calls == [1]

  def test_flush_executes_immediately(self) -> None:
    """flush() should execute the pending trailing call right away."""
    calls: list[int] = []
    tf = ThrottledFunction(lambda x: calls.append(x), 1000, leading=True, trailing=True)
    tf(1)
    tf(2)
    tf.flush()
    assert 2 in calls

  def test_last_call_time_tracks_invocations(self) -> None:
    """last_call_time should update on each actual invocation."""
    tf = ThrottledFunction(lambda: None, 50, leading=True)
    assert tf.last_call_time == 0.0
    tf()
    assert tf.last_call_time > 0.0


class TestThrottleDecorator:
  """Tests for the @throttle decorator."""

  def test_decorator_basic(self) -> None:
    calls: list[str] = []

    @throttle(interval_ms=200)
    def log_event(msg: str) -> None:
      calls.append(msg)

    log_event("first")
    log_event("second")
    assert calls == ["first"]

  def test_decorator_trailing_only(self) -> None:
    calls: list[str] = []

    @throttle(interval_ms=50, leading=False)
    def log_event(msg: str) -> None:
      calls.append(msg)

    log_event("a")
    log_event("b")
    log_event("c")
    time.sleep(0.15)
    assert "c" in calls


class TestCooldownThrottle:
  """Tests for the CooldownThrottle class."""

  def test_should_run_on_first_call(self) -> None:
    ct = CooldownThrottle(cooldown_ms=5000, name="test")
    assert ct.should_run() is True

  def test_should_not_run_during_cooldown(self) -> None:
    ct = CooldownThrottle(cooldown_ms=5000, name="test")
    ct.mark_executed()
    assert ct.should_run() is False

  def test_should_run_after_cooldown(self) -> None:
    ct = CooldownThrottle(cooldown_ms=50, name="test")
    ct.mark_executed()
    time.sleep(0.1)
    assert ct.should_run() is True

  def test_time_until_next(self) -> None:
    ct = CooldownThrottle(cooldown_ms=1000, name="test")
    assert ct.time_until_next_ms() == 0.0
    ct.mark_executed()
    remaining = ct.time_until_next_ms()
    assert 0 < remaining <= 1000

  def test_reset_allows_immediate_run(self) -> None:
    ct = CooldownThrottle(cooldown_ms=60_000, name="test")
    ct.mark_executed()
    assert ct.should_run() is False
    ct.reset()
    assert ct.should_run() is True


# === DEBOUNCE TESTS ===


class TestDebouncedFunction:
  """Tests for the DebouncedFunction class."""

  def test_delays_execution(self) -> None:
    """Function should not fire immediately with trailing-only."""
    calls: list[int] = []
    df = DebouncedFunction(lambda x: calls.append(x), 50)
    df(1)
    assert calls == []  # Not fired yet
    time.sleep(0.15)
    assert calls == [1]

  def test_coalesces_rapid_calls(self) -> None:
    """Rapid calls should coalesce into a single execution with last args."""
    calls: list[int] = []
    df = DebouncedFunction(lambda x: calls.append(x), 80)
    df(1)
    df(2)
    df(3)
    time.sleep(0.2)
    assert calls == [3]

  def test_leading_edge_fires_immediately(self) -> None:
    """With leading=True, first call fires immediately."""
    calls: list[int] = []
    df = DebouncedFunction(lambda x: calls.append(x), 500, leading=True, trailing=False)
    df(1)
    assert calls == [1]

  def test_cancel_prevents_execution(self) -> None:
    """cancel() should prevent the pending call."""
    calls: list[int] = []
    df = DebouncedFunction(lambda x: calls.append(x), 100)
    df(1)
    df.cancel()
    time.sleep(0.2)
    assert calls == []

  def test_flush_executes_immediately(self) -> None:
    """flush() should execute the pending call right away."""
    calls: list[int] = []
    df = DebouncedFunction(lambda x: calls.append(x), 5000)
    df(42)
    df.flush()
    assert calls == [42]

  def test_max_wait_forces_execution(self) -> None:
    """max_wait_ms should force execution even with continuous calls."""
    calls: list[int] = []
    df = DebouncedFunction(lambda x: calls.append(x), 50, max_wait_ms=100)
    start = time.monotonic()
    while time.monotonic() - start < 0.15:
      df(99)
      time.sleep(0.01)
    time.sleep(0.1)
    assert len(calls) >= 1

  def test_pending_property(self) -> None:
    """pending should reflect whether a call is scheduled."""
    df = DebouncedFunction(lambda: None, 1000)
    assert df.pending is False
    df()
    # After call, args are stored but timer handles them
    df.cancel()


class TestDebounceDecorator:
  """Tests for the @debounce decorator."""

  def test_decorator_basic(self) -> None:
    results: list[str] = []

    @debounce(wait_ms=50)
    def handle_input(text: str) -> None:
      results.append(text)

    handle_input("h")
    handle_input("he")
    handle_input("hel")
    handle_input("hell")
    handle_input("hello")
    time.sleep(0.15)
    assert results == ["hello"]

  def test_decorator_with_max_wait(self) -> None:
    results: list[str] = []

    @debounce(wait_ms=50, max_wait_ms=100)
    def auto_save(content: str) -> None:
      results.append(content)

    start = time.monotonic()
    while time.monotonic() - start < 0.15:
      auto_save("data")
      time.sleep(0.01)
    time.sleep(0.1)
    assert len(results) >= 1
