# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Intelligence Pipeline - Data Models

Core data structures for intelligence items, scoring, and classification
"""

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum


class IntelligenceSource(Enum):
    """Source types for intelligence items"""

    FEDERAL_REGISTER = "federal_register"
    STATE_LEGISLATION = "state_legislation"
    RESEARCH_PAPER = "research_paper"
    TECH_NEWS = "tech_news"
    COMPETITOR_BLOG = "competitor_blog"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    INDUSTRY_PUBLICATION = "industry_publication"
    REGULATORY_AGENCY = "regulatory_agency"


class IntelligenceTier(Enum):
    """Tier classification for intelligence items"""

    TIER_1 = "tier_1"  # CEO briefing - critical/strategic
    TIER_2 = "tier_2"  # Auto-action - medium priority
    TIER_3 = "tier_3"  # Archive only - low priority


@dataclass
class IntelligenceItem:
    """Core intelligence item

    Represents a single piece of intelligence (regulation, news, paper, etc.)
    with metadata, content, and scoring information
    """

    source: IntelligenceSource
    title: str
    url: str
    content: str
    published_date: datetime
    metadata: dict = field(default_factory=dict)

    # Populated during scoring phase
    jr_score: float = 0.0
    jr_reasoning: str = ""

    # Populated during classification phase
    tier: IntelligenceTier | None = None
    tier_reasoning: str = ""

    # Populated during synthesis phase
    cor_synthesis: str = ""
    action_items: list[str] = field(default_factory=list)

    # System metadata
    ingested_at: datetime = field(default_factory=datetime.now)
    id: str = field(default="")

    def __post_init__(self):
        """Generate unique ID based on content"""
        if not self.id:
            content_hash = hashlib.sha256(
                f"{self.source.value}:{self.url}:{self.title}".encode(),
            ).hexdigest()[:16]
            self.id = f"intel_{content_hash}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["source"] = self.source.value
        data["tier"] = self.tier.value if self.tier else None
        data["published_date"] = self.published_date.isoformat()
        data["ingested_at"] = self.ingested_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "IntelligenceItem":
        """Create from dictionary"""
        data["source"] = IntelligenceSource(data["source"])
        if data.get("tier"):
            data["tier"] = IntelligenceTier(data["tier"])
        data["published_date"] = datetime.fromisoformat(data["published_date"])
        data["ingested_at"] = datetime.fromisoformat(data["ingested_at"])
        return cls(**data)


@dataclass
class JRScore:
    """JR Engine score with reasoning

    The JR (Junior) Engine provides initial scoring and reasoning
    for intelligence items before Cor Brain synthesis
    """

    score: float  # 0.0 to 1.0
    reasoning: str
    confidence: float  # 0.0 to 1.0
    key_factors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class TierClassification:
    """Tier classification result

    Determines whether item goes to:
    - Tier 1: CEO briefing (critical/strategic)
    - Tier 2: Auto-action (medium priority)
    - Tier 3: Archive only (low priority)
    """

    tier: IntelligenceTier
    reasoning: str
    confidence: float
    action_recommendation: str

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["tier"] = self.tier.value
        return data


@dataclass
class CorSynthesis:
    """Cor Brain synthesis for Tier 1 items

    Provides executive summary and strategic analysis
    """

    executive_summary: str
    business_impact: str
    recommended_actions: list[str]
    risk_assessment: str
    timeline: str
    stakeholders: list[str] = field(default_factory=list)
    estimated_cost: str | None = None
    estimated_value: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
