"""Gemini Ingestion Layer API Endpoints"""

import logging

from fastapi import APIRouter, HTTPException, Path, Query

from app.models.ingestion import (
    JobListResponse,
    JobResult,
    JobStartRequest,
    JobStatusResponse,
    MetricsSummary,
)
from app.services.ingestion_service import get_ingestion_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingestion", tags=["Intelligence Ingestion"])


@router.post("/jobs", response_model=dict, status_code=202)
async def start_ingestion_job(request: JobStartRequest):
    """Start a new intelligence ingestion job.

    This endpoint initiates a nightly batch intelligence collection job that:
    - Collects from 8+ intelligence sources (YouTube, Twitter, News, etc.)
    - Runs for ~45 minutes (target runtime)
    - Collects 1000-5000 high-quality items
    - Costs ~$77/month at 5K items/day
    - Validates quality gates (Tier 1 ratio ≥40%, cost/item ≤$0.02)

    **Returns:**
    - 202 Accepted with job_id for tracking
    - Job runs asynchronously in background

    **Usage:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/ingestion/jobs" \\
      -H "Content-Type: application/json" \\
      -d '{"max_items_per_source": 500}'
    ```
    """
    service = get_ingestion_service()

    try:
        job_id = service.start_job(max_items_per_source=request.max_items_per_source)

        logger.info(f"Ingestion job started: {job_id}")

        return {
            "job_id": job_id,
            "status": "accepted",
            "message": "Ingestion job started (runtime ~45 min)",
            "check_status_at": f"/api/v1/ingestion/jobs/{job_id}",
        }

    except Exception as e:
        logger.error(f"Failed to start ingestion job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start job: {e!s}")


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str = Path(..., description="Job identifier")):
    """Get status of a specific ingestion job.

    **Returns:**
    - Job status (pending, running, completed, failed)
    - Runtime information
    - Progress percentage (if available)

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ingestion/jobs/job_20251117_123456/status"
    ```
    """
    service = get_ingestion_service()
    status = service.get_job_status(job_id)

    if not status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return status


@router.get("/jobs/{job_id}", response_model=JobResult)
async def get_job_result(job_id: str = Path(..., description="Job identifier")):
    """Get full result of a completed ingestion job.

    **Returns:**
    - Complete job metrics
    - Per-source breakdown
    - Quality gate results
    - Cost analysis
    - Tier 1/2/3 distribution

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ingestion/jobs/job_20251117_123456"
    ```
    """
    service = get_ingestion_service()
    result = service.get_job_result(job_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found or not yet completed")

    return result


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """List recent ingestion jobs with pagination.

    **Returns:**
    - Paginated list of jobs (most recent first)
    - Total job count
    - Page information

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ingestion/jobs?page=1&page_size=10"
    ```
    """
    service = get_ingestion_service()
    return service.list_jobs(page=page, page_size=page_size)


@router.get("/metrics", response_model=MetricsSummary)
async def get_metrics_summary():
    """Get aggregated metrics across all ingestion jobs.

    **Returns:**
    - Total/successful/failed job counts
    - Average runtime, items per job
    - Average Tier 1 ratio (target ≥40%)
    - Average cost per job
    - Last job timestamp

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ingestion/metrics"
    ```

    **Key Metrics:**
    - `avg_tier_1_ratio`: Should be ≥0.40 (40% high-value intelligence)
    - `avg_cost_per_job`: Target ~$77/month = ~$2.50/day for 5K items
    - `avg_runtime_minutes`: Target ≤45 minutes
    """
    service = get_ingestion_service()
    return service.get_metrics_summary()


@router.get("/health", response_model=dict)
async def ingestion_health_check():
    """Health check for ingestion service.

    **Returns:**
    - Service status
    - Active job count
    - Total completed jobs

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/ingestion/health"
    ```
    """
    service = get_ingestion_service()

    return {
        "status": "healthy",
        "service": "gemini_ingestion_layer",
        "active_jobs": len(service.running_jobs),
        "completed_jobs": len(service.jobs),
        "total_jobs": len(service.running_jobs) + len(service.jobs),
    }
