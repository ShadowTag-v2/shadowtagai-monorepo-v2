"""
Gemini Ingestion Layer API
FastAPI endpoints for the PNKLN intelligence collection pipeline.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any

import structlog
from fastapi import BackgroundTasks, FastAPI, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ingestion.sources.fourchan_adapter import FourChanAdapter
from ingestion.sources.news_adapter import NewsAdapter
from ingestion.sources.reddit_adapter import RedditAdapter
from ingestion.storage.sqlite_store import IngestStore

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Gemini Ingestion Layer API",
    description="PNKLN Core Stack™ Intelligence Collection Pipeline",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Shared state ──────────────────────────────────────────────────────────────
_store: IngestStore | None = None


def get_store() -> IngestStore:
    global _store
    if _store is None:
        _store = IngestStore()
    return _store


# ── Models ────────────────────────────────────────────────────────────────────


class TierLevel(StrEnum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class SourceType(StrEnum):
    REDDIT = "reddit"
    FOURCHAN = "fourchan"
    NEWS = "news"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    DARKWEB = "darkweb"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestedItemOut(BaseModel):
    id: str
    source: str
    title: str
    content: str | None
    url: str
    published_at: str | None
    author: str | None
    tier: int
    ingested_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    start_time: str | None = None
    end_time: str | None = None
    runtime_minutes: float | None = None
    items_collected: int = 0
    items_by_tier: dict[str, int] = Field(default_factory=dict)
    sources_active: int = 0
    errors: list[str] = Field(default_factory=list)


class TriggerRequest(BaseModel):
    reason: str = Field(default="manual", description="Reason for manual trigger")
    sources: list[SourceType] = Field(
        default=[SourceType.REDDIT, SourceType.NEWS],
        description="Sources to ingest from",
    )
    limit_per_source: int = Field(default=25, ge=1, le=200)


class MetricsResponse(BaseModel):
    total_items: int
    items_by_tier: dict[str, int]
    sources: list[str]
    last_job_id: str | None
    last_job_status: str | None


# ── Background ingest task ────────────────────────────────────────────────────

FREE_ADAPTERS = {
    SourceType.REDDIT: lambda limit: RedditAdapter(limit=limit),
    SourceType.FOURCHAN: lambda limit: FourChanAdapter(),
}


async def _run_ingest(job_id: str, sources: list[SourceType], limit: int) -> None:
    store = get_store()
    errors: list[str] = []
    total = 0
    active = 0

    try:
        for src in sources:
            if src not in FREE_ADAPTERS:
                logger.warning("ingest_source_skipped", src=src, reason="requires credentials")
                errors.append(f"{src}: skipped (credentials not available)")
                continue

            adapter = FREE_ADAPTERS[src](limit)
            active += 1
            count = 0

            try:
                if hasattr(adapter, "authenticate"):
                    await adapter.authenticate()
                async for item in adapter.fetch_items():
                    store.save_item(item)
                    count += 1
                logger.info("ingest_source_done", src=src, count=count)
            except Exception as e:
                logger.error("ingest_source_failed", src=src, error=str(e))
                errors.append(f"{src}: {e}")
            finally:
                total += count

        store.complete_job(job_id, total, active, errors)
        logger.info("ingest_job_completed", job_id=job_id, total=total)
    except Exception as e:
        store.fail_job(job_id, str(e))
        logger.error("ingest_job_failed", job_id=job_id, error=str(e))


# ── News adapter needs its own async loop path ────────────────────────────────


async def _run_news_ingest(job_id: str, limit: int) -> None:
    store = get_store()
    errors: list[str] = []
    count = 0
    try:
        adapter = NewsAdapter()
        async for item in adapter.fetch_items(max_items=limit):
            store.save_item(item)
            count += 1
        store.complete_job(job_id, count, 1, errors)
        logger.info("news_ingest_done", job_id=job_id, count=count)
    except Exception as e:
        store.fail_job(job_id, str(e))
        logger.error("news_ingest_failed", job_id=job_id, error=str(e))


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/", tags=["Health"])
async def root():
    return {"service": "Gemini Ingestion Layer API", "version": "2.0.0", "status": "operational"}


@app.get("/health", tags=["Health"])
async def health_check():
    store = get_store()
    counts = store.count_items()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "store": {"total_items": counts.get("total", 0)},
    }


@app.post(
    "/ingestion/trigger",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Ingestion"],
)
async def trigger_ingestion(request: TriggerRequest, background_tasks: BackgroundTasks):
    """Kick off a real ingest run against the requested sources."""
    store = get_store()
    job_id = f"manual-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    store.create_job(job_id)

    # Separate news (uses different adapter interface) from free adapters
    free_srcs = [s for s in request.sources if s != SourceType.NEWS]
    if free_srcs:
        background_tasks.add_task(_run_ingest, job_id, free_srcs, request.limit_per_source)
    elif SourceType.NEWS in request.sources:
        background_tasks.add_task(_run_news_ingest, job_id, request.limit_per_source)

    logger.info("ingest_triggered", job_id=job_id, sources=request.sources, reason=request.reason)

    return JobStatusResponse(job_id=job_id, status=JobStatus.RUNNING)


@app.get("/ingestion/status", response_model=JobStatusResponse, tags=["Ingestion"])
async def get_ingestion_status(
    job_id: str | None = Query(None, description="Job ID (omit for latest)"),
):
    """Return real job status from SQLite."""
    store = get_store()
    job = store.get_job(job_id) if job_id else store.latest_job()

    if not job:
        return JobStatusResponse(
            job_id=job_id or "none",
            status=JobStatus.PENDING,
            errors=["No jobs found — trigger one first via POST /ingestion/trigger"],
        )

    start = datetime.fromisoformat(job["start_time"]) if job.get("start_time") else None
    end = datetime.fromisoformat(job["end_time"]) if job.get("end_time") else None
    runtime = round((end - start).total_seconds() / 60, 2) if start and end else None

    counts = store.count_items()

    return JobStatusResponse(
        job_id=job["job_id"],
        status=JobStatus(job["status"]),
        start_time=job.get("start_time"),
        end_time=job.get("end_time"),
        runtime_minutes=runtime,
        items_collected=job.get("items_collected", 0),
        items_by_tier={k: v for k, v in counts.items() if k != "total"},
        sources_active=job.get("sources_active", 0),
        errors=job.get("errors", []),
    )


@app.get("/ingestion/items", response_model=list[IngestedItemOut], tags=["Ingestion"])
async def get_ingested_items(
    tier: int | None = Query(None, ge=1, le=3, description="Filter by tier (1/2/3)"),
    source: str | None = Query(None, description="Filter by source prefix (e.g. 'reddit')"),
    since: datetime | None = Query(
        None, description="Only items ingested after this UTC timestamp"
    ),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Query real ingested items from SQLite."""
    import json

    store = get_store()
    rows = store.query_items(tier=tier, source=source, since=since, limit=limit, offset=offset)

    return [
        IngestedItemOut(
            id=r["id"],
            source=r["source"],
            title=r["title"] or "",
            content=r["content"],
            url=r["url"] or "",
            published_at=r["published_at"],
            author=r["author"],
            tier=r["tier"],
            ingested_at=r["ingested_at"],
            metadata=json.loads(r["metadata"] or "{}"),
        )
        for r in rows
    ]


@app.get("/ingestion/metrics", response_model=MetricsResponse, tags=["Metrics"])
async def get_metrics():
    """Live metrics from SQLite."""
    store = get_store()
    counts = store.count_items()
    job = store.latest_job()

    sources_row = store._conn.execute(
        "SELECT DISTINCT source FROM items ORDER BY source"
    ).fetchall()

    return MetricsResponse(
        total_items=counts.get("total", 0),
        items_by_tier={k: v for k, v in counts.items() if k != "total"},
        sources=[r[0] for r in sources_row],
        last_job_id=job["job_id"] if job else None,
        last_job_status=job["status"] if job else None,
    )


# ── Error handler ─────────────────────────────────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("unhandled_exception", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc), "timestamp": datetime.utcnow().isoformat()},
    )


# ── Startup ───────────────────────────────────────────────────────────────────


@app.on_event("startup")
async def startup_event():
    get_store()  # init SQLite
    logger.info("ingestion_api_started", version="2.0.0")


@app.on_event("shutdown")
async def shutdown_event():
    if _store:
        _store.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ingestion:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
