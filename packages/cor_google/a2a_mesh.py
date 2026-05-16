# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
A2A Mesh — Google Interactions API agent-to-agent routing.

Replaces XML-based tengu_scratch/ payloads with typed A2A task dispatch.
Agent cards are stored in Firestore via GCPSubstrate.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
  """Declared capabilities for A2A agent cards."""

  CODE_MUTATION = "code_mutation"
  SECURITY_AUDIT = "security_audit"
  PERFORMANCE_PROFILING = "performance_profiling"
  DEAD_CODE_ELIMINATION = "dead_code_elimination"
  LINT_FIX = "lint_fix"
  DEPLOYMENT = "deployment"
  KNOWLEDGE_DISTILLATION = "knowledge_distillation"
  DESIGN_SYSTEM = "design_system"
  BROWSER_AUTOMATION = "browser_automation"


@dataclass
class AgentCard:
  """A2A Agent Card — declares identity and capabilities."""

  agent_id: str
  display_name: str
  capabilities: list[AgentCapability]
  endpoint: str = ""
  model_id: str = "gemini-3.1-flash-lite-preview-thinking"
  version: str = "1.0.0"
  metadata: dict[str, Any] = field(default_factory=dict)

  def to_dict(self) -> dict[str, Any]:
    return {
      "agent_id": self.agent_id,
      "display_name": self.display_name,
      "capabilities": [c.value for c in self.capabilities],
      "endpoint": self.endpoint,
      "model_id": self.model_id,
      "version": self.version,
      "metadata": self.metadata,
      "registered_ns": time.time_ns(),
    }


class TaskStatus(Enum):
  """A2A task lifecycle states."""

  PENDING = "pending"
  RUNNING = "running"
  COMPLETED = "completed"
  FAILED = "failed"
  CANCELLED = "cancelled"


@dataclass
class A2ATask:
  """A2A Task — unit of work dispatched between agents."""

  task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
  source_agent: str = ""
  target_agent: str = ""
  capability: AgentCapability = AgentCapability.CODE_MUTATION
  payload: dict[str, Any] = field(default_factory=dict)
  status: TaskStatus = TaskStatus.PENDING
  result: dict[str, Any] = field(default_factory=dict)
  created_ns: int = field(default_factory=time.time_ns)
  completed_ns: int = 0

  def to_dict(self) -> dict[str, Any]:
    return {
      "task_id": self.task_id,
      "source_agent": self.source_agent,
      "target_agent": self.target_agent,
      "capability": self.capability.value,
      "payload": self.payload,
      "status": self.status.value,
      "result": self.result,
      "created_ns": self.created_ns,
      "completed_ns": self.completed_ns,
    }


class A2AMesh:
  """
  Agent-to-Agent mesh router.

  Manages agent registration, capability-based routing,
  and task lifecycle. Integrates with GCPSubstrate for persistence
  and AGUIEventBus for event emission.
  """

  def __init__(self) -> None:
    self._agents: dict[str, AgentCard] = {}
    self._tasks: dict[str, A2ATask] = {}
    self._capability_index: dict[AgentCapability, list[str]] = {}

  def register_agent(self, card: AgentCard) -> None:
    """Register an agent card and index its capabilities."""
    self._agents[card.agent_id] = card
    for cap in card.capabilities:
      if cap not in self._capability_index:
        self._capability_index[cap] = []
      if card.agent_id not in self._capability_index[cap]:
        self._capability_index[cap].append(card.agent_id)
    logger.info(
      "A2A: registered agent %s with %d capabilities",
      card.agent_id,
      len(card.capabilities),
    )

  def find_agents(self, capability: AgentCapability) -> list[AgentCard]:
    """Find agents that declare a specific capability."""
    agent_ids = self._capability_index.get(capability, [])
    return [self._agents[aid] for aid in agent_ids if aid in self._agents]

  def dispatch_task(
    self,
    source: str,
    capability: AgentCapability,
    payload: dict[str, Any],
    target: str | None = None,
  ) -> A2ATask:
    """
    Dispatch a task to an agent by capability.

    If target is not specified, routes to the first agent
    declaring the required capability.
    """
    if target is None:
      agents = self.find_agents(capability)
      if not agents:
        task = A2ATask(
          source_agent=source,
          capability=capability,
          payload=payload,
          status=TaskStatus.FAILED,
          result={"error": f"No agent found for capability {capability.value}"},
        )
        self._tasks[task.task_id] = task
        return task
      target = agents[0].agent_id

    task = A2ATask(
      source_agent=source,
      target_agent=target,
      capability=capability,
      payload=payload,
      status=TaskStatus.PENDING,
    )
    self._tasks[task.task_id] = task
    logger.info("A2A: dispatched task %s → %s (%s)", source, target, capability.value)
    return task

  def complete_task(
    self, task_id: str, result: dict[str, Any], success: bool = True
  ) -> A2ATask | None:
    """Mark a task as completed or failed."""
    task = self._tasks.get(task_id)
    if task is None:
      return None
    task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
    task.result = result
    task.completed_ns = time.time_ns()
    return task

  def get_task(self, task_id: str) -> A2ATask | None:
    return self._tasks.get(task_id)

  def list_agents(self) -> list[dict[str, Any]]:
    return [card.to_dict() for card in self._agents.values()]

  def list_tasks(
    self, status: TaskStatus | None = None, limit: int = 50
  ) -> list[dict[str, Any]]:
    tasks = list(self._tasks.values())
    if status:
      tasks = [t for t in tasks if t.status == status]
    tasks.sort(key=lambda t: t.created_ns, reverse=True)
    return [t.to_dict() for t in tasks[:limit]]

  @property
  def agent_count(self) -> int:
    return len(self._agents)

  @property
  def task_count(self) -> int:
    return len(self._tasks)
