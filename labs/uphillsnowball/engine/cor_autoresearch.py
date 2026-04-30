# Copyright 2026 ShadowTag AI. All rights reserved.
"""Cor.autoresearch — Main orchestration engine for UphillSnowball.

Display name: Cor.autoresearch
Python package: cor_autoresearch
Service name: uphillsnowball-engine
Cloud Run name: uphillsnowball-engine
Docker image: uphillsnowball/engine
API prefix: /v1/autoresearch

Architecture:
    Kosmos directs → BioAgents routes → n-autoresearch executes → iii tracks state.
    JudgeSix-Human gates human/server actions. JudgeSix-Agent gates every agent output.
    The whiteboard persists unresolved issues. RKILL terminates unsafe runs.
"""

from __future__ import annotations

import enum
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from typing import Any

logger = logging.getLogger(__name__)


class RunStatus(enum.Enum):
    """Status of an autoresearch run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RKILLED = "rkilled"
    FAILED = "failed"


class JudgeVerdict(enum.Enum):
    """Verdict from JudgeSix-Agent."""

    CLEARED = "cleared"
    KICKBACK = "kickback"
    RKILL = "rkill"


@dataclass
class ResearchRun:
    """A single Cor.autoresearch run instance."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: RunStatus = RunStatus.PENDING
    hypothesis: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    kickback_count: int = 0
    verdicts: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AutoresearchEngine:
    """Main Cor.autoresearch orchestrator.

    Replaces legacy FlyingMonkeys with a clean three-layer architecture:
      1. Kosmos — Research Director (hypothesis, planning, knowledge graph)
      2. BioAgents — Routing layer (HTTP, queue, progress streaming)
      3. n-autoresearch + iii — Execution substrate (experiments, GPU, metrics)

    Eight-agent topology:
      1. JudgeSix-Human — Fast MITM gate for human/server actions
      2. Architect / Kosmos — Hypothesis and plan generation
      3. Builder — Candidate implementation / experiment patch
      4. Critic — ATP 5-19 / 17-layer inspection
      5. Corrector — Rewrites after Judge/Critic rejection
      6. Vault — Packages cleared artifacts, hashes, provenance
      7. JudgeSix-Agent — Final autonomous gate
      8. Jetski — Browser research adapter / data collection sidecar
    """

    def __init__(self) -> None:
        self._runs: dict[str, ResearchRun] = {}
        self._kosmos_bridge: Any = None  # Lazy-loaded KosmosBridge
        self._bioagents_worker: Any = None  # Lazy-loaded BioAgentsWorker
        self._n_autoresearch_client: Any = None  # Lazy-loaded NAutoresearchClient

    async def run(self, hypothesis: str, **kwargs: Any) -> ResearchRun:
        """Start a new Cor.autoresearch run.

        Flow:
            Human/server event
              → JudgeSix-Human (Level 0-5 gate)
              → Architect / Kosmos (hypothesis + plan)
              → BioAgents (route + queue)
              → n-autoresearch / iii (experiment execution)
              → Critic (inspection)
              → Corrector (if needed)
              → Vault (package artifacts)
              → JudgeSix-Agent (CLEARED / KICKBACK / RKILL)
        """
        research_run = ResearchRun(hypothesis=hypothesis, status=RunStatus.RUNNING)
        self._runs[research_run.run_id] = research_run
        logger.info(
            "Started autoresearch run %s: %s",
            research_run.run_id,
            hypothesis[:80],
        )
        # TODO: Wire Kosmos → BioAgents → n-autoresearch loop
        return research_run

    async def cancel(self, run_id: str) -> ResearchRun:
        """Cancel an active run gracefully."""
        research_run = self._runs.get(run_id)
        if research_run is None:
            msg = f"Run {run_id} not found"
            raise KeyError(msg)
        research_run.status = RunStatus.CANCELLED
        logger.info("Cancelled autoresearch run %s", run_id)
        return research_run

    async def rkill(self, run_id: str, reason: str = "") -> ResearchRun:
        """RKILL — emergency stop. Kill batch, freeze whiteboard, forensic packet.

        Triggers:
          - JudgeSix-Agent Level 5 verdict
          - Non-convergent run detection by runtime_watchdog
          - Manual operator RKILL
        """
        research_run = self._runs.get(run_id)
        if research_run is None:
            msg = f"Run {run_id} not found"
            raise KeyError(msg)
        research_run.status = RunStatus.RKILLED
        research_run.metadata["rkill_reason"] = reason
        research_run.metadata["rkill_at"] = datetime.now(UTC).isoformat()
        logger.warning("RKILL on run %s: %s", run_id, reason)
        # TODO: Freeze whiteboard, generate forensic packet
        return research_run

    def get_run(self, run_id: str) -> ResearchRun | None:
        """Retrieve a run by ID."""
        return self._runs.get(run_id)

    def list_runs(self) -> list[ResearchRun]:
        """List all runs."""
        return list(self._runs.values())
