# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Canonical XML tag names and escape utilities for inter-agent protocol.

Ported from src/constants/xml.ts + src/utils/xml.ts (Claude Code v2.1.91).
"""

from __future__ import annotations

from typing import Final

# ── Skill / command metadata ──
COMMAND_NAME_TAG: Final[str] = "command-name"
COMMAND_MESSAGE_TAG: Final[str] = "command-message"
COMMAND_ARGS_TAG: Final[str] = "command-args"

# ── Terminal / bash output ──
BASH_INPUT_TAG: Final[str] = "bash-input"
BASH_STDOUT_TAG: Final[str] = "bash-stdout"
BASH_STDERR_TAG: Final[str] = "bash-stderr"
LOCAL_COMMAND_STDOUT_TAG: Final[str] = "local-command-stdout"
LOCAL_COMMAND_STDERR_TAG: Final[str] = "local-command-stderr"
LOCAL_COMMAND_CAVEAT_TAG: Final[str] = "local-command-caveat"

TERMINAL_OUTPUT_TAGS: Final[tuple[str, ...]] = (
    BASH_INPUT_TAG, BASH_STDOUT_TAG, BASH_STDERR_TAG,
    LOCAL_COMMAND_STDOUT_TAG, LOCAL_COMMAND_STDERR_TAG, LOCAL_COMMAND_CAVEAT_TAG,
)

TICK_TAG: Final[str] = "tick"

# ── Task notifications ──
TASK_NOTIFICATION_TAG: Final[str] = "task-notification"
TASK_ID_TAG: Final[str] = "task-id"
TOOL_USE_ID_TAG: Final[str] = "tool-use-id"
TASK_TYPE_TAG: Final[str] = "task-type"
OUTPUT_FILE_TAG: Final[str] = "output-file"
STATUS_TAG: Final[str] = "status"
SUMMARY_TAG: Final[str] = "summary"
REASON_TAG: Final[str] = "reason"
WORKTREE_TAG: Final[str] = "worktree"
WORKTREE_PATH_TAG: Final[str] = "worktreePath"
WORKTREE_BRANCH_TAG: Final[str] = "worktreeBranch"

# ── Ultraplan / remote review ──
ULTRAPLAN_TAG: Final[str] = "ultraplan"
REMOTE_REVIEW_TAG: Final[str] = "remote-review"
REMOTE_REVIEW_PROGRESS_TAG: Final[str] = "remote-review-progress"

# ── Inter-agent / swarm ──
TEAMMATE_MESSAGE_TAG: Final[str] = "teammate-message"
CHANNEL_MESSAGE_TAG: Final[str] = "channel-message"
CHANNEL_TAG: Final[str] = "channel"
CROSS_SESSION_MESSAGE_TAG: Final[str] = "cross-session-message"

# ── Fork boilerplate ──
FORK_BOILERPLATE_TAG: Final[str] = "fork-boilerplate"
FORK_DIRECTIVE_PREFIX: Final[str] = "Your directive: "

# ── Common argument patterns ──
COMMON_HELP_ARGS: Final[tuple[str, ...]] = ("help", "-h", "--help")
COMMON_INFO_ARGS: Final[tuple[str, ...]] = (
    "list", "show", "display", "current", "view", "get",
    "check", "describe", "print", "version", "about", "status", "?",
)

# ── Aggregate set for O(1) membership checks ──
ALL_TAGS: Final[frozenset[str]] = frozenset((
    COMMAND_NAME_TAG, COMMAND_MESSAGE_TAG, COMMAND_ARGS_TAG,
    *TERMINAL_OUTPUT_TAGS, TICK_TAG,
    TASK_NOTIFICATION_TAG, TASK_ID_TAG, TOOL_USE_ID_TAG, TASK_TYPE_TAG,
    OUTPUT_FILE_TAG, STATUS_TAG, SUMMARY_TAG, REASON_TAG,
    WORKTREE_TAG, WORKTREE_PATH_TAG, WORKTREE_BRANCH_TAG,
    ULTRAPLAN_TAG, REMOTE_REVIEW_TAG, REMOTE_REVIEW_PROGRESS_TAG,
    TEAMMATE_MESSAGE_TAG, CHANNEL_MESSAGE_TAG, CHANNEL_TAG,
    CROSS_SESSION_MESSAGE_TAG, FORK_BOILERPLATE_TAG,
))


# ── XML escape utilities (from src/utils/xml.ts) ──

def escape_xml(s: str) -> str:
    """Escape XML special characters for text content."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_xml_attr(s: str) -> str:
    """Escape for attribute values (quotes + standard escapes)."""
    return escape_xml(s).replace('"', "&quot;").replace("'", "&apos;")


def wrap_tag(tag: str, content: str, *, escape: bool = True) -> str:
    """Wrap content in an XML tag pair."""
    inner = escape_xml(content) if escape else content
    return f"<{tag}>{inner}</{tag}>"


def is_terminal_output_tag(tag: str) -> bool:
    """Return True if the tag indicates terminal output."""
    return tag in TERMINAL_OUTPUT_TAGS
