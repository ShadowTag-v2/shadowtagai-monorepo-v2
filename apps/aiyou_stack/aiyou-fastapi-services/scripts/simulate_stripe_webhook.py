"""Stripe Webhook Simulation — ShadowTag-v4

Simulates incoming Stripe webhook events to validate
the local FastAPI endpoint handler parses correctly.

Events simulated:
- checkout.session.completed (new subscription)
- invoice.payment_succeeded (renewal)
- customer.subscription.deleted (churn)

Usage:
    python simulate_stripe_webhook.py [--target http://localhost:8000/api/v1/stripe/webhook]
"""

import argparse
import hashlib
import hmac
import json
import time
from datetime import datetime

import requests

# Stripe test mode signing secret (use real one from dashboard in prod)
STRIPE_WEBHOOK_SECRET = "whsec_test_shadowtag_omega_v4_local"


def generate_stripe_signature(payload: str, secret: str) -> str:
    """Generate a Stripe-compatible webhook signature."""
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


def simulate_checkout_completed() -> dict:
    """Simulate checkout.session.completed event."""
    return {
        "id": f"evt_test_{int(time.time())}",
        "type": "checkout.session.completed",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_test_shadowtag_001",
                "object": "checkout.session",
                "amount_total": 2900,
                "currency": "usd",
                "customer": "cus_test_shadowtag_omega",
                "customer_email": "test@shadowtagai.com",
                "mode": "subscription",
                "payment_status": "paid",
                "status": "complete",
                "subscription": "sub_test_shadowtag_pro",
                "metadata": {
                    "tier": "pro",
                    "user_id": "usr_shadowtag_test_001",
                    "product": "ShadowTag AI Pro",
                },
            },
        },
        "livemode": False,
        "api_version": "2025-03-31.basil",
    }


def simulate_invoice_payment_succeeded() -> dict:
    """Simulate invoice.payment_succeeded event."""
    return {
        "id": f"evt_test_{int(time.time())}_inv",
        "type": "invoice.payment_succeeded",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "in_test_shadowtag_001",
                "object": "invoice",
                "amount_paid": 2900,
                "currency": "usd",
                "customer": "cus_test_shadowtag_omega",
                "customer_email": "test@shadowtagai.com",
                "status": "paid",
                "subscription": "sub_test_shadowtag_pro",
                "billing_reason": "subscription_cycle",
                "period_start": int(time.time()) - 2592000,
                "period_end": int(time.time()),
            },
        },
        "livemode": False,
        "api_version": "2025-03-31.basil",
    }


def simulate_subscription_deleted() -> dict:
    """Simulate customer.subscription.deleted event."""
    return {
        "id": f"evt_test_{int(time.time())}_del",
        "type": "customer.subscription.deleted",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "sub_test_shadowtag_churn",
                "object": "subscription",
                "customer": "cus_test_shadowtag_churn",
                "status": "canceled",
                "cancel_at_period_end": False,
                "canceled_at": int(time.time()),
                "current_period_end": int(time.time()),
                "items": {
                    "data": [
                        {
                            "price": {
                                "id": "price_test_pro_monthly",
                                "unit_amount": 2900,
                                "currency": "usd",
                            },
                        },
                    ],
                },
            },
        },
        "livemode": False,
        "api_version": "2025-03-31.basil",
    }


def send_webhook(target_url: str, event: dict) -> dict:
    """Send simulated webhook to target URL."""
    payload = json.dumps(event, indent=2)
    signature = generate_stripe_signature(payload, STRIPE_WEBHOOK_SECRET)

    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": signature,
        "User-Agent": "Stripe/1.0 (+https://stripe.com)",
    }

    print(f"\n{'='*60}")
    print(f"📤 Sending: {event['type']}")
    print(f"   Event ID: {event['id']}")
    print(f"   Target: {target_url}")
    print(f"   Signature: {signature[:50]}...")

    try:
        response = requests.post(target_url, data=payload, headers=headers, timeout=10)
        result = {
            "event_type": event["type"],
            "status_code": response.status_code,
            "response_body": response.text[:500],
            "success": response.status_code in (200, 201, 204),
        }
        status_icon = "✅" if result["success"] else "❌"
        print(f"   {status_icon} Response: {response.status_code}")
        if response.text:
            print(f"   Body: {response.text[:200]}")
        return result
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Connection refused — is the FastAPI server running?")
        return {
            "event_type": event["type"],
            "status_code": 0,
            "response_body": "Connection refused",
            "success": False,
        }
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "event_type": event["type"],
            "status_code": 0,
            "response_body": str(e),
            "success": False,
        }


def main():
    parser = argparse.ArgumentParser(description="Stripe Webhook Simulator")
    parser.add_argument(
        "--target",
        default="http://localhost:8000/api/v1/stripe/webhook",
        help="Target webhook URL",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payloads without sending",
    )
    args = parser.parse_args()

    events = [
        simulate_checkout_completed(),
        simulate_invoice_payment_succeeded(),
        simulate_subscription_deleted(),
    ]

    print("\n🔧 Stripe Webhook Simulator — ShadowTag-v4")
    print(f"   Target: {args.target}")
    print(f"   Events: {len(events)}")
    print(f"   Time: {datetime.utcnow().isoformat()}Z")

    if args.dry_run:
        print("\n📋 DRY RUN — printing payloads only:\n")
        for event in events:
            print(json.dumps(event, indent=2))
            print()
        return

    results = []
    for event in events:
        result = send_webhook(args.target, event)
        results.append(result)

    print(f"\n{'='*60}")
    print("📊 Summary:")
    for r in results:
        icon = "✅" if r["success"] else "❌"
        print(f"   {icon} {r['event_type']}: HTTP {r['status_code']}")
    print(f"   Total: {sum(1 for r in results if r['success'])}/{len(results)} successful")


if __name__ == "__main__":
    main()
