# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""IdleReturn Dialog — P1 #6 from Kairos Ultraplan.

Ported from: Claude Code src/services/idleReturn.ts (inferred)

When the loop steward detects that the user has returned after an
idle period, it presents a structured summary of what happened during
the autonomous period rather than dumping raw logs.

Usage:
    from packages.agnt_tools.idle_return import IdleReturnDialog
    dialog = IdleReturnDialog()
    summary = dialog.build(cycle_reports)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger("agnt.idle_return")

BEADS_DIR = (
  Path.home() / ".gemini" / "antigravity" / "Monorepo-Uphillsnowball" / ".beads"
)


@dataclass
class CycleReport:
  """Summary of a single steward cycle."""

  cycle_number: int = 0
  timestamp: str = ""
  actions_taken: int = 0
  details: list[str] = field(default_factory=list)
  verdict: str = ""


@dataclass
class IdleSummary:
  """Structured summary for user return."""

  idle_duration_minutes: float = 0
  cycles_executed: int = 0
  total_actions: int = 0
  key_events: list[str] = field(default_factory=list)
  warnings: list[str] = field(default_factory=list)
  capacity_suspensions: int = 0
  formatted: str = ""


class IdleReturnDialog:
  """Build a structured return-from-idle summary.

  Instead of dumping raw cycle logs, this synthesizes a human-readable
  summary that answers:
    1. How long was I away?
    2. What did the steward do?
    3. Were there any problems?
    4. What needs my attention?
  """

  def __init__(self) -> None:
    self._state_file = BEADS_DIR / "idle_return_state.json"
    BEADS_DIR.mkdir(parents=True, exist_ok=True)

  def record_user_departure(self) -> None:
    """Record when the user stops interacting."""
    state = {"departed_at": datetime.now(UTC).isoformat(), "cycles_since": []}
    self._state_file.write_text(json.dumps(state, indent=2))

  def record_cycle(self, report: CycleReport) -> None:
    """Append a cycle summary to the idle state."""
    state = self._load_state()
    state.setdefault("cycles_since", []).append(
      {
        "cycle": report.cycle_number,
        "ts": report.timestamp or datetime.now(UTC).isoformat(),
        "actions": report.actions_taken,
        "details": report.details[:5],  # Cap to prevent bloat
        "verdict": report.verdict,
      }
    )
    self._state_file.write_text(json.dumps(state, indent=2))

  def build(self, cycle_reports: list[CycleReport] | None = None) -> IdleSummary:
    """Build the return-from-idle summary.

    Args:
        cycle_reports: Optional list of reports. If None, loads from state file.

    Returns:
        IdleSummary with structured summary and formatted text.
    """
    state = self._load_state()
    departed_at = state.get("departed_at", "")
    cycles = state.get("cycles_since", [])

    if cycle_reports:
      cycles = [
        {
          "cycle": r.cycle_number,
          "actions": r.actions_taken,
          "details": r.details[:5],
          "verdict": r.verdict,
        }
        for r in cycle_reports
      ]

    summary = IdleSummary()

    # Calculate idle duration
    if departed_at:
      try:
        dep_dt = datetime.fromisoformat(departed_at)
        summary.idle_duration_minutes = (
          datetime.now(UTC) - dep_dt
        ).total_seconds() / 60
      except ValueError, TypeError:
        pass

    summary.cycles_executed = len(cycles)
    summary.total_actions = sum(c.get("actions", 0) for c in cycles)

    # Extract key events and warnings
    for cycle in cycles:
      for detail in cycle.get("details", []):
        if "ERROR" in detail or "FAIL" in detail:
          summary.warnings.append(detail)
        elif cycle.get("actions", 0) > 0:
          summary.key_events.append(detail)

    # Check capacity suspensions
    cap_state_file = BEADS_DIR / "capacity_wake_state.json"
    if cap_state_file.exists():
      try:
        cap_data = json.loads(cap_state_file.read_text())
        summary.capacity_suspensions = cap_data.get("suspend_count", 0)
      except json.JSONDecodeError, OSError:
        pass

    # Format
    summary.formatted = self._format(summary)
    return summary

  def _format(self, summary: IdleSummary) -> str:
    """Format summary as human-readable text."""
    lines = [
      "╔══════════════════════════════════════╗",
      "║     Welcome Back — Steward Report    ║",
      "╚══════════════════════════════════════╝",
      "",
      f"⏱  Away: {summary.idle_duration_minutes:.0f} minutes",
      f"🔄 Cycles: {summary.cycles_executed}",
      f"⚡ Actions: {summary.total_actions}",
    ]

    if summary.capacity_suspensions > 0:
      lines.append(f"⚠️  Rate limit suspensions: {summary.capacity_suspensions}")

    if summary.key_events:
      lines.append("\n📋 Key Events:")
      for event in summary.key_events[:10]:
        lines.append(f"   • {event}")

    if summary.warnings:
      lines.append("\n🔴 Warnings:")
      for warn in summary.warnings[:5]:
        lines.append(f"   ⚠ {warn}")

    if not summary.key_events and not summary.warnings:
      lines.append("\n✅ Nothing notable — all quiet while you were away.")

    return "\n".join(lines)

  def _load_state(self) -> dict:
    """Load idle state from .beads/."""
    if self._state_file.exists():
      try:
        return json.loads(self._state_file.read_text())
      except json.JSONDecodeError, OSError:
        return {}
    return {}
