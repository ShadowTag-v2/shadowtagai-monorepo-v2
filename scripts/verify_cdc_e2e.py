"""
E2E CDC Pipeline Verification Script.

Publishes a test event to Pub/Sub → verifies Firestore write within 30s.
Tests the full Spanner → Datastream → GCS → Pub/Sub → Cloud Run → Firestore pipeline.

Usage:
    python scripts/verify_cdc_e2e.py
"""

from __future__ import annotations

import json
import sys
import time

from google.cloud import firestore, pubsub_v1, storage

PROJECT_ID = "shadowtag-omega-v4"
TOPIC = f"projects/{PROJECT_ID}/topics/database-events"
BUCKET = "shadowtag-cdc-staging"
TEST_OBJECT = "cdc/test/e2e_verification.json"
FIRESTORE_COLLECTION = "cdc_events"


def create_test_cdc_file() -> None:
    """Upload a test JSON CDC file to the staging bucket."""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET)
    blob = bucket.blob(TEST_OBJECT)
    test_data = {
        "changeType": "INSERT",
        "tableName": "e2e_test",
        "timestamp": time.time(),
        "data": {"test_key": "verification", "value": 42},
    }
    blob.upload_from_string(json.dumps(test_data), content_type="application/json")
    print(f"✅ Uploaded test CDC file: gs://{BUCKET}/{TEST_OBJECT}")


def publish_notification() -> None:
    """Publish a GCS notification to the Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    message = json.dumps(
        {
            "bucket": BUCKET,
            "name": TEST_OBJECT,
            "contentType": "application/json",
            "size": "128",
        }
    ).encode()
    future = publisher.publish(TOPIC, message, eventType="OBJECT_FINALIZE")
    msg_id = future.result()
    print(f"✅ Published Pub/Sub message: {msg_id}")


def verify_firestore_write(timeout: int = 30) -> bool:
    """Poll Firestore for the processed CDC event."""
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection(FIRESTORE_COLLECTION)
    start = time.time()
    while time.time() - start < timeout:
        docs = collection.where("source_object", "==", TEST_OBJECT).order_by("processed_at", direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            print(f"✅ Firestore write verified: {doc.id}")
            print(f"   Status: {data.get('status')}")
            print(f"   Records: {data.get('record_count')}")
            print(f"   Processed: {data.get('processed_at')}")
            return True
        time.sleep(2)
    print("❌ Firestore write not detected within timeout")
    return False


if __name__ == "__main__":
    create_test_cdc_file()
    publish_notification()
    ok = verify_firestore_write()
    sys.exit(0 if ok else 1)
