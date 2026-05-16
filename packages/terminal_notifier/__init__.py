"""Multi-terminal notification routing.

Ported from Claude Code's ``notifier.ts`` — routes notifications to the
appropriate terminal notification channel (iTerm2, Kitty, Ghostty, Apple
Terminal bell) based on auto-detection or user configuration.

Architecture
~~~~~~~~~~~~
- **Auto-detection**: Reads ``TERM_PROGRAM`` to identify the terminal emulator.
- **Channel routing**: Supports iTerm2 OSC sequences, Kitty desktop notifications,
  Ghostty notifications, and basic terminal bell as channels.
- **Extensible**: Hook system allows custom notification handlers.

Supported terminals:
    - iTerm2 (OSC 9 notifications)
    - Kitty (OSC 99 desktop notifications)
    - Ghostty (OSC 777 notifications)
    - Apple Terminal (bell-only)
    - Generic (terminal bell fallback)

Usage::

    from packages.terminal_notifier import send_notification

    send_notification("Build complete!", title="Antigravity")
"""

from packages.terminal_notifier.notifier import (
  NotificationChannel,
  detect_terminal,
  send_notification,
)

__all__ = [
  "NotificationChannel",
  "detect_terminal",
  "send_notification",
]
