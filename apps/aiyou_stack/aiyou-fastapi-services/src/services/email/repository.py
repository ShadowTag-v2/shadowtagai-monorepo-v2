"""Database repository for email service"""

from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.db import models

from . import schemas


class EmailRepository:
    """Repository for email database operations"""

    @staticmethod
    def create_recipient(db: Session, recipient: schemas.RecipientCreate) -> models.Recipient:
        """Create a new recipient"""
        db_recipient = models.Recipient(**recipient.model_dump())
        db.add(db_recipient)
        db.commit()
        db.refresh(db_recipient)
        return db_recipient

    @staticmethod
    def get_recipient(db: Session, recipient_id: int) -> models.Recipient | None:
        """Get recipient by ID"""
        return db.query(models.Recipient).filter(models.Recipient.id == recipient_id).first()

    @staticmethod
    def get_recipient_by_email(db: Session, email: str) -> models.Recipient | None:
        """Get recipient by email"""
        return db.query(models.Recipient).filter(models.Recipient.email == email).first()

    @staticmethod
    def get_recipients(db: Session, skip: int = 0, limit: int = 100) -> list[models.Recipient]:
        """Get list of recipients"""
        return db.query(models.Recipient).offset(skip).limit(limit).all()

    @staticmethod
    def update_recipient(
        db: Session,
        recipient_id: int,
        recipient_update: schemas.RecipientUpdate,
    ) -> models.Recipient | None:
        """Update recipient"""
        db_recipient = EmailRepository.get_recipient(db, recipient_id)
        if db_recipient:
            update_data = recipient_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_recipient, field, value)
            db.commit()
            db.refresh(db_recipient)
        return db_recipient

    @staticmethod
    def create_template(db: Session, template: schemas.EmailTemplateCreate) -> models.EmailTemplate:
        """Create email template"""
        db_template = models.EmailTemplate(**template.model_dump())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template

    @staticmethod
    def get_template(db: Session, template_id: int) -> models.EmailTemplate | None:
        """Get template by ID"""
        return db.query(models.EmailTemplate).filter(models.EmailTemplate.id == template_id).first()

    @staticmethod
    def get_template_by_name(db: Session, name: str) -> models.EmailTemplate | None:
        """Get template by name"""
        return db.query(models.EmailTemplate).filter(models.EmailTemplate.name == name).first()

    @staticmethod
    def get_templates(db: Session, skip: int = 0, limit: int = 100) -> list[models.EmailTemplate]:
        """Get list of templates"""
        return db.query(models.EmailTemplate).offset(skip).limit(limit).all()

    @staticmethod
    def create_flow(db: Session, flow: schemas.EmailFlowCreate) -> models.EmailFlow:
        """Create email flow with steps"""
        # Create flow
        flow_data = flow.model_dump(exclude={"steps"})
        db_flow = models.EmailFlow(**flow_data)
        db.add(db_flow)
        db.flush()

        # Create steps
        for step_data in flow.steps:
            db_step = models.FlowStep(**step_data.model_dump(), flow_id=db_flow.id)
            db.add(db_step)

        db.commit()
        db.refresh(db_flow)
        return db_flow

    @staticmethod
    def get_flow(db: Session, flow_id: int) -> models.EmailFlow | None:
        """Get flow by ID"""
        return db.query(models.EmailFlow).filter(models.EmailFlow.id == flow_id).first()

    @staticmethod
    def get_flows(db: Session, active_only: bool = False) -> list[models.EmailFlow]:
        """Get list of flows"""
        query = db.query(models.EmailFlow)
        if active_only:
            query = query.filter(models.EmailFlow.active)
        return query.all()

    @staticmethod
    def enroll_recipient(db: Session, flow_id: int, recipient_id: int) -> models.FlowEnrollment:
        """Enroll recipient in flow"""
        db_enrollment = models.FlowEnrollment(
            flow_id=flow_id,
            recipient_id=recipient_id,
            current_step=0,
            active=True,
        )
        db.add(db_enrollment)
        db.commit()
        db.refresh(db_enrollment)
        return db_enrollment

    @staticmethod
    def get_enrollment(
        db: Session,
        flow_id: int,
        recipient_id: int,
    ) -> models.FlowEnrollment | None:
        """Get enrollment for recipient in flow"""
        return (
            db.query(models.FlowEnrollment)
            .filter(
                and_(
                    models.FlowEnrollment.flow_id == flow_id,
                    models.FlowEnrollment.recipient_id == recipient_id,
                ),
            )
            .first()
        )

    @staticmethod
    def get_active_enrollments(db: Session) -> list[models.FlowEnrollment]:
        """Get all active enrollments"""
        return db.query(models.FlowEnrollment).filter(models.FlowEnrollment.active).all()

    @staticmethod
    def create_email(db: Session, email_data: dict) -> models.Email:
        """Create email record"""
        db_email = models.Email(**email_data)
        db.add(db_email)
        db.commit()
        db.refresh(db_email)
        return db_email

    @staticmethod
    def get_email(db: Session, email_id: int) -> models.Email | None:
        """Get email by ID"""
        return db.query(models.Email).filter(models.Email.id == email_id).first()

    @staticmethod
    def get_emails(
        db: Session,
        recipient_id: int | None = None,
        status: models.EmailStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[models.Email]:
        """Get list of emails"""
        query = db.query(models.Email)

        if recipient_id:
            query = query.filter(models.Email.recipient_id == recipient_id)
        if status:
            query = query.filter(models.Email.status == status)

        return query.order_by(models.Email.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_email_status(
        db: Session,
        email_id: int,
        status: models.EmailStatus,
        error_message: str | None = None,
    ) -> models.Email | None:
        """Update email status"""
        db_email = EmailRepository.get_email(db, email_id)
        if db_email:
            db_email.status = status
            db_email.updated_at = datetime.utcnow()

            # Set timestamps based on status
            if status == models.EmailStatus.SENT:
                db_email.sent_at = datetime.utcnow()
            elif status == models.EmailStatus.DELIVERED:
                db_email.delivered_at = datetime.utcnow()
            elif status == models.EmailStatus.OPENED:
                db_email.opened_at = datetime.utcnow()
            elif status == models.EmailStatus.CLICKED:
                db_email.clicked_at = datetime.utcnow()
            elif status == models.EmailStatus.FAILED:
                db_email.failed_at = datetime.utcnow()
                db_email.error_message = error_message

            db.commit()
            db.refresh(db_email)
        return db_email

    @staticmethod
    def get_pending_emails(db: Session, limit: int = 100) -> list[models.Email]:
        """Get pending emails to send"""
        now = datetime.utcnow()
        return (
            db.query(models.Email)
            .filter(
                and_(
                    models.Email.status == models.EmailStatus.PENDING,
                    or_(models.Email.scheduled_at is None, models.Email.scheduled_at <= now),
                ),
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_analytics(db: Session, email_id: int) -> models.EmailAnalytics:
        """Create analytics record for email"""
        db_analytics = models.EmailAnalytics(email_id=email_id)
        db.add(db_analytics)
        db.commit()
        db.refresh(db_analytics)
        return db_analytics

    @staticmethod
    def update_analytics(
        db: Session,
        email_id: int,
        event_type: str,
        event_data: dict = None,
    ) -> models.EmailAnalytics | None:
        """Update email analytics"""
        if event_data is None:
            event_data = {}
        db_analytics = (
            db.query(models.EmailAnalytics)
            .filter(models.EmailAnalytics.email_id == email_id)
            .first()
        )

        if not db_analytics:
            db_analytics = EmailRepository.create_analytics(db, email_id)

        now = datetime.utcnow()

        if event_type == "open":
            db_analytics.open_count += 1
            if not db_analytics.first_opened_at:
                db_analytics.first_opened_at = now
            db_analytics.last_opened_at = now

        elif event_type == "click":
            db_analytics.click_count += 1
            if not db_analytics.first_clicked_at:
                db_analytics.first_clicked_at = now
            db_analytics.last_clicked_at = now

        if event_data:
            db_analytics.user_agent = event_data.get("user_agent")
            db_analytics.ip_address = event_data.get("ip_address")
            db_analytics.location = event_data.get("location", {})

        db.commit()
        db.refresh(db_analytics)
        return db_analytics

    @staticmethod
    def create_event(
        db: Session,
        email_id: int,
        event_type: str,
        event_data: dict = None,
    ) -> models.EmailEvent:
        """Create email event"""
        if event_data is None:
            event_data = {}
        db_event = models.EmailEvent(
            email_id=email_id,
            event_type=event_type,
            event_data=event_data,
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
