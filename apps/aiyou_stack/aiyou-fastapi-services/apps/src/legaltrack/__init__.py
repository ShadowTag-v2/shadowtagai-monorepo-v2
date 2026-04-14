"""LEGALTRACK: AI-Powered Legal Calendar

Email ingestion → Deadline extraction → Auto-sync calendars

Value Proposition: Zero missed filings, eliminate malpractice risk
Revenue: $786K Y1 → $22.5M Y3
Market: $800M legal tech compliance
LTV:CAC: 12:1
"""

__version__ = "1.0.0"

from .calendar_sync import (
    CalendarSyncEngine,
    SyncResult,
)
from .deadline_extraction import (
    Deadline,
    DeadlineExtractor,
    DeadlineType,
)
from .email_ingestion import (
    EmailConnector,
    GmailConnector,
    OutlookConnector,
)
