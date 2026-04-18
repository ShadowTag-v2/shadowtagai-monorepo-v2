"""Jurisdiction-Specific Rule Engine
Handles complex deadline calculations with jurisdiction-specific rules
"""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from typing import Any


class ServiceMethod(StrEnum):
    """Methods of service"""

    PERSONAL = "personal"
    MAIL = "mail"
    CERTIFIED_MAIL = "certified_mail"
    ELECTRONIC = "electronic"
    PUBLICATION = "publication"
    SUBSTITUTED = "substituted"


@dataclass
class Holiday:
    """Court holiday"""

    date: date
    name: str
    jurisdiction: str


@dataclass
class DeadlineCalculation:
    """Result of deadline calculation"""

    final_date: date
    base_days: int
    calendar_days: int
    weekends_excluded: int
    holidays_excluded: int
    service_method_addition: int
    calculation_notes: list[str]
    rule_citations: list[str]
    confidence: float


class JurisdictionRuleEngine:
    """Calculates deadlines according to jurisdiction-specific rules

    Handles:
    - Weekend exclusions
    - Court holidays
    - Service method additions
    - Local court rules
    - Federal vs state differences
    """

    def __init__(self, holidays_db_path: str | None = None):
        """Initialize rule engine with holiday database"""
        self.holidays: dict[str, list[Holiday]] = {}
        self.rules_cache: dict[str, Any] = {}

        # Load federal holidays
        self._load_federal_holidays()

        # Load state-specific holidays if database provided
        if holidays_db_path:
            self._load_holidays_from_db(holidays_db_path)

    def calculate_deadline(
        self,
        trigger_date: date,
        jurisdiction: str,
        deadline_type: str,
        base_days: int,
        service_method: ServiceMethod | None = None,
        exclude_weekends: bool = True,
        exclude_holidays: bool = True,
        additional_context: dict[str, Any] | None = None,
    ) -> DeadlineCalculation:
        """Calculate deadline with all jurisdiction-specific rules applied

        Args:
            trigger_date: Date that triggers the deadline
            jurisdiction: Jurisdiction code (e.g., 'federal', 'CA', 'NY-SDNY')
            deadline_type: Type of deadline
            base_days: Base number of days
            service_method: Method of service
            exclude_weekends: Whether to exclude weekends
            exclude_holidays: Whether to exclude court holidays
            additional_context: Any additional context for calculation

        Returns:
            DeadlineCalculation with full details

        """
        notes = []
        rule_citations = []
        current_date = trigger_date
        days_added = 0
        weekends_excluded = 0
        holidays_excluded = 0
        service_addition = 0

        # Apply service method additions
        if service_method:
            service_addition = self._get_service_method_addition(
                jurisdiction,
                service_method,
                deadline_type,
            )
            notes.append(f"Service method '{service_method.value}' adds {service_addition} days")

        total_days_needed = base_days + service_addition

        # Add business days
        while days_added < total_days_needed:
            current_date += timedelta(days=1)
            days_added += 1

            # Check if we need to exclude this day
            if exclude_weekends and self._is_weekend(current_date):
                weekends_excluded += 1
                days_added -= 1
                continue

            if exclude_holidays and self._is_holiday(current_date, jurisdiction):
                holiday = self._get_holiday(current_date, jurisdiction)
                holidays_excluded += 1
                days_added -= 1
                notes.append(f"Excluded holiday: {holiday.name}")
                continue

        # Apply jurisdiction-specific adjustments
        current_date = self._apply_jurisdiction_specific_rules(
            current_date,
            jurisdiction,
            deadline_type,
            notes,
            rule_citations,
        )

        # Calculate total calendar days
        calendar_days = (current_date - trigger_date).days

        # Calculate confidence
        confidence = self._calculate_calculation_confidence(
            jurisdiction,
            deadline_type,
            service_method,
        )

        return DeadlineCalculation(
            final_date=current_date,
            base_days=base_days,
            calendar_days=calendar_days,
            weekends_excluded=weekends_excluded,
            holidays_excluded=holidays_excluded,
            service_method_addition=service_addition,
            calculation_notes=notes,
            rule_citations=rule_citations,
            confidence=confidence,
        )

    def _get_service_method_addition(
        self,
        jurisdiction: str,
        service_method: ServiceMethod,
        deadline_type: str,
    ) -> int:
        """Get additional days based on service method"""
        # Federal rules (FRCP)
        if jurisdiction == "federal":
            if service_method == ServiceMethod.MAIL:
                return 3  # FRCP 6(d)
            if service_method == ServiceMethod.CERTIFIED_MAIL:
                return 3
            if service_method == ServiceMethod.ELECTRONIC:
                return 0  # No addition for e-service
            if service_method == ServiceMethod.PERSONAL:
                return 0
            return 0

        # California state courts
        if jurisdiction == "CA":
            if service_method == ServiceMethod.MAIL:
                return 5  # CCP § 1013(a)
            if service_method == ServiceMethod.ELECTRONIC:
                return 2  # CCP § 1010.6(a)(3)(B)
            if service_method == ServiceMethod.PERSONAL:
                return 0
            return 0

        # New York state courts
        if jurisdiction == "NY":
            if service_method == ServiceMethod.MAIL:
                return 5  # CPLR 2103(b)(2)
            if service_method == ServiceMethod.PERSONAL:
                return 0
            return 0

        # Texas state courts
        if jurisdiction == "TX":
            if service_method == ServiceMethod.MAIL:
                return 4  # TRCP 21a
            if service_method == ServiceMethod.CERTIFIED_MAIL:
                return 4
            if service_method == ServiceMethod.PERSONAL:
                return 0
            return 0

        # Default: no addition
        return 0

    def _is_weekend(self, check_date: date) -> bool:
        """Check if date is a weekend"""
        return check_date.weekday() in [5, 6]  # Saturday, Sunday

    def _is_holiday(self, check_date: date, jurisdiction: str) -> bool:
        """Check if date is a court holiday"""
        # Check federal holidays
        if jurisdiction == "federal" or jurisdiction in self.holidays:
            holidays = self.holidays.get(jurisdiction, [])
            return any(h.date == check_date for h in holidays)

        # Check jurisdiction-specific holidays
        if jurisdiction in self.holidays:
            return any(h.date == check_date for h in self.holidays[jurisdiction])

        return False

    def _get_holiday(self, check_date: date, jurisdiction: str) -> Holiday | None:
        """Get holiday information for a date"""
        holidays = self.holidays.get(jurisdiction, [])
        for holiday in holidays:
            if holiday.date == check_date:
                return holiday
        return None

    def _apply_jurisdiction_specific_rules(
        self,
        calculated_date: date,
        jurisdiction: str,
        deadline_type: str,
        notes: list[str],
        rule_citations: list[str],
    ) -> date:
        """Apply jurisdiction-specific adjustments to calculated date

        Some jurisdictions have special rules like:
        - If deadline falls on weekend, move to next Monday
        - Specific rules for certain types of filings
        - Local court rules
        """
        # Federal courts: If deadline falls on weekend or holiday, move to next business day
        if jurisdiction == "federal":
            while self._is_weekend(calculated_date) or self._is_holiday(
                calculated_date,
                jurisdiction,
            ):
                calculated_date += timedelta(days=1)
                notes.append("Moved to next business day (federal rule)")
            rule_citations.append("FRCP 6(a)")

        # California: If last day is holiday/weekend, extends to next court day
        elif jurisdiction == "CA":
            while self._is_weekend(calculated_date) or self._is_holiday(
                calculated_date,
                jurisdiction,
            ):
                calculated_date += timedelta(days=1)
                notes.append("Extended to next court day (CCP § 12)")
            rule_citations.append("CCP § 12")

        # New York: Similar rule
        elif jurisdiction == "NY":
            while self._is_weekend(calculated_date) or self._is_holiday(
                calculated_date,
                jurisdiction,
            ):
                calculated_date += timedelta(days=1)
                notes.append("Extended to next business day (CPLR 2)")
            rule_citations.append("CPLR 2")

        return calculated_date

    def _calculate_calculation_confidence(
        self,
        jurisdiction: str,
        deadline_type: str,
        service_method: ServiceMethod | None,
    ) -> float:
        """Calculate confidence in the deadline calculation

        Factors:
        - Rule coverage for jurisdiction
        - Complexity of calculation
        - Availability of service method rules
        """
        confidence = 0.5  # Base confidence

        # Well-supported jurisdictions
        if jurisdiction in ["federal", "CA", "NY", "TX", "FL", "IL"]:
            confidence += 0.3
        else:
            confidence += 0.1  # Less confident for less-tested jurisdictions

        # Common deadline types
        if deadline_type in ["response", "filing", "motion"]:
            confidence += 0.15
        else:
            confidence += 0.05

        # Service method rules available
        if service_method and jurisdiction in ["federal", "CA", "NY", "TX"]:
            confidence += 0.1

        return min(confidence, 1.0)

    def _load_federal_holidays(self):
        """Load federal court holidays"""
        # Federal holidays for 2025-2026
        federal_holidays_2025 = [
            Holiday(date(2025, 1, 1), "New Year's Day", "federal"),
            Holiday(date(2025, 1, 20), "Martin Luther King Jr. Day", "federal"),
            Holiday(date(2025, 2, 17), "Presidents' Day", "federal"),
            Holiday(date(2025, 5, 26), "Memorial Day", "federal"),
            Holiday(date(2025, 6, 19), "Juneteenth", "federal"),
            Holiday(date(2025, 7, 4), "Independence Day", "federal"),
            Holiday(date(2025, 9, 1), "Labor Day", "federal"),
            Holiday(date(2025, 10, 13), "Columbus Day", "federal"),
            Holiday(date(2025, 11, 11), "Veterans Day", "federal"),
            Holiday(date(2025, 11, 27), "Thanksgiving", "federal"),
            Holiday(date(2025, 12, 25), "Christmas Day", "federal"),
        ]

        federal_holidays_2026 = [
            Holiday(date(2026, 1, 1), "New Year's Day", "federal"),
            Holiday(date(2026, 1, 19), "Martin Luther King Jr. Day", "federal"),
            Holiday(date(2026, 2, 16), "Presidents' Day", "federal"),
            Holiday(date(2026, 5, 25), "Memorial Day", "federal"),
            Holiday(date(2026, 6, 19), "Juneteenth", "federal"),
            Holiday(date(2026, 7, 4), "Independence Day", "federal"),
            Holiday(date(2026, 9, 7), "Labor Day", "federal"),
            Holiday(date(2026, 10, 12), "Columbus Day", "federal"),
            Holiday(date(2026, 11, 11), "Veterans Day", "federal"),
            Holiday(date(2026, 11, 26), "Thanksgiving", "federal"),
            Holiday(date(2026, 12, 25), "Christmas Day", "federal"),
        ]

        self.holidays["federal"] = federal_holidays_2025 + federal_holidays_2026

    def _load_holidays_from_db(self, db_path: str):
        """Load state-specific holidays from database"""
        # TODO: Implement database loading
        # This would load jurisdiction-specific holidays from a JSON/DB file

    def get_rule_citation(
        self,
        jurisdiction: str,
        deadline_type: str,
        service_method: ServiceMethod | None = None,
    ) -> str:
        """Get the legal rule citation for a deadline calculation"""
        citations = []

        # Federal citations
        if jurisdiction == "federal":
            if deadline_type == "response":
                citations.append("FRCP 12(a)(1)(A) - Answer to Complaint: 21 days")
            if service_method == ServiceMethod.MAIL:
                citations.append("FRCP 6(d) - Additional time for service by mail: 3 days")
            citations.append("FRCP 6(a) - Computing time")

        # California citations
        elif jurisdiction == "CA":
            if deadline_type == "response":
                citations.append("CCP § 412.20 - Answer to Complaint: 30 days")
            if service_method == ServiceMethod.MAIL:
                citations.append("CCP § 1013(a) - Service by mail: add 5 days")
            citations.append("CCP § 12 - Computation of time")

        # New York citations
        elif jurisdiction == "NY":
            if deadline_type == "response":
                citations.append("CPLR 3012(a) - Answer to Complaint: 20-30 days")
            if service_method == ServiceMethod.MAIL:
                citations.append("CPLR 2103(b)(2) - Service by mail: add 5 days")

        return "; ".join(citations) if citations else "General deadline calculation"


class RuleDatabase:
    """Database of jurisdiction-specific deadline rules"""

    def __init__(self):
        self.rules: dict[str, list[dict[str, Any]]] = {}
        self._initialize_federal_rules()
        self._initialize_state_rules()

    def _initialize_federal_rules(self):
        """Initialize federal court rules"""
        self.rules["federal"] = [
            {
                "deadline_type": "response",
                "trigger": "service_of_complaint",
                "base_days": 21,
                "rule_source": "FRCP 12(a)(1)(A)",
                "description": "Time to serve answer to complaint",
                "exclude_weekends": False,  # Federal counts calendar days
                "exclude_holidays": True,
                "service_additions": {
                    ServiceMethod.MAIL: 3,
                    ServiceMethod.ELECTRONIC: 0,
                    ServiceMethod.PERSONAL: 0,
                },
            },
            {
                "deadline_type": "motion",
                "trigger": "filing_of_motion",
                "base_days": 14,
                "rule_source": "FRCP 6(c)(1)",
                "description": "Time to respond to motion",
                "exclude_weekends": False,
                "exclude_holidays": True,
            },
            {
                "deadline_type": "discovery",
                "trigger": "service_of_discovery_request",
                "base_days": 30,
                "rule_source": "FRCP 33(b)(2)",
                "description": "Time to respond to interrogatories",
                "exclude_weekends": False,
                "exclude_holidays": True,
            },
            {
                "deadline_type": "appeal",
                "trigger": "entry_of_judgment",
                "base_days": 30,
                "rule_source": "FRAP 4(a)(1)(A)",
                "description": "Time to file notice of appeal",
                "exclude_weekends": False,
                "exclude_holidays": True,
            },
        ]

    def _initialize_state_rules(self):
        """Initialize state-specific rules"""
        # California
        self.rules["CA"] = [
            {
                "deadline_type": "response",
                "trigger": "service_of_complaint",
                "base_days": 30,
                "rule_source": "CCP § 412.20",
                "description": "Time to respond to complaint",
                "exclude_weekends": True,
                "exclude_holidays": True,
                "service_additions": {
                    ServiceMethod.MAIL: 5,
                    ServiceMethod.ELECTRONIC: 2,
                    ServiceMethod.PERSONAL: 0,
                },
            },
            {
                "deadline_type": "appeal",
                "trigger": "entry_of_judgment",
                "base_days": 60,
                "rule_source": "CCP § 902",
                "description": "Time to file notice of appeal",
                "exclude_weekends": True,
                "exclude_holidays": True,
            },
        ]

        # New York
        self.rules["NY"] = [
            {
                "deadline_type": "response",
                "trigger": "service_of_summons",
                "base_days": 20,
                "rule_source": "CPLR 3012(a)",
                "description": "Time to answer summons (personal service)",
                "exclude_weekends": True,
                "exclude_holidays": True,
                "service_additions": {ServiceMethod.MAIL: 5, ServiceMethod.PERSONAL: 0},
            },
            {
                "deadline_type": "appeal",
                "trigger": "entry_of_judgment",
                "base_days": 30,
                "rule_source": "CPLR 5513",
                "description": "Time to file notice of appeal",
                "exclude_weekends": True,
                "exclude_holidays": True,
            },
        ]

        # Texas
        self.rules["TX"] = [
            {
                "deadline_type": "response",
                "trigger": "service_of_citation",
                "base_days": 20,
                "rule_source": "TRCP 99(b)",
                "description": "Monday following 20 days after service",
                "exclude_weekends": True,
                "exclude_holidays": True,
                "service_additions": {ServiceMethod.MAIL: 4, ServiceMethod.PERSONAL: 0},
            },
        ]

    def get_rule(
        self,
        jurisdiction: str,
        deadline_type: str,
        trigger: str | None = None,
    ) -> dict[str, Any] | None:
        """Retrieve specific rule from database"""
        if jurisdiction not in self.rules:
            return None

        for rule in self.rules[jurisdiction]:
            if rule["deadline_type"] == deadline_type:
                if trigger is None or rule.get("trigger") == trigger:
                    return rule

        return None

    def list_jurisdictions(self) -> list[str]:
        """List all supported jurisdictions"""
        return list(self.rules.keys())
