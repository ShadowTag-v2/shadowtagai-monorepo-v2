"""Gemini Ingestion Layer
Intelligence collection pipeline with ethical compliance

Architecture: GKE CronJob Multi-Container
Runtime: ~45 min/night (batch processing)
Cost: ~$77/month operational
Quality Gates: Items/Day, Sources, Cost/Item, Relevance Scores

Function: Proactive collector (upstream of Judge 6 enforcement)
Integration: Called by services in 4 namespaces
"""

import re
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse


class SourceTier(Enum):
    """Data source tier classification"""

    TIER_1 = "tier_1"  # High-value, authoritative sources
    TIER_2 = "tier_2"  # Moderate-value, verified sources
    TIER_3 = "tier_3"  # Low-value, general sources


class SourceType(Enum):
    """Types of data sources"""

    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    RSS = "rss"
    API = "api"
    WEB = "web"
    ACADEMIC = "academic"
    GOVERNMENT = "government"


class EthicalViolationType(Enum):
    """Types of ethical compliance violations"""

    ROBOTS_TXT = "robots_txt_violation"
    RATE_LIMIT = "rate_limit_exceeded"
    TERMS_OF_SERVICE = "tos_violation"
    COPYRIGHT = "copyright_risk"
    PRIVACY = "privacy_violation"
    ATTRIBUTION = "missing_attribution"


@dataclass
class Source:
    """Represents a data source"""

    url: str
    source_type: SourceType
    tier: SourceTier
    name: str
    enabled: bool = True
    rate_limit_per_hour: int = 60
    last_accessed: datetime | None = None
    robots_txt_checked: bool = False
    robots_txt_compliant: bool = True


@dataclass
class IngestedItem:
    """Represents an ingested data item"""

    item_id: str
    source: Source
    title: str
    content: str
    url: str
    ingested_at: datetime
    relevance_score: float  # 0.0 to 1.0
    timeliness_score: float  # 0.0 to 1.0
    completeness_score: float  # 0.0 to 1.0
    cost_usd: float
    metadata: dict[str, Any]


@dataclass
class EthicalViolation:
    """Represents an ethical compliance violation"""

    violation_type: EthicalViolationType
    source: str
    description: str
    severity: str  # low, medium, high, critical
    timestamp: datetime
    remediation: str


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


@dataclass
class IngestionResult:
    """Result of ingestion operation"""

    items: list[IngestedItem]
    metrics: IngestionMetrics
    violations: list[EthicalViolation]
    runtime_minutes: float
    success: bool
    errors: list[str]


class EthicalComplianceValidator:
    """Validates ethical compliance for web crawling and data collection

    Checks:
    - robots.txt compliance
    - Rate limiting adherence
    - Terms of Service compliance
    - Attribution requirements
    - Privacy considerations
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.max_requests_per_hour = self.config.get("max_requests_per_hour", 60)
        self.respect_robots_txt = self.config.get("respect_robots_txt", True)
        self.user_agent = self.config.get(
            "user_agent",
            "SHADOWTAGAIBot/1.0 (+https://shadowtagai.ai/bot)",
        )

        # Track request history for rate limiting
        self.request_history: dict[str, list[datetime]] = {}

    def validate_robots_txt(self, url: str, source: Source) -> EthicalViolation | None:
        """Check if URL is allowed by robots.txt"""
        if not self.respect_robots_txt:
            return None

        # TODO: Implement actual robots.txt parsing
        # For now, simple placeholder
        if not source.robots_txt_checked:
            return EthicalViolation(
                violation_type=EthicalViolationType.ROBOTS_TXT,
                source=source.url,
                description="robots.txt not checked before accessing source",
                severity="medium",
                timestamp=datetime.utcnow(),
                remediation="Check and cache robots.txt before scraping",
            )

        if not source.robots_txt_compliant:
            return EthicalViolation(
                violation_type=EthicalViolationType.ROBOTS_TXT,
                source=source.url,
                description="Source disallows bot access in robots.txt",
                severity="high",
                timestamp=datetime.utcnow(),
                remediation="Skip this source or request permission",
            )

        return None

    def validate_rate_limit(self, source: Source) -> EthicalViolation | None:
        """Check if rate limit would be exceeded"""
        domain = urlparse(source.url).netloc

        # Get request history for this domain
        now = datetime.utcnow()
        if domain not in self.request_history:
            self.request_history[domain] = []

        # Clean up old requests (older than 1 hour)
        cutoff = datetime.utcnow().timestamp() - 3600
        self.request_history[domain] = [
            req for req in self.request_history[domain] if req.timestamp() > cutoff
        ]

        # Check if we're over rate limit
        requests_last_hour = len(self.request_history[domain])
        if requests_last_hour >= source.rate_limit_per_hour:
            return EthicalViolation(
                violation_type=EthicalViolationType.RATE_LIMIT,
                source=source.url,
                description=f"Rate limit exceeded: {requests_last_hour}/{source.rate_limit_per_hour} requests/hour",
                severity="high",
                timestamp=now,
                remediation="Wait before next request or reduce rate",
            )

        return None

    def validate_attribution(self, item: IngestedItem) -> EthicalViolation | None:
        """Check if proper attribution is included"""
        # Check if source URL is preserved
        if not item.metadata.get("source_url") and not item.url:
            return EthicalViolation(
                violation_type=EthicalViolationType.ATTRIBUTION,
                source=item.source.url,
                description="Missing source attribution in ingested item",
                severity="medium",
                timestamp=datetime.utcnow(),
                remediation="Add source_url to metadata",
            )

        return None

    def record_request(self, source: Source):
        """Record a request for rate limiting"""
        domain = urlparse(source.url).netloc
        if domain not in self.request_history:
            self.request_history[domain] = []
        self.request_history[domain].append(datetime.utcnow())


class TierClassifier:
    """Classifies data sources into tiers based on quality and authority

    Tier 1: High-value, authoritative sources (e.g., .gov, major news, academic)
    Tier 2: Moderate-value, verified sources (e.g., established blogs, verified accounts)
    Tier 3: Low-value, general sources (e.g., forums, user-generated content)
    """

    def __init__(self):
        # Domain patterns for Tier 1
        self.tier_1_patterns = [
            r"\.gov$",
            r"\.edu$",
            r"\.mil$",
            r"nytimes\.com$",
            r"wsj\.com$",
            r"reuters\.com$",
            r"bloomberg\.com$",
            r"nature\.com$",
            r"science\.org$",
        ]

        # Domain patterns for Tier 3 (low quality)
        self.tier_3_patterns = [
            r"reddit\.com",
            r"4chan\.org",
            r"forum",
            r"board",
        ]

    def classify(self, source: Source) -> SourceTier:
        """Classify source into tier"""
        domain = urlparse(source.url).netloc

        # Check Tier 1 patterns
        for pattern in self.tier_1_patterns:
            if re.search(pattern, domain, re.IGNORECASE):
                return SourceTier.TIER_1

        # Check Tier 3 patterns
        for pattern in self.tier_3_patterns:
            if re.search(pattern, domain, re.IGNORECASE):
                return SourceTier.TIER_3

        # Default to Tier 2
        return SourceTier.TIER_2


class GeminiIngestionLayer:
    """Intelligence collection pipeline with ethical compliance

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
    - Feeds data to Judge 6 enforcement layer
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

        # Quality gates
        self.target_items_per_day = self.config.get("target_items_per_day", 1000)
        self.target_unique_sources = self.config.get("target_unique_sources", 10)
        self.target_cost_per_item = self.config.get("target_cost_per_item", 0.10)
        self.target_relevance_score = self.config.get("target_relevance_score", 0.7)
        self.target_runtime_minutes = self.config.get("target_runtime_minutes", 45)

        # Sources registry
        self.sources: list[Source] = []

    def register_source(self, source: Source):
        """Register a data source"""
        # Classify tier if not already set
        if source.tier is None:
            source.tier = self.tier_classifier.classify(source)

        self.sources.append(source)

    def ingest(
        self,
        sources: list[Source] | None = None,
        target_items: int | None = None,
    ) -> IngestionResult:
        """Run ingestion pipeline

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

        # Process each source
        for source in sources:
            if not source.enabled:
                continue

            try:
                # Ethical compliance checks
                robots_violation = self.ethical_validator.validate_robots_txt(source.url, source)
                if robots_violation:
                    violations.append(robots_violation)
                    if robots_violation.severity in ["high", "critical"]:
                        continue  # Skip this source

                rate_violation = self.ethical_validator.validate_rate_limit(source)
                if rate_violation:
                    violations.append(rate_violation)
                    if rate_violation.severity in ["high", "critical"]:
                        continue  # Skip this source

                # Collect items from source (mock implementation)
                source_items = self._collect_from_source(source, target_items // len(sources))

                # Validate attribution for each item
                for item in source_items:
                    attribution_violation = self.ethical_validator.validate_attribution(item)
                    if attribution_violation:
                        violations.append(attribution_violation)

                items.extend(source_items)

                # Record request for rate limiting
                self.ethical_validator.record_request(source)

            except Exception as e:
                errors.append(f"Error collecting from {source.url}: {e!s}")

        # Calculate metrics
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
        """Collect items from a source (mock implementation)

        TODO: Implement actual collectors for each source type:
        - YouTube: YouTube Data API
        - Twitter: Twitter API v2
        - News: NewsAPI, RSS feeds
        - Web: BeautifulSoup, Scrapy
        """
        items = []

        for i in range(min(target_count, 50)):  # Cap at 50 for demo
            item = IngestedItem(
                item_id=f"{source.name}_{i}_{int(time.time())}",
                source=source,
                title=f"Sample item {i} from {source.name}",
                content=f"Content from {source.source_type.value}",
                url=f"{source.url}/item/{i}",
                ingested_at=datetime.utcnow(),
                relevance_score=0.7 + (i % 3) * 0.1,  # Mock score
                timeliness_score=0.8,
                completeness_score=0.9,
                cost_usd=0.05,  # Mock cost
                metadata={
                    "source_url": source.url,
                    "source_type": source.source_type.value,
                    "tier": source.tier.value,
                },
            )
            items.append(item)

        return items

    def _calculate_metrics(
        self,
        items: list[IngestedItem],
        violations: list[EthicalViolation],
        runtime_minutes: float,
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

        # Calculate averages
        total_cost = sum(item.cost_usd for item in items)
        avg_cost = total_cost / len(items) if items else 0.0
        avg_relevance = sum(item.relevance_score for item in items) / len(items)
        avg_timeliness = sum(item.timeliness_score for item in items) / len(items)
        avg_completeness = sum(item.completeness_score for item in items) / len(items)

        # Count unique sources
        unique_sources = len(set(item.source.url for item in items))

        # Calculate tier distribution
        tier_counts = {
            SourceTier.TIER_1: 0,
            SourceTier.TIER_2: 0,
            SourceTier.TIER_3: 0,
        }
        for item in items:
            tier_counts[item.source.tier] += 1

        total_items = len(items)
        tier_1_pct = (tier_counts[SourceTier.TIER_1] / total_items) * 100
        tier_2_pct = (tier_counts[SourceTier.TIER_2] / total_items) * 100
        tier_3_pct = (tier_counts[SourceTier.TIER_3] / total_items) * 100

        # Calculate source type distribution
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
                [v for v in metrics.ethical_violations if v.severity in ["high", "critical"]],
            )
            == 0,
        }

    def export_am_briefing(self, items: list[IngestedItem], format: str = "markdown") -> str:
        """Export AM (morning) briefing from ingested items

        Args:
            items: List of ingested items
            format: Output format ('markdown', 'json', 'html')

        Returns:
            Formatted briefing

        """
        if format == "markdown":
            return self._export_markdown_briefing(items)
        if format == "json":
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
        raise ValueError(f"Unsupported format: {format}")

    def _export_markdown_briefing(self, items: list[IngestedItem]) -> str:
        """Export markdown format briefing"""
        # Sort by relevance score
        sorted_items = sorted(items, key=lambda x: x.relevance_score, reverse=True)

        briefing = "# Intelligence Briefing\n\n"
        briefing += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        briefing += f"**Total Items:** {len(items)}\n\n"

        # Group by tier
        for tier in [SourceTier.TIER_1, SourceTier.TIER_2, SourceTier.TIER_3]:
            tier_items = [i for i in sorted_items if i.source.tier == tier]
            if not tier_items:
                continue

            briefing += f"## {tier.value.replace('_', ' ').title()}\n\n"
            for item in tier_items[:10]:  # Top 10 per tier
                briefing += f"### {item.title}\n"
                briefing += f"- **Source:** {item.source.name}\n"
                briefing += f"- **Relevance:** {item.relevance_score:.2f}\n"
                briefing += f"- **URL:** {item.url}\n\n"

        return briefing
