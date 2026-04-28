#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""P1 Alert Push Notification via Firebase Cloud Messaging (Item #17).

Sends push notifications to admin devices when P1 alerts fire.
Triggered by Cloud Monitoring alerting → Pub/Sub → Cloud Function → this script.

Requires:
- Firebase Admin SDK initialized
- FCM topic 'counselconduit-p1-alerts' with admin device subscriptions
"""

import json
import logging

logger = logging.getLogger("p1_push_notify")


def send_p1_notification(alert_data: dict) -> str | None:
    """Send FCM push notification for P1 alerts.

    Args:
        alert_data: Cloud Monitoring alert payload

    Returns:
        FCM message ID or None on failure
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging
    except ImportError:
        logger.error("firebase-admin not installed")
        return None

    # Initialize Firebase Admin if not already
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {"projectId": "shadowtag-omega-v4"})

    policy_name = alert_data.get("incident", {}).get("policy_name", "Unknown Alert")
    severity = alert_data.get("incident", {}).get("severity", "WARNING")
    started_at = alert_data.get("incident", {}).get("started_at", "")

    # Build FCM message
    message = messaging.Message(
        topic="counselconduit-p1-alerts",
        notification=messaging.Notification(
            title=f"🚨 P1 Alert: {policy_name}",
            body=f"Severity: {severity}\nStarted: {started_at}\nAction required immediately.",
        ),
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                channel_id="p1-alerts",
                priority="max",
                default_sound=True,
                default_vibrate_timings=True,
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=f"🚨 P1: {policy_name}",
                        body=f"Severity: {severity}",
                    ),
                    sound="default",
                    badge=1,
                    category="P1_ALERT",
                ),
            ),
        ),
        data={
            "alert_type": "p1",
            "policy_name": policy_name,
            "severity": severity,
            "started_at": started_at,
            "url": "https://console.cloud.google.com/monitoring/alerting?project=shadowtag-omega-v4",
        },
    )

    try:
        response = messaging.send(message)
        logger.info("P1 notification sent: %s", response)
        return response
    except Exception as e:
        logger.error("FCM send failed: %s", e)
        return None


# Cloud Function entry point
def handle_p1_alert(event, context):
    """Cloud Function triggered by Pub/Sub from Cloud Monitoring alerts."""
    import base64

    if "data" in event:
        alert_json = base64.b64decode(event["data"]).decode("utf-8")
        alert_data = json.loads(alert_json)
        send_p1_notification(alert_data)


if __name__ == "__main__":
    # Manual test
    logging.basicConfig(level=logging.INFO)
    test_alert = {
        "incident": {
            "policy_name": "SLO Burn Rate Critical",
            "severity": "CRITICAL",
            "started_at": "2026-04-21T22:00:00Z",
        }
    }
    send_p1_notification(test_alert)
