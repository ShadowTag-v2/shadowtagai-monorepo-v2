"""
SGR (Select Graphic Rendition) Parser

Port of Claude Code's ink/termio/sgr.ts.
Parses SGR parameters and applies them to a TextStyle.
Handles both semicolon (;) and colon (:) separated parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .types import (
    DefaultColor,
    IndexedColor,
    NamedColorValue,
    RGBColor,
    TextStyle,
    default_style,
)

NAMED_COLORS = (
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
)

UNDERLINE_STYLES = ("none", "single", "double", "curly", "dotted", "dashed")


@dataclass
class _Param:
    value: int | None = None
    subparams: list[int] = field(default_factory=list)
    colon: bool = False


def _parse_params(s: str) -> list[_Param]:
    if s == "":
        return [_Param(value=0)]
    result: list[_Param] = []
    current = _Param()
    num = ""
    in_sub = False
    for i in range(len(s) + 1):
        c = s[i] if i < len(s) else None
        if c == ";" or c is None:
            n = None if num == "" else int(num)
            if in_sub:
                if n is not None:
                    current.subparams.append(n)
            else:
                current.value = n
            result.append(current)
            current = _Param()
            num = ""
            in_sub = False
        elif c == ":":
            n = None if num == "" else int(num)
            if not in_sub:
                current.value = n
                current.colon = True
                in_sub = True
            else:
                if n is not None:
                    current.subparams.append(n)
            num = ""
        elif "0" <= c <= "9":
            num += c
    return result


def _parse_extended_color(params: list[_Param], idx: int) -> RGBColor | IndexedColor | None:
    if idx >= len(params):
        return None
    p = params[idx]
    if p.colon and len(p.subparams) >= 1:
        if p.subparams[0] == 5 and len(p.subparams) >= 2:
            return IndexedColor(index=p.subparams[1])
        if p.subparams[0] == 2 and len(p.subparams) >= 4:
            off = 1 if len(p.subparams) >= 5 else 0
            return RGBColor(
                r=p.subparams[1 + off],
                g=p.subparams[2 + off],
                b=p.subparams[3 + off],
            )
    if idx + 1 >= len(params):
        return None
    nxt = params[idx + 1]
    if nxt.value == 5 and idx + 2 < len(params) and params[idx + 2].value is not None:
        return IndexedColor(index=params[idx + 2].value)  # type: ignore[arg-type]
    if nxt.value == 2:
        r = params[idx + 2].value if idx + 2 < len(params) else None
        g = params[idx + 3].value if idx + 3 < len(params) else None
        b = params[idx + 4].value if idx + 4 < len(params) else None
        if r is not None and g is not None and b is not None:
            return RGBColor(r=r, g=g, b=b)
    return None


def apply_sgr(param_str: str, style: TextStyle) -> TextStyle:
    """Apply SGR parameters to a TextStyle, returning a new style."""
    params = _parse_params(param_str)
    s = style.copy()
    i = 0
    while i < len(params):
        p = params[i]
        code = p.value if p.value is not None else 0
        if code == 0:
            s = default_style()
            i += 1
            continue
        if code == 1:
            s.bold = True
            i += 1
            continue
        if code == 2:
            s.dim = True
            i += 1
            continue
        if code == 3:
            s.italic = True
            i += 1
            continue
        if code == 4:
            s.underline = UNDERLINE_STYLES[p.subparams[0]] if p.colon and p.subparams and p.subparams[0] < len(UNDERLINE_STYLES) else "single"
            i += 1
            continue
        if code in (5, 6):
            s.blink = True
            i += 1
            continue
        if code == 7:
            s.inverse = True
            i += 1
            continue
        if code == 8:
            s.hidden = True
            i += 1
            continue
        if code == 9:
            s.strikethrough = True
            i += 1
            continue
        if code == 21:
            s.underline = "double"
            i += 1
            continue
        if code == 22:
            s.bold = False
            s.dim = False
            i += 1
            continue
        if code == 23:
            s.italic = False
            i += 1
            continue
        if code == 24:
            s.underline = "none"
            i += 1
            continue
        if code == 25:
            s.blink = False
            i += 1
            continue
        if code == 27:
            s.inverse = False
            i += 1
            continue
        if code == 28:
            s.hidden = False
            i += 1
            continue
        if code == 29:
            s.strikethrough = False
            i += 1
            continue
        if code == 53:
            s.overline = True
            i += 1
            continue
        if code == 55:
            s.overline = False
            i += 1
            continue
        if 30 <= code <= 37:
            s.fg = NamedColorValue(name=NAMED_COLORS[code - 30])  # type: ignore[arg-type]
            i += 1
            continue
        if code == 39:
            s.fg = DefaultColor()
            i += 1
            continue
        if 40 <= code <= 47:
            s.bg = NamedColorValue(name=NAMED_COLORS[code - 40])  # type: ignore[arg-type]
            i += 1
            continue
        if code == 49:
            s.bg = DefaultColor()
            i += 1
            continue
        if 90 <= code <= 97:
            s.fg = NamedColorValue(name=NAMED_COLORS[code - 90 + 8])  # type: ignore[arg-type]
            i += 1
            continue
        if 100 <= code <= 107:
            s.bg = NamedColorValue(name=NAMED_COLORS[code - 100 + 8])  # type: ignore[arg-type]
            i += 1
            continue
        if code == 38:
            c = _parse_extended_color(params, i)
            if c:
                s.fg = c
                i += 1 if p.colon else (3 if isinstance(c, IndexedColor) else 5)
                continue
        if code == 48:
            c = _parse_extended_color(params, i)
            if c:
                s.bg = c
                i += 1 if p.colon else (3 if isinstance(c, IndexedColor) else 5)
                continue
        if code == 58:
            c = _parse_extended_color(params, i)
            if c:
                s.underline_color = c
                i += 1 if p.colon else (3 if isinstance(c, IndexedColor) else 5)
                continue
        if code == 59:
            s.underline_color = DefaultColor()
            i += 1
            continue
        i += 1
    return s
