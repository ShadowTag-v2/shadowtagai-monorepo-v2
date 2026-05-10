"""
ANSI Parser — Semantic Action Generator

Port of Claude Code's ink/termio/parser.ts.
A streaming parser that produces structured semantic actions
from ANSI escape sequences. Uses the tokenizer for boundary
detection, then interprets each sequence.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Generator

from .ansi import C0
from .csi import CSI, CURSOR_STYLES, ERASE_DISPLAY, ERASE_LINE_REGION
from .dec import DEC
from .esc import parse_esc
from .osc import parse_osc
from .sgr import apply_sgr
from .tokenizer import Token, Tokenizer
from .types import (
  Action,
  AlternateScreenMode,
  BellAction,
  BracketedPasteMode,
  CursorActionWrapper,
  CursorColumn,
  CursorHide,
  CursorMove,
  CursorNextLine,
  CursorPosition,
  CursorPrevLine,
  CursorRestore,
  CursorRow,
  CursorSave,
  CursorShow,
  CursorStyleAction,
  EraseActionWrapper,
  EraseChars,
  EraseDisplay,
  EraseLine,
  FocusEventsMode,
  Grapheme,
  LinkEnd,
  LinkStart,
  ModeActionWrapper,
  MouseTrackingMode,
  ScrollActionWrapper,
  ScrollDown,
  ScrollSetRegion,
  ScrollUp,
  SGRAction,
  TextAction,
  TextStyle,
  UnknownAction,
  default_style,
)


# =============================================================================
# Grapheme Utilities
# =============================================================================


def _is_emoji(cp: int) -> bool:
  return (
    (0x2600 <= cp <= 0x26FF)
    or (0x2700 <= cp <= 0x27BF)
    or (0x1F300 <= cp <= 0x1F9FF)
    or (0x1FA00 <= cp <= 0x1FAFF)
    or (0x1F1E0 <= cp <= 0x1F1FF)
  )


def _is_east_asian_wide(cp: int) -> bool:
  return (
    (0x1100 <= cp <= 0x115F)
    or (0x2E80 <= cp <= 0x9FFF)
    or (0xAC00 <= cp <= 0xD7A3)
    or (0xF900 <= cp <= 0xFAFF)
    or (0xFE10 <= cp <= 0xFE1F)
    or (0xFE30 <= cp <= 0xFE6F)
    or (0xFF00 <= cp <= 0xFF60)
    or (0xFFE0 <= cp <= 0xFFE6)
    or (0x20000 <= cp <= 0x2FFFD)
    or (0x30000 <= cp <= 0x3FFFD)
  )


def _has_multiple_codepoints(s: str) -> bool:
  return any(count > 0 for count, _ in enumerate(s))


def _grapheme_width(grapheme: str) -> int:
  if _has_multiple_codepoints(grapheme):
    return 2
  first_cp = ord(grapheme[0]) if grapheme else 0
  if _is_emoji(first_cp) or _is_east_asian_wide(first_cp):
    return 2
  return 1


def _segment_graphemes(text: str) -> Generator[Grapheme]:
  """Segment text into graphemes with width info.

  Uses Python's built-in grapheme segmentation via unicodedata
  as a simplified alternative to Intl.Segmenter.
  """
  # Python 3.14 doesn't have Intl.Segmenter equivalent built-in.
  # Use a simple approach: iterate codepoints and yield each char.
  # For production, consider the `grapheme` PyPI package.
  # This handles most common cases correctly.
  i = 0
  while i < len(text):
    # Handle surrogate pairs (already handled by Python str)
    # Combine with following combining characters
    j = i + 1
    while j < len(text) and unicodedata.combining(text[j]):
      j += 1
    # Check for emoji ZWJ sequences
    while (
      j < len(text) and j + 1 < len(text) and text[j] == "\u200d"  # ZWJ
    ):
      j += 2  # skip ZWJ + next char
      while j < len(text) and unicodedata.combining(text[j]):
        j += 1
    segment = text[i:j]
    w = _grapheme_width(segment)
    yield Grapheme(value=segment, width=min(w, 2))  # type: ignore[arg-type]
    i = j


# =============================================================================
# CSI Parsing
# =============================================================================


def _parse_csi_params(param_str: str) -> list[int]:
  if param_str == "":
    return []
  return [0 if s == "" else int(s) for s in re.split(r"[;:]", param_str)]


def _parse_csi(raw: str) -> Action | None:
  """Parse a raw CSI sequence into an action."""
  inner = raw[2:]
  if not inner:
    return None

  final_byte = ord(inner[-1])
  before_final = inner[:-1]

  private_mode = ""
  param_str = before_final
  intermediate = ""

  if before_final and before_final[0] in "?>=":
    private_mode = before_final[0]
    param_str = before_final[1:]

  int_match = re.search(r"([^0-9;:]+)$", param_str)
  if int_match:
    intermediate = int_match.group(1)
    param_str = param_str[: -len(intermediate)]

  params = _parse_csi_params(param_str)
  p0 = params[0] if params else 1
  p1 = params[1] if len(params) > 1 else 1

  # SGR
  if final_byte == CSI.SGR and private_mode == "":
    return SGRAction(params=param_str)

  # Cursor movement
  if final_byte == CSI.CUU:
    return CursorActionWrapper(action=CursorMove(direction="up", count=p0))
  if final_byte == CSI.CUD:
    return CursorActionWrapper(action=CursorMove(direction="down", count=p0))
  if final_byte == CSI.CUF:
    return CursorActionWrapper(action=CursorMove(direction="forward", count=p0))
  if final_byte == CSI.CUB:
    return CursorActionWrapper(action=CursorMove(direction="back", count=p0))
  if final_byte == CSI.CNL:
    return CursorActionWrapper(action=CursorNextLine(count=p0))
  if final_byte == CSI.CPL:
    return CursorActionWrapper(action=CursorPrevLine(count=p0))
  if final_byte == CSI.CHA:
    return CursorActionWrapper(action=CursorColumn(col=p0))
  if final_byte in (CSI.CUP, CSI.HVP):
    return CursorActionWrapper(action=CursorPosition(row=p0, col=p1))
  if final_byte == CSI.VPA:
    return CursorActionWrapper(action=CursorRow(row=p0))

  # Erase
  if final_byte == CSI.ED:
    idx = params[0] if params else 0
    region = ERASE_DISPLAY[idx] if idx < len(ERASE_DISPLAY) else "toEnd"
    return EraseActionWrapper(action=EraseDisplay(region=region))
  if final_byte == CSI.EL:
    idx = params[0] if params else 0
    region = ERASE_LINE_REGION[idx] if idx < len(ERASE_LINE_REGION) else "toEnd"
    return EraseActionWrapper(action=EraseLine(region=region))
  if final_byte == CSI.ECH:
    return EraseActionWrapper(action=EraseChars(count=p0))

  # Scroll
  if final_byte == CSI.SU:
    return ScrollActionWrapper(action=ScrollUp(count=p0))
  if final_byte == CSI.SD:
    return ScrollActionWrapper(action=ScrollDown(count=p0))
  if final_byte == CSI.DECSTBM:
    return ScrollActionWrapper(action=ScrollSetRegion(top=p0, bottom=p1))

  # Cursor save/restore
  if final_byte == CSI.SCOSC:
    return CursorActionWrapper(action=CursorSave())
  if final_byte == CSI.SCORC:
    return CursorActionWrapper(action=CursorRestore())

  # Cursor style
  if final_byte == CSI.DECSCUSR and intermediate == " ":
    idx = p0 if p0 < len(CURSOR_STYLES) else 0
    info = CURSOR_STYLES[idx]
    return CursorActionWrapper(
      action=CursorStyleAction(style=info["style"], blinking=info["blinking"])
    )

  # Private modes
  if private_mode == "?" and final_byte in (CSI.SM, CSI.RM):
    enabled = final_byte == CSI.SM
    if p0 == DEC.CURSOR_VISIBLE:
      return CursorActionWrapper(action=CursorShow() if enabled else CursorHide())
    if p0 in (DEC.ALT_SCREEN_CLEAR, DEC.ALT_SCREEN):
      return ModeActionWrapper(action=AlternateScreenMode(enabled=enabled))
    if p0 == DEC.BRACKETED_PASTE:
      return ModeActionWrapper(action=BracketedPasteMode(enabled=enabled))
    if p0 == DEC.MOUSE_NORMAL:
      return ModeActionWrapper(
        action=MouseTrackingMode(mode="normal" if enabled else "off")
      )
    if p0 == DEC.MOUSE_BUTTON:
      return ModeActionWrapper(
        action=MouseTrackingMode(mode="button" if enabled else "off")
      )
    if p0 == DEC.MOUSE_ANY:
      return ModeActionWrapper(
        action=MouseTrackingMode(mode="any" if enabled else "off")
      )
    if p0 == DEC.FOCUS_EVENTS:
      return ModeActionWrapper(action=FocusEventsMode(enabled=enabled))

  return UnknownAction(sequence=raw)


def _identify_sequence(seq: str) -> str:
  """Identify the type of escape sequence from its raw form."""
  if len(seq) < 2 or ord(seq[0]) != C0.ESC:
    return "unknown"
  second = ord(seq[1])
  if second == 0x5B:
    return "csi"
  if second == 0x5D:
    return "osc"
  if second == 0x4F:
    return "ss3"
  return "esc"


# =============================================================================
# Main Parser
# =============================================================================


class Parser:
  """Streaming ANSI parser — produces semantic actions.

  Maintains style state across incremental feed() calls.

  Usage::

      parser = Parser()
      actions1 = parser.feed("partial\\x1b[")
      actions2 = parser.feed("31mred")  # style state maintained
  """

  def __init__(self) -> None:
    self._tokenizer = Tokenizer()
    self.style: TextStyle = default_style()
    self.in_link: bool = False
    self.link_url: str | None = None

  def reset(self) -> None:
    self._tokenizer.reset()
    self.style = default_style()
    self.in_link = False
    self.link_url = None

  def feed(self, input_str: str) -> list[Action]:
    """Feed input and get resulting actions."""
    tokens = self._tokenizer.feed(input_str)
    actions: list[Action] = []
    for token in tokens:
      actions.extend(self._process_token(token))
    return actions

  def _process_token(self, token: Token) -> list[Action]:
    if token.type == "text":
      return self._process_text(token.value)
    return self._process_sequence(token.value)

  def _process_text(self, text: str) -> list[Action]:
    actions: list[Action] = []
    current = ""
    for char in text:
      if ord(char) == C0.BEL:
        if current:
          graphemes = tuple(_segment_graphemes(current))
          if graphemes:
            actions.append(TextAction(graphemes=graphemes, style=self.style.copy()))
          current = ""
        actions.append(BellAction())
      else:
        current += char
    if current:
      graphemes = tuple(_segment_graphemes(current))
      if graphemes:
        actions.append(TextAction(graphemes=graphemes, style=self.style.copy()))
    return actions

  def _process_sequence(self, seq: str) -> list[Action]:
    seq_type = _identify_sequence(seq)

    if seq_type == "csi":
      action = _parse_csi(seq)
      if not action:
        return []
      if action.type == "sgr":
        self.style = apply_sgr(action.params, self.style)
        return []
      return [action]

    if seq_type == "osc":
      content = seq[2:]
      if content.endswith("\x07"):
        content = content[:-1]
      elif content.endswith("\x1b\\"):
        content = content[:-2]
      action = parse_osc(content)
      if action:
        if action.type == "link":
          if isinstance(action.action, LinkStart):
            self.in_link = True
            self.link_url = action.action.url
          elif isinstance(action.action, LinkEnd):
            self.in_link = False
            self.link_url = None
        return [action]
      return []

    if seq_type == "esc":
      esc_content = seq[1:]
      action = parse_esc(esc_content)
      return [action] if action else []

    if seq_type == "ss3":
      return [UnknownAction(sequence=seq)]

    return [UnknownAction(sequence=seq)]
