# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Session analytics — Phase 4 M4 state report endpoint.

Provides aggregate session metrics for admin dashboards:
  - Active/terminal session counts by state
  - Average session age and TTL utilization
  - Decision distribution (accept/reject/partial)
  - Telemetry latency summary

Design:
  - Read-only endpoint — no mutations
  - Attorney-scoped access — can only view own firm's analytics
  - No PII in response — aggregates only
"""

from __future__ import annotations

import logging
import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from apps.counselconduit.api.auth import get_current_attorney
from apps.counselconduit.api.sandbox.session import (
    AbstractSessionStore,
    SessionState,
)
from apps.counselconduit.api.sandbox.firestore_session_store import (
    FirestoreSessionStore,
)

logger = logging.getLogger("counselconduit.sandbox.analytics")

router = APIRouter(prefix="/api/sandbox/analytics", tags=["sandbox-analytics"])

AttorneyDep = Annotated[dict[str, Any], Depends(get_current_attorney)]

_store: AbstractSessionStore = FirestoreSessionStore()


# ── Response Models ────────────────────────────────────────────────────


class StateDistribution(BaseModel):
    """Count of sessions per lifecycle state."""

    created: int = 0
    speculating: int = 0
    reviewing: int = 0
    committing: int = 0
    committed: int = 0
    rejected: int = 0
    expired: int = 0
    error: int = 0


class DecisionDistribution(BaseModel):
    """Count of decisions by action type."""

    accept: int = 0
    reject: int = 0
    partial_accept: int = 0


class LatencySummary(BaseModel):
    """Telemetry latency summary (from structured logs)."""

    sample_count: int = 0
    avg_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0


class SessionAnalyticsReport(BaseModel):
    """Aggregate analytics for sandbox sessions."""

    generated_at: float = Field(default_factory=time.time)
    attorney_uid_prefix: str = Field(
        "",
        description="8-char prefix of scoped attorney UID (no PII)",
    )
    total_sessions: int = 0
    active_sessions: int = 0
    terminal_sessions: int = 0
    state_distribution: StateDistribution = Field(default_factory=StateDistribution)
    decision_distribution: DecisionDistribution = Field(
        default_factory=DecisionDistribution,
    )
    avg_session_age_s: float = 0.0
    avg_ttl_utilization_pct: float = 0.0


# ── Terminal states ────────────────────────────────────────────────────

_TERMINAL_STATES = frozenset(
    {
        SessionState.COMMITTED.value,
        SessionState.REJECTED.value,
        SessionState.EXPIRED.value,
        SessionState.ERROR.value,
    }
)


# ── Endpoint ───────────────────────────────────────────────────────────


@router.get("/report", response_model=SessionAnalyticsReport)
async def get_analytics_report(
    attorney: AttorneyDep = None,  # type: ignore[assignment]
) -> SessionAnalyticsReport:
    """Generate session analytics report scoped to the current attorney.

    Returns aggregate metrics without exposing any PII.
    """
    attorney_uid = attorney.get("uid", "")
    if not attorney_uid:
        raise HTTPException(status_code=401, detail="Attorney UID required")

    try:
        # Fetch all sessions for this attorney (active + terminal)
        active_sessions = await _store.list_active_sessions(
            attorney_uid=attorney_uid,
            limit=500,
        )

        report = SessionAnalyticsReport(
            attorney_uid_prefix=attorney_uid[:8],
            total_sessions=len(active_sessions),
        )

        state_dist = StateDistribution()
        now = time.time()
        ages: list[float] = []
        ttl_utilizations: list[float] = []

        for session_data in active_sessions:
            state_value = session_data.get("state", "")

            # Count by state
            if state_value == SessionState.CREATED.value:
                state_dist.created += 1
            elif state_value == SessionState.SPECULATING.value:
                state_dist.speculating += 1
            elif state_value == SessionState.REVIEWING.value:
                state_dist.reviewing += 1
            elif state_value == SessionState.COMMITTING.value:
                state_dist.committing += 1
            elif state_value == SessionState.COMMITTED.value:
                state_dist.committed += 1
            elif state_value == SessionState.REJECTED.value:
                state_dist.rejected += 1
            elif state_value == SessionState.EXPIRED.value:
                state_dist.expired += 1
            elif state_value == SessionState.ERROR.value:
                state_dist.error += 1

            # Track active vs terminal
            if state_value in _TERMINAL_STATES:
                report.terminal_sessions += 1
            else:
                report.active_sessions += 1

            # Compute age and TTL utilization
            created_at = session_data.get("created_at", 0.0)
            ttl = session_data.get("ttl_seconds", 1800)
            if created_at > 0:
                age = now - created_at
                ages.append(age)
                if ttl > 0:
                    ttl_utilizations.append(min(age / ttl * 100, 100.0))

        report.state_distribution = state_dist

        if ages:
            report.avg_session_age_s = round(sum(ages) / len(ages), 1)
        if ttl_utilizations:
            report.avg_ttl_utilization_pct = round(sum(ttl_utilizations) / len(ttl_utilizations), 1)

        # Aggregate decision distribution from session decisions
        decision_dist = DecisionDistribution()
        for session_data in active_sessions:
            session_id = session_data.get("session_id", "")
            if not session_id:
                continue
            try:
                decisions = await _store.get_decisions(session_id)
                for d in decisions:
                    action = d.get("action", "")
                    if action == "accept":
                        decision_dist.accept += 1
                    elif action == "reject":
                        decision_dist.reject += 1
                    elif action == "partial_accept":
                        decision_dist.partial_accept += 1
            except Exception:
                # Non-fatal: skip sessions with inaccessible decisions
                logger.debug(
                    "Could not fetch decisions for session %s",
                    session_id[:8],
                )

        report.decision_distribution = decision_dist

        logger.info(
            "Analytics report generated: %d sessions (%d active, %d terminal)",
            report.total_sessions,
            report.active_sessions,
            report.terminal_sessions,
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to generate analytics report: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Analytics report generation failed",
        ) from e
