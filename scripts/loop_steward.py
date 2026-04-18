#!/usr/bin/env python3
"""
Autonomous Loop Steward Daemon
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

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# --- Configuration -----------------------------------------------------------

CYCLE_INTERVAL = int(os.environ.get("STEWARD_CYCLE_INTERVAL", "300"))  # 5 min
MAX_IDLE_CYCLES = int(os.environ.get("STEWARD_MAX_IDLE", "3"))
REPO_ROOT = Path(os.environ.get(
    "REPO_ROOT",
    os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball"),
))
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
            actions.append(Action(
                action_type=ActionType.LINT_FIX,
                description=f"{dirty_count} uncommitted files detected",
                reversible=True,
                risk_level="low",
            ))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return actions


def check_test_status() -> list[Action]:
    """Check if tests need running."""
    actions = []

    # Check if test results are stale (>1 hour since last run)
    test_marker = REPO_ROOT / ".beads" / "last_test_run"
    if test_marker.exists():
        last_run = datetime.fromtimestamp(
            test_marker.stat().st_mtime, tz=timezone.utc
        )
        age_hours = (
            datetime.now(timezone.utc) - last_run
        ).total_seconds() / 3600
        if age_hours > 1:
            actions.append(Action(
                action_type=ActionType.TEST_RUN,
                description=f"Tests stale ({age_hours:.1f}h since last run)",
                reversible=True,
                risk_level="low",
            ))
    else:
        actions.append(Action(
            action_type=ActionType.TEST_RUN,
            description="No test run marker found",
            reversible=True,
            risk_level="low",
        ))

    return actions


def check_dream_schedule() -> list[Action]:
    """Check if Dream consolidation is due."""
    actions = []

    dream_marker = REPO_ROOT / ".beads" / "last_dream_run"
    if dream_marker.exists():
        last_run = datetime.fromtimestamp(
            dream_marker.stat().st_mtime, tz=timezone.utc
        )
        age_hours = (
            datetime.now(timezone.utc) - last_run
        ).total_seconds() / 3600
        if age_hours > 24:
            actions.append(Action(
                action_type=ActionType.DREAM,
                description=f"Dream consolidation due ({age_hours:.0f}h since last)",
                reversible=True,
                risk_level="low",
            ))
    else:
        actions.append(Action(
            action_type=ActionType.DREAM,
            description="No Dream cycle recorded — initial run",
            reversible=True,
            risk_level="low",
        ))

    return actions


# --- Execute Actions ---------------------------------------------------------

def execute_action(action: Action) -> bool:
    """Execute a steward action. Returns True if successful."""
    if DRY_RUN:
        print(f"  [DRY RUN] Would execute: {action.description}")
        return True

    if action.action_type == ActionType.TEST_RUN:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit/", "-x",
                 "--tb=short", "-q"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=120,
            )
            # Update marker
            marker = REPO_ROOT / ".beads" / "last_test_run"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
            print(f"  [EXEC] Tests: {'PASS' if result.returncode == 0 else 'FAIL'}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("  [EXEC] Tests timed out")
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
                print(f"  [EXEC] Dream cycle complete")
                return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("  [EXEC] Dream cycle timed out")
            return False

    elif action.action_type == ActionType.LINT_FIX:
        print(f"  [INFO] {action.description} — steward does not auto-commit")
        return True

    return True


# --- Main Loop ---------------------------------------------------------------

def run_cycle(cycle_number: int, consecutive_idles: int) -> CycleReport:
    """Run a single steward cycle."""
    report = CycleReport(
        timestamp=datetime.now(timezone.utc).isoformat(),
        cycle_number=cycle_number,
    )

    # Gather all potential actions
    actions = []
    actions.extend(check_git_status())
    actions.extend(check_test_status())
    actions.extend(check_dream_schedule())

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


def main():
    """Main steward loop."""
    print("=" * 60)
    print(f"Loop Steward — Started {datetime.now(timezone.utc).isoformat()}")
    print(f"Cycle interval: {CYCLE_INTERVAL}s | Max idle: {MAX_IDLE_CYCLES}")
    print(f"Repo: {REPO_ROOT}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print("=" * 60)

    consecutive_idles = 0
    cycle_number = 0

    # Single cycle mode for testing
    if "--once" in sys.argv:
        report = run_cycle(1, 0)
        print(f"\nCycle 1: {report.actions_evaluated} evaluated, "
              f"{report.actions_taken} taken")
        for detail in report.details:
            print(f"  {detail}")
        return

    # Continuous mode
    try:
        while True:
            cycle_number += 1
            print(f"\n--- Cycle {cycle_number} ---")

            report = run_cycle(cycle_number, consecutive_idles)

            if report.actions_taken == 0:
                consecutive_idles += 1
            else:
                consecutive_idles = 0

            print(f"Actions: {report.actions_taken}/{report.actions_evaluated} | "
                  f"Idle streak: {consecutive_idles}/{MAX_IDLE_CYCLES}")
            for detail in report.details:
                print(f"  {detail}")

            if report.verdict == ActionVerdict.SCALE_BACK:
                scaled_interval = CYCLE_INTERVAL * (2 ** min(consecutive_idles, 5))
                print(f"Scaling back — next cycle in {scaled_interval}s")
                time.sleep(scaled_interval)
            else:
                time.sleep(CYCLE_INTERVAL)

    except KeyboardInterrupt:
        print(f"\nSteward stopped after {cycle_number} cycles")


if __name__ == "__main__":
    main()
