# apps/counselconduit/api/workspace_alerts.py
"""Google Workspace alerts for CounselConduit operations.

Replaces Discord + Resend with native Google Workspace:
  - Gmail API for transactional emails (onboarding, receipts, GDPR notices)
  - Google Chat API for real-time ops alerts (payment failures, security events)

Uses `gws` CLI (googleworkspace/cli) for agent-driven sends,
or direct Google API calls via `google-api-python-client` in production.

Auth: ADC (Application Default Credentials) via service account with
domain-wide delegation, or OAuth 2.0 for user-context sends.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess

logger = logging.getLogger("counselconduit.workspace_alerts")

# Google Chat space for ops alerts (format: "spaces/XXXXX")
CHAT_SPACE = os.getenv("GOOGLE_CHAT_SPACE", "")

# Sender email for Gmail (must be delegated or the authenticated user)
GMAIL_SENDER = os.getenv("GMAIL_SENDER", "ops@shadowtagai.com")

# gws binary path
GWS_BIN = os.getenv("GWS_BIN", "gws")


# ── Google Chat Alerts (replaces Discord) ──────────────────────────────


async def send_chat_alert(
    text: str,
    thread_key: str | None = None,
) -> bool:
    """Send alert to Google Chat space via gws CLI.

    In production (Cloud Run), use the Google Chat API directly.
    Locally, shells out to `gws chat spaces messages create`.
    """
    if not CHAT_SPACE:
        logger.warning("GOOGLE_CHAT_SPACE not set — alert suppressed: %s", text[:80])
        return False

    try:
        # Try direct API first (production path)
        return await _send_chat_api(text, thread_key)
    except Exception:
        # Fallback to gws CLI (local dev path)
        return _send_chat_cli(text, thread_key)


async def _send_chat_api(text: str, thread_key: str | None = None) -> bool:
    """Send via Google Chat API (googleapiclient)."""
    try:
        from googleapiclient.discovery import build
        import google.auth

        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/chat.messages.create"])
        service = build("chat", "v1", credentials=credentials)

        message = {"text": text}
        if thread_key:
            message["thread"] = {"threadKey": thread_key}

        result = (
            service.spaces()
            .messages()
            .create(
                parent=CHAT_SPACE,
                body=message,
                messageReplyOption="REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD" if thread_key else None,
            )
            .execute()
        )

        logger.info("Chat alert sent: %s", result.get("name", "unknown"))
        return True
    except Exception as e:
        logger.warning("Chat API failed, falling back to CLI: %s", e)
        raise


def _send_chat_cli(text: str, thread_key: str | None = None) -> bool:
    """Send via gws CLI (local dev fallback)."""
    try:
        cmd = [
            GWS_BIN,
            "chat",
            "spaces",
            "messages",
            "create",
            "--params",
            json.dumps({"parent": CHAT_SPACE}),
            "--json",
            json.dumps({"text": text}),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("Chat alert sent via CLI")
            return True
        logger.error("gws CLI failed: %s", result.stderr[:200])
        return False
    except Exception as e:
        logger.error("Chat CLI alert failed: %s", e)
        return False


# ── Gmail Email Service (replaces Resend) ──────────────────────────────


async def send_email(
    to: str,
    subject: str,
    body_html: str,
    reply_to: str | None = None,
) -> bool:
    """Send email via Gmail API.

    In production, uses service account with domain-wide delegation.
    Locally, uses gws CLI with OAuth.
    """
    try:
        return await _send_gmail_api(to, subject, body_html, reply_to)
    except Exception:
        return _send_gmail_cli(to, subject, body_html)


async def _send_gmail_api(
    to: str,
    subject: str,
    body_html: str,
    reply_to: str | None = None,
) -> bool:
    """Send via Gmail API (google-api-python-client)."""
    import base64
    from email.mime.text import MIMEText
    from googleapiclient.discovery import build
    import google.auth

    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/gmail.send"])
    service = build("gmail", "v1", credentials=credentials)

    message = MIMEText(body_html, "html")
    message["to"] = to
    message["from"] = GMAIL_SENDER
    message["subject"] = subject
    if reply_to:
        message["reply-to"] = reply_to

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    logger.info("Gmail sent to %s: %s", to, result.get("id", "unknown"))
    return True


def _send_gmail_cli(to: str, subject: str, body_html: str) -> bool:
    """Send via gws CLI (local dev)."""
    try:
        import base64
        from email.mime.text import MIMEText

        msg = MIMEText(body_html, "html")
        msg["to"] = to
        msg["from"] = GMAIL_SENDER
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        cmd = [
            GWS_BIN,
            "gmail",
            "users",
            "messages",
            "send",
            "--params",
            json.dumps({"userId": "me"}),
            "--json",
            json.dumps({"raw": raw}),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            logger.info("Gmail sent via CLI to %s", to)
            return True
        logger.error("gws gmail CLI failed: %s", result.stderr[:200])
        return False
    except Exception as e:
        logger.error("Gmail CLI failed: %s", e)
        return False


# ── Convenience Alert Functions (same interface as discord_alerts.py) ──


async def alert_payment_failure(
    attorney_id: str,
    firm_id: str,
    amount_cents: int,
    error: str,
) -> bool:
    """Alert on Stripe payment failure via Google Chat."""
    text = f"🚨 *Payment Failure*\nAttorney: `{attorney_id}` | Firm: `{firm_id}`\nAmount: ${amount_cents / 100:.2f}\nError: {error}"
    return await send_chat_alert(text, thread_key="payment-failures")


async def alert_security_event(
    event_type: str,
    source_ip: str,
    details: str,
) -> bool:
    """Alert on security events via Google Chat."""
    text = f"⚠️ *Security Event: {event_type}*\nSource IP: `{source_ip}`\nDetails: {details}"
    return await send_chat_alert(text, thread_key="security-events")


async def alert_gdpr_deletion(user_id: str, receipt_id: str) -> bool:
    """Alert when GDPR deletion is scheduled via Google Chat."""
    text = f"🗑️ *GDPR Deletion Scheduled*\nUser: `{user_id}`\nReceipt: `{receipt_id}`\nHard delete in 30 days."
    return await send_chat_alert(text, thread_key="gdpr-deletions")


async def send_onboarding_email(
    to: str,
    attorney_name: str,
    firm_name: str,
) -> bool:
    """Send attorney onboarding welcome email via Gmail."""
    subject = f"Welcome to CounselConduit — {firm_name}"
    body = f"""
    <h2>Welcome, {attorney_name}!</h2>
    <p>Your firm <strong>{firm_name}</strong> has been onboarded to CounselConduit.</p>
    <p>Your AI-powered legal research portal is ready.</p>
    <p>— The CounselConduit Team</p>
    """
    return await send_email(to, subject, body)
