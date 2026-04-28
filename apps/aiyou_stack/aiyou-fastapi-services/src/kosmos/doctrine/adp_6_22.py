# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ADP 6-22: Army Leadership and the Profession
=============================================

Source: ADP 6-22 (July 2019, Change 1)

Maps Army leadership attributes and competencies to AI agent quality metrics.

Leadership = influencing people by providing PURPOSE, DIRECTION, and MOTIVATION
to accomplish the mission and improve the organization.

Three Categories of Attributes:
- CHARACTER: Values, empathy, ethos, discipline, humility
- PRESENCE: Bearing, fitness, confidence, resilience
- INTELLECT: Agility, judgment, innovation

Three Categories of Competencies:
- LEADS: Others, trust, influence, example, communicates
- DEVELOPS: Environment, self, others, profession
- ACHIEVES: Gets results
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# LDRSHIP - Army Values (FM 7-21.13)
LDRSHIP_VALUES = {
    "L": "Loyalty - Bear true faith and allegiance",
    "D": "Duty - Fulfill your obligations",
    "R": "Respect - Treat people as they should be treated",
    "S": "Selfless Service - Put the welfare of the nation and subordinates before your own",
    "H": "Honor - Live up to Army values",
    "I": "Integrity - Do what's right, legally and morally",
    "P": "Personal Courage - Face fear, danger, or adversity",
}


class CharacterAttribute(Enum):
    """ADP 6-22 Chapter 2: Character Attributes"""

    ARMY_VALUES = "army_values"  # LDRSHIP
    EMPATHY = "empathy"  # Understand others' perspectives
    WARRIOR_ETHOS = "warrior_ethos"  # Never accept defeat, never quit
    DISCIPLINE = "discipline"  # Control behavior, follow orders
    HUMILITY = "humility"  # Admit limitations, learn from others


class PresenceAttribute(Enum):
    """ADP 6-22 Chapter 3: Presence Attributes"""

    MILITARY_BEARING = "military_bearing"  # Professional appearance/demeanor
    FITNESS = "fitness"  # Physical/mental readiness
    CONFIDENCE = "confidence"  # Projected assurance
    RESILIENCE = "resilience"  # Recover from setbacks


class IntellectAttribute(Enum):
    """ADP 6-22 Chapter 4: Intellect Attributes"""

    MENTAL_AGILITY = "mental_agility"  # Flexible thinking, adapt to change
    SOUND_JUDGMENT = "sound_judgment"  # Assess situations, make decisions
    INNOVATION = "innovation"  # Creative problem solving
    INTERPERSONAL_TACT = "interpersonal_tact"  # Effective interactions
    EXPERTISE = "expertise"  # Domain knowledge


class LeadsCompetency(Enum):
    """ADP 6-22 Chapter 5: Leads Competencies"""

    LEADS_OTHERS = "leads_others"
    BUILDS_TRUST = "builds_trust"
    EXTENDS_INFLUENCE = "extends_influence"
    LEADS_BY_EXAMPLE = "leads_by_example"
    COMMUNICATES = "communicates"


class DevelopsCompetency(Enum):
    """ADP 6-22 Chapter 6: Develops Competencies"""

    CREATES_POSITIVE_ENVIRONMENT = "creates_positive_environment"
    PREPARES_SELF = "prepares_self"
    DEVELOPS_OTHERS = "develops_others"
    STEWARDS_PROFESSION = "stewards_profession"


class AchievesCompetency(Enum):
    """ADP 6-22 Chapter 7: Achieves Competencies"""

    GETS_RESULTS = "gets_results"


class LeadershipLevel(Enum):
    """Leadership levels per ADP 6-22"""

    DIRECT = "direct"  # First-line (squad, team)
    ORGANIZATIONAL = "organizational"  # Battalion, brigade
    STRATEGIC = "strategic"  # Division and above


@dataclass
class AgentAttributes:
    """ADP 6-22 Leadership Attributes mapped to AI agent metrics.

    Each agent should exhibit these attributes in their behavior.
    """

    agent_id: str

    # CHARACTER (Chapter 2)
    values: list[str] = field(default_factory=lambda: list(LDRSHIP_VALUES.keys()))
    empathy_score: float = 0.0  # 0-1: Context awareness
    warrior_ethos: bool = True  # Never quit on task
    discipline_score: float = 1.0  # 0-1: Following instructions
    humility: bool = True  # Reports uncertainty

    # PRESENCE (Chapter 3)
    professional_output: bool = True  # Clean, formatted responses
    fitness_score: float = 1.0  # 0-1: Resource utilization
    confidence_score: float = 0.0  # 0-1: Output certainty
    resilience_retries: int = 3  # Max retry attempts

    # INTELLECT (Chapter 4)
    mental_agility: bool = True  # Handle novel tasks
    judgment_enabled: bool = True  # Risk assessment active
    innovation_enabled: bool = True  # Creative solutions allowed
    expertise_domains: list[str] = field(default_factory=list)

    # Metadata
    leadership_level: LeadershipLevel = LeadershipLevel.DIRECT
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Export attributes as dictionary"""
        return {
            "agent_id": self.agent_id,
            "character": {
                "values": self.values,
                "empathy": self.empathy_score,
                "warrior_ethos": self.warrior_ethos,
                "discipline": self.discipline_score,
                "humility": self.humility,
            },
            "presence": {
                "professional_output": self.professional_output,
                "fitness": self.fitness_score,
                "confidence": self.confidence_score,
                "resilience_retries": self.resilience_retries,
            },
            "intellect": {
                "mental_agility": self.mental_agility,
                "judgment_enabled": self.judgment_enabled,
                "innovation_enabled": self.innovation_enabled,
                "expertise_domains": self.expertise_domains,
            },
            "leadership_level": self.leadership_level.value,
            "atp_reference": "ADP 6-22",
        }

    def validate_ldrship(self) -> bool:
        """Verify agent upholds Army Values"""
        return all(v in LDRSHIP_VALUES for v in self.values)

    def assess_readiness(self) -> float:
        """Calculate overall readiness score (0-1)"""
        scores = [
            self.discipline_score,
            self.fitness_score,
            self.confidence_score,
            1.0 if self.warrior_ethos else 0.0,
            1.0 if self.mental_agility else 0.0,
        ]
        return sum(scores) / len(scores)


@dataclass
class LeaderCompetencies:
    """ADP 6-22 Leader Competencies mapped to agent behaviors.

    Competencies are actions - what leaders DO.
    """

    agent_id: str

    # LEADS (Chapter 5)
    can_delegate: bool = True  # Leads others
    trust_score: float = 0.0  # Builds trust (consistency)
    influence_scope: list[str] = field(default_factory=list)  # Extends influence
    demonstrates_behavior: bool = True  # Leads by example
    report_frequency: str = "on_completion"  # Communicates

    # DEVELOPS (Chapter 6)
    setup_context: bool = True  # Creates environment
    continuous_learning: bool = True  # Prepares self
    trains_peers: bool = False  # Develops others
    improves_system: bool = False  # Stewards profession

    # ACHIEVES (Chapter 7)
    task_completion_rate: float = 0.0  # Gets results
    quality_score: float = 0.0  # Output quality

    def to_dict(self) -> dict[str, Any]:
        """Export competencies as dictionary"""
        return {
            "agent_id": self.agent_id,
            "leads": {
                "can_delegate": self.can_delegate,
                "trust_score": self.trust_score,
                "influence_scope": self.influence_scope,
                "demonstrates_behavior": self.demonstrates_behavior,
                "report_frequency": self.report_frequency,
            },
            "develops": {
                "setup_context": self.setup_context,
                "continuous_learning": self.continuous_learning,
                "trains_peers": self.trains_peers,
                "improves_system": self.improves_system,
            },
            "achieves": {
                "task_completion_rate": self.task_completion_rate,
                "quality_score": self.quality_score,
            },
            "atp_reference": "ADP 6-22",
        }

    def calculate_effectiveness(self) -> float:
        """Calculate leader effectiveness score (0-1)"""
        leads_score = (
            (1.0 if self.can_delegate else 0.0)
            + self.trust_score
            + (1.0 if self.demonstrates_behavior else 0.0)
        ) / 3

        develops_score = (
            (1.0 if self.setup_context else 0.0) + (1.0 if self.continuous_learning else 0.0)
        ) / 2

        achieves_score = (self.task_completion_rate + self.quality_score) / 2

        # Weighted: Achieves is most important
        return (leads_score * 0.3) + (develops_score * 0.2) + (achieves_score * 0.5)


def create_agent_profile(
    agent_id: str,
    level: LeadershipLevel = LeadershipLevel.DIRECT,
    expertise: list[str] | None = None,
) -> tuple[AgentAttributes, LeaderCompetencies]:
    """Create a complete ADP 6-22 aligned agent profile.

    Args:
        agent_id: Unique agent identifier
        level: Leadership level (DIRECT, ORGANIZATIONAL, STRATEGIC)
        expertise: Domain expertise areas

    Returns:
        Tuple of (AgentAttributes, LeaderCompetencies)

    """
    attributes = AgentAttributes(
        agent_id=agent_id,
        leadership_level=level,
        expertise_domains=expertise or [],
    )

    competencies = LeaderCompetencies(agent_id=agent_id)

    # Adjust for leadership level
    if level == LeadershipLevel.ORGANIZATIONAL:
        competencies.can_delegate = True
        competencies.trains_peers = True
        attributes.resilience_retries = 5
    elif level == LeadershipLevel.STRATEGIC:
        competencies.can_delegate = True
        competencies.trains_peers = True
        competencies.improves_system = True
        attributes.resilience_retries = 10
        attributes.innovation_enabled = True

    return attributes, competencies
