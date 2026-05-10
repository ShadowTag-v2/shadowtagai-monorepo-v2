"""
Validation engine for the agnt_keybindings package.

Ported from Claude Code keybindings/validate.ts — validates user keybinding
configs: structure checks, parse errors, duplicate detection, reserved
shortcut checks, and JSON-level duplicate key detection.

All functions are pure — no I/O, no side-effects.
"""

from __future__ import annotations

import re

from .parser import chord_to_string, parse_chord, parse_keystroke
from .reserved_shortcuts import get_reserved_shortcuts, normalize_key_for_comparison
from .schema import COMMAND_BINDING_RE, KEYBINDING_CONTEXTS_SET
from .types import (
    KeybindingBlock,
    KeybindingWarning,
    ParsedBinding,
)

# ---------------------------------------------------------------------------
# Type guards
# ---------------------------------------------------------------------------


def _is_keybinding_block(obj: object) -> bool:
    """Check if an object is a valid KeybindingBlock-shaped dict."""
    if not isinstance(obj, dict):
        return False
    return isinstance(obj.get("context"), str) and isinstance(obj.get("bindings"), dict)


def _is_keybinding_block_list(arr: object) -> bool:
    """Check if an array contains only valid KeybindingBlock-shaped dicts."""
    return isinstance(arr, list) and all(_is_keybinding_block(item) for item in arr)


# ---------------------------------------------------------------------------
# Single keystroke validation
# ---------------------------------------------------------------------------


def _validate_keystroke(keystroke: str) -> KeybindingWarning | None:
    """Validate a single keystroke string and return any parse error."""
    parts = keystroke.lower().split("+")

    for part in parts:
        trimmed = part.strip()
        if not trimmed:
            return KeybindingWarning(
                type="parse_error",
                severity="error",
                message=f'Empty key part in "{keystroke}"',
                key=keystroke,
                suggestion='Remove extra "+" characters',
            )

    # Try to parse and see if it fails
    parsed = parse_keystroke(keystroke)
    if (
        not parsed.key
        and not parsed.ctrl
        and not parsed.alt
        and not parsed.shift
        and not parsed.meta
    ):
        return KeybindingWarning(
            type="parse_error",
            severity="error",
            message=f'Could not parse keystroke "{keystroke}"',
            key=keystroke,
        )

    return None


# ---------------------------------------------------------------------------
# Block validation
# ---------------------------------------------------------------------------


def _validate_block(
    block: object,
    block_index: int,
) -> list[KeybindingWarning]:
    """Validate a single keybinding block from user config."""
    warnings: list[KeybindingWarning] = []

    if not isinstance(block, dict):
        warnings.append(
            KeybindingWarning(
                type="parse_error",
                severity="error",
                message=f"Keybinding block {block_index + 1} is not an object",
            )
        )
        return warnings

    # Validate context
    raw_context = block.get("context")
    context_name: str | None = None

    if not isinstance(raw_context, str):
        warnings.append(
            KeybindingWarning(
                type="parse_error",
                severity="error",
                message=f'Keybinding block {block_index + 1} missing "context" field',
            )
        )
    elif raw_context not in KEYBINDING_CONTEXTS_SET:
        warnings.append(
            KeybindingWarning(
                type="invalid_context",
                severity="error",
                message=f'Unknown context "{raw_context}"',
                context=raw_context,
                suggestion=f"Valid contexts: {', '.join(sorted(KEYBINDING_CONTEXTS_SET))}",
            )
        )
    else:
        context_name = raw_context

    # Validate bindings field exists
    raw_bindings = block.get("bindings")
    if not isinstance(raw_bindings, dict):
        warnings.append(
            KeybindingWarning(
                type="parse_error",
                severity="error",
                message=f'Keybinding block {block_index + 1} missing "bindings" field',
            )
        )
        return warnings

    for key, action in raw_bindings.items():
        # Validate key syntax
        key_error = _validate_keystroke(key)
        if key_error is not None:
            key_error.context = context_name
            warnings.append(key_error)

        # Validate action
        if action is not None and not isinstance(action, str):
            warnings.append(
                KeybindingWarning(
                    type="invalid_action",
                    severity="error",
                    message=f'Invalid action for "{key}": must be a string or null',
                    key=key,
                    context=context_name,
                )
            )
        elif isinstance(action, str) and action.startswith("command:"):
            # Validate command binding format
            if not COMMAND_BINDING_RE.match(action):
                warnings.append(
                    KeybindingWarning(
                        type="invalid_action",
                        severity="warning",
                        message=(
                            f'Invalid command binding "{action}" for "{key}": '
                            "command name may only contain alphanumeric characters, "
                            "colons, hyphens, and underscores"
                        ),
                        key=key,
                        context=context_name,
                        action=action,
                    )
                )
            # Command bindings must be in Chat context
            if context_name and context_name != "Chat":
                warnings.append(
                    KeybindingWarning(
                        type="invalid_action",
                        severity="warning",
                        message=(
                            f'Command binding "{action}" must be in '
                            f'"Chat" context, not "{context_name}"'
                        ),
                        key=key,
                        context=context_name,
                        action=action,
                        suggestion='Move this binding to a block with "context": "Chat"',
                    )
                )
        elif action == "voice:pushToTalk":
            # Hold detection needs OS auto-repeat. Bare letters print into
            # the input during warmup — space or modifier combo avoids that.
            chord = parse_chord(key)
            ks = chord[0] if chord else None
            if (
                ks
                and not ks.ctrl
                and not ks.alt
                and not ks.shift
                and not ks.meta
                and not ks.super_key
                and re.match(r"^[a-z]$", ks.key)
            ):
                warnings.append(
                    KeybindingWarning(
                        type="invalid_action",
                        severity="warning",
                        message=(
                            f'Binding "{key}" to voice:pushToTalk prints into '
                            "the input during warmup; use space or a modifier "
                            "combo like meta+k"
                        ),
                        key=key,
                        context=context_name,
                        action=action,
                    )
                )

    return warnings


# ---------------------------------------------------------------------------
# JSON-level duplicate key detection
# ---------------------------------------------------------------------------


def check_duplicate_keys_in_json(json_string: str) -> list[KeybindingWarning]:
    """Detect duplicate keys within the same bindings block in a JSON string.

    JSON.parse silently uses the last value for duplicate keys, so we
    need to check the raw string to warn users.
    """
    warnings: list[KeybindingWarning] = []

    # Find each "bindings" block and check for duplicates within it
    bindings_block_re = re.compile(
        r'"bindings"\s*:\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
    )

    for block_match in bindings_block_re.finditer(json_string):
        block_content = block_match.group(1)
        if not block_content:
            continue

        # Find the context for this block by looking backwards
        text_before = json_string[: block_match.start()]
        context_match = re.search(r'"context"\s*:\s*"([^"]+)"[^{]*$', text_before)
        context = context_match.group(1) if context_match else "unknown"

        # Find all keys within this bindings block
        key_re = re.compile(r'"([^"]+)"\s*:')
        keys_by_name: dict[str, int] = {}

        for key_match in key_re.finditer(block_content):
            key = key_match.group(1)
            count = keys_by_name.get(key, 0) + 1
            keys_by_name[key] = count

            if count == 2:
                # Only warn on the second occurrence
                warnings.append(
                    KeybindingWarning(
                        type="duplicate",
                        severity="warning",
                        message=f'Duplicate key "{key}" in {context} bindings',
                        key=key,
                        context=context,
                        suggestion=(
                            "This key appears multiple times in the same context. "
                            "JSON uses the last value, earlier values are ignored."
                        ),
                    )
                )

    return warnings


# ---------------------------------------------------------------------------
# Structure validation
# ---------------------------------------------------------------------------


def validate_user_config(user_blocks: object) -> list[KeybindingWarning]:
    """Validate user keybinding config structure and return all warnings."""
    warnings: list[KeybindingWarning] = []

    if not isinstance(user_blocks, list):
        warnings.append(
            KeybindingWarning(
                type="parse_error",
                severity="error",
                message="keybindings.json must contain an array",
                suggestion="Wrap your bindings in [ ]",
            )
        )
        return warnings

    for i, block in enumerate(user_blocks):
        warnings.extend(_validate_block(block, i))

    return warnings


# ---------------------------------------------------------------------------
# Duplicate detection (semantic — normalised keys)
# ---------------------------------------------------------------------------


def check_duplicates(blocks: list[KeybindingBlock]) -> list[KeybindingWarning]:
    """Check for duplicate bindings within the same context.

    Only checks user bindings (not default + user merged).
    """
    warnings: list[KeybindingWarning] = []
    seen_by_context: dict[str, dict[str, str]] = {}

    for block in blocks:
        context_map = seen_by_context.setdefault(block.context, {})

        for key, action in block.bindings.items():
            normalized_key = normalize_key_for_comparison(key)
            existing_action = context_map.get(normalized_key)

            if existing_action is not None and existing_action != action:
                warnings.append(
                    KeybindingWarning(
                        type="duplicate",
                        severity="warning",
                        message=f'Duplicate binding "{key}" in {block.context} context',
                        key=key,
                        context=block.context,
                        action=action if action is not None else "null (unbind)",
                        suggestion=(
                            f'Previously bound to "{existing_action}". '
                            "Only the last binding will be used."
                        ),
                    )
                )

            context_map[normalized_key] = action if action is not None else "null"

    return warnings


# ---------------------------------------------------------------------------
# Reserved shortcut checks
# ---------------------------------------------------------------------------


def check_reserved_shortcuts(
    bindings: list[ParsedBinding],
) -> list[KeybindingWarning]:
    """Check for reserved shortcuts that may not work."""
    warnings: list[KeybindingWarning] = []
    reserved = get_reserved_shortcuts()

    for binding in bindings:
        key_display = chord_to_string(binding.chord)
        normalized_key = normalize_key_for_comparison(key_display)

        for res in reserved:
            if normalize_key_for_comparison(res.key) == normalized_key:
                warnings.append(
                    KeybindingWarning(
                        type="reserved",
                        severity=res.severity,
                        message=f'"{key_display}" may not work: {res.reason}',
                        key=key_display,
                        context=binding.context,
                        action=binding.action if binding.action is not None else None,
                    )
                )

    return warnings


# ---------------------------------------------------------------------------
# User bindings for validation (avoids circular import with parser)
# ---------------------------------------------------------------------------


def _get_user_bindings_for_validation(
    user_blocks: list[KeybindingBlock],
) -> list[ParsedBinding]:
    """Parse user blocks into bindings for validation."""
    bindings: list[ParsedBinding] = []
    for block in user_blocks:
        for key, action in block.bindings.items():
            chord = [parse_keystroke(k) for k in key.split()]
            bindings.append(
                ParsedBinding(
                    chord=chord,
                    action=action,
                    context=block.context,
                )
            )
    return bindings


# ---------------------------------------------------------------------------
# Combined validation — run all checks
# ---------------------------------------------------------------------------


def validate_bindings(
    user_blocks: object,
    _parsed_bindings: list[ParsedBinding],
) -> list[KeybindingWarning]:
    """Run all validations and return combined, deduplicated warnings.

    Args:
        user_blocks: The raw user config (expected to be a list of dicts).
        _parsed_bindings: The fully parsed bindings (default + user merged).
            Currently unused but reserved for future cross-binding checks.
    """
    warnings: list[KeybindingWarning] = []

    # Validate user config structure
    warnings.extend(validate_user_config(user_blocks))

    # Check for duplicates and reserved shortcuts in user config
    if _is_keybinding_block_list(user_blocks):
        typed_blocks = [
            KeybindingBlock(context=b["context"], bindings=b["bindings"])
            for b in user_blocks  # type: ignore[union-attr]
        ]
        warnings.extend(check_duplicates(typed_blocks))

        # Check reserved shortcuts — only user bindings
        user_bindings = _get_user_bindings_for_validation(typed_blocks)
        warnings.extend(check_reserved_shortcuts(user_bindings))

    # Deduplicate warnings (same key+context+type)
    seen: set[str] = set()
    deduped: list[KeybindingWarning] = []
    for w in warnings:
        dedup_key = f"{w.type}:{w.key}:{w.context}"
        if dedup_key not in seen:
            seen.add(dedup_key)
            deduped.append(w)

    return deduped


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _plural(count: int, word: str) -> str:
    """Simple English pluralisation."""
    return word if count == 1 else f"{word}s"


def format_warning(warning: KeybindingWarning) -> str:
    """Format a single warning for display to the user."""
    icon = "✗" if warning.severity == "error" else "⚠"
    msg = f"{icon} Keybinding {warning.severity}: {warning.message}"
    if warning.suggestion:
        msg += f"\n  {warning.suggestion}"
    return msg


def format_warnings(warnings: list[KeybindingWarning]) -> str:
    """Format multiple warnings for display."""
    if not warnings:
        return ""

    errors = [w for w in warnings if w.severity == "error"]
    warns = [w for w in warnings if w.severity == "warning"]
    lines: list[str] = []

    if errors:
        lines.append(f"Found {len(errors)} keybinding {_plural(len(errors), 'error')}:")
        lines.extend(format_warning(e) for e in errors)

    if warns:
        if lines:
            lines.append("")
        lines.append(f"Found {len(warns)} keybinding {_plural(len(warns), 'warning')}:")
        lines.extend(format_warning(w) for w in warns)

    return "\n".join(lines)
