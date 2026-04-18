# apps/counselconduit/api/firestore_client.py
"""Firestore client for CounselConduit — attestation, matter, and session persistence.

Uses google-cloud-firestore with tenant-scoped collections.
All writes are append-only for attestation receipts (immutable audit trail).

Collections:
- firms/{firm_id}/attestations/{attestation_id} — Kovel receipts
- firms/{firm_id}/matters/{matter_id} — magic link matters
- firms/{firm_id}/sessions/{session_id} — vent/oracle sessions
- firms/{firm_id}/gdpr/{request_id} — GDPR deletion requests
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("counselconduit.firestore")

# Lazy-init Firestore client
_client = None
_DATABASE = os.getenv("FIRESTORE_DATABASE", "shadowtag-engine")


def _get_client():
    """Lazy initialization of Firestore client using ADC."""
    global _client
    if _client is None:
        try:
            from google.cloud import firestore

            _client = firestore.AsyncClient(
                project=os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4"),
                database=_DATABASE,
            )
            logger.info("Firestore client initialized: db=%s", _DATABASE)
        except Exception as e:
            logger.error("Firestore init failed: %s", e)
            raise
    return _client


# ── Attestation Receipts (append-only) ─────────────────────────────────────


async def store_attestation(firm_id: str, attestation: dict[str, Any]) -> str:
    """Store an attestation receipt. Immutable — no update/delete allowed."""
    db = _get_client()
    attestation_id = attestation["attestation_id"]
    doc_ref = db.collection("firms").document(firm_id).collection("attestations").document(attestation_id)
    await doc_ref.set(
        {
            **attestation,
            "_created_at": datetime.now(UTC).isoformat(),
            "_immutable": True,
        }
    )
    logger.info("Attestation stored: firm=%s id=%s", firm_id, attestation_id)
    return attestation_id


async def get_attestation(firm_id: str, attestation_id: str) -> dict[str, Any] | None:
    """Retrieve an attestation receipt."""
    db = _get_client()
    doc = await db.collection("firms").document(firm_id).collection("attestations").document(attestation_id).get()
    return doc.to_dict() if doc.exists else None


# ── Magic Link Matters ─────────────────────────────────────────────────────


async def store_matter(firm_id: str, matter: dict[str, Any]) -> str:
    """Store a magic link matter."""
    db = _get_client()
    matter_id = matter["matter_id"]
    doc_ref = db.collection("firms").document(firm_id).collection("matters").document(matter_id)
    await doc_ref.set(
        {
            **matter,
            "_created_at": datetime.now(UTC).isoformat(),
            "consumed": False,
        }
    )
    return matter_id


async def consume_matter_token(firm_id: str, matter_id: str) -> bool:
    """Mark a magic link token as consumed (single-use)."""
    db = _get_client()
    doc_ref = db.collection("firms").document(firm_id).collection("matters").document(matter_id)
    doc = await doc_ref.get()
    if not doc.exists:
        return False
    data = doc.to_dict()
    if data.get("consumed"):
        return False  # Already used
    await doc_ref.update({"consumed": True, "_consumed_at": datetime.now(UTC).isoformat()})
    return True


# ── GDPR Deletion Requests ────────────────────────────────────────────────


async def store_gdpr_request(firm_id: str, request: dict[str, Any]) -> str:
    """Store a GDPR deletion request (30-day grace period)."""
    db = _get_client()
    request_id = request["receipt_id"]
    doc_ref = db.collection("firms").document(firm_id).collection("gdpr").document(request_id)
    await doc_ref.set(
        {
            **request,
            "_created_at": datetime.now(UTC).isoformat(),
            "status": "pending_grace_period",
        }
    )
    return request_id


# ── Session Storage ────────────────────────────────────────────────────────


async def store_session(firm_id: str, session: dict[str, Any]) -> str:
    """Store a vent/oracle session."""
    db = _get_client()
    session_id = session["session_id"]
    doc_ref = db.collection("firms").document(firm_id).collection("sessions").document(session_id)
    await doc_ref.set(
        {
            **session,
            "_created_at": datetime.now(UTC).isoformat(),
        }
    )
    return session_id


async def append_session_message(firm_id: str, session_id: str, role: str, content: str) -> None:
    """Append a message to a session transcript."""
    from google.cloud import firestore as fs

    db = _get_client()
    doc_ref = db.collection("firms").document(firm_id).collection("sessions").document(session_id)
    await doc_ref.update(
        {
            "messages": fs.ArrayUnion(
                [
                    {
                        "role": role,
                        "content": content,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                ]
            )
        }
    )


# ── Attorney Usage Tracking ────────────────────────────────────────────────


async def update_attorney_usage(
    attorney_id: str,
    tokens_used: int = 0,
    queries: int = 1,
) -> None:
    """Increment token and query counters for billing attribution.

    Stored in attorneys/{attorney_id}/usage/{month} for per-month tracking.
    """
    from google.cloud import firestore as fs

    db = _get_client()
    month_key = datetime.now(UTC).strftime("%Y-%m")
    doc_ref = db.collection("attorneys").document(attorney_id).collection("usage").document(month_key)
    await doc_ref.set(
        {
            "tokens_used": fs.Increment(tokens_used),
            "query_count": fs.Increment(queries),
            "_updated_at": datetime.now(UTC).isoformat(),
        },
        merge=True,
    )


# ── Audit Log ──────────────────────────────────────────────────────────────


class AuditEntry:
    """Structured audit log entry for compliance."""

    def __init__(
        self,
        action: str,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ):
        self.action = action
        self.actor_id = actor_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details or {}
        self.timestamp = datetime.now(UTC).isoformat()


async def write_audit_log(entry: AuditEntry) -> None:
    """Write an immutable audit log entry."""
    db = _get_client()
    await db.collection("audit_log").add(
        {
            "action": entry.action,
            "actor_id": entry.actor_id,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "details": entry.details,
            "timestamp": entry.timestamp,
            "_immutable": True,
        }
    )
    logger.info(
        "Audit: action=%s actor=%s resource=%s/%s",
        entry.action,
        entry.actor_id,
        entry.resource_type,
        entry.resource_id,
    )
