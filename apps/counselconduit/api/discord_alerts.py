# apps/counselconduit/api/discord_alerts.py
"""Discord webhook alerts for payment failures and security events.

Sends structured embed messages to a Discord channel via webhook URL
stored in Google Secret Manager (never hardcoded).
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, UTC
from typing import Any

import httpx

logger = logging.getLogger("counselconduit.discord_alerts")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")


async def send_alert(
    title: str,
    description: str,
    color: int = 0xFF0000,
    fields: list[dict[str, Any]] | None = None,
    mention_role: str | None = None,
) -> bool:
    """Send a Discord embed alert."""
    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not set — alert suppressed: %s", title)
        return False

    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(UTC).isoformat(),
        "footer": {"text": "CounselConduit v3.1.0 | shadowtag-omega-v4"},
    }
    if fields:
        embed["fields"] = fields

    payload: dict[str, Any] = {"embeds": [embed]}
    if mention_role:
        payload["content"] = f"<@&{mention_role}>"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
            r.raise_for_status()
            logger.info("Discord alert sent: %s", title)
            return True
    except Exception as e:
        logger.error("Discord alert failed: %s — %s", title, e)
        return False


async def alert_payment_failure(
    attorney_id: str, firm_id: str, amount_cents: int, error: str,
) -> bool:
    """Alert on Stripe payment failure."""
    return await send_alert(
        title="Payment Failure",
        description=f"Stripe charge failed for attorney `{attorney_id}`",
        color=0xFF0000,
        fields=[
            {"name": "Firm", "value": firm_id, "inline": True},
            {"name": "Amount", "value": f"${amount_cents / 100:.2f}", "inline": True},
            {"name": "Error", "value": error, "inline": False},
        ],
    )


async def alert_security_event(
    event_type: str, source_ip: str, details: str,
) -> bool:
    """Alert on security events."""
    return await send_alert(
        title="Security Event",
        description=f"**{event_type}** detected",
        color=0xFF8C00,
        fields=[
            {"name": "Source IP", "value": source_ip, "inline": True},
            {"name": "Details", "value": details, "inline": False},
        ],
    )


async def alert_gdpr_deletion(user_id: str, receipt_id: str) -> bool:
    """Alert when GDPR deletion is scheduled."""
    return await send_alert(
        title="GDPR Deletion Scheduled",
        description=f"30-day hard delete queued for user `{user_id}`",
        color=0x00FF00,
        fields=[{"name": "Receipt", "value": receipt_id, "inline": True}],
    )
