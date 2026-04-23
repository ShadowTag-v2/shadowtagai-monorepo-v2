"""FinJudge Signup Automation
Webhook handler for Typeform → Email → API Key flow
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, EmailStr

from .auth import APIKeyManager, TierLevel

router = APIRouter(prefix="/signup", tags=["Signup"])

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "hello@finjudge.dev")

# Typeform webhook secret
TYPEFORM_SECRET = os.getenv("TYPEFORM_WEBHOOK_SECRET", "")


# ============================================================================
# Request Models
# ============================================================================


class TypeformResponse(BaseModel):
    """Typeform webhook payload"""

    event_id: str
    event_type: str
    form_response: dict


class SignupRequest(BaseModel):
    """Manual signup request"""

    email: EmailStr
    organization: str | None = None
    use_case: str | None = None


class SignupResponse(BaseModel):
    """Signup success response"""

    success: bool
    message: str
    api_key: str
    tier: str
    monthly_limit: int
    docs_url: str = "https://finjudge.dev/docs"


# ============================================================================
# Email Templates
# ============================================================================


def get_welcome_email_html(api_key: str, email: str, organization: str | None) -> str:
    """Generate welcome email with API key"""
    org_text = f" at {organization}" if organization else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #ffffff; padding: 30px; border: 1px solid #e0e0e0; border-top: none; }}
            .api-key {{ background: #f5f5f5; padding: 15px; border-left: 4px solid #667eea; font-family: monospace; font-size: 14px; margin: 20px 0; word-break: break-all; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            .tier-info {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to FinJudge!</h1>
                <p>Your Supreme Court Clerk for Financial Decisions</p>
            </div>

            <div class="content">
                <p>Hi{org_text},</p>

                <p>Your FinJudge API key is ready! You now have access to ATP 5-19 risk classification for your financial decisions.</p>

                <h2>Your API Key</h2>
                <div class="api-key">
                    <strong>{api_key}</strong>
                </div>

                <p><strong>⚠️ Important:</strong> This is your only chance to see this key. Store it securely!</p>

                <div class="tier-info">
                    <h3>Free Tier Benefits</h3>
                    <ul>
                        <li>✅ 1,000 risk assessments per month</li>
                        <li>✅ Complete ATP 5-19 classification</li>
                        <li>✅ Immutable audit trails</li>
                        <li>✅ Email support</li>
                        <li>✅ Access to CLI and Python SDK</li>
                    </ul>
                </div>

                <h2>Quick Start</h2>
                <p><strong>1. Test your API key:</strong></p>
                <pre style="background: #f5f5f5; padding: 15px; overflow-x: auto;">
curl -X POST https://api.finjudge.dev/v1/judge \\
  -H "Authorization: Bearer {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "decision_id": "test_001",
    "module": "test",
    "actor": {{"role": "trader", "org_unit": "Test", "jurisdiction": "US"}},
    "intent_nl": "Test decision",
    "context": {{"time_horizon": "swing", "objective": "alpha"}},
    "metrics": {{"exposure": {{"notional": 100000, "pct_aum": 2.0}}}}
  }}'
                </pre>

                <p><strong>2. Install the CLI:</strong></p>
                <pre style="background: #f5f5f5; padding: 15px;">
pip install finjudge
finjudge demo
                </pre>

                <p><strong>3. Check your usage:</strong></p>
                <pre style="background: #f5f5f5; padding: 15px;">
curl https://api.finjudge.dev/v1/usage \\
  -H "Authorization: Bearer {api_key}"
                </pre>

                <a href="https://finjudge.dev/docs" class="button">View Documentation</a>
                <a href="https://finjudge.dev/pricing" class="button">Upgrade to Pro</a>

                <h2>Need Help?</h2>
                <p>📧 Email: support@finjudge.dev<br>
                📚 Docs: <a href="https://finjudge.dev/docs">finjudge.dev/docs</a><br>
                💬 Discord: <a href="https://discord.gg/finjudge">discord.gg/finjudge</a></p>

                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e0e0e0;">

                <p style="font-size: 12px; color: #666;">
                    <strong>What's next?</strong><br>
                    We'll send you tips over the next few days to help you get the most out of FinJudge.
                    You'll learn how to integrate it into your financial workflows, set up custom risk frameworks, and scale to thousands of decisions per day.
                </p>
            </div>

            <div class="footer">
                <p>FinJudge - Supreme Court Clerk for Financial Decisions</p>
                <p>Visit <a href="https://finjudge.dev">finjudge.dev</a> | Follow us on <a href="https://x.com/finjudge">X</a></p>
            </div>
        </div>
    </body>
    </html>
    """


# ============================================================================
# Email Sending
# ============================================================================


def send_welcome_email(api_key: str, email: str, organization: str | None = None):
    """Send welcome email with API key"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"⚠️  Email not configured. API key for {email}: {api_key}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎉 Your FinJudge API Key is Ready!"
    msg["From"] = FROM_EMAIL
    msg["To"] = email

    # Plain text version
    text = f"""
    Welcome to FinJudge!

    Your API key: {api_key}

    Free tier benefits:
    - 1,000 risk assessments per month
    - Complete ATP 5-19 classification
    - Immutable audit trails

    Quick start:
    1. Visit https://finjudge.dev/docs
    2. Install CLI: pip install finjudge
    3. Test: finjudge demo

    Need help? Email support@finjudge.dev

    FinJudge - Supreme Court Clerk for Financial Decisions
    https://finjudge.dev
    """

    # HTML version
    html = get_welcome_email_html(api_key, email, organization)

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"✅ Welcome email sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/typeform", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def typeform_webhook(
    payload: TypeformResponse,
    _typeform_signature: str | None = Header(None, alias="typeform-signature"),
):
    """Typeform webhook handler

    Automatically generates API key when user submits signup form.

    **Setup**:
    1. Create Typeform with fields: email, organization (optional), use_case (optional)
    2. Add webhook: https://api.finjudge.dev/signup/typeform
    3. Set TYPEFORM_WEBHOOK_SECRET environment variable
    """
    # TODO: Verify Typeform signature if TYPEFORM_SECRET is set
    # if TYPEFORM_SECRET and typeform_signature:
    #     verify_typeform_signature(payload, typeform_signature)

    # Extract answers from Typeform payload
    answers = payload.form_response.get("answers", [])

    email = None
    organization = None

    for answer in answers:
        field_type = answer.get("type")

        if field_type == "email":
            email = answer.get("email")
        elif field_type in ["short_text", "long_text"]:
            answer.get("field", {}).get("id", "")
            value = answer.get("text")

            if "organization" in answer.get("field", {}).get("title", "").lower():
                organization = value
            elif "use" in answer.get("field", {}).get("title", "").lower():
                pass

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in Typeform response",
        )

    # Generate API key
    key_manager = APIKeyManager()

    try:
        plaintext_key, api_key_record = key_manager.generate_key(
            email=email,
            organization=organization,
            tier=TierLevel.FREE,
        )

        # Send welcome email
        send_welcome_email(plaintext_key, email, organization)

        return SignupResponse(
            success=True,
            message=f"API key sent to {email}",
            api_key=plaintext_key,
            tier=api_key_record.tier.value,
            monthly_limit=api_key_record.monthly_limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate API key: {e!s}",
        ) from e


@router.post("/manual", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def manual_signup(request: SignupRequest):
    """Manual signup endpoint (for testing or custom integrations)

    **Example**:
    ```bash
    curl -X POST https://api.finjudge.dev/signup/manual \
      -H "Content-Type: application/json" \
      -d '{
        "email": "user@example.com",
        "organization": "Acme Corp"
      }'
    ```
    """
    key_manager = APIKeyManager()

    try:
        plaintext_key, api_key_record = key_manager.generate_key(
            email=request.email,
            organization=request.organization,
            tier=TierLevel.FREE,
        )

        # Send welcome email
        send_welcome_email(plaintext_key, request.email, request.organization)

        return SignupResponse(
            success=True,
            message=f"API key sent to {request.email}",
            api_key=plaintext_key,
            tier=api_key_record.tier.value,
            monthly_limit=api_key_record.monthly_limit,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate API key: {e!s}",
        ) from e
