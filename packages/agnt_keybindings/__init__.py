"""
agnt_keybindings — Headless keybinding management for Antigravity agents.

Ported from Claude Code keybindings/ (TypeScript) to pure Python 3.14.
Provides keystroke parsing, chord matching, binding resolution, validation,
user-config loading, and hot-reload for daemon/agent contexts.

Usage::

    from agnt_keybindings import (
        DEFAULT_BINDINGS,
        load_keybindings_sync,
        resolve_key,
    )

    bindings = load_keybindings_sync()
    result = resolve_key(event, active_contexts=["Chat", "Global"], bindings=bindings)
"""

from __future__ import annotations

# Default bindings
from .default_bindings import DEFAULT_BINDINGS, ENABLED_FEATURES, get_default_bindings

# Loader
from .loader import (
    KeybindingsLoadResult,
    dispose_keybinding_watcher,
    get_cached_keybinding_warnings,
    get_keybindings_path,
    initialize_keybinding_watcher,
    is_keybinding_customization_enabled,
    load_keybindings,
    load_keybindings_sync,
    load_keybindings_sync_with_warnings,
    reset_keybinding_loader_for_testing,
    subscribe_to_keybinding_changes,
)

# Matching
from .match import matches_keystroke

# Parser
from .parser import (
    chord_to_string,
    keystroke_to_display_string,
    parse_bindings,
    parse_chord,
    parse_keystroke,
)

# Reserved shortcuts
from .reserved_shortcuts import (
    NON_REBINDABLE,
    get_reserved_shortcuts,
    normalize_key_for_comparison,
)

# Resolver
from .resolver import (
    get_binding_display_text,
    keystrokes_equal,
    resolve_key,
    resolve_key_with_chord_state,
)

# Schema constants
from .schema import (
    KEYBINDING_ACTIONS,
    KEYBINDING_ACTIONS_SET,
    KEYBINDING_CONTEXT_DESCRIPTIONS,
    KEYBINDING_CONTEXTS,
    KEYBINDING_CONTEXTS_SET,
)

# Shortcut format
from .shortcut_format import get_shortcut_display

# Template
from .template import generate_keybindings_template

# --- Public API surface ---
# Types
from .types import (
    ChordCancelled,
    ChordResolveResult,
    ChordStarted,
    InputEvent,
    KeybindingBlock,
    KeybindingWarning,
    ParsedBinding,
    ParsedKeystroke,
    ReservedShortcut,
    ResolveMatch,
    ResolveNone,
    ResolveResult,
    ResolveUnbound,
)

# Validation
from .validate import (
    check_duplicate_keys_in_json,
    validate_bindings,
)

__all__ = [
    # Types
    "ChordCancelled",
    "ChordResolveResult",
    "ChordStarted",
    "InputEvent",
    "KeybindingBlock",
    "KeybindingWarning",
    "KeybindingsLoadResult",
    "ParsedBinding",
    "ParsedKeystroke",
    "ResolveMatch",
    "ResolveNone",
    "ResolveResult",
    "ResolveUnbound",
    "ReservedShortcut",
    # Constants
    "DEFAULT_BINDINGS",
    "ENABLED_FEATURES",
    "KEYBINDING_ACTIONS",
    "KEYBINDING_ACTIONS_SET",
    "KEYBINDING_CONTEXTS",
    "KEYBINDING_CONTEXTS_SET",
    "KEYBINDING_CONTEXT_DESCRIPTIONS",
    "NON_REBINDABLE",
    # Functions
    "check_duplicate_keys_in_json",
    "chord_to_string",
    "dispose_keybinding_watcher",
    "generate_keybindings_template",
    "get_cached_keybinding_warnings",
    "get_default_bindings",
    "get_keybindings_path",
    "get_reserved_shortcuts",
    "normalize_key_for_comparison",
    "get_shortcut_display",
    "initialize_keybinding_watcher",
    "is_keybinding_customization_enabled",
    "keystroke_to_display_string",
    "load_keybindings",
    "load_keybindings_sync",
    "load_keybindings_sync_with_warnings",
    "matches_keystroke",
    "parse_bindings",
    "parse_chord",
    "parse_keystroke",
    "reset_keybinding_loader_for_testing",
    "subscribe_to_keybinding_changes",
    "validate_bindings",
    # Classes / Resolver
    "get_binding_display_text",
    "keystrokes_equal",
    "resolve_key",
    "resolve_key_with_chord_state",
]
