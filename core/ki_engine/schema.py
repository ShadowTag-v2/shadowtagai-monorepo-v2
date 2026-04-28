# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""
KI Schema — Items 1, 7, 17: Typed knowledge with confidence, TTL, classification.

Ports the memory-kernel 9-atom type taxonomy to our KI system with:
- Confidence scoring (0.0–1.0)
- TTL auto-expiry (days or null=permanent)
- Privacy classification (PUBLIC/TEAM/PERSONAL/SECRET)
- Typed relations between KIs
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path


class KIType(StrEnum):
    """9-atom type taxonomy from memory-kernel."""

    FACT = "fact"
    DECISION = "decision"
    CONSTRAINT = "constraint"
    BELIEF = "belief"
    PREFERENCE = "preference"
    OPEN_QUESTION = "open_question"
    PROCEDURE = "procedure"
    ENTITY_SUMMARY = "entity_summary"
    CONFLICT = "conflict"


class KIStatus(StrEnum):
    """Lifecycle status for KIs."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class KIClassification(StrEnum):
    """Privacy classification for KIs."""

    PUBLIC = "public"
    TEAM = "team"
    PERSONAL = "personal"
    SECRET = "secret"


class RelationType(StrEnum):
    """Typed relations between KIs."""

    EXTENDS = "extends"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CAUSED_BY = "caused_by"
    SUPERSEDES = "supersedes"
    APPLIED_TO = "applied_to"
    RELATED = "related"


# Default TTLs by type (days, None = permanent)
DEFAULT_TTLS: dict[KIType, int | None] = {
    KIType.FACT: None,  # Permanent
    KIType.DECISION: None,  # Permanent
    KIType.CONSTRAINT: None,  # Permanent
    KIType.BELIEF: 30,  # 30 days
    KIType.PREFERENCE: 180,  # 6 months
    KIType.OPEN_QUESTION: 90,  # 3 months
    KIType.PROCEDURE: None,  # Permanent
    KIType.ENTITY_SUMMARY: 180,  # 6 months
    KIType.CONFLICT: 30,  # 30 days
}

# Default recall weights by type
DEFAULT_TYPE_WEIGHTS: dict[KIType, float] = {
    KIType.FACT: 1.5,
    KIType.DECISION: 2.0,
    KIType.CONSTRAINT: 2.0,
    KIType.BELIEF: 0.8,
    KIType.PREFERENCE: 0.5,
    KIType.OPEN_QUESTION: 1.0,
    KIType.PROCEDURE: 1.0,
    KIType.ENTITY_SUMMARY: 0.5,
    KIType.CONFLICT: 1.8,  # High — alerts
}

# Confidence thresholds
PROMOTION_THRESHOLD = 0.9  # belief → fact when confidence ≥ 0.9
CONFIDENCE_FLOOR = 0.3  # Below this, consider for pruning


@dataclass
class KIRelation:
    """A typed edge between two KIs."""

    target_ki: str
    relation_type: RelationType
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


@dataclass
class KIMetadata:
    """Enhanced KI metadata with memory-kernel-inspired fields.

    Backward-compatible with existing metadata.json format.
    New fields have defaults so existing KIs load without changes.
    """

    # Original fields (backward-compatible)
    name: str = ""
    summary: str = ""
    created: str = ""
    updated: str = ""
    references: list = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # New fields from memory-kernel (Item 1, 7, 17)
    ki_type: KIType = KIType.FACT
    status: KIStatus = KIStatus.ACTIVE
    confidence: float = 1.0
    ttl_days: int | None = None
    classification: KIClassification = KIClassification.TEAM
    relations: list[KIRelation] = field(default_factory=list)
    agent_id: str | None = None  # For per-agent isolation (Item 11)

    def __post_init__(self):
        now = datetime.now(UTC).isoformat()
        if not self.created:
            self.created = now
        if not self.updated:
            self.updated = now
        if self.ttl_days is None and isinstance(self.ki_type, KIType):
            self.ttl_days = DEFAULT_TTLS.get(self.ki_type)

    @property
    def age_days(self) -> float:
        """Age in days since last update."""
        try:
            updated = datetime.fromisoformat(self.updated.replace("Z", "+00:00"))
            return (datetime.now(UTC) - updated).total_seconds() / 86400
        except ValueError, TypeError:
            return 0.0

    @property
    def is_expired(self) -> bool:
        """Check if TTL has been exceeded."""
        if self.ttl_days is None:
            return False
        return self.age_days > self.ttl_days

    @property
    def recall_weight(self) -> float:
        """Effective recall weight = type_weight × confidence."""
        type_w = DEFAULT_TYPE_WEIGHTS.get(self.ki_type, 1.0)
        return type_w * self.confidence

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict (backward-compatible)."""
        d = {
            "name": self.name,
            "summary": self.summary,
            "created": self.created,
            "updated": self.updated,
            "references": self.references,
            "tags": self.tags,
            # New fields
            "ki_type": self.ki_type.value if isinstance(self.ki_type, KIType) else self.ki_type,
            "status": self.status.value if isinstance(self.status, KIStatus) else self.status,
            "confidence": self.confidence,
            "ttl_days": self.ttl_days,
            "classification": self.classification.value if isinstance(self.classification, KIClassification) else self.classification,
        }
        if self.relations:
            d["relations"] = [
                {
                    "target_ki": r.target_ki,
                    "relation_type": r.relation_type.value if isinstance(r.relation_type, RelationType) else r.relation_type,
                    "created_at": r.created_at,
                }
                for r in self.relations
            ]
        if self.agent_id:
            d["agent_id"] = self.agent_id
        return d

    @classmethod
    def from_dict(cls, d: dict) -> KIMetadata:
        """Deserialize from JSON dict (handles legacy format)."""
        relations = []
        for r in d.get("relations", []):
            relations.append(
                KIRelation(
                    target_ki=r["target_ki"],
                    relation_type=RelationType(r.get("relation_type", "related")),
                    created_at=r.get("created_at", ""),
                )
            )

        # Handle legacy field names
        ki_type_str = d.get("ki_type", "fact")
        try:
            ki_type = KIType(ki_type_str)
        except ValueError:
            ki_type = KIType.FACT

        status_str = d.get("status", "active")
        try:
            status = KIStatus(status_str)
        except ValueError:
            status = KIStatus.ACTIVE

        classification_str = d.get("classification", "team")
        try:
            classification = KIClassification(classification_str)
        except ValueError:
            classification = KIClassification.TEAM

        return cls(
            name=d.get("name", ""),
            summary=d.get("summary", ""),
            created=d.get("created", d.get("createdAt", "")),
            updated=d.get("updated", d.get("updatedAt", "")),
            references=d.get("references", []),
            tags=d.get("tags", []),
            ki_type=ki_type,
            status=status,
            confidence=d.get("confidence", 1.0),
            ttl_days=d.get("ttl_days"),
            classification=classification,
            relations=relations,
            agent_id=d.get("agent_id"),
        )

    @classmethod
    def load(cls, metadata_path: Path) -> KIMetadata:
        """Load from a metadata.json file."""
        with open(metadata_path) as f:
            return cls.from_dict(json.load(f))

    def save(self, metadata_path: Path) -> None:
        """Save to a metadata.json file."""
        with open(metadata_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            f.write("\n")


def generate_ki_id(ki_type: KIType, name: str) -> str:
    """Generate a typed KI ID: TYPE-YYYY-MM-DD-SLUG-hash."""
    prefix_map = {
        KIType.FACT: "FACT",
        KIType.DECISION: "DECI",
        KIType.CONSTRAINT: "CONS",
        KIType.BELIEF: "BELI",
        KIType.PREFERENCE: "PREF",
        KIType.OPEN_QUESTION: "OPEN",
        KIType.PROCEDURE: "PROC",
        KIType.ENTITY_SUMMARY: "ENTS",
        KIType.CONFLICT: "CONF",
    }
    prefix = prefix_map.get(ki_type, "UNKN")
    date = datetime.now(UTC).strftime("%Y-%m-%d")
    slug = name.lower().replace(" ", "-")[:30]
    h = hashlib.sha256(f"{name}{date}".encode()).hexdigest()[:8]
    return f"{prefix}-{date}-{slug}-{h}"
