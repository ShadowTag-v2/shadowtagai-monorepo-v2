# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Agent Progression Tracker — Track agent capability evolution.

Monitors and records agent skill acquisitions, capability gaps, and
progression milestones across sessions. Maps to tool_contracts/agent.progression.yaml.
"""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_FILE = REPO_ROOT / ".agent" / "evidence" / "index.ndjson"
HEARTBEAT_FILE = REPO_ROOT / ".beads" / "kairos_heartbeat.json"


class AgentProgression:
  """Track agent capability progression and skill fleet evolution.

  Records:
      - Skill acquisitions and retirements
      - Capability gap discoveries and closures
      - Session milestone events
  """

  def __init__(self, repo_root: Path | None = None) -> None:
    self._root = (repo_root or REPO_ROOT).resolve()
    self._evidence = self._root / ".agent" / "evidence" / "index.ndjson"
    self._events: list[dict[str, Any]] = []

  def record_skill_acquired(self, skill_name: str, source: str) -> dict[str, Any]:
    """Record a new skill acquisition.

    Args:
        skill_name: The kebab-case skill directory name.
        source: Origin (e.g., 'google/skills', 'vercel-labs/skills', 'manual').

    Returns:
        The event record.
    """
    event = {
      "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
      "action": "skill_acquired",
      "skill": skill_name,
      "source": source,
    }
    self._events.append(event)
    self._append_evidence(event)
    logger.info("Skill acquired: %s from %s", skill_name, source)
    return event

  def record_skill_retired(self, skill_name: str, reason: str) -> dict[str, Any]:
    """Record a skill retirement/archival.

    Args:
        skill_name: The skill being archived.
        reason: Why it was retired (e.g., 'redundant', 'superseded').

    Returns:
        The event record.
    """
    event = {
      "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
      "action": "skill_retired",
      "skill": skill_name,
      "reason": reason,
    }
    self._events.append(event)
    self._append_evidence(event)
    logger.info("Skill retired: %s (%s)", skill_name, reason)
    return event

  def record_gap_discovered(self, capability: str, context: str) -> dict[str, Any]:
    """Record a capability gap discovery.

    Args:
        capability: What capability is missing.
        context: Where/why it was discovered.

    Returns:
        The event record.
    """
    event = {
      "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
      "action": "gap_discovered",
      "capability": capability,
      "context": context,
    }
    self._events.append(event)
    self._append_evidence(event)
    logger.info("Gap discovered: %s", capability)
    return event

  def record_gap_closed(self, capability: str, resolution: str) -> dict[str, Any]:
    """Record a capability gap closure.

    Args:
        capability: The gap that was closed.
        resolution: How it was resolved.

    Returns:
        The event record.
    """
    event = {
      "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
      "action": "gap_closed",
      "capability": capability,
      "resolution": resolution,
    }
    self._events.append(event)
    self._append_evidence(event)
    logger.info("Gap closed: %s via %s", capability, resolution)
    return event

  def record_milestone(self, milestone: str, details: str) -> dict[str, Any]:
    """Record a progression milestone.

    Args:
        milestone: Milestone identifier (e.g., 'v12.3_hardened').
        details: Description of what was achieved.

    Returns:
        The event record.
    """
    event = {
      "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
      "action": "milestone",
      "milestone": milestone,
      "details": details,
    }
    self._events.append(event)
    self._append_evidence(event)
    logger.info("Milestone: %s", milestone)
    return event

  def get_events(self) -> list[dict[str, Any]]:
    """Return all recorded events in this session."""
    return list(self._events)

  def _append_evidence(self, event: dict[str, Any]) -> None:
    """Append an event to the evidence file."""
    self._evidence.parent.mkdir(parents=True, exist_ok=True)
    with open(self._evidence, "a") as f:
      f.write(json.dumps(event) + "\n")
