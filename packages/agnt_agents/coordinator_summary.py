"""Agent coordinator summary — periodic background summarization.

Ported from Claude Code `AgentSummary/agentSummary.ts`.
Generates concise 3-5 word present-tense progress summaries for
sub-agents in coordinator mode.

Architecture:
  - `AgentSummarizer` → timer-based periodic summarization
  - `build_summary_prompt()` → prompt template for progress updates
  - `SummaryResult` → structured summary output
  - Integrates with daemon fleet for KAIROS agent status reporting

Design:
  Claude Code's implementation forks the sub-agent's conversation every
  ~30s using `runForkedAgent()` to generate summaries. Our port uses an
  asyncio-based timer that invokes a callback for model queries, keeping
  the actual model interaction decoupled from the summarization logic.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Protocol

logger = logging.getLogger(__name__)

# --- Constants ---

DEFAULT_SUMMARY_INTERVAL_SECONDS = 30


class SummaryCallback(Protocol):
    """Protocol for summary generation callbacks.

    Implementors should query a lightweight model with the provided
    prompt and return the text response.
    """

    async def __call__(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str | None: ...


@dataclass
class SummaryResult:
    """Result of a summary generation attempt.

    Attributes:
        text: The generated summary text.
        timestamp: When the summary was generated.
        message_count: Number of messages in context when generated.
        agent_id: ID of the agent being summarized.
    """

    text: str
    timestamp: float
    message_count: int
    agent_id: str


@dataclass
class AgentContext:
    """Snapshot of an agent's current state for summarization.

    Attributes:
        agent_id: Unique identifier for the agent.
        messages: Current conversation messages (simplified).
        task_id: Task this agent is working on.
    """

    agent_id: str
    messages: list[dict[str, Any]]
    task_id: str = ""


def build_summary_prompt(previous_summary: str | None = None) -> str:
    """Build the user prompt for summary generation.

    Produces a prompt that instructs the model to generate a concise
    3-5 word present-tense description of the agent's most recent action.

    Args:
        previous_summary: Previous summary to avoid repetition.

    Returns:
        User prompt string.
    """
    prev_line = ""
    if previous_summary:
        prev_line = f'\nPrevious: "{previous_summary}" — say something NEW.\n'

    return f"""Describe your most recent action in 3-5 words using present tense (-ing). \
Name the file or function, not the branch. Do not use tools.
{prev_line}
Good: "Reading runAgent.ts"
Good: "Fixing null check in validate.ts"
Good: "Running auth module tests"
Good: "Adding retry logic to fetchUser"

Bad (past tense): "Analyzed the branch diff"
Bad (too vague): "Investigating the issue"
Bad (too long): "Reviewing full branch diff and AgentTool.tsx integration"
Bad (branch name): "Analyzed adam/background-summary branch diff\""""


SUMMARY_SYSTEM_PROMPT = (
    "You are a progress reporter. Generate a very brief status update "
    "for an AI coding agent's current activity. Respond ONLY with the "
    "summary text, nothing else."
)


class AgentSummarizer:
    """Periodic background summarizer for coordinator sub-agents.

    Runs a timer that fires every `interval_seconds` to generate
    a brief progress summary of what the agent is currently doing.

    Usage::

        summarizer = AgentSummarizer(
            agent_id="agent-1",
            callback=my_model_query,
        )
        summarizer.start()
        # ... agent runs ...
        latest = summarizer.latest_summary
        summarizer.stop()

    Attributes:
        agent_id: ID of the agent being summarized.
        interval_seconds: Seconds between summary attempts.
        latest_summary: Most recent summary result, or None.
    """

    def __init__(
        self,
        agent_id: str,
        callback: SummaryCallback,
        interval_seconds: float = DEFAULT_SUMMARY_INTERVAL_SECONDS,
        min_messages: int = 3,
    ) -> None:
        """Initialize the summarizer.

        Args:
            agent_id: ID of the agent to summarize.
            callback: Async function to query a model for summaries.
            interval_seconds: Seconds between summary attempts.
            min_messages: Minimum messages required before summarizing.
        """
        self.agent_id = agent_id
        self._callback = callback
        self.interval_seconds = interval_seconds
        self._min_messages = min_messages
        self._previous_summary: str | None = None
        self._stopped = False
        self._task: asyncio.Task[None] | None = None
        self._message_provider: MessageProvider | None = None
        self.latest_summary: SummaryResult | None = None
        self.summary_history: list[SummaryResult] = []

    def set_message_provider(self, provider: MessageProvider) -> None:
        """Set the message provider for accessing agent transcript.

        Args:
            provider: Callable that returns current messages for the agent.
        """
        self._message_provider = provider

    def start(self) -> None:
        """Start the periodic summarization timer.

        Creates an asyncio task that runs the summarization loop.
        """
        if self._task is not None:
            logger.warning("AgentSummarizer already started for %s", self.agent_id)
            return

        self._stopped = False
        self._task = asyncio.ensure_future(self._run_loop())
        logger.debug("AgentSummarizer started for %s", self.agent_id)

    def stop(self) -> None:
        """Stop the periodic summarization timer."""
        logger.debug("AgentSummarizer stopping for %s", self.agent_id)
        self._stopped = True
        if self._task is not None:
            self._task.cancel()
            self._task = None

    async def _run_loop(self) -> None:
        """Internal loop that runs summaries on a timer."""
        while not self._stopped:
            try:
                await asyncio.sleep(self.interval_seconds)
                if self._stopped:
                    break
                await self._run_summary()
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in summarization loop for %s", self.agent_id)
                if not self._stopped:
                    # Continue loop on error
                    continue

    async def _run_summary(self) -> None:
        """Execute a single summary generation cycle."""
        # Get current messages
        messages = await self._get_messages()
        if messages is None or len(messages) < self._min_messages:
            logger.debug(
                "Skipping summary for %s: not enough messages (%d)",
                self.agent_id,
                len(messages) if messages else 0,
            )
            return

        # Build prompt
        user_prompt = build_summary_prompt(self._previous_summary)

        # Query model
        try:
            result_text = await self._callback(SUMMARY_SYSTEM_PROMPT, user_prompt)
        except Exception:
            logger.exception("Summary callback failed for %s", self.agent_id)
            return

        if not result_text or not result_text.strip():
            return

        summary_text = result_text.strip()
        self._previous_summary = summary_text

        result = SummaryResult(
            text=summary_text,
            timestamp=time.time(),
            message_count=len(messages),
            agent_id=self.agent_id,
        )

        self.latest_summary = result
        self.summary_history.append(result)

        logger.debug("Agent %s summary: %s", self.agent_id, summary_text)

    async def _get_messages(self) -> list[dict[str, Any]] | None:
        """Get current messages from the message provider.

        Returns:
            List of message dicts, or None if provider unavailable.
        """
        if self._message_provider is None:
            return None
        try:
            return await self._message_provider(self.agent_id)
        except Exception:
            logger.exception("Failed to get messages for %s", self.agent_id)
            return None

    async def generate_one_shot(
        self,
        messages: list[dict[str, Any]],
    ) -> SummaryResult | None:
        """Generate a single summary without the timer loop.

        Useful for on-demand summary generation.

        Args:
            messages: Current agent messages.

        Returns:
            SummaryResult if successful, None otherwise.
        """
        if len(messages) < self._min_messages:
            return None

        user_prompt = build_summary_prompt(self._previous_summary)

        try:
            result_text = await self._callback(SUMMARY_SYSTEM_PROMPT, user_prompt)
        except Exception:
            logger.exception("One-shot summary failed for %s", self.agent_id)
            return None

        if not result_text or not result_text.strip():
            return None

        summary_text = result_text.strip()
        self._previous_summary = summary_text

        result = SummaryResult(
            text=summary_text,
            timestamp=time.time(),
            message_count=len(messages),
            agent_id=self.agent_id,
        )
        self.latest_summary = result
        self.summary_history.append(result)
        return result


class MessageProvider(Protocol):
    """Protocol for providing agent messages."""

    async def __call__(self, agent_id: str) -> list[dict[str, Any]] | None: ...
