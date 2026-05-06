# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""ADK 2.0 Graph Workflow Orchestrator for CounselConduit.

Routes multi-model legal AI queries as a dumb proxy through
Oracle Studio analysis and Vent Mode ephemeral sessions.
Zero data inspection — attorney-client privilege preserved.

Architecture:
    Client -> AG-UI SSE -> Orchestrator -> Model Router
                                        -> [Oracle Studio] -> Memo Generator
                                        -> [Vent Mode] -> Ephemeral Session
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AgentRole(StrEnum):
    """Agent roles in the CounselConduit multi-agent topology."""

    ORCHESTRATOR = "orchestrator"
    ORACLE = "oracle"
    VENT = "vent"

    MODEL_ROUTER = "model_router"


class TaskState(StrEnum):
    """A2A Task lifecycle states (per Google A2A spec)."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"


@dataclass
class TaskContext:
    """Context for a single A2A task execution."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    tenant_id: str = ""
    user_id: str = ""
    role: AgentRole = AgentRole.ORCHESTRATOR
    state: TaskState = TaskState.SUBMITTED
    model_preference: str = "gemini-3.1-flash-lite-preview-thinking"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """ADK 2.0 Graph Workflow Orchestrator.

    Routes incoming A2A tasks to the appropriate sub-agent (Oracle or Vent).
    Pure proxy — zero content inspection.
    """

    def __init__(self) -> None:
        self._active_tasks: dict[str, TaskContext] = {}

    async def submit_task(
        self,
        prompt: str,
        *,
        tenant_id: str,
        user_id: str,
        session_id: str = "",
        model: str = "gemini-3.1-flash-lite-preview-thinking",
        metadata: dict[str, Any] | None = None,
    ) -> TaskContext:
        """Submit a new task to the orchestrator.

        Args:
            prompt: The user's query.
            tenant_id: The law firm tenant ID.
            user_id: The authenticated user ID.
            session_id: Optional session ID for continuity.
            model: Preferred model for inference.
            metadata: Additional task metadata.

        Returns:
            TaskContext with initial state.

        Raises:
            PermissionError: If required routing fields are missing.
        """
        if not tenant_id:
            raise PermissionError("DENY: No tenant_id provided")
        if not user_id:
            raise PermissionError("DENY: No user_id provided")

        ctx = TaskContext(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id or str(uuid.uuid4()),
            model_preference=model,
            metadata=metadata or {},
        )

        ctx.state = TaskState.WORKING
        self._active_tasks[ctx.task_id] = ctx

        logger.info(
            "Task %s submitted: tenant=%s model=%s",
            ctx.task_id,
            ctx.tenant_id,
            ctx.model_preference,
        )
        return ctx

    async def route_task(self, ctx: TaskContext, prompt: str) -> AgentRole:
        """Route a task to the appropriate sub-agent.

        Args:
            ctx: The task context.
            prompt: The user's query.

        Returns:
            The AgentRole the task was routed to.
        """
        # Vent Mode: ephemeral, privilege-preserving sessions
        if ctx.metadata.get("mode") == "vent":
            logger.info("Routing task %s to VENT mode", ctx.task_id)
            return AgentRole.VENT

        # Default: Oracle Studio (7-stage pipeline)
        logger.info("Routing task %s to ORACLE studio", ctx.task_id)
        return AgentRole.ORACLE

    def get_task(self, task_id: str) -> TaskContext | None:
        """Retrieve a task by ID."""
        return self._active_tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        ctx = self._active_tasks.get(task_id)
        if ctx and ctx.state == TaskState.WORKING:
            ctx.state = TaskState.CANCELED
            return True
        return False
