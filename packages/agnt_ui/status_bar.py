"""Status bar — persistent bottom-of-terminal status line.

Replaces the React/Ink bottom bar with a rich Live panel that
shows model, cost, and mode indicators.

Safe Harbor: Pure terminal output. No DOM, no WebSocket.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

try:
  from rich.console import Console
  from rich.table import Table
  from rich.live import Live

  HAS_RICH = True
except ImportError:
  HAS_RICH = False


@dataclass
class StatusState:
  """Mutable state for the status bar."""

  model: str = "gemini-3.1-flash-lite-preview-thinking"
  mode: str = "YOLO"
  cost_usd: float = 0.0
  tokens_in: int = 0
  tokens_out: int = 0
  tool_calls: int = 0
  errors: int = 0
  _extra: dict[str, str] = field(default_factory=dict)

  def set(self, key: str, value: str) -> None:
    """Set an arbitrary status field."""
    self._extra[key] = value


class StatusBar:
  """Persistent status bar for the terminal.

  Usage::

      bar = StatusBar()
      bar.start()
      bar.state.cost_usd = 0.0042
      bar.state.tokens_in = 1500
      bar.refresh()
      # ... later ...
      bar.stop()
  """

  __slots__ = ("state", "_live", "_console")

  def __init__(self) -> None:
    self.state = StatusState()
    self._live = None
    self._console = None

  def _build_table(self) -> object:
    """Build the status bar table."""
    if not HAS_RICH:
      return self._build_plain()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column(style="bold yellow", no_wrap=True)
    table.add_column(style="green", no_wrap=True)
    table.add_column(style="dim", no_wrap=True)
    table.add_column(style="dim", no_wrap=True)

    table.add_row(
      f"🤖 {self.state.model}",
      f"⚡ {self.state.mode}",
      f"💰 ${self.state.cost_usd:.4f}",
      f"📊 {self.state.tokens_in}↓ {self.state.tokens_out}↑",
      f"🔧 {self.state.tool_calls} tools"
      + (f" | ❌ {self.state.errors}" if self.state.errors else ""),
    )

    return table

  def _build_plain(self) -> str:
    """Plain text fallback for terminals without rich."""
    parts = [
      f"Model: {self.state.model}",
      f"Mode: {self.state.mode}",
      f"Cost: ${self.state.cost_usd:.4f}",
      f"Tokens: {self.state.tokens_in}↓/{self.state.tokens_out}↑",
      f"Tools: {self.state.tool_calls}",
    ]
    if self.state.errors:
      parts.append(f"Errors: {self.state.errors}")
    return " | ".join(parts)

  def start(self) -> None:
    """Start the live status bar."""
    if HAS_RICH:
      self._console = Console(file=sys.stderr)
      self._live = Live(
        self._build_table(),
        console=self._console,
        refresh_per_second=2,
      )
      self._live.start()

  def refresh(self) -> None:
    """Refresh the status bar with current state."""
    if self._live and HAS_RICH:
      self._live.update(self._build_table())

  def stop(self) -> None:
    """Stop the live status bar."""
    if self._live:
      self._live.stop()
      self._live = None

  def print_once(self) -> None:
    """Print current status as a one-shot (no live refresh)."""
    if HAS_RICH and self._console is None:
      self._console = Console(file=sys.stderr)
    if self._console:
      self._console.print(self._build_table())
    else:
      print(self._build_plain(), file=sys.stderr)
