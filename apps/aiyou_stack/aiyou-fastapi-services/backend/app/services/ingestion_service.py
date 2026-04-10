"""
Ingestion layer monitoring and management service.
"""

import asyncio
import uuid
from datetime import datetime, timedelta

from app.models.ingestion import (
    AMBriefingDelivery,
    DataSource,
    DataSourceType,
    DataTier,
    EthicalComplianceCheck,
    IngestionJob,
    IngestionMetrics,
    IngestionStatus,
    MultiSourceCoverage,
    TierClassificationMetrics,
)


class IngestionService:
    """
    Service for managing ingestion operations and monitoring.
    """

    def __init__(self):
        """Initialize the ingestion service."""
        self.sources: dict[str, DataSource] = {}
        self.jobs: dict[str, IngestionJob] = {}
        self.metrics_history: list[IngestionMetrics] = []
        self.compliance_checks: list[EthicalComplianceCheck] = []
        self.briefings: list[AMBriefingDelivery] = []

    # Data Source Management

    def create_source(
        self,
        name: str,
        source_type: DataSourceType,
        tier: DataTier,
        url: str | None = None,
        rate_limit: int | None = None,
        cost_per_item: float | None = None,
        metadata: dict | None = None,
    ) -> DataSource:
        """Create a new data source."""
        source_id = str(uuid.uuid4())

        source = DataSource(
            source_id=source_id,
            name=name,
            source_type=source_type,
            tier=tier,
            url=url,
            rate_limit=rate_limit,
            cost_per_item=cost_per_item,
            metadata=metadata or {},
        )

        self.sources[source_id] = source
        return source

    def get_source(self, source_id: str) -> DataSource | None:
        """Get a data source by ID."""
        return self.sources.get(source_id)

    def list_sources(
        self,
        source_type: DataSourceType | None = None,
        tier: DataTier | None = None,
        enabled_only: bool = True,
    ) -> list[DataSource]:
        """List data sources with optional filtering."""
        sources = list(self.sources.values())

        if source_type:
            sources = [s for s in sources if s.source_type == source_type]

        if tier:
            sources = [s for s in sources if s.tier == tier]

        if enabled_only:
            sources = [s for s in sources if s.enabled]

        return sources

    def update_source(self, source_id: str, **kwargs) -> bool:
        """Update a data source."""
        source = self.sources.get(source_id)
        if not source:
            return False

        for key, value in kwargs.items():
            if hasattr(source, key):
                setattr(source, key, value)

        source.updated_at = datetime.utcnow()
        return True

    def delete_source(self, source_id: str) -> bool:
        """Delete a data source."""
        if source_id in self.sources:
            del self.sources[source_id]
            return True
        return False

    # Ingestion Job Management

    async def start_job(
        self, job_name: str, source_ids: list[str], parameters: dict | None = None
    ) -> IngestionJob:
        """Start a new ingestion job."""
        job_id = str(uuid.uuid4())

        job = IngestionJob(
            job_id=job_id,
            job_name=job_name,
            status=IngestionStatus.PENDING,
            source_ids=source_ids,
            start_time=datetime.utcnow(),
        )

        self.jobs[job_id] = job

        # Start async execution
        asyncio.create_task(self._execute_job(job_id, parameters or {}))

        return job

    async def _execute_job(self, job_id: str, parameters: dict):
        """Execute an ingestion job (simulated)."""
        job = self.jobs.get(job_id)
        if not job:
            return

        job.status = IngestionStatus.RUNNING
        job.updated_at = datetime.utcnow()

        # Simulate ingestion work
        await asyncio.sleep(2)

        # Simulate collecting items
        total_items = 0
        items_by_source = {}

        for source_id in job.source_ids:
            source = self.sources.get(source_id)
            if source:
                # Simulate collecting 50-200 items per source
                import random

                items = random.randint(50, 200)
                items_by_source[source_id] = items
                total_items += items

        # Create metrics
        runtime = (datetime.utcnow() - job.start_time).total_seconds() / 60.0

        metrics = IngestionMetrics(
            total_items=total_items,
            items_by_source=items_by_source,
            runtime_minutes=runtime,
            success_rate=0.95,
            relevance_score=0.85,
            timeliness_score=0.90,
            completeness_score=0.88,
        )

        job.items_collected = total_items
        job.metrics = metrics
        job.status = IngestionStatus.COMPLETED
        job.end_time = datetime.utcnow()
        job.runtime_minutes = runtime
        job.updated_at = datetime.utcnow()

        # Store metrics
        self.metrics_history.append(metrics)

    def get_job(self, job_id: str) -> IngestionJob | None:
        """Get an ingestion job by ID."""
        return self.jobs.get(job_id)

    def list_jobs(
        self, status: IngestionStatus | None = None, limit: int = 50
    ) -> list[IngestionJob]:
        """List ingestion jobs."""
        jobs = list(self.jobs.values())

        if status:
            jobs = [j for j in jobs if j.status == status]

        # Sort by created_at descending
        jobs.sort(key=lambda j: j.created_at, reverse=True)

        return jobs[:limit]

    # Metrics and Analysis

    def get_latest_metrics(self) -> IngestionMetrics | None:
        """Get the latest metrics."""
        if not self.metrics_history:
            return None
        return self.metrics_history[-1]

    def get_metrics_summary(self, days: int = 7) -> dict:
        """Get metrics summary for the past N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_metrics = [m for m in self.metrics_history if m.date >= cutoff]

        if not recent_metrics:
            return {
                "period_days": days,
                "total_items": 0,
                "avg_items_per_day": 0,
                "avg_cost": 0,
                "avg_runtime_minutes": 0,
            }

        total_items = sum(m.total_items for m in recent_metrics)
        avg_items = total_items / len(recent_metrics)
        avg_cost = sum(m.total_cost for m in recent_metrics) / len(recent_metrics)
        avg_runtime = sum(m.runtime_minutes for m in recent_metrics) / len(recent_metrics)

        return {
            "period_days": days,
            "total_items": total_items,
            "avg_items_per_day": avg_items,
            "avg_cost_per_day": avg_cost,
            "avg_runtime_minutes": avg_runtime,
            "success_rate": sum(m.success_rate for m in recent_metrics) / len(recent_metrics),
        }

    # Ethical Compliance

    def check_compliance(self, source_id: str) -> EthicalComplianceCheck:
        """Perform ethical compliance check for a source."""
        source = self.sources.get(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        # Simulate compliance checks
        robots_compliant = True
        rate_limit_compliant = source.rate_limit is not None
        tos_compliant = True
        transparency_score = 0.9

        violations = []
        recommendations = []

        if not rate_limit_compliant:
            violations.append("No rate limit configured")
            recommendations.append("Configure rate limiting to avoid being blocked")

        overall_compliant = len(violations) == 0

        check = EthicalComplianceCheck(
            source_id=source_id,
            robots_txt_compliant=robots_compliant,
            rate_limit_compliant=rate_limit_compliant,
            terms_of_service_compliant=tos_compliant,
            transparency_score=transparency_score,
            violations=violations,
            recommendations=recommendations,
            overall_compliant=overall_compliant,
        )

        self.compliance_checks.append(check)
        return check

    def get_compliance_summary(self) -> dict:
        """Get overall compliance summary."""
        if not self.compliance_checks:
            return {"total_checks": 0, "compliant_percentage": 0}

        compliant = sum(1 for c in self.compliance_checks if c.overall_compliant)
        return {
            "total_checks": len(self.compliance_checks),
            "compliant_count": compliant,
            "compliant_percentage": (compliant / len(self.compliance_checks)) * 100,
        }

    # Multi-Source Coverage Analysis

    def analyze_coverage(self) -> MultiSourceCoverage:
        """Analyze multi-source coverage."""
        sources = list(self.sources.values())
        active_sources = [s for s in sources if s.enabled]

        # Count by type and tier
        by_type = {}
        by_tier = {}

        for source in active_sources:
            by_type[source.source_type] = by_type.get(source.source_type, 0) + 1
            by_tier[source.tier] = by_tier.get(source.tier, 0) + 1

        # Calculate diversity score (simple metric)
        diversity_score = len(by_type) / len(DataSourceType) if len(DataSourceType) > 0 else 0

        # Calculate Tier 1 percentage
        tier_1_count = by_tier.get(DataTier.TIER_1, 0)
        tier_1_pct = (tier_1_count / len(active_sources)) * 100 if active_sources else 0

        # Identify gaps
        gaps = []
        for source_type in DataSourceType:
            if source_type not in by_type:
                gaps.append(f"No {source_type.value} sources configured")

        recommendations = []
        if tier_1_pct < 20:
            recommendations.append("Increase Tier 1 sources for higher quality data")
        if diversity_score < 0.5:
            recommendations.append("Add more diverse source types")

        return MultiSourceCoverage(
            total_sources=len(sources),
            active_sources=len(active_sources),
            sources_by_type=by_type,
            sources_by_tier=by_tier,
            coverage_diversity_score=diversity_score,
            tier_1_percentage=tier_1_pct,
            coverage_gaps=gaps,
            recommendations=recommendations,
        )

    # Tier Classification

    def get_tier_metrics(self) -> TierClassificationMetrics:
        """Get tier classification metrics."""
        sources = [s for s in self.sources.values() if s.enabled]

        tier_1 = sum(1 for s in sources if s.tier == DataTier.TIER_1)
        tier_2 = sum(1 for s in sources if s.tier == DataTier.TIER_2)
        tier_3 = sum(1 for s in sources if s.tier == DataTier.TIER_3)

        total = len(sources) if sources else 1

        return TierClassificationMetrics(
            tier_1_count=tier_1,
            tier_2_count=tier_2,
            tier_3_count=tier_3,
            tier_1_percentage=(tier_1 / total) * 100,
            tier_2_percentage=(tier_2 / total) * 100,
            tier_3_percentage=(tier_3 / total) * 100,
            avg_tier_1_relevance=0.92,
            avg_tier_2_relevance=0.75,
            avg_tier_3_relevance=0.55,
        )

    # AM Briefing

    def create_briefing(
        self, tier_1_items: int, tier_2_items: int, tier_3_items: int, relevance_score: float = 0.85
    ) -> AMBriefingDelivery:
        """Create an AM briefing delivery record."""
        briefing_id = str(uuid.uuid4())

        briefing = AMBriefingDelivery(
            briefing_id=briefing_id,
            delivery_time="06:00 AM",
            on_time=True,
            total_items=tier_1_items + tier_2_items + tier_3_items,
            tier_1_items=tier_1_items,
            tier_2_items=tier_2_items,
            tier_3_items=tier_3_items,
            relevance_score=relevance_score,
            timeliness_score=0.90,
            completeness_score=0.88,
        )

        self.briefings.append(briefing)
        return briefing

    def get_briefing_effectiveness(self, days: int = 7) -> dict:
        """Get briefing effectiveness metrics."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [b for b in self.briefings if b.delivery_date >= cutoff]

        if not recent:
            return {"count": 0}

        on_time_count = sum(1 for b in recent if b.on_time)
        avg_relevance = sum(b.relevance_score for b in recent) / len(recent)
        avg_rating = sum(b.user_rating for b in recent if b.user_rating) / max(
            1, sum(1 for b in recent if b.user_rating)
        )

        return {
            "count": len(recent),
            "on_time_percentage": (on_time_count / len(recent)) * 100,
            "avg_relevance_score": avg_relevance,
            "avg_user_rating": avg_rating,
            "avg_items_per_briefing": sum(b.total_items for b in recent) / len(recent),
        }
