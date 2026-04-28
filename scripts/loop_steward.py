#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Autonomous Loop Steward Daemon.
===============================
Timer-based daemon that advances in-progress work while the user is away.
Adapted from Claude Code's autonomous loop steward pattern.

Principles:
  1. Steward, not initiator — continues established work only
  2. Reversibility heuristic — reversible actions proceed, irreversible wait
  3. 3-consecutive-idle scaling — after 3 "nothing to do" cycles, scale back
  4. PR maintenance as idle work — CI status, review threads, rebase

Usage:
  python loop_steward.py --cycle-interval 300 --max-idle 3
  python loop_steward.py --dry-run
"""

import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

# --- Configuration -----------------------------------------------------------

CYCLE_INTERVAL = int(os.environ.get("STEWARD_CYCLE_INTERVAL", "300"))  # 5 min
MAX_IDLE_CYCLES = int(os.environ.get("STEWARD_MAX_IDLE", "3"))
REPO_ROOT = Path(
    os.environ.get(
        "REPO_ROOT",
        os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball"),
    ),
)
DRY_RUN = "--dry-run" in sys.argv


# --- Enums -------------------------------------------------------------------


class ActionVerdict(Enum):
    PROCEED = "proceed"
    WAIT = "wait"
    SCALE_BACK = "scale_back"
    ESCALATE = "escalate"


class ActionType(Enum):
    PR_STATUS = "pr_status"
    CI_CHECK = "ci_check"
    REBASE = "rebase"
    TEST_RUN = "test_run"
    LINT_FIX = "lint_fix"
    DREAM = "dream"
    FTS_REINDEX = "fts_reindex"
    IDLE = "idle"


# --- Data Models -------------------------------------------------------------


@dataclass
class Action:
    """Represents a single steward action."""

    action_type: ActionType
    description: str
    reversible: bool = True
    risk_level: str = "low"  # low, medium, high


@dataclass
class CycleReport:
    """Tracks a single steward cycle."""

    timestamp: str = ""
    cycle_number: int = 0
    actions_evaluated: int = 0
    actions_taken: int = 0
    verdict: ActionVerdict = ActionVerdict.PROCEED
    details: list = field(default_factory=list)


# --- Reversibility Heuristic -------------------------------------------------

REVERSIBLE_ACTIONS = {
    ActionType.PR_STATUS: True,
    ActionType.CI_CHECK: True,
    ActionType.TEST_RUN: True,
    ActionType.LINT_FIX: True,
    ActionType.DREAM: True,
    ActionType.FTS_REINDEX: True,
    ActionType.REBASE: False,  # Irreversible — needs user approval
}


def is_reversible(action: Action) -> bool:
    """Check if an action can be undone without user intervention."""
    return REVERSIBLE_ACTIONS.get(action.action_type, action.reversible)


# --- Action Evaluator --------------------------------------------------------


def evaluate_action(action: Action, consecutive_idles: int) -> ActionVerdict:
    """Determine whether to proceed with an action."""
    # 3-consecutive-idle scaling
    if consecutive_idles >= MAX_IDLE_CYCLES:
        return ActionVerdict.SCALE_BACK

    # Reversibility gate
    if not is_reversible(action):
        return ActionVerdict.WAIT

    # Risk gate
    if action.risk_level == "high":
        return ActionVerdict.ESCALATE

    return ActionVerdict.PROCEED


# --- Steward Actions ---------------------------------------------------------


def check_git_status() -> list[Action]:
    """Check for uncommitted changes or pending work."""
    actions = []

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.stdout.strip():
            dirty_count = len(result.stdout.strip().splitlines())
            actions.append(
                Action(
                    action_type=ActionType.LINT_FIX,
                    description=f"{dirty_count} uncommitted files detected",
                    reversible=True,
                    risk_level="low",
                ),
            )
    except subprocess.TimeoutExpired, FileNotFoundError:
        pass

    return actions


def check_test_status() -> list[Action]:
    """Check if tests need running."""
    actions = []

    # Check if test results are stale (>1 hour since last run)
    test_marker = REPO_ROOT / ".beads" / "last_test_run"
    if test_marker.exists():
        last_run = datetime.fromtimestamp(test_marker.stat().st_mtime, tz=UTC)
        age_hours = (datetime.now(UTC) - last_run).total_seconds() / 3600
        if age_hours > 1:
            actions.append(
                Action(
                    action_type=ActionType.TEST_RUN,
                    description=f"Tests stale ({age_hours:.1f}h since last run)",
                    reversible=True,
                    risk_level="low",
                ),
            )
    else:
        actions.append(
            Action(
                action_type=ActionType.TEST_RUN,
                description="No test run marker found",
                reversible=True,
                risk_level="low",
            ),
        )

    return actions


def check_dream_schedule() -> list[Action]:
    """Check if Dream consolidation is due."""
    actions = []

    dream_marker = REPO_ROOT / ".beads" / "last_dream_run"
    if dream_marker.exists():
        last_run = datetime.fromtimestamp(dream_marker.stat().st_mtime, tz=UTC)
        age_hours = (datetime.now(UTC) - last_run).total_seconds() / 3600
        if age_hours > 24:
            actions.append(
                Action(
                    action_type=ActionType.DREAM,
                    description=f"Dream consolidation due ({age_hours:.0f}h since last)",
                    reversible=True,
                    risk_level="low",
                ),
            )
    else:
        actions.append(
            Action(
                action_type=ActionType.DREAM,
                description="No Dream cycle recorded — initial run",
                reversible=True,
                risk_level="low",
            ),
        )

    return actions


def check_fts_freshness() -> list[Action]:
    """Check if FTS5 index needs rebuilding."""
    actions = []
    ki_dir = Path(os.environ.get("KI_DIR", os.path.expanduser("~/.gemini/antigravity/knowledge")))
    fts_db = ki_dir / ".ki-index.db"
    if not fts_db.exists():
        actions.append(
            Action(
                action_type=ActionType.FTS_REINDEX,
                description="FTS5 index missing — initial build",
                reversible=True,
                risk_level="low",
            ),
        )
    else:
        age_hours = (datetime.now(UTC) - datetime.fromtimestamp(fts_db.stat().st_mtime, tz=UTC)).total_seconds() / 3600
        if age_hours > 12:
            actions.append(
                Action(
                    action_type=ActionType.FTS_REINDEX,
                    description=f"FTS5 index stale ({age_hours:.1f}h since last build)",
                    reversible=True,
                    risk_level="low",
                ),
            )
    return actions


# --- Execute Actions ---------------------------------------------------------


def execute_action(action: Action) -> bool:
    """Execute a steward action. Returns True if successful."""
    if DRY_RUN:
        return True

    if action.action_type == ActionType.TEST_RUN:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit/", "-x", "--tb=short", "-q"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=120,
            )
            # Update marker
            marker = REPO_ROOT / ".beads" / "last_test_run"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    elif action.action_type == ActionType.DREAM:
        try:
            dream_script = REPO_ROOT / "scripts" / "dream_consolidation.py"
            if dream_script.exists():
                result = subprocess.run(
                    [sys.executable, str(dream_script), "--dry-run"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                # Update marker
                marker = REPO_ROOT / ".beads" / "last_dream_run"
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.touch()
                return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    elif action.action_type == ActionType.FTS_REINDEX:
        try:
            ki_dir = Path(os.environ.get("KI_DIR", os.path.expanduser("~/.gemini/antigravity/knowledge")))
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    f"import sys; sys.path.insert(0, '{REPO_ROOT}'); "
                    f"from core.ki_engine.fts_index import reindex_all; "
                    f"from pathlib import Path; "
                    f"print(reindex_all(Path('{ki_dir}')))",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    elif action.action_type == ActionType.LINT_FIX:
        return True

    return True


# --- Main Loop ---------------------------------------------------------------


def run_cycle(cycle_number: int, consecutive_idles: int) -> CycleReport:
    """Run a single steward cycle."""
    report = CycleReport(
        timestamp=datetime.now(UTC).isoformat(),
        cycle_number=cycle_number,
    )

    # Gather all potential actions
    actions = []
    actions.extend(check_git_status())
    actions.extend(check_test_status())
    actions.extend(check_dream_schedule())
    actions.extend(check_fts_freshness())

    report.actions_evaluated = len(actions)

    if not actions:
        report.verdict = ActionVerdict.PROCEED
        report.details.append("No actions needed — idle cycle")
        return report

    # Evaluate and execute
    for action in actions:
        verdict = evaluate_action(action, consecutive_idles)

        if verdict == ActionVerdict.PROCEED:
            success = execute_action(action)
            if success:
                report.actions_taken += 1
                report.details.append(f"✅ {action.description}")
            else:
                report.details.append(f"❌ {action.description}")

        elif verdict == ActionVerdict.WAIT:
            report.details.append(f"⏸️ {action.description} (irreversible — waiting)")

        elif verdict == ActionVerdict.ESCALATE:
            report.details.append(f"⚠️ {action.description} (high risk — escalating)")

        elif verdict == ActionVerdict.SCALE_BACK:
            report.details.append(f"💤 {action.description} (scaling back)")
            report.verdict = ActionVerdict.SCALE_BACK

    return report


def main() -> None:
    """Main steward loop."""
    consecutive_idles = 0
    cycle_number = 0

    # Single cycle mode for testing
    if "--once" in sys.argv:
        report = run_cycle(1, 0)
        for _detail in report.details:
            pass
        return

    # Continuous mode
    try:
        while True:
            cycle_number += 1

            report = run_cycle(cycle_number, consecutive_idles)

            if report.actions_taken == 0:
                consecutive_idles += 1
            else:
                consecutive_idles = 0

            for _detail in report.details:
                pass

            if report.verdict == ActionVerdict.SCALE_BACK:
                scaled_interval = CYCLE_INTERVAL * (2 ** min(consecutive_idles, 5))
                time.sleep(scaled_interval)
            else:
                time.sleep(CYCLE_INTERVAL)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
