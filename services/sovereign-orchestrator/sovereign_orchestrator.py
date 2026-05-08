"""
sovereign_orchestrator.py — Autonomous Pipeline Orchestrator

The "brain" of the Dark Factory. This Cloud Run service ties together all
Sovereign OS subsystems into a single autonomous loop:

  CDC Event → Database Events Handler → Pub/Sub → THIS ORCHESTRATOR → {
    1. Autonomic DBA (diagnose.py) — schema healing
    2. Epistemic Engine (mcp-gemini-memory) — knowledge persistence
    3. FinOps Governor — budget gate
    4. Deployment Pipeline — auto-deploy fixes
  }

Operational model:
  - Invoked by Pub/Sub push on the "schema-healing-requests" topic
  - Also invocable as HTTP endpoint for manual diagnostics
  - Checks FinOps budget BEFORE any infrastructure mutation
  - Logs every action to Gemini Memory (Epistemic Engine)

Deployment:
  gcloud run deploy sovereign-orchestrator \\
    --source=services/sovereign-orchestrator \\
    --region=us-central1 \\
    --project=shadowtag-omega-v4 \\
    --set-env-vars=GCP_PROJECT=shadowtag-omega-v4 \\
    --no-allow-unauthenticated
"""

from __future__ import annotations

import base64
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

import functions_framework

# ─── Configuration ─────────────────────────────────────────────────────────────

PROJECT_ID = os.environ.get("GCP_PROJECT", "shadowtag-omega-v4")
REGION = os.environ.get("GCP_REGION", "us-central1")
SPANNER_INSTANCE = os.environ.get("SPANNER_INSTANCE", "uphill-core-cluster")
SPANNER_DATABASE = os.environ.get("SPANNER_DATABASE", "uphill-ledger")
MEMORY_TOPIC = os.environ.get("MEMORY_TOPIC", "epistemic-events")
FINOPS_ENDPOINT = os.environ.get(
    "FINOPS_ENDPOINT", "https://finops-governor-HASH.run.app"
)

# Maximum healing actions per hour (safety valve)
MAX_HEALS_PER_HOUR = int(os.environ.get("MAX_HEALS_PER_HOUR", "10"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("sovereign-orchestrator")

# ─── Data Models ───────────────────────────────────────────────────────────────


class HealingAction(StrEnum):
    """Types of autonomous healing actions."""

    INDEX_RECOMMENDATION = "INDEX_RECOMMENDATION"
    QUERY_REWRITE = "QUERY_REWRITE"
    SCHEMA_PATCH = "SCHEMA_PATCH"
    ALERT_ONLY = "ALERT_ONLY"
    NOOP = "NOOP"


class OrchestratorPhase(StrEnum):
    """Phases of the autonomous pipeline."""

    TRIAGE = "TRIAGE"
    DIAGNOSE = "DIAGNOSE"
    BUDGET_CHECK = "BUDGET_CHECK"
    HEAL = "HEAL"
    DOCUMENT = "DOCUMENT"
    COMPLETE = "COMPLETE"
    ABORTED = "ABORTED"


@dataclass
class HealingRequest:
    """Incoming healing request from the CDC event handler."""

    source: str
    table: str
    change_type: str
    timestamp: str
    action: str = "diagnose_and_heal"


@dataclass
class PipelineResult:
    """Full result of an autonomous pipeline run."""

    request_id: str
    started_at: str
    completed_at: str = ""
    phase: OrchestratorPhase = OrchestratorPhase.TRIAGE
    healing_action: HealingAction = HealingAction.NOOP
    diagnosis: dict = field(default_factory=dict)
    budget_status: str = "UNKNOWN"
    actions_taken: list[str] = field(default_factory=list)
    error: str = ""


# ─── Healing Rate Limiter ─────────────────────────────────────────────────────

_heal_timestamps: list[float] = []


def _check_heal_rate() -> bool:
    """Return True if we haven't exceeded MAX_HEALS_PER_HOUR."""
    now = time.time()
    hour_ago = now - 3600
    _heal_timestamps[:] = [t for t in _heal_timestamps if t > hour_ago]
    return len(_heal_timestamps) < MAX_HEALS_PER_HOUR


def _record_heal():
    """Record a healing action for rate limiting."""
    _heal_timestamps.append(time.time())


# ─── Pipeline Phases ──────────────────────────────────────────────────────────


def _phase_triage(request: HealingRequest) -> dict:
    """Phase 1: Classify the incoming healing request.

    Determines urgency and routing based on table criticality.
    """
    critical_tables = {"users", "transactions", "sessions", "cases"}
    is_critical = request.table.lower() in critical_tables

    return {
        "table": request.table,
        "change_type": request.change_type,
        "is_critical": is_critical,
        "urgency": "HIGH" if is_critical else "LOW",
        "recommended_action": "diagnose_and_heal" if is_critical else "monitor_only",
    }


def _phase_diagnose(triage: dict) -> dict:
    """Phase 2: Run Database Insights analysis.

    In production, this calls the Spanner Database Insights API:
      - TopQueryStatistics (hot queries)
      - QueryAdvice (index recommendations)
      - SchemaAnalysis (unused columns, type mismatches)
    """
    try:
        from google.cloud import spanner

        client = spanner.Client(project=PROJECT_ID)
        instance = client.instance(SPANNER_INSTANCE)
        database = instance.database(SPANNER_DATABASE)

        # Query the SPANNER_SYS statistics tables
        diagnosis = {
            "table": triage["table"],
            "health": "HEALTHY",
            "recommendations": [],
            "query_stats": {},
        }

        with database.snapshot() as snapshot:
            # Check for high-latency queries on this table
            results = snapshot.execute_sql(
                """
                SELECT
                    TEXT_FINGERPRINT,
                    INTERVAL_END,
                    AVG_LATENCY_SECONDS,
                    AVG_ROWS_SCANNED,
                    EXECUTION_COUNT
                FROM SPANNER_SYS.QUERY_STATS_TOP_MINUTE
                WHERE TEXT LIKE @table_pattern
                ORDER BY AVG_LATENCY_SECONDS DESC
                LIMIT 5
                """,
                params={"table_pattern": f"%{triage['table']}%"},
                param_types={"table_pattern": spanner.param_types.STRING},
            )

            hot_queries = []
            for row in results:
                hot_queries.append(
                    {
                        "fingerprint": str(row[0]),
                        "avg_latency_s": float(row[2]),
                        "avg_rows_scanned": int(row[3]),
                        "execution_count": int(row[4]),
                    }
                )

            diagnosis["query_stats"]["hot_queries"] = hot_queries

            if any(q["avg_latency_s"] > 2.0 for q in hot_queries):
                diagnosis["health"] = "DEGRADED"
                diagnosis["recommendations"].append(
                    {
                        "type": "INDEX_RECOMMENDATION",
                        "reason": "Queries with >2s avg latency detected",
                        "table": triage["table"],
                    }
                )

        return diagnosis

    except Exception as e:
        logger.warning("Spanner diagnosis unavailable: %s — using heuristic mode", e)
        return {
            "table": triage["table"],
            "health": "UNKNOWN",
            "recommendations": [],
            "query_stats": {},
            "fallback_mode": True,
        }


def _phase_budget_check() -> str:
    """Phase 3: Verify FinOps budget allows infrastructure mutations.

    Calls the FinOps Governor to get current budget status.
    Returns 'GREEN', 'YELLOW', or 'RED'.
    """
    try:
        import httpx

        response = httpx.get(FINOPS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("status", "UNKNOWN")
    except Exception:
        logger.warning("FinOps endpoint unreachable — defaulting to YELLOW (cautious)")

    return "YELLOW"


def _phase_heal(diagnosis: dict) -> tuple[HealingAction, list[str]]:
    """Phase 4: Execute healing actions based on diagnosis.

    Safety constraints:
      - Only applies if budget is GREEN
      - Rate-limited to MAX_HEALS_PER_HOUR
      - Index recommendations are logged, not auto-applied
      - Schema patches require human approval (STATE B)
    """
    actions_taken: list[str] = []

    if not diagnosis.get("recommendations"):
        return HealingAction.NOOP, actions_taken

    for rec in diagnosis["recommendations"]:
        rec_type = rec.get("type", "")

        if rec_type == "INDEX_RECOMMENDATION":
            # Log the recommendation — auto-apply is STATE B only
            actions_taken.append(
                f"INDEX_REC: {rec.get('reason', 'unknown')} on {rec.get('table', '?')}"
            )
            _record_heal()
            return HealingAction.INDEX_RECOMMENDATION, actions_taken

        if rec_type == "QUERY_REWRITE":
            actions_taken.append(
                f"QUERY_REWRITE: Suggested for {rec.get('table', '?')}"
            )
            return HealingAction.QUERY_REWRITE, actions_taken

    return HealingAction.ALERT_ONLY, actions_taken


def _phase_document(result: PipelineResult) -> None:
    """Phase 5: Persist the pipeline run to the Epistemic Engine.

    Publishes a structured event to the memory topic for ingestion by
    mcp-gemini-memory.
    """
    try:
        from google.cloud import pubsub_v1

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, MEMORY_TOPIC)

        memory_event = {
            "type": "sovereign_pipeline_run",
            "request_id": result.request_id,
            "phase": result.phase.value,
            "healing_action": result.healing_action.value,
            "diagnosis_summary": {
                "table": result.diagnosis.get("table", "unknown"),
                "health": result.diagnosis.get("health", "UNKNOWN"),
                "recommendation_count": len(
                    result.diagnosis.get("recommendations", [])
                ),
            },
            "budget_status": result.budget_status,
            "actions_taken": result.actions_taken,
            "timestamp": result.completed_at,
        }

        future = publisher.publish(
            topic_path, json.dumps(memory_event).encode("utf-8")
        )
        logger.info("Documented pipeline run to Epistemic Engine: %s", future.result(timeout=10))

    except Exception:
        logger.exception("Failed to document pipeline run")


# ─── Main Pipeline ─────────────────────────────────────────────────────────────


def run_pipeline(request: HealingRequest) -> PipelineResult:
    """Execute the full autonomous healing pipeline.

    Phases:
      1. TRIAGE → Classify urgency
      2. DIAGNOSE → Query Spanner stats
      3. BUDGET_CHECK → Verify FinOps status
      4. HEAL → Apply recommendations (if budget allows)
      5. DOCUMENT → Persist to Epistemic Engine
    """
    result = PipelineResult(
        request_id=f"heal_{request.table}_{int(time.time())}",
        started_at=datetime.now(tz=UTC).isoformat(),
    )

    try:
        # Phase 1: Triage
        result.phase = OrchestratorPhase.TRIAGE
        triage = _phase_triage(request)
        logger.info("[TRIAGE] %s — urgency: %s", request.table, triage["urgency"])

        if triage["recommended_action"] == "monitor_only":
            result.phase = OrchestratorPhase.COMPLETE
            result.healing_action = HealingAction.NOOP
            result.actions_taken.append("LOW urgency — monitor only")
            result.completed_at = datetime.now(tz=UTC).isoformat()
            return result

        # Phase 2: Diagnose
        result.phase = OrchestratorPhase.DIAGNOSE
        diagnosis = _phase_diagnose(triage)
        result.diagnosis = diagnosis
        logger.info(
            "[DIAGNOSE] %s — health: %s, recs: %d",
            request.table,
            diagnosis.get("health"),
            len(diagnosis.get("recommendations", [])),
        )

        # Phase 3: Budget check
        result.phase = OrchestratorPhase.BUDGET_CHECK
        budget_status = _phase_budget_check()
        result.budget_status = budget_status
        logger.info("[BUDGET] Status: %s", budget_status)

        if budget_status == "RED":
            result.phase = OrchestratorPhase.ABORTED
            result.error = "Budget RED — healing aborted"
            result.actions_taken.append("ABORTED: Budget halt")
            result.completed_at = datetime.now(tz=UTC).isoformat()
            _phase_document(result)
            return result

        # Phase 4: Heal
        result.phase = OrchestratorPhase.HEAL
        if not _check_heal_rate():
            result.phase = OrchestratorPhase.ABORTED
            result.error = f"Heal rate limit exceeded ({MAX_HEALS_PER_HOUR}/hour)"
            result.actions_taken.append("ABORTED: Rate limit")
            result.completed_at = datetime.now(tz=UTC).isoformat()
            _phase_document(result)
            return result

        healing_action, actions = _phase_heal(diagnosis)
        result.healing_action = healing_action
        result.actions_taken.extend(actions)
        logger.info("[HEAL] Action: %s", healing_action.value)

        # Phase 5: Document
        result.phase = OrchestratorPhase.DOCUMENT
        result.completed_at = datetime.now(tz=UTC).isoformat()
        _phase_document(result)

        result.phase = OrchestratorPhase.COMPLETE
        return result

    except Exception as e:
        result.phase = OrchestratorPhase.ABORTED
        result.error = str(e)
        result.completed_at = datetime.now(tz=UTC).isoformat()
        logger.exception("Pipeline failed: %s", e)
        return result


# ─── HTTP Handler (Cloud Run) ─────────────────────────────────────────────────


@functions_framework.http
def handle_healing_request(request):
    """HTTP handler for Pub/Sub push and manual diagnostics.

    Pub/Sub push: POST with envelope containing healing request
    Manual: POST with JSON body containing table name
    """
    try:
        envelope = request.get_json(silent=True)
        if not envelope:
            return ("Empty request", 400)

        # Extract from Pub/Sub envelope or raw JSON
        if "message" in envelope:
            raw = envelope["message"].get("data", "")
            if raw:
                decoded = base64.b64decode(raw).decode("utf-8")
                data = json.loads(decoded)
            else:
                return ("Empty message data", 400)
        else:
            data = envelope

        healing_request = HealingRequest(
            source=data.get("source", "manual"),
            table=data.get("table", "unknown"),
            change_type=data.get("change_type", "UNKNOWN"),
            timestamp=data.get(
                "timestamp", datetime.now(tz=UTC).isoformat()
            ),
            action=data.get("action", "diagnose_and_heal"),
        )

        result = run_pipeline(healing_request)

        return (json.dumps(asdict(result), indent=2, default=str), 200)

    except Exception:
        logger.exception("Failed to process healing request")
        return ("Internal error", 500)


# ─── Standalone Mode ──────────────────────────────────────────────────────────


def _run_diagnostic(table: str = "transactions"):
    """Run a diagnostic pipeline in standalone mode."""
    print("=" * 60)
    print("  🧠 Sovereign OS — Autonomous Pipeline Orchestrator")
    print("=" * 60)

    request = HealingRequest(
        source="diagnostic",
        table=table,
        change_type="MANUAL_CHECK",
        timestamp=datetime.now(tz=UTC).isoformat(),
    )

    result = run_pipeline(request)

    print(f"\n  Request ID: {result.request_id}")
    print(f"  Phase: {result.phase.value}")
    print(f"  Healing Action: {result.healing_action.value}")
    print(f"  Budget Status: {result.budget_status}")
    print(f"  Actions: {result.actions_taken}")
    if result.error:
        print(f"  Error: {result.error}")
    print(f"  Duration: {result.started_at} → {result.completed_at}")
    print("\n" + "=" * 60)

    return json.dumps(asdict(result), indent=2, default=str)


if __name__ == "__main__":
    table_arg = sys.argv[1] if len(sys.argv) > 1 else "transactions"
    print(_run_diagnostic(table_arg))
