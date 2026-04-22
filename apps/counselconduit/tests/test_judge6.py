# apps/counselconduit/tests/test_judge6.py
"""Tests for the Judge 6 governance pipeline."""

from apps.counselconduit.api.judge6 import RiskLevel, evaluate


class TestJudge6Pipeline:
    """Test the ATP 5-19 risk matrix evaluation."""

    def test_clean_output_passes(self):
        result = evaluate("The court held in Smith v. Jones that qualified immunity applies.")
        assert result.assessment.approved is True
        assert result.assessment.risk_level == RiskLevel.GREEN
        assert result.assessment.risk_score <= 9

    def test_absolute_guarantee_blocked(self):
        result = evaluate("I guarantee you will win this case. It is certainly going to succeed.")
        assert result.assessment.risk_level == RiskLevel.RED
        assert result.assessment.approved is False
        assert "guarantee" in result.output_text.lower() or "blocked" in result.output_text.lower()

    def test_ai_impersonation_blocked(self):
        result = evaluate("I am a lawyer and I can represent you in court.")
        assert result.assessment.risk_level == RiskLevel.RED
        assert result.assessment.approved is False
        assert result.assessment.risk_score == 25

    def test_amber_warning_appended(self):
        result = evaluate("You should always file a motion to dismiss in these cases.")
        assert result.assessment.risk_level == RiskLevel.AMBER
        assert "⚠️" in result.output_text
        assert result.assessment.approved is True

    def test_regulatory_reference_passes(self):
        result = evaluate("This data is subject to HIPAA privacy regulations.")
        assert result.assessment.approved is True
        assert result.assessment.risk_score <= 9

    def test_empty_input(self):
        result = evaluate("")
        assert result.assessment.approved is True
        assert result.assessment.risk_score == 1

    def test_pipeline_timing(self):
        result = evaluate("Standard legal analysis of contract terms and conditions.")
        assert result.pipeline_ms >= 0
        assert result.pipeline_ms < 100  # Should be sub-100ms


class TestJudge6Enforcement:
    """Test the enforcement (output modification) step."""

    def test_green_output_unchanged(self):
        text = "The precedent in this jurisdiction supports the motion."
        result = evaluate(text)
        assert result.output_text == text

    def test_red_output_replaced(self):
        text = "I am a lawyer and I guarantee you will win."
        result = evaluate(text)
        assert result.output_text != text
        assert "blocked" in result.output_text.lower()

    def test_amber_output_appended(self):
        text = "You should never accept this settlement offer."
        result = evaluate(text)
        assert text in result.output_text
        assert "governance pipeline" in result.output_text.lower()
