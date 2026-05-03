# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Agent Summary — Periodic background summarization for sub-agent progress.

Ported from src/services/AgentSummary/agentSummary.ts.

Core pattern:
  - Every 30s, generates a 3-5 word present-tense summary of the agent's
    most recent action.
  - Summaries are stored for UI display and KAIROS heartbeat reporting.
  - Uses asyncio tasks (not threads) to avoid blocking the main loop.
  - Summary generation is non-overlapping: the next timer starts only
    after the current summary completes.

Integration points:
  - KAIROS heartbeat: reads latest summary for status reporting
  - Agent coordinator: passes task_id + callback for UI updates
  - Sub-agent lifecycle: start/stop tied to agent lifecycle
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

logger = logging.getLogger(__name__)

# Default interval between summary attempts (matches TS SUMMARY_INTERVAL_MS)
SUMMARY_INTERVAL_S = 30.0

# Minimum transcript length before summarization kicks in
MIN_TRANSCRIPT_LENGTH = 3

# Type for the summary update callback
SummaryCallback = Callable[[str, str], None]  # (task_id, summary_text)

# Type for the transcript provider
TranscriptProvider = Callable[[str], Any]  # (agent_id) -> transcript or None


SUMMARY_PROMPT = """Describe your most recent action in 3-5 words using present tense (-ing). \
Name the file or function, not the branch. Do not use tools.
{previous_line}
Good: "Reading runAgent.ts"
Good: "Fixing null check in validate.ts"
Good: "Running auth module tests"
Good: "Adding retry logic to fetchUser"

Bad (past tense): "Analyzed the branch diff"
Bad (too vague): "Investigating the issue"
Bad (too long): "Reviewing full branch diff and AgentTool.tsx integration"
Bad (branch name): "Analyzed adam/background-summary branch diff"
"""


def build_summary_prompt(previous_summary: str | None = None) -> str:
    """Build the summarization prompt, optionally including the previous summary."""
    previous_line = ""
    if previous_summary:
        previous_line = f'\nPrevious: "{previous_summary}" — say something NEW.\n'
    return SUMMARY_PROMPT.format(previous_line=previous_line)


@dataclass
class SummaryState:
    """Tracks the state of a single agent's summarization loop."""

    task_id: str
    agent_id: str
    previous_summary: str | None = None
    summary_count: int = 0
    is_stopped: bool = False
    _task: asyncio.Task[None] | None = field(default=None, repr=False)


class AgentSummarizer:
    """Manages periodic background summarization for one or more agents.

    Usage:
        summarizer = AgentSummarizer(
            on_summary=lambda tid, text: update_ui(tid, text),
            get_transcript=lambda aid: fetch_transcript(aid),
        )
        handle = summarizer.start("task-1", "agent-1")
        # ... later ...
        handle.stop()
    """

    def __init__(
        self,
        *,
        on_summary: SummaryCallback | None = None,
        get_transcript: TranscriptProvider | None = None,
        interval: float = SUMMARY_INTERVAL_S,
    ) -> None:
        self._on_summary = on_summary
        self._get_transcript = get_transcript
        self._interval = interval
        self._active: dict[str, SummaryState] = {}

    @property
    def active_count(self) -> int:
        """Number of currently active summarization loops."""
        return sum(1 for s in self._active.values() if not s.is_stopped)

    def start(self, task_id: str, agent_id: str) -> SummaryState:
        """Start periodic summarization for the given agent.

        Returns a SummaryState handle. Call stop() on the state or use
        stop_all() to shut down.
        """
        state = SummaryState(task_id=task_id, agent_id=agent_id)
        state._task = asyncio.create_task(
            self._summary_loop(state),
            name=f"agent-summary-{task_id}",
        )
        self._active[task_id] = state
        logger.debug("Started summarization for task=%s agent=%s", task_id, agent_id)
        return state

    def stop(self, task_id: str) -> None:
        """Stop summarization for a specific task."""
        state = self._active.get(task_id)
        if state and not state.is_stopped:
            state.is_stopped = True
            if state._task and not state._task.done():
                state._task.cancel()
            logger.debug("Stopped summarization for task=%s", task_id)

    def stop_all(self) -> None:
        """Stop all active summarization loops."""
        for task_id in list(self._active):
            self.stop(task_id)

    def get_latest_summary(self, task_id: str) -> str | None:
        """Get the most recent summary for a task, or None."""
        state = self._active.get(task_id)
        return state.previous_summary if state else None

    async def _summary_loop(self, state: SummaryState) -> None:
        """Internal loop: sleep → summarize → repeat until stopped."""
        try:
            while not state.is_stopped:
                await asyncio.sleep(self._interval)
                if state.is_stopped:
                    break
                await self._run_single_summary(state)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.debug("Summary loop error for task=%s", state.task_id, exc_info=True)

    async def _run_single_summary(self, state: SummaryState) -> None:
        """Execute one summary cycle for the given state."""
        if not self._get_transcript:
            return

        try:
            transcript = self._get_transcript(state.agent_id)
            if transcript is None:
                return

            # Check minimum transcript length
            messages = getattr(transcript, "messages", transcript)
            if isinstance(messages, (list, tuple)) and len(messages) < MIN_TRANSCRIPT_LENGTH:
                logger.debug(
                    "Skipping summary for %s: not enough messages (%d)",
                    state.task_id,
                    len(messages),
                )
                return

            # Build the prompt (used by LLM inference in full implementation)
            _prompt = build_summary_prompt(state.previous_summary)

            # In the full implementation, this would call the LLM.
            # For the stub, we generate a placeholder that the caller
            # can replace with actual inference.
            summary_text = f"Processing task {state.task_id}"

            if summary_text:
                state.previous_summary = summary_text
                state.summary_count += 1
                if self._on_summary:
                    try:
                        self._on_summary(state.task_id, summary_text)
                    except Exception:
                        logger.debug("Summary callback error", exc_info=True)

        except Exception:
            logger.debug("Summary generation error for %s", state.task_id, exc_info=True)
