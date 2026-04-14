import time
from datetime import datetime
from typing import Any

from .ethicalcompliancevalidator import EthicalComplianceValidator, EthicalViolation
from .ingestionmetrics import IngestionMetrics
from .ingestionresult import IngestionResult
from .source import IngestedItem, Source, SourceTier, SourceType
from .tierclassifier import TierClassifier


class GeminiIngestionLayer:
    """
    Intelligence collection pipeline with ethical compliance

    Architecture:
    - GKE CronJob (nightly batch processing)
    - Multi-container setup (collectors, processors, validators)
    - ~45 min/night runtime target
    - ~$77/month operational cost

    Quality Gates:
    - Items/Day: Target 1000+ high-quality items
    - Sources: 10+ unique sources across 3+ types
    - Cost/Item: <$0.10 per item
    - Relevance: >0.7 average score

    Integration:
    - Called by services in 4 namespaces
    - Feeds data to Judge #6 enforcement layer
    - Outputs to AM briefing delivery
    """

    def __init__(
        self,
        ethical_validator: EthicalComplianceValidator | None = None,
        tier_classifier: TierClassifier | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.ethical_validator = ethical_validator or EthicalComplianceValidator()
        self.tier_classifier = tier_classifier or TierClassifier()
        self.config = config or {}
        self.target_items_per_day = self.config.get("target_items_per_day", 1000)
        self.target_unique_sources = self.config.get("target_unique_sources", 10)
        self.target_cost_per_item = self.config.get("target_cost_per_item", 0.1)
        self.target_relevance_score = self.config.get("target_relevance_score", 0.7)
        self.target_runtime_minutes = self.config.get("target_runtime_minutes", 45)
        self.sources: list[Source] = []

    def register_source(self, source: Source):
        """Register a data source"""
        if source.tier is None:
            source.tier = self.tier_classifier.classify(source)
        self.sources.append(source)

    def ingest(
        self, sources: list[Source] | None = None, target_items: int | None = None
    ) -> IngestionResult:
        """
        Run ingestion pipeline

        Args:
            sources: List of sources to ingest from (default: all registered)
            target_items: Target number of items to collect (default: config value)

        Returns:
            IngestionResult with items, metrics, and violations
        """
        start_time = time.perf_counter()
        sources = sources or self.sources
        target_items = target_items or self.target_items_per_day
        items: list[IngestedItem] = []
        violations: list[EthicalViolation] = []
        errors: list[str] = []
        for source in sources:
            if not source.enabled:
                continue
            try:
                robots_violation = self.ethical_validator.validate_robots_txt(source.url, source)
                if robots_violation:
                    violations.append(robots_violation)
                    if robots_violation.severity in ["high", "critical"]:
                        continue
                rate_violation = self.ethical_validator.validate_rate_limit(source)
                if rate_violation:
                    violations.append(rate_violation)
                    if rate_violation.severity in ["high", "critical"]:
                        continue
                source_items = self._collect_from_source(source, target_items // len(sources))
                for item in source_items:
                    attribution_violation = self.ethical_validator.validate_attribution(item)
                    if attribution_violation:
                        violations.append(attribution_violation)
                items.extend(source_items)
                self.ethical_validator.record_request(source)
            except Exception as e:
                errors.append(f"Error collecting from {source.url}: {str(e)}")
        runtime_minutes = (time.perf_counter() - start_time) / 60
        metrics = self._calculate_metrics(items, violations, runtime_minutes)
        return IngestionResult(
            items=items,
            metrics=metrics,
            violations=violations,
            runtime_minutes=runtime_minutes,
            success=len(errors) == 0,
            errors=errors,
        )

    def _collect_from_source(self, source: Source, target_count: int) -> list[IngestedItem]:
        """
        Collect items from a source (mock implementation)

        TODO: Implement actual collectors for each source type:
        - YouTube: YouTube Data API
        - Twitter: Twitter API v2
        - News: NewsAPI, RSS feeds
        - Web: BeautifulSoup, Scrapy
        """
        items = []
        for i in range(min(target_count, 50)):
            item = IngestedItem(
                item_id=f"{source.name}_{i}_{int(time.time())}",
                source=source,
                title=f"Sample item {i} from {source.name}",
                content=f"Content from {source.source_type.value}",
                url=f"{source.url}/item/{i}",
                ingested_at=datetime.utcnow(),
                relevance_score=0.7 + i % 3 * 0.1,
                timeliness_score=0.8,
                completeness_score=0.9,
                cost_usd=0.05,
                metadata={
                    "source_url": source.url,
                    "source_type": source.source_type.value,
                    "tier": source.tier.value,
                },
            )
            items.append(item)
        return items

    def _calculate_metrics(
        self, items: list[IngestedItem], violations: list[EthicalViolation], runtime_minutes: float
    ) -> IngestionMetrics:
        """Calculate ingestion metrics"""
        if not items:
            return IngestionMetrics(
                items_per_day=0,
                unique_sources_count=0,
                average_cost_per_item=0.0,
                average_relevance_score=0.0,
                average_timeliness_score=0.0,
                average_completeness_score=0.0,
                tier_1_percentage=0.0,
                tier_2_percentage=0.0,
                tier_3_percentage=0.0,
                runtime_minutes=runtime_minutes,
                ethical_violations=violations,
                source_type_distribution={},
            )
        total_cost = sum(item.cost_usd for item in items)
        avg_cost = total_cost / len(items) if items else 0.0
        avg_relevance = sum(item.relevance_score for item in items) / len(items)
        avg_timeliness = sum(item.timeliness_score for item in items) / len(items)
        avg_completeness = sum(item.completeness_score for item in items) / len(items)
        unique_sources = len(set(item.source.url for item in items))
        tier_counts = {SourceTier.TIER_1: 0, SourceTier.TIER_2: 0, SourceTier.TIER_3: 0}
        for item in items:
            tier_counts[item.source.tier] += 1
        total_items = len(items)
        tier_1_pct = tier_counts[SourceTier.TIER_1] / total_items * 100
        tier_2_pct = tier_counts[SourceTier.TIER_2] / total_items * 100
        tier_3_pct = tier_counts[SourceTier.TIER_3] / total_items * 100
        source_type_dist: dict[SourceType, int] = {}
        for item in items:
            source_type = item.source.source_type
            source_type_dist[source_type] = source_type_dist.get(source_type, 0) + 1
        return IngestionMetrics(
            items_per_day=total_items,
            unique_sources_count=unique_sources,
            average_cost_per_item=avg_cost,
            average_relevance_score=avg_relevance,
            average_timeliness_score=avg_timeliness,
            average_completeness_score=avg_completeness,
            tier_1_percentage=tier_1_pct,
            tier_2_percentage=tier_2_pct,
            tier_3_percentage=tier_3_pct,
            runtime_minutes=runtime_minutes,
            ethical_violations=violations,
            source_type_distribution=source_type_dist,
        )

    def validate_quality_gates(self, metrics: IngestionMetrics) -> dict[str, bool]:
        """Validate quality gates"""
        return {
            "items_per_day": metrics.items_per_day >= self.target_items_per_day,
            "unique_sources": metrics.unique_sources_count >= self.target_unique_sources,
            "cost_per_item": metrics.average_cost_per_item <= self.target_cost_per_item,
            "relevance_score": metrics.average_relevance_score >= self.target_relevance_score,
            "runtime": metrics.runtime_minutes <= self.target_runtime_minutes,
            "ethical_compliance": len(
                [v for v in metrics.ethical_violations if v.severity in ["high", "critical"]]
            )
            == 0,
        }

    def export_am_briefing(self, items: list[IngestedItem], format: str = "markdown") -> str:
        """
        Export AM (morning) briefing from ingested items

        Args:
            items: List of ingested items
            format: Output format ('markdown', 'json', 'html')

        Returns:
            Formatted briefing
        """
        if format == "markdown":
            return self._export_markdown_briefing(items)
        elif format == "json":
            import json

            return json.dumps(
                [
                    {
                        "title": item.title,
                        "url": item.url,
                        "source": item.source.name,
                        "tier": item.source.tier.value,
                        "relevance": item.relevance_score,
                    }
                    for item in items
                ],
                indent=2,
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_markdown_briefing(self, items: list[IngestedItem]) -> str:
        """Export markdown format briefing"""
        sorted_items = sorted(items, key=lambda x: x.relevance_score, reverse=True)
        briefing = "# Intelligence Briefing\n\n"
        briefing += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        briefing += f"**Total Items:** {len(items)}\n\n"
        for tier in [SourceTier.TIER_1, SourceTier.TIER_2, SourceTier.TIER_3]:
            tier_items = [i for i in sorted_items if i.source.tier == tier]
            if not tier_items:
                continue
            briefing += f"## {tier.value.replace('_', ' ').title()}\n\n"
            for item in tier_items[:10]:
                briefing += f"### {item.title}\n"
                briefing += f"- **Source:** {item.source.name}\n"
                briefing += f"- **Relevance:** {item.relevance_score:.2f}\n"
                briefing += f"- **URL:** {item.url}\n\n"
        return briefing
