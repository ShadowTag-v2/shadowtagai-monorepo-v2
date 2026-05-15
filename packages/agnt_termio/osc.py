"""
OSC (Operating System Command) Types and Parser

Port of Claude Code's ink/termio/osc.ts.
Handles OSC parsing, clipboard write (native + tmux + OSC 52),
hyperlink generation, tab-status, and multiplexer passthrough.
"""

from __future__ import annotations

import base64
import os
import re
import subprocess
import sys
from typing import Literal
from collections.abc import Generator

from .ansi import BEL, ESC, ESC_TYPE, SEP
from .types import (
  Action,
  BothTitle,
  IconName,
  LinkActionWrapper,
  LinkEnd,
  LinkStart,
  RGBColor,
  TabStatusAction,
  TabStatusActionWrapper,
  TitleActionWrapper,
  UnknownAction,
  WindowTitle,
)

# =============================================================================
# Constants
# =============================================================================

OSC_PREFIX = ESC + chr(ESC_TYPE.OSC)

# String Terminator (ESC \) — alternative to BEL for terminating OSC
ST = ESC + "\\"


def _detect_terminal() -> str | None:
  """Detect terminal from env (simplified — no full env registry)."""
  term_program = os.environ.get("TERM_PROGRAM", "").lower()
  if "kitty" in term_program:
    return "kitty"
  lc_terminal = os.environ.get("LC_TERMINAL", "").lower()
  if "kitty" in lc_terminal:
    return "kitty"
  return term_program or None


def osc(*parts: str | int) -> str:
  """Generate an OSC sequence: ESC ] p1;p2;...;pN <terminator>.

  Uses ST terminator for Kitty (avoids beeps), BEL for others.
  """
  terminator = ST if _detect_terminal() == "kitty" else BEL
  return f"{OSC_PREFIX}{SEP.join(str(p) for p in parts)}{terminator}"


# =============================================================================
# OSC Command Numbers
# =============================================================================


class OSC:
  SET_TITLE_AND_ICON = 0
  SET_ICON = 1
  SET_TITLE = 2
  SET_COLOR = 4
  SET_CWD = 7
  HYPERLINK = 8
  ITERM2 = 9  # iTerm2 proprietary sequences
  SET_FG_COLOR = 10
  SET_BG_COLOR = 11
  SET_CURSOR_COLOR = 12
  CLIPBOARD = 52
  KITTY = 99  # Kitty notification protocol
  RESET_COLOR = 104
  RESET_FG_COLOR = 110
  RESET_BG_COLOR = 111
  RESET_CURSOR_COLOR = 112
  SEMANTIC_PROMPT = 133
  GHOSTTY = 777  # Ghostty notification protocol
  TAB_STATUS = 21337  # Tab status extension


# =============================================================================
# Multiplexer Passthrough
# =============================================================================


def wrap_for_multiplexer(sequence: str) -> str:
  """Wrap an escape sequence for terminal multiplexer passthrough.

  tmux and GNU screen intercept escape sequences; DCS passthrough
  tunnels them to the outer terminal unmodified.

  tmux 3.3+ gates this behind `allow-passthrough` (default off). When off,
  tmux silently drops the whole DCS — no junk, no worse than unwrapped OSC.
  """
  if os.environ.get("TMUX"):
    escaped = sequence.replace("\x1b", "\x1b\x1b")
    return f"\x1bPtmux;{escaped}\x1b\\"
  if os.environ.get("STY"):
    return f"\x1bP{sequence}\x1b\\"
  return sequence


def _tmux_passthrough(payload: str) -> str:
  """Wrap a payload in tmux's DCS passthrough.

  Inner ESCs must be doubled. Requires `set -g allow-passthrough on`.
  """
  return f"{ESC}Ptmux;{payload.replace(ESC, ESC + ESC)}{ST}"


# =============================================================================
# Clipboard Path Detection
# =============================================================================

ClipboardPath = Literal["native", "tmux-buffer", "osc52"]


def get_clipboard_path() -> ClipboardPath:
  """Determine which path setClipboard will take, based on env state.

  - 'native': pbcopy (or equivalent) — high-confidence system clipboard write.
  - 'tmux-buffer': tmux load-buffer — paste with prefix+] works.
  - 'osc52': raw OSC 52 sequence to stdout. Best-effort.
  """
  native_available = sys.platform == "darwin" and not os.environ.get("SSH_CONNECTION")
  if native_available:
    return "native"
  if os.environ.get("TMUX"):
    return "tmux-buffer"
  return "osc52"


# =============================================================================
# Clipboard Operations
# =============================================================================

# Linux clipboard tool: None = not yet probed, False = none available.
_linux_copy_tool: str | None | bool = None


def _reset_linux_copy_cache() -> None:
  """Test-only: reset the Linux clipboard tool probe cache."""
  global _linux_copy_tool
  _linux_copy_tool = None


def _exec_no_throw(
  cmd: list[str],
  input_data: str | None = None,
  timeout: float = 2.0,
) -> int:
  """Run a subprocess, returning exit code. Never raises."""
  try:
    proc = subprocess.run(
      cmd,
      input=input_data,
      capture_output=True,
      text=True,
      timeout=timeout,
    )
    return proc.returncode
  except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
    return -1


def _copy_native(text: str) -> None:
  """Shell out to a native clipboard utility as a safety net for OSC 52.

  Only called when not in an SSH session (over SSH, these would write
  to the remote machine's clipboard — OSC 52 is the right path there).
  Fire-and-forget: failures are silent since OSC 52 may have succeeded.
  """
  global _linux_copy_tool

  if sys.platform == "darwin":
    _exec_no_throw(["pbcopy"], input_data=text)
    return

  if sys.platform == "linux":
    if _linux_copy_tool is False:
      return
    if _linux_copy_tool == "wl-copy":
      _exec_no_throw(["wl-copy"], input_data=text)
      return
    if _linux_copy_tool == "xclip":
      _exec_no_throw(["xclip", "-selection", "clipboard"], input_data=text)
      return
    if _linux_copy_tool == "xsel":
      _exec_no_throw(["xsel", "--clipboard", "--input"], input_data=text)
      return
    # First call: probe wl-copy → xclip → xsel, cache winner
    if _exec_no_throw(["wl-copy"], input_data=text) == 0:
      _linux_copy_tool = "wl-copy"
      return
    if _exec_no_throw(["xclip", "-selection", "clipboard"], input_data=text) == 0:
      _linux_copy_tool = "xclip"
      return
    if _exec_no_throw(["xsel", "--clipboard", "--input"], input_data=text) == 0:
      _linux_copy_tool = "xsel"
      return
    _linux_copy_tool = False
    return

  if sys.platform == "win32":
    _exec_no_throw(["clip"], input_data=text)


def tmux_load_buffer(text: str) -> bool:
  """Load text into tmux's paste buffer via `tmux load-buffer`.

  -w (tmux 3.2+) propagates to the outer terminal's clipboard via tmux's
  own OSC 52 emission. -w is dropped for iTerm2: tmux's OSC 52 emission
  crashes the iTerm2 session over SSH.

  Returns True if the buffer was loaded successfully.
  """
  if not os.environ.get("TMUX"):
    return False

  args = (
    ["load-buffer", "-"]
    if os.environ.get("LC_TERMINAL") == "iTerm2"
    else ["load-buffer", "-w", "-"]
  )
  return _exec_no_throw(["tmux", *args], input_data=text) == 0


def set_clipboard(text: str) -> str:
  """OSC 52 clipboard write with native + tmux fallback.

  Returns the sequence for the caller to write to stdout (raw OSC 52
  outside tmux, DCS-wrapped inside).
  """
  b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
  raw = osc(OSC.CLIPBOARD, "c", b64)

  # Native safety net — fire FIRST, before tmux await
  if not os.environ.get("SSH_CONNECTION"):
    _copy_native(text)

  tmux_loaded = tmux_load_buffer(text)

  # Inner OSC uses BEL directly (not osc()) — ST's ESC would need doubling
  if tmux_loaded:
    return _tmux_passthrough(f"{ESC}]52;c;{b64}{BEL}")
  return raw


# =============================================================================
# OSC Parsing
# =============================================================================


def parse_osc(content: str) -> Action | None:
  """Parse an OSC sequence into an action.

  Args:
      content: The sequence content (without ESC ] and terminator).
  """
  semicolon_idx = content.find(";")
  command = content[:semicolon_idx] if semicolon_idx >= 0 else content
  data = content[semicolon_idx + 1 :] if semicolon_idx >= 0 else ""

  try:
    command_num = int(command)
  except ValueError:
    return UnknownAction(sequence=f"\x1b]{content}")

  # Window/icon title
  if command_num == OSC.SET_TITLE_AND_ICON:
    return TitleActionWrapper(action=BothTitle(title=data))
  if command_num == OSC.SET_ICON:
    return TitleActionWrapper(action=IconName(name=data))
  if command_num == OSC.SET_TITLE:
    return TitleActionWrapper(action=WindowTitle(title=data))

  # Hyperlinks (OSC 8)
  if command_num == OSC.HYPERLINK:
    parts = data.split(";", 1)
    params_str = parts[0] if parts else ""
    url = parts[1] if len(parts) > 1 else ""

    if url == "":
      return LinkActionWrapper(action=LinkEnd())

    params: dict[str, str] = {}
    if params_str:
      for pair in params_str.split(":"):
        eq_idx = pair.find("=")
        if eq_idx >= 0:
          params[pair[:eq_idx]] = pair[eq_idx + 1 :]

    return LinkActionWrapper(
      action=LinkStart(
        url=url,
        params=params if params else None,
      ),
    )

  # Tab status (OSC 21337)
  if command_num == OSC.TAB_STATUS:
    return TabStatusActionWrapper(action=_parse_tab_status(data))

  return UnknownAction(sequence=f"\x1b]{content}")


# =============================================================================
# Color Parsing
# =============================================================================

_HEX_RE = re.compile(r"^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$")
_RGB_RE = re.compile(r"^rgb:([0-9a-fA-F]{1,4})/([0-9a-fA-F]{1,4})/([0-9a-fA-F]{1,4})$")


def parse_osc_color(spec: str) -> RGBColor | None:
  """Parse an XParseColor-style color spec into an RGBColor.

  Accepts `#RRGGBB` and `rgb:R/G/B` (1–4 hex digits per component,
  scaled to 8-bit). Returns None on parse failure.
  """
  hex_match = _HEX_RE.match(spec)
  if hex_match:
    return RGBColor(
      r=int(hex_match.group(1), 16),
      g=int(hex_match.group(2), 16),
      b=int(hex_match.group(3), 16),
    )
  rgb_match = _RGB_RE.match(spec)
  if rgb_match:

    def _scale(s: str) -> int:
      return round((int(s, 16) / (16 ** len(s) - 1)) * 255)

    return RGBColor(
      r=_scale(rgb_match.group(1)),
      g=_scale(rgb_match.group(2)),
      b=_scale(rgb_match.group(3)),
    )
  return None


# =============================================================================
# Tab Status
# =============================================================================


def _parse_tab_status(data: str) -> TabStatusAction:
  """Parse OSC 21337 payload: `key=value;key=value;...`."""
  action = TabStatusAction()
  for key, value in _split_tab_status_pairs(data):
    if key == "indicator":
      action.has_indicator = True
      action.indicator = None if value == "" else parse_osc_color(value)
    elif key == "status":
      action.has_status = True
      action.status = None if value == "" else value
    elif key == "status-color":
      action.has_status_color = True
      action.status_color = None if value == "" else parse_osc_color(value)
  return action


def _split_tab_status_pairs(data: str) -> Generator[tuple[str, str]]:
  """Split `k=v;k=v` honoring `\\;` and `\\\\` escapes."""
  key = ""
  val = ""
  in_val = False
  esc = False
  for c in data:
    if esc:
      if in_val:
        val += c
      else:
        key += c
      esc = False
    elif c == "\\":
      esc = True
    elif c == ";":
      yield key, val
      key = ""
      val = ""
      in_val = False
    elif c == "=" and not in_val:
      in_val = True
    elif in_val:
      val += c
    else:
      key += c
  if key or in_val:
    yield key, val


# =============================================================================
# Output Generators
# =============================================================================


def _osc8_id(url: str) -> str:
  """Generate a deterministic id for OSC 8 hyperlinks from the URL."""
  h = 0
  for ch in url:
    h = ((h << 5) - h + ord(ch)) & 0xFFFFFFFF
  return _to_base36(h)


def _to_base36(n: int) -> str:
  """Convert unsigned int to base-36 string."""
  if n == 0:
    return "0"
  chars = "0123456789abcdefghijklmnopqrstuvwxyz"
  result = []
  while n:
    result.append(chars[n % 36])
    n //= 36
  return "".join(reversed(result))


LINK_END = osc(OSC.HYPERLINK, "", "")


def link(url: str, params: dict[str, str] | None = None) -> str:
  """Start a hyperlink (OSC 8).

  Auto-assigns an id= param derived from the URL so terminals group
  wrapped lines of the same link together.
  Empty url = close sequence (empty params per spec).
  """
  if not url:
    return LINK_END
  p = {"id": _osc8_id(url)}
  if params:
    p.update(params)
  param_str = ":".join(f"{k}={v}" for k, v in p.items())
  return osc(OSC.HYPERLINK, param_str, url)


# =============================================================================
# iTerm2 Extensions
# =============================================================================


class ITERM2:
  NOTIFY = 0
  BADGE = 2
  PROGRESS = 4


class PROGRESS:
  CLEAR = 0
  SET = 1
  ERROR = 2
  INDETERMINATE = 3


CLEAR_ITERM2_PROGRESS = (
  f"{OSC_PREFIX}{OSC.ITERM2};{ITERM2.PROGRESS};{PROGRESS.CLEAR};{BEL}"
)
CLEAR_TERMINAL_TITLE = f"{OSC_PREFIX}{OSC.SET_TITLE_AND_ICON};{BEL}"
CLEAR_TAB_STATUS = osc(OSC.TAB_STATUS, "indicator=;status=;status-color=")


# =============================================================================
# Tab Status Emission
# =============================================================================


def tab_status(fields: TabStatusAction) -> str:
  """Emit an OSC 21337 tab-status sequence.

  Omitted fields are left unchanged by the receiving terminal;
  `None` sends an empty value to clear.
  """
  parts: list[str] = []

  def _rgb(c: RGBColor) -> str:
    return f"#{c.r:02x}{c.g:02x}{c.b:02x}"

  if fields.has_indicator:
    parts.append(
      f"indicator={_rgb(fields.indicator) if isinstance(fields.indicator, RGBColor) else ''}"
    )
  if fields.has_status:
    status_val = (
      fields.status.replace("\\", "\\\\").replace(";", "\\;") if fields.status else ""
    )
    parts.append(f"status={status_val}")
  if fields.has_status_color:
    parts.append(
      f"status-color={_rgb(fields.status_color) if isinstance(fields.status_color, RGBColor) else ''}"
    )
  return osc(OSC.TAB_STATUS, ";".join(parts))
