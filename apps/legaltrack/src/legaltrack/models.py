# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class LegalFilingEvent(BaseModel):
    message_id: str
    source_email: str
    received_at: datetime
    subject: str
    body_text_encrypted: bytes
    has_attachments: bool


class ParsedDeadline(BaseModel):
    filing_type: str
    jurisdiction: str
    deadline_date: datetime
    rule_citation: str
    confidence_score: float
    requires_review: bool


class CalendarSyncEvent(BaseModel):
    event_id: str
    provider: str  # google, outlook
    status: str  # pending, synced, error
    metadata: dict[str, Any]


class CEOTrackSchedule(BaseModel):
    # Added to support CEOTrack and Schiznit prodding logic
    task_name: str
    start_time: datetime
    end_time: datetime
    location: str | None = None
    context_tags: list[str] = []
    prod_frequency_mins: int = 15
    is_completed: bool = False
