# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""
Temporal Decay — Item 2: Exponential decay for KI recall ranking.

Implements ACT-R base-level activation with configurable half-life:
  decay(age_days) = exp(-λ × age_days)
  where λ = ln(2) / half_life_days

Combined recall score merges:
  - Type weight (from schema)
  - Confidence score
  - Temporal decay
  - Optional keyword match boost
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from core.ki_engine.schema import DEFAULT_TYPE_WEIGHTS, KIMetadata, KIType


# Default half-life: 30 days (belief matches TTL, facts decay slower)
DEFAULT_HALF_LIFE_DAYS = 30.0

# Per-type half-life overrides
TYPE_HALF_LIVES: dict[KIType, float] = {
    KIType.FACT: 365.0,  # Facts decay very slowly
    KIType.DECISION: 180.0,  # Decisions persist
    KIType.CONSTRAINT: 365.0,  # Constraints persist
    KIType.BELIEF: 30.0,  # Beliefs match TTL
    KIType.PREFERENCE: 90.0,  # Preferences moderate
    KIType.OPEN_QUESTION: 14.0,  # Questions decay fast
    KIType.PROCEDURE: 180.0,  # Procedures persist
    KIType.ENTITY_SUMMARY: 60.0,  # Summaries moderate
    KIType.CONFLICT: 7.0,  # Conflicts are urgent
}


def temporal_decay(
    age_days: float,
    half_life_days: float = DEFAULT_HALF_LIFE_DAYS,
) -> float:
    """Compute temporal decay factor using exponential decay.

    Returns a value in (0, 1] where:
      - age=0 → 1.0
      - age=half_life → 0.5
      - age=2×half_life → 0.25

    Args:
        age_days: Age of the KI in days.
        half_life_days: Half-life in days. After this many days,
            the decay factor is 0.5.

    Returns:
        Decay factor in (0, 1].
    """
    if age_days <= 0:
        return 1.0
    if half_life_days <= 0:
        return 0.0
    decay_rate = math.log(2) / half_life_days
    return math.exp(-decay_rate * age_days)


def recall_score(
    ki: KIMetadata,
    keyword_boost: float = 0.0,
    half_life_override: float | None = None,
) -> float:
    """Compute combined recall score for a KI.

    score = type_weight × confidence × decay × (1 + keyword_boost)

    Args:
        ki: The KI metadata.
        keyword_boost: Additional score from keyword/FTS match (0.0–1.0).
        half_life_override: Override the per-type half-life.

    Returns:
        Combined recall score (higher = more relevant).
    """
    # Type weight
    type_weight = DEFAULT_TYPE_WEIGHTS.get(ki.ki_type, 1.0)

    # Confidence
    confidence = max(0.0, min(1.0, ki.confidence))

    # Temporal decay with per-type half-life
    half_life = half_life_override or TYPE_HALF_LIVES.get(ki.ki_type, DEFAULT_HALF_LIFE_DAYS)
    decay = temporal_decay(ki.age_days, half_life)

    # Combined score
    return type_weight * confidence * decay * (1.0 + keyword_boost)


@dataclass
class RankedKI:
    """A KI with its computed recall score."""

    ki: KIMetadata
    score: float
    decay_factor: float
    keyword_boost: float = 0.0
    path: str = ""

    def __lt__(self, other: RankedKI) -> bool:
        return self.score < other.score


def rank_kis(
    kis: list[KIMetadata],
    keyword_boosts: dict[str, float] | None = None,
) -> list[RankedKI]:
    """Rank a list of KIs by recall score, descending.

    Args:
        kis: List of KI metadata to rank.
        keyword_boosts: Optional map of KI name → keyword boost score.

    Returns:
        Sorted list of RankedKI, highest score first.
    """
    boosts = keyword_boosts or {}
    ranked = []

    for ki in kis:
        boost = boosts.get(ki.name, 0.0)
        half_life = TYPE_HALF_LIVES.get(ki.ki_type, DEFAULT_HALF_LIFE_DAYS)
        decay = temporal_decay(ki.age_days, half_life)
        score = recall_score(ki, keyword_boost=boost)

        ranked.append(
            RankedKI(
                ki=ki,
                score=score,
                decay_factor=decay,
                keyword_boost=boost,
            )
        )

    ranked.sort(reverse=True, key=lambda r: r.score)
    return ranked
