# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""LEGALTRACK: AI-Powered Legal Calendar

Email ingestion → Deadline extraction → Auto-sync calendars

Value Proposition: Zero missed filings, eliminate malpractice risk
Revenue: $786K Y1 → $22.5M Y3
Market: $800M legal tech compliance
LTV:CAC: 12:1
"""

__version__ = "1.0.0"

from .calendar_sync import (
    CalendarSyncEngine,  # noqa: F401
    SyncResult,  # noqa: F401
)
from .deadline_extraction import (
    Deadline,  # noqa: F401
    DeadlineExtractor,  # noqa: F401
    DeadlineType,  # noqa: F401
)
from .email_ingestion import (
    EmailConnector,  # noqa: F401
    GmailConnector,  # noqa: F401
    OutlookConnector,  # noqa: F401
)
