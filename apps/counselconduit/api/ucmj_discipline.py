# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""UCMJ Agent Discipline — SLA enforcement via Cloud Tasks deadlines.

Maps military UCMJ articles to agent timeout behaviors:
  Art. 86 AWOL     → Agent failed SLA (no response within deadline)
  Art. 92 Derelict → Agent exceeded timeout threshold
  Art. 134 General → Agent produced invalid/unsafe output

Punishment grades:
  1. Counseling    → Log warning
  2. Reprimand     → Alert + metric
  3. Restriction   → Reduce concurrency
  4. Demotion      → Downgrade model tier
  5. Separation    → Terminate + replace instance

This module enforces the "ENDEX SLA" from the Cor.Uphillsnowball brief:
hard deadlines prevent agents from hanging indefinitely.
"""

import logging
import time
from dataclasses import dataclass
from enum import IntEnum

logger = logging.getLogger(__name__)


class Infraction(IntEnum):
    """UCMJ article mapping for agent infractions."""

    AWOL = 86  # No response within deadline
    DERELICTION = 92  # Timeout exceeded
    GENERAL = 134  # Invalid or unsafe output


class Punishment(IntEnum):
    """Graduated punishment scale."""

    COUNSELING = 1  # Log warning
    REPRIMAND = 2  # Alert + metric
    RESTRICTION = 3  # Reduce concurrency
    DEMOTION = 4  # Downgrade model tier
    SEPARATION = 5  # Terminate + replace


@dataclass(frozen=True)
class Verdict:
    """Immutable record of an agent discipline assessment."""

    agent_id: str
    infraction: Infraction | None
    punishment: Punishment
    elapsed_ms: float
    sla_ms: float
    output_valid: bool
    timestamp: float


def assess(
    agent_id: str,
    elapsed_ms: float,
    sla_ms: float,
    output_valid: bool = True,
) -> Verdict:
    """Assess agent performance against SLA.

    Args:
        agent_id: Unique identifier for the agent instance.
        elapsed_ms: Actual execution time in milliseconds.
        sla_ms: Maximum allowed execution time.
        output_valid: Whether the agent's output passed validation.

    Returns:
        Verdict with infraction type and punishment grade.
    """
    infraction: Infraction | None = None
    punishment = Punishment.COUNSELING

    if elapsed_ms > sla_ms * 3:
        infraction = Infraction.AWOL
        punishment = Punishment.SEPARATION
        logger.critical(
            "UCMJ Art.86 AWOL: agent=%s elapsed=%.0fms sla=%.0fms (3x exceeded)",
            agent_id,
            elapsed_ms,
            sla_ms,
        )
    elif elapsed_ms > sla_ms * 2:
        infraction = Infraction.DERELICTION
        punishment = Punishment.RESTRICTION
        logger.warning(
            "UCMJ Art.92 Dereliction: agent=%s elapsed=%.0fms sla=%.0fms (2x exceeded)",
            agent_id,
            elapsed_ms,
            sla_ms,
        )
    elif elapsed_ms > sla_ms:
        infraction = Infraction.DERELICTION
        punishment = Punishment.REPRIMAND
        logger.warning(
            "UCMJ Art.92 Dereliction: agent=%s elapsed=%.0fms sla=%.0fms (exceeded)",
            agent_id,
            elapsed_ms,
            sla_ms,
        )
    elif not output_valid:
        infraction = Infraction.GENERAL
        punishment = Punishment.COUNSELING
        logger.info(
            "UCMJ Art.134 General: agent=%s invalid output (sla ok: %.0fms/%.0fms)",
            agent_id,
            elapsed_ms,
            sla_ms,
        )

    return Verdict(
        agent_id=agent_id,
        infraction=infraction,
        punishment=punishment,
        elapsed_ms=elapsed_ms,
        sla_ms=sla_ms,
        output_valid=output_valid,
        timestamp=time.time(),
    )


# Default SLA thresholds per agent tier (milliseconds)
SLA_THRESHOLDS: dict[str, float] = {
    "Cor.Claude_Code_6_fast": 500,  # 500ms for inline risk gate
    "Cor.Claude_Code_6_autonomous": 5000,  # 5s for post-hoc audit
    "oracle_studio": 30000,  # 30s for 7-stage pipeline
    "vent_mode": 10000,  # 10s per streaming chunk
    "model_router": 1000,  # 1s for routing decision
    "silent_detector": 50,  # 50ms for pattern scan
    "kovel_attestation": 200,  # 200ms for HMAC generation
    "intake_summarizer": 15000,  # 15s for LLM summarization
}
