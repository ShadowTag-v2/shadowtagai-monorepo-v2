# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""ADP 5-0 Military Decision Making Process (MDMP) Workflow.

The J-5 Architect orchestrates through MDMP (receipt of mission → WARNO →
mission analysis → COA development → COA analysis → COA comparison →
COA approval → OPORD production).

References:
    - ADP 5-0: The Operations Process
    - ATP 5-0.2-1: Staff Reference Guide (Vol I)
    - JP 3-33: Joint Task Force Headquarters
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("J5-MDMP-Workflow")


@dataclass
class COA:
    """Course of Action candidate from MDMP Step 3."""

    name: str
    description: str
    risk_level: str  # LOW, MODERATE, HIGH, EXTREME
    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)


@dataclass
class OPORD:
    """Operations Order — MDMP final output (Step 7)."""

    situation: dict[str, Any]
    mission: str
    execution: dict[str, Any]
    sustainment: dict[str, Any]
    command_signal: dict[str, Any]


class MDMPWorkflow:
    """The 7-Step MDMP as the planning backbone.

    Receipt → Mission Analysis → COA Dev → COA Analysis →
    COA Comparison → COA Approval → OPORD Production
    """

    async def execute_mdmp(self, call_of_question: dict[str, Any]) -> OPORD:
        """Execute the full MDMP to produce an OPORD.

        Args:
            call_of_question: The operational question to plan against.

        Returns:
            An OPORD (Operations Order) for execution by J-3.
        """
        logger.info("📋 J-5 MDMP initiated for: %s", call_of_question.get("mission", "N/A"))

        # Step 1: Receipt of Mission
        mission = call_of_question.get("mission", "Undefined")

        # Step 2: Mission Analysis
        analysis = self._analyze(call_of_question)

        # Step 3: COA Development
        coas = self._develop_coas(analysis)

        # Step 4-5: COA Analysis & Comparison (wargaming)
        selected = self._wargame_and_compare(coas)

        # Step 6: COA Approval (Hammock Protocol)
        logger.info("🪑 Hammock Protocol: Think before executing...")

        # Step 7: OPORD Production
        opord = OPORD(
            situation=analysis,
            mission=mission,
            execution={"selected_coa": selected.name, "risk": selected.risk_level},
            sustainment={"resources": "allocated"},
            command_signal={"comms": "MCP fleet"},
        )

        logger.info("✅ OPORD produced. Forwarding to J-3 Builder.")
        return opord

    def _analyze(self, coq: dict[str, Any]) -> dict[str, Any]:
        """Step 2: Mission Analysis — break down the problem."""
        return {
            "specified_tasks": coq.get("tasks", []),
            "implied_tasks": [],
            "constraints": coq.get("constraints", []),
            "assumptions": [],
        }

    def _develop_coas(self, analysis: dict[str, Any]) -> list[COA]:
        """Step 3: Develop at least 2 divergent COAs."""
        return [
            COA(
                name="COA_A_Incremental",
                description="Minimal risk, sequential execution",
                risk_level="LOW",
                advantages=["Safety"],
                disadvantages=["Slower"],
            ),
            COA(
                name="COA_B_Aggressive",
                description="Parallel execution, higher throughput",
                risk_level="MODERATE",
                advantages=["Speed"],
                disadvantages=["Complexity"],
            ),
        ]

    def _wargame_and_compare(self, coas: list[COA]) -> COA:
        """Steps 4-5: Wargame and select best COA."""
        # Default: prefer incremental (Simple > Easy)
        return min(coas, key=lambda c: {"LOW": 0, "MODERATE": 1, "HIGH": 2, "EXTREME": 3}[c.risk_level])
