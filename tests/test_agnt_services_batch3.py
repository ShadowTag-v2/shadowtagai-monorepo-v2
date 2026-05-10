# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for AGNT Services Batch 3 — diagnostic_tracking, notifier,
away_summary, rate_limit_messages.
"""

from __future__ import annotations

import pytest

# ── diagnostic_tracking tests ────────────────────────────────────────────

from packages.agnt_services.diagnostic_tracking import (
  Diagnostic,
  DiagnosticFile,
  DiagnosticRange,
  DiagnosticSeverity,
  DiagnosticTrackingService,
  _normalize_uri,
)


class _FakeProvider:
  """Fake DiagnosticProvider for testing."""

  def __init__(self) -> None:
    self._diagnostics: dict[str | None, list[DiagnosticFile]] = {}

  def set_diagnostics(self, key: str | None, files: list[DiagnosticFile]) -> None:
    self._diagnostics[key] = files

  async def get_diagnostics(self, file_uri: str | None = None) -> list[DiagnosticFile]:
    return self._diagnostics.get(file_uri, self._diagnostics.get(None, []))

  async def open_file(self, file_uri: str) -> None:
    pass


def _make_diag(
  msg: str = "error",
  severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
  line: int = 0,
  char: int = 0,
  code: str | None = None,
) -> Diagnostic:
  return Diagnostic(
    message=msg,
    severity=severity,
    range=DiagnosticRange(line, char, line, char + 1),
    code=code,
  )


class TestDiagnosticTracking:
  def setup_method(self) -> None:
    DiagnosticTrackingService.reset_instance()
    self.svc = DiagnosticTrackingService.get_instance()

  def test_singleton(self) -> None:
    assert DiagnosticTrackingService.get_instance() is self.svc

  def test_not_initialized(self) -> None:
    assert not self.svc.is_initialized

  @pytest.mark.asyncio
  async def test_baseline_capture(self) -> None:
    provider = _FakeProvider()
    diag = _make_diag("existing error")
    provider.set_diagnostics(
      "file:///test.py",
      [DiagnosticFile(uri="file:///test.py", diagnostics=[diag])],
    )
    self.svc.initialize(provider)
    await self.svc.before_file_edited("/test.py")
    assert self.svc.is_initialized

  @pytest.mark.asyncio
  async def test_new_diagnostics_detected(self) -> None:
    provider = _FakeProvider()
    existing = _make_diag("existing")
    new_one = _make_diag("new error", line=5)

    # Baseline: only existing
    provider.set_diagnostics(
      "file:///test.py",
      [DiagnosticFile(uri="file:///test.py", diagnostics=[existing])],
    )
    self.svc.initialize(provider)
    await self.svc.before_file_edited("/test.py")

    # After edit: both existing + new
    provider.set_diagnostics(
      None,
      [DiagnosticFile(uri="file:///test.py", diagnostics=[existing, new_one])],
    )
    results = await self.svc.get_new_diagnostics()
    assert len(results) == 1
    assert results[0].diagnostics[0].message == "new error"

  @pytest.mark.asyncio
  async def test_no_new_diagnostics(self) -> None:
    provider = _FakeProvider()
    existing = _make_diag("existing")
    provider.set_diagnostics(
      "file:///test.py",
      [DiagnosticFile(uri="file:///test.py", diagnostics=[existing])],
    )
    self.svc.initialize(provider)
    await self.svc.before_file_edited("/test.py")

    provider.set_diagnostics(
      None,
      [DiagnosticFile(uri="file:///test.py", diagnostics=[existing])],
    )
    results = await self.svc.get_new_diagnostics()
    assert len(results) == 0

  def test_reset_clears_state(self) -> None:
    self.svc.initialize(_FakeProvider())
    self.svc.reset()
    assert self.svc.is_initialized  # Still initialized

  def test_shutdown(self) -> None:
    self.svc.initialize(_FakeProvider())
    self.svc.shutdown()
    assert not self.svc.is_initialized


class TestDiagnosticFormatting:
  def test_format_summary(self) -> None:
    diag = _make_diag("undefined variable", code="F821")
    files = [DiagnosticFile(uri="file:///src/app.py", diagnostics=[diag])]
    summary = DiagnosticTrackingService.format_summary(files)
    assert "app.py" in summary
    assert "F821" in summary
    assert "undefined variable" in summary

  def test_format_truncation(self) -> None:
    diags = [_make_diag(f"error {i}", line=i) for i in range(200)]
    files = [DiagnosticFile(uri="file:///big.py", diagnostics=diags)]
    summary = DiagnosticTrackingService.format_summary(files)
    assert summary.endswith("…[truncated]")
    assert len(summary) <= 4000

  def test_severity_symbols(self) -> None:
    assert DiagnosticTrackingService.severity_symbol(DiagnosticSeverity.ERROR) == "✖"
    assert DiagnosticTrackingService.severity_symbol(DiagnosticSeverity.WARNING) == "⚠"


class TestNormalizeUri:
  def test_file_protocol(self) -> None:
    assert _normalize_uri("file:///home/user/test.py") == "/home/user/test.py"

  def test_claude_fs_right(self) -> None:
    assert _normalize_uri("_claude_fs_right:/test.py") == "/test.py"

  def test_no_prefix(self) -> None:
    assert _normalize_uri("/test.py") == "/test.py"


# ── notifier tests ───────────────────────────────────────────────────────

from packages.agnt_services.notifier import (
  NotificationOptions,
  send_notification,
)


class _MockTerminal:
  def __init__(self) -> None:
    self.calls: list[str] = []

  def notify_iterm2(self, opts: NotificationOptions) -> None:
    self.calls.append(f"iterm2:{opts.message}")

  def notify_kitty(self, *, message: str, title: str, notification_id: int) -> None:
    self.calls.append(f"kitty:{message}")

  def notify_ghostty(self, *, message: str, title: str) -> None:
    self.calls.append(f"ghostty:{message}")

  def notify_bell(self) -> None:
    self.calls.append("bell")


class TestNotifier:
  @pytest.mark.asyncio
  async def test_iterm2_channel(self) -> None:
    term = _MockTerminal()
    opts = NotificationOptions(message="hello", notification_type="test")
    result = await send_notification(opts, term, channel="iterm2")
    assert result == "iterm2"
    assert "iterm2:hello" in term.calls

  @pytest.mark.asyncio
  async def test_kitty_channel(self) -> None:
    term = _MockTerminal()
    opts = NotificationOptions(message="hi", notification_type="test")
    result = await send_notification(opts, term, channel="kitty")
    assert result == "kitty"
    assert any("kitty:" in c for c in term.calls)

  @pytest.mark.asyncio
  async def test_ghostty_channel(self) -> None:
    term = _MockTerminal()
    opts = NotificationOptions(message="hey", notification_type="test")
    result = await send_notification(opts, term, channel="ghostty")
    assert result == "ghostty"

  @pytest.mark.asyncio
  async def test_bell_channel(self) -> None:
    term = _MockTerminal()
    opts = NotificationOptions(message="ding", notification_type="test")
    result = await send_notification(opts, term, channel="terminal_bell")
    assert result == "terminal_bell"
    assert "bell" in term.calls

  @pytest.mark.asyncio
  async def test_disabled_channel(self) -> None:
    term = _MockTerminal()
    opts = NotificationOptions(message="x", notification_type="test")
    result = await send_notification(opts, term, channel="notifications_disabled")
    assert result == "disabled"
    assert len(term.calls) == 0

  @pytest.mark.asyncio
  async def test_auto_iterm2(self, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TERM_PROGRAM", "iTerm.app")
    term = _MockTerminal()
    opts = NotificationOptions(message="auto", notification_type="test")
    result = await send_notification(opts, term, channel="auto")
    assert result == "iterm2"

  @pytest.mark.asyncio
  async def test_auto_unknown(self, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TERM_PROGRAM", "xterm")
    term = _MockTerminal()
    opts = NotificationOptions(message="x", notification_type="test")
    result = await send_notification(opts, term, channel="auto")
    assert result == "no_method_available"


# ── away_summary tests ──────────────────────────────────────────────────

from packages.agnt_services.away_summary import (
  RECENT_MESSAGE_WINDOW,
  build_away_prompt,
  generate_away_summary,
)


class _MockGenerator:
  def __init__(
    self, response: str | None = "Building a web app. Next: add auth."
  ) -> None:
    self.response = response
    self.call_count = 0
    self.last_messages: list[dict[str, str]] = []

  async def generate(
    self, messages: list[dict[str, str]], system_prompt: str
  ) -> str | None:
    self.call_count += 1
    self.last_messages = messages
    return self.response


class TestAwaySummary:
  def test_build_prompt_no_memory(self) -> None:
    prompt = build_away_prompt()
    assert "stepped away" in prompt
    assert "Session memory" not in prompt

  def test_build_prompt_with_memory(self) -> None:
    prompt = build_away_prompt("working on auth")
    assert "Session memory" in prompt
    assert "working on auth" in prompt

  @pytest.mark.asyncio
  async def test_empty_messages(self) -> None:
    gen = _MockGenerator()
    result = await generate_away_summary([], generator=gen)
    assert result is None
    assert gen.call_count == 0

  @pytest.mark.asyncio
  async def test_successful_generation(self) -> None:
    gen = _MockGenerator("Building auth. Next: add JWT.")
    msgs = [{"role": "user", "content": "help me build auth"}]
    result = await generate_away_summary(msgs, generator=gen)
    assert result == "Building auth. Next: add JWT."
    assert gen.call_count == 1

  @pytest.mark.asyncio
  async def test_truncates_to_window(self) -> None:
    gen = _MockGenerator("summary")
    msgs = [{"role": "user", "content": f"msg {i}"} for i in range(50)]
    await generate_away_summary(msgs, generator=gen)
    # Should have RECENT_MESSAGE_WINDOW msgs + 1 appended prompt
    assert len(gen.last_messages) == RECENT_MESSAGE_WINDOW + 1

  @pytest.mark.asyncio
  async def test_generator_returns_none(self) -> None:
    gen = _MockGenerator(None)
    msgs = [{"role": "user", "content": "hi"}]
    result = await generate_away_summary(msgs, generator=gen)
    assert result is None

  @pytest.mark.asyncio
  async def test_generator_raises(self) -> None:
    class _Exploder:
      async def generate(self, messages, system_prompt):
        raise RuntimeError("boom")

    result = await generate_away_summary(
      [{"role": "user", "content": "hi"}], generator=_Exploder()
    )
    assert result is None


# ── rate_limit_messages tests ────────────────────────────────────────────

from packages.agnt_services.rate_limit_messages import (
  LimitStatus,
  RateLimitContext,
  RateLimitType,
  format_reset_time,
  get_rate_limit_error_message,
  get_rate_limit_message,
  get_rate_limit_warning,
  get_using_overage_text,
  is_rate_limit_error_message,
)


class TestIsRateLimitErrorMessage:
  def test_matches(self) -> None:
    assert is_rate_limit_error_message("You've hit your weekly limit")
    assert is_rate_limit_error_message("You've used 80% of your limit")
    assert is_rate_limit_error_message("You're out of extra usage")

  def test_no_match(self) -> None:
    assert not is_rate_limit_error_message("Something else")
    assert not is_rate_limit_error_message("")


class TestGetRateLimitMessage:
  def test_normal_no_message(self) -> None:
    ctx = RateLimitContext(status=LimitStatus.ALLOWED)
    assert get_rate_limit_message(ctx) is None

  def test_rejected_error(self) -> None:
    ctx = RateLimitContext(
      status=LimitStatus.REJECTED,
      rate_limit_type=RateLimitType.FIVE_HOUR,
    )
    msg = get_rate_limit_message(ctx)
    assert msg is not None
    assert msg.severity == "error"
    assert "session limit" in msg.message

  def test_rejected_weekly(self) -> None:
    ctx = RateLimitContext(
      status=LimitStatus.REJECTED,
      rate_limit_type=RateLimitType.SEVEN_DAY,
    )
    msg = get_rate_limit_message(ctx)
    assert msg is not None
    assert "weekly limit" in msg.message

  def test_warning_with_utilization(self) -> None:
    ctx = RateLimitContext(
      status=LimitStatus.ALLOWED_WARNING,
      rate_limit_type=RateLimitType.SEVEN_DAY,
      utilization=0.85,
    )
    msg = get_rate_limit_message(ctx)
    assert msg is not None
    assert msg.severity == "warning"
    assert "85%" in msg.message

  def test_warning_below_threshold(self) -> None:
    ctx = RateLimitContext(
      status=LimitStatus.ALLOWED_WARNING,
      rate_limit_type=RateLimitType.SEVEN_DAY,
      utilization=0.5,
    )
    assert get_rate_limit_message(ctx) is None

  def test_overage_warning(self) -> None:
    ctx = RateLimitContext(
      is_using_overage=True,
      overage_status=LimitStatus.ALLOWED_WARNING,
    )
    msg = get_rate_limit_message(ctx)
    assert msg is not None
    assert "extra usage" in msg.message

  def test_overage_no_warning(self) -> None:
    ctx = RateLimitContext(
      is_using_overage=True,
      overage_status=LimitStatus.ALLOWED,
    )
    assert get_rate_limit_message(ctx) is None


class TestErrorAndWarningHelpers:
  def test_error_only(self) -> None:
    ctx = RateLimitContext(
      status=LimitStatus.REJECTED,
      rate_limit_type=RateLimitType.FIVE_HOUR,
    )
    assert get_rate_limit_error_message(ctx) is not None
    assert get_rate_limit_warning(ctx) is None

  def test_warning_only(self) -> None:
    ctx = RateLimitContext(
      status=LimitStatus.ALLOWED_WARNING,
      rate_limit_type=RateLimitType.SEVEN_DAY,
      utilization=0.9,
    )
    assert get_rate_limit_warning(ctx) is not None
    assert get_rate_limit_error_message(ctx) is None


class TestFormatResetTime:
  def test_past_timestamp(self) -> None:
    assert format_reset_time(0) == "now"

  def test_future_hours(self) -> None:
    import time

    future = int(time.time()) + 7200  # 2 hours
    result = format_reset_time(future)
    assert result.startswith("in ")
    assert "h" in result


class TestUsingOverageText:
  def test_session_limit(self) -> None:
    import time

    future_ts = int(time.time()) + 7200
    ctx = RateLimitContext(rate_limit_type=RateLimitType.FIVE_HOUR, resets_at=future_ts)
    text = get_using_overage_text(ctx)
    assert "extra usage" in text
    assert "session limit" in text

  def test_session_limit_no_reset(self) -> None:
    ctx = RateLimitContext(rate_limit_type=RateLimitType.FIVE_HOUR)
    text = get_using_overage_text(ctx)
    assert "extra usage" in text
    assert text == "You're now using extra usage"

  def test_no_limit_type(self) -> None:
    ctx = RateLimitContext()
    text = get_using_overage_text(ctx)
    assert text == "Now using extra usage"


class TestRegistryBatch3:
  """Verify the 4 new Batch 3 services load through the registry."""

  def test_services_load(self) -> None:
    from packages.agnt_services import ServiceRegistry

    reg = ServiceRegistry()
    for name in (
      "diagnostic_tracking",
      "notifier",
      "away_summary",
      "rate_limit_messages",
    ):
      svc = reg.get(name)
      assert svc is not None, f"Service {name} failed to load"

  def test_registry_count_increased(self) -> None:
    from packages.agnt_services import _SERVICE_REGISTRY

    # Should be at least 37 with the 4 new additions
    assert len(_SERVICE_REGISTRY) >= 37
