# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTagAI. All rights reserved.
"""JudgeSix-Human — Fast MITM gate for human/server actions.

Operates as the first checkpoint in the Cor.autoresearch loop.
Every human or server event passes through JudgeSix-Human before
reaching the engine.

Levels:
  0 — Pass (safe, routine)
  1 — Log (notable but allowed)
  2 — Warn (flag for review, allowed)
  3 — Show three COAs (Courses of Action) to operator
  4 — Dispatch Cor.autoresearch (automated deep analysis)
  5 — Hard lock, forensic packet, management alert

API endpoint: POST /v1/judge/human/evaluate
"""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


class ThreatLevel(enum.IntEnum):
  """JudgeSix-Human threat assessment levels."""

  PASS = 0
  LOG = 1
  WARN = 2
  SHOW_COAS = 3
  DISPATCH_AUTORESEARCH = 4
  HARD_LOCK = 5


@dataclass
class HumanGateResult:
  """Result of a JudgeSix-Human evaluation."""

  level: ThreatLevel = ThreatLevel.PASS
  action: str = ""
  coas: list[str] = field(default_factory=list)
  forensic_packet: dict[str, Any] | None = None
  metadata: dict[str, Any] = field(default_factory=dict)


class JudgeSixHuman:
  """JudgeSix-Human fast MITM gate.

  Evaluates incoming human/server actions against security policy.
  Runs in the control sidecar (uphillsnowball-control).
  """

  def __init__(self, strict_mode: bool = True) -> None:
    self._strict_mode = strict_mode
    self._evaluation_count: int = 0

  async def evaluate(
    self,
    action: str,
    context: dict[str, Any] | None = None,
  ) -> HumanGateResult:
    """Evaluate an incoming human/server action.

    Args:
        action: Description of the action to evaluate.
        context: Additional context (user, session, permissions).

    Returns:
        HumanGateResult with threat level and prescribed action.
    """
    self._evaluation_count += 1

    # TODO: Replace stub with actual policy evaluation
    result = HumanGateResult(
      level=ThreatLevel.PASS,
      action="allow",
      metadata={
        "evaluation_id": self._evaluation_count,
        "action_evaluated": action[:100],
      },
    )

    logger.info(
      "JudgeSix-Human eval #%d: level=%d action=%s",
      self._evaluation_count,
      result.level,
      result.action,
    )
    return result

  def generate_forensic_packet(
    self,
    action: str,
    context: dict[str, Any],
  ) -> dict[str, Any]:
    """Generate a forensic packet for Level 5 hard locks."""
    return {
      "action": action,
      "context": context,
      "evaluation_count": self._evaluation_count,
      "strict_mode": self._strict_mode,
    }
