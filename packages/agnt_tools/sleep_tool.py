# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""SleepTool — Agent-callable pause mechanism.

Ported from: Claude Code src/tools/SleepTool/prompt.ts
Reference: Kairos Ultraplan P0 #1

Allows the agent to voluntarily yield the execution loop for a specified
duration without burning tokens or blocking API calls. This is the
counterpart to Claude Code's SleepTool which lets the agent pace itself
instead of outputting "still waiting" filler.

Usage:
    from packages.agnt_tools.sleep_tool import SleepTool
    tool = SleepTool()
    result = tool.execute(duration_seconds=30, reason="Waiting for CI pipeline")
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime

logger = logging.getLogger("agnt.sleep_tool")

# --- Constants ---------------------------------------------------------------

MIN_SLEEP_SECONDS = 1
MAX_SLEEP_SECONDS = 3600  # 1 hour — hard ceiling
DEFAULT_SLEEP_SECONDS = 30


# --- Data Models -------------------------------------------------------------


@dataclass
class SleepResult:
  """Result of a SleepTool execution."""

  requested_seconds: float
  actual_seconds: float
  reason: str
  slept_at: str
  woke_at: str
  was_capped: bool = False


# --- Tool Implementation -----------------------------------------------------


class SleepTool:
  """Agent-callable tool that pauses execution without consuming tokens.

  The SleepTool gives the agent the ability to voluntarily yield the
  execution loop. This is critical for:
  - Waiting for external processes (CI, builds, deploys)
  - Rate limit backoff without burning context window
  - Pacing autonomous loops to avoid API quota exhaustion
  - Allowing the user time to respond to escalations

  The tool enforces hard limits (1s min, 3600s max) to prevent
  degenerate sleep requests.
  """

  name = "SleepTool"
  description = "Pause execution for a specified duration without consuming tokens. Use when waiting for external processes, rate limits, or user input."

  def execute(
    self,
    duration_seconds: float = DEFAULT_SLEEP_SECONDS,
    reason: str = "Agent-requested pause",
  ) -> SleepResult:
    """Execute the sleep.

    Args:
        duration_seconds: How long to sleep. Clamped to [1, 3600].
        reason: Human-readable reason for the sleep (logged).

    Returns:
        SleepResult with timing details.
    """
    was_capped = False

    # Clamp duration
    if duration_seconds < MIN_SLEEP_SECONDS:
      duration_seconds = MIN_SLEEP_SECONDS
      was_capped = True
    elif duration_seconds > MAX_SLEEP_SECONDS:
      duration_seconds = MAX_SLEEP_SECONDS
      was_capped = True

    slept_at = datetime.now(UTC).isoformat()
    logger.info(
      "SleepTool: sleeping %.1fs — %s%s",
      duration_seconds,
      reason,
      " (CAPPED)" if was_capped else "",
    )

    time.sleep(duration_seconds)

    woke_at = datetime.now(UTC).isoformat()
    actual = (
      datetime.fromisoformat(woke_at) - datetime.fromisoformat(slept_at)
    ).total_seconds()

    logger.info("SleepTool: woke after %.1fs", actual)

    return SleepResult(
      requested_seconds=duration_seconds,
      actual_seconds=actual,
      reason=reason,
      slept_at=slept_at,
      woke_at=woke_at,
      was_capped=was_capped,
    )
