# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Sandbox Session API — Phase 3 Milestone 3.

FastAPI router for the sandbox session diff and commit endpoints.
Wired into the main CounselConduit API app.

Endpoints:
    GET  /api/sandbox/{session_id}/diffs  — Compute overlay diffs
    POST /api/sandbox/{session_id}/commit — Execute attorney decision

Security:
    - Every endpoint requires verified attorney JWT
    - Trust Level 0 enforced at bridge layer
    - All mutations produce immutable audit records
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from apps.counselconduit.api.auth import get_current_attorney
from apps.counselconduit.api.sandbox.firestore_bridge import (
    BridgeResult,
    FirestoreBridge,
)
from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SecurityError,
)

logger = logging.getLogger("counselconduit.sandbox.api")

router = APIRouter(prefix="/api/sandbox", tags=["sandbox"])


# ── Request / Response Models ──────────────────────────────────────────


class CommitRequest(BaseModel):
    """Attorney commit decision request body."""

    action: str = Field(..., description="accept | reject | partial_accept")
    selected_files: list[str] | None = Field(
        None, description="Files to commit (partial_accept only)"
    )
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


# ── Session Store (in-memory for Phase 3 — Firestore-backed in Phase 4) ──

_active_sessions: dict[str, SandboxSession] = {}


def _get_session(session_id: str) -> SandboxSession:
    """Retrieve an active sandbox session or raise 404."""
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session


# ── Endpoints ──────────────────────────────────────────────────────────


@router.get("/{session_id}/diffs", response_model=DiffResponse)
async def get_session_diffs(
    session_id: str,
    matter: str = Query(..., description="Matter ID"),
    attorney: dict[str, Any] = Depends(get_current_attorney),
) -> DiffResponse:
    """Compute and return overlay diffs for attorney review.

    The diffs are computed on-demand from the session's CoW overlay
    vs the original document state. Results are not cached — each
    request recomputes to ensure freshness.
    """
    session = _get_session(session_id)

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
    attorney: dict[str, Any] = Depends(get_current_attorney),
) -> CommitResponse:
    """Execute the attorney's accept/reject/partial decision.

    Produces an immutable audit record for every call.
    """
    session = _get_session(session_id)

    # Map string action to enum
    try:
        action = CommitAction(body.action)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {body.action}",
        )

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
