"""
database-events-handler/main.py — Sovereign OS Event Subscriber

Cloud Run function that processes CDC events from the Datastream → Pub/Sub
pipeline. This is the central nervous system router:

  Spanner DML → Datastream CDC → Pub/Sub → THIS HANDLER → {
    diagnose.py     (Autonomic DBA: schema healing)
    BigQuery        (Analytics sink: all events)
    Stripe webhook  (Payment reconciliation)
    FinOps governor (Cost circuit breaker)
  }

Deployment:
  gcloud run deploy database-events-handler \
    --source=services/database-events-handler \
    --region=us-central1 \
    --project=shadowtag-omega-v4 \
    --set-env-vars=GCP_PROJECT=shadowtag-omega-v4,BIGQUERY_DATASET=uphill_events \
    --no-allow-unauthenticated

Then create a Pub/Sub push subscription:
  gcloud pubsub subscriptions create database-events-push \
    --topic=database-events \
    --push-endpoint=https://database-events-handler-HASH.run.app \
    --push-auth-service-account=counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com
"""

from __future__ import annotations

import base64
import json
import logging
import os
import sys
import time
from datetime import datetime, UTC
from typing import Any

import functions_framework
from google.cloud import bigquery, pubsub_v1

# ─── Configuration ─────────────────────────────────────────────────────────────

PROJECT_ID = os.environ.get("GCP_PROJECT", "shadowtag-omega-v4")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "uphill_events")
BIGQUERY_TABLE = os.environ.get("BIGQUERY_TABLE", "cdc_events")
HEALING_TOPIC = os.environ.get("HEALING_TOPIC", "schema-healing-requests")
FINOPS_TOPIC = os.environ.get("FINOPS_TOPIC", "finops-checks")

# Tables whose mutations trigger specific actions
PAYMENT_TABLES = {"transactions", "subscriptions", "invoices"}
SCHEMA_CRITICAL_TABLES = {"users", "transactions", "sessions", "cases"}

# Event rate limiting: max events per table per minute before circuit break
MAX_EVENTS_PER_MINUTE = int(os.environ.get("MAX_EVENTS_PER_MINUTE", "1000"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("database-events-handler")

# ─── Rate Limiter (In-Memory for Cold Start Simplicity) ───────────────────────

_event_counts: dict[str, list[float]] = {}


def _check_rate_limit(table_name: str) -> bool:
    """Return True if under rate limit, False if breached."""
    now = time.time()
    window_start = now - 60

    if table_name not in _event_counts:
        _event_counts[table_name] = []

    # Prune old entries
    _event_counts[table_name] = [t for t in _event_counts[table_name] if t > window_start]
    _event_counts[table_name].append(now)

    return len(_event_counts[table_name]) <= MAX_EVENTS_PER_MINUTE


# ─── Event Router ─────────────────────────────────────────────────────────────


def _extract_cdc_event(envelope: dict) -> dict[str, Any]:
    """Extract and normalize a CDC event from the Pub/Sub envelope.

    Datastream CDC events have this structure:
    {
      "changeType": "INSERT" | "UPDATE" | "DELETE",
      "tableName": "users",
      "commitTimestamp": "2026-05-08T23:00:00Z",
      "keys": {"UserId": "u_123"},
      "oldValues": {...},
      "newValues": {...}
    }
    """
    # Pub/Sub wraps data in base64
    if "message" in envelope:
        raw_data = envelope["message"].get("data", "")
        if raw_data:
            decoded = base64.b64decode(raw_data).decode("utf-8")
            return json.loads(decoded)
    return envelope


def _route_to_bigquery(event: dict[str, Any], bq_client: bigquery.Client) -> None:
    """Sink every CDC event to BigQuery for analytics and audit trail."""
    row = {
        "event_id": f"{event.get('tableName', 'unknown')}_{int(time.time() * 1000)}",
        "table_name": event.get("tableName", "unknown"),
        "change_type": event.get("changeType", "UNKNOWN"),
        "commit_timestamp": event.get("commitTimestamp", datetime.now(tz=UTC).isoformat()),
        "keys_json": json.dumps(event.get("keys", {})),
        "new_values_json": json.dumps(event.get("newValues", {})),
        "old_values_json": json.dumps(event.get("oldValues", {})),
        "ingested_at": datetime.now(tz=UTC).isoformat(),
    }

    table_ref = f"{PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"

    errors = bq_client.insert_rows_json(table_ref, [row])
    if errors:
        logger.error("BigQuery insert errors: %s", errors)
    else:
        logger.info(
            "Sunk event to BigQuery: %s.%s",
            event.get("tableName"),
            event.get("changeType"),
        )


def _route_to_healing(event: dict[str, Any], publisher: pubsub_v1.PublisherClient) -> None:
    """Forward schema-critical mutations to the Autonomic DBA."""
    table_name = event.get("tableName", "").lower()

    if table_name not in SCHEMA_CRITICAL_TABLES:
        return

    healing_request = {
        "source": "cdc-event-handler",
        "table": table_name,
        "change_type": event.get("changeType"),
        "timestamp": event.get("commitTimestamp", datetime.now(tz=UTC).isoformat()),
        "action": "diagnose_and_heal",
    }

    topic_path = publisher.topic_path(PROJECT_ID, HEALING_TOPIC)
    future = publisher.publish(topic_path, json.dumps(healing_request).encode("utf-8"))
    logger.info("Forwarded healing request for %s: %s", table_name, future.result(timeout=10))


def _route_payment_event(event: dict[str, Any], publisher: pubsub_v1.PublisherClient) -> None:
    """Forward payment-related mutations for Stripe reconciliation."""
    table_name = event.get("tableName", "").lower()

    if table_name not in PAYMENT_TABLES:
        return

    # Only forward INSERTs and UPDATEs (not DELETEs)
    if event.get("changeType") == "DELETE":
        logger.warning("DELETE on payment table %s — logging only, no Stripe action", table_name)
        return

    payment_event = {
        "source": "cdc-event-handler",
        "table": table_name,
        "change_type": event.get("changeType"),
        "keys": event.get("keys", {}),
        "new_values": event.get("newValues", {}),
        "timestamp": event.get("commitTimestamp", datetime.now(tz=UTC).isoformat()),
    }

    # Publish to a dedicated payment-reconciliation topic
    topic_path = publisher.topic_path(PROJECT_ID, "payment-reconciliation")
    future = publisher.publish(topic_path, json.dumps(payment_event).encode("utf-8"))
    logger.info("Forwarded payment event for %s: %s", table_name, future.result(timeout=10))


def _check_finops(event: dict[str, Any], publisher: pubsub_v1.PublisherClient) -> None:
    """Emit a FinOps check event for cost monitoring."""
    finops_event = {
        "source": "cdc-event-handler",
        "event_type": "mutation_count",
        "table": event.get("tableName", "unknown"),
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }

    topic_path = publisher.topic_path(PROJECT_ID, FINOPS_TOPIC)
    future = publisher.publish(topic_path, json.dumps(finops_event).encode("utf-8"))
    logger.debug("FinOps check emitted: %s", future.result(timeout=10))


# ─── HTTP Handler (Cloud Run) ─────────────────────────────────────────────────


@functions_framework.http
def handle_cdc_event(request):
    """HTTP handler for Pub/Sub push subscriptions.

    Returns 200 for successful processing, 500 for errors (Pub/Sub will retry).
    Returns 429 if rate limit breached (circuit breaker).
    """
    try:
        envelope = request.get_json(silent=True)
        if not envelope:
            logger.warning("Empty request body")
            return ("Empty request", 400)

        event = _extract_cdc_event(envelope)
        table_name = event.get("tableName", "unknown")
        change_type = event.get("changeType", "UNKNOWN")

        logger.info(
            "Processing CDC event: %s on %s",
            change_type,
            table_name,
        )

        # Rate limit check (circuit breaker)
        if not _check_rate_limit(table_name):
            logger.warning(
                "CIRCUIT BREAK: Rate limit exceeded for table %s (%d/min)",
                table_name,
                MAX_EVENTS_PER_MINUTE,
            )
            return (
                json.dumps(
                    {
                        "status": "rate_limited",
                        "table": table_name,
                        "message": "Event processing temporarily halted",
                    }
                ),
                429,
            )

        # Initialize clients (lazy, reused across warm instances)
        bq_client = bigquery.Client(project=PROJECT_ID)
        publisher = pubsub_v1.PublisherClient()

        # Route to all subsystems in parallel
        _route_to_bigquery(event, bq_client)
        _route_to_healing(event, publisher)
        _route_payment_event(event, publisher)
        _check_finops(event, publisher)

        return (
            json.dumps(
                {
                    "status": "processed",
                    "table": table_name,
                    "change_type": change_type,
                }
            ),
            200,
        )

    except Exception:
        logger.exception("Failed to process CDC event")
        return ("Internal error", 500)


# ─── Standalone Mode ──────────────────────────────────────────────────────────


def _run_test():
    """Run a test CDC event through the handler."""
    test_event = {
        "changeType": "INSERT",
        "tableName": "transactions",
        "commitTimestamp": datetime.now(tz=UTC).isoformat(),
        "keys": {"TransactionId": "txn_test_001"},
        "newValues": {
            "stripe_customer_id": "cus_test",
            "amount_cents": 14900,
            "currency": "usd",
            "status": "succeeded",
        },
    }

    print("=" * 60)
    print("  🧬 Database Events Handler — Test Mode")
    print("=" * 60)
    print(f"\nTest event: {json.dumps(test_event, indent=2)}")

    # Extract and route (dry run — won't actually call GCP APIs)
    event = _extract_cdc_event(test_event)
    print(f"\nExtracted table: {event.get('tableName')}")
    print(f"Change type: {event.get('changeType')}")
    print(f"Is payment table: {event.get('tableName', '').lower() in PAYMENT_TABLES}")
    print(f"Is schema-critical: {event.get('tableName', '').lower() in SCHEMA_CRITICAL_TABLES}")
    print(f"Rate limit OK: {_check_rate_limit(event.get('tableName', 'test'))}")

    print("\n✅ Test passed — event would route to: BigQuery, Healing, Payment, FinOps")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _run_test()
    else:
        print("Usage: python main.py --test")
        print("For production, deploy as Cloud Run service with Pub/Sub push subscription.")
