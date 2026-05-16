"""XML Tag Registry — core tag definitions and helpers.

Ported from Claude Code v2.1.91 constants/xml.ts.
Dependency-free module — no imports beyond Python stdlib.

These tags define the structured XML vocabulary used across the agent
system for message framing, terminal I/O classification, task status
notifications, and inter-agent communication protocols.
"""

from __future__ import annotations

import re

# =============================================================================
# COMMAND METADATA TAGS
# =============================================================================

# XML tag names used to mark skill/command metadata in messages.
COMMAND_NAME_TAG: str = "command-name"
COMMAND_MESSAGE_TAG: str = "command-message"
COMMAND_ARGS_TAG: str = "command-args"


# =============================================================================
# TERMINAL/BASH I/O TAGS
# =============================================================================

# XML tag names for terminal/bash command input and output in user messages.
# These wrap content that represents terminal activity, not actual user prompts.
BASH_INPUT_TAG: str = "bash-input"
BASH_STDOUT_TAG: str = "bash-stdout"
BASH_STDERR_TAG: str = "bash-stderr"
LOCAL_COMMAND_STDOUT_TAG: str = "local-command-stdout"
LOCAL_COMMAND_STDERR_TAG: str = "local-command-stderr"
LOCAL_COMMAND_CAVEAT_TAG: str = "local-command-caveat"

# All terminal-related tags that indicate a message is terminal output,
# not a user prompt.
TERMINAL_OUTPUT_TAGS: tuple[str, ...] = (
  BASH_INPUT_TAG,
  BASH_STDOUT_TAG,
  BASH_STDERR_TAG,
  LOCAL_COMMAND_STDOUT_TAG,
  LOCAL_COMMAND_STDERR_TAG,
  LOCAL_COMMAND_CAVEAT_TAG,
)

# Timer/heartbeat tag.
TICK_TAG: str = "tick"


# =============================================================================
# TASK NOTIFICATION TAGS
# =============================================================================

# XML tag names for task notifications (background task completions).
TASK_NOTIFICATION_TAG: str = "task-notification"
TASK_ID_TAG: str = "task-id"
TOOL_USE_ID_TAG: str = "tool-use-id"
TASK_TYPE_TAG: str = "task-type"
OUTPUT_FILE_TAG: str = "output-file"
STATUS_TAG: str = "status"
SUMMARY_TAG: str = "summary"
REASON_TAG: str = "reason"
WORKTREE_TAG: str = "worktree"
WORKTREE_PATH_TAG: str = "worktreePath"
WORKTREE_BRANCH_TAG: str = "worktreeBranch"


# =============================================================================
# PLANNING & REVIEW TAGS
# =============================================================================

# XML tag names for ultraplan mode (remote parallel planning sessions).
ULTRAPLAN_TAG: str = "ultraplan"

# XML tag name for remote /review results (teleported review session output).
# Remote session wraps its final review in this tag; local poller extracts it.
REMOTE_REVIEW_TAG: str = "remote-review"

# run_hunt.sh's heartbeat echoes the orchestrator's progress.json inside this
# tag every ~10s. Local poller parses the latest for the task-status line.
REMOTE_REVIEW_PROGRESS_TAG: str = "remote-review-progress"


# =============================================================================
# INTER-AGENT COMMUNICATION TAGS
# =============================================================================

# XML tag name for teammate messages (swarm inter-agent communication).
TEAMMATE_MESSAGE_TAG: str = "teammate-message"

# XML tag name for external channel messages.
CHANNEL_MESSAGE_TAG: str = "channel-message"
CHANNEL_TAG: str = "channel"

# XML tag name for cross-session UDS messages (another agent session's inbox).
CROSS_SESSION_MESSAGE_TAG: str = "cross-session-message"


# =============================================================================
# FORK/SUBAGENT TAGS
# =============================================================================

# XML tag wrapping the rules/format boilerplate in a fork child's first message.
# Lets the transcript renderer collapse the boilerplate and show only the directive.
FORK_BOILERPLATE_TAG: str = "fork-boilerplate"

# Prefix before the directive text, stripped by the renderer. Keep in sync
# across build_child_message (generates) and UserForkBoilerplateMessage (parses).
FORK_DIRECTIVE_PREFIX: str = "Your directive: "


# =============================================================================
# SLASH COMMAND ARGUMENT PATTERNS
# =============================================================================

# Common argument patterns for slash commands that request help.
COMMON_HELP_ARGS: tuple[str, ...] = ("help", "-h", "--help")

# Common argument patterns for slash commands that request current state/info.
COMMON_INFO_ARGS: tuple[str, ...] = (
  "list",
  "show",
  "display",
  "current",
  "view",
  "get",
  "check",
  "describe",
  "print",
  "version",
  "about",
  "status",
  "?",
)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Precompiled regex for unwrap — avoids recompilation on every call.
_UNWRAP_PATTERN_CACHE: dict[str, re.Pattern[str]] = {}


def wrap_xml_tag(tag: str, content: str) -> str:
  """Wrap content in an XML tag pair.

  Args:
      tag: The XML tag name (e.g., 'bash-stdout').
      content: The text content to wrap.

  Returns:
      String in the form ``<tag>content</tag>``.
  """
  return f"<{tag}>{content}</{tag}>"


def unwrap_xml_tag(tag: str, text: str) -> str | None:
  """Extract content from within an XML tag pair.

  Args:
      tag: The XML tag name to look for.
      text: The text potentially containing the wrapped content.

  Returns:
      The inner content if found, or None if the tag is not present.
  """
  if tag not in _UNWRAP_PATTERN_CACHE:
    _UNWRAP_PATTERN_CACHE[tag] = re.compile(
      rf"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>",
      re.DOTALL,
    )
  match = _UNWRAP_PATTERN_CACHE[tag].search(text)
  return match.group(1) if match else None


def is_terminal_output_tag(tag: str) -> bool:
  """Check if a tag name indicates terminal output (not user prompt).

  Args:
      tag: The XML tag name to check.

  Returns:
      True if the tag is in TERMINAL_OUTPUT_TAGS.
  """
  return tag in TERMINAL_OUTPUT_TAGS
