# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Pipeline Bridge — Connects Gemini Interactions + Deep Research
to the existing Speculation Engine orchestrator.

This is the AGNT STATE B P4.1 integration layer. It provides:
  - GeminiPairProgrammer: Live pair-programming via Interactions API
  - GeminiResearchSweep: Autonomous 30-min research sweeps via Deep Research Max
  - PipelineMode: Enum choosing between pair-programming and research modes

The bridge is designed to be wired into the SpeculativeResearchOrchestrator
as an additional execution backend alongside the existing MCP-first routing.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from collections.abc import Generator

from circuit_breaker.telemetry_bridge import default_registry as _cb_registry

logger = logging.getLogger(__name__)

# Register Gemini API circuit breakers with higher tolerance:
#   - 5 consecutive failures → OPEN (Gemini has longer tail latencies)
#   - 180s reset timeout (model warm-up + quota recovery)
_gemini_interactions_breaker = _cb_registry.get_or_create(
    "gemini_interactions", failure_threshold=5, reset_timeout_s=180.0
)
_gemini_research_breaker = _cb_registry.get_or_create(
    "gemini_deep_research", failure_threshold=3, reset_timeout_s=300.0
)


# ---------------------------------------------------------------------------
# Pipeline Mode
# ---------------------------------------------------------------------------


class PipelineMode(StrEnum):
    """Execution mode for the multi-model pipeline."""

    PAIR_PROGRAMMING = "pair_programming"
    RESEARCH_SWEEP = "research_sweep"
    HYBRID = "hybrid"  # Both running concurrently
    SUGGESTION = "suggestion"  # Lightweight single-turn for proactive prefetch


# ---------------------------------------------------------------------------
# Pair Programming Session
# ---------------------------------------------------------------------------


@dataclass
class PairSession:
    """State of a live pair-programming session.

    Attributes:
        session_id: Unique session identifier.
        interaction_chain: Ordered list of interaction IDs forming the conversation.
        model: Gemini model used.
        total_tokens: Running token count.
        start_time: When the session started.
    """

    session_id: str
    interaction_chain: list[str] = field(default_factory=list)
    model: str = "gemini-3-flash-preview"
    total_tokens: int = 0
    start_time: float = field(default_factory=time.monotonic)

    @property
    def duration_seconds(self) -> float:
        return time.monotonic() - self.start_time

    @property
    def turn_count(self) -> int:
        return len(self.interaction_chain)


class GeminiPairProgrammer:
    """Live pair-programming via the Gemini Interactions API.

    Creates a stateful conversation where Antigravity and a Gemini instance
    collaborate on coding tasks in real-time.

    Usage:
        programmer = GeminiPairProgrammer(api_key="...")
        session = programmer.start_session(
            system_prompt="You are a senior Python engineer.",
            model="gemini-3-flash-preview",
        )
        response = programmer.send("Refactor this function for clarity.", session=session)
        print(response.text)

        # Streaming
        for chunk in programmer.send_stream("Now add type hints.", session=session):
            print(chunk, end="")
    """

    def __init__(self, *, api_key: str | None = None) -> None:
        self._api_key = api_key
        self._client: Any | None = None

    @property
    def interactions_client(self) -> Any:
        """Lazy import + init of InteractionsClient."""
        if self._client is None:
            from gemini_interactions.client import InteractionsClient

            self._client = InteractionsClient(api_key=self._api_key)
        return self._client

    def start_session(
        self,
        *,
        system_prompt: str = "You are a senior software engineer collaborating on code.",
        model: str = "gemini-3-flash-preview",
        tools: list[dict[str, Any]] | None = None,
    ) -> PairSession:
        """Start a new pair-programming session.

        Creates the initial interaction to establish system context.
        Returns a PairSession handle for subsequent messages.
        """
        import uuid

        session_id = f"pair-{uuid.uuid4().hex[:12]}"

        # Circuit breaker gate — fail fast if Gemini Interactions is known-down
        if not _gemini_interactions_breaker.allow_request():
            from circuit_breaker import CircuitBreakerOpenError

            raise CircuitBreakerOpenError(
                "gemini_interactions",
                _gemini_interactions_breaker.consecutive_failures,
                _gemini_interactions_breaker.seconds_until_probe,
            )

        try:
            # Bootstrap the session with a system-level greeting
            result = self.interactions_client.create(
                input="Session started. Ready to collaborate.",
                model=model,
                system_instruction=system_prompt,
                tools=tools or [],
                generation_config={
                    "thinking_level": "medium",
                },
            )
            _gemini_interactions_breaker.record_success()
        except Exception:
            _gemini_interactions_breaker.record_failure()
            raise

        session = PairSession(
            session_id=session_id,
            interaction_chain=[result.id],
            model=model,
            total_tokens=result.usage.get("total_tokens", 0) if result.usage else 0,
        )
        logger.info(
            "Pair session %s started (model=%s, interaction=%s)",
            session_id,
            model,
            result.id,
        )
        return session

    def send(
        self,
        message: str,
        *,
        session: PairSession,
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Send a message in an existing pair-programming session.

        Returns the InteractionResult.
        """
        last_id = session.interaction_chain[-1] if session.interaction_chain else None

        if not _gemini_interactions_breaker.allow_request():
            from circuit_breaker import CircuitBreakerOpenError

            raise CircuitBreakerOpenError(
                "gemini_interactions",
                _gemini_interactions_breaker.consecutive_failures,
                _gemini_interactions_breaker.seconds_until_probe,
            )

        try:
            result = self.interactions_client.create(
                input=message,
                model=session.model,
                previous_interaction_id=last_id,
                tools=tools,
            )
            _gemini_interactions_breaker.record_success()
        except Exception:
            _gemini_interactions_breaker.record_failure()
            raise

        session.interaction_chain.append(result.id)
        if result.usage:
            session.total_tokens += result.usage.get("total_tokens", 0)

        return result

    def send_stream(
        self,
        message: str,
        *,
        session: PairSession,
        tools: list[dict[str, Any]] | None = None,
    ) -> Generator[str]:
        """Send a message and stream the response text.

        Yields text chunks as they arrive.
        """
        last_id = session.interaction_chain[-1] if session.interaction_chain else None

        if not _gemini_interactions_breaker.allow_request():
            from circuit_breaker import CircuitBreakerOpenError

            raise CircuitBreakerOpenError(
                "gemini_interactions",
                _gemini_interactions_breaker.consecutive_failures,
                _gemini_interactions_breaker.seconds_until_probe,
            )

        try:
            for event in self.interactions_client.stream(
                input=message,
                model=session.model,
                previous_interaction_id=last_id,
                tools=tools,
            ):
                if event.interaction_id:
                    if event.interaction_id not in session.interaction_chain:
                        session.interaction_chain.append(event.interaction_id)

                if event.text:
                    yield event.text
            _gemini_interactions_breaker.record_success()
        except Exception:
            _gemini_interactions_breaker.record_failure()
            raise


# ---------------------------------------------------------------------------
# Research Sweep
# ---------------------------------------------------------------------------


@dataclass
class SweepResult:
    """Result of an autonomous research sweep.

    Attributes:
        query: The original research query.
        report_text: The final research report.
        images: Generated visualizations.
        duration_seconds: How long the sweep took.
        interaction_id: For follow-up questions.
        agent: Which Deep Research agent was used.
    """

    query: str
    report_text: str
    images: list[Any] = field(default_factory=list)
    duration_seconds: float = 0.0
    interaction_id: str = ""
    agent: str = ""


class GeminiResearchSweep:
    """Autonomous research sweeps via Deep Research Max.

    Executes long-running (10-30 min) deep research tasks in the background,
    optionally with collaborative planning for complex queries.

    Usage:
        sweep = GeminiResearchSweep(api_key="...", max_depth=True)

        # Quick autonomous sweep
        result = sweep.run("Analyze competitive landscape for legal AI startups.")
        print(result.report_text)

        # Planned sweep
        plan = sweep.plan("Research EV battery supply chain risks.")
        print(plan.plan_text)  # Review
        result = sweep.execute(plan)

        # Streaming sweep with real-time updates
        for event in sweep.stream("Quantum computing hardware trends 2025-2026."):
            if event.type == "thought":
                print(f"  🤔 {event.text}")
            elif event.type == "text":
                print(event.text, end="")
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        max_depth: bool = True,
    ) -> None:
        self._api_key = api_key
        self._max_depth = max_depth
        self._client: Any | None = None

    @property
    def dr_client(self) -> Any:
        """Lazy import + init of DeepResearchClient."""
        if self._client is None:
            from gemini_deep_research.client import DeepResearchClient

            self._client = DeepResearchClient(
                api_key=self._api_key,
                max_depth=self._max_depth,
            )
        return self._client

    def run(
        self,
        query: str,
        *,
        tools: list[dict[str, Any]] | None = None,
        timeout: float = 1800.0,  # 30 min default for deep research
    ) -> SweepResult:
        """Run an autonomous research sweep (blocking).

        Args:
            query: What to research.
            tools: Additional tools (MCP servers, etc.).
            timeout: Max wait time in seconds.

        Returns:
            SweepResult with the final report.
        """
        if not _gemini_research_breaker.allow_request():
            from circuit_breaker import CircuitBreakerOpenError

            raise CircuitBreakerOpenError(
                "gemini_deep_research",
                _gemini_research_breaker.consecutive_failures,
                _gemini_research_breaker.seconds_until_probe,
            )

        start = time.monotonic()
        try:
            report = self.dr_client.research(
                query,
                tools=tools,
                timeout=timeout,
            )
            _gemini_research_breaker.record_success()
        except Exception:
            _gemini_research_breaker.record_failure()
            raise
        duration = time.monotonic() - start

        return SweepResult(
            query=query,
            report_text=report.text,
            images=report.images,
            duration_seconds=duration,
            interaction_id=report.interaction_id,
            agent=self.dr_client._agent,
        )

    def plan(self, query: str) -> Any:
        """Start collaborative planning for a research sweep."""
        return self.dr_client.plan(query)

    def execute(self, plan: Any, *, timeout: float = 1800.0) -> SweepResult:
        """Execute a planned research sweep."""
        if not _gemini_research_breaker.allow_request():
            from circuit_breaker import CircuitBreakerOpenError

            raise CircuitBreakerOpenError(
                "gemini_deep_research",
                _gemini_research_breaker.consecutive_failures,
                _gemini_research_breaker.seconds_until_probe,
            )

        start = time.monotonic()
        try:
            report = self.dr_client.execute_plan(plan, timeout=timeout)
            _gemini_research_breaker.record_success()
        except Exception:
            _gemini_research_breaker.record_failure()
            raise
        duration = time.monotonic() - start

        return SweepResult(
            query="(from plan)",
            report_text=report.text,
            images=report.images,
            duration_seconds=duration,
            interaction_id=report.interaction_id,
            agent=getattr(plan, "agent", ""),
        )

    def stream(
        self,
        query: str,
        *,
        tools: list[dict[str, Any]] | None = None,
    ) -> Generator[Any]:
        """Stream a research sweep with real-time updates."""
        yield from self.dr_client.stream_research(query, tools=tools)

    def follow_up(self, sweep_result: SweepResult, question: str) -> str:
        """Ask a follow-up question about a completed sweep."""
        return self.dr_client.follow_up(
            sweep_result.interaction_id,
            question,
        )
