# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Firestore persistence for SweepResult reports.

Schema (collection: ``sweep_results``):
    doc_id:             Auto-generated or ``{session_id}_{timestamp}``
    query:              str  — original research query
    report_text:        str  — markdown report body
    duration_seconds:   float
    interaction_id:     str  — for follow-up questions
    agent:              str  — which Deep Research agent ran
    image_count:        int  — number of generated visualizations
    pipeline_mode:      str  — 'research_sweep' | 'pair_programming' | 'hybrid'
    created_at:         timestamp (server)
    session_id:         str  — KAIROS daemon session ID
    daemon_pid:         int  — PID of the daemon that produced the result
    status:             str  — 'completed' | 'failed' | 'partial'

Indexes:
    - created_at DESC (default ordering for dashboard)
    - pipeline_mode + created_at DESC (filter by mode)
    - status + created_at DESC (filter by health)

Usage::

    from speculation_engine.firestore_persistence import persist_sweep_result, query_recent_sweeps
    from speculation_engine.gemini_bridge import SweepResult

    result = SweepResult(query="Legal AI landscape", report_text="...", duration_seconds=120.0)
    doc_id = persist_sweep_result(result, session_id="kairos-abc123")

    recent = query_recent_sweeps(limit=10)
    for sweep in recent:
        print(sweep["query"], sweep["duration_seconds"])
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# Collection name in Firestore
COLLECTION = "sweep_results"


def _get_firestore_client() -> Any:
    """Lazy-load Firestore client via ADC.

    Returns None if google-cloud-firestore is not installed or auth fails.
    """
    try:
        from google.cloud import firestore  # type: ignore[import-untyped]

        project = os.environ.get("GCP_PROJECT", "shadowtag-omega-v4")
        return firestore.Client(project=project)
    except ImportError:
        logger.debug("google-cloud-firestore not installed — Firestore persistence disabled")
        return None
    except Exception as exc:
        logger.warning("Firestore client init failed: %s", exc)
        return None


def sweep_result_to_doc(
    result: Any,
    *,
    session_id: str = "",
    pipeline_mode: str = "research_sweep",
    status: str = "completed",
) -> dict[str, Any]:
    """Convert a SweepResult dataclass into a Firestore document dict.

    Args:
        result: A ``SweepResult`` from ``gemini_bridge``.
        session_id: KAIROS daemon session identifier.
        pipeline_mode: Pipeline mode string.
        status: Completion status.

    Returns:
        Dict suitable for Firestore ``set()`` / ``add()``.
    """
    return {
        "query": getattr(result, "query", ""),
        "report_text": getattr(result, "report_text", ""),
        "duration_seconds": getattr(result, "duration_seconds", 0.0),
        "interaction_id": getattr(result, "interaction_id", ""),
        "agent": getattr(result, "agent", ""),
        "image_count": len(getattr(result, "images", [])),
        "pipeline_mode": pipeline_mode,
        "created_at_epoch": time.time(),
        "session_id": session_id,
        "daemon_pid": os.getpid(),
        "status": status,
    }


def persist_sweep_result(
    result: Any,
    *,
    session_id: str = "",
    pipeline_mode: str = "research_sweep",
    status: str = "completed",
) -> str | None:
    """Persist a SweepResult to Firestore.

    Args:
        result: A ``SweepResult`` from ``gemini_bridge``.
        session_id: KAIROS daemon session identifier.
        pipeline_mode: Pipeline mode.
        status: Completion status.

    Returns:
        The Firestore document ID, or None if persistence failed/disabled.
    """
    client = _get_firestore_client()
    if client is None:
        logger.info("Firestore persistence disabled — SweepResult not persisted")
        return None

    doc_data = sweep_result_to_doc(
        result,
        session_id=session_id,
        pipeline_mode=pipeline_mode,
        status=status,
    )

    try:
        # Server-side timestamp
        from google.cloud import firestore as fs  # type: ignore[import-untyped]

        doc_data["created_at"] = fs.SERVER_TIMESTAMP

        _, doc_ref = client.collection(COLLECTION).add(doc_data)
        doc_id = doc_ref.id
        logger.info("SweepResult persisted to Firestore: %s/%s", COLLECTION, doc_id)
        return doc_id
    except Exception as exc:
        logger.error("Firestore persist failed: %s", exc)
        return None


def query_recent_sweeps(
    *,
    limit: int = 10,
    pipeline_mode: str | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Query recent sweep results from Firestore.

    Args:
        limit: Maximum number of results.
        pipeline_mode: Optional filter by pipeline mode.
        status: Optional filter by status.

    Returns:
        List of sweep result dicts, most recent first.
    """
    client = _get_firestore_client()
    if client is None:
        return []

    try:
        query = client.collection(COLLECTION)

        if pipeline_mode:
            query = query.where("pipeline_mode", "==", pipeline_mode)
        if status:
            query = query.where("status", "==", status)

        query = query.order_by("created_at_epoch", direction="DESCENDING").limit(limit)

        results: list[dict[str, Any]] = []
        for doc in query.stream():
            data = doc.to_dict()
            data["doc_id"] = doc.id
            results.append(data)
        return results
    except Exception as exc:
        logger.error("Firestore query failed: %s", exc)
        return []


def get_sweep_by_id(doc_id: str) -> dict[str, Any] | None:
    """Retrieve a single sweep result by its document ID."""
    client = _get_firestore_client()
    if client is None:
        return None

    try:
        doc = client.collection(COLLECTION).document(doc_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["doc_id"] = doc.id
            return data
        return None
    except Exception as exc:
        logger.error("Firestore get failed: %s", exc)
        return None
