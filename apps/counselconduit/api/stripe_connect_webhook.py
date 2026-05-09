# apps/counselconduit/api/stripe_connect_webhook.py
"""Stripe Connect Webhook Handler — onboarding lifecycle events.

Handles Connect-specific events:
- account.updated → Track KYC completion, charges_enabled status
- account.application.deauthorized → Attorney disconnected

This is SEPARATE from the main stripe_handler.py which handles
billing webhooks (checkout, subscriptions, invoices).

Outbound Stripe SDK calls are protected by the 'stripe' circuit breaker
(profile: threshold=3, timeout=60s).
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

logger = logging.getLogger("counselconduit.stripe_connect_webhook")

router = APIRouter(prefix="/webhooks", tags=["Connect Webhooks"])

_CONNECT_WEBHOOK_SECRET = os.getenv("STRIPE_CONNECT_WEBHOOK_SECRET", "")


def _get_stripe_breaker():
    """Lazy-load the circuit breaker for Stripe API calls."""
    try:
        from circuit_breaker.telemetry_bridge import default_registry

        return default_registry.get_or_create(
            "stripe",
            failure_threshold=3,
            reset_timeout_s=60.0,
        )
    except Exception:
        return None


@router.post("/stripe-connect", status_code=status.HTTP_200_OK)
async def stripe_connect_webhook(request: Request) -> dict[str, Any]:
    """Handle Stripe Connect account lifecycle events.

    Verifies signature, then dispatches to handler.
    Returns 503 if the stripe circuit breaker is OPEN.
    """
    raw_body = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not _CONNECT_WEBHOOK_SECRET:
        logger.warning("STRIPE_CONNECT_WEBHOOK_SECRET not set — rejecting")
        raise HTTPException(status_code=500, detail="Connect webhook secret not configured")

    # Circuit breaker gate — skip Stripe SDK calls if API is down
    breaker = _get_stripe_breaker()
    if breaker and not breaker.allow_request():
        logger.warning(
            "Circuit breaker OPEN for stripe — rejecting Connect webhook (probe in %.0fs)",
            breaker.seconds_until_probe,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe API circuit breaker is OPEN — retrying later.",
        )

    # Verify signature
    try:
        import stripe

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        event = stripe.Webhook.construct_event(raw_body, sig_header, _CONNECT_WEBHOOK_SECRET)
        if breaker:
            breaker.record_success()
    except ImportError:
        logger.warning("stripe not installed — parsing raw")
        import json

        event = json.loads(raw_body)
    except Exception as e:
        if breaker:
            breaker.record_failure()
        logger.warning("Connect webhook sig failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid signature") from e

    event_type = event.get("type", "")
    logger.info("Connect event: type=%s", event_type)

    if event_type == "account.updated":
        return _handle_account_updated(event)
    elif event_type == "account.application.deauthorized":
        return _handle_deauthorized(event)

    return {"received": True, "type": event_type}


def _handle_account_updated(event: dict[str, Any]) -> dict[str, Any]:
    """Attorney's Connect account was updated (KYC, bank, etc.)."""
    account = event.get("data", {}).get("object", {})
    account_id = account.get("id", "unknown")
    charges = account.get("charges_enabled", False)
    payouts = account.get("payouts_enabled", False)
    details = account.get("details_submitted", False)

    logger.info(
        "Connect account updated: id=%s charges=%s payouts=%s details=%s",
        account_id,
        charges,
        payouts,
        details,
    )

    # Alert Google Chat when attorney completes onboarding
    if charges and payouts and details:
        import asyncio

        try:
            try:
                from apps.counselconduit.api.workspace_alerts import send_chat_alert
            except ImportError:
                from api.workspace_alerts import send_chat_alert  # type: ignore[no-redef]

            asyncio.create_task(
                send_chat_alert(
                    text=f"🎉 *Attorney Onboarding Complete*\nAccount `{account_id}` is now live — charges and payouts enabled.",
                    thread_key="attorney-onboarding",
                )
            )
        except Exception:
            pass

    return {
        "action": "account_updated",
        "account_id": account_id,
        "charges_enabled": charges,
        "payouts_enabled": payouts,
    }


def _handle_deauthorized(event: dict[str, Any]) -> dict[str, Any]:
    """Attorney disconnected their Stripe account."""
    account = event.get("data", {}).get("object", {})
    account_id = account.get("id", "unknown")
    logger.warning("Connect account deauthorized: id=%s", account_id)
    return {"action": "deauthorized", "account_id": account_id}
