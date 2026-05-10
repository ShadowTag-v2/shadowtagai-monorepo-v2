"""
Reserved shortcut guards for the agnt_keybindings package.

Ported from Claude Code keybindings/reservedShortcuts.ts — defines shortcuts
that cannot be rebound (OS/terminal intercepts) and provides a normalization
function for key comparison.

Headless Doctrine Alignment:
  These guards ensure that ctrl+c, ctrl+d, ctrl+z, and ctrl+\\ always reach
  the process signal layer, preventing user configuration from trapping
  the Antigravity daemon or agent loop.
"""

from __future__ import annotations

import sys

from .types import ReservedShortcut

# ---------------------------------------------------------------------------
# Non-rebindable shortcuts — hardcoded in the engine
# ---------------------------------------------------------------------------

NON_REBINDABLE: list[ReservedShortcut] = [
    ReservedShortcut(
        key="ctrl+c",
        reason="Cannot be rebound — used for interrupt/exit (hardcoded)",
        severity="error",
    ),
    ReservedShortcut(
        key="ctrl+d",
        reason="Cannot be rebound — used for exit (hardcoded)",
        severity="error",
    ),
    ReservedShortcut(
        key="ctrl+m",
        reason=("Cannot be rebound — identical to Enter in terminals (both send CR)"),
        severity="error",
    ),
]

# ---------------------------------------------------------------------------
# Terminal control shortcuts intercepted by the terminal / OS
# ---------------------------------------------------------------------------

TERMINAL_RESERVED: list[ReservedShortcut] = [
    ReservedShortcut(
        key="ctrl+z",
        reason="Unix process suspend (SIGTSTP)",
        severity="warning",
    ),
    ReservedShortcut(
        key="ctrl+\\",
        reason="Terminal quit signal (SIGQUIT)",
        severity="error",
    ),
]

# ---------------------------------------------------------------------------
# macOS-specific shortcuts the OS intercepts
# ---------------------------------------------------------------------------

MACOS_RESERVED: list[ReservedShortcut] = [
    ReservedShortcut(key="cmd+c", reason="macOS system copy", severity="error"),
    ReservedShortcut(key="cmd+v", reason="macOS system paste", severity="error"),
    ReservedShortcut(key="cmd+x", reason="macOS system cut", severity="error"),
    ReservedShortcut(key="cmd+q", reason="macOS quit application", severity="error"),
    ReservedShortcut(key="cmd+w", reason="macOS close window/tab", severity="error"),
    ReservedShortcut(key="cmd+tab", reason="macOS app switcher", severity="error"),
    ReservedShortcut(key="cmd+space", reason="macOS Spotlight", severity="error"),
]


# ---------------------------------------------------------------------------
# Platform detection (pure Python — no external deps)
# ---------------------------------------------------------------------------


def _get_platform() -> str:
    """Return the platform slug: 'macos', 'windows', or 'linux'."""
    if sys.platform == "darwin":
        return "macos"
    if sys.platform == "win32":
        return "windows"
    return "linux"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_reserved_shortcuts() -> list[ReservedShortcut]:
    """Get all reserved shortcuts for the current platform.

    Returns non-rebindable shortcuts first (highest priority), then
    terminal-reserved shortcuts, then platform-specific shortcuts.
    """
    reserved = [*NON_REBINDABLE, *TERMINAL_RESERVED]
    if _get_platform() == "macos":
        reserved.extend(MACOS_RESERVED)
    return reserved


def normalize_key_for_comparison(key: str) -> str:
    """Normalize a key string for comparison (lowercase, sorted modifiers).

    Chords (space-separated steps like ``"ctrl+x ctrl+b"``) are normalized
    per-step to avoid mangling multi-step bindings.
    """
    return " ".join(_normalize_step(step) for step in key.strip().split())


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_MODIFIER_ALIASES: dict[str, str] = {
    "control": "ctrl",
    "option": "alt",
    "opt": "alt",
    "command": "cmd",
}

_MODIFIER_NAMES = frozenset(
    {
        "ctrl",
        "control",
        "alt",
        "opt",
        "option",
        "meta",
        "cmd",
        "command",
        "shift",
    }
)


def _normalize_step(step: str) -> str:
    """Normalize a single keystroke step (e.g. ``"Ctrl+K"`` → ``"ctrl+k"``)."""
    parts = step.split("+")
    modifiers: list[str] = []
    main_key = ""

    for part in parts:
        lower = part.strip().lower()
        if lower in _MODIFIER_NAMES:
            modifiers.append(_MODIFIER_ALIASES.get(lower, lower))
        else:
            main_key = lower

    modifiers.sort()
    return "+".join([*modifiers, main_key])
