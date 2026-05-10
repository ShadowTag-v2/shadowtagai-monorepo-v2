# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Away summary — session recap generator.

Ported from src/services/awaySummary.ts (Claude Code v2.1.91).
"""

from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)

RECENT_MESSAGE_WINDOW = 30


def build_away_prompt(session_memory: str | None = None) -> str:
  """Build the prompt for away summary generation."""
  mem = (
    f"Session memory (broader context):\n{session_memory}\n\n" if session_memory else ""
  )
  return (
    f"{mem}The user stepped away and is coming back. "
    "Write exactly 1-3 short sentences. "
    "Start by stating the high-level task — what they are building or debugging, "
    "not implementation details. Next: the concrete next step. "
    "Skip status reports and commit recaps."
  )


class SummaryGenerator(Protocol):
  """Protocol for LLM-based summary generation."""

  async def generate(
    self, messages: list[dict[str, str]], system_prompt: str
  ) -> str | None: ...


async def generate_away_summary(
  messages: list[dict[str, str]],
  *,
  generator: SummaryGenerator,
  session_memory: str | None = None,
) -> str | None:
  """Generate a short session recap.

  Returns None on error/abort/empty transcript.
  """
  if not messages:
    return None

  try:
    recent = messages[-RECENT_MESSAGE_WINDOW:]
    prompt = build_away_prompt(session_memory)
    recent = [*recent, {"role": "user", "content": prompt}]
    return await generator.generate(recent, prompt)
  except Exception:
    logger.debug("Away summary generation failed", exc_info=True)
    return None
