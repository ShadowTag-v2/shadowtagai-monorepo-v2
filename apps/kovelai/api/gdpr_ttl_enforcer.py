"""
GDPR 30-Day TTL Enforcement for Brief Exports.

Implements Cloud Tasks scheduled cleanup of expired brief_exports
documents. Per GDPR Article 17 (Right to Erasure), brief PDFs are
auto-deleted 30 days after generation unless explicitly retained.

Firestore TTL Policy is the primary mechanism. This module provides
the secondary enforcement layer (belt-and-suspenders).

Queue: kovelai-gdpr-cleanup (scheduled daily via Cloud Scheduler)
Collection: brief_exports

@see schema_reference.sql — brief_exports table (expires_at field)
@see OMNIBUS_STRATEGIC_BLUEPRINT.md — Zero-data architecture
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone, UTC

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════

TTL_DAYS = 30
BATCH_SIZE = 500  # Firestore batch limit
COLLECTION = "brief_exports"


# ═══════════════════════════════════════════════════════════
# Models
# ═══════════════════════════════════════════════════════════


class DeletionRecord(BaseModel):
    """Record of a GDPR deletion action."""

    document_id: str
    firm_id: str
    deleted_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    reason: str = "GDPR Article 17 — 30-day TTL expiry"
    ttl_days: int = TTL_DAYS


class DeletionReport(BaseModel):
    """Summary of a GDPR cleanup run."""

    run_id: str
    started_at: str
    completed_at: str | None = None
    documents_scanned: int = 0
    documents_deleted: int = 0
    documents_retained: int = 0
    errors: list[str] = Field(default_factory=list)
    deletion_records: list[DeletionRecord] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# TTL Enforcement
# ═══════════════════════════════════════════════════════════


async def enforce_brief_ttl(
    db,  # google.cloud.firestore_v1.AsyncClient
    dry_run: bool = False,
) -> DeletionReport:
    """
    Scan brief_exports for expired documents and delete them.

    This runs as a Cloud Tasks handler, triggered daily by Cloud Scheduler.

    Args:
        db: Firestore async client
        dry_run: If True, report but don't delete

    Returns:
        DeletionReport with scan/delete summary
    """
    run_id = f"gdpr-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}"
    report = DeletionReport(
        run_id=run_id,
        started_at=datetime.now(UTC).isoformat(),
    )

    cutoff = datetime.now(UTC) - timedelta(days=TTL_DAYS)
    logger.info(
        "GDPR TTL enforcement run %s — scanning for docs older than %s",
        run_id,
        cutoff.isoformat(),
    )

    try:
        # Query expired documents
        query = (
            db.collection(COLLECTION)
            .where("expires_at", "<=", cutoff)
            .limit(BATCH_SIZE)
        )

        docs = query.stream()
        batch = db.batch()
        batch_count = 0

        async for doc in docs:
            report.documents_scanned += 1
            data = doc.to_dict()

            # Safety check: never delete docs from active sessions
            if data.get("session_active", False):
                report.documents_retained += 1
                logger.warning(
                    "Skipping active session doc: %s (firm: %s)",
                    doc.id,
                    data.get("firm_id", "unknown"),
                )
                continue

            if dry_run:
                logger.info("[DRY RUN] Would delete: %s", doc.id)
                report.documents_deleted += 1
                report.deletion_records.append(
                    DeletionRecord(
                        document_id=doc.id,
                        firm_id=data.get("firm_id", "unknown"),
                    )
                )
                continue

            # Batch delete
            batch.delete(doc.reference)
            batch_count += 1
            report.deletion_records.append(
                DeletionRecord(
                    document_id=doc.id,
                    firm_id=data.get("firm_id", "unknown"),
                )
            )

            # Commit in batches of BATCH_SIZE
            if batch_count >= BATCH_SIZE:
                await batch.commit()
                report.documents_deleted += batch_count
                batch_count = 0
                batch = db.batch()

        # Commit remaining
        if batch_count > 0 and not dry_run:
            await batch.commit()
            report.documents_deleted += batch_count

    except Exception as exc:
        error_msg = f"GDPR enforcement error: {exc}"
        logger.error(error_msg)
        report.errors.append(error_msg)

    report.completed_at = datetime.now(UTC).isoformat()

    logger.info(
        "GDPR TTL run %s complete: scanned=%d, deleted=%d, retained=%d, errors=%d",
        run_id,
        report.documents_scanned,
        report.documents_deleted,
        report.documents_retained,
        len(report.errors),
    )

    return report


# ═══════════════════════════════════════════════════════════
# Cloud Scheduler Config (Reference)
# ═══════════════════════════════════════════════════════════

CLOUD_SCHEDULER_CONFIG = {
    "name": "gdpr-brief-ttl-enforcement",
    "schedule": "0 3 * * *",  # Daily at 3:00 AM UTC
    "time_zone": "UTC",
    "http_target": {
        "uri": "https://counselconduit-767252945109.us-central1.run.app/api/gdpr/enforce-ttl",
        "http_method": "POST",
        "oidc_token": {
            "service_account_email": "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com",
        },
    },
    "retry_config": {
        "retry_count": 3,
        "max_retry_duration": "600s",
    },
}
