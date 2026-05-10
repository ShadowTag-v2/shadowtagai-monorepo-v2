# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for S.E.U. Prompt Conformance Validator (Risk #62)."""

from __future__ import annotations


from agnt_classifier.seu_validator import (
  SEUSection,
  SEUValidator,
)


class TestLineClassification:
  """Verify individual line classification."""

  def test_safety_line(self):
    v = SEUValidator()
    assert (
      v.classify_line("WARNING: This is not a substitute for legal advice")
      == SEUSection.SAFETY
    )

  def test_empathy_line(self):
    v = SEUValidator()
    assert (
      v.classify_line("I understand your concern, that's a great question")
      == SEUSection.EMPATHY
    )

  def test_utility_line(self):
    v = SEUValidator()
    assert (
      v.classify_line("Here is the code to implement the feature") == SEUSection.UTILITY
    )

  def test_empty_line(self):
    v = SEUValidator()
    assert v.classify_line("") == SEUSection.UNKNOWN

  def test_whitespace_only(self):
    v = SEUValidator()
    assert v.classify_line("   ") == SEUSection.UNKNOWN


class TestCompliantPrompts:
  """Verify prompts that follow S→E→U ordering pass."""

  def test_correct_seu_order(self):
    prompt = """IMPORTANT: Please consult a qualified attorney for specific legal advice.

I understand your situation and appreciate you reaching out.

Here is a summary of the relevant case law and recommended next steps."""
    v = SEUValidator()
    result = v.check(prompt)
    assert result.is_compliant is True
    assert result.score == 1.0

  def test_safety_only(self):
    prompt = "WARNING: This tool has limitations and cannot guarantee accuracy."
    v = SEUValidator()
    result = v.check(prompt)
    assert result.is_compliant is True

  def test_utility_only(self):
    prompt = "Here is the analysis of your contract terms."
    v = SEUValidator()
    result = v.check(prompt)
    assert result.is_compliant is True

  def test_empty_text(self):
    v = SEUValidator()
    result = v.check("")
    assert result.is_compliant is True
    assert result.score == 1.0


class TestNonCompliantPrompts:
  """Verify prompts that violate S→E→U ordering are caught."""

  def test_utility_before_safety(self):
    prompt = """Here is the contract analysis you requested.

IMPORTANT: Please note this is not a substitute for professional legal advice."""
    v = SEUValidator()
    result = v.check(prompt)
    assert result.is_compliant is False
    assert len(result.violations) > 0

  def test_empathy_before_safety(self):
    prompt = """Thank you for reaching out, I appreciate your patience.

WARNING: This tool cannot guarantee accuracy of legal citations."""
    v = SEUValidator()
    result = v.check(prompt)
    assert result.is_compliant is False

  def test_violation_has_line_number(self):
    prompt = """Here is the code.\n\nIMPORTANT: Exercise caution."""
    v = SEUValidator()
    result = v.check(prompt)
    assert result.is_compliant is False
    assert result.violations[0].line_number > 0

  def test_score_degrades_with_violations(self):
    prompt = """The answer is 42.\nPlease be aware of limitations.\nHappy to help!\nDo not share this."""
    v = SEUValidator()
    result = v.check(prompt)
    assert result.score < 1.0


class TestSourceFile:
  """Verify source file tracking in results."""

  def test_source_file_in_violations(self):
    prompt = "Here is code.\nIMPORTANT: Security warning."
    v = SEUValidator()
    result = v.check(prompt, source_file="prompts/legal.md")
    if result.violations:
      assert result.violations[0].source_file == "prompts/legal.md"


class TestSectionSequence:
  """Verify section sequence tracking."""

  def test_sections_found_order(self):
    prompt = """IMPORTANT disclaimer about limitations.

I understand your concern.

Here is the solution."""
    v = SEUValidator()
    result = v.check(prompt)
    # Should contain S, E, U in order
    assert SEUSection.SAFETY in result.sections_found
    assert SEUSection.UTILITY in result.sections_found
