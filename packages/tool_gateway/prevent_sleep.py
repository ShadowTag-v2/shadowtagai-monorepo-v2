"""Prevent Sleep Service — macOS caffeinate with reference counting.

Ported from Claude Code preventSleep.ts (166L).
Prevents macOS from sleeping during long-running tool executions
using the built-in `caffeinate` command with self-healing timeouts.

Architecture:
  - Reference-counted: multiple callers can request sleep prevention
  - Self-healing: caffeinate spawned with timeout, periodically restarted
  - No-op on non-macOS platforms
  - Context manager for clean usage in Tool Gateway

Integration with Tool Gateway:
  Used as a context manager around long-running tool executions:
      with prevent_sleep():
          execute_tool(...)
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

# Caffeinate timeout in seconds. Process auto-exits after this duration.
# We restart it before expiry to maintain continuous sleep prevention.
CAFFEINATE_TIMEOUT_SECONDS = 300  # 5 minutes

# Restart interval — restart caffeinate before it expires.
# 4 minutes gives buffer before the 5 minute timeout.
RESTART_INTERVAL_SECONDS = 240  # 4 minutes

IS_MACOS = platform.system() == "Darwin"


class PreventSleepService:
  """macOS sleep prevention with reference counting and self-healing.

  Usage:
      # Context manager (preferred)
      with prevent_sleep():
          long_running_operation()

      # Manual control
      service = PreventSleepService.get_instance()
      service.start()
      try:
          long_running_operation()
      finally:
          service.stop()
  """

  _instance: PreventSleepService | None = None
  _lock = threading.Lock()

  def __init__(self) -> None:
    self._ref_count = 0
    self._process: subprocess.Popen[bytes] | None = None
    self._restart_timer: threading.Timer | None = None
    self._cleanup_registered = False
    self._mutex = threading.Lock()

  @classmethod
  def get_instance(cls) -> PreventSleepService:
    """Singleton accessor."""
    if cls._instance is None:
      with cls._lock:
        if cls._instance is None:
          cls._instance = cls()
    return cls._instance

  @classmethod
  def reset_for_testing(cls) -> None:
    """Test-only reset."""
    with cls._lock:
      if cls._instance is not None:
        cls._instance.force_stop()
      cls._instance = None

  def start(self) -> None:
    """Increment ref count and start preventing sleep if needed."""
    with self._mutex:
      self._ref_count += 1
      if self._ref_count == 1:
        self._spawn_caffeinate()
        self._start_restart_timer()

  def stop(self) -> None:
    """Decrement ref count and allow sleep if no more work pending."""
    with self._mutex:
      if self._ref_count > 0:
        self._ref_count -= 1

      if self._ref_count == 0:
        self._stop_restart_timer()
        self._kill_caffeinate()

  def force_stop(self) -> None:
    """Force stop regardless of ref count. Used for cleanup."""
    with self._mutex:
      self._ref_count = 0
      self._stop_restart_timer()
      self._kill_caffeinate()

  @property
  def is_active(self) -> bool:
    """Whether sleep prevention is currently active."""
    return self._ref_count > 0 and self._process is not None

  @property
  def ref_count(self) -> int:
    """Current reference count."""
    return self._ref_count

  # --- Internal ---

  def _spawn_caffeinate(self) -> None:
    """Spawn caffeinate process."""
    if not IS_MACOS:
      return

    if self._process is not None:
      return

    # Register cleanup on first use
    if not self._cleanup_registered:
      self._cleanup_registered = True
      atexit.register(self.force_stop)

    try:
      # -i: Create assertion to prevent idle sleep (least aggressive)
      # -t: Timeout — caffeinate exits automatically after this
      #     Provides self-healing if Python is killed with SIGKILL
      self._process = subprocess.Popen(
        [
          "caffeinate",
          "-i",
          "-t",
          str(CAFFEINATE_TIMEOUT_SECONDS),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
      )
      logger.debug("Started caffeinate (PID %d) to prevent sleep", self._process.pid)
    except (OSError, FileNotFoundError):
      # caffeinate not available or spawn failed
      self._process = None

  def _kill_caffeinate(self) -> None:
    """Kill caffeinate process."""
    if self._process is not None:
      proc = self._process
      self._process = None
      try:
        proc.kill()  # SIGKILL for immediate termination
        proc.wait(timeout=5)
        logger.debug("Stopped caffeinate, allowing sleep")
      except (OSError, subprocess.TimeoutExpired):
        pass  # Process may have already exited

  def _start_restart_timer(self) -> None:
    """Start periodic restart timer."""
    if not IS_MACOS:
      return

    if self._restart_timer is not None:
      return

    def _restart() -> None:
      with self._mutex:
        if self._ref_count > 0:
          logger.debug("Restarting caffeinate to maintain sleep prevention")
          self._kill_caffeinate()
          self._spawn_caffeinate()

          # Schedule next restart
          self._restart_timer = threading.Timer(RESTART_INTERVAL_SECONDS, _restart)
          self._restart_timer.daemon = True
          self._restart_timer.start()

    self._restart_timer = threading.Timer(RESTART_INTERVAL_SECONDS, _restart)
    self._restart_timer.daemon = True
    self._restart_timer.start()

  def _stop_restart_timer(self) -> None:
    """Stop periodic restart timer."""
    if self._restart_timer is not None:
      self._restart_timer.cancel()
      self._restart_timer = None


@contextmanager
def prevent_sleep() -> Generator[None]:
  """Context manager for sleep prevention during tool execution.

  Usage:
      with prevent_sleep():
          execute_long_running_tool()
  """
  service = PreventSleepService.get_instance()
  service.start()
  try:
    yield
  finally:
    service.stop()
