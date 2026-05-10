"""Pydantic schemas for email service"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr


class EmailStatus(StrEnum):
    """Email status enumeration"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"


class FlowType(StrEnum):
    """Email flow type enumeration"""

    WELCOME = "welcome"
    REENGAGEMENT = "reengagement"
    TRANSACTIONAL = "transactional"
    DRIP_CAMPAIGN = "drip_campaign"
    NEWSLETTER = "newsletter"


# Recipient Schemas
class RecipientBase(BaseModel):
    """Base recipient schema"""

    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    metadata: dict[str, Any] = {}
    subscribed: bool = True


class RecipientCreate(RecipientBase):
    """Schema for creating a recipient"""


class RecipientUpdate(BaseModel):
    """Schema for updating a recipient"""

    first_name: str | None = None
    last_name: str | None = None
    metadata: dict[str, Any] | None = None
    subscribed: bool | None = None


class RecipientResponse(RecipientBase):
    """Schema for recipient response"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Email Template Schemas
class EmailTemplateBase(BaseModel):
    """Base email template schema"""

    name: str
    subject: str
    body_html: str
    body_text: str | None = None
    variables: list[str] = []


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating an email template"""


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template"""

    name: str | None = None
    subject: str | None = None
    body_html: str | None = None
    body_text: str | None = None
    variables: list[str] | None = None


class EmailTemplateResponse(EmailTemplateBase):
    """Schema for email template response"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Email Flow Schemas
class FlowStepBase(BaseModel):
    """Base flow step schema"""

    template_id: int
    step_order: int
    delay_days: int = 0
    delay_hours: int = 0
    delay_minutes: int = 0
    conditions: dict[str, Any] = {}


class FlowStepCreate(FlowStepBase):
    """Schema for creating a flow step"""


class FlowStepResponse(FlowStepBase):
    """Schema for flow step response"""

    id: int
    flow_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailFlowBase(BaseModel):
    """Base email flow schema"""

    name: str
    description: str | None = None
    flow_type: FlowType
    active: bool = True
    config: dict[str, Any] = {}


class EmailFlowCreate(EmailFlowBase):
    """Schema for creating an email flow"""

    steps: list[FlowStepCreate] = []


class EmailFlowUpdate(BaseModel):
    """Schema for updating an email flow"""

    name: str | None = None
    description: str | None = None
    flow_type: FlowType | None = None
    active: bool | None = None
    config: dict[str, Any] | None = None


class EmailFlowResponse(EmailFlowBase):
    """Schema for email flow response"""

    id: int
    created_at: datetime
    updated_at: datetime
    steps: list[FlowStepResponse] = []

    model_config = ConfigDict(from_attributes=True)


# Flow Enrollment Schemas
class FlowEnrollmentBase(BaseModel):
    """Base flow enrollment schema"""

    flow_id: int
    recipient_id: int


class FlowEnrollmentCreate(FlowEnrollmentBase):
    """Schema for enrolling a recipient in a flow"""


class FlowEnrollmentResponse(FlowEnrollmentBase):
    """Schema for flow enrollment response"""

    id: int
    current_step: int
    enrolled_at: datetime
    completed_at: datetime | None = None
    active: bool

    model_config = ConfigDict(from_attributes=True)


# Email Schemas
class EmailBase(BaseModel):
    """Base email schema"""

    recipient_id: int
    subject: str
    body_html: str
    body_text: str | None = None
    template_id: int | None = None
    scheduled_at: datetime | None = None
    metadata: dict[str, Any] = {}


class EmailCreate(EmailBase):
    """Schema for creating an email"""


class EmailSendRequest(BaseModel):
    """Schema for sending an email"""

    recipient_email: EmailStr
    template_id: int | None = None
    subject: str | None = None
    body_html: str | None = None
    body_text: str | None = None
    variables: dict[str, Any] = {}
    scheduled_at: datetime | None = None


class EmailResponse(EmailBase):
    """Schema for email response"""

    id: int
    status: EmailStatus
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    opened_at: datetime | None = None
    clicked_at: datetime | None = None
    failed_at: datetime | None = None
    error_message: str | None = None
    tracking_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Analytics Schemas
class EmailAnalyticsResponse(BaseModel):
    """Schema for email analytics response"""

    email_id: int
    open_count: int
    click_count: int
    first_opened_at: datetime | None = None
    last_opened_at: datetime | None = None
    first_clicked_at: datetime | None = None
    last_clicked_at: datetime | None = None
    user_agent: str | None = None
    ip_address: str | None = None
    location: dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class CampaignMetricsResponse(BaseModel):
    """Schema for campaign metrics response"""

    flow_id: int | None = None
    date: datetime
    emails_sent: int
    emails_delivered: int
    emails_opened: int
    emails_clicked: int
    emails_bounced: int
    emails_failed: int
    open_rate: float
    click_rate: float
    bounce_rate: float

    model_config = ConfigDict(from_attributes=True)


# Bulk Operations
class BulkEnrollRequest(BaseModel):
    """Schema for bulk enrollment"""

    flow_id: int
    recipient_emails: list[EmailStr]


class BulkEnrollResponse(BaseModel):
    """Schema for bulk enrollment response"""

    enrolled_count: int
    failed_count: int
    enrollments: list[FlowEnrollmentResponse]
    errors: list[str] = []
