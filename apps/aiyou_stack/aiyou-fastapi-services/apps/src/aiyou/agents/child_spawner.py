"""Child Spawner: Dynamic agent spawning and lifecycle management.

Partners (L3+) can spawn child agents to handle subtasks. This module
manages the spawning, supervision, and retirement of child agents.

Features:
- Resource-aware spawning with limits per parent
- Automatic lifecycle management (warm-up, active, cooldown, retire)
- Parent-child relationship tracking
- Revenue attribution to parent

Usage:
    spawner = ChildSpawner(max_children_per_parent=10)
    child = await spawner.spawn(
        parent_id="agent_123",
        task_type="data_processing",
        ttl_seconds=3600
    )
    result = await child.execute(task)
    await spawner.retire(child.agent_id)
"""

import asyncio
import contextlib
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from .bar_exam_protocol import AgentLevel

logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """Agent lifecycle states."""

    SPAWNING = "spawning"  # Being initialized
    WARMING = "warming"  # Loading context/models
    ACTIVE = "active"  # Ready for tasks
    BUSY = "busy"  # Executing task
    COOLDOWN = "cooldown"  # Post-task wind-down
    RETIRING = "retiring"  # Cleanup in progress
    RETIRED = "retired"  # No longer active


@dataclass
class SpawnRequest:
    """Request to spawn a child agent."""

    parent_id: str
    task_type: str
    ttl_seconds: int = 3600  # 1 hour default
    priority: int = 1  # 1-5, higher = more resources
    inherit_context: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentLifecycle:
    """Tracks lifecycle of a spawned agent."""

    agent_id: str
    parent_id: str
    state: LifecycleState
    task_type: str
    created_at: datetime
    expires_at: datetime
    tasks_completed: int = 0
    revenue_generated: float = 0.0
    last_active: datetime | None = None
    error_count: int = 0


@dataclass
class ChildAgent:
    """A spawned child agent instance."""

    agent_id: str
    parent_id: str
    task_type: str
    executor: Callable | None = None
    lifecycle: AgentLifecycle | None = None

    async def execute(self, task: Any, timeout: float = 60.0) -> Any:
        """Execute a task using this child agent."""
        if self.executor is None:
            raise RuntimeError("Agent executor not initialized")

        if self.lifecycle:
            self.lifecycle.state = LifecycleState.BUSY
            self.lifecycle.last_active = datetime.now(UTC)

        try:
            result = await asyncio.wait_for(self.executor(task), timeout=timeout)
            if self.lifecycle:
                self.lifecycle.tasks_completed += 1
                self.lifecycle.state = LifecycleState.ACTIVE
            return result
        except Exception:
            if self.lifecycle:
                self.lifecycle.error_count += 1
                self.lifecycle.state = LifecycleState.ACTIVE
            raise

    def is_healthy(self) -> bool:
        """Check if agent is healthy and can accept tasks."""
        if not self.lifecycle:
            return False

        now = datetime.now(UTC)

        # Check expiration
        if now >= self.lifecycle.expires_at:
            return False

        # Check error rate
        if self.lifecycle.tasks_completed > 0:
            error_rate = self.lifecycle.error_count / self.lifecycle.tasks_completed
            if error_rate > 0.5:  # 50% error rate threshold
                return False

        # Check state
        return self.lifecycle.state in (LifecycleState.ACTIVE, LifecycleState.WARMING)


class ChildSpawner:
    """Manages spawning and lifecycle of child agents.

    Partners (L3+) can spawn children to parallelize work. This class
    enforces limits, tracks relationships, and handles cleanup.
    """

    # Limits by parent level
    MAX_CHILDREN = {
        AgentLevel.PARTNER: 5,
        AgentLevel.SENIOR_PARTNER: 15,
        AgentLevel.MANAGING_PARTNER: 50,
    }

    def __init__(
        self,
        max_children_per_parent: int = 10,
        default_ttl_seconds: int = 3600,
        executor_factory: Callable | None = None,
    ):
        """Initialize child spawner.

        Args:
            max_children_per_parent: Global max children per parent
            default_ttl_seconds: Default time-to-live for children
            executor_factory: Factory to create child executors

        """
        self.max_children = max_children_per_parent
        self.default_ttl = default_ttl_seconds
        self.executor_factory = executor_factory or self._default_executor_factory

        # Active children by parent
        self.children: dict[str, dict[str, ChildAgent]] = {}

        # All lifecycle records (for history)
        self.lifecycles: dict[str, AgentLifecycle] = {}

        # Parent level cache
        self.parent_levels: dict[str, AgentLevel] = {}

        # Background cleanup task
        self._cleanup_task: asyncio.Task | None = None

    def _default_executor_factory(self, task_type: str, parent_id: str) -> Callable:
        """Create default executor for a child agent."""

        async def executor(task: Any) -> Any:
            # Placeholder - in production this would route to actual LLM
            logger.info(f"Child executing {task_type} task for parent {parent_id}")
            await asyncio.sleep(0.1)  # Simulate work
            return {"status": "completed", "task_type": task_type}

        return executor

    def set_parent_level(self, parent_id: str, level: AgentLevel) -> None:
        """Set the level of a parent agent."""
        self.parent_levels[parent_id] = level

    def get_max_children(self, parent_id: str) -> int:
        """Get max children allowed for a parent."""
        level = self.parent_levels.get(parent_id, AgentLevel.PARALEGAL)
        return min(self.MAX_CHILDREN.get(level, 0), self.max_children)

    def can_spawn(self, parent_id: str) -> tuple[bool, str]:
        """Check if parent can spawn a new child.

        Returns: (can_spawn, reason)
        """
        level = self.parent_levels.get(parent_id, AgentLevel.PARALEGAL)

        # Must be Partner or higher
        if level < AgentLevel.PARTNER:
            return False, f"Level {level.name} cannot spawn children (need L3+)"

        # Check current children count
        current = len(self.children.get(parent_id, {}))
        max_allowed = self.get_max_children(parent_id)

        if current >= max_allowed:
            return False, f"At maximum children ({current}/{max_allowed})"

        return True, "Can spawn"

    async def spawn(self, request: SpawnRequest, executor: Callable | None = None) -> ChildAgent:
        """Spawn a new child agent.

        Args:
            request: SpawnRequest with parent info and task type
            executor: Optional custom executor (uses factory if None)

        Returns:
            ChildAgent ready to execute tasks

        Raises:
            PermissionError: If parent cannot spawn

        """
        can, reason = self.can_spawn(request.parent_id)
        if not can:
            raise PermissionError(f"Cannot spawn: {reason}")

        # Generate unique ID
        agent_id = f"child_{request.parent_id}_{uuid.uuid4().hex[:8]}"

        # Create lifecycle record
        now = datetime.now(UTC)
        ttl = request.ttl_seconds or self.default_ttl
        lifecycle = AgentLifecycle(
            agent_id=agent_id,
            parent_id=request.parent_id,
            state=LifecycleState.SPAWNING,
            task_type=request.task_type,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
        )
        self.lifecycles[agent_id] = lifecycle

        # Create child agent
        child_executor = executor or self.executor_factory(request.task_type, request.parent_id)

        child = ChildAgent(
            agent_id=agent_id,
            parent_id=request.parent_id,
            task_type=request.task_type,
            executor=child_executor,
            lifecycle=lifecycle,
        )

        # Register with parent
        if request.parent_id not in self.children:
            self.children[request.parent_id] = {}
        self.children[request.parent_id][agent_id] = child

        # Warm up
        lifecycle.state = LifecycleState.WARMING
        await self._warm_up(child, request)
        lifecycle.state = LifecycleState.ACTIVE

        logger.info(f"Spawned child {agent_id} for parent {request.parent_id}")
        return child

    async def _warm_up(self, child: ChildAgent, request: SpawnRequest) -> None:
        """Warm up a child agent (load context, etc.)."""
        # In production, this would load relevant context
        await asyncio.sleep(0.01)  # Minimal warm-up

    async def retire(self, agent_id: str, force: bool = False) -> bool:
        """Retire a child agent.

        Args:
            agent_id: ID of child to retire
            force: Force immediate retirement

        Returns:
            True if retired successfully

        """
        lifecycle = self.lifecycles.get(agent_id)
        if not lifecycle:
            return False

        lifecycle.state = LifecycleState.RETIRING

        # Find and remove from parent's children
        parent_children = self.children.get(lifecycle.parent_id, {})
        if agent_id in parent_children:
            del parent_children[agent_id]

        # Cleanup (in production: save state, release resources)
        if not force:
            await asyncio.sleep(0.01)  # Graceful cooldown

        lifecycle.state = LifecycleState.RETIRED
        logger.info(f"Retired child {agent_id} (tasks: {lifecycle.tasks_completed})")

        return True

    async def retire_all(self, parent_id: str) -> int:
        """Retire all children of a parent. Returns count retired."""
        children = list(self.children.get(parent_id, {}).values())
        count = 0
        for child in children:
            if await self.retire(child.agent_id):
                count += 1
        return count

    def get_children(self, parent_id: str) -> list[ChildAgent]:
        """Get all active children of a parent."""
        return list(self.children.get(parent_id, {}).values())

    def get_child(self, agent_id: str) -> ChildAgent | None:
        """Get a specific child agent."""
        for parent_children in self.children.values():
            if agent_id in parent_children:
                return parent_children[agent_id]
        return None

    async def cleanup_expired(self) -> int:
        """Retire all expired children. Returns count retired."""
        now = datetime.now(UTC)
        count = 0

        for lifecycle in list(self.lifecycles.values()):
            if lifecycle.state not in (LifecycleState.RETIRED, LifecycleState.RETIRING):  # noqa: SIM102
                if now >= lifecycle.expires_at:  # noqa: SIM102
                    if await self.retire(lifecycle.agent_id):
                        count += 1

        return count

    async def start_cleanup_loop(self, interval_seconds: int = 60) -> None:
        """Start background cleanup loop."""

        async def cleanup_loop():
            while True:
                try:
                    retired = await self.cleanup_expired()
                    if retired > 0:
                        logger.debug(f"Cleanup retired {retired} expired children")
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(interval_seconds)

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def stop_cleanup_loop(self) -> None:
        """Stop background cleanup loop."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task
            self._cleanup_task = None

    def get_stats(self, parent_id: str | None = None) -> dict[str, Any]:
        """Get spawner statistics."""
        if parent_id:
            children = self.get_children(parent_id)
            return {
                "parent_id": parent_id,
                "active_children": len(children),
                "max_children": self.get_max_children(parent_id),
                "total_tasks": sum(c.lifecycle.tasks_completed for c in children if c.lifecycle),
                "total_revenue": sum(
                    c.lifecycle.revenue_generated for c in children if c.lifecycle
                ),
                "children": [
                    {
                        "agent_id": c.agent_id,
                        "task_type": c.task_type,
                        "state": c.lifecycle.state.value if c.lifecycle else None,
                        "tasks": c.lifecycle.tasks_completed if c.lifecycle else 0,
                    }
                    for c in children
                ],
            }
        total_children = sum(len(c) for c in self.children.values())
        total_parents = len(self.children)
        return {
            "total_parents": total_parents,
            "total_active_children": total_children,
            "total_lifecycles": len(self.lifecycles),
        }

    def attribute_revenue(self, agent_id: str, amount: float) -> bool:
        """Attribute revenue to a child agent."""
        lifecycle = self.lifecycles.get(agent_id)
        if lifecycle:
            lifecycle.revenue_generated += amount
            return True
        return False
