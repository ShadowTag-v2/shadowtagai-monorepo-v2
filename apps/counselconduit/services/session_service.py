# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""Firestore Session Service for ADK 2.0 session persistence.

Stores agent session state, task contexts, and Kovel attestation receipts
in Firestore with tenant-scoped document paths.

Collection structure:
    tenants/{tenant_id}/sessions/{session_id}
    tenants/{tenant_id}/sessions/{session_id}/tasks/{task_id}
    tenants/{tenant_id}/sessions/{session_id}/attestations/{attestation_id}
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionRecord:
    """A persisted session in Firestore."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    user_id: str = ""
    agent_role: str = "orchestrator"
    state: str = "active"
    encryption_key_ref: str = ""  # Firestore doc ref to encryption key
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    ttl_seconds: int = 3600
    metadata: dict[str, Any] = field(default_factory=dict)


class FirestoreSessionService:
    """Manages ADK 2.0 session persistence in Firestore.

    Features:
    - Tenant-scoped document paths (multi-tenant isolation)
    - Encryption key references (keys stored separately with TTL)
    - Session expiry via Firestore TTL policies
    - Kovel attestation receipt storage
    """

    COLLECTION = "tenants"
    SESSIONS_SUBCOL = "sessions"
    TASKS_SUBCOL = "tasks"
    ATTESTATIONS_SUBCOL = "attestations"

    def __init__(self, db: Any = None) -> None:
        """Initialize with a Firestore client.

        Args:
            db: google.cloud.firestore.AsyncClient instance.
                If None, creates one via ADC.
        """
        self._db = db

    def _ensure_db(self) -> Any:
        """Lazy-initialize Firestore client."""
        if self._db is None:
            try:
                from google.cloud import firestore
                self._db = firestore.AsyncClient()
            except ImportError:
                logger.error(
                    "google-cloud-firestore not installed. "
                    "Run: pip install google-cloud-firestore"
                )
                raise
        return self._db

    def _session_ref(self, tenant_id: str, session_id: str) -> Any:
        """Get Firestore document reference for a session."""
        db = self._ensure_db()
        return (
            db.collection(self.COLLECTION)
            .document(tenant_id)
            .collection(self.SESSIONS_SUBCOL)
            .document(session_id)
        )

    async def create_session(self, record: SessionRecord) -> str:
        """Create a new session document in Firestore.

        Args:
            record: The session record to persist.

        Returns:
            The session_id of the created record.
        """
        ref = self._session_ref(record.tenant_id, record.session_id)
        await ref.set(asdict(record))
        logger.info(
            "Session created in Firestore: tenant=%s session=%s",
            record.tenant_id,
            record.session_id,
        )
        return record.session_id

    async def get_session(
        self, tenant_id: str, session_id: str
    ) -> SessionRecord | None:
        """Retrieve a session from Firestore.

        Args:
            tenant_id: The tenant owning the session.
            session_id: The session to retrieve.

        Returns:
            SessionRecord if found, None otherwise.
        """
        ref = self._session_ref(tenant_id, session_id)
        doc = await ref.get()
        if doc.exists:
            return SessionRecord(**doc.to_dict())
        return None

    async def update_session_state(
        self, tenant_id: str, session_id: str, state: str
    ) -> None:
        """Update the state of a session.

        Args:
            tenant_id: The tenant owning the session.
            session_id: The session to update.
            state: The new state value.
        """
        ref = self._session_ref(tenant_id, session_id)
        await ref.update({
            "state": state,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

    async def store_attestation(
        self,
        tenant_id: str,
        session_id: str,
        attestation: dict[str, Any],
    ) -> str:
        """Store a Kovel attestation receipt for a session.

        Args:
            tenant_id: The tenant owning the session.
            session_id: The session the attestation belongs to.
            attestation: The attestation data (hash, timestamp, etc.).

        Returns:
            The attestation document ID.
        """
        attestation_id = str(uuid.uuid4())
        ref = (
            self._session_ref(tenant_id, session_id)
            .collection(self.ATTESTATIONS_SUBCOL)
            .document(attestation_id)
        )
        await ref.set(attestation)
        logger.info(
            "Attestation stored: tenant=%s session=%s attestation=%s",
            tenant_id,
            session_id,
            attestation_id,
        )
        return attestation_id

    async def expire_session(
        self, tenant_id: str, session_id: str
    ) -> None:
        """Mark a session as expired (dead-man's switch trigger).

        Args:
            tenant_id: The tenant owning the session.
            session_id: The session to expire.
        """
        await self.update_session_state(tenant_id, session_id, "expired")
        logger.info(
            "Session expired (dead-man's switch): tenant=%s session=%s",
            tenant_id,
            session_id,
        )
