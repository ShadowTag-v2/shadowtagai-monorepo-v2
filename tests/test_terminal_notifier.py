"""Tests for packages.terminal_notifier.

Validates:
- Auto-detection of terminal emulators via TERM_PROGRAM
- Channel routing for iTerm2, Kitty, Ghostty, Apple Terminal, bell
- OSC escape sequence output
- Notification result structure
- Apple Terminal bell-disabled detection
"""

from __future__ import annotations

import sys
from unittest import mock


from packages.terminal_notifier import (
  NotificationChannel,
  detect_terminal,
  send_notification,
)


class TestDetectTerminal:
  """TERM_PROGRAM-based terminal auto-detection."""

  def test_iterm2_detection(self) -> None:
    with mock.patch.dict("os.environ", {"TERM_PROGRAM": "iTerm.app"}):
      assert detect_terminal() == "iTerm.app"

  def test_kitty_detection(self) -> None:
    with mock.patch.dict("os.environ", {"TERM_PROGRAM": "kitty"}):
      assert detect_terminal() == "kitty"

  def test_ghostty_detection(self) -> None:
    with mock.patch.dict("os.environ", {"TERM_PROGRAM": "ghostty"}):
      assert detect_terminal() == "ghostty"

  def test_apple_terminal_detection(self) -> None:
    with mock.patch.dict("os.environ", {"TERM_PROGRAM": "Apple_Terminal"}):
      assert detect_terminal() == "Apple_Terminal"

  def test_unknown_terminal(self) -> None:
    with mock.patch.dict("os.environ", {}, clear=True):
      assert detect_terminal() == "unknown"


class TestSendNotification:
  """Notification routing and result structure."""

  def test_iterm2_osc9(self) -> None:
    with mock.patch.object(sys, "stderr") as mock_stderr:
      result = send_notification(
        "test msg",
        title="Test",
        channel=NotificationChannel.ITERM2,
      )
      assert result.success is True
      assert result.method_used == "iterm2"
      # Verify OSC 9 sequence was written
      written = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
      assert "\033]9;" in written

  def test_kitty_osc99(self) -> None:
    with mock.patch.object(sys, "stderr") as mock_stderr:
      result = send_notification(
        "test msg",
        title="Test",
        channel=NotificationChannel.KITTY,
      )
      assert result.success is True
      assert result.method_used == "kitty"
      written = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
      assert "\033]99;" in written

  def test_ghostty_osc777(self) -> None:
    with mock.patch.object(sys, "stderr") as mock_stderr:
      result = send_notification(
        "test msg",
        title="Test",
        channel=NotificationChannel.GHOSTTY,
      )
      assert result.success is True
      assert result.method_used == "ghostty"
      written = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
      assert "\033]777;" in written

  def test_bell(self) -> None:
    with mock.patch.object(sys, "stderr") as mock_stderr:
      result = send_notification(
        "test msg",
        channel=NotificationChannel.TERMINAL_BELL,
      )
      assert result.success is True
      assert result.method_used == "terminal_bell"
      written = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
      assert "\a" in written

  def test_disabled_channel(self) -> None:
    result = send_notification(
      "test msg",
      channel=NotificationChannel.DISABLED,
    )
    assert result.success is True
    assert result.method_used == "disabled"

  def test_default_title(self) -> None:
    with mock.patch.object(sys, "stderr") as mock_stderr:
      result = send_notification(
        "hello",
        channel=NotificationChannel.ITERM2,
      )
      assert result.success is True
      written = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
      assert "Antigravity" in written

  def test_iterm2_with_bell(self) -> None:
    with mock.patch.object(sys, "stderr") as mock_stderr:
      result = send_notification(
        "test",
        channel=NotificationChannel.ITERM2_WITH_BELL,
      )
      assert result.success is True
      assert result.method_used == "iterm2_with_bell"
      written = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
      # Both OSC 9 and bell should be present
      assert "\033]9;" in written
      assert "\a" in written


class TestAutoDetection:
  """Auto-detection routing paths."""

  def test_auto_routes_to_iterm2(self) -> None:
    with (
      mock.patch.dict("os.environ", {"TERM_PROGRAM": "iTerm.app"}),
      mock.patch.object(sys, "stderr"),
    ):
      result = send_notification("test", channel=NotificationChannel.AUTO)
      assert result.success is True
      assert result.method_used == "iterm2"

  def test_auto_routes_to_kitty(self) -> None:
    with (
      mock.patch.dict("os.environ", {"TERM_PROGRAM": "kitty"}),
      mock.patch.object(sys, "stderr"),
    ):
      result = send_notification("test", channel=NotificationChannel.AUTO)
      assert result.success is True
      assert result.method_used == "kitty"

  def test_auto_routes_to_ghostty(self) -> None:
    with (
      mock.patch.dict("os.environ", {"TERM_PROGRAM": "ghostty"}),
      mock.patch.object(sys, "stderr"),
    ):
      result = send_notification("test", channel=NotificationChannel.AUTO)
      assert result.success is True
      assert result.method_used == "ghostty"

  def test_auto_unknown_falls_back_to_bell(self) -> None:
    with (
      mock.patch.dict("os.environ", {"TERM_PROGRAM": "alacritty"}),
      mock.patch.object(sys, "stderr"),
    ):
      result = send_notification("test", channel=NotificationChannel.AUTO)
      assert result.success is True
      assert result.method_used == "terminal_bell_fallback"

  def test_auto_apple_terminal_bell_enabled(self) -> None:
    with (
      mock.patch.dict("os.environ", {"TERM_PROGRAM": "Apple_Terminal"}),
      mock.patch.object(sys, "stderr"),
      mock.patch(
        "packages.terminal_notifier.notifier._is_apple_terminal_bell_disabled",
        return_value=False,
      ),
    ):
      result = send_notification("test", channel=NotificationChannel.AUTO)
      assert result.success is True
      assert result.method_used == "terminal_bell"

  def test_auto_apple_terminal_bell_disabled(self) -> None:
    with (
      mock.patch.dict("os.environ", {"TERM_PROGRAM": "Apple_Terminal"}),
      mock.patch(
        "packages.terminal_notifier.notifier._is_apple_terminal_bell_disabled",
        return_value=True,
      ),
    ):
      result = send_notification("test", channel=NotificationChannel.AUTO)
      assert result.success is True
      assert result.method_used == "no_method_available"
