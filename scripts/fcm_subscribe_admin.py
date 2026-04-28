#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FCM Topic Subscription Helper (#7).

Subscribes admin device tokens to the 'counselconduit-p1-alerts' FCM topic.
Run with: python3 scripts/fcm_subscribe_admin.py <registration_token>

To get a registration token, use the Firebase SDK in the admin dashboard.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fcm_subscribe")


def subscribe_to_topic(registration_token: str, topic: str = "counselconduit-p1-alerts") -> dict:
    """Subscribe a device registration token to an FCM topic."""
    try:
        from firebase_admin import messaging, initialize_app
    except ImportError:
        logger.error("firebase-admin not installed. Run: pip install firebase-admin")
        return {"error": "firebase-admin not installed"}

    try:  # noqa: SIM105
        initialize_app()
    except ValueError:
        pass  # Already initialized

    response = messaging.subscribe_to_topic([registration_token], topic)

    result = {
        "topic": topic,
        "success_count": response.success_count,
        "failure_count": response.failure_count,
        "errors": [str(e) for e in response.errors] if response.errors else [],
    }

    if response.success_count > 0:
        logger.info("✅ Successfully subscribed to topic '%s'", topic)
    else:
        logger.error("❌ Failed to subscribe: %s", response.errors)

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fcm_subscribe_admin.py <registration_token>")
        print()
        print("To get a registration token:")
        print("  1. Open the admin dashboard in Chrome")
        print("  2. Open DevTools console")
        print("  3. Run: await Notification.requestPermission()")
        print("  4. Get token from Firebase Messaging SDK")
        sys.exit(1)

    token = sys.argv[1]
    result = subscribe_to_topic(token)
    print(f"Result: {result}")
