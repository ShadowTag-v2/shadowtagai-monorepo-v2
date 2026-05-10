"""Terminal spinner — replaces Ink Spinner component.

Safe Harbor: Pure stdout animation, no external dependencies
beyond optional ``rich``.
"""

from __future__ import annotations

import sys
import threading
import time

try:
  from rich.console import Console
  from rich.spinner import Spinner as RichSpinner
  from rich.live import Live

  HAS_RICH = True
except ImportError:
  HAS_RICH = False


# ─── Fallback ASCII spinner ─────────────────────────────────────────

_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")


class _FallbackSpinner:
  """ASCII braille spinner for terminals without rich."""

  __slots__ = ("_message", "_thread", "_stop_event", "_interval")

  def __init__(self, message: str, interval: float = 0.1) -> None:
    self._message = message
    self._interval = interval
    self._stop_event = threading.Event()
    self._thread: threading.Thread | None = None

  def start(self) -> None:
    self._stop_event.clear()
    self._thread = threading.Thread(target=self._run, daemon=True)
    self._thread.start()

  def _run(self) -> None:
    idx = 0
    while not self._stop_event.is_set():
      frame = _FRAMES[idx % len(_FRAMES)]
      sys.stdout.write(f"\r{frame} {self._message}")
      sys.stdout.flush()
      idx += 1
      time.sleep(self._interval)
    sys.stdout.write("\r" + " " * (len(self._message) + 4) + "\r")
    sys.stdout.flush()

  def stop(self) -> None:
    self._stop_event.set()
    if self._thread:
      self._thread.join(timeout=2)


# ─── Public API ──────────────────────────────────────────────────────


class AgntSpinner:
  """Context-manager spinner for long-running operations.

  Usage::

      with AgntSpinner("Thinking..."):
          do_work()
  """

  __slots__ = ("_message", "_impl", "_live")

  def __init__(self, message: str = "Working...") -> None:
    self._message = message
    self._impl = None
    self._live = None

  def __enter__(self) -> AgntSpinner:
    self.start()
    return self

  def __exit__(self, *_exc) -> None:
    self.stop()

  def start(self) -> None:
    """Start the spinner."""
    if HAS_RICH:
      console = Console(stderr=True)
      spinner = RichSpinner("dots", text=self._message)
      self._live = Live(spinner, console=console, refresh_per_second=10)
      self._live.start()
    else:
      self._impl = _FallbackSpinner(self._message)
      self._impl.start()

  def stop(self) -> None:
    """Stop the spinner."""
    if self._live:
      self._live.stop()
      self._live = None
    if self._impl:
      self._impl.stop()
      self._impl = None

  def update(self, message: str) -> None:
    """Update the spinner message."""
    self._message = message
    if self._live and HAS_RICH:
      spinner = RichSpinner("dots", text=message)
      self._live.update(spinner)
    elif self._impl:
      self._impl._message = message
