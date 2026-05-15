"""
Keystroke parser for the agnt_keybindings package.

Ported from Claude Code keybindings/parser.ts — parses keystroke strings
(``"ctrl+shift+k"``) into ``ParsedKeystroke`` objects, handles chords
(space-separated multi-step bindings), and provides display-string generation.

Zero external dependencies — pure Python 3.14.
"""

from __future__ import annotations

from typing import Literal

from .types import Chord, KeybindingBlock, ParsedBinding, ParsedKeystroke

# ---------------------------------------------------------------------------
# Display platform type
# ---------------------------------------------------------------------------

DisplayPlatform = Literal["macos", "windows", "linux", "wsl", "unknown"]

# ---------------------------------------------------------------------------
# Key alias maps (readonly after module init)
# ---------------------------------------------------------------------------

_KEY_ALIASES: dict[str, str] = {
    "esc": "escape",
    "return": "enter",
    "space": " ",
    "↑": "up",
    "↓": "down",
    "←": "left",
    "→": "right",
}

_DISPLAY_NAMES: dict[str, str] = {
    "escape": "Esc",
    " ": "Space",
    "tab": "tab",
    "enter": "Enter",
    "backspace": "Backspace",
    "delete": "Delete",
    "up": "↑",
    "down": "↓",
    "left": "←",
    "right": "→",
    "pageup": "PageUp",
    "pagedown": "PageDown",
    "home": "Home",
    "end": "End",
}


# ---------------------------------------------------------------------------
# Core parsing
# ---------------------------------------------------------------------------


def parse_keystroke(raw: str) -> ParsedKeystroke:
    """Parse a keystroke string like ``"ctrl+shift+k"`` into a ``ParsedKeystroke``.

    Supports modifier aliases:
      ctrl / control → ctrl
      alt / opt / option → alt
      meta → meta
      cmd / command / super / win → super_key
      shift → shift
    """
    ctrl = alt = shift = meta = super_key = False
    key = ""

    for part in raw.split("+"):
        lower = part.lower()
        if lower in ("ctrl", "control"):
            ctrl = True
        elif lower in ("alt", "opt", "option"):
            alt = True
        elif lower == "shift":
            shift = True
        elif lower == "meta":
            meta = True
        elif lower in ("cmd", "command", "super", "win"):
            super_key = True
        elif lower in _KEY_ALIASES:
            key = _KEY_ALIASES[lower]
        else:
            key = lower

    return ParsedKeystroke(
        key=key, ctrl=ctrl, alt=alt, shift=shift, meta=meta, super_key=super_key
    )


def parse_chord(raw: str) -> Chord:
    """Parse a chord string like ``"ctrl+k ctrl+s"`` into a list of keystrokes.

    A lone space character IS the space key binding, not a separator.
    """
    if raw == " ":
        return [parse_keystroke("space")]
    return [parse_keystroke(step) for step in raw.strip().split()]


# ---------------------------------------------------------------------------
# Display string generation
# ---------------------------------------------------------------------------


def _key_to_display_name(key: str) -> str:
    """Map internal key names to human-readable display names."""
    return _DISPLAY_NAMES.get(key, key)


def keystroke_to_string(ks: ParsedKeystroke) -> str:
    """Convert a ``ParsedKeystroke`` to its canonical string representation."""
    parts: list[str] = []
    if ks.ctrl:
        parts.append("ctrl")
    if ks.alt:
        parts.append("alt")
    if ks.shift:
        parts.append("shift")
    if ks.meta:
        parts.append("meta")
    if ks.super_key:
        parts.append("cmd")
    parts.append(_key_to_display_name(ks.key))
    return "+".join(parts)


def chord_to_string(chord: Chord) -> str:
    """Convert a ``Chord`` to its canonical string representation."""
    return " ".join(keystroke_to_string(ks) for ks in chord)


def keystroke_to_display_string(
    ks: ParsedKeystroke,
    platform: DisplayPlatform = "linux",
) -> str:
    """Convert a ``ParsedKeystroke`` to a platform-appropriate display string.

    Uses ``"opt"`` for alt on macOS, ``"alt"`` elsewhere.
    """
    parts: list[str] = []
    if ks.ctrl:
        parts.append("ctrl")
    # Alt and meta are equivalent in terminals — show platform-appropriate name
    if ks.alt or ks.meta:
        parts.append("opt" if platform == "macos" else "alt")
    if ks.shift:
        parts.append("shift")
    if ks.super_key:
        parts.append("cmd" if platform == "macos" else "super")
    parts.append(_key_to_display_name(ks.key))
    return "+".join(parts)


def chord_to_display_string(
    chord: Chord,
    platform: DisplayPlatform = "linux",
) -> str:
    """Convert a ``Chord`` to a platform-appropriate display string."""
    return " ".join(keystroke_to_display_string(ks, platform) for ks in chord)


# ---------------------------------------------------------------------------
# Block parsing — config → flat list of ParsedBindings
# ---------------------------------------------------------------------------


def parse_bindings(blocks: list[KeybindingBlock]) -> list[ParsedBinding]:
    """Parse keybinding blocks (from JSON config) into a flat list of parsed bindings."""
    bindings: list[ParsedBinding] = []
    for block in blocks:
        for key, action in block.bindings.items():
            bindings.append(
                ParsedBinding(
                    chord=parse_chord(key),
                    action=action,
                    context=block.context,
                )
            )
    return bindings
