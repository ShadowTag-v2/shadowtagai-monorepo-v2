#!/usr/bin/env python3
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
BEADS_DIR = REPO_ROOT / ".beads"


# --- CapacityWake Module (P0 #3, from Claude Code CapacityWake) ---------------
# Instead of blind exponential backoff on 429 Too Many Requests, the steward
# gracefully suspends and waits for a precise wake signal. This saves tokens
# and prevents crash loops during Vertex AI rate limiting.


class CapacityState(Enum):
    """States for the CapacityWake finite state machine."""

    ONLINE = "online"  # Normal operation
    SUSPENDED = "suspended"  # Rate limited — waiting for wake
    RECOVERING = "recovering"  # Testing capacity before full resume


class CapacityWake:
    """Graceful rate-limit suspension instead of blind backoff.

    When a 429 is detected (via subprocess stderr or HTTP header),
    the steward enters SUSPENDED state and sleeps for the Retry-After
    duration (or a default of 60s). On wake, it enters RECOVERING
    state and runs a single lightweight probe before resuming full
    operation.

    Usage::

        cw = CapacityWake()
        if cw.should_suspend():
            cw.suspend()  # Blocks for Retry-After duration
        # ... normal work
        if error_is_rate_limit(e):
            cw.signal_rate_limit(retry_after=60)
    """

    DEFAULT_SUSPEND_SECONDS = 60
    MAX_SUSPEND_SECONDS = 600  # 10 min ceiling

    def __init__(self) -> None:
        self.state = CapacityState.ONLINE
        self._retry_after: float = 0
        self._suspended_at: str = ""
        self._suspend_count: int = 0
        self._state_file = BEADS_DIR / "capacity_wake_state.json"

    def signal_rate_limit(self, retry_after: float | None = None) -> None:
        """Signal that a rate limit was hit.

        Args:
            retry_after: Seconds to wait (from Retry-After header).
                         Defaults to DEFAULT_SUSPEND_SECONDS.
        """
        self._retry_after = min(
            retry_after or self.DEFAULT_SUSPEND_SECONDS,
            self.MAX_SUSPEND_SECONDS,
        )
        self.state = CapacityState.SUSPENDED
        self._suspended_at = datetime.now(UTC).isoformat()
        self._suspend_count += 1
        self._persist_state()

    def should_suspend(self) -> bool:
        """Check if the steward should suspend."""
        return self.state == CapacityState.SUSPENDED

    def suspend(self) -> None:
        """Block for the rate-limit duration, then enter RECOVERING."""
        if self.state != CapacityState.SUSPENDED:
            return

        wait = max(1, self._retry_after)
        time.sleep(wait)
        self.state = CapacityState.RECOVERING
        self._persist_state()

    def recover(self) -> bool:
        """Attempt recovery with a lightweight probe.

        Returns True if capacity is available (steward can resume).
        In this implementation, we simply transition to ONLINE since
        the probe would be an API-specific call.
        """
        # TODO: Add a lightweight Gemini API health check when available
        self.state = CapacityState.ONLINE
        self._persist_state()
        return True

    def extract_retry_after(self, stderr_output: str) -> float | None:
        """Extract Retry-After from subprocess stderr output.

        Looks for patterns like:
          - 'Retry-After: 60'
          - '429 Too Many Requests'
          - 'RESOURCE_EXHAUSTED'
        """
        import re

        # Direct header
        match = re.search(r"Retry-After:\s*(\d+)", stderr_output)
        if match:
            return float(match.group(1))

        # Generic 429 detection
        if "429" in stderr_output or "RESOURCE_EXHAUSTED" in stderr_output:
            return self.DEFAULT_SUSPEND_SECONDS

        return None

    def _persist_state(self) -> None:
        """Write capacity state to .beads/ for monitoring."""
        import json

        BEADS_DIR.mkdir(parents=True, exist_ok=True)
        state_data = {
            "state": self.state.value,
            "retry_after": self._retry_after,
            "suspended_at": self._suspended_at,
            "suspend_count": self._suspend_count,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self._state_file.write_text(json.dumps(state_data, indent=2))


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
    import os
    import sys

    # Permission check with graceful fallback if core modules are missing
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from src.core.permissions import PermissionLearner

        learner = PermissionLearner()
        if learner.is_allowed(action.description) is False:
            return ActionVerdict.WAIT
    except ImportError:
        pass

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
    """Main steward loop with CapacityWake integration."""
    consecutive_idles = 0
    cycle_number = 0
    capacity = CapacityWake()

    # Single cycle mode for testing
    if "--once" in sys.argv:
        report = run_cycle(1, 0)
        for _detail in report.details:
            pass
        return

    # Continuous mode
    try:
        while True:
            # CapacityWake gate (P0 #3): Check if we need to suspend
            if capacity.should_suspend():
                capacity.suspend()
                if not capacity.recover():
                    # Still rate-limited — skip this cycle
                    continue

            cycle_number += 1

            try:
                report = run_cycle(cycle_number, consecutive_idles)
            except Exception as e:
                # Check if the error is a rate limit
                error_str = str(e)
                retry_after = capacity.extract_retry_after(error_str)
                if retry_after is not None:
                    capacity.signal_rate_limit(retry_after)
                    continue
                raise

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
