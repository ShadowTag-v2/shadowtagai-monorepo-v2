# Copyright 2026 ShadowTag AI. All rights reserved.
"""n-autoresearch Execution Client.

n-autoresearch owns the bottom execution layer:
  - Experiment setup and registration
  - GPU worker acquisition and dispatch
  - train.py edits and 5-minute training runs
  - val_bpb metric tracking (keep/discard decisions)
  - Crash tracking and adaptive search modes
  - Search strategy suggestions

In UphillSnowball: n-autoresearch + iii = execution substrate.
It does the measurable experimental work.

Reference: https://github.com/karpathy/autoresearch
Core loop: modify code → train 5 min → check val_bpb → keep/discard → repeat.

API endpoints:
  POST /v1/experiments/setup     — set up experiment
  POST /v1/experiments/register  — register experiment
  POST /v1/experiments/complete  — mark complete
  POST /v1/search/suggest        — get search suggestions
  POST /v1/reports/summary       — generate summary report
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from typing import Any

logger = logging.getLogger(__name__)


class ExperimentStatus(enum.Enum):
    """Status of an n-autoresearch experiment."""

    SETUP = "setup"
    REGISTERED = "registered"
    TRAINING = "training"
    EVALUATING = "evaluating"
    KEPT = "kept"
    DISCARDED = "discarded"
    CRASHED = "crashed"


class SearchMode(enum.Enum):
    """Adaptive search modes for experiment strategy."""

    EXPLORE = "explore"
    EXPLOIT = "exploit"
    HYBRID = "hybrid"


@dataclass
class Experiment:
    """A single n-autoresearch experiment."""

    experiment_id: str = ""
    run_id: str = ""
    status: ExperimentStatus = ExperimentStatus.SETUP
    code_patch: str = ""
    val_bpb: float | None = None
    baseline_bpb: float | None = None
    improvement: float | None = None
    training_duration_sec: float = 300.0  # Default 5 minutes
    gpu_worker_id: str = ""
    crash_log: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


class NAutoresearchClient:
    """Client for n-autoresearch experiment execution.

    Implements the Karpathy autoresearch core loop:
      1. Modify code (generate patch)
      2. Train for fixed 5-minute budget
      3. Check val_bpb metric
      4. Keep improvements, discard regressions
      5. Repeat

    For production GPU work, dispatch to Cloud Run Jobs (up to 168h timeout)
    or external GPU worker pools. Cloud Run service sidecars handle
    orchestration; bounded GPU experiments run as jobs.
    """

    def __init__(self, orchestrator_url: str = "http://127.0.0.1:3111") -> None:
        self._orchestrator_url = orchestrator_url
        self._experiments: dict[str, Experiment] = {}
        self._search_mode: SearchMode = SearchMode.HYBRID
        self._best_bpb: float | None = None

    async def setup_experiment(
        self,
        run_id: str,
        code_patch: str,
        baseline_bpb: float | None = None,
    ) -> Experiment:
        """Set up a new experiment."""
        import uuid

        experiment = Experiment(
            experiment_id=str(uuid.uuid4()),
            run_id=run_id,
            code_patch=code_patch,
            baseline_bpb=baseline_bpb,
        )
        self._experiments[experiment.experiment_id] = experiment
        logger.info(
            "n-autoresearch setup experiment %s for run %s",
            experiment.experiment_id,
            run_id,
        )
        # TODO: POST /v1/experiments/setup to orchestrator
        return experiment

    async def register_experiment(self, experiment_id: str) -> Experiment:
        """Register experiment with the orchestrator for GPU dispatch."""
        experiment = self._experiments.get(experiment_id)
        if experiment is None:
            msg = f"Experiment {experiment_id} not found"
            raise KeyError(msg)
        experiment.status = ExperimentStatus.REGISTERED
        logger.info("n-autoresearch registered %s", experiment_id)
        # TODO: POST /v1/experiments/register to orchestrator
        return experiment

    async def complete_experiment(
        self,
        experiment_id: str,
        val_bpb: float,
    ) -> Experiment:
        """Complete an experiment with val_bpb result. Keep or discard."""
        experiment = self._experiments.get(experiment_id)
        if experiment is None:
            msg = f"Experiment {experiment_id} not found"
            raise KeyError(msg)

        experiment.val_bpb = val_bpb

        # Keep/discard decision
        if experiment.baseline_bpb is not None and val_bpb < experiment.baseline_bpb:
            experiment.status = ExperimentStatus.KEPT
            experiment.improvement = experiment.baseline_bpb - val_bpb
            if self._best_bpb is None or val_bpb < self._best_bpb:
                self._best_bpb = val_bpb
            logger.info(
                "n-autoresearch KEPT %s: val_bpb=%.4f (improvement=%.4f)",
                experiment_id,
                val_bpb,
                experiment.improvement,
            )
        else:
            experiment.status = ExperimentStatus.DISCARDED
            logger.info(
                "n-autoresearch DISCARDED %s: val_bpb=%.4f (no improvement)",
                experiment_id,
                val_bpb,
            )

        return experiment

    async def suggest_search(self, run_id: str) -> dict[str, Any]:
        """Get search strategy suggestions based on experiment history."""
        run_experiments = [
            e for e in self._experiments.values() if e.run_id == run_id
        ]
        kept = sum(1 for e in run_experiments if e.status == ExperimentStatus.KEPT)
        total = len(run_experiments)

        return {
            "search_mode": self._search_mode.value,
            "experiments_total": total,
            "experiments_kept": kept,
            "keep_rate": kept / total if total > 0 else 0.0,
            "best_bpb": self._best_bpb,
        }

    async def generate_summary(self, run_id: str) -> dict[str, Any]:
        """Generate a summary report for a run's experiments."""
        run_experiments = [
            e for e in self._experiments.values() if e.run_id == run_id
        ]
        return {
            "run_id": run_id,
            "total_experiments": len(run_experiments),
            "kept": sum(
                1 for e in run_experiments if e.status == ExperimentStatus.KEPT
            ),
            "discarded": sum(
                1 for e in run_experiments if e.status == ExperimentStatus.DISCARDED
            ),
            "crashed": sum(
                1 for e in run_experiments if e.status == ExperimentStatus.CRASHED
            ),
            "best_bpb": self._best_bpb,
            "search_mode": self._search_mode.value,
        }
