# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Plan Mode V2 — Interview-Based Planning Protocol (P4.3).

Ports Claude Code's `tengu_plan_mode_interview_phase` flag into AGNT.
Implements the 5-phase interview protocol for STATE B tasks:

  Phase 1: UNDERSTAND — Clarify requirements, scope boundaries
  Phase 2: RESEARCH  — Gather context from codebase + KIs
  Phase 3: PLAN      — Propose approach with checkpoints
  Phase 4: REVIEW    — Human validates plan artifact
  Phase 5: EXECUTE   — Implement with numbered checkpoints

Reference: AGNT STATE B Spec P4.3

Usage:
    from packages.plan_mode import PlanSession, PlanPhase

    session = PlanSession(task_id="fix-auth-flow")
    session.advance(PlanPhase.UNDERSTAND, notes="User wants OAuth2 PKCE")
    session.advance(PlanPhase.RESEARCH, notes="Found existing auth module")
    plan_md = session.generate_plan_artifact()
    session.advance(PlanPhase.REVIEW)
    # ... after user approval ...
    session.advance(PlanPhase.EXECUTE)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
from enum import IntEnum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PlanPhase(IntEnum):
    """Plan Mode V2 phases (ordered)."""

    UNDERSTAND = 1
    RESEARCH = 2
    PLAN = 3
    REVIEW = 4
    EXECUTE = 5


PHASE_DESCRIPTIONS = {
    PlanPhase.UNDERSTAND: "Clarify requirements, scope, constraints",
    PlanPhase.RESEARCH: "Gather context from codebase, KIs, docs",
    PlanPhase.PLAN: "Propose approach with checkpoints and estimates",
    PlanPhase.REVIEW: "Human validates the plan artifact",
    PlanPhase.EXECUTE: "Implement with numbered CP-IDs",
}


@dataclass
class PlanCheckpoint:
    """A numbered checkpoint within the execution phase."""

    cp_id: str
    description: str
    status: str = "pending"  # pending | in_progress | done | blocked
    timestamp: str = ""
    notes: str = ""

    def mark_done(self, notes: str = "") -> None:
        self.status = "done"
        self.timestamp = datetime.now(UTC).isoformat()
        if notes:
            self.notes = notes


@dataclass
class PhaseEntry:
    """Record of a single phase transition."""

    phase: PlanPhase
    entered_at: str
    notes: str = ""
    artifacts: list[str] = field(default_factory=list)


@dataclass
class PlanSession:
    """A STATE B planning session with 5-phase lifecycle.

    Tracks the progression through interview phases, generates
    plan artifacts, and manages execution checkpoints.

    Args:
        task_id: Unique identifier for this planning task.
        output_dir: Directory to write plan artifacts.
    """

    task_id: str
    output_dir: Path = field(default_factory=lambda: Path("."))
    current_phase: PlanPhase = PlanPhase.UNDERSTAND
    phases: list[PhaseEntry] = field(default_factory=list)
    checkpoints: list[PlanCheckpoint] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    _started: bool = False

    def __post_init__(self) -> None:
        if not self._started:
            self._enter_phase(PlanPhase.UNDERSTAND)
            self._started = True

    def advance(self, to_phase: PlanPhase, notes: str = "") -> None:
        """Advance to the next phase.

        Enforces sequential ordering — cannot skip phases.

        Args:
            to_phase: Target phase.
            notes: Context notes for the transition.

        Raises:
            ValueError: If attempting to skip phases or go backward.
        """
        if to_phase <= self.current_phase:
            raise ValueError(f"Cannot move from {self.current_phase.name} to {to_phase.name} — phases are sequential")
        if to_phase.value != self.current_phase.value + 1:
            raise ValueError(f"Cannot skip from {self.current_phase.name} to {to_phase.name} — advance one phase at a time")
        self._enter_phase(to_phase, notes)

    def _enter_phase(self, phase: PlanPhase, notes: str = "") -> None:
        entry = PhaseEntry(
            phase=phase,
            entered_at=datetime.now(UTC).isoformat(),
            notes=notes,
        )
        self.phases.append(entry)
        self.current_phase = phase
        logger.info(
            "[PLAN %s] Phase %d/%d: %s — %s",
            self.task_id,
            phase.value,
            len(PlanPhase),
            phase.name,
            PHASE_DESCRIPTIONS[phase],
        )

    def add_checkpoint(self, description: str) -> PlanCheckpoint:
        """Add an execution checkpoint.

        Only valid in PLAN or EXECUTE phases.

        Args:
            description: What this checkpoint verifies.

        Returns:
            The created PlanCheckpoint.
        """
        cp_id = f"CP-{len(self.checkpoints) + 1:03d}"
        cp = PlanCheckpoint(cp_id=cp_id, description=description)
        self.checkpoints.append(cp)
        return cp

    def complete_checkpoint(self, cp_id: str, notes: str = "") -> None:
        """Mark a checkpoint as done."""
        for cp in self.checkpoints:
            if cp.cp_id == cp_id:
                cp.mark_done(notes)
                logger.info("[PLAN %s] %s DONE: %s", self.task_id, cp_id, notes)
                return
        raise KeyError(f"Checkpoint {cp_id} not found")

    def set_context(self, key: str, value: Any) -> None:
        """Store context gathered during RESEARCH phase."""
        self.context[key] = value

    def generate_plan_artifact(self) -> str:
        """Generate a markdown plan artifact for REVIEW phase.

        Returns:
            Markdown string of the plan.
        """
        lines = [
            f"# Plan: {self.task_id}",
            "",
            f"> Generated: {datetime.now(UTC).isoformat()}",
            f"> Current Phase: {self.current_phase.name}",
            "",
            "## Phase History",
            "",
        ]

        for entry in self.phases:
            lines.append(f"- **{entry.phase.name}** ({entry.entered_at})" + (f" — {entry.notes}" if entry.notes else ""))

        if self.context:
            lines.extend(["", "## Research Context", ""])
            for k, v in self.context.items():
                lines.append(f"- **{k}**: {v}")

        if self.checkpoints:
            lines.extend(["", "## Execution Checkpoints", ""])
            for cp in self.checkpoints:
                status_icon = {
                    "pending": "⬜",
                    "in_progress": "🟡",
                    "done": "✅",
                    "blocked": "🔴",
                }.get(cp.status, "⬜")
                lines.append(f"- {status_icon} **{cp.cp_id}**: {cp.description}")

        lines.extend(["", "---", "*END OF PLAN*"])
        return "\n".join(lines)

    def save_plan(self) -> Path:
        """Save the plan artifact to disk.

        Returns:
            Path to the saved plan file.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        plan_path = self.output_dir / f"{self.task_id}-plan.md"
        plan_path.write_text(self.generate_plan_artifact())
        logger.info("[PLAN %s] Saved to %s", self.task_id, plan_path)
        return plan_path

    def save_state(self) -> Path:
        """Serialize session state to JSON for resumption."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        state_path = self.output_dir / f"{self.task_id}-state.json"
        state = {
            "task_id": self.task_id,
            "current_phase": self.current_phase.name,
            "phases": [
                {
                    "phase": e.phase.name,
                    "entered_at": e.entered_at,
                    "notes": e.notes,
                }
                for e in self.phases
            ],
            "checkpoints": [
                {
                    "cp_id": cp.cp_id,
                    "description": cp.description,
                    "status": cp.status,
                    "timestamp": cp.timestamp,
                    "notes": cp.notes,
                }
                for cp in self.checkpoints
            ],
            "context": self.context,
        }
        state_path.write_text(json.dumps(state, indent=2))
        return state_path

    @classmethod
    def load_state(cls, path: Path) -> PlanSession:
        """Load a session from a saved state file."""
        data = json.loads(path.read_text())
        session = cls(
            task_id=data["task_id"],
            output_dir=path.parent,
        )
        session._started = True
        session.current_phase = PlanPhase[data["current_phase"]]
        session.phases = [
            PhaseEntry(
                phase=PlanPhase[e["phase"]],
                entered_at=e["entered_at"],
                notes=e.get("notes", ""),
            )
            for e in data["phases"]
        ]
        session.checkpoints = [PlanCheckpoint(**cp) for cp in data["checkpoints"]]
        session.context = data.get("context", {})
        return session

    @property
    def progress(self) -> str:
        """Human-readable progress summary."""
        done = sum(1 for cp in self.checkpoints if cp.status == "done")
        total = len(self.checkpoints)
        return f"[{self.task_id}] Phase {self.current_phase.value}/5 ({self.current_phase.name}) | Checkpoints: {done}/{total}"
