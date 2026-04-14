"""Atomic Chat Router - REST API Endpoints

Provides endpoints for:
- Creating new atomic chat contexts (OPORD creation)
- Saving chat summaries (OPORD completion)
- Executing workflows (JSON action blocks)
- Searching contexts (full-text + filters)
- Scholarly PDF indexing and search
"""

import logging
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from src.shadowtag_v4.services.context_index import ContextIndexService
from src.shadowtag_v4.services.scholarly_pdf_indexer import ScholarlyPDFIndexer
from src.shadowtag_v4.services.workflow_engine import WorkflowExecutionEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/atomic-chat", tags=["atomic-chat"])


# ==================== Request/Response Models ====================


class CreateContextRequest(BaseModel):
    """Request model for creating new OPORD context."""

    task_title: str = Field(..., description="OPORD task title")
    agent_id: str = Field(..., description="Agent ID executing task")
    shift_number: int = Field(0, ge=0, le=2, description="Shift number (0-2)")

    mission: dict[str, str] = Field(..., description="5W: who, what, when, where, why")
    situation: dict[str, str] | None = Field(
        None,
        description="Enemy forces, friendly forces, attachments, civil considerations",
    )
    execution: dict[str, Any] | None = Field(
        None,
        description="Commander's intent, concept of operations, tasks, coordinating instructions",
    )
    service_support: dict[str, Any] | None = Field(
        None, description="Logistics, personnel, medical/error handling",
    )
    command_signal: dict[str, Any] | None = Field(
        None, description="Command structure, signal channels, succession",
    )
    tags: list[str] | None = Field(None, description="Tags for categorization")


class UpdateContextRequest(BaseModel):
    """Request model for updating OPORD context."""

    opord_number: int = Field(..., description="OPORD number to update")
    summary: str | None = Field(None, description="Task summary")
    decisions: list[str] | None = Field(None, description="Key decisions made")
    status: str | None = Field(None, description="New status")


class SearchContextsRequest(BaseModel):
    """Request model for searching contexts."""

    query: str | None = Field(None, description="Full-text search query")
    tags: list[str] | None = Field(None, description="Filter by tags")
    agent_id: str | None = Field(None, description="Filter by agent")
    shift_number: int | None = Field(None, description="Filter by shift")
    status: str | None = Field(None, description="Filter by status")
    limit: int = Field(100, ge=1, le=1000, description="Max results")


class ExecuteWorkflowRequest(BaseModel):
    """Request model for executing workflow."""

    workflow: dict[str, Any] = Field(..., description="Workflow definition (JSON)")
    inputs: dict[str, str] | None = Field(None, description="Pre-filled input values")


class ScholarlyPDFSearchRequest(BaseModel):
    """Request model for searching scholarly PDFs."""

    query: str = Field(..., description="Search query")
    authors: list[str] | None = Field(None, description="Filter by authors")
    year_range: tuple | None = Field(None, description="Filter by year range")
    topics: list[str] | None = Field(None, description="Filter by topics/tags")
    limit: int = Field(20, ge=1, le=100, description="Max results")


# ==================== Endpoints ====================

# Initialize services
context_service = ContextIndexService()
workflow_engine = WorkflowExecutionEngine()
pdf_indexer = ScholarlyPDFIndexer()


@router.post("/contexts", status_code=status.HTTP_201_CREATED)
async def create_context(request: CreateContextRequest) -> dict[str, Any]:
    """Create new OPORD context.

    This is the "New AI Issue Chat" workflow endpoint.

    Example:
    ```
    POST /api/v1/atomic-chat/contexts
    {
      "task_title": "Implement ERC-8004 Reputation API",
      "agent_id": "agent_042",
      "shift_number": 0,
      "mission": {
        "who": "Squad Alpha (agents 200-250)",
        "what": "REST API endpoints for ERC-8004 reputation queries",
        "when": "Complete by 2025-11-23",
        "where": "src/shadowtag_v4/routers/reputation.py",
        "why": "Enable reputation-based access control"
      },
      "tags": ["api", "blockchain", "erc8004"]
    }
    ```

    """
    try:
        result = context_service.create_context(
            task_title=request.task_title,
            agent_id=request.agent_id,
            shift_number=request.shift_number,
            mission=request.mission,
            situation=request.situation,
            execution=request.execution,
            service_support=request.service_support,
            command_signal=request.command_signal,
            tags=request.tags,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create context: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/contexts/{opord_number}")
async def get_context(opord_number: int) -> dict[str, Any]:
    """Get single OPORD context by number."""
    result = context_service.get_context(opord_number)
    if not result:
        raise HTTPException(status_code=404, detail=f"OPORD {opord_number} not found")
    return result


@router.patch("/contexts/{opord_number}")
async def update_context(opord_number: int, request: UpdateContextRequest) -> dict[str, Any]:
    """Update OPORD context with summary and decisions.

    This is the "Save Chat Summary" workflow endpoint.
    """
    try:
        success = context_service.update_context(
            opord_number=opord_number,
            summary=request.summary,
            decisions=request.decisions,
            status=request.status,
        )

        if not success:
            raise HTTPException(status_code=404, detail=f"OPORD {opord_number} not found")

        return {"opord_number": opord_number, "updated": True}

    except Exception as e:
        logger.error(f"Failed to update context: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/contexts/search")
async def search_contexts(request: SearchContextsRequest) -> list[dict[str, Any]]:
    """Search OPORD contexts with full-text and filters.

    Example:
    ```
    POST /api/v1/atomic-chat/contexts/search
    {
      "query": "reentrancy vulnerability",
      "tags": ["security", "blockchain"],
      "limit": 50
    }
    ```

    """
    try:
        results = context_service.search_contexts(
            query=request.query,
            tags=request.tags,
            agent_id=request.agent_id,
            shift_number=request.shift_number,
            status=request.status,
        )
        return results[: request.limit]

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/workflows/execute")
async def execute_workflow(request: ExecuteWorkflowRequest) -> dict[str, Any]:
    """Execute workflow from JSON definition.

    Example:
    ```
    POST /api/v1/atomic-chat/workflows/execute
    {
      "workflow": {
        "block_name": "New Security Audit",
        "actions": [
          {"type": "AskForInput", "title": "Contract Name"},
          {"type": "GetDate", "format": "YYYY-MM-DD HH:mm"},
          {"type": "CreateNote", "noteTitle": "Security Audit {{Contract Name}}"}
        ]
      },
      "inputs": {
        "Contract Name": "ShadowTagAccount.sol"
      }
    }
    ```

    """
    try:
        result = workflow_engine.execute_workflow(workflow=request.workflow, inputs=request.inputs)
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/scholarly-pdfs/upload")
async def upload_scholarly_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    authors: str = Form(...),  # Comma-separated
    year: int = Form(...),
    topics: str | None = Form(None),  # Comma-separated
) -> dict[str, Any]:
    """Upload and index scholarly PDF.

    Extracts text, indexes in Elasticsearch for full-text search.
    This enables the "Sauron's Panorama" knowledge base.
    """
    try:
        # Read PDF content
        content = await file.read()

        # Parse authors and topics
        author_list = [a.strip() for a in authors.split(",")]
        topic_list = [t.strip() for t in topics.split(",")] if topics else []

        # Index PDF
        result = pdf_indexer.index_pdf(
            pdf_content=content,
            title=title,
            authors=author_list,
            year=year,
            topics=topic_list,
        )

        logger.info(f"Indexed PDF: {title} ({len(result['pages'])} pages)")

        return result

    except Exception as e:
        logger.error(f"PDF upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/scholarly-pdfs/search")
async def search_scholarly_pdfs(
    request: ScholarlyPDFSearchRequest,
) -> list[dict[str, Any]]:
    """Search indexed scholarly PDFs.

    Full-text search across all indexed papers using Elasticsearch.

    Example:
    ```
    POST /api/v1/atomic-chat/scholarly-pdfs/search
    {
      "query": "Elasticsearch indexing performance",
      "year_range": [2020, 2025],
      "topics": ["search", "performance"],
      "limit": 10
    }
    ```

    Returns papers ranked by relevance with excerpt highlights.

    """
    try:
        results = pdf_indexer.search_pdfs(
            query=request.query,
            authors=request.authors,
            year_range=request.year_range,
            topics=request.topics,
            limit=request.limit,
        )

        logger.info(f"PDF search for '{request.query}' returned {len(results)} results")

        return results

    except Exception as e:
        logger.error(f"PDF search failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/shifts/{shift_number}/contexts")
async def get_shift_contexts(shift_number: int, status: str = "active") -> list[dict[str, Any]]:
    """Get all contexts for a specific shift."""
    if shift_number not in [0, 1, 2]:
        raise HTTPException(status_code=400, detail="Shift must be 0, 1, or 2")

    return context_service.get_shift_contexts(shift_number, status)


@router.post("/shifts/{shift_number}/clear-memory")
async def clear_shift_memory(shift_number: int) -> dict[str, Any]:
    """Clear shift memory (archive completed contexts).

    Called during shift handoff to free short-term memory.
    """
    if shift_number not in [0, 1, 2]:
        raise HTTPException(status_code=400, detail="Shift must be 0, 1, or 2")

    count = context_service.clear_shift_memory(shift_number)

    return {"shift_number": shift_number, "contexts_archived": count}
