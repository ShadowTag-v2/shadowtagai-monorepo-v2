# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from dataclasses import dataclass

from .source import EthicalViolation, SourceType


@dataclass
class IngestionMetrics:
    """Metrics for ingestion layer performance"""

    items_per_day: int
    unique_sources_count: int
    average_cost_per_item: float
    average_relevance_score: float
    average_timeliness_score: float
    average_completeness_score: float
    tier_1_percentage: float
    tier_2_percentage: float
    tier_3_percentage: float
    runtime_minutes: float
    ethical_violations: list[EthicalViolation]
    source_type_distribution: dict[SourceType, int]
