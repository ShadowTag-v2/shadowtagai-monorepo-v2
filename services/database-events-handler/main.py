"""
Cloud Run Pub/Sub Handler — Real-time UI Sync via Datastream CDC.

Receives Pub/Sub push messages from the `database-events` topic
(fed by Datastream CDC from Spanner), parses the change event,
and triggers downstream actions (cache invalidation, WebSocket push, etc.).

Deployment:
  gcloud run deploy database-events-handler \
    --source=. \
    --region=us-central1 \
    --project=shadowtag-omega-v4 \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=shadowtag-omega-v4" \
    --allow-unauthenticated=false

Pub/Sub Push Subscription:
  gcloud pubsub subscriptions create database-events-push \
    --topic=database-events \
    --push-endpoint=https://database-events-handler-HASH.run.app \
    --ack-deadline=30 \
    --project=shadowtag-omega-v4
"""

import base64
import json
import logging
import os
from datetime import datetime, UTC

from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database-events-handler")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")


@app.route("/", methods=["POST"])
def handle_database_event():
    """Process a Pub/Sub push message from the database-events topic.

    Datastream CDC events contain:
    - changeType: INSERT | UPDATE | DELETE
    - tableName: the Spanner table that changed
    - rowData: the affected row as JSON
    - commitTimestamp: when the change was committed
    """
    envelope = request.get_json(silent=True)
    if not envelope:
        logger.warning("Empty request body")
        return ("Bad Request: no Pub/Sub message", 400)

    if not isinstance(envelope, dict) or "message" not in envelope:
        logger.warning("Invalid Pub/Sub envelope: %s", type(envelope))
        return ("Bad Request: invalid format", 400)

    pubsub_message = envelope["message"]

    # Decode the base64-encoded data
    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        raw_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
    else:
        logger.warning("No data field in Pub/Sub message")
        return ("Bad Request: missing data", 400)

    try:
        event = json.loads(raw_data)
    except json.JSONDecodeError:
        logger.error("Failed to parse event JSON: %s", raw_data[:200])
        return ("Bad Request: invalid JSON", 400)

    # Extract CDC event fields
    change_type = event.get("changeType", "UNKNOWN")
    table_name = event.get("tableName", "unknown")
    commit_ts = event.get("commitTimestamp", datetime.now(UTC).isoformat())
    row_data = event.get("rowData", {})

    logger.info(
        "CDC Event: %s on %s at %s | keys=%s",
        change_type,
        table_name,
        commit_ts,
        list(row_data.keys())[:5],
    )

    # Route by table name
    handler = TABLE_HANDLERS.get(table_name, _handle_generic)
    try:
        handler(change_type, row_data, commit_ts)
    except Exception:
        logger.exception("Handler error for %s.%s", table_name, change_type)
        # Return 200 to avoid Pub/Sub retry storm on persistent errors
        # Errors are logged and can be alerted on via Cloud Monitoring

    return ("OK", 200)


def _handle_transactions(change_type: str, row_data: dict, commit_ts: str) -> None:
    """Handle Spanner `transactions` table changes.

    When Stripe writes a payment success row, this triggers:
    1. Cache invalidation for the user's subscription status
    2. WebSocket push to connected clients (if any)
    3. Metric emission for FinOps tracking
    """
    stripe_customer_id = row_data.get("stripe_customer_id", "")
    amount = row_data.get("amount_cents", 0)
    status = row_data.get("status", "")

    logger.info(
        "Transaction %s: customer=%s amount=%d status=%s",
        change_type,
        stripe_customer_id[:20],
        amount,
        status,
    )

    if change_type == "INSERT" and status == "succeeded":
        # TODO: Invalidate subscription cache, push WebSocket event
        logger.info("Payment success — triggering UI refresh for %s", stripe_customer_id[:20])


def _handle_users(change_type: str, row_data: dict, commit_ts: str) -> None:
    """Handle Spanner `users` table changes."""
    user_id = row_data.get("user_id", "")
    email = row_data.get("email", "")

    logger.info("User %s: id=%s email=%s", change_type, user_id[:20], email[:30])


def _handle_sessions(change_type: str, row_data: dict, commit_ts: str) -> None:
    """Handle Spanner `sessions` table changes."""
    session_id = row_data.get("session_id", "")
    logger.info("Session %s: id=%s", change_type, session_id[:20])


def _handle_generic(change_type: str, row_data: dict, commit_ts: str) -> None:
    """Fallback handler for unregistered tables."""
    logger.info("Generic CDC: %s with %d fields", change_type, len(row_data))


# Table → Handler routing map
TABLE_HANDLERS = {
    "transactions": _handle_transactions,
    "users": _handle_users,
    "sessions": _handle_sessions,
}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
