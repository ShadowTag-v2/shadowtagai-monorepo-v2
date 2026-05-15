"""Hardware sleep prevention for macOS.

Ported from Claude Code's preventSleep.ts — uses the built-in ``caffeinate``
command to create a power assertion that prevents idle sleep during long-running
agent operations.

Architecture
~~~~~~~~~~~~
- **Reference-counted**: Multiple subsystems can request sleep prevention;
  the ``caffeinate`` process only exits when the last consumer releases.
- **Self-healing**: ``caffeinate`` is spawned with a timeout (``-t 300``) so
  orphaned processes die automatically if the parent Python process is killed
  with SIGKILL (no cleanup handlers run).
- **Periodic restart**: A background thread restarts ``caffeinate`` before its
  timeout expires (every 4 minutes vs. 5-minute timeout) to maintain
  continuous sleep prevention.
- **macOS-only**: All operations are no-ops on non-Darwin platforms.

Usage::

    from packages.prevent_sleep import start_prevent_sleep, stop_prevent_sleep

    start_prevent_sleep()
    try:
        run_long_operation()
    finally:
        stop_prevent_sleep()

Or as a context manager::

    from packages.prevent_sleep import prevent_sleep

    with prevent_sleep():
        run_long_operation()
"""

from packages.prevent_sleep.sleep_guard import (
  PreventSleepContext as prevent_sleep,
  force_stop_prevent_sleep,
  get_ref_count,
  is_preventing_sleep,
  start_prevent_sleep,
  stop_prevent_sleep,
)

__all__ = [
  "force_stop_prevent_sleep",
  "get_ref_count",
  "is_preventing_sleep",
  "prevent_sleep",
  "start_prevent_sleep",
  "stop_prevent_sleep",
]
