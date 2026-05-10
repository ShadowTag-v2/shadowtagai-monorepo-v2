# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for ported agnt_services modules: prevent_sleep, xml_tags,
resilient_retry, circuit_breaker."""

from __future__ import annotations

import sys
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

# ── prevent_sleep tests ──

from packages.agnt_services.prevent_sleep import (
  force_stop_prevent_sleep,
  get_ref_count,
  start_prevent_sleep,
  stop_prevent_sleep,
)


class TestPreventSleep:
  """Tests for the prevent_sleep module."""

  def setup_method(self) -> None:
    force_stop_prevent_sleep()

  def teardown_method(self) -> None:
    force_stop_prevent_sleep()

  def test_ref_counting(self) -> None:
    """Reference count increments and decrements correctly."""
    assert get_ref_count() == 0
    start_prevent_sleep()
    assert get_ref_count() == 1
    start_prevent_sleep()
    assert get_ref_count() == 2
    stop_prevent_sleep()
    assert get_ref_count() == 1
    stop_prevent_sleep()
    assert get_ref_count() == 0

  def test_stop_below_zero(self) -> None:
    """Stop doesn't go below zero."""
    stop_prevent_sleep()
    assert get_ref_count() == 0

  def test_force_stop_resets(self) -> None:
    """Force stop resets ref count to zero."""
    start_prevent_sleep()
    start_prevent_sleep()
    assert get_ref_count() == 2
    force_stop_prevent_sleep()
    assert get_ref_count() == 0

  @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
  def test_caffeinate_spawns_on_macos(self) -> None:
    """On macOS, caffeinate process actually spawns."""
    from packages.agnt_services.prevent_sleep import is_active

    start_prevent_sleep()
    assert is_active()
    force_stop_prevent_sleep()
    # Give the process a moment to die
    time.sleep(0.1)

  @patch("packages.agnt_services.prevent_sleep.sys")
  def test_noop_on_non_darwin(self, mock_sys: MagicMock) -> None:
    """On non-macOS, spawn is a no-op."""
    mock_sys.platform = "linux"
    # Import fresh — the module uses sys.platform at call time
    from packages.agnt_services.prevent_sleep import _spawn_caffeinate

    # Should not raise
    _spawn_caffeinate()


# ── xml_tags tests ──

from packages.agnt_services.xml_tags import (
  ALL_TAGS,
  BASH_STDOUT_TAG,
  COMMAND_NAME_TAG,
  TERMINAL_OUTPUT_TAGS,
  escape_xml,
  escape_xml_attr,
  is_terminal_output_tag,
  wrap_tag,
)


class TestXmlTags:
  """Tests for XML tag constants and utilities."""

  def test_tag_constants_are_strings(self) -> None:
    assert isinstance(COMMAND_NAME_TAG, str)
    assert COMMAND_NAME_TAG == "command-name"

  def test_terminal_output_tags_tuple(self) -> None:
    assert len(TERMINAL_OUTPUT_TAGS) == 6
    assert BASH_STDOUT_TAG in TERMINAL_OUTPUT_TAGS

  def test_all_tags_frozenset(self) -> None:
    assert isinstance(ALL_TAGS, frozenset)
    assert len(ALL_TAGS) >= 25  # At least 25 unique tags
    assert COMMAND_NAME_TAG in ALL_TAGS

  def test_escape_xml_basic(self) -> None:
    assert escape_xml("hello") == "hello"
    assert escape_xml("<script>") == "&lt;script&gt;"
    assert escape_xml("a & b") == "a &amp; b"

  def test_escape_xml_all_chars(self) -> None:
    assert escape_xml("<a>&b</a>") == "&lt;a&gt;&amp;b&lt;/a&gt;"

  def test_escape_xml_attr(self) -> None:
    assert escape_xml_attr('value="test"') == "value=&quot;test&quot;"
    assert escape_xml_attr("it's") == "it&apos;s"

  def test_escape_xml_attr_includes_base_escapes(self) -> None:
    result = escape_xml_attr('<a & "b">')
    assert "&lt;" in result
    assert "&amp;" in result
    assert "&quot;" in result
    assert "&gt;" in result

  def test_wrap_tag(self) -> None:
    result = wrap_tag("bash-stdout", "hello <world>")
    assert result == "<bash-stdout>hello &lt;world&gt;</bash-stdout>"

  def test_wrap_tag_no_escape(self) -> None:
    result = wrap_tag("raw", "<b>bold</b>", escape=False)
    assert result == "<raw><b>bold</b></raw>"

  def test_is_terminal_output_tag(self) -> None:
    assert is_terminal_output_tag("bash-stdout") is True
    assert is_terminal_output_tag("bash-stderr") is True
    assert is_terminal_output_tag("command-name") is False
    assert is_terminal_output_tag("unknown") is False

  def test_escape_empty_string(self) -> None:
    assert escape_xml("") == ""
    assert escape_xml_attr("") == ""


# ── resilient_retry tests ──

from packages.agnt_services.resilient_retry import (
  BASE_DELAY_MS,
  CannotRetryError,
  FallbackTriggeredError,
  RetryConfig,
  RetryOutcome,
  get_retry_delay,
  is_529_error,
  is_retryable_status,
  with_retry,
  with_retry_sync,
)


class TestRetryDelay:
  """Tests for get_retry_delay calculation."""

  def test_first_attempt_base_delay(self) -> None:
    delay = get_retry_delay(1)
    # BASE_DELAY_MS + up to 25% jitter
    assert BASE_DELAY_MS <= delay <= BASE_DELAY_MS * 1.25

  def test_exponential_growth(self) -> None:
    d1 = get_retry_delay(1, max_delay_ms=100_000)
    d3 = get_retry_delay(3, max_delay_ms=100_000)
    # Attempt 3 base is 4x attempt 1 base (2^2)
    assert d3 > d1

  def test_max_delay_cap(self) -> None:
    delay = get_retry_delay(20, max_delay_ms=5000)
    assert delay <= 5000 * 1.25  # Base capped + jitter

  def test_retry_after_header(self) -> None:
    delay = get_retry_delay(1, retry_after_header="10")
    assert delay == 10_000  # 10 seconds in ms

  def test_invalid_retry_after_falls_back(self) -> None:
    delay = get_retry_delay(1, retry_after_header="invalid")
    assert delay >= BASE_DELAY_MS


class TestRetryableStatus:
  def test_retryable_codes(self) -> None:
    for code in (408, 409, 429, 500, 502, 503, 529):
      assert is_retryable_status(code), f"{code} should be retryable"

  def test_non_retryable_codes(self) -> None:
    for code in (200, 400, 401, 403, 404):
      assert not is_retryable_status(code), f"{code} should NOT be retryable"


class TestIs529Error:
  def test_status_code(self) -> None:
    assert is_529_error(529) is True

  def test_message_sniffing(self) -> None:
    assert is_529_error(None, '"type":"overloaded_error"') is True

  def test_not_529(self) -> None:
    assert is_529_error(500) is False
    assert is_529_error(None, "some other error") is False


class TestWithRetrySync:
  def test_success_first_try(self) -> None:
    result, stats = with_retry_sync(lambda: 42, RetryConfig(max_retries=3))
    assert result == 42
    assert stats.total_attempts == 1
    assert stats.outcome == RetryOutcome.SUCCESS

  def test_retry_on_failure(self) -> None:
    call_count = 0

    def flaky():
      nonlocal call_count
      call_count += 1
      if call_count < 3:
        exc = Exception("transient")
        exc.status = 500  # type: ignore[attr-defined]
        raise exc
      return "ok"

    result, stats = with_retry_sync(flaky, RetryConfig(max_retries=5, max_delay_ms=10))
    assert result == "ok"
    assert stats.total_attempts == 3

  def test_exhausted_retries(self) -> None:
    def always_fail():
      exc = Exception("fail")
      exc.status = 500  # type: ignore[attr-defined]
      raise exc

    with pytest.raises(CannotRetryError):
      with_retry_sync(always_fail, RetryConfig(max_retries=2, max_delay_ms=10))

  def test_non_retryable_error(self) -> None:
    def bad_request():
      exc = Exception("bad request")
      exc.status = 400  # type: ignore[attr-defined]
      raise exc

    with pytest.raises(CannotRetryError) as exc_info:
      with_retry_sync(bad_request, RetryConfig(max_retries=5, max_delay_ms=10))
    assert exc_info.value.attempts == 1

  def test_fallback_on_529s(self) -> None:
    def overloaded():
      exc = Exception("overloaded")
      exc.status = 529  # type: ignore[attr-defined]
      raise exc

    with pytest.raises(FallbackTriggeredError):
      with_retry_sync(
        overloaded,
        RetryConfig(
          max_retries=10,
          max_529_retries=2,
          fallback_model="fallback-model",
          max_delay_ms=10,
        ),
      )


class TestWithRetryAsync:
  @pytest.mark.asyncio
  async def test_async_success(self) -> None:
    async def op():
      return "async_ok"

    result, stats = await with_retry(op, RetryConfig(max_retries=3))
    assert result == "async_ok"
    assert stats.outcome == RetryOutcome.SUCCESS

  @pytest.mark.asyncio
  async def test_async_retry(self) -> None:
    call_count = 0

    async def flaky():
      nonlocal call_count
      call_count += 1
      if call_count < 2:
        exc = Exception("transient")
        exc.status = 503  # type: ignore[attr-defined]
        raise exc
      return "recovered"

    result, stats = await with_retry(flaky, RetryConfig(max_retries=5, max_delay_ms=10))
    assert result == "recovered"
    assert stats.total_attempts == 2


# ── circuit_breaker tests ──

from packages.agnt_services.circuit_breaker import (
  CircuitBreaker,
  CircuitBreakerConfig,
  CircuitOpenError,
  CircuitState,
  get_breaker,
  reset_all,
)


class TestCircuitBreaker:
  def test_initial_state_closed(self) -> None:
    cb = CircuitBreaker("test-cb")
    assert cb.state == CircuitState.CLOSED

  def test_success_stays_closed(self) -> None:
    cb = CircuitBreaker("test-success")
    result = cb.call(lambda: 42)
    assert result == 42
    assert cb.state == CircuitState.CLOSED

  def test_failures_trip_open(self) -> None:
    cb = CircuitBreaker(
      "test-trip",
      CircuitBreakerConfig(failure_threshold=3),
    )
    for _ in range(3):
      with pytest.raises(ValueError):
        cb.call(lambda: (_ for _ in ()).throw(ValueError("boom")))

    assert cb.state == CircuitState.OPEN

  def test_open_circuit_fast_fails(self) -> None:
    cb = CircuitBreaker(
      "test-fast-fail",
      CircuitBreakerConfig(failure_threshold=2, timeout_seconds=60),
    )
    for _ in range(2):
      with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("err")))

    with pytest.raises(CircuitOpenError) as exc_info:
      cb.call(lambda: "should not execute")

    assert exc_info.value.circuit_name == "test-fast-fail"
    assert exc_info.value.retry_after_seconds > 0

  def test_open_transitions_to_half_open(self) -> None:
    cb = CircuitBreaker(
      "test-half-open",
      CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.1),
    )
    for _ in range(2):
      with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("err")))

    assert cb.state == CircuitState.OPEN
    time.sleep(0.15)  # Wait for timeout
    assert cb.state == CircuitState.HALF_OPEN

  def test_half_open_success_closes(self) -> None:
    cb = CircuitBreaker(
      "test-close",
      CircuitBreakerConfig(
        failure_threshold=2,
        success_threshold=2,
        timeout_seconds=0.05,
      ),
    )
    # Trip it
    for _ in range(2):
      with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("err")))

    time.sleep(0.1)  # Wait for HALF_OPEN

    # Successful probes should close
    cb.call(lambda: "ok")
    cb.call(lambda: "ok")
    assert cb.state == CircuitState.CLOSED

  def test_half_open_failure_reopens(self) -> None:
    cb = CircuitBreaker(
      "test-reopen",
      CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.05),
    )
    for _ in range(2):
      with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("err")))

    time.sleep(0.1)
    assert cb.state == CircuitState.HALF_OPEN

    with pytest.raises(RuntimeError):
      cb.call(lambda: (_ for _ in ()).throw(RuntimeError("fail again")))

    assert cb.state == CircuitState.OPEN

  def test_manual_reset(self) -> None:
    cb = CircuitBreaker(
      "test-reset",
      CircuitBreakerConfig(failure_threshold=2),
    )
    for _ in range(2):
      with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError("err")))

    assert cb.state == CircuitState.OPEN
    cb.reset()
    assert cb.state == CircuitState.CLOSED

  def test_stats(self) -> None:
    cb = CircuitBreaker("test-stats")
    cb.call(lambda: "ok")
    stats = cb.stats()
    assert stats.state == CircuitState.CLOSED
    assert stats.success_count == 1
    assert stats.total_calls == 1

  def test_registry_singleton(self) -> None:
    reset_all()
    cb1 = get_breaker("singleton-test")
    cb2 = get_breaker("singleton-test")
    assert cb1 is cb2

  def test_thread_safety(self) -> None:
    cb = CircuitBreaker(
      "test-threads",
      CircuitBreakerConfig(failure_threshold=100),
    )
    errors: list[Exception] = []

    def worker():
      try:
        for _ in range(50):
          cb.call(lambda: "ok")
      except Exception as e:
        errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
      t.start()
    for t in threads:
      t.join()

    assert not errors
    assert cb.stats().total_calls == 200


# ── Registry integration ──


class TestRegistryIntegration:
  """Verify the 4 new modules load via the service registry."""

  def test_new_services_load(self) -> None:
    from packages.agnt_services import health_check

    result = health_check()
    details = result["details"]

    for svc in ("prevent_sleep", "xml_tags", "resilient_retry", "circuit_breaker"):
      assert details.get(svc) == "ready", (
        f"Service '{svc}' should be ready, got: {details.get(svc)}"
      )

  def test_registry_count_increased(self) -> None:
    from packages.agnt_services import health_check

    result = health_check()
    ready = result["ready"]
    # Was 10, now should be at least 14
    assert ready >= 14, f"Expected >=14 ready services, got {ready}"
