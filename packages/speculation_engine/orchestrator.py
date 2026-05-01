# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Speculative Research Orchestrator — Wires SpeculationEngine into DeepResearchEngine.

Architecture:
  SpeculationEngine (CoW overlay + suggestion pipeline) is integrated into
  the DeepResearchEngine's phase lifecycle to enable proactive speculative
  execution during research sessions.

Integration points:
  RESEARCHING  → pre-compute suggestions for next research queries
  SYNTHESIZING → speculatively pre-generate execution plans
  EXECUTING    → use CoW overlay for speculative file writes
  VERIFYING    → validate overlay diff before merge

The orchestrator creates phase handlers that wrap both engines together,
maintaining a unified session_id for telemetry correlation.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from speculation_engine.engine import (
    SpeculationEngine,
    SpeculationState,
)
from speculation_engine.suggestion import (
    SessionState,
    SuggestionConfig,
    SuggestionResult,
    try_generate_suggestion,
)
from speculation_engine.telemetry import log_speculation_event

logger = logging.getLogger(__name__)


@dataclass
class SpeculativeResearchConfig:
    """Configuration for speculative research integration."""

    # Enable speculative suggestion during RESEARCHING phase.
    speculate_during_research: bool = True
    # Enable speculative plan generation during SYNTHESIZING phase.
    speculate_during_synthesis: bool = True
    # Enable CoW overlay during EXECUTING phase.
    use_cow_overlay: bool = True
    # Maximum speculation time per phase (seconds).
    max_speculation_time_s: float = 30.0
    # Trust level for bypass_permissions (0=never, 1=session-approved, 2=always).
    trust_level: int = 0
    # Suggestion generation function (None = disabled).
    generate_fn: Callable[..., tuple[str, str]] | None = None
    # Suggestion configuration.
    suggestion_config: SuggestionConfig = field(default_factory=SuggestionConfig)


@dataclass
class SpeculativePhaseResult:
    """Result of a speculative phase execution."""

    phase: str
    speculation_active: bool = False
    suggestion: SuggestionResult | None = None
    overlay_files_written: int = 0
    time_saved_ms: float = 0.0
    inner_result: dict[str, Any] = field(default_factory=dict)


class SpeculativeResearchOrchestrator:
    """Orchestrates SpeculationEngine within DeepResearchEngine lifecycle.

    Usage::

        from deep_research.state_machine import DeepResearchEngine, ResearchConfig
        from speculation_engine.orchestrator import SpeculativeResearchOrchestrator

        orchestrator = SpeculativeResearchOrchestrator(
            workspace="/path/to/repo",
            config=SpeculativeResearchConfig(trust_level=1),
        )
        research_engine = DeepResearchEngine(
            config=ResearchConfig(),
            on_phase_change=orchestrator.on_phase_change,
        )
        handlers = orchestrator.create_phase_handlers()
        result = await research_engine.run(
            objective="Design caching layer",
            phase_handlers=handlers,
        )
    """

    def __init__(
        self,
        workspace: str,
        config: SpeculativeResearchConfig | None = None,
        *,
        gemini_api_key: str | None = None,
    ) -> None:
        self._workspace = workspace
        self._config = config or SpeculativeResearchConfig()
        self._engine = SpeculationEngine(
            cwd=workspace,
            bypass_permissions=self._config.trust_level >= 2,
        )
        self._session_id = ""
        self._speculation_results: list[SpeculativePhaseResult] = []
        self._session_state = SessionState()
        self._gemini_api_key = gemini_api_key
        self._pair_programmer: Any | None = None
        self._research_sweep: Any | None = None
        self._active_mode: Any = None  # PipelineMode, set by auto_route

    def auto_route(self, query: str) -> Any:
        """Auto-select PipelineMode based on query complexity.

        Heuristics:
          - Short queries (<100 chars) → pair_programming
          - Keywords like 'research', 'analyze', 'compare', 'landscape' → research_sweep
          - Default → pair_programming

        Returns:
            The PipelineMode enum value selected.
        """
        from speculation_engine.gemini_bridge import PipelineMode
        from speculation_engine.telemetry import SpanContext

        research_keywords = {
            "research",
            "analyze",
            "compare",
            "landscape",
            "survey",
            "audit",
            "investigate",
            "benchmark",
            "evaluate",
            "trend",
        }

        query_lower = query.lower()
        is_complex = len(query) > 100 or any(kw in query_lower for kw in research_keywords)

        with SpanContext("orchestrator.auto_route", query_length=len(query)):
            if is_complex:
                self._active_mode = PipelineMode.RESEARCH_SWEEP
            else:
                self._active_mode = PipelineMode.PAIR_PROGRAMMING

        logger.info("Pipeline auto-routed to %s for query: %s...", self._active_mode.value, query[:60])
        return self._active_mode

    @property
    def pair_programmer(self) -> Any:
        """Lazy-init GeminiPairProgrammer for live pair-programming."""
        if self._pair_programmer is None:
            from speculation_engine.gemini_bridge import GeminiPairProgrammer

            self._pair_programmer = GeminiPairProgrammer(
                api_key=self._gemini_api_key,
            )
        return self._pair_programmer

    @property
    def research_sweep(self) -> Any:
        """Lazy-init GeminiResearchSweep for autonomous research."""
        if self._research_sweep is None:
            from speculation_engine.gemini_bridge import GeminiResearchSweep

            self._research_sweep = GeminiResearchSweep(
                api_key=self._gemini_api_key,
                max_depth=True,
            )
        return self._research_sweep

    @property
    def speculation_engine(self) -> SpeculationEngine:
        """Access the underlying SpeculationEngine."""
        return self._engine

    @property
    def results(self) -> list[SpeculativePhaseResult]:
        """All speculative phase results from the current session."""
        return list(self._speculation_results)

    def on_phase_change(self, transition: Any) -> None:
        """Callback for DeepResearchEngine phase transitions.

        Automatically manages speculation engine state in response to
        phase transitions.
        """
        to_phase = getattr(transition, "to_phase", None)
        session_id = getattr(transition, "metadata", {}).get("session_id", "")

        if session_id and not self._session_id:
            self._session_id = session_id

        phase_value = to_phase.value if hasattr(to_phase, "value") else str(to_phase)

        # Start speculation on entering relevant phases.
        if phase_value in ("researching", "synthesizing", "executing"):
            if self._engine.state == SpeculationState.IDLE:
                self._engine.start()
                log_speculation_event(
                    event="phase_start",
                    session_id=self._session_id,
                    phase=phase_value,
                )

        # Clean up speculation on terminal phases.
        if phase_value in ("complete", "failed", "idle"):
            if self._engine.state != SpeculationState.IDLE:
                self._engine.abort(reason=f"phase_{phase_value}")

    def create_phase_handlers(
        self,
        inner_handlers: dict[str, Callable[..., Any]] | None = None,
    ) -> dict[str, Any]:
        """Create DeepResearchEngine phase handlers with speculation wiring.

        Args:
            inner_handlers: Optional inner handlers to wrap with speculation.
                Keys should be ResearchPhase enum values.

        Returns:
            Phase handler dict for DeepResearchEngine.run(phase_handlers=...).
        """
        from deep_research.state_machine import ResearchPhase

        handlers: dict[ResearchPhase, Callable[..., Any]] = {}
        _inner = inner_handlers or {}

        if self._config.speculate_during_research:
            handlers[ResearchPhase.RESEARCHING] = self._make_speculative_handler(
                ResearchPhase.RESEARCHING,
                _inner.get(ResearchPhase.RESEARCHING),
            )

        if self._config.speculate_during_synthesis:
            handlers[ResearchPhase.SYNTHESIZING] = self._make_speculative_handler(
                ResearchPhase.SYNTHESIZING,
                _inner.get(ResearchPhase.SYNTHESIZING),
            )

        if self._config.use_cow_overlay:
            handlers[ResearchPhase.EXECUTING] = self._make_cow_handler(
                _inner.get(ResearchPhase.EXECUTING),
            )

        # Pass through any inner handlers we didn't wrap.
        for phase, handler in _inner.items():
            if phase not in handlers:
                handlers[phase] = handler

        return handlers

    def _make_speculative_handler(
        self,
        phase: Any,
        inner_handler: Callable[..., Any] | None,
    ) -> Callable[..., Any]:
        """Create a handler that runs speculation alongside inner logic."""

        async def handler(
            objective: str,
            context: dict[str, Any],
            state: Any,
        ) -> dict[str, Any]:
            start = time.monotonic()
            phase_value = phase.value if hasattr(phase, "value") else str(phase)

            # Run inner handler (the actual phase work).
            inner_result: dict[str, Any] = {}
            if inner_handler:
                result = inner_handler(objective, context, state)
                if asyncio.iscoroutine(result):
                    inner_result = await result
                else:
                    inner_result = result
            else:
                inner_result = {
                    "phase": phase_value,
                    "objective": objective[:120],
                    "status": "default",
                }

            # Run speculative suggestion generation.
            suggestion = self._generate_speculative_suggestion(objective, context)

            if suggestion and suggestion.suggestion:
                self._engine.set_pipelined_suggestion(suggestion.suggestion)

            spec_result = SpeculativePhaseResult(
                phase=phase_value,
                speculation_active=True,
                suggestion=suggestion,
                time_saved_ms=(time.monotonic() - start) * 1000,
                inner_result=inner_result,
            )
            self._speculation_results.append(spec_result)

            log_speculation_event(
                event="phase_complete",
                session_id=self._session_id,
                phase=phase_value,
                has_suggestion=suggestion.suggestion is not None if suggestion else False,
                time_saved_ms=spec_result.time_saved_ms,
            )

            return {
                **inner_result,
                "_speculation": {
                    "suggestion": suggestion.suggestion if suggestion else None,
                    "generation_time_ms": suggestion.generation_time_ms if suggestion else 0,
                    "time_saved_ms": spec_result.time_saved_ms,
                },
            }

        return handler

    def _make_cow_handler(
        self,
        inner_handler: Callable[..., Any] | None,
    ) -> Callable[..., Any]:
        """Create an EXECUTING handler that uses CoW overlay isolation."""

        async def handler(
            objective: str,
            context: dict[str, Any],
            state: Any,
        ) -> dict[str, Any]:
            # Ensure engine is active with overlay.
            if self._engine.state == SpeculationState.IDLE:
                self._engine.start()

            inner_result: dict[str, Any] = {}
            if inner_handler:
                result = inner_handler(objective, context, state)
                if asyncio.iscoroutine(result):
                    inner_result = await result
                else:
                    inner_result = result
            else:
                inner_result = {
                    "phase": "executing",
                    "objective": objective[:120],
                    "status": "default",
                }

            overlay_count = len(self._engine.overlay.written_files) if self._engine.overlay else 0

            spec_result = SpeculativePhaseResult(
                phase="executing",
                speculation_active=True,
                overlay_files_written=overlay_count,
                inner_result=inner_result,
            )
            self._speculation_results.append(spec_result)

            log_speculation_event(
                event="cow_phase_complete",
                session_id=self._session_id,
                overlay_files=overlay_count,
            )

            return {
                **inner_result,
                "_cow_overlay": {
                    "files_written": overlay_count,
                    "overlay_active": self._engine.overlay is not None,
                },
            }

        return handler

    def _generate_speculative_suggestion(
        self,
        objective: str,
        context: dict[str, Any],
    ) -> SuggestionResult | None:
        """Generate a speculative prompt suggestion for the current phase."""
        if not self._config.generate_fn:
            return None

        messages = [
            {"role": "user", "content": objective},
            {"role": "assistant", "content": f"Research context: {list(context.keys())}"},
        ]

        # Update session state for suggestion eligibility.
        self._session_state.assistant_turn_count = max(
            self._session_state.assistant_turn_count,
            self._config.suggestion_config.min_assistant_turns,
        )

        return try_generate_suggestion(
            messages=messages,
            state=self._session_state,
            config=self._config.suggestion_config,
            generate_fn=self._config.generate_fn,
        )

    def accept_speculation(self) -> dict[str, Any]:
        """Accept current speculation and merge overlay to workspace."""
        if self._engine.state in (
            SpeculationState.COMPLETE,
            SpeculationState.WAITING_ACCEPT,
        ):
            return self._engine.accept()
        return {
            "messages": [],
            "boundary": None,
            "time_saved_ms": 0,
            "merged_files": [],
            "query_required": True,
            "pipelined_suggestion": None,
        }

    def get_session_summary(self) -> dict[str, Any]:
        """Return a summary of all speculative activity in this session."""
        total_time_saved = sum(r.time_saved_ms for r in self._speculation_results)
        suggestion_count = sum(1 for r in self._speculation_results if r.suggestion and r.suggestion.suggestion)
        overlay_files = sum(r.overlay_files_written for r in self._speculation_results)

        return {
            "session_id": self._session_id,
            "phases_speculated": len(self._speculation_results),
            "suggestions_generated": suggestion_count,
            "overlay_files_written": overlay_files,
            "total_time_saved_ms": round(total_time_saved, 1),
            "engine_state": self._engine.state.value,
        }

    def reset(self) -> None:
        """Reset orchestrator for a new session."""
        if self._engine.state != SpeculationState.IDLE:
            self._engine.abort(reason="reset")
        self._session_id = ""
        self._speculation_results = []
        self._session_state = SessionState()
