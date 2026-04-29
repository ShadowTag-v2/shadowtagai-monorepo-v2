# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""8-Agent Synthesis Coordinator — Temporal-native Agent Board.

Agent 0: The Board. Orchestrates the 8-agent synthesis map using
Temporal activities and signals — not bash loops or XML files.

Architecture:
    THE TRIAD (Agents 1–3):
        Agent 1 (Builder):   Modifies implementation code. NEVER reviews.
        Agent 2 (Reviewer):  Audits code. NEVER writes production code.
        Agent 3 (Tester):    Writes test suites. NEVER decides architecture.

    JUDGE 6 (Agent 4):
        Pre-deployment gate: Wet Fleece → Dry Ground → Battle.
        If any phase fails, triggers Temporal-reversal.

    SUPPORT DAEMONS (Agents 5–8):
        Agent 5 (COR.KAIROS):          Nightly knowledge distillation.
        Agent 6 (Aegaeon Cache):   Token microcompaction & KV slab.
        Agent 7 (Omega Auth):      GCP Secret Manager fetch.
        Agent 8 (Rich Hickey):     Dead code enforcement (vulture + ruff).

Communication:
    Agents do NOT exchange XML files in a scratch directory.
    They communicate via Temporal activity results and workflow signals.
    This is durable, crash-proof, and fully auditable.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum

logger = logging.getLogger("Agent-Board")


class AgentRole(StrEnum):
    """The 8 agents in the synthesis map."""

    BUILDER = "builder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    JUDGE_6 = "judge_6"
    COR.KAIROS = "kairos"
    AEGAEON = "aegaeon"
    OMEGA_AUTH = "omega_auth"
    RICH_HICKEY = "rich_hickey"


class AgentCapability(StrEnum):
    """Capabilities that agents are authorized to perform."""

    WRITE_CODE = "write_code"
    REVIEW_CODE = "review_code"
    WRITE_TESTS = "write_tests"
    ENFORCE_RISK = "enforce_risk"
    DISTILL_KNOWLEDGE = "distill_knowledge"
    MANAGE_CACHE = "manage_cache"
    FETCH_SECRETS = "fetch_secrets"
    ENFORCE_SIMPLICITY = "enforce_simplicity"


@dataclass(frozen=True)
class AgentSpec:
    """Specification for a single agent in the synthesis map.

    Attributes:
        role: The agent's designated role.
        temporal_activity: The Temporal activity name this agent maps to.
        capabilities: Set of authorized capabilities.
        forbidden: Set of explicitly forbidden capabilities.
    """

    role: AgentRole
    temporal_activity: str
    capabilities: frozenset[AgentCapability]
    forbidden: frozenset[AgentCapability]


# ── The 8-Agent Synthesis Map ──────────────────────────────────────

SYNTHESIS_MAP: dict[AgentRole, AgentSpec] = {
    AgentRole.BUILDER: AgentSpec(
        role=AgentRole.BUILDER,
        temporal_activity="j3_decisive_ops_strike",
        capabilities=frozenset({AgentCapability.WRITE_CODE}),
        forbidden=frozenset({AgentCapability.REVIEW_CODE, AgentCapability.WRITE_TESTS}),
    ),
    AgentRole.REVIEWER: AgentSpec(
        role=AgentRole.REVIEWER,
        temporal_activity="j6_sustaining_ops_audit",
        capabilities=frozenset({AgentCapability.REVIEW_CODE}),
        forbidden=frozenset({AgentCapability.WRITE_CODE, AgentCapability.WRITE_TESTS}),
    ),
    AgentRole.TESTER: AgentSpec(
        role=AgentRole.TESTER,
        temporal_activity="j3_roc_drill_sandbox",
        capabilities=frozenset({AgentCapability.WRITE_TESTS}),
        forbidden=frozenset({AgentCapability.WRITE_CODE, AgentCapability.REVIEW_CODE}),
    ),
    AgentRole.JUDGE_6: AgentSpec(
        role=AgentRole.JUDGE_6,
        temporal_activity="j6_judge_deploy_gate",
        capabilities=frozenset({AgentCapability.ENFORCE_RISK}),
        forbidden=frozenset({AgentCapability.WRITE_CODE}),
    ),
    AgentRole.COR.KAIROS: AgentSpec(
        role=AgentRole.COR.KAIROS,
        temporal_activity="j5_kairos_distill",
        capabilities=frozenset({AgentCapability.DISTILL_KNOWLEDGE}),
        forbidden=frozenset({AgentCapability.WRITE_CODE}),
    ),
    AgentRole.AEGAEON: AgentSpec(
        role=AgentRole.AEGAEON,
        temporal_activity="j4_aegaeon_cache",
        capabilities=frozenset({AgentCapability.MANAGE_CACHE}),
        forbidden=frozenset({AgentCapability.WRITE_CODE}),
    ),
    AgentRole.OMEGA_AUTH: AgentSpec(
        role=AgentRole.OMEGA_AUTH,
        temporal_activity="j7_omega_auth",
        capabilities=frozenset({AgentCapability.FETCH_SECRETS}),
        forbidden=frozenset({AgentCapability.WRITE_CODE}),
    ),
    AgentRole.RICH_HICKEY: AgentSpec(
        role=AgentRole.RICH_HICKEY,
        temporal_activity="j8_hickey_enforce",
        capabilities=frozenset({AgentCapability.ENFORCE_SIMPLICITY}),
        forbidden=frozenset(),
    ),
}


class SynthesisCoordinator:
    """Agent-0: The Board — orchestrates the 8-agent synthesis.

    Validates agent capability boundaries before dispatching work.
    Prevents agents from operating outside their authorized scope.
    """

    def __init__(self) -> None:
        self._map = SYNTHESIS_MAP

    def get_agent_spec(self, role: AgentRole) -> AgentSpec:
        """Retrieve the spec for a given agent role.

        Args:
            role: The agent role to look up.

        Returns:
            The agent specification.

        Raises:
            KeyError: If the role is not in the synthesis map.
        """
        return self._map[role]

    def validate_capability(
        self,
        role: AgentRole,
        capability: AgentCapability,
    ) -> bool:
        """Check if an agent is authorized for a capability.

        Args:
            role: The agent attempting the action.
            capability: The capability being attempted.

        Returns:
            True if authorized, False if forbidden.

        Raises:
            PermissionError: If the capability is explicitly forbidden.
        """
        spec = self.get_agent_spec(role)

        if capability in spec.forbidden:
            logger.error(
                "🚫 BOUNDARY VIOLATION: Agent %s attempted forbidden capability %s",
                role.value,
                capability.value,
            )
            raise PermissionError(
                f"Agent {role.value} is forbidden from {capability.value}. Authorized capabilities: {[c.value for c in spec.capabilities]}"
            )

        if capability not in spec.capabilities:
            logger.warning(
                "⚠️ Agent %s lacks capability %s (not forbidden, but not authorized)",
                role.value,
                capability.value,
            )
            return False

        logger.info(
            "✅ Agent %s authorized for %s → activity %s",
            role.value,
            capability.value,
            spec.temporal_activity,
        )
        return True

    def dispatch(self, role: AgentRole, capability: AgentCapability) -> str:
        """Validate and return the Temporal activity name for dispatch.

        Args:
            role: The agent to dispatch.
            capability: The capability being exercised.

        Returns:
            The Temporal activity name to execute.

        Raises:
            PermissionError: If the capability is forbidden.
            ValueError: If the capability is not authorized.
        """
        if not self.validate_capability(role, capability):
            raise ValueError(f"Agent {role.value} is not authorized for {capability.value}")
        return self.get_agent_spec(role).temporal_activity

    def get_triad_activities(self) -> list[str]:
        """Return the Temporal activity names for the Builder/Reviewer/Tester triad.

        Returns:
            List of 3 activity names in execution order.
        """
        return [
            self._map[AgentRole.BUILDER].temporal_activity,
            self._map[AgentRole.REVIEWER].temporal_activity,
            self._map[AgentRole.TESTER].temporal_activity,
        ]

    def get_daemon_activities(self) -> list[str]:
        """Return the Temporal activity names for support daemons (5–8).

        Returns:
            List of 4 activity names for COR.KAIROS, Aegaeon, Omega, Hickey.
        """
        return [
            self._map[AgentRole.COR.KAIROS].temporal_activity,
            self._map[AgentRole.AEGAEON].temporal_activity,
            self._map[AgentRole.OMEGA_AUTH].temporal_activity,
            self._map[AgentRole.RICH_HICKEY].temporal_activity,
        ]
