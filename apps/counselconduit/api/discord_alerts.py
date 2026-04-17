# apps/counselconduit/api/discord_alerts.py
"""Discord webhook integration for error alerting.

Sends critical alerts (payment failures, high error rates, governance blocks)
to a Discord channel via webhook.
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timezone

import httpx

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
logger = logging.getLogger(__name__)


async def send_alert(
    title: str,
    description: str,
    color: int = 0xFF4444,  # Red
    fields: list[dict] | None = None,
) -> bool:
    """Send an alert to the Discord webhook.

    Args:
        title: Alert title.
        description: Alert description.
        color: Embed color (hex). Red=0xFF4444, Amber=0xFFBB33, Green=0x34D399.
        fields: Optional list of {"name": str, "value": str, "inline": bool}.

    Returns:
        True if sent successfully.
    """
    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not configured — alert dropped")
        return False

    embed = {
        "title": f"🚨 {title}",
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": "CounselConduit Alert System"},
    }
    if fields:
        embed["fields"] = fields

    payload = {
        "username": "KovelAI Alerts",
        "avatar_url": "https://kovelai.web.app/images/circuit-leaf-logo.png",
        "embeds": [embed],
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
            return resp.status_code == 204
    except Exception as e:
        logger.error("discord_alert_failed", exc_info=e)
        return False


# ── Pre-built Alerts ──────────────────────────────────────────────────────


async def alert_payment_failed(attorney_id: str, attempt: int, amount: str):
    """Alert when a payment fails."""
    await send_alert(
        title="Payment Failed",
        description=f"Attorney `{attorney_id}` payment failed (attempt {attempt}/4)",
        color=0xFF4444,
        fields=[
            {"name": "Amount", "value": amount, "inline": True},
            {"name": "Attempt", "value": f"{attempt}/4", "inline": True},
        ],
    )


async def alert_governance_block(attorney_id: str, risk_score: int, query_preview: str):
    """Alert when Judge #6 blocks a response."""
    await send_alert(
        title="Governance Block (RED)",
        description=f"Judge #6 blocked response for `{attorney_id}`",
        color=0xFF4444,
        fields=[
            {"name": "Risk Score", "value": str(risk_score), "inline": True},
            {"name": "Query Preview", "value": query_preview[:100], "inline": False},
        ],
    )


async def alert_high_error_rate(error_pct: float, window_minutes: int):
    """Alert when 5xx error rate exceeds threshold."""
    await send_alert(
        title="High Error Rate",
        description=f"5xx error rate at {error_pct:.1f}% over {window_minutes}min",
        color=0xFFBB33,
    )


async def alert_token_budget(attorney_id: str, used: int, limit: int):
    """Alert when attorney approaches token budget."""
    pct = int(used / limit * 100)
    await send_alert(
        title="Token Budget Warning",
        description=f"Attorney `{attorney_id}` at {pct}% token usage",
        color=0xFFBB33,
        fields=[
            {"name": "Used", "value": f"{used:,}", "inline": True},
            {"name": "Limit", "value": f"{limit:,}", "inline": True},
        ],
    )
