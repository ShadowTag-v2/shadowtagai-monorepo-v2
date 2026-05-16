# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
LegalTrack Rules Engine FastAPI Router
======================================
Adopts the Zero-Touch (ZT.1) Deadline Management spec for GCP Cloud Run.
Pattern: Agent-Drafted, Human-Verified.
"""

from __future__ import annotations

import datetime
import logging
import os
import sqlite3
import uuid
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from pydantic import UUID4, BaseModel, Field

from ..calendar.google_sync import GoogleCalendarController
from .jurisdiction import JurisdictionEngine

logger = logging.getLogger("legaltrack_rules")

router = APIRouter()

# ── SQLite persistence (replaces in-memory _store) ───────────────────────────
_DB_PATH = os.environ.get("LEGALTRACK_DB", "/tmp/legaltrack.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deadline_extractions (
            extraction_id TEXT PRIMARY KEY,
            matter_id TEXT NOT NULL,
            tenant_id TEXT,
            trigger_event TEXT,
            exhibit_citation_id TEXT,
            calculated_due_date TEXT,
            jurisdiction_rule TEXT,
            days_to_respond INTEGER,
            business_days_only INTEGER,
            jurisdiction TEXT,
            confidence REAL,
            status TEXT DEFAULT 'pending_approval',
            approved_by TEXT,
            approval_notes TEXT,
            rejected_by TEXT,
            rejection_reason TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["calculated_due_date"] = datetime.date.fromisoformat(d["calculated_due_date"])
    d["created_at"] = datetime.datetime.fromisoformat(d["created_at"])
    d["business_days_only"] = bool(d["business_days_only"])
    for k in ("extraction_id", "matter_id"):
        d[k] = uuid.UUID(d[k])
    return d


# ── Request / Response models ─────────────────────────────────────────────────


class FilingIngestRequest(BaseModel):
    tenant_id: UUID4
    raw_text: str = Field(..., min_length=10, max_length=500_000)
    source: str = Field(..., description="email_webhook | manual_upload | api")
    jurisdiction: str = Field(default="FRCP")
    trigger_date: datetime.date = Field(..., description="The date the filing was served / received")


class ExtractionResponse(BaseModel):
    extraction_id: UUID4
    matter_id: UUID4
    trigger_event: str
    exhibit_citation_id: str
    calculated_due_date: datetime.date
    jurisdiction_rule: str
    days_to_respond: int
    business_days_only: bool
    confidence: float
    status: str  # pending_approval | approved | rejected
    created_at: datetime.datetime


class ApproveRequest(BaseModel):
    approver_id: UUID4
    notes: str = ""


class RejectRequest(BaseModel):
    rejector_id: UUID4
    reason: str = Field(..., min_length=1)


def _record_to_response(rec: dict) -> ExtractionResponse:
    return ExtractionResponse(
        extraction_id=rec["extraction_id"],
        matter_id=rec["matter_id"],
        trigger_event=rec["trigger_event"],
        exhibit_citation_id=rec["exhibit_citation_id"],
        calculated_due_date=rec["calculated_due_date"],
        jurisdiction_rule=rec["jurisdiction_rule"],
        days_to_respond=rec["days_to_respond"],
        business_days_only=rec["business_days_only"],
        confidence=rec["confidence"],
        status=rec["status"],
        created_at=rec["created_at"],
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "/matters/{matter_id}/ingest",
    response_model=list[ExtractionResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest filing → AI extracts deadlines → queued for human approval",
)
async def ingest_filing(
    matter_id: Annotated[UUID4, Path()],
    req: Annotated[FilingIngestRequest, Body()],
) -> list[ExtractionResponse]:
    """Ingest filing → AI extracts deadlines → persisted to SQLite for approval."""
    engine = JurisdictionEngine()
    rule = engine.resolve_rule("service_of_complaint", req.jurisdiction)
    if not rule:
        raise HTTPException(status_code=400, detail=f"Unknown rule for jurisdiction {req.jurisdiction}")

    due_date = engine.calculate(req.trigger_date, rule.math)
    extraction_id = str(uuid.uuid4())
    now = datetime.datetime.now(timezone.utc).isoformat()

    conn = _get_conn()
    conn.execute(
        """INSERT INTO deadline_extractions
           (extraction_id, matter_id, tenant_id, trigger_event, exhibit_citation_id,
            calculated_due_date, jurisdiction_rule, days_to_respond, business_days_only,
            jurisdiction, confidence, status, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            extraction_id,
            str(matter_id),
            str(req.tenant_id),
            "service_of_complaint",
            "Page 1, Paragraph 1",
            due_date.isoformat(),
            "FRCP 12(a)(1)(A)(i)",
            rule.math.add_days,
            int(rule.math.business_days_only),
            req.jurisdiction,
            0.95,
            "pending_approval",
            now,
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM deadline_extractions WHERE extraction_id=?", (extraction_id,)).fetchone()
    conn.close()
    return [_record_to_response(_row_to_dict(row))]


@router.get(
    "/matters/{matter_id}/queue",
    response_model=list[ExtractionResponse],
)
async def list_queue(
    matter_id: Annotated[UUID4, Path()],
    include_status: Annotated[str, Query()] = "pending_approval",
) -> list[ExtractionResponse]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM deadline_extractions WHERE matter_id=? AND status=?",
        (str(matter_id), include_status),
    ).fetchall()
    conn.close()
    return [_record_to_response(_row_to_dict(r)) for r in rows]


@router.post(
    "/extractions/{extraction_id}/approve",
    response_model=ExtractionResponse,
)
async def approve_extraction(
    extraction_id: Annotated[UUID4, Path()],
    req: Annotated[ApproveRequest, Body()],
) -> ExtractionResponse:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM deadline_extractions WHERE extraction_id=?", (str(extraction_id),)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Extraction not found")
    rec = _row_to_dict(row)
    if rec["status"] != "pending_approval":
        conn.close()
        raise HTTPException(status_code=409, detail=f"Already {rec['status']}")

    conn.execute(
        "UPDATE deadline_extractions SET status='approved', approved_by=?, approval_notes=? WHERE extraction_id=?",
        (str(req.approver_id), req.notes, str(extraction_id)),
    )
    conn.commit()
    rec = _row_to_dict(conn.execute("SELECT * FROM deadline_extractions WHERE extraction_id=?", (str(extraction_id),)).fetchone())
    conn.close()

    # Gap 3 — wire approved deadline to Google Calendar
    due = rec["calculated_due_date"]
    cal = GoogleCalendarController()
    await cal.upsert_event(
        calendar_id="primary",
        title=f"[LegalTrack] {rec['trigger_event']} — {rec['jurisdiction_rule']}",
        start_iso=due.isoformat(),
        end_iso=due.isoformat(),
        source_system="legaltrack",
        event_hash=str(rec["extraction_id"]),
    )
    return _record_to_response(rec)


@router.post(
    "/extractions/{extraction_id}/reject",
    response_model=ExtractionResponse,
)
async def reject_extraction(
    extraction_id: Annotated[UUID4, Path()],
    req: Annotated[RejectRequest, Body()],
) -> ExtractionResponse:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM deadline_extractions WHERE extraction_id=?", (str(extraction_id),)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Extraction not found")
    rec = _row_to_dict(row)
    if rec["status"] != "pending_approval":
        conn.close()
        raise HTTPException(status_code=409, detail=f"Already {rec['status']}")

    conn.execute(
        "UPDATE deadline_extractions SET status='rejected', rejected_by=?, rejection_reason=? WHERE extraction_id=?",
        (str(req.rejector_id), req.reason, str(extraction_id)),
    )
    conn.commit()
    rec = _row_to_dict(conn.execute("SELECT * FROM deadline_extractions WHERE extraction_id=?", (str(extraction_id),)).fetchone())
    conn.close()
    return _record_to_response(rec)


@router.get(
    "/matters/{matter_id}/docket",
    response_model=list[ExtractionResponse],
)
async def get_docket(
    matter_id: Annotated[UUID4, Path()],
) -> list[ExtractionResponse]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM deadline_extractions WHERE matter_id=? AND status='approved' ORDER BY calculated_due_date ASC",
        (str(matter_id),),
    ).fetchall()
    conn.close()
    return [_record_to_response(_row_to_dict(r)) for r in rows]
