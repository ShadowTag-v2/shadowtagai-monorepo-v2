"""Gemini Ingestion Layer V2 - Production Ready
Replaces mock collectors with real API integrations

CRITICAL GAPS FIXED:
1. ✅ Real API collectors (YouTube, Twitter, News, Academic, Reddit)
2. ✅ robots.txt parser integration
3. ✅ Redis rate limiting (with in-memory fallback)
4. ✅ Ethical compliance validation

Production-ready for deployment.
"""

import time
from datetime import datetime
from typing import Any

# Import real collectors
from ..collectors import (
    AcademicCollector,
    NewsCollector,
    RedditCollector,
    TwitterCollector,
    YouTubeCollector,
)
from ..utils.rate_limiter import InMemoryRateLimiter, RedisRateLimiter

# Import utilities
from ..utils.robots_parser import RobotsParser

# Import from original module
from .gemini_ingestion import (
    EthicalViolation,
    EthicalViolationType,
    IngestedItem,
    IngestionMetrics,
    IngestionResult,
    Source,
    SourceTier,
    SourceType,
    TierClassifier,
)


class ProductionEthicalValidator:
    """Production-ready ethical compliance validator with real implementations"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.user_agent = self.config.get("user_agent", "PNKLNBot/1.0 (+https://pnkln.ai/bot)")

        # Initialize robots.txt parser
        self.robots_parser = RobotsParser(user_agent=self.user_agent)

        # Initialize rate limiter
        redis_url = self.config.get("redis_url")
        if redis_url:
            try:
                self.rate_limiter = RedisRateLimiter(
                    redis_url=redis_url,
                    default_limit=60,
                    default_window=3600,
                )
                print(f"✅ Using Redis rate limiter at {redis_url}")
            except Exception as e:
                print(f"⚠️ Redis unavailable ({e}), using in-memory fallback")
                self.rate_limiter = InMemoryRateLimiter(default_limit=60, default_window=3600)
        else:
            self.rate_limiter = InMemoryRateLimiter(default_limit=60, default_window=3600)

    def validate_robots_txt(self, url: str, source: Source) -> EthicalViolation | None:
        """Real robots.txt validation"""
        is_allowed = self.robots_parser.is_allowed(url)

        source.robots_txt_checked = True
        source.robots_txt_compliant = is_allowed

        if not is_allowed:
            return EthicalViolation(
                violation_type=EthicalViolationType.ROBOTS_TXT,
                source=source.url,
                description="robots.txt disallows bot access",
                severity="high",
                timestamp=datetime.utcnow(),
                remediation="Skip source or request permission",
            )
        return None

    def validate_rate_limit(self, source: Source) -> EthicalViolation | None:
        """Real rate limiting with persistence"""
        from urllib.parse import urlparse

        domain = urlparse(source.url).netloc
        rate_key = f"rate_limit:{domain}"

        is_allowed = self.rate_limiter.is_allowed(
            key=rate_key,
            limit=source.rate_limit_per_hour,
            window=3600,
        )

        if not is_allowed:
            return EthicalViolation(
                violation_type=EthicalViolationType.RATE_LIMIT,
                source=source.url,
                description=f"Rate limit exceeded: {source.rate_limit_per_hour}/hour",
                severity="high",
                timestamp=datetime.utcnow(),
                remediation="Wait before next request",
            )
        return None

    def validate_attribution(self, item: IngestedItem) -> EthicalViolation | None:
        """Validate attribution"""
        if not item.metadata.get("source_url") and not item.url:
            return EthicalViolation(
                violation_type=EthicalViolationType.ATTRIBUTION,
                source=item.source.url,
                description="Missing source attribution",
                severity="medium",
                timestamp=datetime.utcnow(),
                remediation="Add source_url to metadata",
            )
        return None

    def record_request(self, source: Source):
        """Record request for rate limiting"""
        from urllib.parse import urlparse

        domain = urlparse(source.url).netloc
        self.rate_limiter.record_request(f"rate_limit:{domain}")


class ProductionIngestionLayer:
    """Production-Ready Gemini Ingestion Layer

    Replaces all mock implementations with real API integrations
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.ethical_validator = ProductionEthicalValidator(config)
        self.tier_classifier = TierClassifier()

        # Quality gates
        self.target_items_per_day = self.config.get("target_items_per_day", 1000)
        self.target_unique_sources = self.config.get("target_unique_sources", 10)
        self.target_cost_per_item = self.config.get("target_cost_per_item", 0.10)
        self.target_relevance_score = self.config.get("target_relevance_score", 0.7)
        self.target_runtime_minutes = self.config.get("target_runtime_minutes", 45)

        # Collectors registry
        self.collectors = {}
        self._init_collectors()

        # Sources registry
        self.sources: list[Source] = []

    def _init_collectors(self):
        """Initialize real API collectors"""
        api_keys = self.config.get("api_keys", {})

        # YouTube collector
        if api_keys.get("youtube"):
            self.collectors[SourceType.YOUTUBE] = YouTubeCollector(
                api_key=api_keys["youtube"],
                config=self.config.get("youtube", {}),
            )
            print("✅ YouTube collector initialized")

        # Twitter collector
        if api_keys.get("twitter"):
            self.collectors[SourceType.TWITTER] = TwitterCollector(
                api_key=api_keys["twitter"],
                config=self.config.get("twitter", {}),
            )
            print("✅ Twitter collector initialized")

        # News collector
        if api_keys.get("news"):
            self.collectors[SourceType.NEWS] = NewsCollector(
                api_key=api_keys["news"],
                config=self.config.get("news", {}),
            )
            print("✅ News collector initialized")

        # Academic collector (arXiv - no key needed)
        self.collectors[SourceType.ACADEMIC] = AcademicCollector(
            config=self.config.get("academic", {}),
        )
        print("✅ Academic collector initialized")

        # Reddit collector
        reddit_config = self.config.get("reddit", {})
        if reddit_config.get("client_id") and reddit_config.get("client_secret"):
            self.collectors[SourceType.API] = RedditCollector(
                config=reddit_config,
            )  # Reddit uses API type
            print("✅ Reddit collector initialized")

    def register_source(self, source: Source):
        """Register a source"""
        if source.tier is None:
            source.tier = self.tier_classifier.classify(source)
        self.sources.append(source)

    def ingest(
        self,
        sources: list[Source] | None = None,
        target_items: int | None = None,
    ) -> IngestionResult:
        """Run production ingestion pipeline"""
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
                # Ethical checks
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

                # Use real collector
                collector = self.collectors.get(source.source_type)
                if collector:
                    source_items = collector.collect(source, target_items // len(sources))
                else:
                    errors.append(f"No collector for {source.source_type.value}")
                    continue

                # Validate attribution
                for item in source_items:
                    attr_violation = self.ethical_validator.validate_attribution(item)
                    if attr_violation:
                        violations.append(attr_violation)

                items.extend(source_items)
                self.ethical_validator.record_request(source)

            except Exception as e:
                errors.append(f"Error from {source.url}: {e!s}")

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

    def _calculate_metrics(
        self,
        items: list[IngestedItem],
        violations: list[EthicalViolation],
        runtime_minutes: float,
    ) -> IngestionMetrics:
        """Calculate metrics"""
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
        avg_cost = total_cost / len(items)
        avg_relevance = sum(item.relevance_score for item in items) / len(items)
        avg_timeliness = sum(item.timeliness_score for item in items) / len(items)
        avg_completeness = sum(item.completeness_score for item in items) / len(items)

        unique_sources = len(set(item.source.url for item in items))

        tier_counts = {SourceTier.TIER_1: 0, SourceTier.TIER_2: 0, SourceTier.TIER_3: 0}
        for item in items:
            tier_counts[item.source.tier] += 1

        total = len(items)
        tier_1_pct = (tier_counts[SourceTier.TIER_1] / total) * 100
        tier_2_pct = (tier_counts[SourceTier.TIER_2] / total) * 100
        tier_3_pct = (tier_counts[SourceTier.TIER_3] / total) * 100

        source_type_dist: dict[SourceType, int] = {}
        for item in items:
            st = item.source.source_type
            source_type_dist[st] = source_type_dist.get(st, 0) + 1

        return IngestionMetrics(
            items_per_day=total,
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
