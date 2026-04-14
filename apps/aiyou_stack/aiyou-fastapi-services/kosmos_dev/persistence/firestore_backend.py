"""Firestore backend for Shadowtag whiteboard persistence.

Provides real-time sync capabilities for the shared whiteboard.
"""

from __future__ import annotations

from typing import Any

from google.cloud import firestore
from shadowtag.core.whiteboard import Finding, Whiteboard


class FirestoreBackend:
    """Firestore persistence for Shadowtag whiteboard."""

    def __init__(
        self,
        project_id: str,
        database: str = "(default)",
        collection: str = "shadowtag_sessions",
    ):
        self.project_id = project_id
        self.database = database
        self.collection = collection
        self._client: firestore.Client | None = None

    @property
    def client(self) -> firestore.Client:
        """Lazy initialization of Firestore client."""
        if self._client is None:
            self._client = firestore.Client(
                project=self.project_id,
                database=self.database,
            )
        return self._client

    async def save_whiteboard(self, whiteboard: Whiteboard) -> None:
        """Save whiteboard state to Firestore."""
        doc_ref = self.client.collection(self.collection).document(whiteboard.session_id)
        doc_ref.set(whiteboard.to_dict())

    async def load_whiteboard(self, session_id: str) -> Whiteboard | None:
        """Load whiteboard state from Firestore."""
        doc_ref = self.client.collection(self.collection).document(session_id)
        doc = doc_ref.get()

        if not doc.exists:
            return None

        return Whiteboard.from_dict(doc.to_dict())

    async def save_finding(
        self,
        session_id: str,
        finding: Finding,
    ) -> None:
        """Save a single finding (for incremental updates)."""
        doc_ref = (
            self.client.collection(self.collection)
            .document(session_id)
            .collection("findings")
            .document(finding.id)
        )
        doc_ref.set(finding.to_dict())

    async def delete_session(self, session_id: str) -> None:
        """Delete a session and all its findings."""
        doc_ref = self.client.collection(self.collection).document(session_id)

        # Delete subcollection
        findings = doc_ref.collection("findings").stream()
        for finding in findings:
            finding.reference.delete()

        # Delete main document
        doc_ref.delete()

    def list_sessions(self, limit: int = 100) -> list[dict[str, Any]]:
        """List recent sessions."""
        docs = (
            self.client.collection(self.collection)
            .order_by("metrics.total_findings", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )

        sessions = []
        for doc in docs:
            data = doc.to_dict()
            sessions.append(
                {
                    "session_id": doc.id,
                    "total_findings": data.get("metrics", {}).get("total_findings", 0),
                    "consensus_reached": data.get("metrics", {}).get("consensus_reached", 0),
                },
            )

        return sessions
