# labs/uphillsnowball/agent/memory.py
"""Agent Memory: Cross-Session State Persistence.

The Hippocampus layer of the Tri-Mind Topology.
Persists agent state, task history, and learned patterns
across sessions using Firestore.

Collections (in 'shadowtag-engine' database):
    agent_state/     — Current agent configuration and status
    task_history/    — Completed task records
    learned/         — Patterns and heuristics discovered by agents
    context_cache/   — Cached context windows for session resume
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("uphillsnowball.memory")

_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_DATABASE_ID = os.getenv("MEMORY_DATABASE", "shadowtag-engine")


@dataclass
class AgentState:
  """Persistent state for a single agent."""

  agent_id: str
  role: str
  status: str = "idle"  # idle | active | error | suspended
  current_task: str = ""
  tasks_completed: int = 0
  tokens_consumed: int = 0
  last_active: float = field(default_factory=time.time)
  config: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskRecord:
  """Completed task record for institutional memory."""

  task_id: str
  description: str
  agent_role: str
  status: str  # completed | failed | cancelled
  result_summary: str = ""
  duration_ms: int = 0
  tokens_used: int = 0
  risk_score: int = 0
  completed_at: float = field(default_factory=time.time)


@dataclass
class LearnedPattern:
  """A pattern or heuristic discovered by agents."""

  pattern_id: str
  category: str  # code | architecture | risk | performance
  description: str
  confidence: float = 0.8
  times_applied: int = 0
  discovered_at: float = field(default_factory=time.time)


class AgentMemory:
  """Cross-session memory persistence using Firestore.

  Uses the 'shadowtag-engine' database (separate from the default
  CounselConduit database for isolation).
  """

  def __init__(self) -> None:
    self._db = None

  def _get_db(self):
    """Lazy-initialize Firestore client for memory database."""
    if self._db is None:
      try:
        from google.cloud import firestore

        self._db = firestore.AsyncClient(
          project=_PROJECT_ID,
          database=_DATABASE_ID,
        )
        logger.info("Memory DB connected: %s/%s", _PROJECT_ID, _DATABASE_ID)
      except Exception as e:
        logger.warning("Memory DB unavailable (offline mode): %s", e)
    return self._db

  async def save_agent_state(self, state: AgentState) -> None:
    """Persist current agent state."""
    db = self._get_db()
    if db is None:
      logger.debug("Offline mode — state not persisted: %s", state.agent_id)
      return

    state.last_active = time.time()
    await (
      db.collection("agent_state")
      .document(state.agent_id)
      .set(
        {
          "role": state.role,
          "status": state.status,
          "current_task": state.current_task,
          "tasks_completed": state.tasks_completed,
          "tokens_consumed": state.tokens_consumed,
          "last_active": state.last_active,
          "config": state.config,
        }
      )
    )

  async def load_agent_state(self, agent_id: str) -> AgentState | None:
    """Load persisted agent state."""
    db = self._get_db()
    if db is None:
      return None

    doc = await db.collection("agent_state").document(agent_id).get()
    if doc.exists:
      data = doc.to_dict()
      return AgentState(agent_id=agent_id, **data)
    return None

  async def record_task(self, record: TaskRecord) -> None:
    """Record a completed task for institutional memory."""
    db = self._get_db()
    if db is None:
      return

    await (
      db.collection("task_history")
      .document(record.task_id)
      .set(
        {
          "description": record.description,
          "agent_role": record.agent_role,
          "status": record.status,
          "result_summary": record.result_summary,
          "duration_ms": record.duration_ms,
          "tokens_used": record.tokens_used,
          "risk_score": record.risk_score,
          "completed_at": record.completed_at,
        }
      )
    )

  async def save_learned_pattern(self, pattern: LearnedPattern) -> None:
    """Persist a discovered pattern."""
    db = self._get_db()
    if db is None:
      return

    await (
      db.collection("learned")
      .document(pattern.pattern_id)
      .set(
        {
          "category": pattern.category,
          "description": pattern.description,
          "confidence": pattern.confidence,
          "times_applied": pattern.times_applied,
          "discovered_at": pattern.discovered_at,
        }
      )
    )

  async def get_recent_tasks(self, limit: int = 20) -> list[TaskRecord]:
    """Retrieve recent task history for context."""
    db = self._get_db()
    if db is None:
      return []

    query = (
      db.collection("task_history")
      .order_by("completed_at", direction="DESCENDING")
      .limit(limit)
    )

    results = []
    async for doc in query.stream():
      data = doc.to_dict()
      results.append(TaskRecord(task_id=doc.id, **data))
    return results


# ── Singleton ──────────────────────────────────────────────────────────────

_memory: AgentMemory | None = None


def get_memory() -> AgentMemory:
  """Get or create the singleton AgentMemory."""
  global _memory  # noqa: PLW0603
  if _memory is None:
    _memory = AgentMemory()
  return _memory
