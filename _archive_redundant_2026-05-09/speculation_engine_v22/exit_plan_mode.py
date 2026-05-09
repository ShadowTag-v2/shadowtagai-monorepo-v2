# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ExitPlanMode State Machine — Speculation Engine lifecycle controller.

Implements the Claude Code CCR (Claude Code Runtime) ExitPlanMode
semantics as a state machine for the AGNT speculation engine.

States:
    IDLE       → No active planning session
    PLANNING   → Agent is decomposing a task into steps
    SPECULATING → Agent is speculatively executing steps
    CONFIRMING → Agent has completed speculation, awaiting user confirmation
    EXECUTING  → User-confirmed, executing for real
    ABANDONED  → Session timed out or user cancelled

Transitions:
    IDLE → PLANNING         : on begin_planning()
    PLANNING → SPECULATING  : on begin_speculation()
    PLANNING → ABANDONED    : on timeout or cancel()
    SPECULATING → CONFIRMING: on speculation_complete()
    SPECULATING → PLANNING  : on needs_revision()
    CONFIRMING → EXECUTING  : on user_confirm()
    CONFIRMING → PLANNING   : on user_revise()
    CONFIRMING → ABANDONED  : on user_cancel()
    EXECUTING → IDLE        : on execution_complete()
    ABANDONED → IDLE        : on reset()

Reference: Claude Code utils/ultraplan/ccrSession.ts
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class PlanState(StrEnum):
    """States in the ExitPlanMode state machine."""

    IDLE = "IDLE"
    PLANNING = "PLANNING"
    SPECULATING = "SPECULATING"
    CONFIRMING = "CONFIRMING"
    EXECUTING = "EXECUTING"
    ABANDONED = "ABANDONED"


class TransitionError(Exception):
    """Raised when an invalid state transition is attempted."""


@dataclass
class PlanStep:
    """A single step in a planning session.

    Attributes:
        step_id: Unique identifier for this step.
        description: Human-readable step description.
        tool_calls: Tool calls this step would execute.
        status: Current step status (pending/speculated/confirmed/executed/failed).
        speculation_result: Result from speculative execution.
        execution_result: Result from real execution.
    """

    step_id: str
    description: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    status: str = "pending"
    speculation_result: dict[str, Any] | None = None
    execution_result: dict[str, Any] | None = None


@dataclass
class PlanSession:
    """A planning/speculation session.

    Attributes:
        session_id: Unique session identifier.
        state: Current state machine state.
        steps: Ordered list of plan steps.
        created_at: Unix timestamp of session creation.
        last_activity: Unix timestamp of last activity.
        timeout_seconds: Inactivity timeout before auto-abandonment.
        metadata: Additional session metadata.
    """

    session_id: str
    state: PlanState = PlanState.IDLE
    steps: list[PlanStep] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    timeout_seconds: float = 300.0  # 5-minute default
    metadata: dict[str, Any] = field(default_factory=dict)


# Valid state transitions
_VALID_TRANSITIONS: dict[PlanState, set[PlanState]] = {
    PlanState.IDLE: {PlanState.PLANNING},
    PlanState.PLANNING: {PlanState.SPECULATING, PlanState.ABANDONED},
    PlanState.SPECULATING: {PlanState.CONFIRMING, PlanState.PLANNING},
    PlanState.CONFIRMING: {PlanState.EXECUTING, PlanState.PLANNING, PlanState.ABANDONED},
    PlanState.EXECUTING: {PlanState.IDLE},
    PlanState.ABANDONED: {PlanState.IDLE},
}


class ExitPlanModeController:
    """Controls the ExitPlanMode state machine for the speculation engine.

    This controller manages the lifecycle of a planning session, including
    speculative pre-execution, user confirmation, and real execution.

    Args:
        timeout_seconds: Inactivity timeout in seconds (default: 300).
    """

    def __init__(self, timeout_seconds: float = 300.0) -> None:
        self._timeout = timeout_seconds
        self._session: PlanSession | None = None
        self._history: list[tuple[PlanState, PlanState, float]] = []

    @property
    def state(self) -> PlanState:
        """Current state of the state machine."""
        if self._session is None:
            return PlanState.IDLE
        return self._session.state

    @property
    def session(self) -> PlanSession | None:
        """Current active session, if any."""
        return self._session

    def _transition(self, target: PlanState) -> None:
        """Execute a state transition.

        Args:
            target: The target state.

        Raises:
            TransitionError: If the transition is invalid.
        """
        current = self.state

        valid_targets = _VALID_TRANSITIONS.get(current, set())
        if target not in valid_targets:
            msg = f"Invalid transition: {current} → {target} (valid: {valid_targets})"
            raise TransitionError(msg)

        now = time.time()
        self._history.append((current, target, now))

        if self._session:
            self._session.state = target
            self._session.last_activity = now

        logger.info("ExitPlanMode: %s → %s", current, target)

    def begin_planning(self, session_id: str, metadata: dict[str, Any] | None = None) -> PlanSession:
        """Start a new planning session.

        Args:
            session_id: Unique session identifier.
            metadata: Optional session metadata.

        Returns:
            The new PlanSession.

        Raises:
            TransitionError: If not in IDLE state.
        """
        self._session = PlanSession(
            session_id=session_id,
            state=PlanState.IDLE,
            timeout_seconds=self._timeout,
            metadata=metadata or {},
        )
        self._transition(PlanState.PLANNING)
        return self._session

    def add_step(self, step_id: str, description: str, tool_calls: list[dict[str, Any]] | None = None) -> PlanStep:
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
        if self.state != PlanState.PLANNING:
            msg = f"Cannot add steps in {self.state} state"
            raise TransitionError(msg)

        step = PlanStep(
            step_id=step_id,
            description=description,
            tool_calls=tool_calls or [],
        )
        assert self._session is not None
        self._session.steps.append(step)
        self._session.last_activity = time.time()
        return step

    def begin_speculation(self) -> None:
        """Transition from PLANNING to SPECULATING.

        Raises:
            TransitionError: If not in PLANNING state or no steps defined.
        """
        if self._session and not self._session.steps:
            msg = "Cannot speculate with no steps defined"
            raise TransitionError(msg)
        self._transition(PlanState.SPECULATING)

    def record_speculation_result(self, step_id: str, result: dict[str, Any]) -> None:
        """Record the result of a speculative execution.

        Args:
            step_id: The step that was speculatively executed.
            result: The speculation result.

        Raises:
            TransitionError: If not in SPECULATING state.
        """
        if self.state != PlanState.SPECULATING:
            msg = f"Cannot record speculation in {self.state} state"
            raise TransitionError(msg)

        assert self._session is not None
        for step in self._session.steps:
            if step.step_id == step_id:
                step.speculation_result = result
                step.status = "speculated"
                break

        self._session.last_activity = time.time()

    def speculation_complete(self) -> None:
        """All steps speculated — transition to CONFIRMING.

        Raises:
            TransitionError: If not in SPECULATING state.
        """
        self._transition(PlanState.CONFIRMING)

    def needs_revision(self) -> None:
        """Speculation revealed issues — return to PLANNING.

        Raises:
            TransitionError: If not in SPECULATING state.
        """
        if self.state != PlanState.SPECULATING:
            msg = f"needs_revision requires SPECULATING state, currently in {self.state}"
            raise TransitionError(msg)
        self._transition(PlanState.PLANNING)

    def user_confirm(self) -> None:
        """User confirms the speculated plan — transition to EXECUTING.

        Raises:
            TransitionError: If not in CONFIRMING state.
        """
        self._transition(PlanState.EXECUTING)

    def user_revise(self) -> None:
        """User wants to revise the plan — return to PLANNING.

        Raises:
            TransitionError: If not in CONFIRMING state.
        """
        self._transition(PlanState.PLANNING)

    def user_cancel(self) -> None:
        """User cancels the plan — abandon the session.

        Raises:
            TransitionError: If not in CONFIRMING state.
        """
        self._transition(PlanState.ABANDONED)

    def execution_complete(self) -> None:
        """All steps executed — return to IDLE.

        Raises:
            TransitionError: If not in EXECUTING state.
        """
        self._transition(PlanState.IDLE)
        self._session = None

    def cancel(self) -> None:
        """Cancel from PLANNING state — abandon.

        Raises:
            TransitionError: If not in PLANNING state.
        """
        self._transition(PlanState.ABANDONED)

    def reset(self) -> None:
        """Reset from ABANDONED to IDLE.

        Raises:
            TransitionError: If not in ABANDONED state.
        """
        self._transition(PlanState.IDLE)
        self._session = None

    def check_timeout(self) -> bool:
        """Check if the current session has timed out.

        Returns:
            True if the session has timed out and was auto-abandoned.
        """
        if self._session is None:
            return False

        if self.state in (PlanState.IDLE, PlanState.ABANDONED):
            return False

        elapsed = time.time() - self._session.last_activity
        if elapsed > self._session.timeout_seconds:
            logger.warning(
                "ExitPlanMode: session '%s' timed out after %.1fs",
                self._session.session_id,
                elapsed,
            )
            # Only PLANNING and CONFIRMING can transition to ABANDONED
            if self.state in (PlanState.PLANNING, PlanState.CONFIRMING):
                self._transition(PlanState.ABANDONED)
                return True
            # SPECULATING can go back to PLANNING first
            if self.state == PlanState.SPECULATING:
                self._transition(PlanState.PLANNING)
                self._transition(PlanState.ABANDONED)
                return True

        return False

    @property
    def transition_history(self) -> list[tuple[PlanState, PlanState, float]]:
        """Return the transition history as (from_state, to_state, timestamp) tuples."""
        return list(self._history)

    def __repr__(self) -> str:
        session_id = self._session.session_id if self._session else "none"
        return f"ExitPlanModeController(state={self.state}, session={session_id})"
