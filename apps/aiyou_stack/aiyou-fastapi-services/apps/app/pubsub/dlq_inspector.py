# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Dead Letter Queue Inspector - Forensic tool for failed audit traces.

The "Coroner" for compliance failures.
"""

import json
import os
from datetime import datetime
from typing import Any

from google.cloud import pubsub_v1


class DLQInspector:
    """Forensic inspector for Dead Letter Queue.

    Features:
    - Pull failed messages for analysis
    - Replay messages to main queue
    - Generate failure reports
    """

    def __init__(
        self,
        project_id: str | None = None,
        dlq_subscription: str = "audit-trace-dlq-sub",
        main_topic: str = "audit-trace-events",
    ):
        self.project_id = project_id or os.environ.get("GCP_PROJECT_ID", "acquired-jet-478701-b3")
        self.dlq_subscription = dlq_subscription
        self.main_topic = main_topic

        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()

        self.subscription_path = self.subscriber.subscription_path(
            self.project_id,
            self.dlq_subscription,
        )
        self.topic_path = self.publisher.topic_path(self.project_id, self.main_topic)

    def examine(self, max_messages: int = 10) -> list[dict[str, Any]]:
        """Examine failed messages in the DLQ.

        Args:
            max_messages: Maximum number of messages to retrieve

        Returns:
            List of failed message details

        """
        print(f"Inspecting Dead Letter Queue: {self.dlq_subscription}...")

        response = self.subscriber.pull(
            request={
                "subscription": self.subscription_path,
                "max_messages": max_messages,
            },
        )

        if not response.received_messages:
            print("DLQ is empty. All audits processed successfully.")
            return []

        failures = []

        for received_message in response.received_messages:
            msg = received_message.message

            failure_info = {
                "message_id": msg.message_id,
                "publish_time": msg.publish_time.isoformat() if msg.publish_time else None,
                "ack_id": received_message.ack_id,
                "attributes": dict(msg.attributes),
                "data_raw": msg.data.decode("utf-8", errors="replace"),
                "data_parsed": None,
                "error_context": None,
            }

            # Try to parse the payload
            try:
                failure_info["data_parsed"] = json.loads(msg.data.decode("utf-8"))
            except json.JSONDecodeError as e:
                failure_info["error_context"] = f"JSON parse error: {e}"

            failures.append(failure_info)

            # Print summary
            print(f"\n{'=' * 60}")
            print(f"Found Dead Message ID: {msg.message_id}")
            print(f"Original Publish Time: {failure_info['publish_time']}")

            if failure_info["data_parsed"]:
                print(f"Decision ID: {failure_info['data_parsed'].get('decision_id', 'N/A')}")
                print(f"Decision: {failure_info['data_parsed'].get('decision', 'N/A')}")
            else:
                print(f"RAW DATA (Corrupted): {failure_info['data_raw'][:200]}...")

        return failures

    def replay(self, ack_id: str) -> str | None:
        """Replay a single message back to the main topic.

        Args:
            ack_id: The ack_id of the message to replay

        Returns:
            New message ID if successful, None otherwise

        """
        # First, pull the specific message
        response = self.subscriber.pull(
            request={
                "subscription": self.subscription_path,
                "max_messages": 100,  # Pull batch to find our message
            },
        )

        for received_message in response.received_messages:
            if received_message.ack_id == ack_id:
                msg = received_message.message

                # Republish to main topic
                future = self.publisher.publish(
                    self.topic_path,
                    msg.data,
                    **dict(msg.attributes),
                    replayed="true",
                    original_message_id=msg.message_id,
                )

                new_message_id = future.result()

                # Acknowledge the DLQ message
                self.subscriber.acknowledge(
                    request={
                        "subscription": self.subscription_path,
                        "ack_ids": [ack_id],
                    },
                )

                print(f"Replayed message {msg.message_id} -> {new_message_id}")
                return new_message_id

        print(f"Message with ack_id {ack_id} not found")
        return None

    def replay_all(self) -> list[str]:
        """Replay all messages in the DLQ back to the main topic.

        Returns:
            List of new message IDs

        """
        response = self.subscriber.pull(
            request={"subscription": self.subscription_path, "max_messages": 1000},
        )

        if not response.received_messages:
            print("DLQ is empty. Nothing to replay.")
            return []

        new_message_ids = []
        ack_ids = []

        for received_message in response.received_messages:
            msg = received_message.message

            # Republish
            future = self.publisher.publish(
                self.topic_path,
                msg.data,
                **dict(msg.attributes),
                replayed="true",
                original_message_id=msg.message_id,
            )

            new_message_ids.append(future.result())
            ack_ids.append(received_message.ack_id)

        # Acknowledge all DLQ messages
        if ack_ids:
            self.subscriber.acknowledge(
                request={"subscription": self.subscription_path, "ack_ids": ack_ids},
            )

        print(f"Replayed {len(new_message_ids)} messages")
        return new_message_ids

    def purge(self, ack_ids: list[str] | None = None) -> int:
        """Purge messages from the DLQ (acknowledge without processing).

        Args:
            ack_ids: Specific messages to purge, or None to purge all

        Returns:
            Number of messages purged

        """
        if ack_ids:
            self.subscriber.acknowledge(
                request={"subscription": self.subscription_path, "ack_ids": ack_ids},
            )
            print(f"Purged {len(ack_ids)} messages")
            return len(ack_ids)

        # Purge all
        response = self.subscriber.pull(
            request={"subscription": self.subscription_path, "max_messages": 1000},
        )

        if not response.received_messages:
            print("DLQ is empty")
            return 0

        all_ack_ids = [m.ack_id for m in response.received_messages]

        self.subscriber.acknowledge(
            request={"subscription": self.subscription_path, "ack_ids": all_ack_ids},
        )

        print(f"Purged {len(all_ack_ids)} messages")
        return len(all_ack_ids)

    def generate_report(self) -> str:
        """Generate a forensic report of DLQ contents.

        Returns:
            Markdown-formatted report

        """
        failures = self.examine(max_messages=100)

        report = f"""# Dead Letter Queue Forensic Report
Generated: {datetime.utcnow().isoformat()}Z

## Summary
- **Total Failed Messages**: {len(failures)}
- **DLQ Subscription**: {self.dlq_subscription}
- **Main Topic**: {self.main_topic}

## Failed Messages
"""

        for i, failure in enumerate(failures, 1):
            report += f"""
### Message {i}
- **Message ID**: {failure["message_id"]}
- **Publish Time**: {failure["publish_time"]}
- **Attributes**: {json.dumps(failure["attributes"], indent=2)}

"""
            if failure["data_parsed"]:
                report += f"""**Parsed Data**:
```json
{json.dumps(failure["data_parsed"], indent=2)}
```
"""
            else:
                report += f"""**Raw Data (Corrupted)**:
```
{failure["data_raw"][:500]}
```

**Error**: {failure["error_context"]}
"""

        report += """
## Recommended Actions
1. Review error patterns above
2. Fix processing bugs in AuditWorker
3. Replay messages: `inspector.replay_all()`
4. Monitor for new DLQ entries
"""

        return report


if __name__ == "__main__":
    inspector = DLQInspector()

    print("=" * 60)
    print("DEAD LETTER QUEUE INSPECTOR")
    print("=" * 60)

    # Examine DLQ
    failures = inspector.examine()

    if failures:
        print("\n" + "=" * 60)
        print("FORENSIC REPORT")
        print("=" * 60)
        print(inspector.generate_report())
