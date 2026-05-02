# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Firestore persistence for SweepResult and PairSession reports.

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

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from circuit_breaker.telemetry_bridge import default_registry as _cb_registry

logger = logging.getLogger(__name__)

# Register the Firestore circuit breaker with production-tuned thresholds:
#   - 3 consecutive failures → OPEN (Firestore is usually fast, 3 failures = real outage)
#   - 120s reset timeout (GCP control plane recovery window)
_firestore_breaker = _cb_registry.get_or_create(
    "firestore", failure_threshold=3, reset_timeout_s=120.0
)

# Rate limiting constants
RATELIMIT_FILE = Path(os.environ.get("BEADS_DIR", ".beads")) / "sweep_ratelimit.json"
MAX_SWEEPS_PER_HOUR = int(os.environ.get("MAX_SWEEPS_PER_HOUR", "4"))
TTL_DAYS = int(os.environ.get("SWEEP_TTL_DAYS", "30"))

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
    # Circuit breaker gate — fail fast if Firestore is known-down
    if not _firestore_breaker.allow_request():
        logger.warning("Circuit breaker OPEN for firestore — SweepResult not persisted")
        return None

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
        _firestore_breaker.record_success()
        logger.info("SweepResult persisted to Firestore: %s/%s", COLLECTION, doc_id)
        return doc_id
    except Exception as exc:
        _firestore_breaker.record_failure()
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
    if not _firestore_breaker.allow_request():
        logger.warning("Circuit breaker OPEN for firestore — query_recent_sweeps skipped")
        return []

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
        _firestore_breaker.record_success()
        return results
    except Exception as exc:
        _firestore_breaker.record_failure()
        logger.error("Firestore query failed: %s", exc)
        return []


def get_sweep_by_id(doc_id: str) -> dict[str, Any] | None:
    """Retrieve a single sweep result by its document ID."""
    if not _firestore_breaker.allow_request():
        logger.warning("Circuit breaker OPEN for firestore — get_sweep_by_id skipped")
        return None

    client = _get_firestore_client()
    if client is None:
        return None

    try:
        doc = client.collection(COLLECTION).document(doc_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["doc_id"] = doc.id
            _firestore_breaker.record_success()
            return data
        _firestore_breaker.record_success()
        return None
    except Exception as exc:
        _firestore_breaker.record_failure()
        logger.error("Firestore get failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------


def _load_rate_state() -> dict[str, Any]:
    """Load the rate limit state from disk."""
    try:
        if RATELIMIT_FILE.exists():
            return json.loads(RATELIMIT_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        pass
    return {"timestamps": []}


def _save_rate_state(state: dict[str, Any]) -> None:
    """Persist rate limit state to disk."""
    try:
        RATELIMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        RATELIMIT_FILE.write_text(json.dumps(state, default=str))
    except OSError:
        pass  # Fail-open


def check_sweep_rate_limit() -> bool:
    """Check if a new research sweep is allowed under rate limiting.

    Uses a sliding window of MAX_SWEEPS_PER_HOUR (default 4).

    Returns:
        True if the sweep is allowed, False if rate-limited.
    """
    state = _load_rate_state()
    now = time.time()
    one_hour_ago = now - 3600.0

    # Prune timestamps older than 1 hour
    recent = [ts for ts in state.get("timestamps", []) if ts > one_hour_ago]

    if len(recent) >= MAX_SWEEPS_PER_HOUR:
        logger.warning(
            "Research sweep rate-limited: %d/%d sweeps in the last hour",
            len(recent),
            MAX_SWEEPS_PER_HOUR,
        )
        return False

    return True


def record_sweep_invocation() -> None:
    """Record that a sweep was just invoked (for rate limiting)."""
    state = _load_rate_state()
    now = time.time()
    one_hour_ago = now - 3600.0

    recent = [ts for ts in state.get("timestamps", []) if ts > one_hour_ago]
    recent.append(now)
    state["timestamps"] = recent
    _save_rate_state(state)


# ---------------------------------------------------------------------------
# TTL Enforcement (30-day retention)
# ---------------------------------------------------------------------------


def enforce_ttl(*, ttl_days: int | None = None) -> int:
    """Delete sweep_results documents older than TTL_DAYS.

    Args:
        ttl_days: Override the default TTL_DAYS (30).

    Returns:
        Number of documents deleted.
    """
    if not _firestore_breaker.allow_request():
        logger.warning("Circuit breaker OPEN for firestore — TTL enforcement skipped")
        return 0

    client = _get_firestore_client()
    if client is None:
        return 0

    cutoff_days = ttl_days if ttl_days is not None else TTL_DAYS
    cutoff_epoch = time.time() - (cutoff_days * 86400)

    deleted = 0
    try:
        # Query documents older than the cutoff using the epoch timestamp
        old_docs = (
            client.collection(COLLECTION)
            .where("created_at_epoch", "<", cutoff_epoch)
            .limit(500)  # Batch size to avoid memory issues
            .stream()
        )

        for doc in old_docs:
            doc.reference.delete()
            deleted += 1

        if deleted > 0:
            logger.info("TTL enforcement: deleted %d documents older than %d days", deleted, cutoff_days)
    except Exception as exc:
        logger.error("TTL enforcement failed: %s", exc)

    return deleted


# ---------------------------------------------------------------------------
# Pair Programming Session Persistence
# ---------------------------------------------------------------------------

PAIR_SESSION_COLLECTION = "pair_sessions"


def persist_pair_session(
    session: Any,
    *,
    messages: list[dict[str, str]] | None = None,
    status: str = "completed",
) -> str | None:
    """Persist a GeminiPairProgrammer PairSession to Firestore.

    Args:
        session: A ``PairSession`` from ``gemini_bridge``.
        messages: Optional conversation messages for audit trail.
        status: Completion status.

    Returns:
        The Firestore document ID, or None if persistence failed/disabled.
    """
    if not _firestore_breaker.allow_request():
        logger.warning("Circuit breaker OPEN for firestore — PairSession not persisted")
        return None

    client = _get_firestore_client()
    if client is None:
        logger.info("Firestore persistence disabled — PairSession not persisted")
        return None

    doc_data = {
        "session_id": getattr(session, "session_id", ""),
        "model": getattr(session, "model", ""),
        "turn_count": getattr(session, "turn_count", 0),
        "total_tokens": getattr(session, "total_tokens", 0),
        "duration_seconds": getattr(session, "duration_seconds", 0.0),
        "interaction_chain": getattr(session, "interaction_chain", []),
        "message_count": len(messages) if messages else 0,
        "status": status,
        "created_at_epoch": time.time(),
        "daemon_pid": os.getpid(),
    }

    # Store message summaries (not full content, for security)
    if messages:
        doc_data["message_roles"] = [m.get("role", "unknown") for m in messages[:50]]

    try:
        from google.cloud import firestore as fs  # type: ignore[import-untyped]

        doc_data["created_at"] = fs.SERVER_TIMESTAMP
        _, doc_ref = client.collection(PAIR_SESSION_COLLECTION).add(doc_data)
        doc_id = doc_ref.id
        _firestore_breaker.record_success()
        logger.info("PairSession persisted to Firestore: %s/%s", PAIR_SESSION_COLLECTION, doc_id)
        return doc_id
    except Exception as exc:
        _firestore_breaker.record_failure()
        logger.error("PairSession persist failed: %s", exc)
        return None


def query_recent_sessions(
    *,
    limit: int = 10,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Query recent pair programming sessions from Firestore.

    Args:
        limit: Maximum number of results.
        status: Optional filter by status.

    Returns:
        List of session dicts, most recent first.
    """
    if not _firestore_breaker.allow_request():
        logger.warning("Circuit breaker OPEN for firestore — query_recent_sessions skipped")
        return []

    client = _get_firestore_client()
    if client is None:
        return []

    try:
        query = client.collection(PAIR_SESSION_COLLECTION)
        if status:
            query = query.where("status", "==", status)
        query = query.order_by("created_at_epoch", direction="DESCENDING").limit(limit)

        results: list[dict[str, Any]] = []
        for doc in query.stream():
            data = doc.to_dict()
            data["doc_id"] = doc.id
            results.append(data)
        _firestore_breaker.record_success()
        return results
    except Exception as exc:
        _firestore_breaker.record_failure()
        logger.error("Firestore session query failed: %s", exc)
        return []
