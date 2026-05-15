"""
Keystroke matching for the agnt_keybindings package.

Ported from Claude Code keybindings/match.ts — compares raw terminal
``InputEvent`` objects against ``ParsedKeystroke`` targets, handling the
alt/meta collapse quirk and the escape-sets-meta terminal legacy.

In headless Python context, ``InputEvent`` replaces Ink's ``Key`` type.
The matching logic is identical — modifier comparison, key-name extraction
from boolean flags, and single-binding convenience matching.
"""

from __future__ import annotations

from .types import InputEvent, ParsedBinding, ParsedKeystroke

# ---------------------------------------------------------------------------
# Key-name extraction from InputEvent boolean flags
# ---------------------------------------------------------------------------


def get_key_name(event: InputEvent) -> str | None:
    """Extract the normalized key name from an ``InputEvent``.

    Maps boolean flags (``event.escape``, ``event.return_key``, etc.) to
    string names that match ``ParsedKeystroke.key`` format.
    """
    if event.escape:
        return "escape"
    if event.return_key:
        return "enter"
    if event.tab:
        return "tab"
    if event.backspace:
        return "backspace"
    if event.delete:
        return "delete"
    if event.up_arrow:
        return "up"
    if event.down_arrow:
        return "down"
    if event.left_arrow:
        return "left"
    if event.right_arrow:
        return "right"
    if event.page_up:
        return "pageup"
    if event.page_down:
        return "pagedown"
    if event.home:
        return "home"
    if event.end:
        return "end"
    if len(event.input) == 1:
        return event.input.lower()
    return None


# ---------------------------------------------------------------------------
# Modifier comparison
# ---------------------------------------------------------------------------


def _modifiers_match(event: InputEvent, target: ParsedKeystroke) -> bool:
    """Check if all modifiers match between an ``InputEvent`` and a ``ParsedKeystroke``.

    Alt and Meta: terminals historically set ``meta=True`` for Alt/Option.
    A ``meta`` modifier in config is treated as an alias for ``alt`` — both
    match when ``event.meta`` is true.

    Super (Cmd/Win): distinct from alt/meta. Only arrives via the kitty
    keyboard protocol on supporting terminals.
    """
    if event.ctrl != target.ctrl:
        return False
    if event.shift != target.shift:
        return False

    # Alt and meta both map to event.meta in terminals (terminal limitation)
    target_needs_meta = target.alt or target.meta
    if event.meta != target_needs_meta:
        return False

    # Super (cmd/win) is distinct from alt/meta
    return event.super_key == target.super_key


# ---------------------------------------------------------------------------
# Public matching API
# ---------------------------------------------------------------------------


def matches_keystroke(event: InputEvent, target: ParsedKeystroke) -> bool:
    """Check if an ``InputEvent`` matches a ``ParsedKeystroke`` target."""
    key_name = get_key_name(event)
    if key_name != target.key:
        return False

    # QUIRK: Terminals set meta=True when escape is pressed (legacy behavior
    # from how escape sequences work). Ignore the meta modifier when matching
    # the escape key itself, otherwise bindings like "escape" (without
    # modifiers) would never match.
    if event.escape:
        return _modifiers_match(
            InputEvent(
                input=event.input,
                ctrl=event.ctrl,
                shift=event.shift,
                meta=False,  # ← override
                super_key=event.super_key,
            ),
            target,
        )

    return _modifiers_match(event, target)


def matches_binding(event: InputEvent, binding: ParsedBinding) -> bool:
    """Check if an ``InputEvent`` matches a parsed binding's first keystroke.

    For single-keystroke bindings only. Multi-step chords are handled by the
    resolver module.
    """
    if len(binding.chord) != 1:
        return False
    keystroke = binding.chord[0]
    return matches_keystroke(event, keystroke)
