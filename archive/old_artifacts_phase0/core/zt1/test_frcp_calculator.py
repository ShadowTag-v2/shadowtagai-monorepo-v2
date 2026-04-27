import datetime

from frcp_calculator import FRCPDeadlineCalculator

# --- Test Architect Validation Gates (Gemini 3.1 Pro Native) ---


def test_frcp_standard_computation():
    """FRCP: Adds days correctly when landing on a standard weekday."""
    trigger = datetime.date(2026, 4, 1)  # Wednesday
    # 21 days from Wed April 1 is Wed April 22 (A valid weekday)
    deadline = FRCPDeadlineCalculator.compute_deadline(trigger, 21)
    assert deadline == datetime.date(2026, 4, 22)


def test_frcp_weekend_rollover():
    """FRCP: If deadline lands on a Saturday, it must roll forward to Monday."""
    trigger = datetime.date(2026, 4, 3)  # Friday
    # 15 days from Friday April 3 is Saturday April 18.
    # Must roll to Monday April 20.
    deadline = FRCPDeadlineCalculator.compute_deadline(trigger, 15)
    assert deadline == datetime.date(2026, 4, 20)


def test_frcp_holiday_rollover():
    """FRCP: If deadline lands on a Holiday Monday, it must roll to Tuesday."""
    trigger = datetime.date(2026, 5, 4)  # Monday
    # 21 days from May 4 is Mon May 25 (Memorial Day).
    # Must roll to Tuesday May 26.
    deadline = FRCPDeadlineCalculator.compute_deadline(trigger, 21)
    assert deadline == datetime.date(2026, 5, 26)


def test_mcp_json_payload_validation():
    """Asserts the system properly gates the extraction payload for Human verification."""
    mock_agent_output = {"trigger_date": "2026-06-01", "duration_days": 14, "exhibit_id": "SUMMONS_001"}

    result = FRCPDeadlineCalculator.evaluate_mcp_extracted_payload(mock_agent_output)

    assert result["status"] == "pending_human_verification"  # The primary safety brake
    assert result["computed_under"] == "FRCP 6(a)"
    assert result["calculated_deadline"] == "2026-06-15"


def test_hallucination_trap():
    """Asserts that malformed outputs from the LLM extraction throw cleanly."""
    mock_hallucination = {"trigger_date": "Sometimes in June", "exhibit_id": "SUMMONS_002"}
    result = FRCPDeadlineCalculator.evaluate_mcp_extracted_payload(mock_hallucination)
    assert result["status"] == "error"
