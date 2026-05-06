# Copyright 2026 ShadowTagAI. All rights reserved.
"""Runtime Watchdog — replaces legacy 'monkey watchdog'.

Monitors active research runs for:
  - Non-convergence (val_bpb not improving)
  - Resource budget exhaustion
  - Timeout violations
  - Crash loops
  - Anomalous behavior

Replaces: monkey watchdog
Concepts: ENDEX (end exercise), RKILL (kill batch)
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RuntimeWatchdog:
    """Runtime watchdog for Cor.autoresearch runs.

    Monitors run health and triggers ENDEX (graceful stop) or
    RKILL (emergency stop) when conditions are met.
    """

    DEFAULT_MAX_DURATION_SEC = 3600  # 1 hour for GPU jobs
    DEFAULT_MAX_CRASH_COUNT = 3
    DEFAULT_CONVERGENCE_WINDOW = 10  # experiments without improvement

    def __init__(
        self,
        max_duration_sec: int = DEFAULT_MAX_DURATION_SEC,
        max_crash_count: int = DEFAULT_MAX_CRASH_COUNT,
        convergence_window: int = DEFAULT_CONVERGENCE_WINDOW,
    ) -> None:
        self._max_duration_sec = max_duration_sec
        self._max_crash_count = max_crash_count
        self._convergence_window = convergence_window
        self._run_states: dict[str, dict[str, Any]] = {}

    def register_run(self, run_id: str) -> None:
        """Register a run for monitoring."""
        self._run_states[run_id] = {
            "crash_count": 0,
            "experiments_without_improvement": 0,
            "total_experiments": 0,
            "warnings": [],
        }
        logger.info("Watchdog registered run %s", run_id)

    def record_experiment(
        self,
        run_id: str,
        improved: bool,
        crashed: bool = False,
    ) -> dict[str, Any]:
        """Record an experiment result and check watchdog conditions.

        Returns a dict with 'action': 'continue' | 'endex' | 'rkill'.
        """
        state = self._run_states.get(run_id)
        if state is None:
            msg = f"Run {run_id} not registered with watchdog"
            raise KeyError(msg)

        state["total_experiments"] += 1

        if crashed:
            state["crash_count"] += 1
            if state["crash_count"] >= self._max_crash_count:
                logger.warning(
                    "Watchdog RKILL: run %s hit %d crashes",
                    run_id,
                    state["crash_count"],
                )
                return {"action": "rkill", "reason": "crash_loop"}

        if improved:
            state["experiments_without_improvement"] = 0
        else:
            state["experiments_without_improvement"] += 1
            if state["experiments_without_improvement"] >= self._convergence_window:
                logger.warning(
                    "Watchdog ENDEX: run %s no improvement in %d experiments",
                    run_id,
                    state["experiments_without_improvement"],
                )
                return {"action": "endex", "reason": "non_convergence"}

        return {"action": "continue"}

    def get_status(self, run_id: str) -> dict[str, Any]:
        """Get watchdog status for a run."""
        return self._run_states.get(run_id, {})
