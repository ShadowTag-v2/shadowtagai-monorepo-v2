# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
P4.3: Plan Mode V2 (Interview Phase)

Require agent to explicitly output `[PLAN_MODE_V2_ACTIVE]` when researching.
Automatically prompt user for clarification if uncertainty > threshold.
"""

import logging

logger = logging.getLogger(__name__)


class PlanModeInterview:
  def __init__(self, uncertainty_threshold: float = 0.7):
    self.uncertainty_threshold = uncertainty_threshold

  def activate(self) -> str:
    """
    Activates Plan Mode V2.
    """
    return "[PLAN_MODE_V2_ACTIVE]"

  def evaluate_uncertainty(self, uncertainty_score: float, topic: str) -> str | None:
    """
    Evaluates if the uncertainty score requires prompting the user.
    """
    if uncertainty_score > self.uncertainty_threshold:
      logger.info(
        f"Uncertainty ({uncertainty_score}) exceeds threshold ({self.uncertainty_threshold}) for topic: {topic}"
      )
      return (
        f"I need some clarification on {topic}. Could you please provide more details?"
      )
    return None
