# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Zero-Touch Legal Deadline Management (ZT) API
FastAPI endpoints for automated deadline extraction, tracking, and notification.
"""

from datetime import UTC, date, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

# Initialize FastAPI app
app = FastAPI(
  title="Zero-Touch Legal Deadline Management API",
  description="Automated legal deadline extraction, tracking, and notification system",
  version="1.0.0",
  docs_url="/docs",
  redoc_url="/redoc",
)


# ============================================================================
# Models
# ============================================================================


class JurisdictionType(str, Enum):
  """Legal jurisdiction types."""

  FEDERAL = "federal"
  STATE = "state"
  LOCAL = "local"
  INTERNATIONAL = "international"


class DeadlineConfidence(str, Enum):
  """Confidence level for extracted deadlines."""

  HIGH = "high"  # 90-100% confidence
  MEDIUM = "medium"  # 70-89% confidence
  LOW = "low"  # 50-69% confidence
  UNCERTAIN = "uncertain"  # <50% confidence, requires review


class DeadlineType(str, Enum):
  """Types of legal deadlines."""

  FILING = "filing"
  RESPONSE = "response"
  PAYMENT = "payment"
  HEARING = "hearing"
  DISCOVERY = "discovery"
  MOTION = "motion"
  APPEAL = "appeal"
  NOTICE = "notice"
  STATUTE_OF_LIMITATIONS = "statute_of_limitations"
  CONTRACT_OBLIGATION = "contract_obligation"
  COMPLIANCE = "compliance"
  OTHER = "other"


class DeadlineStatus(str, Enum):
  """Deadline status."""

  PENDING = "pending"
  UPCOMING = "upcoming"
  CRITICAL = "critical"
  COMPLETED = "completed"
  MISSED = "missed"
  EXTENDED = "extended"
  CANCELLED = "cancelled"


class ReminderFrequency(str, Enum):
  """Reminder schedule types."""

  STANDARD = "standard"  # 30, 14, 7, 1 days
  INTENSIVE = "intensive"  # 30, 14, 7, 3, 1 days
  CRITICAL = "critical"  # 30, 14, 7, 5, 3, 2, 1 days
  CUSTOM = "custom"


class DocumentType(str, Enum):
  """Legal document types."""

  COURT_ORDER = "court_order"
  COMPLAINT = "complaint"
  SUMMONS = "summons"
  MOTION = "motion"
  NOTICE = "notice"
  CONTRACT = "contract"
  SUBPOENA = "subpoena"
  DISCOVERY_REQUEST = "discovery_request"
  JUDGMENT = "judgment"
  FILING = "filing"
  OTHER = "other"


class DeadlineRule(BaseModel):
  """Jurisdiction-specific deadline calculation rule."""

  id: str = Field(default_factory=lambda: str(uuid4()), description="Rule ID")
  jurisdiction: str = Field(
    ..., description="Jurisdiction (e.g., 'federal', 'CA', 'NY-SDNY')"
  )
  jurisdiction_type: JurisdictionType = Field(..., description="Jurisdiction type")
  deadline_type: DeadlineType = Field(..., description="Type of deadline")
  base_days: int = Field(..., description="Base number of days")
  exclude_weekends: bool = Field(default=True, description="Exclude weekends")
  exclude_holidays: bool = Field(default=True, description="Exclude court holidays")
  service_method_additions: dict[str, int] = Field(
    default_factory=dict, description="Additional days based on service method"
  )
  trigger_event: str = Field(..., description="Event that triggers deadline")
  rule_source: str = Field(..., description="Legal source (e.g., 'FRCP 12(a)(1)(A)')")
  notes: str | None = Field(None, description="Additional notes")
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
  updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "jurisdiction": "federal",
        "jurisdiction_type": "federal",
        "deadline_type": "response",
        "base_days": 21,
        "exclude_weekends": True,
        "exclude_holidays": True,
        "service_method_additions": {"personal": 0, "mail": 3, "electronic": 0},
        "trigger_event": "service_of_complaint",
        "rule_source": "FRCP 12(a)(1)(A)",
        "notes": "Answer to complaint deadline for federal civil cases",
      }
    }
  )


class ExtractedDeadline(BaseModel):
  """A deadline extracted from a legal document."""

  id: str = Field(
    default_factory=lambda: str(uuid4()), description="Unique deadline ID"
  )
  document_id: str = Field(..., description="Source document ID")
  deadline_type: DeadlineType = Field(..., description="Type of deadline")
  deadline_date: date = Field(..., description="Calculated deadline date")
  trigger_date: date | None = Field(None, description="Date that triggered deadline")
  trigger_event: str = Field(..., description="Event description")
  description: str = Field(..., description="Deadline description")
  jurisdiction: str = Field(..., description="Jurisdiction")
  case_number: str | None = Field(None, description="Case/matter number")
  party_names: list[str] = Field(default_factory=list, description="Parties involved")
  confidence: DeadlineConfidence = Field(..., description="Extraction confidence")
  status: DeadlineStatus = Field(
    default=DeadlineStatus.PENDING, description="Current status"
  )
  requires_review: bool = Field(default=False, description="Flagged for human review")
  review_reason: str | None = Field(None, description="Reason for review")
  calculation_details: dict[str, Any] = Field(
    default_factory=dict, description="Details of deadline calculation"
  )
  reminder_schedule: list[date] = Field(
    default_factory=list, description="Scheduled reminder dates"
  )
  assigned_to: str | None = Field(None, description="Assigned lawyer/staff")
  extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
  verified_at: datetime | None = Field(None, description="Verification timestamp")
  verified_by: str | None = Field(None, description="Verifying user")
  metadata: dict[str, Any] = Field(
    default_factory=dict, description="Additional metadata"
  )

  model_config = ConfigDict(
    json_schema_extra={
      "example": {
        "id": "dl_20251117_abc123",
        "document_id": "doc_complaint_xyz789",
        "deadline_type": "response",
        "deadline_date": "2025-12-08",
        "trigger_date": "2025-11-17",
        "trigger_event": "Service of summons and complaint",
        "description": "Deadline to file answer to complaint",
        "jurisdiction": "federal",
        "case_number": "1:25-cv-12345",
        "party_names": ["Smith", "Jones Corp"],
        "confidence": "high",
        "status": "pending",
        "requires_review": False,
        "calculation_details": {
          "base_days": 21,
          "service_method": "personal",
          "weekends_excluded": 3,
          "holidays_excluded": 1,
          "total_calendar_days": 25,
        },
        "reminder_schedule": ["2025-11-08", "2025-11-24", "2025-12-01", "2025-12-07"],
      }
    }
  )


class LegalDocument(BaseModel):
  """Legal document for deadline extraction."""

  id: str = Field(default_factory=lambda: str(uuid4()), description="Document ID")
  document_type: DocumentType = Field(..., description="Type of document")
  file_name: str = Field(..., description="Original file name")
  file_path: str = Field(..., description="Storage path (GCS)")
  jurisdiction: str = Field(..., description="Jurisdiction")
  case_number: str | None = Field(None, description="Case/matter number")
  filing_date: date | None = Field(None, description="Document filing date")
  service_date: date | None = Field(None, description="Service date")
  service_method: str | None = Field(None, description="Method of service")
  extracted_text: str | None = Field(None, description="OCR/extracted text")
  deadlines_count: int = Field(default=0, description="Number of deadlines found")
  processing_status: str = Field(default="pending", description="Processing status")
  uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
  processed_at: datetime | None = Field(None, description="Processing timestamp")
  uploaded_by: str = Field(..., description="Uploading user")
  metadata: dict[str, Any] = Field(
    default_factory=dict, description="Additional metadata"
  )


class DeadlineVerification(BaseModel):
  """Deadline verification by lawyer."""

  deadline_id: str = Field(..., description="Deadline ID to verify")
  approved: bool = Field(..., description="Verification approval")
  corrected_date: date | None = Field(None, description="Corrected deadline date")
  notes: str | None = Field(None, description="Verification notes")
  verified_by: str = Field(..., description="Verifying user")


class CalendarEntry(BaseModel):
  """Calendar entry for deadline."""

  deadline_id: str = Field(..., description="Associated deadline ID")
  calendar_provider: str = Field(
    ..., description="Calendar provider (Google, Outlook, etc.)"
  )
  calendar_id: str = Field(..., description="Calendar ID")
  event_id: str | None = Field(None, description="Calendar event ID")
  synced: bool = Field(default=False, description="Sync status")
  sync_error: str | None = Field(None, description="Sync error message")
  last_synced: datetime | None = Field(None, description="Last sync timestamp")


class ReminderConfig(BaseModel):
  """Reminder configuration."""

  deadline_id: str = Field(..., description="Deadline ID")
  frequency: ReminderFrequency = Field(..., description="Reminder frequency")
  custom_days: list[int] | None = Field(
    None, description="Custom reminder days before deadline"
  )
  notification_channels: list[str] = Field(
    default_factory=lambda: ["email"], description="Notification channels"
  )
  recipients: list[str] = Field(..., description="Recipient email/user IDs")


class DeadlineSearchRequest(BaseModel):
  """Search request for deadlines."""

  jurisdiction: str | None = Field(None, description="Filter by jurisdiction")
  deadline_type: DeadlineType | None = Field(None, description="Filter by type")
  status: DeadlineStatus | None = Field(None, description="Filter by status")
  date_from: date | None = Field(None, description="Deadline date range start")
  date_to: date | None = Field(None, description="Deadline date range end")
  case_number: str | None = Field(None, description="Filter by case number")
  assigned_to: str | None = Field(None, description="Filter by assignee")
  requires_review: bool | None = Field(None, description="Filter by review status")
  limit: int = Field(default=100, ge=1, le=1000)
  offset: int = Field(default=0, ge=0)


class DeadlineStatistics(BaseModel):
  """Statistics for deadline management."""

  total_deadlines: int
  by_status: dict[str, int]
  by_type: dict[str, int]
  upcoming_7_days: int
  upcoming_30_days: int
  critical_count: int
  requires_review_count: int
  missed_count: int
  avg_confidence_score: float
  auto_verified_percentage: float


# ============================================================================
# Endpoints
# ============================================================================


@app.get("/", tags=["Health"])
async def root():
  """API root endpoint."""
  return {
    "service": "Zero-Touch Legal Deadline Management API",
    "version": "1.0.0",
    "status": "operational",
    "documentation": "/docs",
  }


@app.get("/health", tags=["Health"])
async def health_check():
  """Health check endpoint."""
  return {
    "status": "healthy",
    "timestamp": datetime.now(UTC),
    "checks": {"database": "ok", "gcs": "ok", "ml_service": "ok", "calendar_api": "ok"},
  }


@app.post(
  "/documents/upload",
  response_model=LegalDocument,
  status_code=status.HTTP_201_CREATED,
  tags=["Documents"],
)
async def upload_document(
  file: UploadFile = File(...),
  document_type: DocumentType = Query(..., description="Document type"),
  jurisdiction: str = Query(..., description="Jurisdiction"),
  case_number: str | None = Query(None, description="Case number"),
  service_date: date | None = Query(None, description="Service date"),
  service_method: str | None = Query(None, description="Service method"),
  uploaded_by: str = Query(..., description="User ID"),
):
  """
  Upload legal document for deadline extraction.

  Accepts PDF, DOCX, or image files. The system will:
  1. OCR/extract text from the document
  2. Identify potential deadlines using NLP/ML
  3. Calculate deadlines based on jurisdiction rules
  4. Flag uncertain deadlines for review
  5. Populate calendar entries
  """
  # TODO: Implement actual file upload to GCS, OCR, and extraction

  doc_id = f"doc_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}"

  return LegalDocument(
    id=doc_id,
    document_type=document_type,
    file_name=file.filename,
    file_path=f"gs://legal-deadlines/documents/{doc_id}/{file.filename}",
    jurisdiction=jurisdiction,
    case_number=case_number,
    service_date=service_date,
    service_method=service_method,
    processing_status="processing",
    uploaded_by=uploaded_by,
  )


@app.get(
  "/documents/{document_id}/deadlines",
  response_model=list[ExtractedDeadline],
  tags=["Documents"],
)
async def get_document_deadlines(document_id: str):
  """
  Get all deadlines extracted from a specific document.
  """
  # TODO: Implement actual database query

  # Mock response
  return [
    ExtractedDeadline(
      document_id=document_id,
      deadline_type=DeadlineType.RESPONSE,
      deadline_date=date(2025, 12, 8),
      trigger_date=date(2025, 11, 17),
      trigger_event="Service of summons and complaint",
      description="Deadline to file answer to complaint",
      jurisdiction="federal",
      case_number="1:25-cv-12345",
      party_names=["Smith", "Jones Corp"],
      confidence=DeadlineConfidence.HIGH,
      status=DeadlineStatus.PENDING,
      requires_review=False,
      calculation_details={
        "base_days": 21,
        "service_method": "personal",
        "weekends_excluded": 3,
        "holidays_excluded": 0,
        "total_calendar_days": 21,
      },
      reminder_schedule=[
        date(2025, 11, 8),
        date(2025, 11, 24),
        date(2025, 12, 1),
        date(2025, 12, 7),
      ],
    )
  ]


@app.post(
  "/deadlines/search", response_model=list[ExtractedDeadline], tags=["Deadlines"]
)
async def search_deadlines(request: DeadlineSearchRequest):
  """
  Search and filter deadlines.

  Supports filtering by:
  - Jurisdiction
  - Deadline type
  - Status
  - Date range
  - Case number
  - Assignee
  - Review status
  """
  # TODO: Implement actual search with filters
  return []


@app.get(
  "/deadlines/{deadline_id}", response_model=ExtractedDeadline, tags=["Deadlines"]
)
async def get_deadline(deadline_id: str):
  """Get specific deadline by ID."""
  # TODO: Implement actual retrieval
  raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail=f"Deadline {deadline_id} not found"
  )


@app.post(
  "/deadlines/{deadline_id}/verify",
  response_model=ExtractedDeadline,
  tags=["Deadlines"],
)
async def verify_deadline(deadline_id: str, verification: DeadlineVerification):
  """
  Verify or correct an extracted deadline.

  Allows lawyers to:
  - Approve AI-extracted deadline
  - Correct the deadline date
  - Add notes

  Verified deadlines are automatically synced to calendar.
  """
  # TODO: Implement verification workflow
  # Update deadline status
  # If corrected, update ML feedback loop
  # Trigger calendar sync
  pass


@app.get(
  "/deadlines/review/pending",
  response_model=list[ExtractedDeadline],
  tags=["Deadlines"],
)
async def get_pending_reviews(
  limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)
):
  """
  Get deadlines pending review.

  Returns deadlines flagged for human review due to:
  - Low confidence extraction
  - Complex calculation
  - Conflicting rules
  - Missing information
  """
  # TODO: Implement query for pending reviews
  return []


@app.post(
  "/deadlines/{deadline_id}/calendar", response_model=CalendarEntry, tags=["Calendar"]
)
async def sync_to_calendar(
  deadline_id: str,
  calendar_provider: str = Query(..., description="Calendar provider"),
  calendar_id: str = Query(..., description="Calendar ID"),
):
  """
  Sync deadline to calendar.

  Creates calendar event with:
  - Deadline as all-day event
  - Reminder notifications
  - Case details in description
  - Links to documents
  """
  # TODO: Implement calendar API integration (Google Calendar, Outlook)
  return CalendarEntry(
    deadline_id=deadline_id,
    calendar_provider=calendar_provider,
    calendar_id=calendar_id,
    synced=True,
    last_synced=datetime.now(UTC),
  )


@app.post(
  "/deadlines/{deadline_id}/reminders",
  response_model=ReminderConfig,
  tags=["Reminders"],
)
async def configure_reminders(deadline_id: str, config: ReminderConfig):
  """
  Configure reminder schedule for deadline.

  Reminder frequencies:
  - STANDARD: 30, 14, 7, 1 days before
  - INTENSIVE: 30, 14, 7, 3, 1 days before
  - CRITICAL: 30, 14, 7, 5, 3, 2, 1 days before
  - CUSTOM: User-defined days

  Notification channels:
  - Email
  - SMS
  - Slack
  - Push notification
  """
  # TODO: Implement reminder configuration
  # Create scheduled tasks for notifications
  return config


@app.get("/rules/jurisdictions", response_model=list[str], tags=["Rules"])
async def get_jurisdictions():
  """
  Get list of supported jurisdictions.

  Returns all jurisdictions with configured deadline rules.
  """
  # TODO: Query available jurisdictions from rules database
  return [
    "federal",
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
  ]


@app.get(
  "/rules/jurisdiction/{jurisdiction}",
  response_model=list[DeadlineRule],
  tags=["Rules"],
)
async def get_jurisdiction_rules(jurisdiction: str):
  """
  Get all deadline rules for a jurisdiction.

  Returns comprehensive rule set including:
  - Filing deadlines
  - Response deadlines
  - Discovery deadlines
  - Motion deadlines
  - Appeal deadlines
  """
  # TODO: Query rules from database
  return []


@app.post(
  "/rules",
  response_model=DeadlineRule,
  status_code=status.HTTP_201_CREATED,
  tags=["Rules"],
)
async def create_rule(rule: DeadlineRule):
  """
  Create new jurisdiction rule.

  **Admin only**: Add or update deadline calculation rules.
  """
  # TODO: Implement rule creation with validation
  return rule


@app.get("/statistics", response_model=DeadlineStatistics, tags=["Analytics"])
async def get_statistics(
  jurisdiction: str | None = Query(None),
  date_from: date | None = Query(None),
  date_to: date | None = Query(None),
):
  """
  Get deadline management statistics.

  Analytics for:
  - Total deadlines tracked
  - Status distribution
  - Type distribution
  - Upcoming deadlines
  - Critical deadlines
  - Review queue size
  - Missed deadlines
  - Confidence metrics
  """
  # TODO: Implement analytics queries
  return DeadlineStatistics(
    total_deadlines=0,
    by_status={},
    by_type={},
    upcoming_7_days=0,
    upcoming_30_days=0,
    critical_count=0,
    requires_review_count=0,
    missed_count=0,
    avg_confidence_score=0.0,
    auto_verified_percentage=0.0,
  )


@app.get(
  "/dashboard/upcoming", response_model=list[ExtractedDeadline], tags=["Dashboard"]
)
async def get_upcoming_deadlines(
  days: int = Query(30, ge=1, le=365, description="Days ahead to look"),
  assigned_to: str | None = Query(None, description="Filter by assignee"),
):
  """
  Get upcoming deadlines for dashboard.

  Returns deadlines in the next N days, sorted by date.
  Used for lawyer dashboard view.
  """
  # TODO: Implement query
  return []


@app.get(
  "/dashboard/critical", response_model=list[ExtractedDeadline], tags=["Dashboard"]
)
async def get_critical_deadlines(
  assigned_to: str | None = Query(None, description="Filter by assignee"),
):
  """
  Get critical deadlines (7 days or less).

  High-priority view for imminent deadlines.
  """
  # TODO: Implement query for deadlines <= 7 days out
  return []


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
  """Global exception handler."""
  return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={
      "error": "Internal server error",
      "detail": str(exc),
      "timestamp": datetime.now(UTC).isoformat(),
    },
  )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
  """Initialize services on startup."""
  # TODO: Initialize DB connections, GCS clients, ML models, etc.


@app.on_event("shutdown")
async def shutdown_event():
  """Clean up on shutdown."""
  # TODO: Close DB connections, etc.


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
  import uvicorn

  uvicorn.run(
    "legal_deadlines:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
  )
