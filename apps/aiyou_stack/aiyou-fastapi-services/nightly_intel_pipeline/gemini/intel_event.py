# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""IntelEvent Schema - Structured Intelligence Event
=================================================
Core dataclass for normalized intelligence events.

This is the output format from Gemini extraction, consumed by JR Engine.
"""

import hashlib
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import StrEnum


class SourceType(StrEnum):
    """Type of intelligence source"""

    REGULATION = "regulation"  # Laws, rules, regulations
    NEWS = "news"  # News articles, press releases
    RFP = "rfp"  # Requests for proposals
    COMPETITOR_DOC = "competitor_doc"  # Competitor documentation
    BLOG = "blog"  # Technical blogs, tutorials
    LAWSUIT = "lawsuit"  # Legal filings, court cases
    RESEARCH = "research"  # Academic papers (arXiv)
    GITHUB = "github"  # GitHub repositories
    FEDERAL_REGISTER = "federal_register"  # Federal Register documents
    INDUSTRY = "industry"  # Industry reports, analysis
    UNKNOWN = "unknown"  # Unclassified content


class ChangeType(StrEnum):
    """Type of change/event"""

    NEW_LAW = "new_law"  # New legislation enacted
    AMENDMENT = "amendment"  # Change to existing law/rule
    GUIDANCE = "guidance"  # Agency guidance, interpretation
    ANNOUNCEMENT = "announcement"  # General announcement
    PROPOSED_RULE = "proposed_rule"  # Proposed rulemaking
    FINAL_RULE = "final_rule"  # Final rule published
    ENFORCEMENT = "enforcement"  # Enforcement action
    DEADLINE = "deadline"  # Compliance deadline
    RESEARCH_PAPER = "research_paper"  # New research published
    CODE_RELEASE = "code_release"  # Software release
    UPDATE = "update"  # General update
    UNKNOWN = "unknown"


class Jurisdiction(StrEnum):
    """Jurisdiction/geographic scope"""

    US_FEDERAL = "US-FEDERAL"
    US_CA = "US-CA"  # California
    US_NY = "US-NY"  # New York
    US_TX = "US-TX"  # Texas
    US_FL = "US-FL"  # Florida
    US_OTHER = "US-OTHER"
    EU = "EU"  # European Union
    UK = "UK"  # United Kingdom
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass
class IntelEvent:
    """Structured intelligence event - output from Gemini extraction.

    This is the core data structure for the semantic ingestion layer.
    Raw documents are converted to IntelEvents before JR Engine scoring.

    Attributes:
        id: Unique event identifier (UUID)
        source_url: Original source URL
        source_type: Classification of source (regulation, news, etc.)
        jurisdiction: Geographic/legal jurisdiction
        effective_date: When the event takes effect (if applicable)
        topic_tags: List of topic classifications
        change_type: Type of change/event
        summary: Human-readable summary (from Gemini)
        impacts: List of business impact statements
        risk_tags: Risk classification tags
        confidence: Gemini's confidence score (0.0-1.0)
        raw_text_hash: SHA-256 hash of source text
        gemini_model: Model used for extraction
        created_at: When this event was created

    """

    # Core identifiers
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_url: str = ""
    source_type: SourceType = SourceType.UNKNOWN

    # Classification
    jurisdiction: Jurisdiction = Jurisdiction.UNKNOWN
    effective_date: date | None = None
    topic_tags: list[str] = field(default_factory=list)
    change_type: ChangeType = ChangeType.UNKNOWN

    # Content
    title: str = ""
    summary: str = ""
    impacts: list[str] = field(default_factory=list)
    risk_tags: list[str] = field(default_factory=list)

    # JR Engine hints (pre-filled by Gemini for faster scoring)
    purpose_hint: str = ""  # Suggested Purpose alignment
    reasons_hint: str = ""  # Suggested Reasons
    brakes_hint: list[str] = field(default_factory=list)  # Suggested Brakes

    # Metadata
    confidence: float = 0.0
    raw_text_hash: str = ""
    gemini_model: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    # Original content reference
    original_content_id: str = ""  # e.g., arxiv_id, repo_name, document_number
    original_file_path: str = ""  # Path to raw file

    @classmethod
    def from_raw_text(cls, text: str, source_url: str = "", content_id: str = "") -> "IntelEvent":
        """Create a minimal IntelEvent from raw text.

        This creates a placeholder that will be enriched by Gemini.

        Args:
            text: Raw text content
            source_url: Source URL
            content_id: Original content identifier

        Returns:
            IntelEvent with hash and minimal fields populated

        """
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        return cls(
            source_url=source_url,
            raw_text_hash=text_hash,
            original_content_id=content_id,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        d = asdict(self)

        # Convert enums to values
        d["source_type"] = self.source_type.value
        d["jurisdiction"] = self.jurisdiction.value
        d["change_type"] = self.change_type.value

        # Convert dates to ISO format
        if self.effective_date:
            d["effective_date"] = self.effective_date.isoformat()
        if self.created_at:
            d["created_at"] = self.created_at.isoformat()

        return d

    @classmethod
    def from_dict(cls, data: dict) -> "IntelEvent":
        """Create from dictionary (e.g., JSON response)"""
        # Convert string enums back to Enum types
        if "source_type" in data:
            try:
                data["source_type"] = SourceType(data["source_type"])
            except ValueError:
                data["source_type"] = SourceType.UNKNOWN

        if "jurisdiction" in data:
            try:
                data["jurisdiction"] = Jurisdiction(data["jurisdiction"])
            except ValueError:
                data["jurisdiction"] = Jurisdiction.UNKNOWN

        if "change_type" in data:
            try:
                data["change_type"] = ChangeType(data["change_type"])
            except ValueError:
                data["change_type"] = ChangeType.UNKNOWN

        # Convert date strings
        if "effective_date" in data and isinstance(data["effective_date"], str):
            try:
                data["effective_date"] = date.fromisoformat(data["effective_date"])
            except ValueError:
                data["effective_date"] = None

        if "created_at" in data and isinstance(data["created_at"], str):
            try:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            except ValueError:
                data["created_at"] = datetime.now()

        # Filter to only valid fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        return cls(**filtered_data)

    def is_high_priority(self) -> bool:
        """Check if this event is high priority based on risk tags"""
        high_priority_tags = {
            "compliance_deadline",
            "fine_per_violation",
            "enforcement_action",
            "executive_order",
            "critical_security",
        }
        return bool(set(self.risk_tags) & high_priority_tags)

    def get_jr_hints(self) -> dict:
        """Get pre-filled hints for JR Engine scoring.

        Returns:
            Dict with purpose_hint, reasons_hint, brakes_hint

        """
        return {
            "purpose_hint": self.purpose_hint,
            "reasons_hint": self.reasons_hint,
            "brakes_hint": self.brakes_hint,
        }
