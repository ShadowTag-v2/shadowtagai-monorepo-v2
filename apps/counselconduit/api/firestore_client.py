# apps/counselconduit/api/firestore_client.py
"""Firestore Document Ingestion & Persistence Layer.

Collections:
    attorneys/       — Attorney profiles, subscription tier, usage
    documents/       — Ingested legal documents (metadata only, content ephemeral)
    sessions/        — Active privileged sessions
    billing_events/  — Payment and billing history
    audit_log/       — All privileged computation logs

Zero-retention: Client query content is NEVER written to Firestore.
Only metadata (timestamps, token counts, attorney IDs) is persisted.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from google.cloud import firestore
from pydantic import BaseModel

logger = logging.getLogger("counselconduit.firestore")

_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_DATABASE_ID = os.getenv("FIRESTORE_DATABASE", "(default)")

# ── Models ─────────────────────────────────────────────────────────────────

class AttorneyProfile(BaseModel):
    """Attorney/firm profile stored in Firestore."""
    uid: str
    email: str
    firm_name: str = ""
    tier: str = "trial"  # trial | professional | enterprise
    stripe_customer_id: str = ""
    stripe_subscription_id: str = ""
    monthly_token_limit: int = 100_000
    tokens_used_this_month: int = 0
    created_at: float = 0.0
    last_active: float = 0.0


class DocumentMetadata(BaseModel):
    """Metadata for an ingested legal document (content NOT stored)."""
    doc_id: str
    attorney_id: str
    filename: str
    file_type: str  # pdf, docx, txt
    size_bytes: int = 0
    page_count: int = 0
    ingested_at: float = 0.0
    embedding_status: str = "pending"  # pending | processing | complete | failed


class AuditEntry(BaseModel):
    """Audit log entry for privileged computations."""
    attorney_id: str
    action: str  # query | stream | document_ingest | document_delete
    tokens_used: int = 0
    model: str = ""
    timestamp: float = 0.0
    ip_address: str = ""


# ── Firestore Client ──────────────────────────────────────────────────────

_db: firestore.AsyncClient | None = None


def _get_db() -> firestore.AsyncClient:
    """Lazy-initialize async Firestore client."""
    global _db  # noqa: PLW0603
    if _db is None:
        _db = firestore.AsyncClient(
            project=_PROJECT_ID,
            database=_DATABASE_ID,
        )
        logger.info("Firestore client initialized: project=%s db=%s", _PROJECT_ID, _DATABASE_ID)
    return _db


# ── Attorney Operations ───────────────────────────────────────────────────

async def get_attorney(uid: str) -> AttorneyProfile | None:
    """Retrieve attorney profile by UID."""
    db = _get_db()
    doc = await db.collection("attorneys").document(uid).get()
    if doc.exists:
        return AttorneyProfile(**doc.to_dict(), uid=uid)
    return None


async def create_attorney(profile: AttorneyProfile) -> str:
    """Create a new attorney profile. Returns document ID."""
    db = _get_db()
    profile.created_at = time.time()
    profile.last_active = time.time()
    await db.collection("attorneys").document(profile.uid).set(
        profile.model_dump(exclude={"uid"}),
    )
    logger.info("Attorney created: uid=%s email=%s", profile.uid, profile.email)
    return profile.uid


async def update_attorney_usage(uid: str, tokens: int) -> None:
    """Increment token usage for an attorney."""
    db = _get_db()
    ref = db.collection("attorneys").document(uid)
    await ref.update({
        "tokens_used_this_month": firestore.Increment(tokens),
        "last_active": time.time(),
    })


async def update_attorney_tier(uid: str, tier: str, stripe_sub_id: str = "") -> None:
    """Update attorney subscription tier."""
    db = _get_db()
    update_data: dict[str, Any] = {"tier": tier, "last_active": time.time()}
    if stripe_sub_id:
        update_data["stripe_subscription_id"] = stripe_sub_id
    
    # Set token limits by tier
    tier_limits = {
        "trial": 10_000,
        "professional": 100_000,
        "enterprise": 1_000_000,
    }
    update_data["monthly_token_limit"] = tier_limits.get(tier, 100_000)
    
    await db.collection("attorneys").document(uid).update(update_data)
    logger.info("Attorney tier updated: uid=%s tier=%s", uid, tier)


# ── Document Operations ───────────────────────────────────────────────────

async def ingest_document_metadata(meta: DocumentMetadata) -> str:
    """Store document metadata (NOT content) in Firestore."""
    db = _get_db()
    meta.ingested_at = time.time()
    ref = db.collection("documents").document(meta.doc_id)
    await ref.set(meta.model_dump())
    logger.info(
        "Document metadata ingested: doc_id=%s attorney=%s file=%s",
        meta.doc_id, meta.attorney_id, meta.filename,
    )
    return meta.doc_id


async def get_attorney_documents(attorney_id: str) -> list[DocumentMetadata]:
    """List all documents belonging to an attorney."""
    db = _get_db()
    docs = db.collection("documents").where(
        filter=firestore.FieldFilter("attorney_id", "==", attorney_id)
    ).order_by("ingested_at", direction=firestore.Query.DESCENDING)
    
    results = []
    async for doc in docs.stream():
        results.append(DocumentMetadata(**doc.to_dict()))
    return results


# ── Audit Log ──────────────────────────────────────────────────────────────

async def write_audit_log(entry: AuditEntry) -> None:
    """Write an audit entry for compliance. Immutable — append-only."""
    db = _get_db()
    entry.timestamp = time.time()
    await db.collection("audit_log").add(entry.model_dump())


# ── Billing Events ─────────────────────────────────────────────────────────

async def record_billing_event(
    attorney_id: str,
    event_type: str,
    amount_cents: int = 0,
    stripe_event_id: str = "",
) -> None:
    """Record a billing event for Triple-Dip telemetry."""
    db = _get_db()
    await db.collection("billing_events").add({
        "attorney_id": attorney_id,
        "event_type": event_type,
        "amount_cents": amount_cents,
        "stripe_event_id": stripe_event_id,
        "timestamp": time.time(),
    })
