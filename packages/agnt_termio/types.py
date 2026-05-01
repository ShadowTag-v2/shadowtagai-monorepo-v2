"""
ANSI Parser — Semantic Types

Port of Claude Code's ink/termio/types.ts.

These types represent the semantic meaning of ANSI escape sequences,
not their string representation. Inspired by ghostty's action-based design.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# =============================================================================
# Colors
# =============================================================================

NamedColor = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "brightBlack",
    "brightRed",
    "brightGreen",
    "brightYellow",
    "brightBlue",
    "brightMagenta",
    "brightCyan",
    "brightWhite",
]


@dataclass(frozen=True, slots=True)
class NamedColorValue:
    type: Literal["named"] = field(default="named", init=False)
    name: NamedColor = "white"


@dataclass(frozen=True, slots=True)
class IndexedColor:
    type: Literal["indexed"] = field(default="indexed", init=False)
    index: int = 0  # 0-255


@dataclass(frozen=True, slots=True)
class RGBColor:
    type: Literal["rgb"] = field(default="rgb", init=False)
    r: int = 0
    g: int = 0
    b: int = 0


@dataclass(frozen=True, slots=True)
class DefaultColor:
    type: Literal["default"] = field(default="default", init=False)


Color = NamedColorValue | IndexedColor | RGBColor | DefaultColor

# =============================================================================
# Text Styles
# =============================================================================

UnderlineStyle = Literal["none", "single", "double", "curly", "dotted", "dashed"]


@dataclass(slots=True)
class TextStyle:
    """Text style attributes — represents current styling state."""

    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: UnderlineStyle = "none"
    blink: bool = False
    inverse: bool = False
    hidden: bool = False
    strikethrough: bool = False
    overline: bool = False
    fg: Color = field(default_factory=DefaultColor)
    bg: Color = field(default_factory=DefaultColor)
    underline_color: Color = field(default_factory=DefaultColor)

    def copy(self) -> TextStyle:
        """Create a shallow copy of this style."""
        return TextStyle(
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            blink=self.blink,
            inverse=self.inverse,
            hidden=self.hidden,
            strikethrough=self.strikethrough,
            overline=self.overline,
            fg=self.fg,
            bg=self.bg,
            underline_color=self.underline_color,
        )


def default_style() -> TextStyle:
    """Create a default (reset) text style."""
    return TextStyle()


def styles_equal(a: TextStyle, b: TextStyle) -> bool:
    """Check if two styles are equal."""
    return (
        a.bold == b.bold
        and a.dim == b.dim
        and a.italic == b.italic
        and a.underline == b.underline
        and a.blink == b.blink
        and a.inverse == b.inverse
        and a.hidden == b.hidden
        and a.strikethrough == b.strikethrough
        and a.overline == b.overline
        and a.fg == b.fg
        and a.bg == b.bg
        and a.underline_color == b.underline_color
    )


# =============================================================================
# Cursor Actions
# =============================================================================

CursorDirection = Literal["up", "down", "forward", "back"]


@dataclass(frozen=True, slots=True)
class CursorMove:
    type: Literal["move"] = field(default="move", init=False)
    direction: CursorDirection = "down"
    count: int = 1


@dataclass(frozen=True, slots=True)
class CursorPosition:
    type: Literal["position"] = field(default="position", init=False)
    row: int = 1
    col: int = 1


@dataclass(frozen=True, slots=True)
class CursorColumn:
    type: Literal["column"] = field(default="column", init=False)
    col: int = 1


@dataclass(frozen=True, slots=True)
class CursorRow:
    type: Literal["row"] = field(default="row", init=False)
    row: int = 1


@dataclass(frozen=True, slots=True)
class CursorSave:
    type: Literal["save"] = field(default="save", init=False)


@dataclass(frozen=True, slots=True)
class CursorRestore:
    type: Literal["restore"] = field(default="restore", init=False)


@dataclass(frozen=True, slots=True)
class CursorShow:
    type: Literal["show"] = field(default="show", init=False)


@dataclass(frozen=True, slots=True)
class CursorHide:
    type: Literal["hide"] = field(default="hide", init=False)


@dataclass(frozen=True, slots=True)
class CursorStyleAction:
    type: Literal["style"] = field(default="style", init=False)
    style: Literal["block", "underline", "bar"] = "block"
    blinking: bool = True


@dataclass(frozen=True, slots=True)
class CursorNextLine:
    type: Literal["nextLine"] = field(default="nextLine", init=False)
    count: int = 1


@dataclass(frozen=True, slots=True)
class CursorPrevLine:
    type: Literal["prevLine"] = field(default="prevLine", init=False)
    count: int = 1


CursorAction = (
    CursorMove
    | CursorPosition
    | CursorColumn
    | CursorRow
    | CursorSave
    | CursorRestore
    | CursorShow
    | CursorHide
    | CursorStyleAction
    | CursorNextLine
    | CursorPrevLine
)


# =============================================================================
# Erase Actions
# =============================================================================


@dataclass(frozen=True, slots=True)
class EraseDisplay:
    type: Literal["display"] = field(default="display", init=False)
    region: Literal["toEnd", "toStart", "all", "scrollback"] = "toEnd"


@dataclass(frozen=True, slots=True)
class EraseLine:
    type: Literal["line"] = field(default="line", init=False)
    region: Literal["toEnd", "toStart", "all"] = "toEnd"


@dataclass(frozen=True, slots=True)
class EraseChars:
    type: Literal["chars"] = field(default="chars", init=False)
    count: int = 1


EraseAction = EraseDisplay | EraseLine | EraseChars


# =============================================================================
# Scroll Actions
# =============================================================================


@dataclass(frozen=True, slots=True)
class ScrollUp:
    type: Literal["up"] = field(default="up", init=False)
    count: int = 1


@dataclass(frozen=True, slots=True)
class ScrollDown:
    type: Literal["down"] = field(default="down", init=False)
    count: int = 1


@dataclass(frozen=True, slots=True)
class ScrollSetRegion:
    type: Literal["setRegion"] = field(default="setRegion", init=False)
    top: int = 1
    bottom: int = 1


ScrollAction = ScrollUp | ScrollDown | ScrollSetRegion


# =============================================================================
# Mode Actions
# =============================================================================


@dataclass(frozen=True, slots=True)
class AlternateScreenMode:
    type: Literal["alternateScreen"] = field(default="alternateScreen", init=False)
    enabled: bool = False


@dataclass(frozen=True, slots=True)
class BracketedPasteMode:
    type: Literal["bracketedPaste"] = field(default="bracketedPaste", init=False)
    enabled: bool = False


@dataclass(frozen=True, slots=True)
class MouseTrackingMode:
    type: Literal["mouseTracking"] = field(default="mouseTracking", init=False)
    mode: Literal["off", "normal", "button", "any"] = "off"


@dataclass(frozen=True, slots=True)
class FocusEventsMode:
    type: Literal["focusEvents"] = field(default="focusEvents", init=False)
    enabled: bool = False


ModeAction = AlternateScreenMode | BracketedPasteMode | MouseTrackingMode | FocusEventsMode


# =============================================================================
# Link Actions (OSC 8)
# =============================================================================


@dataclass(frozen=True, slots=True)
class LinkStart:
    type: Literal["start"] = field(default="start", init=False)
    url: str = ""
    params: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class LinkEnd:
    type: Literal["end"] = field(default="end", init=False)


LinkAction = LinkStart | LinkEnd


# =============================================================================
# Title Actions (OSC 0/1/2)
# =============================================================================


@dataclass(frozen=True, slots=True)
class WindowTitle:
    type: Literal["windowTitle"] = field(default="windowTitle", init=False)
    title: str = ""


@dataclass(frozen=True, slots=True)
class IconName:
    type: Literal["iconName"] = field(default="iconName", init=False)
    name: str = ""


@dataclass(frozen=True, slots=True)
class BothTitle:
    type: Literal["both"] = field(default="both", init=False)
    title: str = ""


TitleAction = WindowTitle | IconName | BothTitle


# =============================================================================
# Tab Status Action (OSC 21337)
# =============================================================================


@dataclass(slots=True)
class TabStatusAction:
    """Per-tab chrome metadata. Tristate for each field:
    - attribute absent → not mentioned in sequence, no change
    - None → explicitly cleared (bare key or key= with empty value)
    - value → set to this
    """

    indicator: Color | None = None
    status: str | None = None
    status_color: Color | None = None
    has_indicator: bool = False
    has_status: bool = False
    has_status_color: bool = False


# =============================================================================
# Grapheme
# =============================================================================


@dataclass(frozen=True, slots=True)
class Grapheme:
    """A grapheme (visual character unit) with width info."""

    value: str = ""
    width: Literal[1, 2] = 1


# =============================================================================
# Parsed Actions — The output of the parser
# =============================================================================


@dataclass(frozen=True, slots=True)
class TextAction:
    type: Literal["text"] = field(default="text", init=False)
    graphemes: tuple[Grapheme, ...] = ()
    style: TextStyle = field(default_factory=TextStyle)


@dataclass(frozen=True, slots=True)
class CursorActionWrapper:
    type: Literal["cursor"] = field(default="cursor", init=False)
    action: CursorAction = field(default_factory=CursorSave)


@dataclass(frozen=True, slots=True)
class EraseActionWrapper:
    type: Literal["erase"] = field(default="erase", init=False)
    action: EraseAction = field(default_factory=EraseDisplay)


@dataclass(frozen=True, slots=True)
class ScrollActionWrapper:
    type: Literal["scroll"] = field(default="scroll", init=False)
    action: ScrollAction = field(default_factory=ScrollUp)


@dataclass(frozen=True, slots=True)
class ModeActionWrapper:
    type: Literal["mode"] = field(default="mode", init=False)
    action: ModeAction = field(default_factory=lambda: AlternateScreenMode())


@dataclass(frozen=True, slots=True)
class LinkActionWrapper:
    type: Literal["link"] = field(default="link", init=False)
    action: LinkAction = field(default_factory=LinkEnd)


@dataclass(frozen=True, slots=True)
class TitleActionWrapper:
    type: Literal["title"] = field(default="title", init=False)
    action: TitleAction = field(default_factory=lambda: BothTitle())


@dataclass(frozen=True, slots=True)
class TabStatusActionWrapper:
    type: Literal["tabStatus"] = field(default="tabStatus", init=False)
    action: TabStatusAction = field(default_factory=TabStatusAction)


@dataclass(frozen=True, slots=True)
class SGRAction:
    type: Literal["sgr"] = field(default="sgr", init=False)
    params: str = ""


@dataclass(frozen=True, slots=True)
class BellAction:
    type: Literal["bell"] = field(default="bell", init=False)


@dataclass(frozen=True, slots=True)
class ResetAction:
    type: Literal["reset"] = field(default="reset", init=False)


@dataclass(frozen=True, slots=True)
class UnknownAction:
    type: Literal["unknown"] = field(default="unknown", init=False)
    sequence: str = ""


Action = (
    TextAction
    | CursorActionWrapper
    | EraseActionWrapper
    | ScrollActionWrapper
    | ModeActionWrapper
    | LinkActionWrapper
    | TitleActionWrapper
    | TabStatusActionWrapper
    | SGRAction
    | BellAction
    | ResetAction
    | UnknownAction
)
