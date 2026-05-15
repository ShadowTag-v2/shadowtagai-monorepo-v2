"""LawTrack Pydantic Models

Comprehensive data models for the LawTrack legal deadline management platform.
Includes enums, base models, request/response models for all API operations.
"""

from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# =============================================================================
# ENUMS
# =============================================================================


class Jurisdiction(StrEnum):
    CA = "CA"
    TX = "TX"
    NY = "NY"
    FL = "FL"
    FEDERAL = "FEDERAL"


class EventType(StrEnum):
    SUMMONS_SERVICE = "summons_service"
    COMPLAINT_FILED = "complaint_filed"
    MOTION_TO_DISMISS = "motion_to_dismiss"
    ANSWER_DUE = "answer_due"
    DISCOVERY_CUTOFF = "discovery_cutoff"
    TRIAL_DATE = "trial_date"


class DeadlineColor(StrEnum):
    RED = "RED"  # < 3 days
    YELLOW = "YELLOW"  # < 10 days
    GREEN = "GREEN"  # > 10 days


class EventStatus(StrEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    WAIVED = "WAIVED"


class IngestionStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    FAILED = "FAILED"


class EnforcementLevel(StrEnum):
    GENTLE = "GENTLE"  # Email only, working hours
    STANDARD = "STANDARD"  # Email + Mobile, extended hours
    URGENT = "URGENT"  # Multi-channel, weekends allowed
    AGGRESSIVE = "AGGRESSIVE"  # Hourly reminders
    NO_SLACK = "NO_SLACK"  # Escalation to partners


# =============================================================================
# BASE MODELS
# =============================================================================


class JurisdictionRule(BaseModel):
    id: str
    jurisdiction: Jurisdiction
    event_type: EventType
    days_offset: int
    is_business_days: bool = True
    description: str


class Matter(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    jurisdiction: Jurisdiction
    case_number: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TimelineEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    matter_id: UUID
    event_type: EventType
    deadline_date: date
    status: EventStatus = EventStatus.PENDING
    description: str
    confidence_score: float = 1.0
    rule_id: str | None = None


class EmailIngestion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    from_address: str
    subject: str
    raw_email_ref: str  # Encrypted storage reference
    received_at: datetime
    processing_status: IngestionStatus = IngestionStatus.PENDING
    parsed_case_number: str | None = None
    matter_id: UUID | None = None
    parsed_events: list[dict[str, Any]] = Field(default_factory=list)
    error_message: str | None = None
    processed_at: datetime | None = None


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class DeadlineCalculationResponse(BaseModel):
    date: date
    description: str
    rule_id: str
    confidence_score: float


class CreateRuleRequest(BaseModel):
    jurisdiction: Jurisdiction
    event_type: EventType
    days_offset: int
    is_business_days: bool
    description: str


class UpdateRuleRequest(BaseModel):
    days_offset: int | None = None
    description: str | None = None


class CalculateDeadlineRequest(BaseModel):
    jurisdiction: Jurisdiction
    event_type: EventType
    trigger_date: date


class RuleResponse(BaseModel):
    id: str
    jurisdiction: Jurisdiction
    event_type: EventType
    days_offset: int
    description: str


class CreateMatterRequest(BaseModel):
    name: str
    jurisdiction: Jurisdiction
    case_number: str | None = None


class UpdateMatterRequest(BaseModel):
    name: str | None = None
    case_number: str | None = None
    status: str | None = None


class AddEventRequest(BaseModel):
    event_type: EventType
    date: date
    description: str | None = None


class MatterResponse(BaseModel):
    id: UUID
    name: str
    jurisdiction: Jurisdiction
    case_number: str | None = None
    status: str
    created_at: datetime


class TimelineResponse(BaseModel):
    matter: Matter
    events: list[TimelineEvent]


class DashboardResponse(BaseModel):
    critical_count: int
    upcoming_count: int
    matters: list[MatterResponse]


class EmailWebhookRequest(BaseModel):
    from_address: str
    subject: str
    body: str
    received_at: datetime


class IngestionStatusResponse(BaseModel):
    id: UUID
    processing_status: IngestionStatus
    parsed_case_number: str | None
    matter_id: UUID | None
    events_created: int
    error_message: str | None
    processed_at: datetime | None


class EnforcementConfig(BaseModel):
    matter_id: UUID
    level: EnforcementLevel
    quiet_hours_start: int = 20  # 8 PM
    quiet_hours_end: int = 8  # 8 AM
    max_daily_alerts: int = 3


class UpdateEnforcementRequest(BaseModel):
    level: EnforcementLevel


class EnforcementPresetsResponse(BaseModel):
    levels: list[str]
    descriptions: dict[str, str]
