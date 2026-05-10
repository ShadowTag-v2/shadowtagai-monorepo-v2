"""
ESC Sequence Parser

Port of Claude Code's ink/termio/esc.ts.
Handles simple escape sequences: ESC + one or two characters.
"""

from __future__ import annotations

from .types import (
  Action,
  CursorActionWrapper,
  CursorMove,
  CursorNextLine,
  CursorRestore,
  CursorSave,
  ResetAction,
  UnknownAction,
)


def parse_esc(chars: str) -> Action | None:
  """Parse a simple ESC sequence.

  Args:
      chars: Characters after ESC (not including ESC itself).
  """
  if len(chars) == 0:
    return None

  first = chars[0]

  # Full reset (RIS)
  if first == "c":
    return ResetAction()

  # Cursor save (DECSC)
  if first == "7":
    return CursorActionWrapper(action=CursorSave())

  # Cursor restore (DECRC)
  if first == "8":
    return CursorActionWrapper(action=CursorRestore())

  # Index — move cursor down (IND)
  if first == "D":
    return CursorActionWrapper(action=CursorMove(direction="down", count=1))

  # Reverse index — move cursor up (RI)
  if first == "M":
    return CursorActionWrapper(action=CursorMove(direction="up", count=1))

  # Next line (NEL)
  if first == "E":
    return CursorActionWrapper(action=CursorNextLine(count=1))

  # Horizontal tab set (HTS)
  if first == "H":
    return None

  # Charset selection (ESC ( X, ESC ) X, etc.) — silently ignore
  if first in "()" and len(chars) >= 2:
    return None

  return UnknownAction(sequence=f"\x1b{chars}")
