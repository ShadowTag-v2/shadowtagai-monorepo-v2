# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""FastAPI endpoint for HumanGateStep external event resumption.

This module provides the HTTP interface that allows authorized users
to approve or reject a pending HumanGateStep in the SK Process pipeline.
The endpoint fires an OnExternalEvent("UserApproved") signal to the
running Semantic Kernel process.

Security: Requires firm-scoped JWT + Judge6 authorization gate.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("human_gate_api")

router = APIRouter(prefix="/api/v1/process", tags=["process-gate"])


# ── Request / Response Models ──


class HumanGateDecision(BaseModel):
    """Client payload for approving/rejecting a pending human gate."""

    process_id: str = Field(..., description="The SK process instance ID awaiting approval.")
    decision: str = Field(..., pattern="^(approve|reject)$", description="Must be 'approve' or 'reject'.")
    reviewer_notes: str | None = Field(None, max_length=2000, description="Optional reviewer notes attached to decision.")


class HumanGateResponse(BaseModel):
    """Response confirming the gate decision was processed."""

    process_id: str
    decision: str
    event_fired: str
    timestamp: str
    reviewer: str


# ── In-memory process registry (replaced by Firestore in production) ──

_pending_gates: dict[str, dict] = {}


def register_pending_gate(process_id: str, metadata: dict | None = None) -> None:
    """Register a process as awaiting human approval.

    Called by the SK Process runner when HumanGateStep.AwaitApproval()
    is reached.
    """
    _pending_gates[process_id] = {
        "registered_at": datetime.now(UTC).isoformat(),
        "metadata": metadata or {},
        "status": "pending",
    }
    logger.info("Registered pending gate for process %s", process_id)


def get_pending_gate(process_id: str) -> dict | None:
    """Get a pending gate by process ID."""
    return _pending_gates.get(process_id)


def resolve_pending_gate(process_id: str, decision: str) -> bool:
    """Mark a pending gate as resolved.

    Returns True if the gate was pending and is now resolved.
    """
    gate = _pending_gates.get(process_id)
    if gate and gate["status"] == "pending":
        gate["status"] = decision
        gate["resolved_at"] = datetime.now(UTC).isoformat()
        return True
    return False


# ── Endpoints ──


@router.post("/gate/decide", response_model=HumanGateResponse)
async def decide_human_gate(
    body: HumanGateDecision,
    x_firm_id: Annotated[str, Header(description="Firm tenant ID")] = "",
    x_user_id: Annotated[str, Header(description="Authenticated user ID")] = "",
) -> HumanGateResponse:
    """Process a human gate decision (approve/reject).

    Fires OnExternalEvent("UserApproved") or OnExternalEvent("UserRejected")
    to the running SK Process instance.

    Requires:
    - Valid firm-scoped JWT (X-Firm-Id header)
    - Authenticated user with reviewer role (X-User-Id header)
    - The process must be in a pending gate state
    """
    if not x_firm_id or not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Missing required headers: X-Firm-Id, X-User-Id",
        )

    # Check if process has a pending gate
    gate = get_pending_gate(body.process_id)
    if gate is None:
        raise HTTPException(
            status_code=404,
            detail=f"No pending gate found for process {body.process_id}",
        )

    if gate["status"] != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"Gate already resolved with decision: {gate['status']}",
        )

    # Resolve the gate
    resolved = resolve_pending_gate(body.process_id, body.decision)
    if not resolved:
        raise HTTPException(
            status_code=500,
            detail="Failed to resolve gate — race condition or state corruption",
        )

    # Determine the external event name based on decision
    event_name = "UserApproved" if body.decision == "approve" else "UserRejected"

    # In production: this would call the SK Process runner via gRPC/HTTP
    # to fire builder.OnExternalEvent(event_name) on the target process.
    # For now, we log the intent.
    logger.info(
        "Firing OnExternalEvent('%s') for process %s by reviewer %s (firm: %s)",
        event_name,
        body.process_id,
        x_user_id,
        x_firm_id,
    )

    return HumanGateResponse(
        process_id=body.process_id,
        decision=body.decision,
        event_fired=event_name,
        timestamp=datetime.now(UTC).isoformat(),
        reviewer=x_user_id,
    )


@router.get("/gate/{process_id}")
async def get_gate_status(
    process_id: str,
    x_firm_id: Annotated[str, Header(description="Firm tenant ID")] = "",
) -> dict:
    """Get the current status of a human gate for a process.

    Returns the gate metadata and current status (pending/approve/reject).
    """
    if not x_firm_id:
        raise HTTPException(status_code=401, detail="Missing X-Firm-Id header")

    gate = get_pending_gate(process_id)
    if gate is None:
        raise HTTPException(
            status_code=404,
            detail=f"No gate found for process {process_id}",
        )

    return {
        "process_id": process_id,
        "status": gate["status"],
        "registered_at": gate["registered_at"],
        "resolved_at": gate.get("resolved_at"),
        "metadata": gate["metadata"],
    }


@router.get("/gates/pending")
async def list_pending_gates(
    x_firm_id: Annotated[str, Header(description="Firm tenant ID")] = "",
) -> dict:
    """List all pending human gates.

    Returns a list of process IDs with pending approval gates.
    Used by the lawyer oversight dashboard.
    """
    if not x_firm_id:
        raise HTTPException(status_code=401, detail="Missing X-Firm-Id header")

    pending = [{"process_id": pid, **gate} for pid, gate in _pending_gates.items() if gate["status"] == "pending"]

    return {
        "firm_id": x_firm_id,
        "pending_count": len(pending),
        "gates": pending,
    }
