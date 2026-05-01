"""
Default keybinding definitions for the agnt_keybindings package.

Ported from Claude Code keybindings/defaultBindings.ts — provides the
canonical set of keybinding blocks that ship as built-in defaults.

Platform-specific keys are resolved at import time via ``sys.platform``.
Feature flags (GrowthBook ``feature()`` in the TS source) are replaced with
a simple ``ENABLED_FEATURES`` set that the host application can configure
before loading this module.
"""

from __future__ import annotations

import sys

from .types import KeybindingBlock

# ---------------------------------------------------------------------------
# Feature flag registry — host app populates before first access
# ---------------------------------------------------------------------------

ENABLED_FEATURES: set[str] = set()
"""Feature flags that mirror the TypeScript ``feature()`` guard.

Populate this set before accessing ``DEFAULT_BINDINGS`` to activate
gated binding blocks (e.g. ``ENABLED_FEATURES.add("KAIROS")``).
"""


def _has_feature(name: str) -> bool:
    """Check whether a feature flag is enabled."""
    return name in ENABLED_FEATURES


# ---------------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------------


def _get_platform() -> str:
    """Return 'macos', 'windows', or 'linux'."""
    if sys.platform == "darwin":
        return "macos"
    if sys.platform == "win32":
        return "windows"
    return "linux"


# Platform-specific image paste shortcut:
# - Windows: alt+v (ctrl+v is system paste)
# - Other platforms: ctrl+v
def _image_paste_key() -> str:
    return "alt+v" if _get_platform() == "windows" else "ctrl+v"


# Platform-specific mode cycle shortcut:
# - Windows without VT mode: meta+m (shift+tab doesn't work reliably)
# - Other platforms: shift+tab
# In headless Python (daemon/agent), we always support VT mode.
def _mode_cycle_key() -> str:
    return "shift+tab"


# ---------------------------------------------------------------------------
# Default binding definitions
# ---------------------------------------------------------------------------


def get_default_bindings() -> list[KeybindingBlock]:
    """Build and return the default keybinding blocks.

    This is a function (not a module-level constant) so that feature-flag
    and platform detection happens at call-time, not import-time.
    """
    image_paste = _image_paste_key()
    mode_cycle = _mode_cycle_key()

    blocks: list[KeybindingBlock] = []

    # -- Global context ---------------------------------------------------
    global_bindings: dict[str, str | None] = {
        "ctrl+c": "app:interrupt",
        "ctrl+d": "app:exit",
        "ctrl+l": "app:redraw",
        "ctrl+t": "app:toggleTodos",
        "ctrl+o": "app:toggleTranscript",
        "ctrl+shift+o": "app:toggleTeammatePreview",
        "ctrl+r": "history:search",
    }
    if _has_feature("KAIROS") or _has_feature("KAIROS_BRIEF"):
        global_bindings["ctrl+shift+b"] = "app:toggleBrief"
    if _has_feature("QUICK_SEARCH"):
        global_bindings["ctrl+shift+f"] = "app:globalSearch"
        global_bindings["cmd+shift+f"] = "app:globalSearch"
        global_bindings["ctrl+shift+p"] = "app:quickOpen"
        global_bindings["cmd+shift+p"] = "app:quickOpen"
    if _has_feature("TERMINAL_PANEL"):
        global_bindings["meta+j"] = "app:toggleTerminal"

    blocks.append(KeybindingBlock(context="Global", bindings=global_bindings))

    # -- Chat context -----------------------------------------------------
    chat_bindings: dict[str, str | None] = {
        "escape": "chat:cancel",
        "ctrl+x ctrl+k": "chat:killAgents",
        mode_cycle: "chat:cycleMode",
        "meta+p": "chat:modelPicker",
        "meta+o": "chat:fastMode",
        "meta+t": "chat:thinkingToggle",
        "enter": "chat:submit",
        "up": "history:previous",
        "down": "history:next",
        "ctrl+_": "chat:undo",
        "ctrl+shift+-": "chat:undo",
        "ctrl+x ctrl+e": "chat:externalEditor",
        "ctrl+g": "chat:externalEditor",
        "ctrl+s": "chat:stash",
        image_paste: "chat:imagePaste",
    }
    if _has_feature("MESSAGE_ACTIONS"):
        chat_bindings["shift+up"] = "chat:messageActions"
    if _has_feature("VOICE_MODE"):
        chat_bindings["space"] = "voice:pushToTalk"

    blocks.append(KeybindingBlock(context="Chat", bindings=chat_bindings))

    # -- Autocomplete context ---------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Autocomplete",
            bindings={
                "tab": "autocomplete:accept",
                "escape": "autocomplete:dismiss",
                "up": "autocomplete:previous",
                "down": "autocomplete:next",
            },
        )
    )

    # -- Settings context -------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Settings",
            bindings={
                "escape": "confirm:no",
                "up": "select:previous",
                "down": "select:next",
                "k": "select:previous",
                "j": "select:next",
                "ctrl+p": "select:previous",
                "ctrl+n": "select:next",
                "space": "select:accept",
                "enter": "settings:close",
                "/": "settings:search",
                "r": "settings:retry",
            },
        )
    )

    # -- Confirmation context ---------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Confirmation",
            bindings={
                "y": "confirm:yes",
                "n": "confirm:no",
                "enter": "confirm:yes",
                "escape": "confirm:no",
                "up": "confirm:previous",
                "down": "confirm:next",
                "tab": "confirm:nextField",
                "space": "confirm:toggle",
                "shift+tab": "confirm:cycleMode",
                "ctrl+e": "confirm:toggleExplanation",
                "ctrl+d": "permission:toggleDebug",
            },
        )
    )

    # -- Tabs context -----------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Tabs",
            bindings={
                "tab": "tabs:next",
                "shift+tab": "tabs:previous",
                "right": "tabs:next",
                "left": "tabs:previous",
            },
        )
    )

    # -- Transcript context -----------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Transcript",
            bindings={
                "ctrl+e": "transcript:toggleShowAll",
                "ctrl+c": "transcript:exit",
                "escape": "transcript:exit",
                "q": "transcript:exit",
            },
        )
    )

    # -- HistorySearch context --------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="HistorySearch",
            bindings={
                "ctrl+r": "historySearch:next",
                "escape": "historySearch:accept",
                "tab": "historySearch:accept",
                "ctrl+c": "historySearch:cancel",
                "enter": "historySearch:execute",
            },
        )
    )

    # -- Task context -----------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Task",
            bindings={"ctrl+b": "task:background"},
        )
    )

    # -- ThemePicker context ----------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="ThemePicker",
            bindings={"ctrl+t": "theme:toggleSyntaxHighlighting"},
        )
    )

    # -- Scroll context ---------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Scroll",
            bindings={
                "pageup": "scroll:pageUp",
                "pagedown": "scroll:pageDown",
                "wheelup": "scroll:lineUp",
                "wheeldown": "scroll:lineDown",
                "ctrl+home": "scroll:top",
                "ctrl+end": "scroll:bottom",
                "ctrl+shift+c": "selection:copy",
                "cmd+c": "selection:copy",
            },
        )
    )

    # -- Help context -----------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Help",
            bindings={"escape": "help:dismiss"},
        )
    )

    # -- Attachments context ----------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Attachments",
            bindings={
                "right": "attachments:next",
                "left": "attachments:previous",
                "backspace": "attachments:remove",
                "delete": "attachments:remove",
                "down": "attachments:exit",
                "escape": "attachments:exit",
            },
        )
    )

    # -- Footer context ---------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Footer",
            bindings={
                "up": "footer:up",
                "ctrl+p": "footer:up",
                "down": "footer:down",
                "ctrl+n": "footer:down",
                "right": "footer:next",
                "left": "footer:previous",
                "enter": "footer:openSelected",
                "escape": "footer:clearSelection",
            },
        )
    )

    # -- MessageSelector context ------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="MessageSelector",
            bindings={
                "up": "messageSelector:up",
                "down": "messageSelector:down",
                "k": "messageSelector:up",
                "j": "messageSelector:down",
                "ctrl+p": "messageSelector:up",
                "ctrl+n": "messageSelector:down",
                "ctrl+up": "messageSelector:top",
                "shift+up": "messageSelector:top",
                "meta+up": "messageSelector:top",
                "shift+k": "messageSelector:top",
                "ctrl+down": "messageSelector:bottom",
                "shift+down": "messageSelector:bottom",
                "meta+down": "messageSelector:bottom",
                "shift+j": "messageSelector:bottom",
                "enter": "messageSelector:select",
            },
        )
    )

    # -- MessageActions context (feature-gated) ---------------------------
    if _has_feature("MESSAGE_ACTIONS"):
        blocks.append(
            KeybindingBlock(
                context="MessageActions",
                bindings={
                    "up": "messageActions:prev",
                    "down": "messageActions:next",
                    "k": "messageActions:prev",
                    "j": "messageActions:next",
                    "meta+up": "messageActions:top",
                    "meta+down": "messageActions:bottom",
                    "super+up": "messageActions:top",
                    "super+down": "messageActions:bottom",
                    "shift+up": "messageActions:prevUser",
                    "shift+down": "messageActions:nextUser",
                    "escape": "messageActions:escape",
                    "ctrl+c": "messageActions:ctrlc",
                    "enter": "messageActions:enter",
                    "c": "messageActions:c",
                    "p": "messageActions:p",
                },
            )
        )

    # -- DiffDialog context -----------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="DiffDialog",
            bindings={
                "escape": "diff:dismiss",
                "left": "diff:previousSource",
                "right": "diff:nextSource",
                "up": "diff:previousFile",
                "down": "diff:nextFile",
                "enter": "diff:viewDetails",
            },
        )
    )

    # -- ModelPicker context ----------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="ModelPicker",
            bindings={
                "left": "modelPicker:decreaseEffort",
                "right": "modelPicker:increaseEffort",
            },
        )
    )

    # -- Select context ---------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Select",
            bindings={
                "up": "select:previous",
                "down": "select:next",
                "j": "select:next",
                "k": "select:previous",
                "ctrl+n": "select:next",
                "ctrl+p": "select:previous",
                "enter": "select:accept",
                "escape": "select:cancel",
            },
        )
    )

    # -- Plugin context ---------------------------------------------------
    blocks.append(
        KeybindingBlock(
            context="Plugin",
            bindings={
                "space": "plugin:toggle",
                "i": "plugin:install",
            },
        )
    )

    return blocks


# Module-level convenience — lazily evaluated on first access
DEFAULT_BINDINGS: list[KeybindingBlock] = get_default_bindings()
