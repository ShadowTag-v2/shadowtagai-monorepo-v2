# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Audit Event Publisher - High-speed API for publishing audit traces to Pub/Sub.

Governance-grade event publishing with automatic retries and batching.
"""

import json
import os
from datetime import datetime
from typing import Any

from google.api_core import retry
from google.cloud import pubsub_v1


class AuditPublisher:
    """
    High-speed publisher for audit trace events.

    Features:
    - Automatic batching for throughput
    - Retry with exponential backoff
    - Future-based async publishing
    """

    def __init__(self, project_id: str | None = None, topic_id: str = "audit-trace-events"):
        self.project_id = project_id or os.environ.get("GCP_PROJECT_ID", "acquired-jet-478701-b3")
        self.topic_id = topic_id

        # Configure batching for high throughput
        batch_settings = pubsub_v1.types.BatchSettings(
            max_messages=100,
            max_bytes=1024 * 1024,  # 1MB
            max_latency=0.1,  # 100ms
        )

        self.publisher = pubsub_v1.PublisherClient(batch_settings=batch_settings)
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_id)

    def publish(
        self,
        decision_id: str,
        decision: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Publish an audit trace event.

        Args:
            decision_id: Unique identifier for the decision
            decision: The decision outcome (APPROVE/DENY/REVIEW)
            inputs: Input data that led to the decision
            outputs: Output data from the decision
            metadata: Optional additional metadata

        Returns:
            Message ID from Pub/Sub
        """
        trace_data = {
            "decision_id": decision_id,
            "decision": decision,
            "inputs": inputs,
            "outputs": outputs,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
        }

        # Serialize to JSON bytes
        data = json.dumps(trace_data).encode("utf-8")

        # Publish with retry
        future = self.publisher.publish(
            self.topic_path,
            data,
            decision_id=decision_id,
            decision=decision,
            retry=retry.Retry(deadline=30.0),
        )

        # Wait for result (blocking)
        message_id = future.result()
        return message_id

    def publish_async(
        self,
        decision_id: str,
        decision: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> pubsub_v1.publisher.futures.Future:
        """
        Publish an audit trace event asynchronously.

        Returns:
            Future that resolves to message ID
        """
        trace_data = {
            "decision_id": decision_id,
            "decision": decision,
            "inputs": inputs,
            "outputs": outputs,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
        }

        data = json.dumps(trace_data).encode("utf-8")

        return self.publisher.publish(self.topic_path, data, decision_id=decision_id, decision=decision)

    def publish_batch(self, events: list[dict[str, Any]]) -> list[str]:
        """
        Publish multiple audit events efficiently.

        Args:
            events: List of event dictionaries with decision_id, decision, inputs, outputs

        Returns:
            List of message IDs
        """
        futures = []

        for event in events:
            future = self.publish_async(
                decision_id=event["decision_id"],
                decision=event["decision"],
                inputs=event.get("inputs", {}),
                outputs=event.get("outputs", {}),
                metadata=event.get("metadata"),
            )
            futures.append(future)

        # Wait for all to complete
        message_ids = [f.result() for f in futures]
        return message_ids


# Singleton instance
_publisher: AuditPublisher | None = None


def get_publisher() -> AuditPublisher:
    """Get or create singleton publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = AuditPublisher()
    return _publisher


if __name__ == "__main__":
    # Test publishing
    publisher = AuditPublisher()

    msg_id = publisher.publish(
        decision_id="test_001",
        decision="APPROVE",
        inputs={"user_id": "u123", "amount": 100.00},
        outputs={"risk_score": 0.15, "approved": True},
        metadata={"source": "test_script"},
    )

    print(f"Published message: {msg_id}")
