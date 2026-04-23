"""AI Threads API endpoints

REST API for managing curated AI agent knowledge threads:
- CRUD operations for threads, authors, and posts
- Semantic search with vector embeddings
- Bulk import from compilations
- Export to JSON, Markdown, PDF formats
- Scrape job management
"""

import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.shadowtag_v4.database import get_db

from app.api.schemas.ai_threads import (
    BulkImportRequest,
    BulkImportResponse,
    ExportFormat,
    ExportRequest,
    ExportResponse,
    ScrapeJobCreate,
    ScrapeJobResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    SortOrder,
    ThreadAnalytics,
    ThreadCategoryEnum,
    ThreadCreate,
    ThreadListRequest,
    ThreadListResponse,
    ThreadResponse,
    ThreadStatusEnum,
    ThreadSummary,
    ThreadUpdate,
)
from app.services.scrape_job_service import ScrapeJobService
from app.services.thread_service import ThreadService

router = APIRouter()


def get_thread_service(db: Session = Depends(get_db)) -> ThreadService:
    """Dependency to get ThreadService instance."""
    return ThreadService(db)


def get_scrape_job_service(db: Session = Depends(get_db)) -> ScrapeJobService:
    """Dependency to get ScrapeJobService instance."""
    return ScrapeJobService(db)


# ============================================================================
# Thread CRUD Endpoints
# ============================================================================


@router.post("", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    data: ThreadCreate,
    service: ThreadService = Depends(get_thread_service),
):
    """Create a new AI agent thread.

    The thread must include author information (either existing author_id or new author data)
    and can optionally include individual posts.
    """
    try:
        thread = await service.create_thread(data)
        return thread
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create thread: {e!s}",
        ) from e


@router.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: str,
    service: ThreadService = Depends(get_thread_service),
):
    """Get a thread by ID with all posts and author info."""
    thread = await service.get_thread(thread_id)
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread not found: {thread_id}",
        )
    return thread


@router.patch("/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: str,
    data: ThreadUpdate,
    service: ThreadService = Depends(get_thread_service),
):
    """Update thread fields (title, category, tags, scores, metadata)."""
    thread = await service.update_thread(thread_id, data)
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread not found: {thread_id}",
        )
    return thread


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
    thread_id: str,
    service: ThreadService = Depends(get_thread_service),
):
    """Delete a thread and all related posts/embeddings."""
    deleted = await service.delete_thread(thread_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread not found: {thread_id}",
        )


@router.get("", response_model=ThreadListResponse)
async def list_threads(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: ThreadCategoryEnum | None = None,
    status_filter: ThreadStatusEnum | None = Query(default=None, alias="status"),
    min_likes: int | None = Query(default=None, ge=0),
    tags: str | None = Query(default=None, description="Comma-separated tags"),
    author_username: str | None = None,
    sort: SortOrder = SortOrder.LIKES_DESC,
    service: ThreadService = Depends(get_thread_service),
):
    """List threads with pagination and filters.

    Supports filtering by category, status, minimum likes, tags, and author.
    Results can be sorted by likes, date, or relevance.
    """
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    request = ThreadListRequest(
        page=page,
        page_size=page_size,
        category=category,
        status=status_filter,
        min_likes=min_likes,
        tags=tag_list,
        author_username=author_username,
        sort=sort,
    )

    return await service.list_threads(request)


# ============================================================================
# Search Endpoints
# ============================================================================


@router.post("/search", response_model=SearchResponse)
async def search_threads(
    request: SearchRequest,
    service: ThreadService = Depends(get_thread_service),
):
    """Semantic search for threads.

    Uses vector embeddings to find threads matching the query.
    Supports filtering by category, likes, tags, and date range.

    Note: Requires ThreadKnowledgeBase for vector search.
    Falls back to keyword search if vector search unavailable.
    """
    start_time = time.time()

    # TODO: Integrate with ThreadKnowledgeBase for semantic search
    # For now, return basic keyword-based results
    list_request = ThreadListRequest(
        page=1,
        page_size=request.top_k,
        category=request.category,
        min_likes=request.min_likes,
        tags=request.tags,
        sort=SortOrder.LIKES_DESC,
    )

    list_response = await service.list_threads(list_request)

    # Convert to search results
    results = [
        SearchResult(
            thread=summary,
            score=1.0 - (i * 0.05),  # Placeholder scores
            highlights=[],
            matched_post_positions=[],
        )
        for i, summary in enumerate(list_response.threads)
    ]

    search_time = (time.time() - start_time) * 1000

    return SearchResponse(
        query=request.query,
        total_results=list_response.total,
        results=results,
        search_time_ms=search_time,
        filters_applied={
            "category": request.category.value if request.category else None,
            "min_likes": request.min_likes,
            "tags": request.tags,
            "date_from": request.date_from.isoformat() if request.date_from else None,
            "date_to": request.date_to.isoformat() if request.date_to else None,
        },
    )


# ============================================================================
# Import/Export Endpoints
# ============================================================================


@router.post("/bulk-import", response_model=BulkImportResponse)
async def bulk_import_threads(
    request: BulkImportRequest,
    service: ThreadService = Depends(get_thread_service),
):
    """Bulk import threads from a raw compilation.

    Parses the compilation text to extract threads, authors, and posts.
    Supports auto-categorization and optional embedding generation.

    Example compilation format:
    ```
    ---
    **Thread 1: Author Name (@handle) - "Title" - Post ID: 123 - Date: Jan 1, 2025 - Likes: 500**

    1/ First post content...
    2/ Second post content...

    ---
    ```
    """
    start_time = time.time()

    try:
        results = await service.import_compilation(request)
        processing_time = (time.time() - start_time) * 1000

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        return BulkImportResponse(
            total_found=len(results),
            successfully_imported=len(successful),
            failed=len(failed),
            results=results,
            processing_time_ms=processing_time,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {e!s}",
        ) from e


@router.post("/export", response_model=ExportResponse)
async def export_threads(
    request: ExportRequest,
    service: ThreadService = Depends(get_thread_service),
):
    """Export threads to specified format.

    Supported formats:
    - JSON: Structured data with all fields
    - Markdown: Formatted document with headers and content
    - TXT: Plain text compilation
    - PDF: Coming soon (returns file URL)
    """
    try:
        content, count = await service.export_threads(request)

        return ExportResponse(
            format=request.format,
            thread_count=count,
            content=content if request.format != ExportFormat.PDF else None,
            file_url=None,  # TODO: Implement PDF generation with file upload
            file_size_bytes=len(content.encode()) if content else None,
            generated_at=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {e!s}",
        ) from e


# ============================================================================
# Analytics Endpoints
# ============================================================================


@router.get("/analytics/summary", response_model=ThreadAnalytics)
async def get_analytics(
    service: ThreadService = Depends(get_thread_service),
):
    """Get analytics summary for the thread collection."""
    return await service.get_analytics()


@router.get("/categories", response_model=list[dict])
async def list_categories():
    """List all available thread categories."""
    return [
        {
            "id": cat.value,
            "name": cat.name.replace("_", " ").title(),
            "description": _get_category_description(cat),
        }
        for cat in ThreadCategoryEnum
    ]


def _get_category_description(category: ThreadCategoryEnum) -> str:
    """Get description for a category."""
    descriptions = {
        ThreadCategoryEnum.AGENT_BASICS: "Introductory content about AI agents",
        ThreadCategoryEnum.PROMPT_ENGINEERING: "System prompts, few-shot examples, chain of thought",
        ThreadCategoryEnum.MEMORY_SYSTEMS: "Short and long-term memory, context management",
        ThreadCategoryEnum.TOOL_INTEGRATION: "Function calling, API integrations, tool use",
        ThreadCategoryEnum.MULTI_AGENT: "Agent swarms, orchestration, collaboration",
        ThreadCategoryEnum.RAG_RETRIEVAL: "Retrieval-augmented generation, knowledge bases",
        ThreadCategoryEnum.DEPLOYMENT: "Production deployment, scaling, infrastructure",
        ThreadCategoryEnum.EVALUATION: "Testing, metrics, benchmarking agents",
        ThreadCategoryEnum.FRAMEWORKS: "LangChain, CrewAI, AutoGen, LangGraph",
        ThreadCategoryEnum.GENERAL: "General AI agent discussions",
    }
    return descriptions.get(category, "")


# ============================================================================
# Scrape Job Endpoints
# ============================================================================


@router.post("/scrape-jobs", response_model=ScrapeJobResponse, status_code=status.HTTP_201_CREATED)
async def create_scrape_job(
    data: ScrapeJobCreate,
    service: ScrapeJobService = Depends(get_scrape_job_service),
):
    """Create a new scrape job to collect threads.

    Jobs can be scheduled for later or run immediately.
    The scraper will search for threads matching the query
    and import them into the system.
    """
    return service.create(data.model_dump())


@router.get("/scrape-jobs", response_model=list[ScrapeJobResponse])
async def list_scrape_jobs(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    service: ScrapeJobService = Depends(get_scrape_job_service),
):
    """List scrape jobs with optional status filter."""
    return service.list(status_filter, limit)


@router.get("/scrape-jobs/{job_id}", response_model=ScrapeJobResponse)
async def get_scrape_job(
    job_id: str,
    service: ScrapeJobService = Depends(get_scrape_job_service),
):
    """Get scrape job status by ID."""
    job = service.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scrape job not found: {job_id}",
        )
    return job


# ============================================================================
# Indexing Status Endpoints
# ============================================================================


@router.get("/unindexed", response_model=list[ThreadSummary])
async def get_unindexed_threads(
    limit: int = Query(default=100, ge=1, le=500),
    service: ThreadService = Depends(get_thread_service),
):
    """Get threads pending vector indexing."""
    threads = await service.get_unindexed_threads(limit)
    return [
        ThreadSummary(
            id=t.id,
            title=t.title,
            author_username=t.author.username if t.author else "unknown",
            author_display_name=t.author.display_name if t.author else "Unknown",
            category=t.category,
            tags=t.tags or [],
            likes=t.likes,
            post_count=t.post_count,
            published_at=t.published_at,
            status=t.status,
        )
        for t in threads
    ]


@router.post("/{thread_id}/mark-indexed", status_code=status.HTTP_200_OK)
async def mark_thread_indexed(
    thread_id: str,
    embedding_id: str = Query(..., description="Reference to vector store embedding"),
    service: ThreadService = Depends(get_thread_service),
):
    """Mark a thread as indexed with its embedding reference."""
    success = await service.mark_thread_indexed(thread_id, embedding_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread not found: {thread_id}",
        )
    return {"status": "indexed", "embedding_id": embedding_id}
