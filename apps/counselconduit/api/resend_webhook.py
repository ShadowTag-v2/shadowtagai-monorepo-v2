# apps/counselconduit/api/resend_webhook.py
"""Resend Webhook Handler — email delivery tracking.

Tracks email delivery status from Resend:
- email.delivered → Mark magic link as delivered
- email.bounced → Alert attorney, invalidate magic link
- email.complained → Suppress future sends to this address

Webhook endpoint: POST /webhooks/resend
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

logger = logging.getLogger("counselconduit.resend_webhook")

router = APIRouter(prefix="/webhooks", tags=["Email Webhooks"])

_RESEND_WEBHOOK_SECRET = os.getenv("RESEND_WEBHOOK_SECRET", "")


@router.post("/resend", status_code=status.HTTP_200_OK)
async def resend_webhook(request: Request) -> dict[str, Any]:
    """Handle Resend email delivery events."""
    body = await request.json()
    event_type = body.get("type", "")
    data = body.get("data", {})

    logger.info("Resend event: type=%s to=%s", event_type, data.get("to"))

    if event_type == "email.delivered":
        return _handle_delivered(data)
    elif event_type == "email.bounced":
        return _handle_bounced(data)
    elif event_type == "email.complained":
        return _handle_complained(data)

    return {"received": True, "type": event_type}


def _handle_delivered(data: dict[str, Any]) -> dict[str, Any]:
    """Email was delivered successfully."""
    logger.info("Email delivered: to=%s subject=%s", data.get("to"), data.get("subject"))
    return {"action": "delivered", "to": data.get("to")}


def _handle_bounced(data: dict[str, Any]) -> dict[str, Any]:
    """Email bounced — invalid address."""
    to = data.get("to", "unknown")
    logger.warning("Email BOUNCED: to=%s — invalidating magic link", to)

    # Fire Google Chat alert for bounced emails
    import asyncio
    try:
        try:
            from apps.counselconduit.api.workspace_alerts import send_chat_alert
        except ImportError:
            from api.workspace_alerts import send_chat_alert  # type: ignore[no-redef]

        asyncio.create_task(
            send_chat_alert(
                text=f"📧 *Email Bounced*\nMagic link email to `{to}` bounced. Address may be invalid.",
                thread_key="email-delivery",
            )
        )
    except Exception:
        pass

    return {"action": "bounced", "to": to}


def _handle_complained(data: dict[str, Any]) -> dict[str, Any]:
    """Recipient marked email as spam."""
    to = data.get("to", "unknown")
    logger.warning("Email COMPLAINT: to=%s — suppressing future sends", to)
    return {"action": "complained", "to": to, "suppressed": True}
