# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Deep Research State Machine — Deterministic phase transitions for
architectural planning with gate-driven execution.

Inspired by Claude Code v2.1.91 patterns:
  - autoDream.ts: time-gate → session-gate → lock-gate cascade
  - speculation.ts: forked agent execution with overlay isolation
  - toolOrchestration.ts: concurrent vs serial tool partitioning

State transitions follow a strict linear path with rollback:
  IDLE → PLANNING → RESEARCHING → SYNTHESIZING → EXECUTING → VERIFYING → COMPLETE
                                                                   ↓ (failure)
                                                             FAILED → IDLE

Each phase has:
  - Entry guards (preconditions that must be true)
  - Allowed operations (tool whitelist for that phase)
  - Timeout / circuit-breaker
  - Rollback action on failure
  - Telemetry event emission
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from collections.abc import Callable

logger = logging.getLogger(__name__)


class ResearchPhase(StrEnum):
  """All valid phases of the deep research pipeline."""

  IDLE = "idle"
  PLANNING = "planning"
  RESEARCHING = "researching"
  SYNTHESIZING = "synthesizing"
  EXECUTING = "executing"
  VERIFYING = "verifying"
  COMPLETE = "complete"
  FAILED = "failed"


# Valid phase transitions — enforced at runtime.
VALID_TRANSITIONS: dict[ResearchPhase, set[ResearchPhase]] = {
  ResearchPhase.IDLE: {ResearchPhase.PLANNING},
  ResearchPhase.PLANNING: {ResearchPhase.RESEARCHING, ResearchPhase.FAILED},
  ResearchPhase.RESEARCHING: {
    ResearchPhase.SYNTHESIZING,
    ResearchPhase.FAILED,
  },
  ResearchPhase.SYNTHESIZING: {
    ResearchPhase.EXECUTING,
    ResearchPhase.FAILED,
  },
  ResearchPhase.EXECUTING: {ResearchPhase.VERIFYING, ResearchPhase.FAILED},
  ResearchPhase.VERIFYING: {ResearchPhase.COMPLETE, ResearchPhase.FAILED},
  ResearchPhase.COMPLETE: {ResearchPhase.IDLE},
  ResearchPhase.FAILED: {ResearchPhase.IDLE},
}

# Phase-specific tool whitelists (Claude Code speculation pattern).
PHASE_ALLOWED_TOOLS: dict[ResearchPhase, set[str]] = {
  ResearchPhase.PLANNING: {
    "sequential_thinking",
    "search_documents",
    "answer_query",
    "view_file",
    "list_dir",
    "grep_search",
  },
  ResearchPhase.RESEARCHING: {
    "search_documents",
    "answer_query",
    "get_documents",
    "read_url_content",
    "search_web",
    "view_file",
    "list_dir",
    "grep_search",
  },
  ResearchPhase.SYNTHESIZING: {
    "sequential_thinking",
    "view_file",
    "list_dir",
  },
  ResearchPhase.EXECUTING: {
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "run_command",
    "view_file",
    "list_dir",
    "grep_search",
  },
  ResearchPhase.VERIFYING: {
    "run_command",
    "view_file",
    "list_dir",
    "grep_search",
    "lighthouse_audit",
    "take_screenshot",
  },
}


@dataclass
class ResearchConfig:
  """Configuration for a deep research session."""

  # Maximum time per phase (seconds).
  phase_timeout_s: float = 300.0
  # Maximum total research time (seconds).
  total_timeout_s: float = 1800.0
  # Circuit breaker: max consecutive failures before abort.
  max_consecutive_failures: int = 3
  # Maximum research queries per session.
  max_queries: int = 50
  # Maximum execution retries per phase.
  max_retries: int = 2
  # Whether to auto-advance through phases.
  auto_advance: bool = True
  # Whether to emit telemetry events.
  emit_telemetry: bool = True


@dataclass
class PhaseTransition:
  """Records a state transition with full metadata."""

  from_phase: ResearchPhase
  to_phase: ResearchPhase
  timestamp: float = field(default_factory=time.time)
  duration_ms: float = 0.0
  success: bool = True
  error: str | None = None
  metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchResult:
  """Result of a complete deep research session."""

  session_id: str
  phases_completed: list[PhaseTransition]
  final_phase: ResearchPhase
  findings: dict[str, Any] = field(default_factory=dict)
  execution_artifacts: list[str] = field(default_factory=list)
  total_duration_ms: float = 0.0
  total_queries: int = 0
  success: bool = False
  error: str | None = None


@dataclass
class _PhaseState:
  """Internal mutable state for phase tracking."""

  phase: ResearchPhase = ResearchPhase.IDLE
  phase_start: float = 0.0
  consecutive_failures: int = 0
  total_queries: int = 0
  findings: dict[str, Any] = field(default_factory=dict)
  transitions: list[PhaseTransition] = field(default_factory=list)
  execution_artifacts: list[str] = field(default_factory=list)


class DeepResearchEngine:
  """Deterministic multi-phase research orchestrator.

  Drives the IDLE → PLANNING → RESEARCHING → SYNTHESIZING →
  EXECUTING → VERIFYING → COMPLETE pipeline with phase guards,
  circuit breakers, and rollback safety.

  Usage::

      engine = DeepResearchEngine(config=ResearchConfig())
      result = await engine.run(
          objective="Design a caching layer for the API gateway",
          context={"workspace": "/path/to/repo"},
      )

  The engine enforces:
    - Strict phase ordering (no skipping phases)
    - Tool whitelisting per phase
    - Timeout per phase and total session
    - Circuit breaker on consecutive failures
    - Rollback to IDLE on unrecoverable error
  """

  def __init__(
    self,
    config: ResearchConfig | None = None,
    on_phase_change: Callable[[PhaseTransition], None] | None = None,
  ) -> None:
    self._config = config or ResearchConfig()
    self._on_phase_change = on_phase_change
    self._state = _PhaseState()
    self._session_id = ""
    self._session_start = 0.0
    self._abort_event = asyncio.Event()
    self._lock = asyncio.Lock()

  # ── Public API ──────────────────────────────────────────────

  @property
  def current_phase(self) -> ResearchPhase:
    """The current phase of the research pipeline."""
    return self._state.phase

  @property
  def session_id(self) -> str:
    """The unique identifier for the current session."""
    return self._session_id

  @property
  def is_active(self) -> bool:
    """Whether a research session is currently running."""
    return self._state.phase not in {
      ResearchPhase.IDLE,
      ResearchPhase.COMPLETE,
      ResearchPhase.FAILED,
    }

  def abort(self) -> None:
    """Signal the engine to abort the current session."""
    self._abort_event.set()

  def is_tool_allowed(self, tool_name: str) -> bool:
    """Check if a tool is allowed in the current phase."""
    allowed = PHASE_ALLOWED_TOOLS.get(self._state.phase)
    if allowed is None:
      return False
    return tool_name in allowed

  async def run(
    self,
    objective: str,
    context: dict[str, Any] | None = None,
    phase_handlers: dict[
      ResearchPhase,
      Callable[
        [str, dict[str, Any], _PhaseState],
        Any,
      ],
    ]
    | None = None,
  ) -> ResearchResult:
    """Execute the full research pipeline.

    Args:
        objective: The research objective / architectural question.
        context: Additional context (workspace path, file refs, etc.).
        phase_handlers: Optional custom handlers per phase.
            Each handler receives (objective, context, state)
            and should return phase-specific results to store
            in state.findings[phase_name].

    Returns:
        ResearchResult with all findings, artifacts, and metadata.
    """
    async with self._lock:
      return await self._run_pipeline(objective, context or {}, phase_handlers or {})

  # ── Internal Pipeline ───────────────────────────────────────

  async def _run_pipeline(
    self,
    objective: str,
    context: dict[str, Any],
    phase_handlers: dict[ResearchPhase, Callable[..., Any]],
  ) -> ResearchResult:
    self._session_id = f"dr-{uuid.uuid4().hex[:12]}"
    self._session_start = time.time()
    self._abort_event.clear()
    self._state = _PhaseState()

    logger.info(
      "[DeepResearch] Starting session %s: %s",
      self._session_id,
      objective[:120],
    )

    pipeline_phases = [
      ResearchPhase.PLANNING,
      ResearchPhase.RESEARCHING,
      ResearchPhase.SYNTHESIZING,
      ResearchPhase.EXECUTING,
      ResearchPhase.VERIFYING,
    ]

    try:
      for target_phase in pipeline_phases:
        if self._abort_event.is_set():
          logger.warning(
            "[DeepResearch] Abort signaled before %s",
            target_phase,
          )
          await self._transition(ResearchPhase.FAILED, error="aborted")
          break

        # Check total timeout.
        elapsed = time.time() - self._session_start
        if elapsed > self._config.total_timeout_s:
          logger.warning(
            "[DeepResearch] Total timeout (%.1fs) exceeded",
            elapsed,
          )
          await self._transition(ResearchPhase.FAILED, error="total_timeout")
          break

        # Transition to next phase.
        await self._transition(target_phase)

        # Execute phase handler with timeout.
        handler = phase_handlers.get(target_phase, self._default_phase_handler)
        try:
          result = await asyncio.wait_for(
            asyncio.ensure_future(
              self._execute_phase(handler, objective, context, target_phase)
            ),
            timeout=self._config.phase_timeout_s,
          )
          self._state.findings[target_phase.value] = result
          self._state.consecutive_failures = 0
        except TimeoutError:
          logger.warning("[DeepResearch] Phase %s timed out", target_phase)
          self._state.consecutive_failures += 1
          if self._state.consecutive_failures >= self._config.max_consecutive_failures:
            await self._transition(
              ResearchPhase.FAILED,
              error=f"circuit_breaker_{target_phase.value}",
            )
            break
        except Exception as exc:
          logger.exception(
            "[DeepResearch] Phase %s failed: %s",
            target_phase,
            exc,
          )
          self._state.consecutive_failures += 1
          if self._state.consecutive_failures >= self._config.max_consecutive_failures:
            await self._transition(
              ResearchPhase.FAILED,
              error=str(exc),
            )
            break
      else:
        # All phases completed successfully.
        await self._transition(ResearchPhase.COMPLETE)

    except Exception as exc:
      logger.exception("[DeepResearch] Pipeline error: %s", exc)
      try:
        await self._transition(ResearchPhase.FAILED, error=str(exc))
      except Exception:
        self._state.phase = ResearchPhase.FAILED

    total_duration = (time.time() - self._session_start) * 1000
    return ResearchResult(
      session_id=self._session_id,
      phases_completed=list(self._state.transitions),
      final_phase=self._state.phase,
      findings=dict(self._state.findings),
      execution_artifacts=list(self._state.execution_artifacts),
      total_duration_ms=total_duration,
      total_queries=self._state.total_queries,
      success=self._state.phase == ResearchPhase.COMPLETE,
      error=(
        self._state.transitions[-1].error
        if self._state.transitions and not self._state.transitions[-1].success
        else None
      ),
    )

  async def _transition(
    self,
    to_phase: ResearchPhase,
    error: str | None = None,
  ) -> None:
    """Perform a validated phase transition."""
    from_phase = self._state.phase
    valid_targets = VALID_TRANSITIONS.get(from_phase, set())

    if to_phase not in valid_targets:
      msg = f"Invalid transition: {from_phase.value} → {to_phase.value}. Valid targets: {[p.value for p in valid_targets]}"
      raise ValueError(msg)

    now = time.time()
    duration_ms = (
      (now - self._state.phase_start) * 1000 if self._state.phase_start > 0 else 0.0
    )

    transition = PhaseTransition(
      from_phase=from_phase,
      to_phase=to_phase,
      timestamp=now,
      duration_ms=duration_ms,
      success=error is None,
      error=error,
      metadata={
        "session_id": self._session_id,
        "total_queries": self._state.total_queries,
      },
    )

    self._state.transitions.append(transition)
    self._state.phase = to_phase
    self._state.phase_start = now

    logger.info(
      "[DeepResearch] %s → %s (%.0fms)%s",
      from_phase.value,
      to_phase.value,
      duration_ms,
      f" error={error}" if error else "",
    )

    if self._on_phase_change:
      try:
        self._on_phase_change(transition)
      except Exception:
        logger.exception("[DeepResearch] on_phase_change callback error")

    # Emit telemetry.
    if self._config.emit_telemetry:
      from deep_research.telemetry import emit_phase_event

      emit_phase_event(transition)

  async def _execute_phase(
    self,
    handler: Callable[..., Any],
    objective: str,
    context: dict[str, Any],
    phase: ResearchPhase,
  ) -> Any:
    """Execute a phase handler with retry logic."""
    last_error: Exception | None = None
    for attempt in range(1, self._config.max_retries + 1):
      try:
        result = handler(objective, context, self._state)
        if asyncio.iscoroutine(result):
          return await result
        return result
      except Exception as exc:
        last_error = exc
        logger.warning(
          "[DeepResearch] Phase %s attempt %d/%d failed: %s",
          phase.value,
          attempt,
          self._config.max_retries,
          exc,
        )
        if attempt < self._config.max_retries:
          await asyncio.sleep(0.1 * attempt)

    raise last_error or RuntimeError(f"Phase {phase.value} exhausted retries")

  @staticmethod
  async def _default_phase_handler(
    objective: str,
    context: dict[str, Any],
    state: _PhaseState,
  ) -> dict[str, Any]:
    """Default no-op handler that passes through."""
    return {
      "objective": objective,
      "phase": state.phase.value,
      "status": "completed_default",
    }

  # ── Convenience Methods ─────────────────────────────────────

  def get_phase_summary(self) -> dict[str, Any]:
    """Return a summary of all phase transitions."""
    return {
      "session_id": self._session_id,
      "current_phase": self._state.phase.value,
      "transitions": [
        {
          "from": t.from_phase.value,
          "to": t.to_phase.value,
          "duration_ms": round(t.duration_ms, 1),
          "success": t.success,
          "error": t.error,
        }
        for t in self._state.transitions
      ],
      "total_queries": self._state.total_queries,
      "consecutive_failures": self._state.consecutive_failures,
    }

  def record_query(self) -> bool:
    """Record a research query. Returns False if limit exceeded."""
    self._state.total_queries += 1
    return self._state.total_queries <= self._config.max_queries

  def add_artifact(self, path: str) -> None:
    """Register an execution artifact (file created/modified)."""
    self._state.execution_artifacts.append(path)
