#!/usr/bin/env python3
"""
Provision Cloud Monitoring Alerts for ShadowTag AI infrastructure.
Creates alerts for Firestore read/write spikes and error counts.
Target project: shadowtag-omega-v4
"""
import sys
import argparse

try:
    from google.cloud import monitoring_v3
    from google.api_core.exceptions import GoogleAPICallError
except ImportError:
    print("Error: Missing google-cloud-monitoring library. Run: pip install google-cloud-monitoring")
    sys.exit(1)

def create_firestore_alert(project_id: str, email_address: str):
    client = monitoring_v3.AlertPolicyServiceClient()
    project_name = f"projects/{project_id}"

    # 1. Create Notification Channel
    channel_client = monitoring_v3.NotificationChannelServiceClient()
    channel = monitoring_v3.NotificationChannel()
    channel.type_ = "email"
    channel.labels = {"email_address": email_address}
    channel.display_name = "Admin Alerts"
    
    try:
        created_channel = channel_client.create_notification_channel(
            name=project_name, notification_channel=channel
        )
        print(f"Created notification channel: {created_channel.name}")
    except GoogleAPICallError as e:
        print(f"Failed to create channel: {e}")
        return

    # 2. Alert Policy: Firestore Spikes
    policy = monitoring_v3.AlertPolicy()
    policy.display_name = "High Firestore Usage (Omega-v4)"
    
    condition = monitoring_v3.AlertPolicy.Condition()
    condition.display_name = "Firestore Read/Write Spikes"
    
    # MQL for Cloud Firestore writes exceeding threshold
    condition.condition_threshold.filter = (
        'metric.type="firestore.googleapis.com/document/write_count" AND '
        'resource.type="firestore_database"'
    )
    condition.condition_threshold.comparison = monitoring_v3.ComparisonType.COMPARISON_GT
    condition.condition_threshold.threshold_value = 50000.0  # Alert if > 50k writes
    condition.condition_threshold.duration.seconds = 300  # over 5 minutes
    
    condition.condition_threshold.aggregations.append(
        monitoring_v3.Aggregation(
            alignment_period={"seconds": 60},
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
        )
    )
    
    policy.conditions.append(condition)
    policy.notification_channels.append(created_channel.name)
    policy.combiner = monitoring_v3.AlertPolicy.ConditionCombinerType.OR

    try:
        created_policy = client.create_alert_policy(
            name=project_name, alert_policy=policy
        )
        print(f"Created alert policy: {created_policy.name}")
    except GoogleAPICallError as e:
        print(f"Failed to create policy: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="shadowtag-omega-v4")
    parser.add_argument("--email", default="admin@shadowtagai.com")
    args = parser.parse_args()
    
    print(f"Provisioning alerts for {args.project}...")
    create_firestore_alert(args.project, args.email)
