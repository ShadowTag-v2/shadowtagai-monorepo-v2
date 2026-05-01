# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Deep Research Client — Autonomous multi-step research agent.

Usage:
    client = DeepResearchClient(api_key="...")

    # Quick research (polling)
    report = client.research("Analyze the EV battery market landscape.")
    print(report.text)

    # Collaborative planning
    plan = client.plan("Research Google TPU history.")
    refined = client.refine_plan(plan, "Focus more on 2025-2026.")
    report = client.execute_plan(refined)

    # Streaming with real-time updates
    for event in client.stream_research("Quantum computing trends."):
        if event.type == "thought":
            print(f"  Thinking: {event.text}")
        elif event.type == "text":
            print(event.text, end="")
"""

from __future__ import annotations

import base64
import logging
import os
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from collections.abc import Generator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AGENT_FAST = "deep-research-preview-04-2026"
AGENT_MAX = "deep-research-max-preview-04-2026"

DEFAULT_POLL_INTERVAL_SECONDS = 10
MAX_POLL_DURATION_SECONDS = 3600  # 60 min max research time
MAX_STREAM_RECONNECT_ATTEMPTS = 5  # More generous for long tasks
RECONNECT_BACKOFF_SECONDS = 3.0


class ResearchStatus(StrEnum):
    """Status of a Deep Research task."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Typed wrappers
# ---------------------------------------------------------------------------


@dataclass
class ResearchImage:
    """An image generated during research (chart, graph, etc.).

    Attributes:
        data: Base64-encoded image bytes.
        mime_type: Image MIME type (e.g., "image/png").
    """

    data: str
    mime_type: str = "image/png"

    def save(self, path: str) -> None:
        """Save the image to disk."""
        with open(path, "wb") as f:
            f.write(base64.b64decode(self.data))


@dataclass
class ResearchReport:
    """Final research report from Deep Research.

    Attributes:
        text: The full research report text (markdown).
        images: Any generated visualizations.
        interaction_id: The interaction ID for follow-up questions.
        status: Completion status.
        usage: Token usage metadata.
        raw: Raw interaction object.
    """

    text: str
    images: list[ResearchImage] = field(default_factory=list)
    interaction_id: str = ""
    status: str = "completed"
    usage: dict[str, Any] | None = None
    raw: Any = None


@dataclass
class PlanResult:
    """Research plan from collaborative planning.

    Attributes:
        plan_text: The proposed research plan.
        interaction_id: ID for continuing the planning conversation.
        agent: The agent used.
    """

    plan_text: str
    interaction_id: str
    agent: str = AGENT_FAST


@dataclass
class ResearchStreamEvent:
    """A streaming event from a Deep Research task.

    Attributes:
        type: Event type ("thought", "text", "image", "complete", "error").
        text: Text content for thought/text events.
        image: Image data for image events.
        interaction_id: Set when the research starts.
        event_id: Server event ID for reconnection.
    """

    type: str
    text: str | None = None
    image: ResearchImage | None = None
    interaction_id: str | None = None
    event_id: str | None = None


@dataclass
class ResearchTask:
    """A handle to a running research task for manual polling.

    Attributes:
        interaction_id: The interaction ID to poll.
        client: Reference to the DeepResearchClient for polling.
    """

    interaction_id: str
    _client_ref: Any = None  # DeepResearchClient

    def poll(self) -> ResearchReport | None:
        """Check if the research is complete. Returns report if done, None if still running."""
        if self._client_ref is None:
            msg = "ResearchTask not bound to a client"
            raise ValueError(msg)
        return self._client_ref._poll_once(self.interaction_id)

    def wait(
        self,
        *,
        poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
        timeout: float = MAX_POLL_DURATION_SECONDS,
    ) -> ResearchReport:
        """Block until research completes or timeout."""
        if self._client_ref is None:
            msg = "ResearchTask not bound to a client"
            raise ValueError(msg)
        return self._client_ref._poll_until_complete(
            self.interaction_id,
            poll_interval=poll_interval,
            timeout=timeout,
        )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class DeepResearchClient:
    """Client for the Gemini Deep Research API.

    Provides research(), plan(), stream_research(), and follow_up() methods
    for autonomous multi-step research using the Deep Research agents.

    Args:
        api_key: Gemini API key. Falls back to GEMINI_API_KEY env var.
        agent: Default agent (AGENT_FAST or AGENT_MAX).
        max_depth: Use AGENT_MAX for maximum comprehensiveness.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        agent: str = AGENT_FAST,
        max_depth: bool = False,
    ) -> None:
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self._agent = AGENT_MAX if max_depth else agent
        self._client: Any | None = None  # Lazy init

    @property
    def client(self) -> Any:
        """Lazily initialize the google-genai Client."""
        if self._client is None:
            try:
                from google import genai

                kwargs: dict[str, Any] = {}
                if self._api_key:
                    kwargs["api_key"] = self._api_key
                self._client = genai.Client(**kwargs)
            except ImportError as exc:
                msg = "google-genai SDK not installed. Run: pip install google-genai>=1.65.0"
                raise ImportError(msg) from exc
        return self._client

    # ---------------------------------------------------------------------------
    # Core API
    # ---------------------------------------------------------------------------

    def research(
        self,
        prompt: str | list[Any],
        *,
        agent: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        visualization: str = "auto",
        poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
        timeout: float = MAX_POLL_DURATION_SECONDS,
    ) -> ResearchReport:
        """Run a Deep Research task and block until completion.

        Args:
            prompt: Research prompt (text or multimodal list).
            agent: Agent to use (defaults to self._agent).
            tools: Additional tools (google_search, url_context, etc.).
            visualization: "auto" or "off".
            poll_interval: Seconds between status polls.
            timeout: Maximum wait time in seconds.

        Returns:
            ResearchReport with the final research output.
        """
        task = self.start_research(
            prompt,
            agent=agent,
            tools=tools,
            visualization=visualization,
        )
        return task.wait(poll_interval=poll_interval, timeout=timeout)

    def start_research(
        self,
        prompt: str | list[Any],
        *,
        agent: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        visualization: str = "auto",
    ) -> ResearchTask:
        """Start a research task in the background (non-blocking).

        Returns a ResearchTask handle for polling or waiting.
        """
        agent = agent or self._agent

        kwargs: dict[str, Any] = {
            "input": prompt,
            "agent": agent,
            "background": True,
            "agent_config": {
                "type": "deep-research",
                "visualization": visualization,
            },
        }

        if tools:
            kwargs["tools"] = tools

        interaction = self.client.interactions.create(**kwargs)
        task = ResearchTask(
            interaction_id=getattr(interaction, "id", ""),
            _client_ref=self,
        )
        logger.info("Deep Research started: %s (agent=%s)", task.interaction_id, agent)
        return task

    def plan(
        self,
        prompt: str | list[Any],
        *,
        agent: str | None = None,
        poll_interval: float = 5.0,
        timeout: float = 120.0,
    ) -> PlanResult:
        """Start collaborative planning — returns a research plan for review.

        Args:
            prompt: What to research.
            agent: Agent to use.
            poll_interval: Poll interval for plan generation.
            timeout: Max time to wait for plan.

        Returns:
            PlanResult with the proposed plan text.
        """
        agent = agent or self._agent

        interaction = self.client.interactions.create(
            agent=agent,
            input=prompt,
            agent_config={
                "type": "deep-research",
                "thinking_summaries": "auto",
                "collaborative_planning": True,
            },
            background=True,
        )

        interaction_id = getattr(interaction, "id", "")
        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:
            result = self.client.interactions.get(interaction_id)
            status = getattr(result, "status", "")

            if status == "completed":
                outputs = getattr(result, "outputs", []) or []
                plan_text = ""
                for output in outputs:
                    if getattr(output, "type", None) == "text":
                        plan_text = getattr(output, "text", "")

                return PlanResult(
                    plan_text=plan_text,
                    interaction_id=interaction_id,
                    agent=agent,
                )
            elif status in ("failed", "cancelled"):
                error = getattr(result, "error", "Unknown error")
                msg = f"Plan generation failed: {error}"
                raise RuntimeError(msg)

            time.sleep(poll_interval)

        msg = f"Plan generation timed out after {timeout}s"
        raise TimeoutError(msg)

    def refine_plan(
        self,
        plan: PlanResult,
        feedback: str,
        *,
        poll_interval: float = 5.0,
        timeout: float = 120.0,
    ) -> PlanResult:
        """Refine a research plan with additional feedback.

        Args:
            plan: The PlanResult to refine.
            feedback: User feedback (e.g., "Focus more on X").

        Returns:
            Updated PlanResult.
        """
        interaction = self.client.interactions.create(
            agent=plan.agent,
            input=feedback,
            agent_config={
                "type": "deep-research",
                "thinking_summaries": "auto",
                "collaborative_planning": True,
            },
            previous_interaction_id=plan.interaction_id,
            background=True,
        )

        interaction_id = getattr(interaction, "id", "")
        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:
            result = self.client.interactions.get(interaction_id)
            status = getattr(result, "status", "")

            if status == "completed":
                outputs = getattr(result, "outputs", []) or []
                plan_text = ""
                for output in outputs:
                    if getattr(output, "type", None) == "text":
                        plan_text = getattr(output, "text", "")

                return PlanResult(
                    plan_text=plan_text,
                    interaction_id=interaction_id,
                    agent=plan.agent,
                )
            elif status in ("failed", "cancelled"):
                error = getattr(result, "error", "Unknown error")
                msg = f"Plan refinement failed: {error}"
                raise RuntimeError(msg)

            time.sleep(poll_interval)

        msg = f"Plan refinement timed out after {timeout}s"
        raise TimeoutError(msg)

    def execute_plan(
        self,
        plan: PlanResult,
        *,
        approval_message: str = "Plan looks good!",
        poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
        timeout: float = MAX_POLL_DURATION_SECONDS,
    ) -> ResearchReport:
        """Execute an approved research plan.

        Args:
            plan: The approved PlanResult.
            approval_message: Message to send when approving the plan.
            poll_interval: Poll interval during research.
            timeout: Maximum research time.

        Returns:
            ResearchReport with the final output.
        """
        interaction = self.client.interactions.create(
            agent=plan.agent,
            input=approval_message,
            agent_config={
                "type": "deep-research",
                "thinking_summaries": "auto",
                "collaborative_planning": False,
            },
            previous_interaction_id=plan.interaction_id,
            background=True,
        )

        interaction_id = getattr(interaction, "id", "")
        return self._poll_until_complete(
            interaction_id,
            poll_interval=poll_interval,
            timeout=timeout,
        )

    def stream_research(
        self,
        prompt: str | list[Any],
        *,
        agent: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        visualization: str = "auto",
    ) -> Generator[ResearchStreamEvent]:
        """Stream a Deep Research task with real-time thought/text/image updates.

        Handles automatic reconnection for long-running research.

        Yields:
            ResearchStreamEvent objects.
        """
        agent = agent or self._agent

        kwargs: dict[str, Any] = {
            "input": prompt,
            "agent": agent,
            "background": True,
            "stream": True,
            "agent_config": {
                "type": "deep-research",
                "thinking_summaries": "auto",
                "visualization": visualization,
            },
        }
        if tools:
            kwargs["tools"] = tools

        interaction_id: str | None = None
        last_event_id: str | None = None
        is_complete = False

        for attempt in range(MAX_STREAM_RECONNECT_ATTEMPTS + 1):
            try:
                if attempt == 0:
                    raw_stream = self.client.interactions.create(**kwargs)
                elif interaction_id:
                    reconnect_kwargs: dict[str, Any] = {"stream": True}
                    if last_event_id:
                        reconnect_kwargs["last_event_id"] = last_event_id
                    raw_stream = self.client.interactions.get(interaction_id, **reconnect_kwargs)
                else:
                    break

                for chunk in raw_stream:
                    event_type = getattr(chunk, "event_type", "")

                    if event_type == "interaction.start":
                        interaction_obj = getattr(chunk, "interaction", None)
                        if interaction_obj:
                            interaction_id = getattr(interaction_obj, "id", None)
                            yield ResearchStreamEvent(
                                type="start",
                                interaction_id=interaction_id,
                            )

                    if hasattr(chunk, "event_id") and chunk.event_id:
                        last_event_id = chunk.event_id

                    if event_type == "content.delta":
                        delta = getattr(chunk, "delta", None)
                        if delta:
                            delta_type = getattr(delta, "type", "")

                            if delta_type == "text":
                                yield ResearchStreamEvent(
                                    type="text",
                                    text=getattr(delta, "text", ""),
                                    event_id=last_event_id,
                                )
                            elif delta_type == "thought_summary":
                                content = getattr(delta, "content", None)
                                thought_text = ""
                                if content:
                                    thought_text = getattr(content, "text", "")
                                yield ResearchStreamEvent(
                                    type="thought",
                                    text=thought_text,
                                    event_id=last_event_id,
                                )
                            elif delta_type == "image":
                                img_data = getattr(delta, "data", "")
                                img_mime = getattr(delta, "mime_type", "image/png")
                                yield ResearchStreamEvent(
                                    type="image",
                                    image=ResearchImage(data=img_data, mime_type=img_mime),
                                    event_id=last_event_id,
                                )

                    elif event_type in ("interaction.complete", "error"):
                        is_complete = True
                        yield ResearchStreamEvent(
                            type="complete" if event_type == "interaction.complete" else "error",
                            event_id=last_event_id,
                        )
                        return

                # Stream ended without completion — check status
                if interaction_id and not is_complete:
                    status = self.client.interactions.get(interaction_id)
                    if getattr(status, "status", "") != "in_progress":
                        return
                else:
                    return

            except Exception:
                logger.warning(
                    "Research stream dropped (attempt %d/%d), reconnecting...",
                    attempt + 1,
                    MAX_STREAM_RECONNECT_ATTEMPTS,
                )
                time.sleep(RECONNECT_BACKOFF_SECONDS * (attempt + 1))

    def follow_up(
        self,
        interaction_id: str,
        question: str,
        *,
        model: str = "gemini-3.1-pro-preview",
    ) -> str:
        """Ask a follow-up question about a completed research report.

        Args:
            interaction_id: The completed research interaction ID.
            question: Follow-up question.
            model: Model to use for the follow-up (not the DR agent).

        Returns:
            Response text.
        """
        interaction = self.client.interactions.create(
            input=question,
            model=model,
            previous_interaction_id=interaction_id,
        )
        outputs = getattr(interaction, "outputs", []) or []
        for output in reversed(outputs):
            if getattr(output, "type", None) == "text":
                return getattr(output, "text", "")
        return ""

    # ---------------------------------------------------------------------------
    # Internal polling
    # ---------------------------------------------------------------------------

    def _poll_once(self, interaction_id: str) -> ResearchReport | None:
        """Single poll check. Returns report if complete, None if still running."""
        result = self.client.interactions.get(interaction_id)
        status = getattr(result, "status", "")

        if status == ResearchStatus.COMPLETED:
            return self._extract_report(result)
        elif status in (ResearchStatus.FAILED, ResearchStatus.CANCELLED):
            error = getattr(result, "error", "Unknown error")
            msg = f"Research failed: {error}"
            raise RuntimeError(msg)

        return None

    def _poll_until_complete(
        self,
        interaction_id: str,
        *,
        poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
        timeout: float = MAX_POLL_DURATION_SECONDS,
    ) -> ResearchReport:
        """Poll until research completes or timeout."""
        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:
            report = self._poll_once(interaction_id)
            if report is not None:
                return report
            logger.debug(
                "Research %s still in progress, polling in %ds...",
                interaction_id,
                poll_interval,
            )
            time.sleep(poll_interval)

        msg = f"Research timed out after {timeout}s"
        raise TimeoutError(msg)

    @staticmethod
    def _extract_report(interaction: Any) -> ResearchReport:
        """Extract a typed ResearchReport from a completed interaction."""
        outputs = getattr(interaction, "outputs", []) or []
        text_parts: list[str] = []
        images: list[ResearchImage] = []

        for output in outputs:
            output_type = getattr(output, "type", "")
            if output_type == "text":
                text_parts.append(getattr(output, "text", ""))
            elif output_type == "image":
                data = getattr(output, "data", "")
                mime = getattr(output, "mime_type", "image/png")
                if data:
                    images.append(ResearchImage(data=data, mime_type=mime))

        usage_obj = getattr(interaction, "usage", None)
        usage_dict = None
        if usage_obj:
            usage_dict = {
                "total_tokens": getattr(usage_obj, "total_tokens", 0),
            }

        return ResearchReport(
            text="\n\n".join(text_parts),
            images=images,
            interaction_id=getattr(interaction, "id", ""),
            status=getattr(interaction, "status", "completed"),
            usage=usage_dict,
            raw=interaction,
        )
