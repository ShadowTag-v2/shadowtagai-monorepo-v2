"""
Database Events Handler — Cloud Run Service
════════════════════════════════════════════

Receives Pub/Sub push messages triggered by GCS OBJECT_FINALIZE events
from the Datastream CDC pipeline. Processes Avro/JSON CDC files from
the `shadowtag-cdc-staging` bucket and writes normalized change events
to Firestore for downstream consumption.

Architecture:
  Spanner → Datastream → GCS (shadowtag-cdc-staging/cdc/) →
  Pub/Sub (database-events) → THIS HANDLER → Firestore (cdc_events/)
"""

from __future__ import annotations

import base64
import json
import logging
import os
import sys
from datetime import datetime, UTC
from typing import Any

from flask import Flask, Response, request
from google.cloud import firestore, storage

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ID = os.environ.get("GCP_PROJECT", "shadowtag-omega-v4")
CDC_BUCKET = os.environ.get("CDC_BUCKET", "shadowtag-cdc-staging")
FIRESTORE_COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "cdc_events")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
  stream=sys.stdout,
)
logger = logging.getLogger("database-events-handler")

# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Lazy-initialized clients (cold start optimization)
_firestore_client: firestore.Client | None = None
_storage_client: storage.Client | None = None


def get_firestore_client() -> firestore.Client:
  """Lazy Firestore client initialization."""
  global _firestore_client
  if _firestore_client is None:
    _firestore_client = firestore.Client(project=PROJECT_ID)
  return _firestore_client


def get_storage_client() -> storage.Client:
  """Lazy GCS client initialization."""
  global _storage_client
  if _storage_client is None:
    _storage_client = storage.Client(project=PROJECT_ID)
  return _storage_client


# ---------------------------------------------------------------------------
# Core Processing
# ---------------------------------------------------------------------------


def process_cdc_object(bucket_name: str, object_name: str) -> dict[str, Any]:
  """
  Download and parse a CDC object from GCS.

  Datastream writes Avro files by default, but can be configured for JSON.
  This handler supports JSON CDC files. For Avro, add fastavro dependency.

  Returns:
      Parsed CDC event metadata dict.
  """
  client = get_storage_client()
  bucket = client.bucket(bucket_name)
  blob = bucket.blob(object_name)

  if not blob.exists():
    logger.warning("CDC object not found: gs://%s/%s", bucket_name, object_name)
    return {"status": "not_found", "object": object_name}

  # Read the CDC file content
  content = blob.download_as_text()

  # Parse based on file extension
  if object_name.endswith(".json"):
    try:
      records = json.loads(content)
    except json.JSONDecodeError:
      # Newline-delimited JSON (NDJSON)
      records = [
        json.loads(line) for line in content.strip().split("\n") if line.strip()
      ]
  else:
    # For Avro files, log and skip (would need fastavro)
    logger.info("Skipping non-JSON CDC file: %s", object_name)
    return {"status": "skipped", "object": object_name, "reason": "non-json"}

  # Normalize to list
  if isinstance(records, dict):
    records = [records]

  return {
    "status": "processed",
    "object": object_name,
    "record_count": len(records),
    "records": records,
  }


def write_to_firestore(cdc_result: dict[str, Any], source_object: str) -> str:
  """
  Write processed CDC event to Firestore for downstream consumers.

  Returns:
      Document ID of the written event.
  """
  db = get_firestore_client()
  collection = db.collection(FIRESTORE_COLLECTION)

  doc_data = {
    "source_object": source_object,
    "status": cdc_result.get("status", "unknown"),
    "record_count": cdc_result.get("record_count", 0),
    "processed_at": datetime.now(UTC).isoformat(),
    "pipeline": "datastream-cdc",
  }

  # Include first 10 records as sample (avoid Firestore 1MB doc limit)
  records = cdc_result.get("records", [])
  if records:
    doc_data["sample_records"] = records[:10]

  _, doc_ref = collection.add(doc_data)
  logger.info("Written CDC event to Firestore: %s/%s", FIRESTORE_COLLECTION, doc_ref.id)
  return doc_ref.id


# ---------------------------------------------------------------------------
# HTTP Endpoints
# ---------------------------------------------------------------------------


@app.route("/", methods=["POST"])
def handle_pubsub_push() -> tuple[str | Response, int]:
  """
  Pub/Sub push endpoint.

  Expects a Pub/Sub message envelope with base64-encoded data
  containing the GCS notification payload.
  """
  envelope = request.get_json(silent=True)

  if not envelope:
    logger.error("Empty request body")
    return "Bad Request: no Pub/Sub message", 400

  message = envelope.get("message", {})
  if not message:
    logger.error("No message in Pub/Sub envelope")
    return "Bad Request: no message", 400

  # Decode the Pub/Sub message data
  data_b64 = message.get("data", "")
  if data_b64:
    try:
      data = json.loads(base64.b64decode(data_b64).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
      logger.error("Failed to decode Pub/Sub data: %s", e)
      return "Bad Request: invalid message data", 400
  else:
    # GCS notifications can also send data in attributes
    data = message.get("attributes", {})

  # Extract GCS object info from the notification
  bucket_name = data.get("bucket", data.get("bucketId", CDC_BUCKET))
  object_name = data.get("name", data.get("objectId", ""))

  if not object_name:
    logger.warning("No object name in notification: %s", data)
    # Ack the message to prevent redelivery
    return "OK: no object to process", 200

  logger.info(
    "Processing CDC event: gs://%s/%s (size: %s, type: %s)",
    bucket_name,
    object_name,
    data.get("size", "unknown"),
    data.get("contentType", "unknown"),
  )

  # Skip non-CDC paths (e.g., metadata files)
  if not object_name.startswith("cdc/"):
    logger.info("Skipping non-CDC path: %s", object_name)
    return "OK: non-CDC path", 200

  try:
    # Process the CDC file
    result = process_cdc_object(bucket_name, object_name)

    if result["status"] == "processed":
      doc_id = write_to_firestore(result, object_name)
      logger.info(
        "CDC pipeline complete: %s → %s records → Firestore %s",
        object_name,
        result.get("record_count", 0),
        doc_id,
      )
    else:
      logger.info("CDC file %s: %s", result["status"], object_name)

    return "OK", 200

  except Exception:
    logger.exception("Error processing CDC event: %s", object_name)
    # Return 500 to trigger Pub/Sub retry
    return "Internal Server Error", 500


@app.route("/health", methods=["GET"])
def health_check() -> tuple[str, int]:
  """Health check endpoint for Cloud Run."""
  return "OK", 200


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)
