"""Calendar Integration Service
Integrates with Google Calendar, Outlook, and other calendar providers
"""

import asyncio
from datetime import date, timedelta
from enum import StrEnum
from typing import Any


class CalendarProvider(StrEnum):
    """Supported calendar providers"""

    GOOGLE = "google"
    OUTLOOK = "outlook"
    APPLE = "apple"
    CALDAV = "caldav"


class NotificationChannel(StrEnum):
    """Notification delivery channels"""

    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    PUSH = "push"
    WEBHOOK = "webhook"


class CalendarService:
    """Manages calendar synchronization and event creation

    Supports:
    - Google Calendar API
    - Microsoft Outlook API
    - Apple Calendar (CalDAV)
    - Generic CalDAV servers
    """

    def __init__(self, credentials_path: str | None = None):
        """Initialize calendar service

        Args:
            credentials_path: Path to service account credentials

        """
        self.google_client = None
        self.outlook_client = None
        self.credentials_path = credentials_path

    async def create_deadline_event(
        self,
        provider: CalendarProvider,
        calendar_id: str,
        deadline_id: str,
        deadline_date: date,
        title: str,
        description: str,
        case_number: str | None = None,
        document_links: list[str] | None = None,
        reminders: list[int] | None = None,
    ) -> str:
        """Create calendar event for deadline

        Args:
            provider: Calendar provider
            calendar_id: Target calendar ID
            deadline_id: Internal deadline ID
            deadline_date: Deadline date
            title: Event title
            description: Event description
            case_number: Case/matter number
            document_links: Links to related documents
            reminders: Reminder minutes before event

        Returns:
            Event ID from calendar provider

        """
        if provider == CalendarProvider.GOOGLE:
            return await self._create_google_event(
                calendar_id,
                deadline_id,
                deadline_date,
                title,
                description,
                case_number,
                document_links,
                reminders,
            )
        if provider == CalendarProvider.OUTLOOK:
            return await self._create_outlook_event(
                calendar_id,
                deadline_id,
                deadline_date,
                title,
                description,
                case_number,
                document_links,
                reminders,
            )
        raise ValueError(f"Unsupported calendar provider: {provider}")

    async def _create_google_event(
        self,
        calendar_id: str,
        deadline_id: str,
        deadline_date: date,
        title: str,
        description: str,
        case_number: str | None,
        document_links: list[str] | None,
        reminders: list[int] | None,
    ) -> str:
        """Create Google Calendar event"""
        # TODO: Implement Google Calendar API integration
        # from google.oauth2 import service_account
        # from googleapiclient.discovery import build

        # Build event description with all details
        full_description = self._build_event_description(
            description, case_number, document_links, deadline_id,
        )

        # Event structure
        {
            "summary": title,
            "description": full_description,
            "start": {
                "date": deadline_date.isoformat(),
                "timeZone": "America/New_York",  # TODO: Make configurable
            },
            "end": {
                "date": deadline_date.isoformat(),
                "timeZone": "America/New_York",
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": minutes}
                    for minutes in (reminders or [1440, 10080, 20160])  # 1, 7, 14 days
                ],
            },
            "extendedProperties": {
                "private": {"deadline_id": deadline_id, "source": "zero_touch_legal_deadlines"},
            },
        }

        # TODO: Call Google Calendar API
        # service = build('calendar', 'v3', credentials=credentials)
        # created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        # return created_event['id']

        # Mock return for now
        return f"google_event_{deadline_id}"

    async def _create_outlook_event(
        self,
        calendar_id: str,
        deadline_id: str,
        deadline_date: date,
        title: str,
        description: str,
        case_number: str | None,
        document_links: list[str] | None,
        reminders: list[int] | None,
    ) -> str:
        """Create Outlook/Microsoft 365 event"""
        # TODO: Implement Microsoft Graph API integration

        full_description = self._build_event_description(
            description, case_number, document_links, deadline_id,
        )

        # Event structure for Microsoft Graph API
        {
            "subject": title,
            "body": {"contentType": "HTML", "content": full_description},
            "start": {
                "dateTime": f"{deadline_date.isoformat()}T00:00:00",
                "timeZone": "Eastern Standard Time",  # TODO: Make configurable
            },
            "end": {
                "dateTime": f"{deadline_date.isoformat()}T23:59:59",
                "timeZone": "Eastern Standard Time",
            },
            "isAllDay": True,
            "reminderMinutesBeforeStart": reminders[0] if reminders else 1440,
            "importance": "high",
        }

        # TODO: Call Microsoft Graph API
        # POST https://graph.microsoft.com/v1.0/me/calendars/{calendar_id}/events

        # Mock return for now
        return f"outlook_event_{deadline_id}"

    def _build_event_description(
        self,
        description: str,
        case_number: str | None,
        document_links: list[str] | None,
        deadline_id: str,
    ) -> str:
        """Build comprehensive event description"""
        parts = [description]

        if case_number:
            parts.append(f"\n\nCase Number: {case_number}")

        if document_links:
            parts.append("\n\nRelated Documents:")
            for link in document_links:
                parts.append(f"- {link}")

        parts.append(f"\n\nDeadline ID: {deadline_id}")
        parts.append("Managed by Zero-Touch Legal Deadline Management System")

        return "\n".join(parts)

    async def update_event(
        self, provider: CalendarProvider, calendar_id: str, event_id: str, updates: dict[str, Any],
    ) -> bool:
        """Update existing calendar event"""
        # TODO: Implement update logic for each provider
        return True

    async def delete_event(
        self, provider: CalendarProvider, calendar_id: str, event_id: str,
    ) -> bool:
        """Delete calendar event"""
        # TODO: Implement delete logic for each provider
        return True


class ReminderService:
    """Manages reminder notifications across multiple channels

    Cascading reminders:
    - STANDARD: 30, 14, 7, 1 days before
    - INTENSIVE: 30, 14, 7, 3, 1 days before
    - CRITICAL: 30, 14, 7, 5, 3, 2, 1 days before
    """

    STANDARD_DAYS = [30, 14, 7, 1]
    INTENSIVE_DAYS = [30, 14, 7, 3, 1]
    CRITICAL_DAYS = [30, 14, 7, 5, 3, 2, 1]

    def __init__(self):
        """Initialize reminder service"""
        self.email_client = None
        self.sms_client = None
        self.slack_client = None

    def get_reminder_dates(self, deadline_date: date, frequency: str) -> list[date]:
        """Calculate reminder dates based on frequency

        Args:
            deadline_date: The deadline date
            frequency: STANDARD, INTENSIVE, or CRITICAL

        Returns:
            List of reminder dates

        """
        if frequency == "STANDARD":
            days = self.STANDARD_DAYS
        elif frequency == "INTENSIVE":
            days = self.INTENSIVE_DAYS
        elif frequency == "CRITICAL":
            days = self.CRITICAL_DAYS
        else:
            days = self.STANDARD_DAYS

        reminder_dates = []
        for days_before in days:
            reminder_date = deadline_date - timedelta(days=days_before)
            if reminder_date >= date.today():
                reminder_dates.append(reminder_date)

        return reminder_dates

    async def send_reminder(
        self,
        deadline_id: str,
        deadline_date: date,
        title: str,
        description: str,
        case_number: str | None,
        recipients: list[str],
        channels: list[NotificationChannel],
        days_until_deadline: int,
    ):
        """Send reminder notification

        Args:
            deadline_id: Deadline identifier
            deadline_date: Deadline date
            title: Deadline title
            description: Deadline description
            case_number: Case number
            recipients: List of recipient emails/phones
            channels: Notification channels to use
            days_until_deadline: Days remaining

        """
        # Build reminder message
        urgency = self._get_urgency_level(days_until_deadline)
        message = self._build_reminder_message(
            title, description, case_number, deadline_date, days_until_deadline, urgency,
        )

        # Send via each channel
        tasks = []
        for channel in channels:
            if channel == NotificationChannel.EMAIL:
                tasks.append(self._send_email_reminder(recipients, message, urgency))
            elif channel == NotificationChannel.SMS:
                tasks.append(self._send_sms_reminder(recipients, message))
            elif channel == NotificationChannel.SLACK:
                tasks.append(self._send_slack_reminder(recipients, message, urgency))
            elif channel == NotificationChannel.PUSH:
                tasks.append(self._send_push_reminder(recipients, message, urgency))

        await asyncio.gather(*tasks)

    def _get_urgency_level(self, days_until: int) -> str:
        """Determine urgency level based on days remaining"""
        if days_until <= 1:
            return "CRITICAL"
        if days_until <= 3:
            return "HIGH"
        if days_until <= 7:
            return "MEDIUM"
        return "NORMAL"

    def _build_reminder_message(
        self,
        title: str,
        description: str,
        case_number: str | None,
        deadline_date: date,
        days_until: int,
        urgency: str,
    ) -> dict[str, str]:
        """Build reminder message with HTML and plain text versions"""
        urgency_emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "⏰", "NORMAL": "📅"}

        emoji = urgency_emoji.get(urgency, "📅")

        subject = f"{emoji} Legal Deadline Alert: {title} - {days_until} day(s) remaining"

        plain_text = f"""
{emoji} LEGAL DEADLINE REMINDER {emoji}

Deadline: {title}
Due Date: {deadline_date.strftime("%B %d, %Y")}
Days Remaining: {days_until}
Urgency: {urgency}
{f"Case Number: {case_number}" if case_number else ""}

Description:
{description}

⚖️ This is an automated reminder from the Zero-Touch Legal Deadline Management System.
Please ensure timely compliance to avoid missed deadlines.
        """.strip()

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px;">
            <div style="background-color: {"#d32f2f" if urgency == "CRITICAL" else "#f57c00" if urgency == "HIGH" else "#ffa726" if urgency == "MEDIUM" else "#42a5f5"}; color: white; padding: 20px; border-radius: 5px;">
                <h2>{emoji} LEGAL DEADLINE REMINDER</h2>
            </div>
            <div style="padding: 20px; background-color: #f5f5f5; margin-top: 10px; border-radius: 5px;">
                <h3>{title}</h3>
                <p><strong>Due Date:</strong> {deadline_date.strftime("%B %d, %Y")}</p>
                <p><strong>Days Remaining:</strong> <span style="font-size: 24px; color: {"#d32f2f" if urgency == "CRITICAL" else "#f57c00" if urgency == "HIGH" else "#ffa726"};">{days_until}</span></p>
                <p><strong>Urgency Level:</strong> {urgency}</p>
                {f"<p><strong>Case Number:</strong> {case_number}</p>" if case_number else ""}
            </div>
            <div style="padding: 20px; margin-top: 10px;">
                <h4>Description:</h4>
                <p>{description}</p>
            </div>
            <div style="padding: 20px; background-color: #e3f2fd; margin-top: 10px; border-radius: 5px; font-size: 12px;">
                <p>⚖️ This is an automated reminder from the Zero-Touch Legal Deadline Management System.</p>
                <p>Please ensure timely compliance to avoid missed deadlines.</p>
            </div>
        </body>
        </html>
        """

        return {"subject": subject, "plain_text": plain_text, "html": html}

    async def _send_email_reminder(
        self, recipients: list[str], message: dict[str, str], urgency: str,
    ):
        """Send email reminder"""
        # TODO: Implement email sending via SendGrid, AWS SES, or similar
        # For now, log the action
        print(f"[EMAIL] Sending {urgency} reminder to {recipients}")
        print(f"Subject: {message['subject']}")

    async def _send_sms_reminder(self, recipients: list[str], message: dict[str, str]):
        """Send SMS reminder"""
        # TODO: Implement SMS via Twilio, AWS SNS, or similar
        # SMS should be concise version
        sms_text = message["plain_text"][:160]  # Limit to standard SMS length
        print(f"[SMS] Sending reminder to {recipients}: {sms_text}")

    async def _send_slack_reminder(
        self, recipients: list[str], message: dict[str, str], urgency: str,
    ):
        """Send Slack reminder"""
        # TODO: Implement Slack webhook integration
        # Format as Slack blocks for rich formatting
        print(f"[SLACK] Sending {urgency} reminder to {recipients}")

    async def _send_push_reminder(
        self, recipients: list[str], message: dict[str, str], urgency: str,
    ):
        """Send push notification"""
        # TODO: Implement push notifications via Firebase Cloud Messaging or similar
        print(f"[PUSH] Sending {urgency} push notification to {recipients}")


class VerificationWorkflow:
    """Manages lawyer verification and approval workflow
    """

    def __init__(self):
        """Initialize verification workflow"""

    async def queue_for_review(
        self, deadline_id: str, reason: str, confidence: float, _assigned_to: str | None = None,
    ):
        """Queue deadline for lawyer review

        Args:
            deadline_id: Deadline to review
            reason: Reason for review (low confidence, complex calculation, etc.)
            confidence: AI confidence score
            assigned_to: Assigned lawyer/staff

        """
        # TODO: Implement review queue (database, task queue, etc.)
        print(f"[REVIEW QUEUE] Deadline {deadline_id} queued: {reason} (confidence: {confidence})")

    async def notify_reviewer(
        self, deadline_id: str, reviewer_email: str, _deadline_details: dict[str, Any],
    ):
        """Send notification to assigned reviewer"""
        # TODO: Send email/notification to reviewer
        print(f"[NOTIFICATION] Notifying {reviewer_email} about deadline {deadline_id}")

    async def process_verification(
        self,
        deadline_id: str,
        approved: bool,
        corrected_date: date | None,
        notes: str | None,
        verified_by: str,
    ) -> bool:
        """Process verification response from lawyer

        Args:
            deadline_id: Deadline being verified
            approved: Whether deadline is approved
            corrected_date: Corrected date if applicable
            notes: Verification notes
            verified_by: Verifying user

        Returns:
            Success status

        """
        if approved:
            # Mark as verified, sync to calendar
            print(f"[VERIFIED] Deadline {deadline_id} approved by {verified_by}")
            return True
        # Update deadline with corrections
        print(f"[CORRECTED] Deadline {deadline_id} corrected by {verified_by}")
        if corrected_date:
            # Update deadline date
            # Feed back to ML model for improvement
            pass
        return True

    async def get_pending_reviews(
        self, _assigned_to: str | None = None, limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get list of deadlines pending review"""
        # TODO: Query review queue from database
        return []
