# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ULTRATHINK Framework - Base Skill

Foundation class for all skills in the ULTRATHINK framework.
Skills are reusable expertise libraries that can be invoked by any agent.
"""

from abc import ABC, abstractmethod
from typing import Any
from .types import SkillInput, SkillOutput, SkillType, UltrathinkConfig


class BaseSkill(ABC):
  """
  Base class for all ULTRATHINK skills.

  Skills are domain-specific instruction sets that embed
  the ULTRATHINK philosophy while providing specialized capabilities.
  """

  def __init__(
    self,
    skill_type: SkillType,
    name: str,
    description: str,
    config: UltrathinkConfig | None = None,
  ):
    self.skill_type = skill_type
    self.name = name
    self.description = description
    self.config = config or UltrathinkConfig()
    self._execution_count = 0
    self._success_count = 0

  @abstractmethod
  async def execute(self, skill_input: SkillInput) -> SkillOutput:
    """
    Execute the skill's primary function.

    Args:
        skill_input: Input parameters and context

    Returns:
        SkillOutput with results and metadata
    """
    pass

  def get_activation_triggers(self) -> list[str]:
    """
    Get the phrases/patterns that should activate this skill.

    Returns:
        List of trigger patterns
    """
    return []

  def validate_input(self, skill_input: SkillInput) -> bool:
    """
    Validate that the input is appropriate for this skill.

    Returns:
        True if input is valid, False otherwise
    """
    if skill_input.skill_type != self.skill_type:
      return False

    # Additional validation can be added by subclasses
    return True

  def create_changelog(self, before: str, after: str, changes: list[str]) -> list[str]:
    """
    Create a changelog documenting the evolution.

    Args:
        before: State before skill execution
        after: State after skill execution
        changes: List of changes made

    Returns:
        Formatted changelog entries
    """
    changelog = [
      "=== CHANGELOG ===",
      "",
      "BEFORE:",
      before,
      "",
      "CHANGES:",
      *[f"- {change}" for change in changes],
      "",
      "AFTER:",
      after,
      "",
      "=== END CHANGELOG ===",
    ]
    return changelog

  def assess_improvement(self, before: str, after: str) -> dict[str, Any]:
    """
    Assess the improvement achieved by the skill execution.

    Returns:
        Assessment metrics
    """
    assessment = {
      "elegance_gain": 0.0,
      "complexity_reduction": 0.0,
      "clarity_improvement": 0.0,
      "functionality_preserved": True,
      "notes": [],
    }

    # In a real implementation, this would analyze the before/after
    # using various metrics. For now, return the framework.

    return assessment

  def record_execution(self, success: bool) -> None:
    """Record execution statistics."""
    self._execution_count += 1
    if success:
      self._success_count += 1

  def get_success_rate(self) -> float:
    """Get the skill's success rate."""
    if self._execution_count == 0:
      return 0.0
    return self._success_count / self._execution_count

  def get_metadata(self) -> dict[str, Any]:
    """Get skill metadata including statistics."""
    return {
      "skill_type": self.skill_type.value,
      "name": self.name,
      "description": self.description,
      "execution_count": self._execution_count,
      "success_count": self._success_count,
      "success_rate": self.get_success_rate(),
    }
