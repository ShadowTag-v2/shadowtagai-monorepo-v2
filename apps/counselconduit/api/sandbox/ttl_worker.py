# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session TTL Expiration Worker — Phase 4 M5.

Cloud Tasks-compatible cron worker that scans for and expires sessions
that have exceeded their TTL. Designed to run as a periodic task via
Google Cloud Tasks (per Queue Doctrine: GCT is the exclusive queue broker).

Architecture:
    Cloud Scheduler → Cloud Tasks → POST /api/sandbox/cron/expire-sessions
    → This worker → FirestoreSessionStore.expire_session()

Design principles:
    - Idempotent — safe to run multiple times for same session
    - Batched — processes up to MAX_BATCH sessions per invocation
    - Audited — every expiration logged to structured logger
    - No PII — only session_id prefix in logs
    - Cloud Tasks header verification (X-CloudTasks-QueueName)
"""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from apps.counselconduit.api.sandbox.firestore_session_store import (
  FirestoreSessionStore,
)
from apps.counselconduit.api.sandbox.session import SessionState

logger = logging.getLogger("counselconduit.sandbox.ttl_worker")

router = APIRouter(prefix="/api/sandbox/cron", tags=["sandbox-cron"])

# Maximum sessions to expire per invocation (Cloud Tasks timeout-safe)
MAX_BATCH = 100

# States that are eligible for TTL expiration
_EXPIRABLE_STATES = frozenset(
  {
    SessionState.CREATED.value,
    SessionState.SPECULATING.value,
    SessionState.REVIEWING.value,
    SessionState.COMMITTING.value,
  }
)

_store = FirestoreSessionStore()


# ── Response Models ────────────────────────────────────────────────────


class ExpirationReport(BaseModel):
  """Report from a TTL expiration sweep."""

  scanned: int = 0
  expired: int = 0
  already_terminal: int = 0
  errors: int = 0
  duration_ms: float = 0.0
  timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# ── Worker Endpoint ────────────────────────────────────────────────────


@router.post("/expire-sessions", response_model=ExpirationReport)
async def expire_sessions_cron(
  x_cloudtasks_queuename: str | None = Header(None, alias="X-CloudTasks-QueueName"),
  x_appengine_cron: str | None = Header(None, alias="X-Appengine-Cron"),
) -> ExpirationReport:
  """Expire sandbox sessions that have exceeded their TTL.

  This endpoint is designed to be called by Cloud Tasks or Cloud Scheduler.
  It scans all non-terminal sessions and expires those past their TTL.

  Security:
      - Verifies Cloud Tasks or Cloud Scheduler headers
      - No user authentication required (machine-to-machine only)
      - All expirations are logged for audit trail
  """
  # Verify this is a legitimate Cloud Tasks/Scheduler invocation
  # In production, Cloud Run verifies these headers. In dev, allow bypass.
  is_authorized = (
    x_cloudtasks_queuename is not None or x_appengine_cron == "true" or _is_local_dev()
  )
  if not is_authorized:
    raise HTTPException(
      status_code=403,
      detail="This endpoint is only accessible via Cloud Tasks or Cloud Scheduler",
    )

  start = time.perf_counter()
  report = ExpirationReport()

  try:
    # Fetch all non-terminal sessions (up to MAX_BATCH)
    sessions = await _fetch_expirable_sessions()
    report.scanned = len(sessions)

    now = time.time()
    for session_data in sessions:
      session_id = session_data.get("session_id", "")
      state = session_data.get("state", "")
      created_at = session_data.get("created_at", 0.0)
      ttl_seconds = session_data.get("ttl_seconds", 1800)

      if not session_id:
        continue

      # Check if already terminal
      if state not in _EXPIRABLE_STATES:
        report.already_terminal += 1
        continue

      # Check TTL
      age = now - created_at
      if age <= ttl_seconds:
        continue  # Not expired yet

      # Expire the session
      try:
        await _store.expire_session(session_id)
        report.expired += 1
        logger.info(
          "TTL expired session %s… (age=%.0fs, ttl=%ds, state=%s)",
          session_id[:8],
          age,
          ttl_seconds,
          state,
        )
      except Exception:
        report.errors += 1
        logger.warning(
          "Failed to expire session %s…",
          session_id[:8],
          exc_info=True,
        )

  except Exception as e:
    logger.exception("TTL expiration sweep failed: %s", e)
    raise HTTPException(
      status_code=500,
      detail="TTL expiration sweep failed",
    ) from e

  report.duration_ms = round((time.perf_counter() - start) * 1000, 2)

  logger.info(
    "TTL sweep complete: scanned=%d expired=%d errors=%d (%.0fms)",
    report.scanned,
    report.expired,
    report.errors,
    report.duration_ms,
  )

  return report


# ── Internal ───────────────────────────────────────────────────────────


async def _fetch_expirable_sessions() -> list[dict[str, Any]]:
  """Fetch sessions that could potentially be expired.

  Queries Firestore for sessions in non-terminal states, limited
  to MAX_BATCH for Cloud Tasks timeout safety.
  """
  query = _store.db.collection(FirestoreSessionStore.COLLECTION)
  query = query.where(
    "state",
    "in",
    list(_EXPIRABLE_STATES),
  )
  query = query.limit(MAX_BATCH)
  docs = await query.get()
  return [doc.to_dict() for doc in docs]


def _is_local_dev() -> bool:
  """Check if running in local development mode."""
  import os

  return os.environ.get("K_SERVICE") is None
