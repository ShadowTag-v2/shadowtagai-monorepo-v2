# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Jurisdiction Rule Engine — LegalTrack (Cloud Run Native)
================================
Applies jurisdiction-specific deadline math over a trigger date.
MVP baseline: FRCP (Federal Rules of Civil Procedure).
Local rule overlays are injected via RulePack objects.

Zero-CPU: pure Python date arithmetic only.
"""

import datetime
from dataclasses import dataclass, field
from typing import Any

# ── Federal court holidays (2025-2026) ────────────────────────────────────────

_FEDERAL_HOLIDAYS: frozenset[datetime.date] = frozenset(
    {
        # 2025
        datetime.date(2025, 1, 1),
        datetime.date(2025, 1, 20),
        datetime.date(2025, 2, 17),
        datetime.date(2025, 5, 26),
        datetime.date(2025, 7, 4),
        datetime.date(2025, 9, 1),
        datetime.date(2025, 10, 13),
        datetime.date(2025, 11, 11),
        datetime.date(2025, 11, 27),
        datetime.date(2025, 12, 25),
        # 2026
        datetime.date(2026, 1, 1),
        datetime.date(2026, 1, 19),
        datetime.date(2026, 2, 16),
        datetime.date(2026, 5, 25),
        datetime.date(2026, 7, 3),  # observed (July 4 is Saturday)
        datetime.date(2026, 9, 7),
        datetime.date(2026, 10, 12),
        datetime.date(2026, 11, 11),
        datetime.date(2026, 11, 26),
        datetime.date(2026, 12, 25),
    }
)


# ── Data structures ───────────────────────────────────────────────────────────


@dataclass
class DeadlineMath:
    """Portable deadline calculation spec — maps to rule_packs.deadline_math_json."""

    add_days: int
    business_days_only: bool = False
    local_holiday_set: frozenset[datetime.date] = field(default_factory=lambda: _FEDERAL_HOLIDAYS)


@dataclass
class RulePack:
    """Single jurisdiction rule — mirrors rule_packs DB row."""

    rule_id: str
    jurisdiction: str
    trigger_event_type: str
    math: DeadlineMath

    @classmethod
    def from_db_row(cls, row: dict[str, Any]) -> "RulePack":
        math_json: dict[str, Any] = row["deadline_math_json"]
        return cls(
            rule_id=str(row["rule_id"]),
            jurisdiction=row["jurisdiction"],
            trigger_event_type=row["trigger_event_type"],
            math=DeadlineMath(
                add_days=math_json["add_days"],
                business_days_only=math_json.get("business_days_only", False),
            ),
        )


# ── FRCP baseline rule packs ──────────────────────────────────────────────────

FRCP_RULES: list[RulePack] = [
    RulePack(
        rule_id="frcp-12a1ai",
        jurisdiction="FRCP",
        trigger_event_type="service_of_complaint",
        math=DeadlineMath(add_days=21, business_days_only=False),
    ),
    RulePack(
        rule_id="frcp-15a1a",
        jurisdiction="FRCP",
        trigger_event_type="service_of_pleading",
        math=DeadlineMath(add_days=21, business_days_only=False),
    ),
    RulePack(
        rule_id="frcp-56b",
        jurisdiction="FRCP",
        trigger_event_type="close_of_discovery",
        math=DeadlineMath(add_days=30, business_days_only=False),
    ),
    RulePack(
        rule_id="frcp-26a1",
        jurisdiction="FRCP",
        trigger_event_type="scheduling_order_entered",
        math=DeadlineMath(add_days=14, business_days_only=True),
    ),
]


# ── Engine ────────────────────────────────────────────────────────────────────


class JurisdictionEngine:
    """
    Applies deadline math to a trigger date under a specific jurisdiction.

    Usage:
        engine = JurisdictionEngine()
        due = engine.calculate(trigger_date, math)
    """

    def __init__(
        self,
        extra_holidays: frozenset[datetime.date] | None = None,
    ) -> None:
        self._holidays = _FEDERAL_HOLIDAYS | (extra_holidays or frozenset())

    def calculate(
        self,
        trigger_date: datetime.date,
        math: DeadlineMath,
    ) -> datetime.date:
        """Add days to trigger_date, optionally skipping non-business days."""
        if math.business_days_only:
            return self._add_business_days(trigger_date, math.add_days, math.local_holiday_set)
        due = trigger_date + datetime.timedelta(days=math.add_days)
        return self._push_off_weekend_holiday(due)

    def _add_business_days(
        self,
        start: datetime.date,
        days: int,
        holidays: frozenset[datetime.date],
    ) -> datetime.date:
        """Count only Mon-Fri non-holiday days."""
        current = start
        added = 0
        while added < days:
            current += datetime.timedelta(days=1)
            if current.weekday() < 5 and current not in holidays:
                added += 1
        return self._push_off_weekend_holiday(current)

    def _push_off_weekend_holiday(self, date: datetime.date) -> datetime.date:
        """If due date lands on weekend/holiday, push to next business day."""
        while date.weekday() >= 5 or date in self._holidays:
            date += datetime.timedelta(days=1)
        return date

    def resolve_rule(
        self,
        trigger_event_type: str,
        jurisdiction: str = "FRCP",
    ) -> RulePack | None:
        """Look up a built-in FRCP rule by trigger event."""
        for rule in FRCP_RULES:
            if rule.trigger_event_type == trigger_event_type and rule.jurisdiction == jurisdiction:
                return rule
        return None
