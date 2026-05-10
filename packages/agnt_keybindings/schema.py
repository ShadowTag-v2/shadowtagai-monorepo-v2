"""
Schema constants and validation primitives for agnt_keybindings.

Ported from Claude Code keybindings/schema.ts — provides the canonical
lists of context names, action identifiers, and context descriptions.

The TypeScript original uses Zod schemas; the Python port uses plain
constants + the ``validate.py`` module for structural validation, avoiding
a runtime dependency on pydantic or any schema library.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Valid context names — mirrors KeybindingContextName in types.py
# ---------------------------------------------------------------------------

KEYBINDING_CONTEXTS: tuple[str, ...] = (
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
)

# ---------------------------------------------------------------------------
# Human-readable descriptions for each keybinding context
# ---------------------------------------------------------------------------

KEYBINDING_CONTEXT_DESCRIPTIONS: dict[str, str] = {
    "Global": "Active everywhere, regardless of focus",
    "Chat": "When the chat input is focused",
    "Autocomplete": "When autocomplete menu is visible",
    "Confirmation": "When a confirmation/permission dialog is shown",
    "Help": "When the help overlay is open",
    "Transcript": "When viewing the transcript",
    "HistorySearch": "When searching command history (ctrl+r)",
    "Task": "When a task/agent is running in the foreground",
    "ThemePicker": "When the theme picker is open",
    "Settings": "When the settings menu is open",
    "Tabs": "When tab navigation is active",
    "Attachments": "When navigating image attachments in a select dialog",
    "Footer": "When footer indicators are focused",
    "MessageSelector": "When the message selector (rewind) is open",
    "DiffDialog": "When the diff dialog is open",
    "ModelPicker": "When the model picker is open",
    "Select": "When a select/list component is focused",
    "Plugin": "When the plugin dialog is open",
    "MessageActions": "When the message actions overlay is open",
    "Scroll": "When scroll/selection mode is active",
}

# ---------------------------------------------------------------------------
# All valid keybinding action identifiers
# ---------------------------------------------------------------------------

KEYBINDING_ACTIONS: tuple[str, ...] = (
    # App-level actions (Global context)
    "app:interrupt",
    "app:exit",
    "app:toggleTodos",
    "app:toggleTranscript",
    "app:toggleBrief",
    "app:toggleTeammatePreview",
    "app:toggleTerminal",
    "app:redraw",
    "app:globalSearch",
    "app:quickOpen",
    # History navigation
    "history:search",
    "history:previous",
    "history:next",
    # Chat input actions
    "chat:cancel",
    "chat:killAgents",
    "chat:cycleMode",
    "chat:modelPicker",
    "chat:fastMode",
    "chat:thinkingToggle",
    "chat:submit",
    "chat:newline",
    "chat:undo",
    "chat:externalEditor",
    "chat:stash",
    "chat:imagePaste",
    "chat:messageActions",
    # Autocomplete menu actions
    "autocomplete:accept",
    "autocomplete:dismiss",
    "autocomplete:previous",
    "autocomplete:next",
    # Confirmation dialog actions
    "confirm:yes",
    "confirm:no",
    "confirm:previous",
    "confirm:next",
    "confirm:nextField",
    "confirm:previousField",
    "confirm:cycleMode",
    "confirm:toggle",
    "confirm:toggleExplanation",
    # Tabs navigation actions
    "tabs:next",
    "tabs:previous",
    # Transcript viewer actions
    "transcript:toggleShowAll",
    "transcript:exit",
    # History search actions
    "historySearch:next",
    "historySearch:accept",
    "historySearch:cancel",
    "historySearch:execute",
    # Task/agent actions
    "task:background",
    # Theme picker actions
    "theme:toggleSyntaxHighlighting",
    # Help menu actions
    "help:dismiss",
    # Attachment navigation
    "attachments:next",
    "attachments:previous",
    "attachments:remove",
    "attachments:exit",
    # Footer indicator actions
    "footer:up",
    "footer:down",
    "footer:next",
    "footer:previous",
    "footer:openSelected",
    "footer:clearSelection",
    "footer:close",
    # Message selector (rewind) actions
    "messageSelector:up",
    "messageSelector:down",
    "messageSelector:top",
    "messageSelector:bottom",
    "messageSelector:select",
    # Diff dialog actions
    "diff:dismiss",
    "diff:previousSource",
    "diff:nextSource",
    "diff:back",
    "diff:viewDetails",
    "diff:previousFile",
    "diff:nextFile",
    # Model picker actions
    "modelPicker:decreaseEffort",
    "modelPicker:increaseEffort",
    # Select component actions
    "select:next",
    "select:previous",
    "select:accept",
    "select:cancel",
    # Plugin dialog actions
    "plugin:toggle",
    "plugin:install",
    # Permission dialog actions
    "permission:toggleDebug",
    # Settings config panel actions
    "settings:search",
    "settings:retry",
    "settings:close",
    # Voice actions
    "voice:pushToTalk",
    # Scroll/Selection actions
    "scroll:pageUp",
    "scroll:pageDown",
    "scroll:lineUp",
    "scroll:lineDown",
    "scroll:top",
    "scroll:bottom",
    "selection:copy",
    # Message actions overlay
    "messageActions:prev",
    "messageActions:next",
    "messageActions:top",
    "messageActions:bottom",
    "messageActions:prevUser",
    "messageActions:nextUser",
    "messageActions:escape",
    "messageActions:ctrlc",
    "messageActions:enter",
    "messageActions:c",
    "messageActions:p",
)

# Pre-compiled set for O(1) lookups in validation
KEYBINDING_ACTIONS_SET: frozenset[str] = frozenset(KEYBINDING_ACTIONS)
KEYBINDING_CONTEXTS_SET: frozenset[str] = frozenset(KEYBINDING_CONTEXTS)

# ---------------------------------------------------------------------------
# Command binding regex
# ---------------------------------------------------------------------------

COMMAND_BINDING_RE: re.Pattern[str] = re.compile(r"^command:[a-zA-Z0-9:\-_]+$")
