# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Audit Event Worker - Resilient processor with DLQ support.

Governance-grade message processing that never loses an audit trail.
"""

import json
import os
from collections.abc import Callable
from datetime import datetime, timedelta

from google.cloud import pubsub_v1, storage


class AuditWorker:
    """
    Resilient audit event processor with DLQ support.

    Features:
    - Automatic retry with exponential backoff
    - Dead Letter Queue routing after max attempts
    - GCS signed URL generation for audit retrieval
    - Webhook delivery for notifications
    """

    def __init__(
        self,
        project_id: str | None = None,
        subscription_id: str = "audit-trace-sub",
        gcs_bucket: str = "shadowtagai-audit-traces",
    ):
        self.project_id = project_id or os.environ.get("GCP_PROJECT_ID", "acquired-jet-478701-b3")
        self.subscription_id = subscription_id
        self.gcs_bucket = gcs_bucket

        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_id)

        # GCS client for audit storage
        self.storage_client = storage.Client()

    def generate_signed_trace(self, trace_data: dict) -> str:
        """
        Store audit trace in GCS and return signed URL.

        Args:
            trace_data: The audit trace data

        Returns:
            Signed URL valid for 7 days
        """
        decision_id = trace_data.get("decision_id", "unknown")
        timestamp = datetime.utcnow().strftime("%Y/%m/%d")

        # Create blob path: audit-traces/2025/11/26/decision_id.json
        blob_name = f"audit-traces/{timestamp}/{decision_id}.json"

        bucket = self.storage_client.bucket(self.gcs_bucket)
        blob = bucket.blob(blob_name)

        # Upload trace
        blob.upload_from_string(json.dumps(trace_data, indent=2), content_type="application/json")

        # Generate signed URL (7 days)
        signed_url = blob.generate_signed_url(version="v4", expiration=timedelta(days=7), method="GET")

        return signed_url

    def deliver_webhook(self, decision_id: str, signed_url: str) -> bool:
        """
        Deliver audit notification via webhook.

        Args:
            decision_id: The decision identifier
            signed_url: GCS signed URL for the audit trace

        Returns:
            True if delivery succeeded
        """
        webhook_url = os.environ.get("AUDIT_WEBHOOK_URL")
        if not webhook_url:
            return True  # No webhook configured

        import requests

        try:
            response = requests.post(
                webhook_url,
                json={
                    "event": "audit_trace_created",
                    "decision_id": decision_id,
                    "trace_url": signed_url,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                timeout=10,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def process_message(self, message: pubsub_v1.subscriber.message.Message) -> None:
        """
        Process a single audit message with failure classification.

        Failure types:
        - Transient (network): nack() -> retry immediately
        - Fatal (bad data): nack() -> after 5 tries goes to DLQ
        """
        print(f"\n[RECEIVED] Msg ID: {message.message_id} | Attempt: {message.delivery_attempt}")

        try:
            # Parse message
            data_str = message.data.decode("utf-8")
            trace_data = json.loads(data_str)

            # Process the audit trace
            signed_url = self.generate_signed_trace(trace_data)
            self.deliver_webhook(trace_data.get("decision_id", "unknown"), signed_url)

            print(f" -> [SUCCESS] Acking message. URL: {signed_url[:80]}...")
            message.ack()

        except json.JSONDecodeError as e:
            print(f" -> [FATAL] Malformed JSON: {e}")
            print(" -> Nacking to route to DLQ for forensic analysis")
            message.nack()

        except ConnectionError as e:
            print(f" -> [TRANSIENT] Network error: {e}")
            print(" -> Nacking to trigger retry")
            message.nack()

        except Exception as e:
            print(f" -> [ERROR] Processing failed: {e}")
            print(" -> Nacking. If this persists 5 times, Pub/Sub sends to DLQ.")
            message.nack()

    def start(self, timeout: float | None = None) -> None:
        """
        Start the worker with streaming pull.

        Args:
            timeout: Optional timeout in seconds (None = run forever)
        """
        print(f"Starting Audit Worker on {self.subscription_path}")
        print("Waiting for messages...")

        streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=self.process_message)

        try:
            streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            print(f"Worker stopped: {e}")
            streaming_pull_future.cancel()
            streaming_pull_future.result()

    def start_with_callback(self, callback: Callable[[dict], None], timeout: float | None = None) -> None:
        """
        Start worker with custom callback for processing.

        Args:
            callback: Function to call with parsed trace data
            timeout: Optional timeout in seconds
        """

        def wrapped_callback(message: pubsub_v1.subscriber.message.Message) -> None:
            print(f"\n[RECEIVED] Msg ID: {message.message_id} | Attempt: {message.delivery_attempt}")

            try:
                data_str = message.data.decode("utf-8")
                trace_data = json.loads(data_str)

                # Call custom processor
                callback(trace_data)

                print(" -> [SUCCESS] Acking message")
                message.ack()

            except json.JSONDecodeError as e:
                print(f" -> [FATAL] Malformed JSON: {e}")
                message.nack()

            except Exception as e:
                print(f" -> [ERROR] Processing failed: {e}")
                message.nack()

        print(f"Starting Audit Worker (custom callback) on {self.subscription_path}")

        streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=wrapped_callback)

        try:
            streaming_pull_future.result(timeout=timeout)
        except Exception as e:
            print(f"Worker stopped: {e}")
            streaming_pull_future.cancel()


if __name__ == "__main__":
    # Run worker
    worker = AuditWorker()
    worker.start()
