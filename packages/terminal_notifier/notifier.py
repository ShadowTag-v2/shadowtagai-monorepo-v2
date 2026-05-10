"""Multi-terminal notification routing engine.

Ported from Claude Code ``src/services/notifier.ts``.

Key design decisions from the original:

1. **Auto-detection** via ``TERM_PROGRAM`` env var matches the exact terminal.
2. **Channel cascade**: User can override with a preferred channel, or ``auto``
   detects from the environment.
3. **OSC escape sequences**: iTerm2 uses OSC 9, Kitty uses OSC 99,
   Ghostty uses OSC 777. Bell uses ``\\a``.
4. **Apple Terminal bell check**: On Apple Terminal, the original checks
   whether the bell is disabled in Terminal preferences via ``osascript``
   + ``defaults export``. We replicate this with subprocess calls.
"""

from __future__ import annotations

import enum
import logging
import os
import random
import subprocess
import sys
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DEFAULT_TITLE = "Antigravity"


class NotificationChannel(enum.Enum):
  """Supported notification channels."""

  AUTO = "auto"
  ITERM2 = "iterm2"
  ITERM2_WITH_BELL = "iterm2_with_bell"
  KITTY = "kitty"
  GHOSTTY = "ghostty"
  TERMINAL_BELL = "terminal_bell"
  DISABLED = "notifications_disabled"


@dataclass(frozen=True)
class NotificationResult:
  """Result of a notification attempt."""

  method_used: str
  success: bool


def detect_terminal() -> str:
  """Detect the current terminal emulator from ``TERM_PROGRAM``.

  Returns the raw value of ``TERM_PROGRAM`` or ``"unknown"`` if unset.
  """
  return os.environ.get("TERM_PROGRAM", "unknown")


def send_notification(
  message: str,
  *,
  title: str | None = None,
  channel: NotificationChannel = NotificationChannel.AUTO,
  notification_type: str = "general",
) -> NotificationResult:
  """Send a notification to the user's terminal.

  Parameters
  ----------
  message:
      The notification body text.
  title:
      Optional title (defaults to "Antigravity").
  channel:
      Which channel to use. ``AUTO`` detects from ``TERM_PROGRAM``.
  notification_type:
      Classification for analytics (e.g., "task_complete", "error").

  Returns
  -------
  NotificationResult
      Which method was actually used and whether it succeeded.
  """
  resolved_title = title or DEFAULT_TITLE

  try:
    method = _send_to_channel(channel, message, resolved_title)
    return NotificationResult(method_used=method, success=True)
  except Exception:
    logger.debug("Notification failed", exc_info=True)
    return NotificationResult(method_used="error", success=False)


def _send_to_channel(channel: NotificationChannel, message: str, title: str) -> str:
  """Route notification to the appropriate channel."""
  if channel == NotificationChannel.AUTO:
    return _send_auto(message, title)

  if channel == NotificationChannel.ITERM2:
    _notify_iterm2(message, title)
    return "iterm2"

  if channel == NotificationChannel.ITERM2_WITH_BELL:
    _notify_iterm2(message, title)
    _notify_bell()
    return "iterm2_with_bell"

  if channel == NotificationChannel.KITTY:
    _notify_kitty(message, title)
    return "kitty"

  if channel == NotificationChannel.GHOSTTY:
    _notify_ghostty(message, title)
    return "ghostty"

  if channel == NotificationChannel.TERMINAL_BELL:
    _notify_bell()
    return "terminal_bell"

  if channel == NotificationChannel.DISABLED:
    return "disabled"

  return "none"


def _send_auto(message: str, title: str) -> str:
  """Auto-detect terminal and send via the best available method."""
  terminal = detect_terminal()

  if terminal == "Apple_Terminal":
    # Apple Terminal: bell only (if not disabled)
    bell_disabled = _is_apple_terminal_bell_disabled()
    if not bell_disabled:
      _notify_bell()
      return "terminal_bell"
    return "no_method_available"

  if terminal == "iTerm.app":
    _notify_iterm2(message, title)
    return "iterm2"

  if terminal == "kitty":
    _notify_kitty(message, title)
    return "kitty"

  if terminal == "ghostty":
    _notify_ghostty(message, title)
    return "ghostty"

  # Unknown terminal — try bell as fallback
  _notify_bell()
  return "terminal_bell_fallback"


# ---------------------------------------------------------------------------
# Terminal-specific notification implementations
# ---------------------------------------------------------------------------


def _notify_iterm2(message: str, title: str) -> None:
  """Send an iTerm2 notification via OSC 9.

  See: https://iterm2.com/documentation-escape-codes.html
  """
  # OSC 9 ; <message> ST
  osc = f"\033]9;{title}: {message}\007"
  sys.stderr.write(osc)
  sys.stderr.flush()


def _notify_kitty(message: str, title: str) -> None:
  """Send a Kitty notification via OSC 99.

  See: https://sw.kovidgoyal.net/kitty/desktop-notifications/
  """
  notif_id = random.randint(0, 9999)
  # OSC 99 ; i=<id>:d=0:p=title ; <title> ST
  # OSC 99 ; i=<id>:d=1:p=body ; <body> ST
  title_osc = f"\033]99;i={notif_id}:d=0:p=title;{title}\033\\"
  body_osc = f"\033]99;i={notif_id}:d=1:p=body;{message}\033\\"
  sys.stderr.write(title_osc + body_osc)
  sys.stderr.flush()


def _notify_ghostty(message: str, title: str) -> None:
  """Send a Ghostty notification via OSC 777.

  Ghostty uses the notify OSC: ``\\033]777;notify;<title>;<body>\\007``
  """
  osc = f"\033]777;notify;{title};{message}\007"
  sys.stderr.write(osc)
  sys.stderr.flush()


def _notify_bell() -> None:
  """Send a terminal bell character (BEL / ``\\a``)."""
  sys.stderr.write("\a")
  sys.stderr.flush()


def _is_apple_terminal_bell_disabled() -> bool:
  """Check if the bell is disabled in Apple Terminal's current profile.

  Replicates the original's ``osascript`` + ``defaults export`` approach.
  Returns True if the bell is explicitly disabled, False otherwise.
  """
  try:
    terminal = detect_terminal()
    if terminal != "Apple_Terminal":
      return False

    # Get current profile name via osascript
    result = subprocess.run(
      [
        "osascript",
        "-e",
        'tell application "Terminal" to name of current settings of front window',
      ],
      capture_output=True,
      text=True,
      timeout=5,
    )
    current_profile = result.stdout.strip()
    if not current_profile:
      return False

    # Export Terminal preferences
    defaults_result = subprocess.run(
      ["defaults", "export", "com.apple.Terminal", "-"],
      capture_output=True,
      text=True,
      timeout=5,
    )
    if defaults_result.returncode != 0:
      return False

    # Parse plist to check Bell setting
    # We use a simple string search instead of importing plist
    # to avoid a dependency — the original lazy-loads plist too.
    plist_text = defaults_result.stdout
    # Look for the profile section and its Bell key
    if f"<key>{current_profile}</key>" in plist_text:
      # Find the Bell setting near the profile — crude but effective
      profile_start = plist_text.index(f"<key>{current_profile}</key>")
      section = plist_text[profile_start : profile_start + 2000]
      if "<key>Bell</key>" in section:
        bell_idx = section.index("<key>Bell</key>")
        after_bell = section[bell_idx + len("<key>Bell</key>") : bell_idx + 100]
        return "<false/>" in after_bell
    return False
  except Exception:
    logger.debug("Apple Terminal bell check failed", exc_info=True)
    return False
