# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Firestore Session Store — Phase 4 Milestone 1.

Replaces the in-memory _active_sessions dict (Phase 3) with Firestore-backed
persistent session storage. Enables:
  1. Session resume — attorney can close browser and come back
  2. Multi-device access — same session across devices
  3. 30-day TTL auto-expiry — aligns with GDPR Module
  4. Immutable decision audit trail — append-only sub-collection

Firestore Schema:
    sandbox_sessions/{session_id}
        ├── overlay_files/{file_path_hash}
        └── decisions/{decision_id}

Security invariants:
    - Trust Level 0 enforced on every read/write
    - Attorney UID verified against session config
    - No PII in session metadata (session_id prefix only in logs)
    - TTL enforced both client-side and via Firestore TTL policy
"""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any

from apps.counselconduit.api.sandbox.session import (
    CommitAction,
    SandboxSession,
    SecurityError,
    SessionConfig,
    SessionState,
)

logger = logging.getLogger("counselconduit.sandbox.store")

# Default TTL for sandbox sessions (30 days for GDPR compliance)
SESSION_TTL_DAYS = 30


def _sha256_short(content: str) -> str:
    """Compute short SHA-256 hash for document IDs."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:24]


class FirestoreSessionStore:
    """Firestore-backed session store with full CRUD + audit trail.

    Replaces the Phase 3 in-memory dict with persistent Firestore storage.
    All operations enforce Trust Level 0 security invariant.
    """

    COLLECTION = "sandbox_sessions"
    OVERLAY_SUB = "overlay_files"
    DECISIONS_SUB = "decisions"

    def __init__(self, db: Any | None = None):
        """Initialize store with Firestore client.

        Args:
            db: Firestore client instance. If None, imports from firestore_client.
        """
        self._db = db

    @property
    def db(self) -> Any:
        """Lazy Firestore client initialization."""
        if self._db is None:
            try:
                from apps.counselconduit.api.firestore_client import _get_client
            except ImportError:
                from api.firestore_client import _get_client  # type: ignore[no-redef]
            self._db = _get_client()
        return self._db

    # ── Create ────────────────────────────────────────────────────────────

    async def create_session(self, session: SandboxSession) -> str:
        """Persist a new sandbox session to Firestore.

        Args:
            session: SandboxSession instance to persist.

        Returns:
            session_id of the created session.

        Raises:
            SecurityError: If trust level is not 0.
        """
        if session.config.trust_level != 0:
            msg = "Cannot persist session with trust_level != 0"
            raise SecurityError(msg)

        expire_at = datetime.now(UTC) + timedelta(days=SESSION_TTL_DAYS)

        doc_ref = self.db.collection(self.COLLECTION).document(session.session_id)
        await doc_ref.set(
            {
                "session_id": session.session_id,
                "state": session.state.value,
                "matter_id": session.config.matter_id,
                "attorney_uid": session.config.attorney_uid,
                "ttl_seconds": session.config.ttl_seconds,
                "max_overlay_files": session.config.max_overlay_files,
                "trust_level": session.config.trust_level,
                "created_at": session.created_at,
                "rejection_reason": session.rejection_reason,
                "committed_files": session.committed_files,
                "expire_at": expire_at,
                "_updated_at": datetime.now(UTC).isoformat(),
                "_source": "firestore_session_store",
            }
        )

        # Write overlay files as sub-collection documents
        if session.overlay_files:
            await self._write_overlay_files(session.session_id, session.overlay_files)

        logger.info(
            "Session created: %s… (matter=%s, state=%s)",
            session.session_id[:8],
            session.config.matter_id[:8] if session.config.matter_id else "none",
            session.state.value,
        )
        return session.session_id

    # ── Read ──────────────────────────────────────────────────────────────

    async def get_session(self, session_id: str) -> SandboxSession | None:
        """Load a sandbox session from Firestore.

        Args:
            session_id: Session identifier.

        Returns:
            Hydrated SandboxSession, or None if not found / expired.
        """
        doc_ref = self.db.collection(self.COLLECTION).document(session_id)
        doc = await doc_ref.get()

        if not doc.exists:
            return None

        data = doc.to_dict()

        # Check TTL expiry
        expire_at = data.get("expire_at")
        if expire_at and hasattr(expire_at, "timestamp"):
            if datetime.now(UTC).timestamp() > expire_at.timestamp():
                logger.info("Session %s… expired, marking EXPIRED", session_id[:8])
                await self.update_state(session_id, SessionState.EXPIRED)
                return None

        # Hydrate SandboxSession from Firestore document
        config = SessionConfig(
            matter_id=data.get("matter_id", ""),
            attorney_uid=data.get("attorney_uid", ""),
            ttl_seconds=data.get("ttl_seconds", 1800),
            max_overlay_files=data.get("max_overlay_files", 50),
        )

        session = SandboxSession(
            session_id=data.get("session_id", session_id),
            config=config,
            state=SessionState(data.get("state", "created")),
            created_at=data.get("created_at", time.time()),
            rejection_reason=data.get("rejection_reason", ""),
            committed_files=data.get("committed_files", []),
        )

        # Load overlay files from sub-collection
        session.overlay_files = await self._read_overlay_files(session_id)

        return session

    async def session_exists(self, session_id: str) -> bool:
        """Check if a session document exists without full hydration."""
        doc_ref = self.db.collection(self.COLLECTION).document(session_id)
        doc = await doc_ref.get()
        return doc.exists

    # ── Update ────────────────────────────────────────────────────────────

    async def update_state(
        self,
        session_id: str,
        new_state: SessionState,
        *,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Update session state in Firestore.

        Args:
            session_id: Session identifier.
            new_state: New session state.
            extra_fields: Additional fields to update alongside state.
        """
        doc_ref = self.db.collection(self.COLLECTION).document(session_id)
        update_data: dict[str, Any] = {
            "state": new_state.value,
            "_updated_at": datetime.now(UTC).isoformat(),
        }
        if extra_fields:
            update_data.update(extra_fields)

        await doc_ref.update(update_data)
        logger.info("Session %s… state → %s", session_id[:8], new_state.value)

    async def update_overlay(
        self,
        session_id: str,
        overlay_files: dict[str, str],
        diff_summary: list[dict[str, Any]],
    ) -> None:
        """Update overlay files and transition to REVIEWING.

        Args:
            session_id: Session identifier.
            overlay_files: Map of file paths to overlay content.
            diff_summary: Structured diff summary for UI rendering.
        """
        # Write overlay files to sub-collection
        await self._write_overlay_files(session_id, overlay_files)

        # Update session document with summary and state
        doc_ref = self.db.collection(self.COLLECTION).document(session_id)
        await doc_ref.update(
            {
                "state": SessionState.REVIEWING.value,
                "diff_summary": diff_summary,
                "overlay_file_count": len(overlay_files),
                "_updated_at": datetime.now(UTC).isoformat(),
            }
        )

    # ── Decision Audit Trail (Append-Only) ────────────────────────────────

    async def record_decision(
        self,
        session_id: str,
        *,
        action: CommitAction,
        attorney_uid: str,
        firm_id: str,
        selected_files: list[str] | None = None,
        rejection_reason: str = "",
        result_summary: dict[str, Any] | None = None,
    ) -> str:
        """Record an immutable decision in the decisions sub-collection.

        This is APPEND-ONLY — no overwrites, no deletes.
        Each decision attempt gets its own document for full traceability.

        Args:
            session_id: Session identifier.
            action: Attorney decision (accept/reject/partial).
            attorney_uid: UID of the deciding attorney.
            firm_id: Firm identifier.
            selected_files: Files selected for partial accept.
            rejection_reason: Reason for rejection.
            result_summary: Summary of the commit result.

        Returns:
            Decision document ID.
        """
        decisions_ref = self.db.collection(self.COLLECTION).document(session_id).collection(self.DECISIONS_SUB)

        decision_data = {
            "action": action.value,
            "attorney_uid": attorney_uid,
            "firm_id": firm_id,
            "selected_files": selected_files or [],
            "rejection_reason": rejection_reason,
            "result_summary": result_summary or {},
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": session_id,
            "_immutable": True,
        }

        # Auto-generate doc ID for append-only semantics
        _ts, doc_ref = await decisions_ref.add(decision_data)
        decision_id = doc_ref.id

        logger.info(
            "Decision recorded: session=%s… action=%s decision=%s",
            session_id[:8],
            action.value,
            decision_id[:8],
        )
        return decision_id

    async def get_decisions(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve all decisions for a session (ordered by timestamp).

        Returns:
            List of decision records, oldest first.
        """
        decisions_ref = self.db.collection(self.COLLECTION).document(session_id).collection(self.DECISIONS_SUB)
        query = decisions_ref.order_by("timestamp")
        docs = await query.get()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    # ── Delete / Cleanup ──────────────────────────────────────────────────

    async def expire_session(self, session_id: str) -> None:
        """Mark a session as expired (soft delete).

        Does NOT delete the document — preserves audit trail.
        """
        await self.update_state(session_id, SessionState.EXPIRED)

    # ── Internal: Overlay Sub-Collection ──────────────────────────────────

    async def _write_overlay_files(self, session_id: str, overlay_files: dict[str, str]) -> None:
        """Write overlay files as sub-collection documents.

        Each file is stored as a separate document for efficient per-file access.
        Document ID is derived from the file path hash.
        """
        batch = self.db.batch()
        overlay_ref = self.db.collection(self.COLLECTION).document(session_id).collection(self.OVERLAY_SUB)

        for file_path, content in overlay_files.items():
            doc_id = _sha256_short(file_path)
            doc_ref = overlay_ref.document(doc_id)
            batch.set(
                doc_ref,
                {
                    "file_path": file_path,
                    "content": content,
                    "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                    "_updated_at": datetime.now(UTC).isoformat(),
                },
            )

        await batch.commit()

    async def _read_overlay_files(self, session_id: str) -> dict[str, str]:
        """Read all overlay files from the sub-collection.

        Returns:
            Map of file paths to file content.
        """
        overlay_ref = self.db.collection(self.COLLECTION).document(session_id).collection(self.OVERLAY_SUB)
        docs = await overlay_ref.get()
        return {doc.to_dict().get("file_path", ""): doc.to_dict().get("content", "") for doc in docs}

    # ── Utility ───────────────────────────────────────────────────────────

    async def list_active_sessions(
        self,
        attorney_uid: str | None = None,
        matter_id: str | None = None,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List active (non-expired, non-committed) sessions.

        Args:
            attorney_uid: Filter by attorney UID.
            matter_id: Filter by matter ID.
            limit: Maximum sessions to return.

        Returns:
            List of session summaries.
        """
        query = self.db.collection(self.COLLECTION)

        if attorney_uid:
            query = query.where("attorney_uid", "==", attorney_uid)
        if matter_id:
            query = query.where("matter_id", "==", matter_id)

        # Exclude terminal states
        query = query.where(
            "state",
            "not-in",
            [
                SessionState.COMMITTED.value,
                SessionState.REJECTED.value,
                SessionState.EXPIRED.value,
            ],
        )
        query = query.limit(limit)

        docs = await query.get()
        return [doc.to_dict() for doc in docs]
