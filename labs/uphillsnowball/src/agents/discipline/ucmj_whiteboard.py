"""UCMJ Whiteboard — Optimistic Concurrency Control & Drag Race SLAs.

Agents don't just "time out" — they hallucinate over each other.
They must be physically constrained by OCC locks and court-martialed
if they hang.

SwarmWhiteboard: Redis-backed Optimistic Concurrency Control to
    prevent hallucination collisions. Two agents cannot write to
    the same issue without version conflict detection.

ucmj_drag_race_sla: Article 92 (Failure to Obey) timeout enforcement.
    If an agent exceeds its SLA, it is replaced. No exceptions.
    No second chances. The mission continues without it.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any
from collections.abc import Callable, Coroutine

import redis

logger = logging.getLogger("UCMJ-Discipline")

# Default UCMJ Article 92 timeout (35 seconds)
_DEFAULT_SLA_MS = 35000


class SwarmWhiteboard:
  """Optimistic Concurrency Control to prevent hallucination collisions.

  Uses Redis WATCH/MULTI/EXEC for atomic version-checked writes.
  If two agents attempt to write the same issue simultaneously,
  the slower agent gets a version conflict and must retry.

  This prevents the most dangerous failure mode: two agents
  independently modifying the same state, each believing their
  view is current.

  Args:
      redis_url: Redis connection URL.
  """

  def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
    self.r = redis.Redis.from_url(redis_url, decode_responses=True)

  def read_state(self, issue_id: str) -> dict:
    """Read the current whiteboard state for an issue.

    Args:
        issue_id: The issue identifier.

    Returns:
        Current state dict with version number.
    """
    key = f"whiteboard:{issue_id}"
    raw = self.r.get(key)
    if raw is None:
      return {"version": 0, "data": {}}
    return json.loads(raw)

  def write_state(
    self,
    issue_id: str,
    expected_version: int,
    new_data: dict,
  ) -> bool:
    """Atomically write state with OCC version check.

    Uses Redis WATCH to detect concurrent modifications.
    If another agent modified the state between our read and
    write, the transaction fails.

    Args:
        issue_id: The issue identifier.
        expected_version: The version we expect (from our last read).
        new_data: The new state data to write.

    Returns:
        True if write succeeded, False if version conflict.
    """
    key = f"whiteboard:{issue_id}"

    with self.r.pipeline() as pipe:
      try:
        pipe.watch(key)
        raw = pipe.get(key)
        current = json.loads(raw) if raw else {"version": 0}

        if current["version"] != expected_version:
          logger.warning(
            "⚠️ OCC CONFLICT: Issue %s. Expected v%d, got v%d. Agent must re-read and retry.",
            issue_id,
            expected_version,
            current["version"],
          )
          return False

        new_state = {
          "version": current["version"] + 1,
          "data": new_data,
        }

        pipe.multi()
        pipe.set(key, json.dumps(new_state))
        pipe.execute()

        logger.info(
          "✅ Whiteboard write: Issue %s → v%d",
          issue_id,
          new_state["version"],
        )
        return True

      except redis.WatchError:
        logger.warning(
          "⚠️ WATCH CONFLICT: Issue %s modified during transaction. Concurrent agent detected.",
          issue_id,
        )
        return False

  def clear_issue(self, issue_id: str) -> None:
    """Clear the whiteboard state for a completed issue.

    Args:
        issue_id: The issue identifier.
    """
    self.r.delete(f"whiteboard:{issue_id}")


async def ucmj_drag_race_sla(
  agent_task: Callable[[], Coroutine[Any, Any, dict]],
  timeout_ms: int = _DEFAULT_SLA_MS,
  agent_name: str = "UNKNOWN",
) -> dict:
  """Article 92: Failure to Obey — UCMJ timeout enforcement.

  If an agent exceeds its SLA, it is court-martialed (replaced).
  The mission continues without it.

  The 35-second default matches the C++ ZMQ IPC round-trip budget
  for the Midas quant engine.

  Args:
      agent_task: Async callable that returns the agent's result.
      timeout_ms: Maximum execution time in milliseconds.
      agent_name: Agent identifier for logging.

  Returns:
      Agent result on success, or ARTICLE_92_VIOLATION on timeout.
  """
  try:
    result = await asyncio.wait_for(
      agent_task(),
      timeout=timeout_ms / 1000.0,
    )
    logger.info("✅ Agent %s completed within SLA (%dms).", agent_name, timeout_ms)
    return result

  except TimeoutError:
    logger.critical(
      "⏰ UCMJ ARTICLE 92 VIOLATION: Agent %s exceeded %dms SLA. Court-martial initiated. Agent will be replaced.",
      agent_name,
      timeout_ms,
    )
    return {
      "status": "HUNG",
      "agent": agent_name,
      "sla_ms": timeout_ms,
      "directive": "REPLACE_AGENT",
      "ucmj": "ARTICLE_92_VIOLATION",
    }
