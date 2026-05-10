# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prevents macOS from sleeping while the agent is working.

Ported from src/services/preventSleep.ts (Claude Code v2.1.91).

Uses the built-in `caffeinate` command to create a power assertion that
prevents idle sleep. This keeps the Mac awake during API requests and
tool execution so long-running operations don't get interrupted.

The caffeinate process is spawned with a timeout and periodically restarted.
This provides self-healing behavior: if the Python process is killed with
SIGKILL (which doesn't run cleanup handlers), the orphaned caffeinate will
automatically exit after the timeout expires.

Only runs on macOS — no-op on other platforms.
"""

from __future__ import annotations

import atexit
import logging
import subprocess
import sys
import threading
from typing import Final

logger = logging.getLogger(__name__)

# Caffeinate timeout in seconds. Process auto-exits after this duration.
# We restart it before expiry to maintain continuous sleep prevention.
CAFFEINATE_TIMEOUT_SECONDS: Final[int] = 300  # 5 minutes

# Restart interval — restart caffeinate before it expires.
# Use 4 minutes to give plenty of buffer before the 5-minute timeout.
RESTART_INTERVAL_SECONDS: Final[float] = 4 * 60  # 4 minutes

_lock = threading.Lock()
_caffeinate_process: subprocess.Popen[bytes] | None = None
_restart_timer: threading.Timer | None = None
_ref_count: int = 0
_cleanup_registered: bool = False


def start_prevent_sleep() -> None:
  """Increment the reference count and start preventing sleep if needed.

  Call this when starting work that should keep the Mac awake.
  Thread-safe via internal lock.
  """
  global _ref_count

  with _lock:
    _ref_count += 1
    if _ref_count == 1:
      _spawn_caffeinate()
      _start_restart_timer()


def stop_prevent_sleep() -> None:
  """Decrement the reference count and allow sleep if no more work is pending.

  Call this when work completes. Thread-safe.
  """
  global _ref_count

  with _lock:
    if _ref_count > 0:
      _ref_count -= 1

    if _ref_count == 0:
      _stop_restart_timer()
      _kill_caffeinate()


def force_stop_prevent_sleep() -> None:
  """Force stop preventing sleep, regardless of reference count.

  Use this for cleanup on exit. Thread-safe.
  """
  global _ref_count

  with _lock:
    _ref_count = 0
    _stop_restart_timer()
    _kill_caffeinate()


def get_ref_count() -> int:
  """Return the current reference count (for diagnostics)."""
  return _ref_count


def is_active() -> bool:
  """Return True if caffeinate is currently running."""
  return _caffeinate_process is not None and _caffeinate_process.poll() is None


def _spawn_caffeinate() -> None:
  """Spawn a caffeinate process. Must be called with _lock held."""
  global _caffeinate_process, _cleanup_registered

  # Only run on macOS
  if sys.platform != "darwin":
    return

  # Already running
  if _caffeinate_process is not None and _caffeinate_process.poll() is None:
    return

  # Register cleanup on first use
  if not _cleanup_registered:
    _cleanup_registered = True
    atexit.register(force_stop_prevent_sleep)

  try:
    # -i: Create an assertion to prevent idle sleep
    #     This is the least aggressive option — display can still sleep
    # -t: Timeout in seconds — caffeinate exits automatically after this
    #     This provides self-healing if Python is killed with SIGKILL
    _caffeinate_process = subprocess.Popen(
      ["caffeinate", "-i", "-t", str(CAFFEINATE_TIMEOUT_SECONDS)],
      stdin=subprocess.DEVNULL,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
    )
    logger.debug(
      "Started caffeinate (pid=%d) to prevent sleep", _caffeinate_process.pid
    )
  except FileNotFoundError:
    # caffeinate not available (shouldn't happen on macOS)
    logger.debug("caffeinate binary not found")
    _caffeinate_process = None
  except OSError as e:
    logger.debug("caffeinate spawn error: %s", e)
    _caffeinate_process = None


def _kill_caffeinate() -> None:
  """Kill the caffeinate process. Must be called with _lock held."""
  global _caffeinate_process

  if _caffeinate_process is not None:
    proc = _caffeinate_process
    _caffeinate_process = None
    try:
      proc.kill()  # SIGKILL for immediate termination
      proc.wait(timeout=2)
      logger.debug("Stopped caffeinate, allowing sleep")
    except ProcessLookupError, subprocess.TimeoutExpired:
      # Process may have already exited
      pass


def _restart_callback() -> None:
  """Timer callback to restart caffeinate before it expires."""
  with _lock:
    if _ref_count > 0:
      logger.debug("Restarting caffeinate to maintain sleep prevention")
      _kill_caffeinate()
      _spawn_caffeinate()
      _start_restart_timer()


def _start_restart_timer() -> None:
  """Start the periodic restart timer. Must be called with _lock held."""
  global _restart_timer

  # Only run on macOS
  if sys.platform != "darwin":
    return

  # Already running
  if _restart_timer is not None:
    return

  _restart_timer = threading.Timer(RESTART_INTERVAL_SECONDS, _restart_callback)
  _restart_timer.daemon = True  # Don't keep Python alive for this
  _restart_timer.start()


def _stop_restart_timer() -> None:
  """Stop the periodic restart timer. Must be called with _lock held."""
  global _restart_timer

  if _restart_timer is not None:
    _restart_timer.cancel()
    _restart_timer = None


__all__ = [
  "start_prevent_sleep",
  "stop_prevent_sleep",
  "force_stop_prevent_sleep",
  "get_ref_count",
  "is_active",
]
