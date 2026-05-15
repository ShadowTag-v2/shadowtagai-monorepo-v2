# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Terminal notification dispatch — multi-terminal notification routing.

Ported from src/services/notifier.ts (Claude Code v2.1.91).

Routes notifications to the correct terminal emulator based on the
``$TERM_PROGRAM`` environment variable.  Supported terminals:

  - iTerm2: OSC 9 + proprietary escape sequences
  - Kitty: OSC 99 desktop notification protocol
  - Ghostty: OSC 777 notification
  - Apple Terminal: BEL (\\a) bell character

The dispatch logic is pure — terminal-specific escape sequence emission
is delegated to a ``TerminalNotification`` protocol, keeping this module
testable without a real terminal.
"""

from __future__ import annotations

import logging
import os
import random
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)

DEFAULT_TITLE = "Claude Code"


@dataclass(frozen=True, slots=True)
class NotificationOptions:
  """Notification payload."""

  message: str
  notification_type: str
  title: str | None = None


class TerminalNotification(Protocol):
  """Protocol for terminal-specific notification emission."""

  def notify_iterm2(self, opts: NotificationOptions) -> None: ...
  def notify_kitty(self, *, message: str, title: str, notification_id: int) -> None: ...
  def notify_ghostty(self, *, message: str, title: str) -> None: ...
  def notify_bell(self) -> None: ...


def _detect_terminal() -> str:
  """Detect the current terminal emulator from environment."""
  return os.environ.get("TERM_PROGRAM", "")


def _generate_kitty_id() -> int:
  """Generate a random Kitty notification ID."""
  return random.randint(0, 9999)


async def send_notification(
  opts: NotificationOptions,
  terminal: TerminalNotification,
  *,
  channel: str = "auto",
  hook_callback: object | None = None,
) -> str:
  """Send a notification through the configured channel.

  Parameters
  ----------
  opts:
      The notification payload.
  terminal:
      Terminal-specific notification emitter.
  channel:
      The notification channel to use.  ``"auto"`` detects the terminal.
  hook_callback:
      Optional async callable for notification hooks (pre-send).

  Returns
  -------
  str
      The method that was actually used (e.g., ``"iterm2"``, ``"terminal_bell"``).
  """
  if hook_callback is not None and callable(hook_callback):
    try:
      import asyncio

      result = hook_callback(opts)
      if asyncio.iscoroutine(result):
        await result
    except Exception:
      logger.debug("Notification hook failed", exc_info=True)

  return _send_to_channel(channel, opts, terminal)


def _send_to_channel(
  channel: str,
  opts: NotificationOptions,
  terminal: TerminalNotification,
) -> str:
  """Dispatch notification to the specified channel."""
  title = opts.title or DEFAULT_TITLE

  try:
    if channel == "auto":
      return _send_auto(opts, terminal)
    if channel == "iterm2":
      terminal.notify_iterm2(opts)
      return "iterm2"
    if channel == "iterm2_with_bell":
      terminal.notify_iterm2(opts)
      terminal.notify_bell()
      return "iterm2_with_bell"
    if channel == "kitty":
      terminal.notify_kitty(
        message=opts.message, title=title, notification_id=_generate_kitty_id()
      )
      return "kitty"
    if channel == "ghostty":
      terminal.notify_ghostty(message=opts.message, title=title)
      return "ghostty"
    if channel == "terminal_bell":
      terminal.notify_bell()
      return "terminal_bell"
    if channel == "notifications_disabled":
      return "disabled"
    return "none"
  except Exception:
    return "error"


def _send_auto(
  opts: NotificationOptions,
  terminal: TerminalNotification,
) -> str:
  """Auto-detect terminal and dispatch accordingly."""
  title = opts.title or DEFAULT_TITLE
  term = _detect_terminal()

  if term == "Apple_Terminal":
    # On Apple Terminal, we can only use bell
    terminal.notify_bell()
    return "terminal_bell"
  if term == "iTerm.app":
    terminal.notify_iterm2(opts)
    return "iterm2"
  if term == "kitty":
    terminal.notify_kitty(
      message=opts.message, title=title, notification_id=_generate_kitty_id()
    )
    return "kitty"
  if term == "ghostty":
    terminal.notify_ghostty(message=opts.message, title=title)
    return "ghostty"

  return "no_method_available"
