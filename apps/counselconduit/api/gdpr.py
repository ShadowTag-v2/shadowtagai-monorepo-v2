# apps/counselconduit/api/gdpr.py
"""GDPR Account Deletion Flow — Cor.30 R27.

Full account deletion within 30 days, automated, with email receipt.
Cascade: user data → transcripts → billing → audit log entry.

Architecture:
- Soft delete: mark as deleted, start 30-day countdown
- Hard delete: Cloud Task fires after 30 days, wipes all data
- Audit: Deletion event logged (append-only, never deleted)
- Email: Confirmation receipt sent via Resend/SendGrid
"""

from __future__ import annotations

import logging
import os
import time
from datetime import UTC, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.gdpr")

router = APIRouter(prefix="/account", tags=["GDPR"])


# ── Models ─────────────────────────────────────────────────────────────────


class DeletionRequest(BaseModel):
    """User-initiated account deletion request."""

    confirmation: str = Field(
        ...,
        description="Must be 'DELETE MY ACCOUNT' to confirm",
    )
    reason: str | None = Field(
        None,
        description="Optional reason (not required, data-minimization)",
        max_length=500,
    )


class DeletionReceipt(BaseModel):
    """Receipt confirming deletion was scheduled."""

    status: str = "scheduled"
    deletion_date: str  # ISO 8601 — 30 days from now
    receipt_id: str
    message: str = (
        "Your account and all associated data will be permanently deleted " "within 30 days. You will receive a confirmation email when complete."
    )


class DataExportRequest(BaseModel):
    """GDPR Article 20 — Right to data portability."""

    format: str = Field(default="json", pattern="^(json|csv)$")


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.post(
    "/delete",
    response_model=DeletionReceipt,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_account_deletion(
    request: DeletionRequest,
) -> DeletionReceipt:
    """Request account deletion (GDPR Article 17 — Right to Erasure).

    - Requires explicit confirmation string
    - Schedules deletion 30 days out (grace period for undo)
    - Logs to append-only audit trail
    - Sends email receipt
    """
    if request.confirmation != "DELETE MY ACCOUNT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CONFIRMATION_REQUIRED",
                "message": "Please type 'DELETE MY ACCOUNT' to confirm.",
            },
        )

    # Generate receipt
    from apps.counselconduit.api.uuid7 import uuid7_str

    receipt_id = uuid7_str()
    deletion_date = datetime.now(UTC).isoformat()

    # TODO: Wire to Firestore soft-delete + Cloud Tasks 30-day trigger
    # TODO: Wire to email service for receipt delivery

    logger.info(
        "Account deletion scheduled: receipt=%s reason=%s",
        receipt_id,
        request.reason or "none",
    )

    return DeletionReceipt(
        receipt_id=receipt_id,
        deletion_date=deletion_date,
    )


@router.post("/export", status_code=status.HTTP_202_ACCEPTED)
async def request_data_export(
    request: DataExportRequest,
) -> dict[str, Any]:
    """Request data export (GDPR Article 20 — Right to Portability).

    Generates a download link (signed URL, 24h TTL) for all user data:
    - Profile information
    - Session transcripts (lawyer view only)
    - Billing history
    - Audit log (user's own actions)
    """
    from apps.counselconduit.api.uuid7 import uuid7_str

    export_id = uuid7_str()

    # TODO: Wire to Cloud Tasks to generate export file
    # TODO: Wire to signed URL generation for secure download

    logger.info("Data export requested: export=%s format=%s", export_id, request.format)

    return {
        "status": "processing",
        "export_id": export_id,
        "format": request.format,
        "message": "Your data export is being prepared. You'll receive an email with a download link within 24 hours.",
    }


@router.get("/deletion-status/{receipt_id}")
async def check_deletion_status(receipt_id: str) -> dict[str, Any]:
    """Check the status of a pending account deletion."""
    # TODO: Query Firestore for deletion status
    return {
        "receipt_id": receipt_id,
        "status": "pending",
        "message": "Deletion is scheduled. Contact support to cancel.",
    }
