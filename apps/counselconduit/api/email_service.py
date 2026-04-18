# apps/counselconduit/api/email_service.py
"""Email service for magic-link delivery and lifecycle notifications.

Uses Resend as primary provider. Falls back to structlog for dev mode.

Templates:
- magic_link: client onboarding invitation
- vent_receipt: payment confirmation for Vent Mode
- gdpr_confirmation: deletion request acknowledgment
- attestation_receipt: Kovel attestation receipt PDF
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("counselconduit.email_service")

_RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
_FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@kovelai.com")
_FROM_NAME = os.getenv("FROM_NAME", "KovelAI")


async def send_email(
    to: str,
    subject: str,
    html: str,
    reply_to: str | None = None,
    tags: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Send an email via Resend.

    Returns {"id": "email_id"} on success, {"error": "..."} on failure.
    """
    if not _RESEND_API_KEY:
        logger.info("DEV_MODE: email to=%s subject=%s (no RESEND_API_KEY)", to, subject)
        return {"id": "dev-mode-no-send", "to": to, "subject": subject}

    try:
        import resend

        resend.api_key = _RESEND_API_KEY

        params: dict[str, Any] = {
            "from_": f"{_FROM_NAME} <{_FROM_EMAIL}>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if reply_to:
            params["reply_to"] = reply_to
        if tags:
            params["tags"] = tags

        email = resend.Emails.send(params)
        logger.info("Email sent: to=%s subject=%s id=%s", to, subject, email.get("id"))
        return email

    except ImportError:
        logger.warning("resend not installed — email not sent")
        return {"error": "resend not installed", "to": to}
    except Exception as e:
        logger.error("Email send failed: %s", e)
        return {"error": str(e), "to": to}


# ── Pre-built Email Templates ─────────────────────────────────────────────


async def send_magic_link_email(
    to: str,
    attorney_name: str,
    firm_name: str,
    magic_link: str,
    matter_description: str = "",
) -> dict[str, Any]:
    """Send a magic link invitation email to a client."""
    html = f"""
    <div style="font-family: 'Inter', -apple-system, sans-serif; max-width: 580px; margin: 0 auto; padding: 40px 20px;">
      <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 16px; padding: 40px; color: #e2e8f0;">
        <div style="text-align: center; margin-bottom: 32px;">
          <h1 style="font-size: 24px; font-weight: 700; margin: 0; color: #f8fafc;">
            You've been invited to a secure research session
          </h1>
        </div>
        <p style="font-size: 16px; line-height: 1.6; margin: 0 0 16px; color: #cbd5e1;">
          <strong>{attorney_name}</strong> at <strong>{firm_name}</strong> has set up a
          confidential AI-powered legal research session for you.
        </p>
        {"<p style='font-size: 14px; line-height: 1.5; margin: 0 0 24px; color: #94a3b8; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px;'>" + matter_description + "</p>" if matter_description else ""}
        <div style="text-align: center; margin: 32px 0;">
          <a href="{magic_link}" style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
            Access Your Portal
          </a>
        </div>
        <p style="font-size: 12px; color: #64748b; text-align: center; margin: 24px 0 0;">
          This link expires in 72 hours and can only be used once.<br/>
          All communications are protected under attorney-client privilege.
        </p>
      </div>
      <div style="text-align: center; margin-top: 16px;">
        <p style="font-size: 11px; color: #475569;">
          Powered by <a href="https://kovelai.web.app" style="color: #3b82f6; text-decoration: none;">KovelAI</a>
          — Privilege-preserving legal AI
        </p>
      </div>
    </div>
    """
    return await send_email(
        to=to,
        subject=f"{attorney_name} has invited you to a secure research session",
        html=html,
        tags=[{"name": "type", "value": "magic_link"}],
    )


async def send_vent_receipt(
    to: str,
    amount_display: str,
    session_id: str,
    firm_name: str,
) -> dict[str, Any]:
    """Send a Vent Mode payment receipt."""
    html = f"""
    <div style="font-family: 'Inter', -apple-system, sans-serif; max-width: 580px; margin: 0 auto; padding: 40px 20px;">
      <div style="background: #0f172a; border-radius: 16px; padding: 40px; color: #e2e8f0;">
        <h1 style="font-size: 20px; font-weight: 700; color: #34d399; margin: 0 0 24px;">✓ Payment Confirmed</h1>
        <p style="font-size: 16px; margin: 0 0 16px; color: #cbd5e1;">
          Your intake session with <strong>{firm_name}</strong> has been paid.
        </p>
        <div style="background: rgba(255,255,255,0.05); border-radius: 8px; padding: 16px; margin: 16px 0;">
          <div style="display: flex; justify-content: space-between; margin: 8px 0;">
            <span style="color: #94a3b8;">Amount</span>
            <span style="color: #f8fafc; font-weight: 600;">{amount_display}</span>
          </div>
          <div style="display: flex; justify-content: space-between; margin: 8px 0;">
            <span style="color: #94a3b8;">Session ID</span>
            <span style="color: #f8fafc; font-family: monospace; font-size: 12px;">{session_id[:16]}...</span>
          </div>
        </div>
      </div>
    </div>
    """
    return await send_email(
        to=to,
        subject=f"Payment confirmed — {amount_display} intake session",
        html=html,
        tags=[{"name": "type", "value": "vent_receipt"}],
    )


async def send_gdpr_confirmation(
    to: str,
    request_id: str,
    deletion_date: str,
) -> dict[str, Any]:
    """Send GDPR deletion request confirmation."""
    html = f"""
    <div style="font-family: 'Inter', -apple-system, sans-serif; max-width: 580px; margin: 0 auto; padding: 40px 20px;">
      <div style="background: #0f172a; border-radius: 16px; padding: 40px; color: #e2e8f0;">
        <h1 style="font-size: 20px; font-weight: 700; margin: 0 0 24px;">Account Deletion Request</h1>
        <p style="font-size: 16px; margin: 0 0 16px; color: #cbd5e1;">
          We've received your request to delete your account data.
        </p>
        <div style="background: rgba(255,187,51,0.1); border: 1px solid rgba(255,187,51,0.3); border-radius: 8px; padding: 16px; margin: 16px 0;">
          <p style="color: #fbbf24; font-size: 14px; margin: 0;">
            ⚠️ Your data will be permanently deleted on <strong>{deletion_date}</strong>.
            You can cancel this request within 30 days by contacting support.
          </p>
        </div>
        <p style="font-size: 12px; color: #64748b; margin: 16px 0 0;">
          Request ID: <code style="color: #94a3b8;">{request_id}</code>
        </p>
      </div>
    </div>
    """
    return await send_email(
        to=to,
        subject="Your account deletion request has been received",
        html=html,
        tags=[{"name": "type", "value": "gdpr_confirmation"}],
    )
