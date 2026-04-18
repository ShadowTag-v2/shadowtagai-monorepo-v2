"""FastAPI endpoints for Context Window Management"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .models import (
    AnalysisRole,
    AnalysisSession,
    ChatSummary,
    ContextIndex,
    CreateSessionRequest,
    CreateSummaryRequest,
    SessionStatus,
    UpdateSessionRequest,
)
from .service import ContextManager

# Initialize router
router = APIRouter(prefix="/api/v1/context", tags=["Context Management"])

# Initialize service (singleton)
context_manager = ContextManager()


class SessionResponse(BaseModel):
    """API response for session operations"""

    success: bool
    message: str
    session: AnalysisSession | None = None


class SummaryResponse(BaseModel):
    """API response for summary operations"""

    success: bool
    message: str
    summary: ChatSummary | None = None


class SessionListResponse(BaseModel):
    """API response for session list operations"""

    success: bool
    total: int
    sessions: list[AnalysisSession]


# ============================================================================
# Session Endpoints
# ============================================================================


@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new AI analysis session

    This endpoint creates a new analysis session and adds it to the context index.
    Use this when starting a new AI chat for architecture review, code analysis, etc.

    Example:
        ```json
        {
            "issue_title": "Gemini Ingestion Layer Analysis",
            "role": "architecture_review",
            "goal": "Comprehensive pre-production analysis of ingestion pipeline",
            "constraints": "Pre-prod environment, no production telemetry",
            "model_name": "gemini-2.0-pro",
            "confidence_threshold": 0.60
        }
        ```

    """
    try:
        session = context_manager.create_session(request)
        return SessionResponse(
            success=True,
            message=f"Created session {session.session_id}",
            session=session,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Retrieve a session by ID

    Returns the full session details including metadata, token usage,
    and related session references.
    """
    session = context_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return SessionResponse(
        success=True,
        message="Session retrieved",
        session=session,
    )


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update an existing session

    Allows updating status, token count, and completion timestamp.
    Automatically manages active session counts and token consumption tracking.

    Example:
        ```json
        {
            "status": "completed",
            "total_tokens": 125000,
            "completed_at": "2025-11-15T14:30:00Z"
        }
        ```

    """
    session = context_manager.update_session(
        session_id=session_id,
        status=request.status,
        total_tokens=request.total_tokens,
        completed_at=request.completed_at,
    )

    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return SessionResponse(
        success=True,
        message=f"Updated session {session_id}",
        session=session,
    )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    role: AnalysisRole | None = Query(None, description="Filter by analysis role"),
    status: SessionStatus | None = Query(None, description="Filter by session status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
):
    """List sessions with optional filtering

    Retrieve all sessions or filter by role (e.g., architecture_review, code_analysis)
    and status (active, completed, archived).

    Sessions are returned in reverse chronological order (most recent first).
    """
    sessions = context_manager.list_sessions(role=role, status=status, limit=limit)

    return SessionListResponse(
        success=True,
        total=len(sessions),
        sessions=sessions,
    )


@router.get("/sessions/search", response_model=SessionListResponse)
async def search_sessions(
    q: str = Query(..., description="Search query"),
    fields: list[str] = Query(
        ["issue_title", "goal", "constraints"],
        description="Fields to search in",
    ),
):
    """Search sessions by text query

    Performs a case-insensitive search across specified fields.
    Returns matching sessions in reverse chronological order.

    Example:
        `/sessions/search?q=ingestion&fields=issue_title&fields=goal`

    """
    sessions = context_manager.search_sessions(query=q, search_in=fields)

    return SessionListResponse(
        success=True,
        total=len(sessions),
        sessions=sessions,
    )


@router.post("/sessions/{session_id}/archive", response_model=SessionResponse)
async def archive_session(session_id: str):
    """Archive a completed session

    Marks a session as archived, removing it from active tracking
    while preserving the historical record.
    """
    session = context_manager.archive_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return SessionResponse(
        success=True,
        message=f"Archived session {session_id}",
        session=session,
    )


# ============================================================================
# Summary Endpoints
# ============================================================================


@router.post("/summaries", response_model=SummaryResponse)
async def create_summary(request: CreateSummaryRequest):
    """Create a summary for a completed session

    Captures key outcomes, decisions, findings, and recommendations from
    an AI analysis session. Automatically marks the session as completed.

    Example:
        ```json
        {
            "session_id": "gemini-ingestion-20251115-abc123",
            "summary": "Completed comprehensive analysis...",
            "key_decisions": ["Approved 60% confidence threshold"],
            "findings": ["Ethical compliance is robust"],
            "recommendations": ["Add LinkedIn source"],
            "risks_identified": ["Twitter API dependency"],
            "related_threads": ["https://github.com/org/repo/issues/123"],
            "tags": ["ingestion", "gemini-2.0-pro", "pre-production"]
        }
        ```

    """
    try:
        # Verify session exists
        session = context_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")

        summary = context_manager.create_summary(request)
        return SummaryResponse(
            success=True,
            message=f"Created summary for session {request.session_id}",
            summary=summary,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summaries/{session_id}", response_model=SummaryResponse)
async def get_summary(session_id: str):
    """Retrieve a summary by session ID

    Returns the chat summary including decisions, findings, recommendations,
    and identified risks for the specified session.
    """
    summary = context_manager.get_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Summary for session {session_id} not found")

    return SummaryResponse(
        success=True,
        message="Summary retrieved",
        summary=summary,
    )


# ============================================================================
# Index & Export Endpoints
# ============================================================================


@router.get("/index", response_model=ContextIndex)
async def get_index():
    """Get the full context index

    Returns the master index with all sessions, statistics, and metadata.
    Use this to get an overview of all analysis activities.
    """
    return context_manager.get_index()


@router.get("/sessions/{session_id}/export")
async def export_session_context(session_id: str):
    """Export a session with its summary for AI context loading

    Provides a complete export of a session including metadata, summary,
    and related information in a format suitable for loading into an AI chat.

    This is useful for continuing a previous analysis or referencing past work.
    """
    export_data = context_manager.export_session_context(session_id)
    if not export_data:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return export_data


@router.get("/sessions/active")
async def get_active_sessions():
    """Get all currently active sessions

    Returns a list of sessions with status=ACTIVE.
    Useful for tracking ongoing analysis work.
    """
    sessions = context_manager.get_active_sessions()

    return SessionListResponse(
        success=True,
        total=len(sessions),
        sessions=sessions,
    )


# ============================================================================
# Health Check
# ============================================================================


@router.get("/health")
async def health_check():
    """Health check endpoint

    Returns the health status of the context management service.
    """
    index = context_manager.get_index()

    return {
        "status": "healthy",
        "service": "context_management",
        "total_sessions": index.total_sessions,
        "active_sessions": index.active_sessions,
        "total_tokens_consumed": index.total_tokens_consumed,
        "storage_path": str(context_manager.storage_path),
    }
