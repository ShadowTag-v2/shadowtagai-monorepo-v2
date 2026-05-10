# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tip Registry — Batch 6 port from Claude Code v2.1.91.

Contextual tip system for displaying relevant hints during spinner/wait states.
Tips are filtered by relevance criteria and cooldown sessions.

Ported from: external_repos/claude_code_services/tips/tipRegistry.ts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Tip:
  """A single contextual tip with relevance criteria."""

  id: str
  content: str
  cooldown_sessions: int = 5
  # Tags for filtering (e.g., "new-user", "power-user", "git", "mcp")
  tags: tuple[str, ...] = ()


@dataclass
class TipHistory:
  """Tracks which tips have been shown and when."""

  _shown: dict[str, int] = field(default_factory=dict)
  _session_count: int = 0

  def mark_shown(self, tip_id: str) -> None:
    """Record that a tip was shown in the current session."""
    self._shown[tip_id] = self._session_count

  def sessions_since_shown(self, tip_id: str) -> int:
    """Return sessions since a tip was last shown, or infinity if never."""
    if tip_id not in self._shown:
      return 999_999
    return self._session_count - self._shown[tip_id]

  def new_session(self) -> None:
    """Increment the session counter."""
    self._session_count += 1


# ── Built-in tip catalog ──────────────────────────────────────────────

BUILTIN_TIPS: list[Tip] = [
  Tip(
    id="plan-mode",
    content="Use Plan Mode to prepare for complex requests before making changes.",
    cooldown_sessions=5,
    tags=("workflow",),
  ),
  Tip(
    id="skills-directory",
    content="Create skills by adding .md files to .agents/skills/ for reusable capabilities.",
    cooldown_sessions=15,
    tags=("power-user",),
  ),
  Tip(
    id="subagent-fanout",
    content='Say "fan out subagents" for parallel task execution.',
    cooldown_sessions=3,
    tags=("power-user", "parallel"),
  ),
  Tip(
    id="memory-command",
    content="Use /memory to view and manage agent memory across sessions.",
    cooldown_sessions=15,
    tags=("session",),
  ),
  Tip(
    id="git-worktrees",
    content="Use git worktrees to run multiple agent sessions in parallel.",
    cooldown_sessions=10,
    tags=("git", "parallel"),
  ),
  Tip(
    id="loop-command",
    content="/loop runs any prompt on a recurring schedule. Great for monitoring.",
    cooldown_sessions=3,
    tags=("kairos", "automation"),
  ),
  Tip(
    id="todo-list",
    content="Ask the agent to create a todo list for complex tasks to track progress.",
    cooldown_sessions=20,
    tags=("workflow",),
  ),
  Tip(
    id="custom-agents",
    content="Use /agents to optimize specific tasks: Architect, Writer, Reviewer.",
    cooldown_sessions=15,
    tags=("power-user",),
  ),
  Tip(
    id="prompt-queue",
    content="Hit Enter to queue up additional messages while the agent is working.",
    cooldown_sessions=5,
    tags=("new-user",),
  ),
  Tip(
    id="resume-conversation",
    content="Run with --continue or --resume to pick up a previous conversation.",
    cooldown_sessions=10,
    tags=("session",),
  ),
]


def get_relevant_tips(
  history: TipHistory,
  tags: set[str] | None = None,
  max_tips: int = 3,
  context: dict[str, Any] | None = None,
) -> list[Tip]:
  """Get relevant tips filtered by cooldown and optional tags.

  Args:
      history: Tip display history tracker.
      tags: Optional set of tags to filter by (OR logic).
      max_tips: Maximum number of tips to return.
      context: Optional context dict for future relevance scoring.

  Returns:
      List of eligible tips, sorted by longest-unseen first.
  """
  eligible: list[tuple[int, Tip]] = []
  for tip in BUILTIN_TIPS:
    sessions_ago = history.sessions_since_shown(tip.id)
    if sessions_ago < tip.cooldown_sessions:
      continue
    if tags and not set(tip.tags) & tags:
      continue
    eligible.append((sessions_ago, tip))

  # Sort by longest unseen first
  eligible.sort(key=lambda x: -x[0])
  return [tip for _, tip in eligible[:max_tips]]
