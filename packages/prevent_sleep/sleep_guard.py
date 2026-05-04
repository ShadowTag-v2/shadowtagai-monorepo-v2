"""macOS sleep prevention via ``caffeinate``.

Ported from Claude Code ``src/services/preventSleep.ts``.

Key design decisions from the original:

1. **caffeinate -i -t 300**: ``-i`` prevents idle sleep (least aggressive —
   display can still sleep). ``-t 300`` makes the process auto-exit after
   5 minutes, providing self-healing if the parent is SIGKILL'd.

2. **Periodic restart**: A daemon thread restarts ``caffeinate`` every 4 minutes
   (before the 5-minute timeout) to maintain continuous prevention.

3. **Reference counting**: ``start_prevent_sleep`` / ``stop_prevent_sleep``
   are symmetric. Only the transition from 0→1 spawns, and 1→0 kills.

4. **unref() equivalent**: The subprocess is spawned with ``start_new_session=True``
   so it doesn't block Python's own exit. The restart thread is daemonized.
"""

from __future__ import annotations

import atexit
import logging
import platform
import subprocess
import threading
from contextlib import contextmanager
from collections.abc import Generator

logger = logging.getLogger(__name__)

# Caffeinate timeout in seconds — process auto-exits after this duration.
CAFFEINATE_TIMEOUT_SECONDS = 300  # 5 minutes

# Restart interval — restart caffeinate before it expires.
# 4 minutes gives plenty of buffer before the 5-minute timeout.
RESTART_INTERVAL_SECONDS = 4 * 60  # 240 seconds

_lock = threading.Lock()
_ref_count = 0
_caffeinate_proc: subprocess.Popen[bytes] | None = None
_restart_timer: threading.Timer | None = None
_atexit_registered = False


def start_prevent_sleep() -> None:
    """Increment the reference count and start preventing sleep if needed.

    Call this when starting work that should keep the Mac awake.
    """
    global _ref_count
    with _lock:
        _ref_count += 1
        if _ref_count == 1:
            _spawn_caffeinate()
            _start_restart_timer()


def stop_prevent_sleep() -> None:
    """Decrement the reference count and allow sleep if no more work is pending.

    Call this when work completes.
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

    Use this for cleanup on exit.
    """
    global _ref_count
    with _lock:
        _ref_count = 0
        _stop_restart_timer()
        _kill_caffeinate()


def is_preventing_sleep() -> bool:
    """Return True if sleep prevention is currently active."""
    with _lock:
        return _caffeinate_proc is not None and _caffeinate_proc.poll() is None


def get_ref_count() -> int:
    """Return the current reference count."""
    with _lock:
        return _ref_count


@contextmanager
def PreventSleepContext() -> Generator[None]:
    """Context manager for sleep prevention.

    Usage::

        with PreventSleepContext():
            run_long_operation()
    """
    start_prevent_sleep()
    try:
        yield
    finally:
        stop_prevent_sleep()


def _spawn_caffeinate() -> None:
    """Spawn the caffeinate process. Must be called with ``_lock`` held."""
    global _caffeinate_proc, _atexit_registered

    # Only run on macOS
    if platform.system() != "Darwin":
        return

    # Already running
    if _caffeinate_proc is not None and _caffeinate_proc.poll() is None:
        return

    # Register atexit cleanup on first use
    if not _atexit_registered:
        _atexit_registered = True
        atexit.register(force_stop_prevent_sleep)

    try:
        # -i: Create assertion to prevent idle sleep (display can still sleep)
        # -t: Timeout in seconds — self-healing if Python is SIGKILL'd
        _caffeinate_proc = subprocess.Popen(
            ["caffeinate", "-i", "-t", str(CAFFEINATE_TIMEOUT_SECONDS)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Python equivalent of .unref()
        )
        logger.debug("Started caffeinate (PID %d) to prevent sleep", _caffeinate_proc.pid)
    except (FileNotFoundError, OSError) as exc:
        # caffeinate not available or spawn failed — silently degrade
        logger.debug("caffeinate spawn failed: %s", exc)
        _caffeinate_proc = None


def _kill_caffeinate() -> None:
    """Kill the caffeinate process. Must be called with ``_lock`` held."""
    global _caffeinate_proc

    if _caffeinate_proc is not None:
        proc = _caffeinate_proc
        _caffeinate_proc = None
        try:
            proc.kill()  # SIGKILL for immediate termination
            proc.wait(timeout=2)
            logger.debug("Stopped caffeinate, allowing sleep")
        except (OSError, subprocess.TimeoutExpired):
            # Process may have already exited
            pass


def _restart_caffeinate() -> None:
    """Restart caffeinate to maintain continuous sleep prevention.

    Called by the restart timer. Re-acquires the lock.
    """
    with _lock:
        if _ref_count > 0:
            logger.debug("Restarting caffeinate to maintain sleep prevention")
            _kill_caffeinate()
            _spawn_caffeinate()
            # Schedule the next restart
            _start_restart_timer()


def _start_restart_timer() -> None:
    """Start the periodic restart timer. Must be called with ``_lock`` held."""
    global _restart_timer

    # Only run on macOS
    if platform.system() != "Darwin":
        return

    # Already running
    if _restart_timer is not None and _restart_timer.is_alive():
        return

    _restart_timer = threading.Timer(RESTART_INTERVAL_SECONDS, _restart_caffeinate)
    _restart_timer.daemon = True  # Don't block Python exit
    _restart_timer.start()


def _stop_restart_timer() -> None:
    """Stop the periodic restart timer. Must be called with ``_lock`` held."""
    global _restart_timer

    if _restart_timer is not None:
        _restart_timer.cancel()
        _restart_timer = None
