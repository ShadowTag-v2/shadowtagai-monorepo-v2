# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AgentOps Integration: Full observability for autonomous agents.

Provides:
- Session tracking across multi-cycle workflows
- Event recording for thoughts, actions, observations
- Cost tracking and budget alerts
- Performance metrics and dashboards
- Trace hierarchy for complex agent interactions
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

try:
    import agentops

    AGENTOPS_AVAILABLE = True
except ImportError:
    AGENTOPS_AVAILABLE = False
    logging.warning("AgentOps SDK not installed. Install with: pip install agentops")

from kosmos.core.orchestrator import ReActResult, ReActStep

logger = logging.getLogger(__name__)


@dataclass
class AgentSession:
    """Represents an AgentOps session for tracking."""

    session_id: str
    goal: str
    agent_name: str
    started_at: datetime
    tags: list[str]
    session_obj: Any | None = None  # AgentOps session object


class AgentOpsTracker:
    """AgentOps integration for Kosmos agents.

    Tracks:
    - Multi-agent sessions across workflow phases
    - Individual ReAct cycles with thought/action/observation
    - Token usage and cost per operation
    - Success/failure metrics
    - Long-horizon task completion
    """

    def __init__(
        self,
        api_key: str | None = None,
        auto_start_session: bool = True,
        tags: list[str] | None = None,
    ):
        """Initialize AgentOps tracker.

        Args:
            api_key: AgentOps API key (reads from AGENTOPS_API_KEY env var if None)
            auto_start_session: Whether to auto-start a session
            tags: Default tags for all sessions

        """
        if not AGENTOPS_AVAILABLE:
            logger.warning("AgentOps not available - tracking will be no-op")
            self.enabled = False
            return

        self.enabled = True
        self.api_key = api_key or os.getenv("AGENTOPS_API_KEY")

        if not self.api_key:
            logger.warning("No AgentOps API key provided - tracking disabled")
            self.enabled = False
            return

        # Initialize AgentOps
        agentops.init(api_key=self.api_key, auto_start_session=auto_start_session)
        logger.info("AgentOps tracker initialized")

        self.default_tags = tags or ["kosmos", "autonomous-agent"]
        self.current_session: AgentSession | None = None

    def start_session(
        self,
        goal: str,
        agent_name: str,
        session_id: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Start a new AgentOps session for tracking.

        Args:
            goal: Research goal/task description
            agent_name: Name of the agent
            session_id: Optional explicit session ID
            tags: Additional tags for this session

        Returns:
            Session ID

        """
        if not self.enabled:
            return "no-op"

        all_tags = self.default_tags + (tags or [])
        all_tags.append(agent_name)

        # Start AgentOps session
        session_obj = agentops.start_session(tags=all_tags)

        self.current_session = AgentSession(
            session_id=session_id
            or str(session_obj.session_id if hasattr(session_obj, "session_id") else "unknown"),
            goal=goal,
            agent_name=agent_name,
            started_at=datetime.utcnow(),
            tags=all_tags,
            session_obj=session_obj,
        )

        # Record session start event
        self.record_event(
            event_type="session_start",
            data={
                "goal": goal,
                "agent": agent_name,
                "tags": all_tags,
            },
        )

        logger.info(f"Started AgentOps session: {self.current_session.session_id}")
        return self.current_session.session_id

    def end_session(
        self,
        result: str = "success",
        final_output: str | None = None,
    ):
        """End the current AgentOps session.

        Args:
            result: Session result ("success", "failure", "timeout")
            final_output: Optional final output/answer

        """
        if not self.enabled or not self.current_session:
            return

        self.record_event(
            event_type="session_end",
            data={
                "result": result,
                "final_output": final_output,
                "duration_seconds": (
                    datetime.utcnow() - self.current_session.started_at
                ).total_seconds(),
            },
        )

        # End AgentOps session
        agentops.end_session(result)

        logger.info(
            f"Ended AgentOps session: {self.current_session.session_id} with result: {result}",
        )
        self.current_session = None

    def record_thought(self, iteration: int, thought: str):
        """Record a reasoning thought from ReAct loop.

        Args:
            iteration: Loop iteration number
            thought: Thought/reasoning text

        """
        self.record_event(
            event_type="thought",
            data={
                "iteration": iteration,
                "thought": thought,
            },
        )

    def record_action(
        self,
        iteration: int,
        action: str,
        action_input: Any,
    ):
        """Record an action (tool invocation) from ReAct loop.

        Args:
            iteration: Loop iteration number
            action: Tool name
            action_input: Tool parameters

        """
        self.record_event(
            event_type="action",
            data={
                "iteration": iteration,
                "action": action,
                "action_input": action_input,
            },
        )

    def record_observation(
        self,
        iteration: int,
        observation: str,
        tokens: int | None = None,
        cost: float | None = None,
    ):
        """Record an observation (tool result) from ReAct loop.

        Args:
            iteration: Loop iteration number
            observation: Tool result text
            tokens: Optional token count
            cost: Optional cost in USD

        """
        self.record_event(
            event_type="observation",
            data={
                "iteration": iteration,
                "observation": observation[:1000],  # Truncate long observations
                "observation_length": len(observation),
                "tokens": tokens,
                "cost": cost,
            },
        )

    def record_react_step(self, step: ReActStep, cost: float | None = None):
        """Record a complete ReAct step (thought + action + observation).

        Args:
            step: ReActStep instance
            cost: Optional cost for this step

        """
        if not self.enabled:
            return

        self.record_thought(step.iteration, step.thought)

        if step.action:
            self.record_action(step.iteration, step.action, step.action_input)

        if step.observation:
            self.record_observation(step.iteration, step.observation, cost=cost)

    def record_react_result(self, result: ReActResult):
        """Record a complete ReAct cycle result.

        Args:
            result: ReActResult instance

        """
        if not self.enabled:
            return

        self.record_event(
            event_type="react_cycle_complete",
            data={
                "success": result.success,
                "total_iterations": result.total_iterations,
                "termination_reason": result.termination_reason,
                "has_final_answer": result.final_answer is not None,
                "error": result.error,
            },
        )

    def record_event(
        self,
        event_type: str,
        data: dict[str, Any],
    ):
        """Record a custom event.

        Args:
            event_type: Type of event
            data: Event data dictionary

        """
        if not self.enabled:
            return

        try:
            agentops.record(
                agentops.Event(
                    event_type=event_type,
                    **data,
                ),
            )
        except Exception as e:
            logger.error(f"Failed to record AgentOps event: {e}")

    def record_error(
        self,
        error_type: str,
        error_message: str,
        context: dict[str, Any] | None = None,
    ):
        """Record an error event.

        Args:
            error_type: Error type/category
            error_message: Error message
            context: Optional error context

        """
        self.record_event(
            event_type="error",
            data={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {},
            },
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - end session on exit."""
        if self.current_session:
            result = "failure" if exc_type else "success"
            self.end_session(result=result)

    def __repr__(self) -> str:
        return (
            f"AgentOpsTracker(enabled={self.enabled}, "
            f"current_session={self.current_session.session_id if self.current_session else None})"
        )
