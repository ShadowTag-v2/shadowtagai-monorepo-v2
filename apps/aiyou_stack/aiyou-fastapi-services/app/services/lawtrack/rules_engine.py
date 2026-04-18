"""LawTrack Rules Engine

Jurisdiction-specific procedural rule loading, business day calculation,
and deadline computation with confidence scoring.
"""

import logging
from datetime import date, timedelta
from functools import lru_cache

from app.models.lawtrack import (
    DeadlineCalculationResponse,
    EventType,
    Jurisdiction,
)

logger = logging.getLogger(__name__)


class BusinessDayCalculator:
    """Helper for legal business day calculations."""

    @staticmethod
    def is_weekend(d: date) -> bool:
        return d.weekday() >= 5  # 5=Saturday, 6=Sunday

    @staticmethod
    def is_holiday(d: date, jurisdiction: Jurisdiction) -> bool:
        # TODO: Implement real holiday lookup from rules DB
        return False

    @staticmethod
    def next_business_day(d: date, jurisdiction: Jurisdiction = Jurisdiction.FEDERAL) -> date:
        """Roll forward to next business day."""
        while BusinessDayCalculator.is_weekend(d) or BusinessDayCalculator.is_holiday(
            d,
            jurisdiction,
        ):
            d += timedelta(days=1)
        return d

    @staticmethod
    def add_business_days(
        start_date: date,
        days: int,
        jurisdiction: Jurisdiction = Jurisdiction.FEDERAL,
    ) -> date:
        """Add N business days to start_date."""
        current = start_date
        added = 0
        while added < days:
            current += timedelta(days=1)
            if not BusinessDayCalculator.is_weekend(
                current,
            ) and not BusinessDayCalculator.is_holiday(current, jurisdiction):
                added += 1
        return current


class RulesEngine:
    """Core logic for calculating deadlines based on jurisdiction rules."""

    def __init__(self):
        self._rules_cache = {}

    def calculate_deadline(
        self,
        jurisdiction: Jurisdiction,
        event_type: EventType,
        trigger_date: date,
    ) -> DeadlineCalculationResponse | None:
        """Calculate deadline based on jurisdiction and event type."""
        # MVP Hardcoded Rules
        # In real impl, fetch from DB

        days_to_add = 0
        rule_id = "default"

        if jurisdiction == Jurisdiction.CA:
            if event_type == EventType.SUMMONS_SERVICE:
                days_to_add = 30
            elif event_type == EventType.COMPLAINT_FILED:
                days_to_add = 30  # Just an example
        elif jurisdiction == Jurisdiction.FEDERAL:
            if event_type == EventType.SUMMONS_SERVICE or event_type == EventType.COMPLAINT_FILED:
                days_to_add = 21

        if days_to_add == 0 and event_type not in [EventType.TRIAL_DATE]:
            # Fallback or unknown rule
            return None

        # Calculate raw date
        raw_deadline = trigger_date + timedelta(days=days_to_add)

        # Adjust for weekends/holidays (Rule: Roll forward)
        final_deadline = BusinessDayCalculator.next_business_day(raw_deadline, jurisdiction)

        return DeadlineCalculationResponse(
            date=final_deadline,
            description=f"Deadline for {event_type} in {jurisdiction}",
            rule_id=rule_id,
            confidence_score=1.0,  # High confidence for hardcoded rules
        )


@lru_cache
def get_rules_engine() -> RulesEngine:
    return RulesEngine()
