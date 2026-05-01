"""
Keybindings template generator for the agnt_keybindings package.

Ported from Claude Code keybindings/template.ts — generates a well-documented
template file (``keybindings.json``) with all default bindings, excluding
reserved shortcuts that cannot be rebound.
"""

from __future__ import annotations

import json

from .default_bindings import DEFAULT_BINDINGS
from .reserved_shortcuts import NON_REBINDABLE, normalize_key_for_comparison
from .types import KeybindingBlock


def _filter_reserved_shortcuts(
    blocks: list[KeybindingBlock],
) -> list[KeybindingBlock]:
    """Filter out reserved shortcuts that cannot be rebound.

    These would cause ``/doctor`` to warn, so we exclude them from
    the template.
    """
    reserved_keys = {normalize_key_for_comparison(r.key) for r in NON_REBINDABLE}

    filtered: list[KeybindingBlock] = []
    for block in blocks:
        new_bindings: dict[str, str | None] = {}
        for key, action in block.bindings.items():
            if normalize_key_for_comparison(key) not in reserved_keys:
                new_bindings[key] = action
        if new_bindings:
            filtered.append(
                KeybindingBlock(context=block.context, bindings=new_bindings)
            )

    return filtered


def generate_keybindings_template() -> str:
    """Generate a template ``keybindings.json`` file content.

    Creates a fully valid JSON file with all default bindings that users
    can customize.  Reserved shortcuts (``ctrl+c``, ``ctrl+d``, ``ctrl+m``)
    are excluded.
    """
    bindings = _filter_reserved_shortcuts(DEFAULT_BINDINGS)

    config = {
        "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
        "$docs": "https://code.claude.com/docs/en/keybindings",
        "bindings": [{"context": b.context, "bindings": b.bindings} for b in bindings],
    }

    return json.dumps(config, indent=2) + "\n"
