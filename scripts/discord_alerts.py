"""Discord webhook alert utility for CounselConduit.

Sends structured alerts to Discord channels for operational events:
- Deployment notifications
- Error alerts
- Billing events
- Security incidents

Usage:
    from scripts.discord_alerts import send_alert, AlertLevel

    await send_alert(
        AlertLevel.SUCCESS,
        title="Deployment Complete",
        description="CounselConduit v3.2.0 deployed to Cloud Run",
        fields={"Region": "us-central1", "Duration": "47s"},
    )

Environment:
    DISCORD_WEBHOOK_URL: Required. Discord webhook URL.
    DISCORD_WEBHOOK_URL_ALERTS: Optional. Separate channel for critical alerts.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels mapped to Discord embed colors."""

    SUCCESS = 0x22C55E  # green-500
    INFO = 0x3B82F6  # blue-500
    WARNING = 0xF59E0B  # amber-500
    ERROR = 0xEF4444  # red-500
    CRITICAL = 0x991B1B  # red-800


# ── Embed Builder ─────────────────────────────────────────────────────


def _build_embed(
    level: AlertLevel,
    title: str,
    description: str | None = None,
    fields: dict[str, str] | None = None,
    footer: str | None = None,
) -> dict[str, Any]:
    """Build a Discord embed payload."""
    embed: dict[str, Any] = {
        "title": f"{_level_emoji(level)} {title}",
        "color": level.value,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if description:
        embed["description"] = description
    if fields:
        embed["fields"] = [{"name": k, "value": str(v), "inline": len(str(v)) < 40} for k, v in fields.items()]
    if footer:
        embed["footer"] = {"text": footer}
    else:
        embed["footer"] = {"text": "ShadowTagAI · CounselConduit"}
    return embed


def _level_emoji(level: AlertLevel) -> str:
    return {
        AlertLevel.SUCCESS: "✅",
        AlertLevel.INFO: "ℹ️",
        AlertLevel.WARNING: "⚠️",
        AlertLevel.ERROR: "❌",
        AlertLevel.CRITICAL: "🚨",
    }.get(level, "📌")


# ── Sender ────────────────────────────────────────────────────────────


def send_alert(
    level: AlertLevel,
    title: str,
    description: str | None = None,
    fields: dict[str, str] | None = None,
    footer: str | None = None,
    webhook_url: str | None = None,
) -> bool:
    """Send an alert to Discord. Returns True on success.

    Uses DISCORD_WEBHOOK_URL env var if webhook_url not provided.
    For CRITICAL alerts, also sends to DISCORD_WEBHOOK_URL_ALERTS if set.
    """
    url = webhook_url or os.environ.get("DISCORD_WEBHOOK_URL", "")
    if not url:
        logger.warning("DISCORD_WEBHOOK_URL not set — alert suppressed: %s", title)
        return False

    embed = _build_embed(level, title, description, fields, footer)
    payload = json.dumps({"embeds": [embed]}).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status not in (200, 204):
                logger.error("Discord webhook returned %d", resp.status)
                return False
    except urllib.error.URLError as exc:
        logger.exception("Discord webhook failed: %s", exc)
        return False

    # Also send critical alerts to secondary channel
    if level == AlertLevel.CRITICAL:
        alerts_url = os.environ.get("DISCORD_WEBHOOK_URL_ALERTS", "")
        if alerts_url and alerts_url != url:
            try:
                req2 = urllib.request.Request(
                    alerts_url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                urllib.request.urlopen(req2, timeout=10)
            except urllib.error.URLError:
                pass  # Best-effort for secondary channel

    logger.info("Discord alert sent: %s", title)
    return True


# ── Convenience Functions ─────────────────────────────────────────────


def alert_deploy(
    service: str,
    version: str,
    region: str = "us-central1",
    duration_s: float | None = None,
) -> bool:
    """Send a deployment success alert."""
    fields = {"Service": service, "Version": version, "Region": region}
    if duration_s is not None:
        fields["Duration"] = f"{duration_s:.1f}s"
    return send_alert(
        AlertLevel.SUCCESS,
        title=f"Deploy: {service}",
        description=f"`{service}` version `{version}` deployed successfully.",
        fields=fields,
    )


def alert_error(
    service: str,
    error_msg: str,
    trace: str | None = None,
) -> bool:
    """Send an error alert."""
    fields: dict[str, str] = {"Service": service}
    desc = f"```\n{error_msg}\n```"
    if trace:
        desc += f"\n**Stack trace:**\n```\n{trace[:1000]}\n```"
    return send_alert(
        AlertLevel.ERROR,
        title=f"Error: {service}",
        description=desc,
        fields=fields,
    )


def alert_billing(
    event: str,
    tenant_id: str,
    amount: str | None = None,
) -> bool:
    """Send a billing event alert."""
    fields: dict[str, str] = {"Event": event, "Tenant": tenant_id}
    if amount:
        fields["Amount"] = amount
    return send_alert(
        AlertLevel.INFO,
        title=f"Billing: {event}",
        fields=fields,
    )


# ── CLI ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    level_name = sys.argv[1] if len(sys.argv) > 1 else "INFO"
    title = sys.argv[2] if len(sys.argv) > 2 else "Test Alert"
    desc = sys.argv[3] if len(sys.argv) > 3 else "This is a test alert from discord_alerts.py"

    level = AlertLevel[level_name.upper()]
    ok = send_alert(level, title, desc)
    sys.exit(0 if ok else 1)
