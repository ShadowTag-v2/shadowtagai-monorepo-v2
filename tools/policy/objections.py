"""AiYouJR Objection Taxonomy Engine

Implements the "Voice Objections per AiYouJR" constraint from ATP 5-19.
Agents can formally register disputes against proposed actions, creating
an audit trail before the action proceeds or is blocked.

Objection Types:
- SAFETY: Action poses safety risk to users or data
- ETHICS: Action violates ethical guidelines or doctrine
- QUALITY: Action degrades code quality or introduces tech debt
- SCOPE: Action exceeds authorized scope boundaries
- COMPLIANCE: Action violates regulatory or legal constraints
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, UTC
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

OBJECTIONS_LOG = Path(os.environ.get(
    "OBJECTIONS_LOG",
    ".beads/objections.jsonl",
))


class ObjectionType(StrEnum):
    """ATP 5-19 objection categories."""

    SAFETY = "SAFETY"
    ETHICS = "ETHICS"
    QUALITY = "QUALITY"
    SCOPE = "SCOPE"
    COMPLIANCE = "COMPLIANCE"


class ObjectionResolution(StrEnum):
    """How the objection was resolved."""

    PENDING = "PENDING"
    OVERRIDDEN = "OVERRIDDEN"
    ACCEPTED = "ACCEPTED"
    ESCALATED = "ESCALATED"


@dataclass
class Objection:
    """A formal agent objection record."""

    agent_id: str
    objection_type: ObjectionType
    reason: str
    code_snippet: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    resolution: ObjectionResolution = ObjectionResolution.PENDING
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
    )


def log_objection(
    agent_id: str,
    reason: str,
    code_snippet: str = "",
    objection_type: ObjectionType = ObjectionType.QUALITY,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Log a formal objection from an agent.

    Args:
        agent_id: ID of the objecting agent.
        reason: Human-readable reason for the objection.
        code_snippet: Optional code that triggered the objection.
        objection_type: Category of objection (default: QUALITY).
        context: Optional additional context.

    Returns:
        Dict with status and the logged objection.
    """
    objection = Objection(
        agent_id=agent_id,
        objection_type=objection_type,
        reason=reason,
        code_snippet=code_snippet[:2000],  # Cap at 2KB
        context=context or {},
    )

    # Persist to JSONL log
    OBJECTIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(OBJECTIONS_LOG, "a") as f:
        f.write(json.dumps(asdict(objection)) + "\n")

    logger.warning(
        "OBJECTION_LOGGED",
        extra={
            "agent_id": agent_id,
            "type": objection_type.value,
            "reason": reason[:120],
        },
    )

    return {
        "status": "OBJECTION_LOGGED",
        "tier": "ATP_5_19_EVAL",
        "objection": asdict(objection),
    }


def get_objections(
    agent_id: str | None = None,
    resolution: ObjectionResolution | None = None,
) -> list[dict[str, Any]]:
    """Read objections from the log, optionally filtered.

    Args:
        agent_id: Filter by agent ID.
        resolution: Filter by resolution status.

    Returns:
        List of objection dicts matching the filters.
    """
    if not OBJECTIONS_LOG.exists():
        return []

    results = []
    with open(OBJECTIONS_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if agent_id and entry.get("agent_id") != agent_id:
                continue
            if resolution and entry.get("resolution") != resolution.value:
                continue
            results.append(entry)

    return results
