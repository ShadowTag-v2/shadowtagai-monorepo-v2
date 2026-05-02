# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for the post-processing sanitizer logic in kairos_daemon's _generate_fn.

The daemon's _generate_fn applies a 4-step post-processing pipeline after
Tier 1 (Flash-Lite) returns raw text:
  1. Strip wrapping quotes/backticks
  2. Remove trailing periods
  3. Split on sentence boundaries (keep first fragment)
  4. Truncate to MAX_SUGGESTION_WORDS (12)

These tests verify each step independently and in combination, matching the
inline logic at kairos_daemon.py L1041-1047.
"""

from __future__ import annotations

import re


# Mirror the exact sanitization logic from kairos_daemon.py _generate_fn
MAX_SUGGESTION_WORDS = 12


def sanitize_suggestion(raw: str) -> str | None:
    """Apply the same post-processing as kairos_daemon._generate_fn.

    Returns None if the result is empty after cleaning.
    """
    if not raw or not raw.strip():
        return None
    # Step 1: Strip wrapping quotes and backticks
    cleaned = raw.strip().strip("\"'`").rstrip(".")
    # Step 2: Take first sentence fragment (before sentence boundaries)
    first_frag = re.split(r"[.!?]\s+", cleaned)[0].strip()
    # Step 3: Truncate to MAX_SUGGESTION_WORDS
    words = first_frag.split()
    if len(words) > MAX_SUGGESTION_WORDS:
        first_frag = " ".join(words[:MAX_SUGGESTION_WORDS])
    return first_frag if first_frag else None


class TestStripWrapping:
    """Step 1: Remove wrapping quotes and backticks."""

    def test_strip_double_quotes(self) -> None:
        assert sanitize_suggestion('"Run the tests"') == "Run the tests"

    def test_strip_single_quotes(self) -> None:
        assert sanitize_suggestion("'Deploy to staging'") == "Deploy to staging"

    def test_strip_backticks(self) -> None:
        assert sanitize_suggestion("`Check git status`") == "Check git status"

    def test_no_quotes_passthrough(self) -> None:
        assert sanitize_suggestion("Run the tests") == "Run the tests"

    def test_mixed_wrapping(self) -> None:
        # Only outer layer stripped
        result = sanitize_suggestion("\"'Run the tests'\"")
        assert "Run the tests" in result

    def test_leading_whitespace_stripped(self) -> None:
        assert sanitize_suggestion("  Run the tests  ") == "Run the tests"


class TestTrailingPeriod:
    """Step 2: Remove trailing periods."""

    def test_strip_trailing_period(self) -> None:
        assert sanitize_suggestion("Run the tests.") == "Run the tests"

    def test_strip_trailing_period_in_quotes(self) -> None:
        assert sanitize_suggestion('"Run the tests."') == "Run the tests"

    def test_no_period_passthrough(self) -> None:
        assert sanitize_suggestion("Run the tests") == "Run the tests"


class TestSentenceSplit:
    """Step 3: Keep only the first sentence fragment."""

    def test_single_sentence(self) -> None:
        assert sanitize_suggestion("Run the tests") == "Run the tests"

    def test_two_sentences(self) -> None:
        assert sanitize_suggestion("Run the tests. Then deploy") == "Run the tests"

    def test_question_split(self) -> None:
        assert sanitize_suggestion("Check the logs? Then fix") == "Check the logs"

    def test_exclamation_split(self) -> None:
        assert sanitize_suggestion("Deploy now! Then verify") == "Deploy now"

    def test_no_split_on_abbreviations(self) -> None:
        # Abbreviations like "v2.5" don't have space after the period
        assert sanitize_suggestion("Upgrade to v2.5 framework") == "Upgrade to v2.5 framework"


class TestWordTruncation:
    """Step 4: Cap at MAX_SUGGESTION_WORDS (12)."""

    def test_under_limit(self) -> None:
        text = "Run the full test suite now"
        assert sanitize_suggestion(text) == text

    def test_at_limit(self) -> None:
        text = " ".join(f"word{i}" for i in range(12))
        assert sanitize_suggestion(text) == text

    def test_over_limit(self) -> None:
        text = " ".join(f"word{i}" for i in range(15))
        result = sanitize_suggestion(text)
        assert result is not None
        assert len(result.split()) == 12

    def test_way_over_limit(self) -> None:
        text = " ".join(f"w{i}" for i in range(50))
        result = sanitize_suggestion(text)
        assert result is not None
        assert len(result.split()) == 12


class TestEdgeCases:
    """Edge cases and combined scenarios."""

    def test_empty_string(self) -> None:
        assert sanitize_suggestion("") is None

    def test_whitespace_only(self) -> None:
        assert sanitize_suggestion("   ") is None

    def test_only_quotes(self) -> None:
        assert sanitize_suggestion('""') is None

    def test_only_period(self) -> None:
        assert sanitize_suggestion(".") is None

    def test_combined_cleaning(self) -> None:
        """Full pipeline: quotes + period + sentence split + truncation."""
        raw = '"Run the full validation cascade. Then check all 15 files across the entire monorepo."'
        result = sanitize_suggestion(raw)
        assert result == "Run the full validation cascade"

    def test_real_flash_lite_output(self) -> None:
        """Simulated realistic Flash-Lite outputs."""
        examples = [
            ("Run the test suite", "Run the test suite"),
            ("'Check git status'", "Check git status"),
            ('"Deploy to staging."', "Deploy to staging"),
            ("Execute the validation cascade script", "Execute the validation cascade script"),
            ("Run ruff on changed files", "Run ruff on changed files"),
            ('"Fix the import statement. Then run lint."', "Fix the import statement"),
        ]
        for raw, expected in examples:
            assert sanitize_suggestion(raw) == expected, f"Failed for raw={raw!r}"


class TestFilterPipelineIntegration:
    """Test that sanitized output passes the 12-rule filter pipeline."""

    def test_sanitized_output_passes_filter(self) -> None:
        """After sanitization, valid suggestions should pass the filter."""
        from speculation_engine.suggestion import should_filter_suggestion

        valid_inputs = [
            "Run the test suite",
            '"Deploy to staging."',
            "'Check git status'",
            "`Refactor auth middleware`",
            "Execute the validation cascade script",
        ]
        for raw in valid_inputs:
            cleaned = sanitize_suggestion(raw)
            assert cleaned is not None, f"Sanitizer returned None for {raw!r}"
            reason = should_filter_suggestion(cleaned)
            assert reason is None, f"Filter rejected sanitized output {cleaned!r} from {raw!r}: {reason}"

    def test_claude_voice_still_filtered_after_sanitize(self) -> None:
        """Sanitizer doesn't strip Claude voice — the filter catches it."""
        from speculation_engine.suggestion import should_filter_suggestion

        claude_outputs = [
            "Let me run the tests for you",
            "I'll check the git status",
            "Here's what I found in the logs",
        ]
        for raw in claude_outputs:
            cleaned = sanitize_suggestion(raw)
            assert cleaned is not None
            reason = should_filter_suggestion(cleaned)
            assert reason is not None, f"Claude voice slipped through filter: {cleaned!r}"
