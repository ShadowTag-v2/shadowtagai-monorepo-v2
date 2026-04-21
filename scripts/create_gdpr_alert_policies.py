# scripts/create_gdpr_alert_policies.py
"""#6: Create Cloud Monitoring alert policies for GDPR endpoint 429 rate limit triggers.

Creates:
- Alert on GDPR endpoint 429 rate > 10/min
- Alert on DLQ message count > 0
- Alert on export endpoint latency > 30s p99
"""

from __future__ import annotations

import json
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

GCLOUD = os.path.expanduser("~/google-cloud-sdk/bin/gcloud")
PROJECT = "shadowtag-omega-v4"
NOTIFICATION_CHANNEL = "projects/shadowtag-omega-v4/notificationChannels/6144499617599280001"


def create_rate_limit_alert() -> dict:
    """Create alert for GDPR 429 rate limit triggers."""
    policy = {
        "displayName": "GDPR Endpoint 429 Rate Limit Alert",
        "documentation": {
            "content": "GDPR endpoints are returning 429 Too Many Requests at a high rate. This may indicate abuse or a misconfigured client.",
            "mimeType": "text/markdown",
        },
        "conditions": [
            {
                "displayName": "429 rate > 10/min on GDPR endpoints",
                "conditionThreshold": {
                    "filter": (
                        'resource.type="cloud_run_revision" '
                        'AND metric.type="run.googleapis.com/request_count" '
                        'AND metric.labels.response_code="429" '
                        'AND resource.labels.service_name="counselconduit"'
                    ),
                    "aggregations": [
                        {
                            "alignmentPeriod": "60s",
                            "perSeriesAligner": "ALIGN_RATE",
                        }
                    ],
                    "comparison": "COMPARISON_GT",
                    "thresholdValue": 10,
                    "duration": "60s",
                    "trigger": {"count": 1},
                },
            }
        ],
        "combiner": "OR",
        "notificationChannels": [NOTIFICATION_CHANNEL],
        "alertStrategy": {
            "autoClose": "604800s",  # 7 days
        },
    }
    return policy


def create_dlq_alert() -> dict:
    """Create alert for DLQ messages > 0."""
    policy = {
        "displayName": "GDPR Dead Letter Queue Alert",
        "documentation": {
            "content": "Failed GDPR deletion tasks have been routed to the dead-letter queue. Manual investigation required.",
            "mimeType": "text/markdown",
        },
        "conditions": [
            {
                "displayName": "DLQ message count > 0",
                "conditionThreshold": {
                    "filter": (
                        'resource.type="cloud_tasks_queue" '
                        'AND resource.labels.queue_id="gdpr-deletions-dlq" '
                        'AND metric.type="cloudtasks.googleapis.com/queue/depth"'
                    ),
                    "aggregations": [
                        {
                            "alignmentPeriod": "300s",
                            "perSeriesAligner": "ALIGN_MAX",
                        }
                    ],
                    "comparison": "COMPARISON_GT",
                    "thresholdValue": 0,
                    "duration": "0s",
                    "trigger": {"count": 1},
                },
            }
        ],
        "combiner": "OR",
        "notificationChannels": [NOTIFICATION_CHANNEL],
    }
    return policy


def create_export_latency_alert() -> dict:
    """Create alert for export endpoint p99 latency > 30s."""
    policy = {
        "displayName": "GDPR Export Latency Alert (p99 > 30s)",
        "documentation": {
            "content": "The GDPR data export endpoint p99 latency has exceeded 30 seconds.",
            "mimeType": "text/markdown",
        },
        "conditions": [
            {
                "displayName": "Export p99 latency > 30s",
                "conditionThreshold": {
                    "filter": (
                        'resource.type="cloud_run_revision" '
                        'AND metric.type="run.googleapis.com/request_latencies" '
                        'AND resource.labels.service_name="counselconduit"'
                    ),
                    "aggregations": [
                        {
                            "alignmentPeriod": "300s",
                            "perSeriesAligner": "ALIGN_PERCENTILE_99",
                        }
                    ],
                    "comparison": "COMPARISON_GT",
                    "thresholdValue": 30000,  # 30s in ms
                    "duration": "300s",
                    "trigger": {"count": 1},
                },
            }
        ],
        "combiner": "OR",
        "notificationChannels": [NOTIFICATION_CHANNEL],
    }
    return policy


def main() -> None:
    """Create all GDPR alert policies."""
    policies = [
        ("429 Rate Limit", create_rate_limit_alert()),
        ("DLQ Alert", create_dlq_alert()),
        ("Export Latency", create_export_latency_alert()),
    ]

    for name, policy in policies:
        policy_json = json.dumps(policy)
        print(f"[INFO] Creating alert policy: {name}")
        print(f"  Policy JSON length: {len(policy_json)} bytes")
        # In production: use google-cloud-monitoring client library
        # For now, output the policy for manual creation
        output_path = f"/tmp/alert_policy_{name.lower().replace(' ', '_')}.json"
        with open(output_path, "w") as f:
            json.dump(policy, f, indent=2)
        print(f"  Written to: {output_path}")

    print(f"\n[DONE] {len(policies)} alert policies generated")


if __name__ == "__main__":
    main()
