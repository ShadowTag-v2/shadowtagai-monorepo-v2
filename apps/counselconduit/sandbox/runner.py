# apps/counselconduit/sandbox/runner.py
"""Phase 3 Sandbox Runner — Isolated container execution for tool calls.

Scaffolds the isolated execution environment for sandboxed tool calls
in CounselConduit. Tool calls run in ephemeral containers with:
- Read-only filesystem
- No network access (configurable per-tier)
- Short-lived proxy tokens
- Resource limits (CPU, memory, wall-clock)
- Tenant-scoped output capture
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger("counselconduit.sandbox.runner")


class SandboxTier(StrEnum):
    """Isolation levels for sandbox execution."""

    BASIC = "basic"  # Solo tier — no network, 30s timeout
    STANDARD = "standard"  # Practice tier — limited network, 60s timeout
    ENTERPRISE = "enterprise"  # Enterprise — custom network policy, 300s timeout


@dataclass
class SandboxConfig:
    """Configuration for a sandbox execution environment."""

    tier: SandboxTier = SandboxTier.BASIC
    max_wall_clock_seconds: int = 30
    max_memory_mb: int = 256
    max_cpu_millicores: int = 500
    allow_network: bool = False
    network_allowlist: list[str] = field(default_factory=list)
    read_only_fs: bool = True
    max_output_bytes: int = 1_048_576  # 1MB


TIER_CONFIGS: dict[SandboxTier, SandboxConfig] = {
    SandboxTier.BASIC: SandboxConfig(
        tier=SandboxTier.BASIC,
        max_wall_clock_seconds=30,
        max_memory_mb=256,
        max_cpu_millicores=500,
        allow_network=False,
    ),
    SandboxTier.STANDARD: SandboxConfig(
        tier=SandboxTier.STANDARD,
        max_wall_clock_seconds=60,
        max_memory_mb=512,
        max_cpu_millicores=1000,
        allow_network=True,
        network_allowlist=["*.googleapis.com", "*.firebaseio.com"],
    ),
    SandboxTier.ENTERPRISE: SandboxConfig(
        tier=SandboxTier.ENTERPRISE,
        max_wall_clock_seconds=300,
        max_memory_mb=2048,
        max_cpu_millicores=2000,
        allow_network=True,
        # Enterprise has custom allowlists per-firm
    ),
}


@dataclass
class SandboxExecution:
    """Represents a single sandbox execution."""

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    firm_id: str = ""
    session_id: str = ""
    tool_name: str = ""
    config: SandboxConfig = field(default_factory=SandboxConfig)
    status: str = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output: str = ""
    error: str | None = None
    exit_code: int | None = None
    resource_usage: dict[str, Any] = field(default_factory=dict)


class SandboxRunner:
    """Orchestrates tool execution in isolated containers.

    Phase 3 scaffold — actual container orchestration will use
    Cloud Run Jobs or GKE sandboxed pods.
    """

    def __init__(self, project_id: str = "shadowtag-omega-v4") -> None:
        self._project_id = project_id
        self._executions: dict[str, SandboxExecution] = {}

    def create_execution(
        self,
        firm_id: str,
        session_id: str,
        tool_name: str,
        tier: SandboxTier = SandboxTier.BASIC,
    ) -> SandboxExecution:
        """Create a new sandbox execution request."""
        config = TIER_CONFIGS.get(tier, TIER_CONFIGS[SandboxTier.BASIC])
        execution = SandboxExecution(
            firm_id=firm_id,
            session_id=session_id,
            tool_name=tool_name,
            config=config,
        )
        self._executions[execution.execution_id] = execution
        logger.info(
            "Sandbox execution created: %s (firm=%s, tool=%s, tier=%s)",
            execution.execution_id,
            firm_id,
            tool_name,
            tier.value,
        )
        return execution

    async def execute(self, execution_id: str, payload: dict[str, Any]) -> SandboxExecution:
        """Execute a tool call in a sandboxed environment.

        Phase 3 TODO: Replace with actual Cloud Run Job submission.
        Currently validates config and returns a mock execution result.
        """
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        execution.status = "running"
        execution.started_at = datetime.now(UTC)

        # Phase 3 TODO: Submit to Cloud Run Jobs / GKE sandbox
        # For now, validate the configuration is correct
        logger.info(
            "Sandbox execution started: %s (timeout=%ds, memory=%dMB, network=%s)",
            execution_id,
            execution.config.max_wall_clock_seconds,
            execution.config.max_memory_mb,
            execution.config.allow_network,
        )

        execution.status = "completed"
        execution.completed_at = datetime.now(UTC)
        execution.exit_code = 0
        execution.output = f"[SCAFFOLD] Tool '{execution.tool_name}' validated for sandbox execution"

        return execution

    def get_execution(self, execution_id: str) -> SandboxExecution | None:
        """Retrieve execution status."""
        return self._executions.get(execution_id)

    def cleanup_expired(self, max_age_seconds: int = 3600) -> int:
        """Remove completed executions older than max_age_seconds."""
        now = datetime.now(UTC)
        expired = [eid for eid, ex in self._executions.items() if ex.completed_at and (now - ex.completed_at).total_seconds() > max_age_seconds]
        for eid in expired:
            del self._executions[eid]
        if expired:
            logger.info("Cleaned up %d expired sandbox executions", len(expired))
        return len(expired)
