"""FastAPI routes for ingestion layer management and monitoring."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.ingestion import (
    CoverageAnalysisResponse,
    CreateDataSourceRequest,
    DataSource,
    DataSourceType,
    DataTier,
    IngestionJob,
    IngestionJobStatusResponse,
    IngestionMetrics,
    IngestionStatus,
    StartIngestionJobRequest,
    TierClassificationMetrics,
)
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


# Dependency to get ingestion service
def get_ingestion_service() -> IngestionService:
    """Get the ingestion service instance."""
    return None


# Data Source Endpoints


@router.post("/sources", response_model=DataSource)
async def create_source(
    request: CreateDataSourceRequest,
    service: IngestionService = Depends(get_ingestion_service),
):
    """Create a new data source."""
    try:
        source = service.create_source(
            name=request.name,
            source_type=request.source_type,
            tier=request.tier,
            url=request.url,
            rate_limit=request.rate_limit,
            cost_per_item=request.cost_per_item,
            metadata=request.metadata,
        )
        return source
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create source: {e!s}") from e


@router.get("/sources", response_model=list[DataSource])
async def list_sources(
    source_type: DataSourceType | None = Query(None),
    tier: DataTier | None = Query(None),
    enabled_only: bool = Query(True),
    service: IngestionService = Depends(get_ingestion_service),
):
    """List data sources with optional filtering."""
    return service.list_sources(source_type=source_type, tier=tier, enabled_only=enabled_only)


@router.get("/sources/{source_id}", response_model=DataSource)
async def get_source(source_id: str, service: IngestionService = Depends(get_ingestion_service)):
    """Get a specific data source."""
    source = service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {source_id} not found")
    return source


@router.delete("/sources/{source_id}")
async def delete_source(source_id: str, service: IngestionService = Depends(get_ingestion_service)):
    """Delete a data source."""
    success = service.delete_source(source_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Source {source_id} not found")
    return {"message": "Source deleted successfully"}


# Ingestion Job Endpoints


@router.post("/jobs/start", response_model=IngestionJobStatusResponse)
async def start_job(
    request: StartIngestionJobRequest,
    service: IngestionService = Depends(get_ingestion_service),
):
    """Start a new ingestion job."""
    try:
        job = await service.start_job(
            job_name=request.job_name,
            source_ids=request.source_ids,
            parameters=request.parameters,
        )
        return IngestionJobStatusResponse(job=job, message=f"Job {job.job_id} started successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start job: {e!s}") from e


@router.get("/jobs/{job_id}", response_model=IngestionJobStatusResponse)
async def get_job_status(job_id: str, service: IngestionService = Depends(get_ingestion_service)):
    """Get the status of an ingestion job."""
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return IngestionJobStatusResponse(job=job, message=f"Job status: {job.status.value}")


@router.get("/jobs", response_model=list[IngestionJob])
async def list_jobs(
    status: IngestionStatus | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    service: IngestionService = Depends(get_ingestion_service),
):
    """List ingestion jobs with optional filtering."""
    return service.list_jobs(status=status, limit=limit)


# Metrics Endpoints


@router.get("/metrics/latest", response_model=Optional[IngestionMetrics])  # noqa: UP045
async def get_latest_metrics(service: IngestionService = Depends(get_ingestion_service)):
    """Get the latest ingestion metrics."""
    return service.get_latest_metrics()


@router.get("/metrics/summary")
async def get_metrics_summary(
    days: int = Query(7, ge=1, le=90),
    service: IngestionService = Depends(get_ingestion_service),
):
    """Get metrics summary for the past N days."""
    return service.get_metrics_summary(days=days)


# Coverage Analysis


@router.get("/coverage/analyze", response_model=CoverageAnalysisResponse)
async def analyze_coverage(service: IngestionService = Depends(get_ingestion_service)):
    """Analyze multi-source coverage."""
    coverage = service.analyze_coverage()
    return CoverageAnalysisResponse(coverage=coverage, recommendations=coverage.recommendations)


# Tier Classification


@router.get("/tiers/metrics", response_model=TierClassificationMetrics)
async def get_tier_metrics(service: IngestionService = Depends(get_ingestion_service)):
    """Get tier classification metrics."""
    return service.get_tier_metrics()


# Ethical Compliance


@router.get("/compliance/check/{source_id}")
async def check_source_compliance(
    source_id: str,
    service: IngestionService = Depends(get_ingestion_service),
):
    """Perform ethical compliance check for a source."""
    try:
        check = service.check_compliance(source_id)
        return check
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/compliance/summary")
async def get_compliance_summary(service: IngestionService = Depends(get_ingestion_service)):
    """Get overall compliance summary."""
    return service.get_compliance_summary()


# AM Briefing


@router.get("/briefings/effectiveness")
async def get_briefing_effectiveness(
    days: int = Query(7, ge=1, le=90),
    service: IngestionService = Depends(get_ingestion_service),
):
    """Get AM briefing effectiveness metrics."""
    return service.get_briefing_effectiveness(days=days)
