# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ZT.1 FastAPI Router — Zero-Touch Legal Deadline Management
==========================================================
Agent-Drafted, Human-Verified pattern.

Mount in main app::

    from zt_legal_router import router as zt_router
    app.include_router(zt_router)

Requires app.state.db_pool (asyncpg.Pool) set during lifespan.
See zt_legal_db.create_pool / close_pool for pool lifecycle helpers.

Endpoints:
    POST   /api/v1/zt/matters/{matter_id}/ingest        — ingest filing
    GET    /api/v1/zt/matters/{matter_id}/queue         — list pending extractions
    POST   /api/v1/zt/extractions/{extraction_id}/approve
    POST   /api/v1/zt/extractions/{extraction_id}/reject
    GET    /api/v1/zt/matters/{matter_id}/docket        — approved deadlines
"""

from __future__ import annotations

import datetime
import logging
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Request, status
from pydantic import UUID4, BaseModel, Field

from zt_legal_db import (  # type: ignore[import]
    approve_extraction,
    insert_extraction,
    list_docket,
    list_extractions_by_matter,
    reject_extraction,
    row_to_response_dict,
)
from zt_legal_db import get_extraction as db_get_extraction

logger = logging.getLogger("zt_legal_router")

router = APIRouter(prefix="/api/v1/zt", tags=["zt-legal"])


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


# ── DB dependency ─────────────────────────────────────────────────────────────


async def get_db(request: Request) -> AsyncGenerator:
    """Yield an asyncpg connection from the app pool."""
    async with request.app.state.db_pool.acquire() as conn:
        yield conn


DBConn = Annotated[object, Depends(get_db)]


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_deadline_record(
    matter_id: uuid.UUID,
    tenant_id: uuid.UUID,
    trigger_date: datetime.date,
    dl: object,
    jurisdiction: str,
) -> dict:
    from control.pnkln.pnkln_core.engines.jurisdiction import (  # type: ignore[import]
        DeadlineMath,
        JurisdictionEngine,
    )

    engine = JurisdictionEngine()
    math = DeadlineMath(
        add_days=dl.days_to_respond,  # type: ignore[attr-defined]
        business_days_only=dl.business_days_only,  # type: ignore[attr-defined]
    )
    due_date = engine.calculate(trigger_date, math)

    return {
        "extraction_id": uuid.uuid4(),
        "matter_id": matter_id,
        "tenant_id": tenant_id,
        "trigger_event": dl.trigger_event,  # type: ignore[attr-defined]
        "exhibit_citation_id": dl.exhibit_citation_id,  # type: ignore[attr-defined]
        "calculated_due_date": due_date,
        "trigger_date": trigger_date,
        "jurisdiction_rule": dl.jurisdiction_rule,  # type: ignore[attr-defined]
        "days_to_respond": dl.days_to_respond,  # type: ignore[attr-defined]
        "business_days_only": dl.business_days_only,  # type: ignore[attr-defined]
        "jurisdiction": jurisdiction,
        "confidence": 0.92,
    }


def _row_to_response(row: dict) -> ExtractionResponse:
    d = row_to_response_dict(row)
    return ExtractionResponse(**d)


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
    conn: DBConn,
) -> list[ExtractionResponse]:
    import sys
    from pathlib import Path

    from control.pnkln.pnkln_core.agents.legal import (  # type: ignore[import]
        extract_deadlines_from_filing,
    )

    # Resolving path to the Ultrathink Router
    src_path = str(Path(__file__).parent.parent.parent.parent / "legaltrack" / "src")
    if src_path not in sys.path:
        sys.path.append(src_path)

    from legaltrack.autopilot.glicko_router import UltrathinkRouter

    # Glicko-2 Dynamic Routing based on text size (proxy for complexity)
    router_engine = UltrathinkRouter()
    complexity = "high" if len(req.raw_text) > 15000 else "moderate"
    agent_path, expected_latency = router_engine.route_task(complexity)

    logger.info(f"[zt/ingest] Glicko-2 router determined optimal path: {agent_path} | Expected Latency: {expected_latency}s")

    try:
        deadlines = extract_deadlines_from_filing(
            raw_text=req.raw_text,
            filing_name=f"matter-{matter_id}",
        )
    except RuntimeError as exc:
        logger.error("[zt/ingest] compute backend unavailable: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No zero-CPU backend available. Start ANE bridge or kvcached worker.",
        ) from exc

    responses: list[ExtractionResponse] = []
    for dl in deadlines:
        rec = _build_deadline_record(
            matter_id=uuid.UUID(str(matter_id)),
            tenant_id=uuid.UUID(str(req.tenant_id)),
            trigger_date=req.trigger_date,
            dl=dl,
            jurisdiction=req.jurisdiction,
        )
        eid = await insert_extraction(conn, rec)
        saved = await db_get_extraction(conn, eid)
        if saved:
            responses.append(_row_to_response(saved))

    logger.info("[zt/ingest] matter=%s → %s extractions queued", matter_id, len(responses))
    return responses


@router.get(
    "/matters/{matter_id}/queue",
    response_model=list[ExtractionResponse],
    summary="List pending-approval deadline extractions for a matter",
)
async def list_queue(
    matter_id: Annotated[UUID4, Path()],
    include_status: Annotated[str, Query()] = "pending_approval",
    conn: DBConn = None,
) -> list[ExtractionResponse]:
    rows = await list_extractions_by_matter(conn, uuid.UUID(str(matter_id)), include_status)
    return [_row_to_response(r) for r in rows]


@router.post(
    "/extractions/{extraction_id}/approve",
    response_model=ExtractionResponse,
    summary="Human approves extraction → commits to master docket",
)
async def approve_extraction_endpoint(
    extraction_id: Annotated[UUID4, Path()],
    req: Annotated[ApproveRequest, Body()],
    conn: DBConn,
) -> ExtractionResponse:
    existing = await db_get_extraction(conn, uuid.UUID(str(extraction_id)))
    if not existing:
        raise HTTPException(status_code=404, detail="Extraction not found")
    if existing["status"] != "pending_approval":
        raise HTTPException(status_code=409, detail=f"Already {existing['status']}")

    updated = await approve_extraction(
        conn,
        uuid.UUID(str(extraction_id)),
        uuid.UUID(str(req.approver_id)),
        req.notes,
    )
    if not updated:
        raise HTTPException(status_code=409, detail="Concurrent update conflict — retry")

    logger.info("[zt/approve] extraction=%s approved by %s", extraction_id, req.approver_id)
    return _row_to_response(updated)


@router.post(
    "/extractions/{extraction_id}/reject",
    response_model=ExtractionResponse,
    summary="Human rejects extraction with mandatory reason",
)
async def reject_extraction_endpoint(
    extraction_id: Annotated[UUID4, Path()],
    req: Annotated[RejectRequest, Body()],
    conn: DBConn,
) -> ExtractionResponse:
    existing = await db_get_extraction(conn, uuid.UUID(str(extraction_id)))
    if not existing:
        raise HTTPException(status_code=404, detail="Extraction not found")
    if existing["status"] != "pending_approval":
        raise HTTPException(status_code=409, detail=f"Already {existing['status']}")

    updated = await reject_extraction(
        conn,
        uuid.UUID(str(extraction_id)),
        uuid.UUID(str(req.rejector_id)),
        req.reason,
    )
    if not updated:
        raise HTTPException(status_code=409, detail="Concurrent update conflict — retry")

    logger.info("[zt/reject] extraction=%s rejected: %s", extraction_id, req.reason)
    return _row_to_response(updated)


@router.get(
    "/matters/{matter_id}/docket",
    response_model=list[ExtractionResponse],
    summary="Master docket — approved deadlines for a matter",
)
async def get_docket(
    matter_id: Annotated[UUID4, Path()],
    conn: DBConn,
) -> list[ExtractionResponse]:
    rows = await list_docket(conn, uuid.UUID(str(matter_id)))
    return [_row_to_response(r) for r in rows]
