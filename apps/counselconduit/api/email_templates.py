# apps/counselconduit/api/email_templates.py
"""Email Notification Templates for CounselConduit billing events.

Triggered by Stripe webhooks. Sent via Google Workspace / SendGrid.
"""

from __future__ import annotations

WELCOME_EMAIL = {
  "subject": "Welcome to KovelAI — Your Practice is Set Up",
  "html": """
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 560px; margin: 0 auto; background: #0a0d14; color: #e4e8f7; padding: 2rem; border-radius: 12px;">
      <h1 style="color: #c9a14a; font-size: 1.4rem;">🛡️ Welcome to KovelAI</h1>
      <p style="color: #8b92a8; line-height: 1.6;">Your privileged computing environment is now active. All queries are processed under the Kovel Doctrine with zero-retention architecture.</p>
      <a href="https://kovelai.web.app/chat.html" style="display: inline-block; background: #c9a14a; color: #0a0d14; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 1rem 0;">Launch Privileged Chat →</a>
      <p style="font-size: 0.8rem; color: #8b92a8; margin-top: 1.5rem;">This email was sent to {email}. If you didn't create this account, please contact support@kovelai.com.</p>
    </div>
    """,
}

PAYMENT_SUCCESS_EMAIL = {
  "subject": "KovelAI — Payment Confirmed",
  "html": """
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 560px; margin: 0 auto; background: #0a0d14; color: #e4e8f7; padding: 2rem; border-radius: 12px;">
      <h1 style="color: #34d399; font-size: 1.4rem;">✅ Payment Confirmed</h1>
      <p style="color: #8b92a8; line-height: 1.6;">Your {tier} plan payment of ${amount} has been processed successfully.</p>
      <table style="width: 100%; color: #8b92a8; font-size: 0.85rem; margin: 1rem 0;">
        <tr><td>Plan:</td><td style="text-align: right; color: #e4e8f7;">{tier}</td></tr>
        <tr><td>Amount:</td><td style="text-align: right; color: #e4e8f7;">${amount}</td></tr>
        <tr><td>Period:</td><td style="text-align: right; color: #e4e8f7;">{period}</td></tr>
        <tr><td>Token Limit:</td><td style="text-align: right; color: #e4e8f7;">{tokens} tokens/mo</td></tr>
      </table>
      <a href="https://kovelai.web.app/dashboard.html" style="display: inline-block; background: #c9a14a; color: #0a0d14; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600;">View Dashboard</a>
    </div>
    """,
}

PAYMENT_FAILED_EMAIL = {
  "subject": "KovelAI — Payment Failed • Action Required",
  "html": """
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 560px; margin: 0 auto; background: #0a0d14; color: #e4e8f7; padding: 2rem; border-radius: 12px;">
      <h1 style="color: #f87171; font-size: 1.4rem;">⚠️ Payment Failed</h1>
      <p style="color: #8b92a8; line-height: 1.6;">We were unable to process your payment. Your account will enter a grace period. Please update your payment method to avoid service interruption.</p>
      <p style="color: #8b92a8; font-size: 0.85rem;">Attempt {attempt} of 4 • Grace period: 7 days remaining</p>
      <a href="https://kovelai.web.app/pricing.html" style="display: inline-block; background: #f87171; color: #0a0d14; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600;">Update Payment →</a>
    </div>
    """,
}

TOKEN_LIMIT_WARNING_EMAIL = {
  "subject": "KovelAI — 80% Token Usage Reached",
  "html": """
    <div style="font-family: 'Inter', Arial, sans-serif; max-width: 560px; margin: 0 auto; background: #0a0d14; color: #e4e8f7; padding: 2rem; border-radius: 12px;">
      <h1 style="color: #fbbf24; font-size: 1.4rem;">📊 Token Usage Alert</h1>
      <p style="color: #8b92a8; line-height: 1.6;">You've used {used} of your {limit} monthly token allocation ({pct}%). Consider upgrading your plan for uninterrupted service.</p>
      <a href="https://kovelai.web.app/pricing.html" style="display: inline-block; background: #c9a14a; color: #0a0d14; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600;">Upgrade Plan</a>
    </div>
    """,
}
