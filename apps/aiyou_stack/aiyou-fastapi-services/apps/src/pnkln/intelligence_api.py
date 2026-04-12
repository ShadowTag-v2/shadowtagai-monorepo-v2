"""
PNKLN Intelligence-as-a-Service API
Monetize the intelligence pipeline (currently $77/mo cost, $0 revenue)

Revenue model:
- Tier 1 feed: $499/mo (priority intelligence)
- Tier 2 feed: $199/mo (standard intelligence)
- Tier 3 feed: $49/mo (background intelligence)
- API access: $29-$499/mo (metered)
- Data enrichment: $0.01-$0.05/item

Year 1 target: $50K revenue (5 customers @ $10K/year avg)
Year 5 target: $2M revenue (enterprise contracts + API revenue)
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class IntelligenceTier(StrEnum):
    TIER_1_PRIORITY = "tier_1_priority"  # $499/mo
    TIER_2_STANDARD = "tier_2_standard"  # $199/mo
    TIER_3_BACKGROUND = "tier_3_background"  # $49/mo
    TIER_30_SOVEREIGN = "tier_30_sovereign"  # $1M+ (Private Instance)


class EnrichmentType(StrEnum):
    SENTIMENT = "sentiment"  # $0.01
    ENTITIES = "entities"  # $0.02
    SUMMARY = "summary"  # $0.03
    CLASSIFICATION = "classification"  # $0.05


PRICING_TABLE = {
    EnrichmentType.SENTIMENT: 0.01,
    EnrichmentType.ENTITIES: 0.02,
    EnrichmentType.SUMMARY: 0.03,
    EnrichmentType.CLASSIFICATION: 0.05,
}


class UsageRecord(BaseModel):
    customer_id: str
    timestamp: datetime
    requests_count: int = 0
    enrichment_counts: dict[EnrichmentType, int] = Field(default_factory=dict)

    def calculate_cost(self) -> float:
        cost = 0.0
        # API calls metering (example: 1000 free, then $0.001)
        if self.requests_count > 1000:
            cost += (self.requests_count - 1000) * 0.001

        for etype, count in self.enrichment_counts.items():
            cost += count * PRICING_TABLE.get(etype, 0.0)
        return cost


class IntelligenceAPI:
    def __init__(self):
        self.usage_db: dict[str, UsageRecord] = {}

    def log_usage(self, customer_id: str, enrichment: EnrichmentType | None = None):
        if customer_id not in self.usage_db:
            self.usage_db[customer_id] = UsageRecord(
                customer_id=customer_id, timestamp=datetime.now()
            )

        record = self.usage_db[customer_id]
        record.requests_count += 1
        if enrichment:
            record.enrichment_counts[enrichment] = record.enrichment_counts.get(enrichment, 0) + 1

    def get_current_bill(self, customer_id: str) -> float:
        if customer_id not in self.usage_db:
            return 0.0
        return self.usage_db[customer_id].calculate_cost()

    def get_tier_features(self, tier: IntelligenceTier) -> dict[str, Any]:
        if tier == IntelligenceTier.TIER_30_SOVEREIGN:
            return {
                "latency": "zero-latency (on-prem)",
                "sources": "classified/internal",
                "support": "dedicated_engineer",
                "features": ["full_source_code", "white_label", "custom_models"],
            }
        elif tier == IntelligenceTier.TIER_1_PRIORITY:
            return {"latency": "realtime", "sources": "all", "support": "24/7"}
        elif tier == IntelligenceTier.TIER_2_STANDARD:
            return {"latency": "15min", "sources": "major", "support": "email"}
        return {"latency": "daily", "sources": "public", "support": "community"}
