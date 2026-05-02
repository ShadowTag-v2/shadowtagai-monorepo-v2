"""
Ingestion Service - Wraps Gemini Ingestion Layer for FastAPI
"""

import asyncio
import logging
from datetime import datetime
from uuid import uuid4

from pnkln.core.gemini_ingestion_layer import (
    GeminiIngestionLayer,
    IngestionResult as CoreIngestionResult,
    IngestionStatus as CoreIngestionStatus,
)
from app.models.ingestion import (
    JobResult,
    JobStatusResponse,
    JobListResponse,
    MetricsSummary,
    IngestionStatus,
    SourceType,
    SourceMetrics,
)

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service layer for managing ingestion jobs.

    Wraps the GeminiIngestionLayer from PNKLN Core Stack and provides:
    - Job lifecycle management
    - Async job execution
    - Job history tracking
    - Metrics aggregation
    """

    def __init__(self):
        """Initialize ingestion service"""
        self.ingestion_layer = GeminiIngestionLayer()
        self.jobs: dict[str, CoreIngestionResult] = {}
        self.running_jobs: dict[str, asyncio.Task] = {}
        logger.info("Ingestion Service initialized")

    def _convert_status(self, core_status: CoreIngestionStatus) -> IngestionStatus:
        """Convert core status to API status"""
        mapping = {
            CoreIngestionStatus.PENDING: IngestionStatus.PENDING,
            CoreIngestionStatus.RUNNING: IngestionStatus.RUNNING,
            CoreIngestionStatus.COMPLETED: IngestionStatus.COMPLETED,
            CoreIngestionStatus.FAILED: IngestionStatus.FAILED,
            CoreIngestionStatus.PARTIAL_SUCCESS: IngestionStatus.PARTIAL_SUCCESS,
        }
        return mapping.get(core_status, IngestionStatus.FAILED)

    def _convert_result_to_job_result(self, result: CoreIngestionResult) -> JobResult:
        """Convert core IngestionResult to API JobResult"""
        # Convert source metrics
        source_metrics = {}
        for source_type, metrics in result.source_metrics.items():
            source_metrics[source_type] = SourceMetrics(
                source_type=SourceType(source_type.value),
                items_ingested=metrics.items_ingested,
                items_tier_1=metrics.items_tier_1,
                items_tier_2=metrics.items_tier_2,
                items_tier_3=metrics.items_tier_3,
                avg_relevance_score=metrics.avg_relevance_score,
                total_cost_usd=metrics.total_cost_usd,
                errors=metrics.errors,
                last_successful_fetch=metrics.last_successful_fetch,
                tier_1_ratio=metrics.tier_1_ratio,
                cost_per_item=metrics.cost_per_item,
            )

        return JobResult(
            job_id=result.job_id,
            status=self._convert_status(result.status),
            runtime_minutes=result.runtime_minutes,
            total_items=result.total_items,
            active_sources_count=result.active_sources_count,
            tier_1_ratio=result.tier_1_ratio,
            avg_cost_per_item=result.avg_cost_per_item,
            total_cost_usd=result.total_cost_usd,
            quality_gates_passed=result.quality_gates_passed,
            am_briefing_delivered=result.am_briefing_delivered,
            errors=result.errors,
            timestamp=result.timestamp,
            source_metrics=source_metrics,
        )

    async def _run_job_async(self, job_id: str, max_items_per_source: int) -> CoreIngestionResult:
        """Run ingestion job asynchronously"""
        try:
            logger.info(f"Starting job {job_id}")
            result = await self.ingestion_layer.run_nightly_job(job_id=job_id, max_items_per_source=max_items_per_source)
            self.jobs[job_id] = result
            logger.info(f"Job {job_id} completed with status: {result.status}")
            return result
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            raise
        finally:
            # Remove from running jobs
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

    def start_job(self, max_items_per_source: int = 500) -> str:
        """
        Start a new ingestion job.

        Args:
            max_items_per_source: Max items to collect per source

        Returns:
            Job ID
        """
        job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"

        # Create async task
        task = asyncio.create_task(self._run_job_async(job_id, max_items_per_source))
        self.running_jobs[job_id] = task

        logger.info(f"Started job {job_id} with max_items={max_items_per_source}")
        return job_id

    def get_job_status(self, job_id: str) -> JobStatusResponse | None:
        """
        Get status of a specific job.

        Args:
            job_id: Job identifier

        Returns:
            Job status or None if not found
        """
        # Check if job is running
        if job_id in self.running_jobs:
            task = self.running_jobs[job_id]
            if task.done():
                try:
                    result = task.result()
                    return JobStatusResponse(
                        job_id=job_id,
                        status=self._convert_status(result.status),
                        started_at=result.timestamp,
                        runtime_minutes=result.runtime_minutes,
                        progress_pct=100.0,
                        message=f"Completed: {result.total_items} items collected",
                    )
                except Exception as e:
                    return JobStatusResponse(job_id=job_id, status=IngestionStatus.FAILED, started_at=datetime.utcnow(), message=f"Failed: {str(e)}")
            else:
                return JobStatusResponse(
                    job_id=job_id, status=IngestionStatus.RUNNING, started_at=datetime.utcnow(), progress_pct=None, message="Job is running..."
                )

        # Check completed jobs
        if job_id in self.jobs:
            result = self.jobs[job_id]
            return JobStatusResponse(
                job_id=job_id,
                status=self._convert_status(result.status),
                started_at=result.timestamp,
                runtime_minutes=result.runtime_minutes,
                progress_pct=100.0,
                message=f"Completed: {result.total_items} items collected",
            )

        return None

    def get_job_result(self, job_id: str) -> JobResult | None:
        """
        Get full result of a completed job.

        Args:
            job_id: Job identifier

        Returns:
            Job result or None if not found/completed
        """
        if job_id in self.jobs:
            return self._convert_result_to_job_result(self.jobs[job_id])

        # Check if still running
        if job_id in self.running_jobs:
            task = self.running_jobs[job_id]
            if task.done():
                try:
                    result = task.result()
                    return self._convert_result_to_job_result(result)
                except Exception:
                    return None

        return None

    def list_jobs(self, page: int = 1, page_size: int = 10) -> JobListResponse:
        """
        List recent jobs with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Paginated job list
        """
        # Combine running and completed jobs
        all_job_ids = list(self.running_jobs.keys()) + list(self.jobs.keys())
        all_job_ids = sorted(set(all_job_ids), reverse=True)  # Most recent first

        # Paginate
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_ids = all_job_ids[start_idx:end_idx]

        # Get status for each job
        jobs_status = []
        for job_id in paginated_ids:
            status = self.get_job_status(job_id)
            if status:
                jobs_status.append(status)

        return JobListResponse(jobs=jobs_status, total=len(all_job_ids), page=page, page_size=page_size)

    def get_metrics_summary(self) -> MetricsSummary:
        """
        Get aggregated metrics across all jobs.

        Returns:
            Metrics summary
        """
        completed_jobs = list(self.jobs.values())

        if not completed_jobs:
            return MetricsSummary(
                total_jobs=0,
                successful_jobs=0,
                failed_jobs=0,
                avg_runtime_minutes=0.0,
                avg_items_per_job=0,
                avg_tier_1_ratio=0.0,
                avg_cost_per_job=0.0,
                last_job_timestamp=None,
            )

        successful = [j for j in completed_jobs if j.status == CoreIngestionStatus.COMPLETED]
        failed = [j for j in completed_jobs if j.status == CoreIngestionStatus.FAILED]

        return MetricsSummary(
            total_jobs=len(completed_jobs),
            successful_jobs=len(successful),
            failed_jobs=len(failed),
            avg_runtime_minutes=sum(j.runtime_minutes for j in completed_jobs) / len(completed_jobs),
            avg_items_per_job=int(sum(j.total_items for j in completed_jobs) / len(completed_jobs)),
            avg_tier_1_ratio=sum(j.tier_1_ratio for j in completed_jobs) / len(completed_jobs),
            avg_cost_per_job=sum(j.total_cost_usd for j in completed_jobs) / len(completed_jobs),
            last_job_timestamp=max(j.timestamp for j in completed_jobs) if completed_jobs else None,
        )


# Singleton instance
_ingestion_service: IngestionService | None = None


def get_ingestion_service() -> IngestionService:
    """Get singleton ingestion service instance"""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service
