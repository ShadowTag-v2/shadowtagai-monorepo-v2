"""Email provider integrations"""

from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import aiosmtplib
import httpx

from src.core.exceptions import EmailProviderError
from src.core.logging import get_logger
from src.core.settings import get_settings

settings = get_settings()
logger = get_logger(__name__)


class EmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    async def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an email"""
        pass


class SMTPProvider(EmailProvider):
    """SMTP email provider"""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_TLS

    async def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = (
                f"{from_name or settings.EMAIL_FROM_NAME} <{from_email or settings.EMAIL_FROM}>"
            )
            message["To"] = to_email

            # Add text and HTML parts
            if body_text:
                part1 = MIMEText(body_text, "plain")
                message.attach(part1)

            part2 = MIMEText(body_html, "html")
            message.attach(part2)

            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.host, port=self.port, use_tls=self.use_tls
            ) as smtp:
                if self.username and self.password:
                    await smtp.login(self.username, self.password)

                await smtp.send_message(message)

            logger.info(f"Email sent via SMTP to {to_email}")
            return {"success": True, "provider": "smtp", "message_id": None}

        except Exception as e:
            logger.error(f"SMTP send failed: {str(e)}")
            raise EmailProviderError(f"SMTP send failed: {str(e)}")


class SendGridProvider(EmailProvider):
    """SendGrid email provider"""

    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.base_url = "https://api.sendgrid.com/v3"

    async def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send email via SendGrid API"""
        if not self.api_key:
            raise EmailProviderError("SendGrid API key not configured")

        try:
            payload = {
                "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
                "from": {
                    "email": from_email or settings.EMAIL_FROM,
                    "name": from_name or settings.EMAIL_FROM_NAME,
                },
                "content": [{"type": "text/html", "value": body_html}],
            }

            if body_text:
                payload["content"].insert(0, {"type": "text/plain", "value": body_text})

            if metadata:
                payload["custom_args"] = metadata

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code >= 400:
                    raise EmailProviderError(f"SendGrid API error: {response.text}")

            logger.info(f"Email sent via SendGrid to {to_email}")
            message_id = response.headers.get("X-Message-Id")
            return {"success": True, "provider": "sendgrid", "message_id": message_id}

        except httpx.HTTPError as e:
            logger.error(f"SendGrid HTTP error: {str(e)}")
            raise EmailProviderError(f"SendGrid send failed: {str(e)}")
        except Exception as e:
            logger.error(f"SendGrid send failed: {str(e)}")
            raise EmailProviderError(f"SendGrid send failed: {str(e)}")


class MailgunProvider(EmailProvider):
    """Mailgun email provider"""

    def __init__(self):
        self.api_key = settings.MAILGUN_API_KEY
        self.domain = settings.MAILGUN_DOMAIN
        self.base_url = f"https://api.mailgun.net/v3/{self.domain}"

    async def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        from_email: str | None = None,
        from_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send email via Mailgun API"""
        if not self.api_key or not self.domain:
            raise EmailProviderError("Mailgun API key or domain not configured")

        try:
            data = {
                "from": f"{from_name or settings.EMAIL_FROM_NAME} <{from_email or settings.EMAIL_FROM}>",
                "to": to_email,
                "subject": subject,
                "html": body_html,
            }

            if body_text:
                data["text"] = body_text

            if metadata:
                for key, value in metadata.items():
                    data[f"v:{key}"] = str(value)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages", auth=("api", self.api_key), data=data, timeout=30.0
                )

                if response.status_code >= 400:
                    raise EmailProviderError(f"Mailgun API error: {response.text}")

                result = response.json()

            logger.info(f"Email sent via Mailgun to {to_email}")
            return {"success": True, "provider": "mailgun", "message_id": result.get("id")}

        except httpx.HTTPError as e:
            logger.error(f"Mailgun HTTP error: {str(e)}")
            raise EmailProviderError(f"Mailgun send failed: {str(e)}")
        except Exception as e:
            logger.error(f"Mailgun send failed: {str(e)}")
            raise EmailProviderError(f"Mailgun send failed: {str(e)}")


class EmailProviderFactory:
    """Factory for creating email providers"""

    @staticmethod
    def get_provider(provider_name: str | None = None) -> EmailProvider:
        """Get email provider instance"""
        # Auto-detect based on configuration
        if provider_name is None:
            if settings.SENDGRID_API_KEY:
                provider_name = "sendgrid"
            elif settings.MAILGUN_API_KEY and settings.MAILGUN_DOMAIN:
                provider_name = "mailgun"
            else:
                provider_name = "smtp"

        providers = {"smtp": SMTPProvider, "sendgrid": SendGridProvider, "mailgun": MailgunProvider}

        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown email provider: {provider_name}")

        return provider_class()
