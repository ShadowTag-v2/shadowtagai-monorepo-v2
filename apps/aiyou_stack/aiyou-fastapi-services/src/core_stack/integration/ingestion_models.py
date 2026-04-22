"""PNKLN Core Stack™ — Gemini Ingestion Layer Data Models
Integration contract between Ingestion → Judge 6 → Services
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class SourceTier(Enum):
    """Source tier classification for intelligence quality"""

    TIER_1 = 1  # High-value, authoritative (YouTube official, major news APIs)
    TIER_2 = 2  # Medium-value, diverse perspectives (verified Twitter, regional news)
    TIER_3 = 3  # Low-value, bulk context (general Twitter, Reddit)


class ContentType(Enum):
    """Type of ingested content"""

    VIDEO_TRANSCRIPT = "video_transcript"
    TEXT_ARTICLE = "text_article"
    SOCIAL_POST = "social_post"
    API_RESPONSE = "api_response"
    SCRAPED_HTML = "scraped_html"


@dataclass
class QualityMetrics:
    """Quality assessment for ingested data batch"""

    avg_relevance: float  # 0.0-1.0, minimum 0.70
    completeness: float  # 0.0-1.0, minimum 0.90
    timeliness: float  # 0.0-1.0, freshness of data
    source_diversity: int  # Count of unique sources

    def meets_gates(self) -> bool:
        """Check if quality gates are met"""
        return self.avg_relevance >= 0.70 and self.completeness >= 0.90 and self.timeliness >= 0.80

    def to_dict(self) -> dict[str, Any]:
        return {
            "avg_relevance": round(self.avg_relevance, 3),
            "completeness": round(self.completeness, 3),
            "timeliness": round(self.timeliness, 3),
            "source_diversity": self.source_diversity,
        }


@dataclass
class CostSummary:
    """Cost tracking for ingestion run"""

    total_cost_usd: float
    cost_per_item: float
    api_costs: dict[str, float]  # Breakdown by API (YouTube, Twitter, etc.)
    compute_cost: float

    def meets_budget(self, max_cost_per_item: float = 0.001) -> bool:
        """Check if cost is within budget"""
        return self.cost_per_item <= max_cost_per_item

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cost_usd": round(self.total_cost_usd, 2),
            "cost_per_item": round(self.cost_per_item, 6),
            "api_costs": {k: round(v, 2) for k, v in self.api_costs.items()},
            "compute_cost": round(self.compute_cost, 2),
        }


@dataclass
class IngestedItem:
    """Individual intelligence item from Gemini Ingestion Layer.
    This is the atomic unit passed to Judge 6 for validation.
    """

    item_id: str
    source: str
    tier: SourceTier
    content_type: ContentType
    content: str
    metadata: dict[str, Any]
    ingestion_score: float  # Classifier confidence
    ingestion_timestamp: datetime

    # Judge 6 adds these fields during validation (initially None)
    judge_verdict: str | None = None
    prb_compliance: bool | None = None
    atp_519_risk: str | None = None  # RA-1 through RA-4
    judge_latency_us: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for Cloud Storage / Pub/Sub"""
        return {
            "item_id": self.item_id,
            "source": self.source,
            "tier": self.tier.value,
            "content_type": self.content_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "ingestion_score": round(self.ingestion_score, 3),
            "ingestion_timestamp": self.ingestion_timestamp.isoformat(),
            # Judge 6 fields (None if not yet validated)
            "judge_verdict": self.judge_verdict,
            "prb_compliance": self.prb_compliance,
            "atp_519_risk": self.atp_519_risk,
            "judge_latency_us": self.judge_latency_us,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IngestedItem":
        """Deserialize from Cloud Storage"""
        return cls(
            item_id=data["item_id"],
            source=data["source"],
            tier=SourceTier(data["tier"]),
            content_type=ContentType(data["content_type"]),
            content=data["content"],
            metadata=data["metadata"],
            ingestion_score=data["ingestion_score"],
            ingestion_timestamp=datetime.fromisoformat(data["ingestion_timestamp"]),
            judge_verdict=data.get("judge_verdict"),
            prb_compliance=data.get("prb_compliance"),
            atp_519_risk=data.get("atp_519_risk"),
            judge_latency_us=data.get("judge_latency_us"),
        )


@dataclass
class IngestionBriefing:
    """Complete output from Gemini Ingestion Layer (daily batch).
    This is what gets written to Cloud Storage and triggers Judge 6 update.
    """

    briefing_date: str  # YYYY-MM-DD
    ingestion_window_start: datetime
    ingestion_window_end: datetime
    total_items: int
    tier_distribution: dict[str, int]  # {"tier_1": 12456, "tier_2": 21089, ...}
    top_topics: list[dict[str, Any]]
    quality_metrics: QualityMetrics
    cost_summary: CostSummary
    items: list[IngestedItem]

    # Runtime metadata
    runtime_minutes: float
    crawler_version: str
    classifier_version: str

    def meets_quality_gates(self) -> bool:
        """Validate against all quality gates before Judge 6 ingestion.
        Rollback trigger: 3 consecutive days failing gates.
        """
        return (
            self.total_items >= 10000
            and self.quality_metrics.meets_gates()
            and self.cost_summary.meets_budget()
            and self.runtime_minutes <= 60
        )

    def get_tier_percentage(self, tier: SourceTier) -> float:
        """Calculate percentage of items in given tier"""
        tier_key = f"tier_{tier.value}"
        tier_count = self.tier_distribution.get(tier_key, 0)
        return (tier_count / self.total_items * 100) if self.total_items > 0 else 0.0

    def to_json(self) -> str:
        """Serialize for Cloud Storage (gs://pnkln-ingestion-daily/)"""
        data = {
            "briefing_date": self.briefing_date,
            "ingestion_window": {
                "start": self.ingestion_window_start.isoformat(),
                "end": self.ingestion_window_end.isoformat(),
            },
            "total_items": self.total_items,
            "tier_distribution": self.tier_distribution,
            "top_topics": self.top_topics,
            "quality_metrics": self.quality_metrics.to_dict(),
            "cost_summary": self.cost_summary.to_dict(),
            "items": [item.to_dict() for item in self.items],
            "runtime_metadata": {
                "runtime_minutes": round(self.runtime_minutes, 2),
                "crawler_version": self.crawler_version,
                "classifier_version": self.classifier_version,
            },
            "delivery_status": "ready_for_judge_6"
            if self.meets_quality_gates()
            else "failed_quality_gates",
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "IngestionBriefing":
        """Deserialize from Cloud Storage"""
        data = json.loads(json_str)
        return cls(
            briefing_date=data["briefing_date"],
            ingestion_window_start=datetime.fromisoformat(data["ingestion_window"]["start"]),
            ingestion_window_end=datetime.fromisoformat(data["ingestion_window"]["end"]),
            total_items=data["total_items"],
            tier_distribution=data["tier_distribution"],
            top_topics=data["top_topics"],
            quality_metrics=QualityMetrics(**data["quality_metrics"]),
            cost_summary=CostSummary(**data["cost_summary"]),
            items=[IngestedItem.from_dict(item) for item in data["items"]],
            runtime_minutes=data["runtime_metadata"]["runtime_minutes"],
            crawler_version=data["runtime_metadata"]["crawler_version"],
            classifier_version=data["runtime_metadata"]["classifier_version"],
        )


@dataclass
class JudgeDecision:
    """Real-time validation response from Judge 6.
    Returned to services in <500μs p99.
    """

    item_id: str
    allowed: bool
    latency_us: int  # Must be <500,000 for p99
    coverage: float  # Must be ≥0.98
    reasoning: str | None
    fallback_triggered: bool

    # ATP 5-19 risk assessment
    risk_level: str  # RA-1 (Extremely High) through RA-4 (Low)
    prb_violations: list[str]  # Purpose/Reasons/Brakes violations

    def meets_sla(self) -> bool:
        """Check if decision meets Judge 6 SLA"""
        return (
            self.latency_us < 500_000  # p99 <500μs
            and self.coverage >= 0.98  # 98% coverage minimum
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "allowed": self.allowed,
            "latency_us": self.latency_us,
            "coverage": round(self.coverage, 4),
            "reasoning": self.reasoning,
            "fallback_triggered": self.fallback_triggered,
            "risk_level": self.risk_level,
            "prb_violations": self.prb_violations,
            "sla_met": self.meets_sla(),
        }


# Example usage / test data
if __name__ == "__main__":
    # Create sample ingested item
    item = IngestedItem(
        item_id="ing_20251115_000001",
        source="youtube.com/c/cspan",
        tier=SourceTier.TIER_1,
        content_type=ContentType.VIDEO_TRANSCRIPT,
        content="Senate hearing on AI regulation... [transcript]",
        metadata={"video_id": "dQw4w9WgXcQ", "duration_seconds": 3600, "upload_date": "2025-11-14"},
        ingestion_score=0.92,
        ingestion_timestamp=datetime.now(),
    )

    # Create sample briefing
    briefing = IngestionBriefing(
        briefing_date="2025-11-15",
        ingestion_window_start=datetime(2025, 11, 15, 2, 0, 0),
        ingestion_window_end=datetime(2025, 11, 15, 2, 45, 0),
        total_items=47234,
        tier_distribution={"tier_1": 12456, "tier_2": 21089, "tier_3": 13689},
        top_topics=[
            {"topic": "AI Regulation", "items": 8234, "avg_score": 0.87},
            {"topic": "DoD Procurement", "items": 3421, "avg_score": 0.82},
        ],
        quality_metrics=QualityMetrics(
            avg_relevance=0.76,
            completeness=0.94,
            timeliness=0.89,
            source_diversity=23,
        ),
        cost_summary=CostSummary(
            total_cost_usd=2.54,
            cost_per_item=0.000054,
            api_costs={"youtube": 1.20, "twitter": 0.80, "newsapi": 0.40},
            compute_cost=0.14,
        ),
        items=[item],
        runtime_minutes=44.5,
        crawler_version="v1.0.0",
        classifier_version="v1.0.0",
    )

    # Serialize
    print("=== INGESTION BRIEFING ===")
    print(briefing.to_json())
    print(f"\nQuality gates met: {briefing.meets_quality_gates()}")
    print(f"Tier 1 percentage: {briefing.get_tier_percentage(SourceTier.TIER_1):.1f}%")

    # Create sample Judge decision
    decision = JudgeDecision(
        item_id="ing_20251115_000001",
        allowed=True,
        latency_us=342,  # Well under 500μs
        coverage=0.987,
        reasoning="Compliant with ATP 5-19, no PRB violations",
        fallback_triggered=False,
        risk_level="RA-4 (Low)",
        prb_violations=[],
    )

    print("\n=== JUDGE #6 DECISION ===")
    print(json.dumps(decision.to_dict(), indent=2))
    print(f"\nSLA met: {decision.meets_sla()}")
