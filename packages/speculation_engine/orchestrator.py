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
import contextlib

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
from speculation_engine.exit_plan_mode import (
    ExitPlanModeController,
    PlanSession,
    PlanState,
    PlanStep,
    TransitionError,
)
from speculation_engine.suggestion import (
    SessionState,
    SuggestionConfig,
    SuggestionResult,
    try_generate_suggestion,
)
from speculation_engine.telemetry import (
    log_speculation_event,
    record_speculation_result,
)
from speculation_engine.feature_flags import FeatureFlagStore, SpecFlags

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
        plan_timeout_seconds: float = 300.0,
        flags: FeatureFlagStore | None = None,
    ) -> None:
        self._workspace = workspace
        self._config = config or SpeculativeResearchConfig()
        self._flags = flags or FeatureFlagStore.create()
        self._engine = SpeculationEngine(
            cwd=workspace,
            bypass_permissions=self._config.trust_level >= 2,
        )
        self._plan_controller = ExitPlanModeController(
            timeout_seconds=plan_timeout_seconds,
        )
        self._session_id = ""
        self._speculation_results: list[SpeculativePhaseResult] = []
        self._session_state = SessionState()
        self._gemini_api_key = gemini_api_key
        self._pair_programmer: Any | None = None
        self._research_sweep: Any | None = None
        self._active_mode: Any = None  # PipelineMode, set by auto_route

        # Lazy-init async consumer when ASYNC_CONSUMER flag is enabled.
        self._async_consumer: Any | None = None

        # Lazy-init mailbox when AGENT_MAILBOX flag is enabled.
        self._mailbox: Any | None = None

    @property
    def flags(self) -> FeatureFlagStore:
        """Access the feature flag store."""
        return self._flags

    @property
    def async_consumer(self) -> Any:
        """Lazy-init AsyncSuggestionConsumer when ASYNC_CONSUMER is enabled."""
        if self._async_consumer is None and self._flags.is_enabled(SpecFlags.ASYNC_CONSUMER):
            from speculation_engine.async_consumer import AsyncSuggestionConsumer

            self._async_consumer = AsyncSuggestionConsumer()
            logger.info("AsyncSuggestionConsumer activated (flag: ASYNC_CONSUMER)")
        return self._async_consumer

    @property
    def mailbox(self) -> Any:
        """Lazy-init AgentMailbox when AGENT_MAILBOX is enabled."""
        if self._mailbox is None and self._flags.is_enabled(SpecFlags.AGENT_MAILBOX):
            from speculation_engine.mailbox import AgentMailbox

            self._mailbox = AgentMailbox()
            logger.info("AgentMailbox activated (flag: AGENT_MAILBOX)")
        return self._mailbox

    def auto_route(self, query: str) -> Any:
        """Auto-select PipelineMode based on query complexity.

        When SEMANTIC_ROUTING flag is enabled, uses a structured intent
        classification approach (mirroring sequential-thinking MCP patterns)
        instead of simple keyword matching.

        Fallback heuristics:
          - Short queries (<100 chars) → pair_programming
          - Keywords like 'research', 'analyze', 'compare', 'landscape' → research_sweep
          - Default → pair_programming

        Returns:
            The PipelineMode enum value selected.
        """
        from speculation_engine.telemetry import SpanContext

        with SpanContext("orchestrator.auto_route", query_length=len(query)):
            if self._flags.is_enabled(SpecFlags.SEMANTIC_ROUTING):
                mode = self._semantic_classify(query)
            else:
                mode = self._keyword_classify(query)

            self._active_mode = mode

        logger.info("Pipeline auto-routed to %s for query: %s...", self._active_mode.value, query[:60])
        return self._active_mode

    def _keyword_classify(self, query: str) -> Any:
        """Classic keyword-based intent classification (default fallback)."""
        from speculation_engine.gemini_bridge import PipelineMode

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
        return PipelineMode.RESEARCH_SWEEP if is_complex else PipelineMode.PAIR_PROGRAMMING

    def _semantic_classify(self, query: str) -> Any:
        """Structured semantic intent classification.

        Uses a multi-step reasoning pipeline inspired by sequential-thinking
        MCP patterns: decompose the query into intent signals, evaluate
        complexity indicators, and route to the appropriate pipeline mode.

        This replaces the keyword heuristic with a structured classification:
          1. Length analysis (character count, sentence count)
          2. Intent signal extraction (action verbs, domain markers)
          3. Complexity scoring (multi-hop reasoning, comparison needs)
          4. Mode selection based on composite score
        """
        from speculation_engine.gemini_bridge import PipelineMode

        query_lower = query.lower()
        score = 0.0

        # Factor 1: Length-based complexity (0-0.3)
        char_len = len(query)
        sentence_count = query.count(".") + query.count("?") + query.count("!") + 1
        if char_len > 200:
            score += 0.3
        elif char_len > 100:
            score += 0.2
        elif char_len > 50:
            score += 0.1
        if sentence_count > 3:
            score += 0.1

        # Factor 2: Research intent signals (0-0.3)
        research_verbs = {
            "research", "analyze", "compare", "survey", "audit",
            "investigate", "benchmark", "evaluate", "assess", "review",
            "examine", "explore", "study", "profile", "diagnose",
        }
        domain_markers = {
            "landscape", "trend", "ecosystem", "architecture",
            "tradeoff", "trade-off", "alternatives", "options",
            "competitors", "state of the art", "best practices",
        }
        verb_hits = sum(1 for v in research_verbs if v in query_lower)
        domain_hits = sum(1 for d in domain_markers if d in query_lower)
        score += min(verb_hits * 0.1, 0.3)
        score += min(domain_hits * 0.15, 0.3)

        # Factor 3: Multi-hop reasoning indicators (0-0.2)
        multi_hop_markers = {
            "and then", "followed by", "after that", "in order to",
            "step by step", "first", "second", "third",
            "how does", "why does", "what are the",
        }
        hop_hits = sum(1 for m in multi_hop_markers if m in query_lower)
        score += min(hop_hits * 0.1, 0.2)

        # Factor 4: Comparison/evaluation needs (0-0.2)
        comparison_markers = {"vs", "versus", "or", "better", "worse", "pros", "cons"}
        comp_hits = sum(1 for c in comparison_markers if c in query_lower.split())
        score += min(comp_hits * 0.1, 0.2)

        # Threshold: >= 0.4 → research sweep, otherwise pair programming
        threshold = 0.4
        mode = PipelineMode.RESEARCH_SWEEP if score >= threshold else PipelineMode.PAIR_PROGRAMMING

        log_speculation_event(
            event="semantic_routing",
            session_id=self._session_id,
            score=round(score, 2),
            threshold=threshold,
            mode=mode.value,
            query_length=len(query),
        )

        return mode

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

    @property
    def plan_controller(self) -> ExitPlanModeController:
        """Access the ExitPlanModeController for planning lifecycle management."""
        return self._plan_controller

    @property
    def plan_state(self) -> PlanState:
        """Current state of the planning state machine."""
        return self._plan_controller.state

    def on_phase_change(self, transition: Any) -> None:
        """Callback for DeepResearchEngine phase transitions.

        Automatically manages speculation engine AND planning controller
        state in response to phase transitions.
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
            # Also clean up any active planning session.
            if self._plan_controller.state not in (PlanState.IDLE, PlanState.ABANDONED):
                with contextlib.suppress(TransitionError):
                    self._plan_controller.cancel()

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

    # --- ExitPlanMode Integration ---

    def enter_plan_mode(self, metadata: dict[str, Any] | None = None) -> PlanSession:
        """Enter planning mode via ExitPlanModeController.

        Args:
            metadata: Optional metadata for the planning session.

        Returns:
            The new PlanSession.

        Raises:
            TransitionError: If the controller is not in IDLE state.
        """
        session = self._plan_controller.begin_planning(
            session_id=self._session_id or f"plan-{int(time.time())}",
            metadata=metadata,
        )
        log_speculation_event(
            event="plan_mode_entered",
            session_id=self._session_id,
        )
        return session

    def add_plan_step(
        self,
        step_id: str,
        description: str,
        tool_calls: list[dict[str, Any]] | None = None,
    ) -> PlanStep:
        """Add a step to the current plan.

        Args:
            step_id: Unique step identifier.
            description: Human-readable description.
            tool_calls: Tool calls this step would execute.

        Returns:
            The new PlanStep.

        Raises:
            TransitionError: If not in PLANNING state.
        """
        return self._plan_controller.add_step(
            step_id=step_id,
            description=description,
            tool_calls=tool_calls,
        )

    def begin_plan_speculation(self) -> None:
        """Begin speculative execution of the current plan.

        Transitions plan controller PLANNING → SPECULATING and starts
        the speculation engine if idle.

        When SPECULATION_TELEMETRY flag is enabled, records a detailed
        speculation result event to the .beads/ evidence trail.

        Raises:
            TransitionError: If not in PLANNING state or no steps.
        """
        self._plan_controller.begin_speculation()
        if self._engine.state == SpeculationState.IDLE:
            self._engine.start()
        log_speculation_event(
            event="plan_speculation_started",
            session_id=self._session_id,
        )

        # Task 5: Record detailed speculation result for quality benchmarking.
        if self._flags.is_enabled(SpecFlags.SPECULATION_TELEMETRY):
            session = self._plan_controller.session
            step_count = len(session.steps) if session else 0
            record_speculation_result(
                session_id=self._session_id,
                step_count=step_count,
                plan_state=self._plan_controller.state.value,
                metadata=session.metadata if session else None,
            )

    def confirm_plan(self) -> None:
        """User confirms the speculated plan.

        When AGENT_MAILBOX flag is enabled, routes through the multi-agent
        mailbox for delegated approval instead of direct confirmation.
        Falls back to direct confirmation if mailbox is not enabled or
        has no required agents configured.

        Transitions: CONFIRMING → EXECUTING.

        Raises:
            TransitionError: If not in CONFIRMING state.
        """
        # Guard: verify we are in CONFIRMING before any side-effects.
        if self._plan_controller.state != PlanState.CONFIRMING:
            msg = f"Cannot confirm plan in {self._plan_controller.state} state"
            raise TransitionError(msg)

        # Task 7: Route through AgentMailbox when enabled.
        if self._flags.is_enabled(SpecFlags.AGENT_MAILBOX) and self.mailbox is not None:
            session = self._plan_controller.session
            plan_id = session.session_id if session else self._session_id
            plan_data = {
                "steps": [
                    {"id": s.step_id, "description": s.description}
                    for s in (session.steps if session else [])
                ],
                "session_id": self._session_id,
            }
            # Submit to mailbox — if no required agents, auto-approves.
            envelope = self.mailbox.submit_plan(
                plan_id=plan_id,
                plan_data=plan_data,
            )
            log_speculation_event(
                event="plan_submitted_to_mailbox",
                session_id=self._session_id,
                plan_id=plan_id,
                status=envelope.status.value,
            )
            # If auto-approved (no required agents), proceed with confirmation.
            if envelope.status.value == "approved":
                self._plan_controller.user_confirm()
            else:
                # Plan remains in CONFIRMING until mailbox resolves.
                logger.info(
                    "Plan '%s' awaiting mailbox approval from: %s",
                    plan_id,
                    envelope.pending_agents,
                )
                return
        else:
            self._plan_controller.user_confirm()

        log_speculation_event(
            event="plan_confirmed",
            session_id=self._session_id,
        )

    def revise_plan(self) -> None:
        """User wants to revise the plan.

        Transitions: CONFIRMING → PLANNING.

        Raises:
            TransitionError: If not in CONFIRMING state.
        """
        self._plan_controller.user_revise()
        log_speculation_event(
            event="plan_revised",
            session_id=self._session_id,
        )

    def cancel_plan(self) -> None:
        """Cancel the current plan.

        Handles cancellation from either PLANNING or CONFIRMING state.
        """
        try:
            self._plan_controller.user_cancel()
        except TransitionError:
            try:
                self._plan_controller.cancel()
            except TransitionError:
                logger.warning("Cannot cancel plan in state %s", self._plan_controller.state)
                return

        log_speculation_event(
            event="plan_cancelled",
            session_id=self._session_id,
        )

    def speculation_complete(self) -> None:
        """Mark speculation as complete — transition to CONFIRMING.

        This is the orchestrator wrapper for the SPECULATING → CONFIRMING
        transition, ensuring telemetry events are emitted.

        Raises:
            TransitionError: If not in SPECULATING state.
        """
        self._plan_controller.speculation_complete()
        log_speculation_event(
            event="plan_speculation_complete",
            session_id=self._session_id,
        )

    def needs_revision_from_speculation(self) -> None:
        """Speculation revealed issues — return to PLANNING.

        Orchestrator wrapper for the SPECULATING → PLANNING transition.

        Raises:
            TransitionError: If not in SPECULATING state.
        """
        self._plan_controller.needs_revision()
        log_speculation_event(
            event="plan_speculation_needs_revision",
            session_id=self._session_id,
        )

    def check_mailbox_resolution(self) -> bool:
        """Check if a pending mailbox approval has resolved.

        When the plan is in CONFIRMING state and was deferred to the
        mailbox, this method polls the mailbox for resolution.

        Returns:
            True if the mailbox resolved and the plan was confirmed.
            False if still pending, expired, or no mailbox envelope exists.
        """
        if self._plan_controller.state != PlanState.CONFIRMING:
            return False
        if self.mailbox is None:
            return False

        session = self._plan_controller.session
        if session is None:
            return False

        envelope = self.mailbox.get_envelope(session.session_id)
        if envelope is None:
            return False

        # Check timeouts first
        self.mailbox.check_timeouts()

        if envelope.status.value == "approved":
            self._plan_controller.user_confirm()
            log_speculation_event(
                event="plan_confirmed_via_mailbox",
                session_id=self._session_id,
                plan_id=session.session_id,
            )
            return True

        if envelope.status.value in ("rejected", "expired"):
            log_speculation_event(
                event="plan_mailbox_denied",
                session_id=self._session_id,
                plan_id=session.session_id,
                status=envelope.status.value,
            )
            return False

        return False

    def complete_plan_execution(self) -> None:
        """Mark plan execution as complete.

        Transitions: EXECUTING → IDLE.

        Raises:
            TransitionError: If not in EXECUTING state.
        """
        self._plan_controller.execution_complete()
        log_speculation_event(
            event="plan_mode_exited",
            session_id=self._session_id,
            exit_reason="complete",
        )

    def check_plan_timeout(self) -> bool:
        """Check if the planning session has timed out.

        Returns:
            True if the session timed out and was auto-abandoned.
        """
        timed_out = self._plan_controller.check_timeout()
        if timed_out:
            log_speculation_event(
                event="plan_mode_exited",
                session_id=self._session_id,
                exit_reason="timeout",
            )
        return timed_out

    def reset(self) -> None:
        """Reset orchestrator for a new session."""
        if self._engine.state != SpeculationState.IDLE:
            self._engine.abort(reason="reset")
        # Reset plan controller if not idle.
        if self._plan_controller.state == PlanState.ABANDONED:
            self._plan_controller.reset()
        elif self._plan_controller.state != PlanState.IDLE:
            try:
                self._plan_controller.cancel()
                self._plan_controller.reset()
            except TransitionError:
                pass  # Best effort
        self._session_id = ""
        self._speculation_results = []
        self._session_state = SessionState()
