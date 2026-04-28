# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""JudgeSix-Agent — Final autonomous gate before anything reaches the user.

Operates as the last checkpoint in the Cor.autoresearch loop.
Every agent output passes through JudgeSix-Agent before delivery.

Verdicts:
  CLEARED  — Deliver to browser tab
  KICKBACK — Return to Architect with guidance
  RKILL    — Kill batch, freeze whiteboard, forensic packet

The whiteboard remains active from the first KICKBACK until
CLEARED or RKILLED, preserving:
  - Kickback count
  - Capabilities state
  - Output summaries
  - Judge verdicts

API endpoint: POST /v1/judge/agent/evaluate
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class AgentVerdict(enum.Enum):
    """JudgeSix-Agent verdict types."""

    CLEARED = "cleared"
    KICKBACK = "kickback"
    RKILL = "rkill"


@dataclass
class AgentGateResult:
    """Result of a JudgeSix-Agent evaluation."""

    verdict: AgentVerdict = AgentVerdict.CLEARED
    guidance: str = ""
    kickback_count: int = 0
    whiteboard_active: bool = False
    forensic_packet: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class JudgeSixAgent:
    """JudgeSix-Agent final autonomous output gate.

    Evaluates all agent outputs before they reach the user.
    Runs in the engine sidecar (uphillsnowball-engine).

    Max kickbacks before auto-RKILL can be configured.
    """

    MAX_KICKBACKS = 5

    def __init__(self, max_kickbacks: int = MAX_KICKBACKS) -> None:
        self._max_kickbacks = max_kickbacks
        self._evaluation_count: int = 0
        self._whiteboard: dict[str, Any] = {}

    async def evaluate(
        self,
        run_id: str,
        output: dict[str, Any],
        kickback_count: int = 0,
    ) -> AgentGateResult:
        """Evaluate an agent output for clearance.

        Args:
            run_id: The research run ID.
            output: The agent's output to evaluate.
            kickback_count: How many times this run has been kicked back.

        Returns:
            AgentGateResult with verdict and guidance.
        """
        self._evaluation_count += 1

        # Auto-RKILL on excessive kickbacks
        if kickback_count >= self._max_kickbacks:
            logger.warning(
                "JudgeSix-Agent auto-RKILL: run %s hit %d kickbacks",
                run_id,
                kickback_count,
            )
            return AgentGateResult(
                verdict=AgentVerdict.RKILL,
                guidance=f"Non-convergent: {kickback_count} kickbacks exceeded max {self._max_kickbacks}",
                kickback_count=kickback_count,
                whiteboard_active=True,
                forensic_packet=self._generate_forensic_packet(run_id, output),
            )

        # TODO: Replace stub with actual quality/safety evaluation
        result = AgentGateResult(
            verdict=AgentVerdict.CLEARED,
            kickback_count=kickback_count,
            metadata={
                "evaluation_id": self._evaluation_count,
                "run_id": run_id,
            },
        )

        logger.info(
            "JudgeSix-Agent eval #%d: run=%s verdict=%s",
            self._evaluation_count,
            run_id,
            result.verdict.value,
        )
        return result

    def _generate_forensic_packet(
        self,
        run_id: str,
        output: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate forensic packet for RKILL events."""
        return {
            "run_id": run_id,
            "output_summary": str(output)[:500],
            "whiteboard_state": dict(self._whiteboard),
            "evaluation_count": self._evaluation_count,
        }

    def get_whiteboard(self, run_id: str) -> dict[str, Any]:
        """Get whiteboard state for a run."""
        return self._whiteboard.get(run_id, {})

    def update_whiteboard(
        self,
        run_id: str,
        data: dict[str, Any],
    ) -> None:
        """Update whiteboard state for a run."""
        if run_id not in self._whiteboard:
            self._whiteboard[run_id] = {}
        self._whiteboard[run_id].update(data)
