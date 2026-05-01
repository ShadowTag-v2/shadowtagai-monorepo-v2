# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Sandbox Session API — Phase 4 Milestone 1.

FastAPI router for the sandbox session lifecycle endpoints.
Now backed by FirestoreSessionStore for persistent session storage.

Endpoints:
    POST /api/sandbox/sessions         — Create a new sandbox session
    GET  /api/sandbox/sessions         — List active sessions
    GET  /api/sandbox/{session_id}     — Resume / hydrate an existing session
    GET  /api/sandbox/{session_id}/diffs  — Compute overlay diffs
    POST /api/sandbox/{session_id}/commit — Execute attorney decision

Security:
    - Every endpoint requires verified attorney JWT
    - Trust Level 0 enforced at bridge layer
    - All mutations produce immutable audit records
    - Session persistence via Firestore with 30-day TTL
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from apps.counselconduit.api.auth import get_current_attorney
from apps.counselconduit.api.sandbox.firestore_bridge import (
    BridgeResult,
    FirestoreBridge,
)
from apps.counselconduit.api.sandbox.firestore_session_store import (
    FirestoreSessionStore,
)
from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SecurityError,
    SessionConfig,
    SessionState,
)
from apps.counselconduit.api.sandbox.ws_state_push import (
    manager as ws_manager,
    router as ws_router,
)

logger = logging.getLogger("counselconduit.sandbox.api")

router = APIRouter(prefix="/api/sandbox", tags=["sandbox"])
router.include_router(ws_router)

# ── Dependency Injection (B008 compliant) ──────────────────────────────
AttorneyDep = Annotated[dict[str, Any], Depends(get_current_attorney)]


# ── Session Store (Phase 4: Firestore-backed with in-memory fallback) ──
#
# The store is the single source of truth for session CRUD.
# _active_sessions kept as a compatibility shim for existing tests.
_active_sessions: dict[str, SandboxSession] = {}
_store = FirestoreSessionStore()


async def _get_session(session_id: str) -> SandboxSession:
    """Retrieve a sandbox session from Firestore, falling back to memory.

    Phase 4 migration: prefers Firestore, falls back to in-memory dict
    for backward compatibility during transition.
    """
    # Phase 4: Try Firestore first
    try:
        session = await _store.get_session(session_id)
        if session:
            return session
    except Exception:
        logger.debug("Firestore lookup failed, trying in-memory: %s", session_id[:8])

    # Fallback: in-memory (Phase 3 compat + test fixtures)
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session


# ── Request / Response Models ──────────────────────────────────────────


class CreateSessionRequest(BaseModel):
    """Request to create a new sandbox session."""

    matter_id: str = Field(..., description="Matter ID for scoping")
    ttl_seconds: int = Field(1800, description="Session TTL in seconds (default: 30min)")
    max_overlay_files: int = Field(50, description="Maximum overlay files")


class CreateSessionResponse(BaseModel):
    """Response after creating a new sandbox session."""

    session_id: str
    state: str
    matter_id: str
    created_at: float


class SessionSummary(BaseModel):
    """Summary of a sandbox session for listing."""

    session_id: str
    state: str
    matter_id: str
    attorney_uid: str = ""
    created_at: float = 0.0


class CommitRequest(BaseModel):
    """Attorney commit decision request body."""

    action: str = Field(..., description="accept | reject | partial_accept")
    selected_files: list[str] | None = Field(None, description="Files to commit (partial_accept only)")
    matter_id: str = Field(..., description="Matter ID for scoping")
    rejection_reason: str = Field("", description="Rejection reason (reject only)")


class DiffResponse(BaseModel):
    """Response containing computed diffs for the session overlay."""

    session_id: str
    matter_id: str
    diffs: list[dict[str, Any]]
    file_count: int


class CommitResponse(BaseModel):
    """Response after executing the attorney decision."""

    success: bool
    committed_files: list[str] = Field(default_factory=list)
    rejected_files: list[str] = Field(default_factory=list)
    audit_id: str = ""
    error: str = ""
    duration_ms: float = 0.0


# ── Session Lifecycle Endpoints (Phase 4 NEW) ─────────────────────────


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    body: CreateSessionRequest,
    attorney: AttorneyDep = None,  # type: ignore[assignment]
) -> CreateSessionResponse:
    """Create a new sandbox session and persist to Firestore.

    The session starts in CREATED state and can be resumed later.
    """
    attorney_uid = attorney.get("uid", "")
    if not attorney_uid:
        raise HTTPException(status_code=401, detail="Attorney UID required")

    config = SessionConfig(
        matter_id=body.matter_id,
        attorney_uid=attorney_uid,
        ttl_seconds=body.ttl_seconds,
        max_overlay_files=body.max_overlay_files,
    )
    session = SandboxSession(config=config)

    # Persist to Firestore
    try:
        await _store.create_session(session)
    except SecurityError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to create session: %s", e)
        raise HTTPException(status_code=500, detail="Session creation failed") from e

    # Also keep in memory for fast access within this process
    _active_sessions[session.session_id] = session

    logger.info(
        "Session created: %s (matter=%s, attorney=%s)",
        session.session_id[:8],
        body.matter_id[:8],
        attorney_uid[:8],
    )

    return CreateSessionResponse(
        session_id=session.session_id,
        state=session.state.value,
        matter_id=body.matter_id,
        created_at=session.created_at,
    )


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(
    matter: str | None = Query(None, description="Filter by matter ID"),
    attorney: AttorneyDep = None,  # type: ignore[assignment]
) -> list[SessionSummary]:
    """List active sandbox sessions for the current attorney."""
    attorney_uid = attorney.get("uid", "")

    try:
        sessions = await _store.list_active_sessions(
            attorney_uid=attorney_uid or None,
            matter_id=matter,
        )
        return [
            SessionSummary(
                session_id=s.get("session_id", ""),
                state=s.get("state", ""),
                matter_id=s.get("matter_id", ""),
                attorney_uid=s.get("attorney_uid", ""),
                created_at=s.get("created_at", 0.0),
            )
            for s in sessions
        ]
    except Exception as e:
        logger.exception("Failed to list sessions: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list sessions") from e


@router.get("/{session_id}", response_model=CreateSessionResponse)
async def resume_session(
    session_id: str,
    attorney: AttorneyDep = None,  # type: ignore[assignment]
) -> CreateSessionResponse:
    """Resume / hydrate an existing sandbox session from Firestore.

    Returns the session metadata for the frontend to restore state.
    """
    session = await _get_session(session_id)

    # Verify attorney has access to this session
    attorney_uid = attorney.get("uid", "")
    if session.config.attorney_uid and session.config.attorney_uid != attorney_uid:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this session",
        )

    return CreateSessionResponse(
        session_id=session.session_id,
        state=session.state.value,
        matter_id=session.config.matter_id,
        created_at=session.created_at,
    )


# ── Existing Endpoints (Phase 3 — updated for Phase 4) ────────────────


@router.get("/{session_id}/diffs", response_model=DiffResponse)
async def get_session_diffs(
    session_id: str,
    matter: str = Query(..., description="Matter ID"),
    attorney: AttorneyDep = None,  # type: ignore[assignment]
) -> DiffResponse:
    """Compute and return overlay diffs for attorney review.

    The diffs are computed on-demand from the session's CoW overlay
    vs the original document state. Results are not cached — each
    request recomputes to ensure freshness.
    """
    session = await _get_session(session_id)

    # Verify attorney has access to this matter
    if session.config.matter_id != matter:
        raise HTTPException(
            status_code=403,
            detail="Matter ID does not match session",
        )

    try:
        bridge = FirestoreBridge(session)
        # Compute diffs against empty originals (Phase 3 — full overlay)
        # Phase 4 will integrate actual Firestore document fetch
        originals: dict[str, str] = {}
        diffs = bridge.compute_diffs(
            original_files=originals,
            privilege_map=session.config.privilege_map if hasattr(session.config, "privilege_map") else None,
        )

        return DiffResponse(
            session_id=session_id,
            matter_id=matter,
            diffs=[d.to_dict() for d in diffs],
            file_count=len(diffs),
        )

    except SecurityError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except Exception as e:
        logger.exception("Failed to compute diffs: %s", e)
        raise HTTPException(status_code=500, detail="Diff computation failed") from e


@router.post("/{session_id}/commit", response_model=CommitResponse)
async def commit_session(
    session_id: str,
    body: CommitRequest,
    request: Request,
    attorney: AttorneyDep = None,  # type: ignore[assignment]
) -> CommitResponse:
    """Execute the attorney's accept/reject/partial decision.

    Produces an immutable audit record for every call.
    Phase 4: Also records decision in Firestore session store.
    """
    session = await _get_session(session_id)

    # Map string action to enum
    try:
        action = CommitAction(body.action)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {body.action}",
        ) from None

    attorney_uid = attorney.get("uid", "")
    firm_id = attorney.get("firm_id", "")

    if not attorney_uid:
        raise HTTPException(status_code=401, detail="Attorney UID required")

    try:
        bridge = FirestoreBridge(session)
        result: BridgeResult = await bridge.commit_to_firestore(
            action=action,
            attorney_uid=attorney_uid,
            firm_id=firm_id,
            selected_files=body.selected_files,
            rejection_reason=body.rejection_reason,
        )

        # Phase 4: Record decision in Firestore session store
        try:
            await _store.record_decision(
                session_id=session_id,
                action=action,
                attorney_uid=attorney_uid,
                firm_id=firm_id,
                selected_files=body.selected_files,
                rejection_reason=body.rejection_reason,
                result_summary=result.to_dict(),
            )
        except Exception:
            logger.warning("Failed to record decision in session store (non-fatal)")

        # Phase 4: Update session state in Firestore
        new_state = SessionState.COMMITTED if action != CommitAction.REJECT else SessionState.REJECTED
        try:
            await _store.update_state(
                session_id,
                new_state,
                extra_fields={
                    "committed_files": result.committed_files,
                    "rejection_reason": body.rejection_reason if action == CommitAction.REJECT else "",
                },
            )
        except Exception:
            logger.warning("Failed to update session state in store (non-fatal)")

        # Push real-time state notification to connected WebSocket clients
        await ws_manager.notify_state_change(
            session_id=session_id,
            from_state="reviewing",
            to_state="committed" if action != CommitAction.REJECT else "rejected",
            metadata={
                "action": action.value,
                "file_count": len(result.committed_files),
                "audit_id": result.audit_id,
            },
        )

        return CommitResponse(
            success=result.success,
            committed_files=result.committed_files,
            rejected_files=result.rejected_files,
            audit_id=result.audit_id,
            error=result.error,
            duration_ms=result.duration_ms,
        )

    except SecurityError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except Exception as e:
        logger.exception("Commit failed: %s", e)
        raise HTTPException(status_code=500, detail="Commit operation failed") from e
