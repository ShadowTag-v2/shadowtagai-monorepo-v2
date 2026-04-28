# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""BioAgents Routing Layer.

BioAgents owns:
  - HTTP layer and API routing
  - Job queue and dispatch
  - Research agent orchestration
  - Progress streaming (SSE/WebSocket)
  - File upload handling
  - JWT auth for API access

In UphillSnowball: BioAgents = Research API + queue/router + progress stream.
It receives work, routes it, and reports progress.

Six BioAgents:
  1. Architect — Kosmos Research Director (hypothesis + plan)
  2. Builder — Produces candidate implementation / experiment patch
  3. Critic — ATP 5-19 / 17-layer inspection
  4. Corrector — Rewrites after Judge/Critic rejection
  5. Vault — Packages cleared artifacts, hashes, provenance, citations
  6. Jetski — Browser research adapter / data collection sidecar
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class AgentRole(enum.Enum):
    """BioAgent roles in the research pipeline."""

    ARCHITECT = "architect"
    BUILDER = "builder"
    CRITIC = "critic"
    CORRECTOR = "corrector"
    VAULT = "vault"
    JETSKI = "jetski"


class JobStatus(enum.Enum):
    """Status of a routed job."""

    QUEUED = "queued"
    DISPATCHED = "dispatched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class ResearchJob:
    """A job routed through BioAgents."""

    job_id: str = ""
    agent: AgentRole = AgentRole.ARCHITECT
    status: JobStatus = JobStatus.QUEUED
    payload: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)


class BioAgentsWorker:
    """BioAgents routing layer for the Cor.autoresearch pipeline.

    Routes work through the six-agent pipeline:
        Architect → Builder → Critic → Corrector (if needed) → Vault → Jetski

    API endpoints mapped:
        POST /v1/autoresearch/runs         — create run
        GET  /v1/autoresearch/runs/:id      — get run
        GET  /v1/autoresearch/runs/:id/events — SSE event stream
        POST /v1/autoresearch/runs/:id/cancel — cancel
        POST /v1/autoresearch/runs/:id/rkill  — RKILL
    """

    def __init__(self) -> None:
        self._jobs: dict[str, ResearchJob] = {}

    async def dispatch(
        self,
        agent: AgentRole,
        payload: dict[str, Any],
    ) -> ResearchJob:
        """Dispatch work to a specific BioAgent."""
        import uuid

        job = ResearchJob(
            job_id=str(uuid.uuid4()),
            agent=agent,
            status=JobStatus.DISPATCHED,
            payload=payload,
        )
        self._jobs[job.job_id] = job
        logger.info("BioAgents dispatched %s to %s", job.job_id, agent.value)
        # TODO: Wire to actual agent execution
        return job

    async def get_events(
        self,
        run_id: str,
    ) -> list[dict[str, Any]]:
        """Get SSE events for a run (progress streaming)."""
        events: list[dict[str, Any]] = []
        for job in self._jobs.values():
            if job.payload.get("run_id") == run_id:
                events.extend(job.events)
        return events

    async def route_pipeline(
        self,
        hypothesis: dict[str, Any],
        run_id: str,
    ) -> dict[str, Any]:
        """Route a hypothesis through the full BioAgent pipeline.

        Flow: Architect → Builder → Critic → Corrector → Vault
        """
        pipeline_result: dict[str, Any] = {"run_id": run_id, "stages": []}

        for agent in [
            AgentRole.ARCHITECT,
            AgentRole.BUILDER,
            AgentRole.CRITIC,
            AgentRole.VAULT,
        ]:
            job = await self.dispatch(
                agent,
                {"run_id": run_id, "hypothesis": hypothesis},
            )
            pipeline_result["stages"].append({"agent": agent.value, "job_id": job.job_id})

        return pipeline_result
