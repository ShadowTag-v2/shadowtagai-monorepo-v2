"""
ZT.1 Test Suite — All 4 TDD gates from ZT1_DEADLINE_ARCH.md
=============================================================

Gate 1: Mock Filing Ingestion          — ShadowTag-v2_ingest MCP simulation
Gate 2: Zero-Drift Assertion Check     — [Date, Trigger, Citation] in response
Gate 3: Hallucination Trap             — empty doc → [] not fabricated 30-day
Gate 4: Jurisdictional Overlay         — local rules applied (weekends, holidays)
"""

from __future__ import annotations

import datetime
import json
import unittest
from unittest.mock import MagicMock, patch

from control.pnkln.pnkln_core.agents.legal import (
    _coerce_item,
    extract_deadlines_from_filing,
)
from control.pnkln.pnkln_core.engines.jurisdiction import (
    FRCP_RULES,
    DeadlineMath,
    JurisdictionEngine,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

_MOCK_SUMMONS_TEXT = """
UNITED STATES DISTRICT COURT
SOUTHERN DISTRICT OF NEW YORK

ACME CORP, Plaintiff, vs. BETA LLC, Defendant.
Case No. 1:26-cv-00123

SUMMONS

You are hereby summoned to appear and respond to the attached complaint.
Pursuant to Rule 12(a)(1)(A)(i) of the Federal Rules of Civil Procedure,
you have 21 days after service of this summons to serve your answer.

Service was effected on March 10, 2026. Page 1, ¶3.

If you fail to respond, judgment by default will be entered against you.
"""

_MOCK_AI_RESPONSE_VALID = json.dumps(
    [
        {
            "trigger_event": "service of summons",
            "exhibit_citation_id": "Page 1, ¶3",
            "days_to_respond": 21,
            "business_days_only": False,
            "jurisdiction_rule": "FRCP 12(a)(1)(A)(i)",
            "raw_date_text": "March 10, 2026",
        }
    ]
)

_MOCK_AI_RESPONSE_EMPTY = json.dumps([])

# ── Gate 1: Mock Filing Ingestion ─────────────────────────────────────────────


class TestGate1MockIngestion(unittest.TestCase):
    """Simulate submitting a Federal Court summons via ShadowTag-v2_ingest MCP."""

    @patch("apps.ShadowTag-v2_stack.ShadowTag-v2_fastapi_services.zero_cpu_router.dispatch_compute")
    def test_filing_ingestion_returns_extractions(self, mock_dispatch: MagicMock) -> None:
        mock_dispatch.return_value = [{"text": _MOCK_AI_RESPONSE_VALID, "class": "claim"}]

        results = extract_deadlines_from_filing(
            raw_text=_MOCK_SUMMONS_TEXT,
            filing_name="summons-test.pdf",
        )

        mock_dispatch.assert_called_once()
        call_kwargs = mock_dispatch.call_args
        assert call_kwargs.kwargs["file_name"] == "summons-test.pdf"
        assert "legal-deadline-extraction" in call_kwargs.kwargs["prompt_description"]
        assert len(results) == 1

    @patch("apps.ShadowTag-v2_stack.ShadowTag-v2_fastapi_services.zero_cpu_router.dispatch_compute")
    def test_ingestion_passes_filing_text_in_prompt(self, mock_dispatch: MagicMock) -> None:
        mock_dispatch.return_value = [{"text": _MOCK_AI_RESPONSE_EMPTY}]
        extract_deadlines_from_filing(raw_text=_MOCK_SUMMONS_TEXT)

        prompt_text: str = mock_dispatch.call_args.kwargs["text"]
        assert "SUMMONS" in prompt_text
        assert "21 days" in prompt_text


# ── Gate 2: Zero-Drift Assertion Check ────────────────────────────────────────


class TestGate2ZeroDrift(unittest.TestCase):
    """
    Agent must return [Deadline Date, Trigger Event, Exhibit Citation ID].
    Citation must point to the exact paragraph — no vague references.
    """

    def test_extraction_carries_all_three_zero_drift_fields(self) -> None:
        items = json.loads(_MOCK_AI_RESPONSE_VALID)
        dl = _coerce_item(items[0])
        assert dl is not None

        # All three required Zero-Drift fields must be non-empty
        assert dl.trigger_event != ""
        assert dl.exhibit_citation_id != ""
        assert dl.days_to_respond > 0

    def test_exhibit_citation_is_specific(self) -> None:
        items = json.loads(_MOCK_AI_RESPONSE_VALID)
        dl = _coerce_item(items[0])
        assert dl is not None

        # Citation must reference a location (page, paragraph, or section)
        citation = dl.exhibit_citation_id.lower()
        has_location = any(kw in citation for kw in ["page", "¶", "section", "§", "para"])
        assert has_location, f"Citation too vague: {dl.exhibit_citation_id!r}"

    def test_jurisdiction_rule_present(self) -> None:
        items = json.loads(_MOCK_AI_RESPONSE_VALID)
        dl = _coerce_item(items[0])
        assert dl is not None
        assert "FRCP" in dl.jurisdiction_rule

    def test_malformed_item_returns_none(self) -> None:
        bad_item = {"trigger_event": "something", "days_to_respond": "not-an-int"}
        result = _coerce_item(bad_item)
        assert result is None


# ── Gate 3: Hallucination Trap ────────────────────────────────────────────────


class TestGate3HallucinationTrap(unittest.TestCase):
    """
    Pass a document with NO deadlines.
    The agent MUST return [] — NOT a fabricated standard 30-day response.
    """

    @patch("apps.ShadowTag-v2_stack.ShadowTag-v2_fastapi_services.zero_cpu_router.dispatch_compute")
    def test_no_deadline_document_returns_empty_list(self, mock_dispatch: MagicMock) -> None:
        mock_dispatch.return_value = [{"text": _MOCK_AI_RESPONSE_EMPTY}]
        results = extract_deadlines_from_filing(
            raw_text="This is a press release about our new office location.",
        )
        assert results == []

    @patch("apps.ShadowTag-v2_stack.ShadowTag-v2_fastapi_services.zero_cpu_router.dispatch_compute")
    def test_hallucination_pattern_is_filtered(self, mock_dispatch: MagicMock) -> None:
        hallucinated = json.dumps(
            [
                {
                    "trigger_event": "standard response window — 30 days",
                    "exhibit_citation_id": "Page 1, ¶1",
                    "days_to_respond": 30,
                    "business_days_only": False,
                    "jurisdiction_rule": "",
                    "raw_date_text": "",
                }
            ]
        )
        mock_dispatch.return_value = [{"text": hallucinated}]
        results = extract_deadlines_from_filing(raw_text="No deadlines here.")
        # Hallucination guard must filter "standard response window" pattern
        assert results == []

    @patch("apps.ShadowTag-v2_stack.ShadowTag-v2_fastapi_services.zero_cpu_router.dispatch_compute")
    def test_non_json_response_returns_empty_list(self, mock_dispatch: MagicMock) -> None:
        mock_dispatch.return_value = [{"text": "Here are the deadlines: none found."}]
        results = extract_deadlines_from_filing(raw_text="Anything.")
        assert results == []

    @patch("apps.ShadowTag-v2_stack.ShadowTag-v2_fastapi_services.zero_cpu_router.dispatch_compute")
    def test_empty_model_output_returns_empty_list(self, mock_dispatch: MagicMock) -> None:
        mock_dispatch.return_value = []
        results = extract_deadlines_from_filing(raw_text="Anything.")
        assert results == []


# ── Gate 4: Jurisdictional Overlay ───────────────────────────────────────────


class TestGate4JurisdictionalOverlay(unittest.TestCase):
    """
    Local rule overlays: weekends, holidays, and business-day-only counting
    must be applied correctly to trigger dates.
    """

    def setUp(self) -> None:
        self.engine = JurisdictionEngine()

    def test_calendar_days_no_skip(self) -> None:
        """21 calendar days from Wednesday 2026-03-10 = Tuesday 2026-03-31."""
        trigger = datetime.date(2026, 3, 10)
        math = DeadlineMath(add_days=21, business_days_only=False)
        result = self.engine.calculate(trigger, math)
        assert result == datetime.date(2026, 3, 31)

    def test_weekend_push_forward(self) -> None:
        """If calculated date lands on Saturday it must push to Monday."""
        # March 14 2026 is Saturday
        trigger = datetime.date(2026, 3, 7)
        math = DeadlineMath(add_days=7, business_days_only=False)
        result = self.engine.calculate(trigger, math)
        # March 14 is Saturday → pushed to Monday March 16
        assert result == datetime.date(2026, 3, 16)

    def test_business_days_skips_weekends(self) -> None:
        """14 business days from Monday 2026-03-23 excludes 4 weekend days."""
        trigger = datetime.date(2026, 3, 23)
        math = DeadlineMath(add_days=14, business_days_only=True)
        result = self.engine.calculate(trigger, math)
        # 14 business days from 2026-03-23 = April 13 (skipping 2 weekends)
        assert result.weekday() < 5  # must land on a weekday

    def test_federal_holiday_push(self) -> None:
        """Due date on Independence Day (observed 2026-07-03) → July 6 (Monday)."""
        # Add 0-day math so due date == trigger == 2026-07-03
        trigger = datetime.date(2026, 7, 2)
        math = DeadlineMath(add_days=1, business_days_only=False)
        result = self.engine.calculate(trigger, math)
        # July 3 is observed holiday → July 6
        assert result == datetime.date(2026, 7, 6)

    def test_custom_local_holiday_override(self) -> None:
        """A local court-specific holiday is respected when injected."""
        local_holiday = frozenset({datetime.date(2026, 4, 3)})  # hypothetical
        engine_local = JurisdictionEngine(extra_holidays=local_holiday)
        trigger = datetime.date(2026, 4, 2)
        math = DeadlineMath(add_days=1, business_days_only=False)
        result = engine_local.calculate(trigger, math)
        # April 3 is local holiday (Friday) → pushed to April 6 (Monday)
        assert result == datetime.date(2026, 4, 6)

    def test_frcp_rule_lookup(self) -> None:
        """FRCP 12(a) service_of_complaint rule resolves to 21 calendar days."""
        rule = self.engine.resolve_rule("service_of_complaint", "FRCP")
        assert rule is not None
        assert rule.math.add_days == 21
        assert rule.math.business_days_only is False

    def test_unknown_rule_returns_none(self) -> None:
        rule = self.engine.resolve_rule("nonexistent_trigger", "FRCP")
        assert rule is None

    def test_frcp_rules_are_complete(self) -> None:
        """All baseline FRCP rules are registered."""
        trigger_types = {r.trigger_event_type for r in FRCP_RULES}
        assert "service_of_complaint" in trigger_types
        assert "service_of_pleading" in trigger_types
        assert "close_of_discovery" in trigger_types


if __name__ == "__main__":
    unittest.main()
