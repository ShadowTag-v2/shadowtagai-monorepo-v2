"""
Shortcut display formatter for the agnt_keybindings package.

Ported from Claude Code keybindings/shortcutFormat.ts — provides
``get_shortcut_display()`` for non-UI contexts (commands, services, daemons).
"""

from __future__ import annotations

import logging

from .loader import load_keybindings_sync
from .resolver import get_binding_display_text
from .types import KeybindingContextName

logger = logging.getLogger(__name__)

_logged_fallbacks: set[str] = set()


def get_shortcut_display(
    action: str,
    context: KeybindingContextName,
    fallback: str,
) -> str:
    """Get the display text for a configured shortcut.

    Args:
        action: The action name (e.g. ``'app:toggleTranscript'``).
        context: The keybinding context (e.g. ``'Global'``).
        fallback: Fallback text if the binding is not found.

    Returns:
        The configured shortcut display text, or *fallback*.
    """
    bindings = load_keybindings_sync()
    resolved = get_binding_display_text(action, context, bindings)

    if resolved is None:
        key = f"{action}:{context}"
        if key not in _logged_fallbacks:
            _logged_fallbacks.add(key)
            logger.debug(
                "keybinding_fallback_used action=%s context=%s fallback=%s",
                action,
                context,
                fallback,
            )
        return fallback

    return resolved
