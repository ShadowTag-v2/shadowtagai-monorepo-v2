"""
Base Skill class for the pinkln Agent Architecture System.

Skills are atomic capabilities - reusable expertise modules used by agents.
Examples: ResearchExplorer, DesignCritic, CopyConverter, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SkillTrigger(Enum):
    """When to trigger this skill."""

    MANUAL = "manual"  # Explicitly called
    AUTO = "auto"  # Automatically triggered by context
    CONDITIONAL = "conditional"  # Triggered when conditions met


@dataclass
class SkillMetadata:
    """Metadata for a skill."""

    name: str
    version: str
    description: str
    triggers: list[str] = field(default_factory=list)
    author: str = "pinkln"
    tags: list[str] = field(default_factory=list)


class BaseSkill(ABC):
    """
    Base class for all pinkln Skills.

    A Skill is a reusable capability or expertise module. Think of it like a
    library function, but for prompting/agent behavior.

    Every Skill:
    - Captures our voice and standards ("boy scout rule", aesthetic, ruthlessness)
    - Aligns with craftmanship ethos: elegant, intuitive, removing complexity
    - Questions assumptions ("why must it function so?")
    - Plans like Da Vinci, crafts like Jobs
    """

    def __init__(self, name: str, version: str = "1.0", description: str = ""):
        """
        Initialize a skill.

        Args:
            name: Skill name
            version: Version number
            description: Description of what this skill does
        """
        self.metadata = SkillMetadata(name=name, version=version, description=description)
        self.context: dict[str, Any] | None = None

    @abstractmethod
    async def execute(self, input_data: dict[str, Any], **kwargs) -> dict[str, Any]:
        """
        Execute the skill.

        Args:
            input_data: Input data for the skill
            **kwargs: Additional arguments

        Returns:
            Result dictionary with:
            - output: The main result
            - metadata: Execution metadata
            - critique: Self-critique of the result
            - assumptions: Assumptions made
        """
        pass

    @abstractmethod
    def get_prompt_template(self) -> str:
        """
        Get the prompt template for this skill.

        Returns:
            Formatted prompt string
        """
        pass

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """
        Validate input data.

        Args:
            input_data: Input to validate

        Returns:
            True if valid
        """
        return True  # Override in subclasses for specific validation

    def reflect(self, output: Any) -> dict[str, Any]:
        """
        Reflect on the output quality (part of RCR framework).

        Args:
            output: The output to reflect on

        Returns:
            Reflection dictionary with assumptions, weaknesses, improvements
        """
        return {"assumptions": [], "weaknesses": [], "improvements": [], "confidence": 0.8}

    def critique(self, output: Any) -> dict[str, Any]:
        """
        Critique the output (part of RCR framework).

        Args:
            output: Output to critique

        Returns:
            Critique dictionary
        """
        return {"flaws": [], "inefficiencies": [], "edge_cases_missed": [], "complexity_issues": []}

    def set_context(self, context: dict[str, Any]):
        """Set execution context."""
        self.context = context

    def get_metadata(self) -> dict[str, Any]:
        """Get skill metadata."""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "description": self.metadata.description,
            "triggers": self.metadata.triggers,
            "author": self.metadata.author,
            "tags": self.metadata.tags,
        }

    def __repr__(self) -> str:
        return f"<Skill: {self.metadata.name} v{self.metadata.version}>"


class SkillRegistry:
    """Registry for managing skills."""

    def __init__(self):
        self.skills: dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill):
        """Register a skill."""
        self.skills[skill.metadata.name] = skill

    def get(self, name: str) -> BaseSkill | None:
        """Get a skill by name."""
        return self.skills.get(name)

    def list_skills(self) -> list[str]:
        """List all registered skills."""
        return list(self.skills.keys())

    def get_skills_by_tag(self, tag: str) -> list[BaseSkill]:
        """Get skills with a specific tag."""
        return [skill for skill in self.skills.values() if tag in skill.metadata.tags]
