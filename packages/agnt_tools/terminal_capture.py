# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Terminal Capture Tool
AGNT equivalent of Claude Code's TerminalCaptureTool.
Captures the visual state and text buffer of the terminal for debugging context.
"""

import subprocess


class TerminalCaptureTool:
  def __init__(self):
    self.name = "terminal_capture"

  def capture(self, lines: int = 100) -> str:
    """
    Attempts to dump the current terminal multiplexer scrollback buffer.
    Defaults to capturing tmux pane history.
    """
    try:
      res = subprocess.run(
        ["tmux", "capture-pane", "-p", "-S", f"-{lines}"],
        capture_output=True,
        text=True,
        check=True,
      )
      return res.stdout.strip()
    except Exception as e:
      return f"[Terminal Capture Failed] {e}"
