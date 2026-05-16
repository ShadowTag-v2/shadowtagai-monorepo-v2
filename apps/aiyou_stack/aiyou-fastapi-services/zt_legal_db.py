# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ZT.1 Database Layer — asyncpg queries against the lawtrack schema.

All functions take an asyncpg.Connection (or pool) as the first argument.
Designed for FastAPI's dependency injection: callers acquire a connection
from the pool and pass it in.

Schema defined in: infra/migrations/002_zt_legal.sql
"""

from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any

logger = logging.getLogger("zt_legal_db")


# ── Reads ─────────────────────────────────────────────────────────────────────


async def get_extraction(conn: Any, extraction_id: uuid.UUID) -> dict | None:
    row = await conn.fetchrow(
        """
        SELECT
            extraction_id, matter_id, tenant_id,
            trigger_event, exhibit_citation_id, raw_date_text,
            trigger_date, calculated_due_date, days_to_respond,
            business_days_only, jurisdiction, jurisdiction_rule,
            confidence_score, status,
            approved_by, approved_at, approval_notes,
            rejected_by, rejected_at, rejection_reason,
            created_at, updated_at
        FROM deadline_extractions
        WHERE extraction_id = $1
        """,
        extraction_id,
    )
    return dict(row) if row else None


async def list_extractions_by_matter(
    conn: Any,
    matter_id: uuid.UUID,
    status_filter: str = "pending_approval",
) -> list[dict]:
    rows = await conn.fetch(
        """
        SELECT
            extraction_id, matter_id, tenant_id,
            trigger_event, exhibit_citation_id,
            trigger_date, calculated_due_date, days_to_respond,
            business_days_only, jurisdiction, jurisdiction_rule,
            confidence_score, status, created_at, updated_at
        FROM deadline_extractions
        WHERE matter_id = $1 AND status = $2
        ORDER BY calculated_due_date ASC
        """,
        matter_id,
        status_filter,
    )
    return [dict(r) for r in rows]


async def list_docket(conn: Any, matter_id: uuid.UUID) -> list[dict]:
    """Approved deadlines only, chronological."""
    return await list_extractions_by_matter(conn, matter_id, "approved")


# ── Writes ────────────────────────────────────────────────────────────────────


async def insert_extraction(conn: Any, rec: dict) -> uuid.UUID:
    """Insert a new extraction record. Returns the extraction_id."""
    extraction_id = rec.get("extraction_id") or uuid.uuid4()
    await conn.execute(
        """
        INSERT INTO deadline_extractions (
            extraction_id, matter_id, tenant_id,
            trigger_event, exhibit_citation_id,
            trigger_date, calculated_due_date, days_to_respond,
            business_days_only, jurisdiction, jurisdiction_rule,
            confidence_score, status
        ) VALUES (
            $1, $2, $3,
            $4, $5,
            $6, $7, $8,
            $9, $10, $11,
            $12, $13
        )
        """,
        extraction_id,
        rec["matter_id"],
        rec["tenant_id"],
        rec["trigger_event"],
        rec["exhibit_citation_id"],
        rec["trigger_date"],
        rec["calculated_due_date"],
        rec["days_to_respond"],
        rec["business_days_only"],
        rec.get("jurisdiction", "FRCP"),
        rec.get("jurisdiction_rule", ""),
        rec.get("confidence", 0.92),
        "pending_approval",
    )
    logger.info("[zt_db] inserted extraction=%s matter=%s", extraction_id, rec["matter_id"])
    return extraction_id


async def approve_extraction(
    conn: Any,
    extraction_id: uuid.UUID,
    approver_id: uuid.UUID,
    notes: str = "",
) -> dict | None:
    row = await conn.fetchrow(
        """
        UPDATE deadline_extractions
        SET
            status        = 'approved',
            approved_by   = $2,
            approved_at   = now(),
            approval_notes = $3,
            updated_at    = now()
        WHERE extraction_id = $1 AND status = 'pending_approval'
        RETURNING extraction_id, matter_id, trigger_event, exhibit_citation_id,
                  calculated_due_date, jurisdiction_rule, days_to_respond,
                  business_days_only, confidence_score, status, created_at
        """,
        extraction_id,
        approver_id,
        notes,
    )
    if row:
        logger.info("[zt_db] approved extraction=%s by=%s", extraction_id, approver_id)
    return dict(row) if row else None


async def reject_extraction(
    conn: Any,
    extraction_id: uuid.UUID,
    rejector_id: uuid.UUID,
    reason: str,
) -> dict | None:
    row = await conn.fetchrow(
        """
        UPDATE deadline_extractions
        SET
            status           = 'rejected',
            rejected_by      = $2,
            rejected_at      = now(),
            rejection_reason = $3,
            updated_at       = now()
        WHERE extraction_id = $1 AND status = 'pending_approval'
        RETURNING extraction_id, matter_id, trigger_event, exhibit_citation_id,
                  calculated_due_date, jurisdiction_rule, days_to_respond,
                  business_days_only, confidence_score, status, created_at
        """,
        extraction_id,
        rejector_id,
        reason,
    )
    if row:
        logger.info(
            "[zt_db] rejected extraction=%s by=%s reason=%s",
            extraction_id,
            rejector_id,
            reason,
        )
    return dict(row) if row else None


# ── Pool lifecycle helpers (call from FastAPI lifespan) ───────────────────────


async def create_pool(dsn: str) -> Any:
    """Create an asyncpg connection pool from DSN."""
    import asyncpg  # type: ignore[import]

    pool = await asyncpg.create_pool(
        dsn,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    logger.info("[zt_db] pool created")
    return pool


async def close_pool(pool: Any) -> None:
    await pool.close()
    logger.info("[zt_db] pool closed")


def row_to_response_dict(row: dict) -> dict:
    """Normalise asyncpg row dict to match ExtractionResponse field names."""
    return {
        "extraction_id": row["extraction_id"],
        "matter_id": row["matter_id"],
        "trigger_event": row["trigger_event"],
        "exhibit_citation_id": row["exhibit_citation_id"],
        "calculated_due_date": (
            row["calculated_due_date"]
            if isinstance(row["calculated_due_date"], datetime.date)
            else datetime.date.fromisoformat(str(row["calculated_due_date"]))
        ),
        "jurisdiction_rule": row.get("jurisdiction_rule") or "",
        "days_to_respond": row["days_to_respond"],
        "business_days_only": row["business_days_only"],
        "confidence": float(row.get("confidence_score", row.get("confidence", 0.92))),
        "status": row["status"],
        "created_at": (
            row["created_at"] if isinstance(row["created_at"], datetime.datetime) else datetime.datetime.fromisoformat(str(row["created_at"]))
        ),
    }
