"""
Core types for the agnt_keybindings package.

Ported from Claude Code keybindings/types.ts — all TypeScript interfaces
become frozen dataclasses; union types become Python Literal/enum patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Parsed keystroke — canonical representation of a single key + modifiers
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ParsedKeystroke:
    """A single keystroke normalised to canonical modifier booleans.

    Modifier aliases are collapsed during parsing:
      ctrl / control → ctrl
      alt / opt / option → alt
      meta → meta  (terminal-level, same wire as alt in most emulators)
      cmd / command / super / win → super_key
      shift → shift

    The ``key`` field holds the *main* key name after alias resolution
    (e.g. ``"escape"`` not ``"esc"``, ``"enter"`` not ``"return"``).
    """

    key: str = ""
    ctrl: bool = False
    alt: bool = False
    shift: bool = False
    meta: bool = False
    super_key: bool = False  # 'super' is a Python builtin — avoid shadowing


# A chord is a sequence of keystrokes (e.g. ctrl+x ctrl+k → 2-step chord)
Chord = list[ParsedKeystroke]


# ---------------------------------------------------------------------------
# Keybinding context — execution silo names
# ---------------------------------------------------------------------------

KeybindingContextName = Literal[
    "Global",
    "Chat",
    "Autocomplete",
    "Confirmation",
    "Help",
    "Transcript",
    "HistorySearch",
    "Task",
    "ThemePicker",
    "Settings",
    "Tabs",
    "Attachments",
    "Footer",
    "MessageSelector",
    "DiffDialog",
    "ModelPicker",
    "Select",
    "Plugin",
    "MessageActions",
    "Scroll",
]


# ---------------------------------------------------------------------------
# Binding block — a context → {key: action} mapping loaded from config
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class KeybindingBlock:
    """One block of bindings scoped to a context.

    ``bindings`` maps keystroke strings (e.g. ``"ctrl+k"``) to either:
      - an action string (``"app:interrupt"``)
      - ``None`` to explicitly unbind a default shortcut
    """

    context: KeybindingContextName
    bindings: dict[str, str | None] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Parsed binding — fully resolved binding ready for matching
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class ParsedBinding:
    """A binding with its chord already parsed, ready for the resolver."""

    chord: Chord
    action: str | None
    context: KeybindingContextName


# ---------------------------------------------------------------------------
# Resolve results
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ResolveMatch:
    """A resolved action from a keystroke."""

    action: str
    type: Literal["match"] = "match"


@dataclass(frozen=True, slots=True)
class ResolveNone:
    """No binding matched the keystroke."""

    type: Literal["none"] = "none"


@dataclass(frozen=True, slots=True)
class ResolveUnbound:
    """The key was explicitly unbound (action = None)."""

    type: Literal["unbound"] = "unbound"


@dataclass(frozen=True, slots=True)
class ChordStarted:
    """A chord prefix was matched — waiting for the next keystroke."""

    pending: list[ParsedKeystroke]
    type: Literal["chord_started"] = "chord_started"


@dataclass(frozen=True, slots=True)
class ChordCancelled:
    """A pending chord was cancelled (escape or no match)."""

    type: Literal["chord_cancelled"] = "chord_cancelled"


ResolveResult = ResolveMatch | ResolveNone | ResolveUnbound
ChordResolveResult = (
    ResolveMatch | ResolveNone | ResolveUnbound | ChordStarted | ChordCancelled
)


# ---------------------------------------------------------------------------
# Reserved shortcut descriptor
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ReservedShortcut:
    """A shortcut that cannot be rebound or is intercepted by the OS/terminal."""

    key: str
    reason: str
    severity: Literal["error", "warning"]


# ---------------------------------------------------------------------------
# Validation warning
# ---------------------------------------------------------------------------

WarningType = Literal[
    "parse_error",
    "duplicate",
    "reserved",
    "invalid_context",
    "invalid_action",
]


@dataclass(slots=True)
class KeybindingWarning:
    """A validation warning or error about a keybinding configuration."""

    type: WarningType
    severity: Literal["error", "warning"]
    message: str
    key: str | None = None
    context: str | None = None
    action: str | None = None
    suggestion: str | None = None


# ---------------------------------------------------------------------------
# Input event — replaces Ink's Key type for headless Python context
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InputEvent:
    """Raw terminal input event, analogous to Ink's Key type.

    Used by match.py to compare against ParsedKeystrokes.
    Fields mirror the boolean flags that terminal input libraries produce.
    """

    # Character input (the raw character typed, if any)
    input: str = ""

    # Modifier flags
    ctrl: bool = False
    shift: bool = False
    meta: bool = False  # Alt/Option in most terminals
    super_key: bool = False  # Cmd on macOS / Win key — kitty protocol only

    # Special key flags
    escape: bool = False
    return_key: bool = False
    tab: bool = False
    backspace: bool = False
    delete: bool = False
    up_arrow: bool = False
    down_arrow: bool = False
    left_arrow: bool = False
    right_arrow: bool = False
    page_up: bool = False
    page_down: bool = False
    home: bool = False
    end: bool = False
