"""Email automation service layer"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from jinja2 import Template
from sqlalchemy.orm import Session

from src.core.exceptions import (
    InvalidEmailFlow,
    RecipientNotFound,
    TemplateNotFound,
)
from src.core.logging import get_logger
from src.db import models

from . import providers, repository, schemas

logger = get_logger(__name__)


class EmailService:
    """Email automation service"""

    def __init__(self, provider_name: str | None = None):
        self.provider = providers.EmailProviderFactory.get_provider(provider_name)
        self.repo = repository.EmailRepository

    async def send_email(self, db: Session, request: schemas.EmailSendRequest) -> models.Email:
        """Send a single email"""
        # Get or create recipient
        recipient = self.repo.get_recipient_by_email(db, request.recipient_email)
        if not recipient:
            recipient = self.repo.create_recipient(
                db,
                schemas.RecipientCreate(email=request.recipient_email),
            )

        # Get template if specified
        subject = request.subject
        body_html = request.body_html
        body_text = request.body_text

        if request.template_id:
            template = self.repo.get_template(db, request.template_id)
            if not template:
                raise TemplateNotFound(f"Template {request.template_id} not found")

            # Render template with variables
            subject = Template(template.subject).render(**request.variables)
            body_html = Template(template.body_html).render(**request.variables)
            if template.body_text:
                body_text = Template(template.body_text).render(**request.variables)

        # Create tracking ID
        tracking_id = str(uuid.uuid4())

        # Create email record
        email_data = {
            "recipient_id": recipient.id,
            "template_id": request.template_id,
            "subject": subject,
            "body_html": body_html,
            "body_text": body_text,
            "scheduled_at": request.scheduled_at,
            "tracking_id": tracking_id,
            "metadata": request.variables,
            "status": models.EmailStatus.PENDING
            if request.scheduled_at
            else models.EmailStatus.SENDING,
        }
        db_email = self.repo.create_email(db, email_data)

        # Send immediately if not scheduled
        if not request.scheduled_at:
            await self._send_email_now(db, db_email)

        return db_email

    async def _send_email_now(self, db: Session, email: models.Email) -> None:
        """Send email immediately"""
        try:
            # Update status to sending
            self.repo.update_email_status(db, email.id, models.EmailStatus.SENDING)

            # Get recipient
            recipient = self.repo.get_recipient(db, email.recipient_id)
            if not recipient:
                raise RecipientNotFound(f"Recipient {email.recipient_id} not found")

            # Send via provider
            await self.provider.send(
                to_email=recipient.email,
                subject=email.subject,
                body_html=email.body_html,
                body_text=email.body_text,
                metadata={"tracking_id": email.tracking_id},
            )

            # Update status to sent
            self.repo.update_email_status(db, email.id, models.EmailStatus.SENT)

            # Create analytics record
            self.repo.create_analytics(db, email.id)

            logger.info(f"Email {email.id} sent successfully to {recipient.email}")

        except Exception as e:
            logger.error(f"Failed to send email {email.id}: {e!s}")
            self.repo.update_email_status(
                db,
                email.id,
                models.EmailStatus.FAILED,
                error_message=str(e),
            )
            raise

    async def process_email_queue(self, db: Session, batch_size: int = 100) -> int:
        """Process pending emails in queue"""
        pending_emails = self.repo.get_pending_emails(db, limit=batch_size)
        sent_count = 0

        for email in pending_emails:
            try:
                await self._send_email_now(db, email)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to process email {email.id}: {e!s}")
                continue

        return sent_count

    def create_flow(self, db: Session, flow: schemas.EmailFlowCreate) -> models.EmailFlow:
        """Create email flow"""
        # Validate steps
        if not flow.steps:
            raise InvalidEmailFlow("Flow must have at least one step")

        # Ensure steps are ordered correctly
        for i, step in enumerate(flow.steps):
            if step.step_order != i:
                step.step_order = i

        return self.repo.create_flow(db, flow)

    def enroll_recipient(
        self,
        db: Session,
        flow_id: int,
        recipient_email: str,
    ) -> models.FlowEnrollment:
        """Enroll recipient in email flow"""
        # Get or create recipient
        recipient = self.repo.get_recipient_by_email(db, recipient_email)
        if not recipient:
            recipient = self.repo.create_recipient(
                db,
                schemas.RecipientCreate(email=recipient_email),
            )

        # Check if already enrolled
        existing = self.repo.get_enrollment(db, flow_id, recipient.id)
        if existing and existing.active:
            logger.info(f"Recipient {recipient.email} already enrolled in flow {flow_id}")
            return existing

        # Create enrollment
        return self.repo.enroll_recipient(db, flow_id, recipient.id)

    async def bulk_enroll(
        self,
        db: Session,
        request: schemas.BulkEnrollRequest,
    ) -> schemas.BulkEnrollResponse:
        """Bulk enroll recipients in flow"""
        enrollments = []
        errors = []
        enrolled_count = 0
        failed_count = 0

        for email in request.recipient_emails:
            try:
                enrollment = self.enroll_recipient(db, request.flow_id, email)
                enrollments.append(enrollment)
                enrolled_count += 1
            except Exception as e:
                errors.append(f"{email}: {e!s}")
                failed_count += 1
                logger.error(f"Failed to enroll {email}: {e!s}")

        # Convert to response schemas
        enrollment_responses = [
            schemas.FlowEnrollmentResponse.model_validate(e) for e in enrollments
        ]

        return schemas.BulkEnrollResponse(
            enrolled_count=enrolled_count,
            failed_count=failed_count,
            enrollments=enrollment_responses,
            errors=errors,
        )

    async def process_flow_enrollments(self, db: Session) -> int:
        """Process active flow enrollments and send scheduled emails"""
        enrollments = self.repo.get_active_enrollments(db)
        processed_count = 0

        for enrollment in enrollments:
            try:
                await self._process_enrollment(db, enrollment)
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to process enrollment {enrollment.id}: {e!s}")
                continue

        return processed_count

    async def _process_enrollment(self, db: Session, enrollment: models.FlowEnrollment) -> None:
        """Process a single flow enrollment"""
        flow = self.repo.get_flow(db, enrollment.flow_id)
        if not flow or not flow.active:
            return

        # Get current step
        steps = sorted(flow.steps, key=lambda s: s.step_order)
        if enrollment.current_step >= len(steps):
            # Flow completed
            enrollment.completed_at = datetime.utcnow()
            enrollment.active = False
            db.commit()
            return

        current_step = steps[enrollment.current_step]

        # Calculate when to send
        total_delay = timedelta(
            days=current_step.delay_days,
            hours=current_step.delay_hours,
            minutes=current_step.delay_minutes,
        )
        send_time = enrollment.enrolled_at + total_delay

        # Check if it's time to send
        if datetime.utcnow() < send_time:
            return

        # Get template and recipient
        template = self.repo.get_template(db, current_step.template_id)
        recipient = self.repo.get_recipient(db, enrollment.recipient_id)

        if not template or not recipient:
            return

        # Check conditions (if any)
        if current_step.conditions:
            # TODO: Implement condition checking logic
            pass

        # Create and send email
        tracking_id = str(uuid.uuid4())
        email_data = {
            "recipient_id": recipient.id,
            "template_id": template.id,
            "subject": Template(template.subject).render(**recipient.metadata),
            "body_html": Template(template.body_html).render(**recipient.metadata),
            "body_text": Template(template.body_text).render(**recipient.metadata)
            if template.body_text
            else None,
            "tracking_id": tracking_id,
            "metadata": {"flow_id": flow.id, "step": enrollment.current_step},
            "status": models.EmailStatus.SENDING,
        }
        db_email = self.repo.create_email(db, email_data)

        try:
            await self._send_email_now(db, db_email)

            # Move to next step
            enrollment.current_step += 1
            db.commit()

        except Exception as e:
            logger.error(f"Failed to send flow email: {e!s}")
            raise

    def track_open(self, db: Session, tracking_id: str, event_data: dict = None) -> None:
        """Track email open event"""
        if event_data is None:
            event_data = {}
        email = db.query(models.Email).filter(models.Email.tracking_id == tracking_id).first()

        if email:
            # Update email status
            if email.status not in [models.EmailStatus.OPENED, models.EmailStatus.CLICKED]:
                self.repo.update_email_status(db, email.id, models.EmailStatus.OPENED)

            # Update analytics
            self.repo.update_analytics(db, email.id, "open", event_data)

            # Create event
            self.repo.create_event(db, email.id, "open", event_data)

            logger.info(f"Email {email.id} opened")

    def track_click(self, db: Session, tracking_id: str, event_data: dict = None) -> None:
        """Track email click event"""
        if event_data is None:
            event_data = {}
        email = db.query(models.Email).filter(models.Email.tracking_id == tracking_id).first()

        if email:
            # Update email status
            self.repo.update_email_status(db, email.id, models.EmailStatus.CLICKED)

            # Update analytics
            self.repo.update_analytics(db, email.id, "click", event_data)

            # Create event
            self.repo.create_event(db, email.id, "click", event_data)

            logger.info(f"Email {email.id} clicked")

    def get_campaign_metrics(
        self,
        db: Session,
        flow_id: int | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        """Get campaign metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)

        query = db.query(models.Email).filter(models.Email.created_at >= start_date)

        if flow_id:
            query = query.filter(models.Email.metadata["flow_id"].astext == str(flow_id))

        emails = query.all()

        total = len(emails)
        sent = sum(
            1
            for e in emails
            if e.status
            in [
                models.EmailStatus.SENT,
                models.EmailStatus.DELIVERED,
                models.EmailStatus.OPENED,
                models.EmailStatus.CLICKED,
            ]
        )
        delivered = sum(1 for e in emails if e.delivered_at is not None)
        opened = sum(1 for e in emails if e.opened_at is not None)
        clicked = sum(1 for e in emails if e.clicked_at is not None)
        bounced = sum(1 for e in emails if e.status == models.EmailStatus.BOUNCED)
        failed = sum(1 for e in emails if e.status == models.EmailStatus.FAILED)

        return {
            "total_emails": total,
            "emails_sent": sent,
            "emails_delivered": delivered,
            "emails_opened": opened,
            "emails_clicked": clicked,
            "emails_bounced": bounced,
            "emails_failed": failed,
            "open_rate": (opened / sent * 100) if sent > 0 else 0,
            "click_rate": (clicked / sent * 100) if sent > 0 else 0,
            "bounce_rate": (bounced / sent * 100) if sent > 0 else 0,
            "delivery_rate": (delivered / sent * 100) if sent > 0 else 0,
            "period_days": days,
        }
