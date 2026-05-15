"""
Keystroke resolver for the agnt_keybindings package.

Ported from Claude Code keybindings/resolver.ts — resolves InputEvents against
parsed bindings within active contexts, supporting both single-keystroke and
multi-step chord sequences.

Pure functions — no state, no side-effects, just matching logic.
"""

from __future__ import annotations

from .match import get_key_name, matches_binding
from .parser import chord_to_string
from .types import (
    ChordCancelled,
    ChordResolveResult,
    ChordStarted,
    InputEvent,
    KeybindingContextName,
    ParsedBinding,
    ParsedKeystroke,
    ResolveMatch,
    ResolveNone,
    ResolveResult,
    ResolveUnbound,
)

# ---------------------------------------------------------------------------
# Simple resolution (single-keystroke only)
# ---------------------------------------------------------------------------


def resolve_key(
    event: InputEvent,
    active_contexts: list[KeybindingContextName],
    bindings: list[ParsedBinding],
) -> ResolveResult:
    """Resolve a key input to an action (single-keystroke bindings only).

    Args:
        event: The raw terminal input event.
        active_contexts: Currently active context names (e.g. ``["Chat", "Global"]``).
        bindings: All parsed bindings to search through.

    Returns:
        A ``ResolveMatch``, ``ResolveNone``, or ``ResolveUnbound``.
    """
    ctx_set = set(active_contexts)
    match: ParsedBinding | None = None

    for binding in bindings:
        # Phase 1: single-keystroke bindings only
        if len(binding.chord) != 1:
            continue
        if binding.context not in ctx_set:
            continue
        if matches_binding(event, binding):
            match = binding  # last one wins (user overrides)

    if match is None:
        return ResolveNone()
    if match.action is None:
        return ResolveUnbound()
    return ResolveMatch(action=match.action)


# ---------------------------------------------------------------------------
# Display-text lookup
# ---------------------------------------------------------------------------


def get_binding_display_text(
    action: str,
    context: KeybindingContextName,
    bindings: list[ParsedBinding],
) -> str | None:
    """Get the display text for an action from bindings.

    Searches in reverse order so user overrides take precedence.
    Returns ``None`` if no binding matches.
    """
    # findLast — iterate in reverse
    for binding in reversed(bindings):
        if binding.action == action and binding.context == context:
            return chord_to_string(binding.chord)
    return None


# ---------------------------------------------------------------------------
# Keystroke comparison
# ---------------------------------------------------------------------------


def keystrokes_equal(a: ParsedKeystroke, b: ParsedKeystroke) -> bool:
    """Compare two ParsedKeystrokes for equality.

    Collapses alt/meta into one logical modifier — legacy terminals
    can't distinguish them (see ``match.py _modifiers_match``), so
    ``"alt+k"`` and ``"meta+k"`` are the same key. Super (cmd/win)
    is distinct — only arrives via kitty keyboard protocol.
    """
    return (
        a.key == b.key
        and a.ctrl == b.ctrl
        and a.shift == b.shift
        and (a.alt or a.meta) == (b.alt or b.meta)
        and a.super_key == b.super_key
    )


# ---------------------------------------------------------------------------
# Chord prefix / exact matching (internal)
# ---------------------------------------------------------------------------


def _chord_prefix_matches(
    prefix: list[ParsedKeystroke],
    binding: ParsedBinding,
) -> bool:
    """Check if a chord prefix matches the beginning of a binding's chord."""
    if len(prefix) >= len(binding.chord):
        return False
    return all(
        keystrokes_equal(prefix[i], binding.chord[i]) for i in range(len(prefix))
    )


def _chord_exactly_matches(
    chord: list[ParsedKeystroke],
    binding: ParsedBinding,
) -> bool:
    """Check if a full chord matches a binding's chord exactly."""
    if len(chord) != len(binding.chord):
        return False
    return all(keystrokes_equal(chord[i], binding.chord[i]) for i in range(len(chord)))


# ---------------------------------------------------------------------------
# Build a ParsedKeystroke from an InputEvent
# ---------------------------------------------------------------------------


def _build_keystroke(event: InputEvent) -> ParsedKeystroke | None:
    """Build a ``ParsedKeystroke`` from a raw ``InputEvent``.

    QUIRK: Terminals set ``meta=True`` when escape is pressed (legacy
    terminal behaviour). We should NOT record this as a modifier for the
    escape key itself, otherwise chord matching will fail.
    """
    key_name = get_key_name(event)
    if key_name is None:
        return None

    effective_meta = False if event.escape else event.meta

    return ParsedKeystroke(
        key=key_name,
        ctrl=event.ctrl,
        alt=effective_meta,
        shift=event.shift,
        meta=effective_meta,
        super_key=event.super_key,
    )


# ---------------------------------------------------------------------------
# Full chord-state resolution
# ---------------------------------------------------------------------------


def resolve_key_with_chord_state(
    event: InputEvent,
    active_contexts: list[KeybindingContextName],
    bindings: list[ParsedBinding],
    pending: list[ParsedKeystroke] | None,
) -> ChordResolveResult:
    """Resolve a key with chord state support.

    Handles multi-keystroke chord bindings like ``"ctrl+k ctrl+s"``.

    Args:
        event: The raw terminal input event.
        active_contexts: Currently active context names.
        bindings: All parsed bindings to search through.
        pending: Current chord state (``None`` if not in a chord).

    Returns:
        A ``ChordResolveResult`` variant.
    """
    # Cancel chord on escape
    if event.escape and pending is not None:
        return ChordCancelled()

    # Build current keystroke
    current_keystroke = _build_keystroke(event)
    if current_keystroke is None:
        if pending is not None:
            return ChordCancelled()
        return ResolveNone()

    # Build the full chord sequence to test
    test_chord = [*pending, current_keystroke] if pending else [current_keystroke]

    # Filter bindings by active contexts (Set lookup: O(n) instead of O(n·m))
    ctx_set = set(active_contexts)
    context_bindings = [b for b in bindings if b.context in ctx_set]

    # Check if this could be a prefix for longer chords. Group by chord
    # string so a later null-override shadows the default it unbinds —
    # otherwise null-unbinding ``ctrl+x ctrl+k`` still makes ``ctrl+x``
    # enter chord-wait and the single-key binding on the prefix never fires.
    chord_winners: dict[str, str | None] = {}
    for binding in context_bindings:
        if len(binding.chord) > len(test_chord) and _chord_prefix_matches(
            test_chord, binding
        ):
            chord_winners[chord_to_string(binding.chord)] = binding.action

    has_longer_chords = any(a is not None for a in chord_winners.values())

    # If this keystroke could start a longer chord, prefer that
    # (even if there's an exact single-key match)
    if has_longer_chords:
        return ChordStarted(pending=test_chord)

    # Check for exact matches (last one wins)
    exact_match: ParsedBinding | None = None
    for binding in context_bindings:
        if _chord_exactly_matches(test_chord, binding):
            exact_match = binding

    if exact_match is not None:
        if exact_match.action is None:
            return ResolveUnbound()
        return ResolveMatch(action=exact_match.action)

    # No match and no potential longer chords
    if pending is not None:
        return ChordCancelled()

    return ResolveNone()
