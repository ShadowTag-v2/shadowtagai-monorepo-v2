# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Firestore Backend: Persistent storage for world model state.

Provides:
- World model serialization to Firestore
- Session state persistence and recovery
- Hypothesis, analysis, and literature tracking
- Query capabilities for retrieval
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from google.cloud import firestore

    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    logging.warning("Firestore SDK not installed. Install with: pip install google-cloud-firestore")

from kosmos.core.world_model import (
    AnalysisResult,
    Hypothesis,
    KosmosWorldModel,
    LiteratureRef,
)

logger = logging.getLogger(__name__)


class FirestoreBackend:
    """Firestore persistence backend for world model state.

    Schema:
        /sessions/{session_id}
            - metadata (goal, status, phase, timestamps, costs)
        /sessions/{session_id}/hypotheses/{hypothesis_id}
            - hypothesis data
        /sessions/{session_id}/analysis_results/{result_id}
            - analysis result data
        /sessions/{session_id}/literature/{lit_id}
            - literature reference data
    """

    def __init__(
        self,
        project_id: str,
        database: str = "(default)",
    ):
        """Initialize Firestore backend.

        Args:
            project_id: GCP project ID
            database: Firestore database name

        """
        if not FIRESTORE_AVAILABLE:
            raise RuntimeError("Firestore SDK not installed")

        self.project_id = project_id
        self.db = firestore.Client(project=project_id, database=database)

        logger.info(f"Firestore backend initialized for project {project_id}")

    def save_world_model(self, world_model: KosmosWorldModel):
        """Save complete world model state to Firestore.

        Args:
            world_model: KosmosWorldModel instance to save

        """
        session_id = world_model.session_id

        # Save session metadata
        session_ref = self.db.collection("sessions").document(session_id)
        session_data = {
            "session_id": session_id,
            "goal": world_model.goal,
            "status": world_model.status,
            "phase": world_model.phase.value,
            "phase_history": world_model.phase_history,
            "created_at": world_model.created_at,
            "total_cost": world_model.total_cost,
            "total_tokens": world_model.total_tokens,
            "num_hypotheses": len(world_model.hypotheses),
            "num_analysis_results": len(world_model.analysis_results),
            "num_literature_refs": len(world_model.literature_refs),
        }
        session_ref.set(session_data, merge=True)

        # Save hypotheses
        for hyp in world_model.hypotheses:
            hyp_ref = session_ref.collection("hypotheses").document(hyp.id)
            hyp_ref.set(hyp.to_dict(), merge=True)

        # Save analysis results
        for result in world_model.analysis_results:
            result_ref = session_ref.collection("analysis_results").document(result.id)
            result_ref.set(result.to_dict(), merge=True)

        # Save literature refs
        for lit in world_model.literature_refs:
            lit_ref = session_ref.collection("literature").document(lit.id)
            lit_ref.set(lit.to_dict(), merge=True)

        logger.info(
            f"Saved world model for session {session_id}: "
            f"{len(world_model.hypotheses)} hypotheses, "
            f"{len(world_model.analysis_results)} results, "
            f"{len(world_model.literature_refs)} literature",
        )

    def load_world_model(self, session_id: str) -> KosmosWorldModel | None:
        """Load world model state from Firestore.

        Args:
            session_id: Session ID to load

        Returns:
            KosmosWorldModel instance or None if not found

        """
        session_ref = self.db.collection("sessions").document(session_id)
        session_doc = session_ref.get()

        if not session_doc.exists:
            logger.warning(f"Session {session_id} not found in Firestore")
            return None

        session_data = session_doc.to_dict()

        # Create world model instance
        world_model = KosmosWorldModel(
            session_id=session_id,
            goal=session_data["goal"],
        )
        world_model.status = session_data.get("status", "initialized")
        world_model.created_at = session_data.get("created_at")
        world_model.total_cost = session_data.get("total_cost", 0.0)
        world_model.total_tokens = session_data.get("total_tokens", 0)
        world_model.phase_history = session_data.get("phase_history", [])

        # Load hypotheses
        hyp_docs = session_ref.collection("hypotheses").stream()
        for hyp_doc in hyp_docs:
            hyp_data = hyp_doc.to_dict()
            hypothesis = Hypothesis.from_dict(hyp_data)
            world_model.hypotheses.append(hypothesis)

        # Load analysis results
        result_docs = session_ref.collection("analysis_results").stream()
        for result_doc in result_docs:
            result_data = result_doc.to_dict()
            analysis_result = AnalysisResult.from_dict(result_data)
            world_model.analysis_results.append(analysis_result)

        # Load literature refs
        lit_docs = session_ref.collection("literature").stream()
        for lit_doc in lit_docs:
            lit_data = lit_doc.to_dict()
            lit_ref = LiteratureRef.from_dict(lit_data)
            world_model.literature_refs.append(lit_ref)

        logger.info(
            f"Loaded world model for session {session_id}: "
            f"{len(world_model.hypotheses)} hypotheses, "
            f"{len(world_model.analysis_results)} results, "
            f"{len(world_model.literature_refs)} literature",
        )

        return world_model

    def list_sessions(
        self,
        limit: int = 100,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List available sessions.

        Args:
            limit: Maximum number of sessions to return
            status: Optional status filter (e.g., "running", "completed")

        Returns:
            List of session metadata dictionaries

        """
        query = self.db.collection("sessions").limit(limit)

        if status:
            query = query.where("status", "==", status)

        sessions = []
        for doc in query.stream():
            sessions.append(doc.to_dict())

        return sessions

    def delete_session(self, session_id: str):
        """Delete a session and all its subcollections.

        Args:
            session_id: Session ID to delete

        """
        session_ref = self.db.collection("sessions").document(session_id)

        # Delete subcollections
        self._delete_collection(session_ref.collection("hypotheses"))
        self._delete_collection(session_ref.collection("analysis_results"))
        self._delete_collection(session_ref.collection("literature"))

        # Delete session document
        session_ref.delete()

        logger.info(f"Deleted session {session_id}")

    def _delete_collection(self, collection_ref, batch_size: int = 100):
        """Delete all documents in a collection."""
        docs = collection_ref.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted += 1

        if deleted >= batch_size:
            # Recursively delete remaining documents
            return self._delete_collection(collection_ref, batch_size)

    def update_session_status(self, session_id: str, status: str):
        """Update session status.

        Args:
            session_id: Session ID
            status: New status

        """
        session_ref = self.db.collection("sessions").document(session_id)
        session_ref.update({"status": status})

    def get_hypothesis(self, session_id: str, hypothesis_id: str) -> Hypothesis | None:
        """Get a specific hypothesis.

        Args:
            session_id: Session ID
            hypothesis_id: Hypothesis ID

        Returns:
            Hypothesis instance or None

        """
        hyp_ref = (
            self.db.collection("sessions")
            .document(session_id)
            .collection("hypotheses")
            .document(hypothesis_id)
        )

        hyp_doc = hyp_ref.get()
        if not hyp_doc.exists:
            return None

        return Hypothesis.from_dict(hyp_doc.to_dict())

    def query_hypotheses(
        self,
        session_id: str,
        min_confidence: float | None = None,
        tested: bool | None = None,
    ) -> list[Hypothesis]:
        """Query hypotheses with filters.

        Args:
            session_id: Session ID
            min_confidence: Minimum confidence score
            tested: Filter by tested status

        Returns:
            List of matching Hypothesis instances

        """
        query = self.db.collection("sessions").document(session_id).collection("hypotheses")

        if min_confidence is not None:
            query = query.where("confidence", ">=", min_confidence)

        if tested is not None:
            query = query.where("tested", "==", tested)

        hypotheses = []
        for doc in query.stream():
            hypotheses.append(Hypothesis.from_dict(doc.to_dict()))

        return hypotheses

    def __repr__(self) -> str:
        return f"FirestoreBackend(project={self.project_id})"
