# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from datetime import date

import pytest

from app.models.lawtrack import EventType, Jurisdiction
from app.services.lawtrack.rules_engine import BusinessDayCalculator, RulesEngine


class TestBusinessDayCalculator:
    def test_next_business_day_simple(self):
        # Friday (Business Day) -> Friday
        friday = date(2023, 10, 27)
        assert BusinessDayCalculator.next_business_day(friday) == friday

    def test_next_business_day_weekend(self):
        # Saturday -> Monday
        saturday = date(2023, 10, 28)
        monday = date(2023, 10, 30)
        assert BusinessDayCalculator.next_business_day(saturday) == monday

    def test_add_business_days(self):
        # Monday + 2 business days = Wednesday
        monday = date(2023, 10, 30)
        wednesday = date(2023, 11, 1)
        assert BusinessDayCalculator.add_business_days(monday, 2) == wednesday

        # Friday + 1 business day = Monday
        friday = date(2023, 10, 27)
        next_monday = date(2023, 10, 30)
        assert BusinessDayCalculator.add_business_days(friday, 1) == next_monday


class TestRulesEngine:
    @pytest.fixture
    def rules_engine(self):
        return RulesEngine()

    def test_calculate_deadline_ca_civil(self, rules_engine):
        # CA: Response to summons is 30 days
        service_date = date(2023, 10, 1)
        # 30 days from Oct 1 is Oct 31 (Tuesday)
        expected = date(2023, 10, 31)

        deadline = rules_engine.calculate_deadline(
            jurisdiction=Jurisdiction.CA,
            event_type=EventType.SUMMONS_SERVICE,
            trigger_date=service_date,
        )
        assert deadline.date == expected
        assert deadline.confidence_score >= 0.9

    def test_calculate_deadline_federal(self, rules_engine):
        # Federal: Response to complaint is 21 days
        service_date = date(2023, 10, 1)
        # 21 days from Oct 1 is Oct 22 (Sunday) -> Moves to Monday Oct 23
        expected = date(2023, 10, 23)

        deadline = rules_engine.calculate_deadline(
            jurisdiction=Jurisdiction.FEDERAL,
            event_type=EventType.COMPLAINT_FILED,
            trigger_date=service_date,
        )
        assert deadline.date == expected

    def test_unknown_event_type(self, rules_engine):
        # Should return None or raise error depending on implementation
        # Assuming safe return with low confidence or None based on common patterns
        deadline = rules_engine.calculate_deadline(
            jurisdiction=Jurisdiction.CA,
            event_type="UNKNOWN_EVENT",  # Invalid type string
            trigger_date=date(2023, 1, 1),
        )
        assert deadline is None
