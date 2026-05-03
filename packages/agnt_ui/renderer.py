"""Terminal renderer — rich-based replacement for React/Ink.

Provides structured output for:
- Tool call headers and results
- Streaming LLM token output
- Markdown rendering
- Status and progress indicators

Safe Harbor: Pure stdout/stderr. No browser, no DOM, no WebSocket.
"""

from __future__ import annotations

import sys
from typing import IO

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.theme import Theme

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


# ─── Theme ────────────────────────────────────────────────────────────

_AGNT_THEME = {
    "agnt.tool": "bold cyan",
    "agnt.result": "green",
    "agnt.error": "bold red",
    "agnt.warning": "yellow",
    "agnt.dim": "dim",
    "agnt.header": "bold magenta",
    "agnt.cost": "bold yellow",
}


class TerminalRenderer:
    """Rich-based terminal renderer for agent output.

    Falls back to plain print() if rich is not installed.
    """

    __slots__ = ("_console", "_err_console", "_stream_buffer")

    def __init__(
        self,
        file: IO[str] | None = None,
        force_terminal: bool = False,
    ) -> None:
        if HAS_RICH:
            theme = Theme(_AGNT_THEME)
            self._console = Console(
                file=file or sys.stdout,
                theme=theme,
                force_terminal=force_terminal,
            )
            self._err_console = Console(
                file=sys.stderr,
                theme=theme,
                force_terminal=force_terminal,
            )
        else:
            self._console = None
            self._err_console = None
        self._stream_buffer: list[str] = []

    # ─── Tool output ─────────────────────────────────────────────

    def tool_start(self, tool_name: str, args_summary: str = "") -> None:
        """Render a tool invocation header."""
        label = f"⚡ {tool_name}"
        if args_summary:
            label += f"  {args_summary}"
        if self._console:
            self._console.print(
                Text(label, style="agnt.tool"),
            )
        else:
            print(label)

    def tool_result(self, result: str) -> None:
        """Render a tool result."""
        if self._console:
            self._console.print(
                Text(f"  ✓ {result}", style="agnt.result"),
            )
        else:
            print(f"  ✓ {result}")

    def tool_error(self, error: str) -> None:
        """Render a tool error."""
        if self._err_console:
            self._err_console.print(
                Text(f"  ✗ {error}", style="agnt.error"),
            )
        else:
            print(f"  ✗ {error}", file=sys.stderr)

    # ─── Streaming tokens ────────────────────────────────────────

    def stream_token(self, token: str) -> None:
        """Write a single streaming token from the LLM."""
        self._stream_buffer.append(token)
        if self._console:
            self._console.print(token, end="", highlight=False)
        else:
            print(token, end="", flush=True)

    def stream_flush(self) -> str:
        """Flush the stream buffer and return accumulated text."""
        text = "".join(self._stream_buffer)
        self._stream_buffer.clear()
        if self._console:
            self._console.print()  # newline
        else:
            print()
        return text

    # ─── Markdown ────────────────────────────────────────────────

    def render_markdown(self, md_text: str) -> None:
        """Render markdown in the terminal."""
        if self._console and HAS_RICH:
            self._console.print(Markdown(md_text))
        else:
            print(md_text)

    def render_code(self, code: str, language: str = "python", title: str = "") -> None:
        """Render a syntax-highlighted code block."""
        if self._console and HAS_RICH:
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            if title:
                self._console.print(Panel(syntax, title=title))
            else:
                self._console.print(syntax)
        else:
            if title:
                print(f"--- {title} ---")
            print(code)

    # ─── Status messages ─────────────────────────────────────────

    def header(self, text: str) -> None:
        """Print a styled header."""
        if self._console:
            self._console.print(Text(text, style="agnt.header"))
        else:
            print(f"\n{'─' * 60}\n{text}\n{'─' * 60}")

    def info(self, text: str) -> None:
        """Print an info message."""
        if self._console:
            self._console.print(f"[agnt.dim]ℹ {text}[/]")
        else:
            print(f"ℹ {text}")

    def warning(self, text: str) -> None:
        """Print a warning."""
        if self._err_console:
            self._err_console.print(f"[agnt.warning]⚠ {text}[/]")
        else:
            print(f"⚠ {text}", file=sys.stderr)

    def error(self, text: str) -> None:
        """Print an error."""
        if self._err_console:
            self._err_console.print(f"[agnt.error]✗ {text}[/]")
        else:
            print(f"✗ {text}", file=sys.stderr)

    def cost(self, label: str, amount: float) -> None:
        """Print a cost indicator."""
        msg = f"💰 {label}: ${amount:.4f}"
        if self._console:
            self._console.print(Text(msg, style="agnt.cost"))
        else:
            print(msg)

    # ─── Panels ──────────────────────────────────────────────────

    def panel(self, content: str, title: str = "", border_style: str = "cyan") -> None:
        """Render a bordered panel."""
        if self._console and HAS_RICH:
            self._console.print(Panel(content, title=title or None, border_style=border_style))
        else:
            if title:
                print(f"\n┌─ {title} {'─' * max(0, 50 - len(title))}┐")
            print(content)
            if title:
                print(f"└{'─' * 54}┘")
