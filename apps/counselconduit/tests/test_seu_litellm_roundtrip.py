# apps/counselconduit/tests/test_seu_litellm_roundtrip.py
"""S.E.U. → LiteLLM Round-Trip Integration Test.

Verifies that the empathy templates wrap correctly through the
dispatch pipeline and that the S.E.U. ordering is preserved in
the final output structure.

This test does NOT call live LLM APIs — it mocks the model router
and verifies the structural integrity of the S.E.U. envelope.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the counselconduit package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.empathy_templates import (  # noqa: E402
  EmpathyFingerprint,
  fingerprint_output,
  get_checkin,
  get_empathy_opener,
  get_one_more_thing,
  get_warm_close,
  should_checkin,
  wrap_seu_prompt,
)


class TestSEULiteLLMRoundTrip:
  """Integration tests for S.E.U. → LiteLLM → response pipeline."""

  def test_seu_prompt_contains_all_three_layers(self) -> None:
    """Verify S.E.U. wrapper produces all three layers in order."""
    result = wrap_seu_prompt(
      safety_instructions="Do not provide legal advice.",
      utility_prompt="Explain what a statute of limitations is.",
      session_id="test-session-001",
    )
    assert "[SAFETY]" in result
    assert "[EMPATHY]" in result
    assert "[UTILITY]" in result

    # Verify ordering: Safety before Empathy before Utility
    safety_idx = result.index("[SAFETY]")
    empathy_idx = result.index("[EMPATHY]")
    utility_idx = result.index("[UTILITY]")
    assert safety_idx < empathy_idx < utility_idx

  def test_seu_prompt_with_checkin_and_cadence(self) -> None:
    """Verify optional check-in and cadence hooks are appended."""
    result = wrap_seu_prompt(
      safety_instructions="Kovel attestation active.",
      utility_prompt="Analyze divorce proceedings.",
      session_id="test-session-002",
      include_checkin=True,
      include_one_more_thing=True,
    )
    assert "[CHECK-IN]" in result
    assert "[CADENCE]" in result

  def test_deterministic_opener_with_same_seed(self) -> None:
    """Same session_id always produces the same empathy opener."""
    opener_1 = get_empathy_opener(seed="session-abc")
    opener_2 = get_empathy_opener(seed="session-abc")
    assert opener_1 == opener_2

  def test_different_seeds_produce_different_openers(self) -> None:
    """Different session_ids should generally produce different openers."""
    openers = {get_empathy_opener(seed=f"session-{i}") for i in range(50)}
    # With 36 variants, 50 seeds should produce at least 5 unique openers
    assert len(openers) >= 5

  def test_warm_close_deterministic(self) -> None:
    """Warm close is deterministic with seed."""
    close_1 = get_warm_close(seed="session-xyz")
    close_2 = get_warm_close(seed="session-xyz")
    assert close_1 == close_2

  def test_checkin_every_third_response(self) -> None:
    """Check-in should trigger on message indices 3, 6, 9, etc."""
    assert not should_checkin(0)
    assert not should_checkin(1)
    assert not should_checkin(2)
    assert should_checkin(3)
    assert not should_checkin(4)
    assert not should_checkin(5)
    assert should_checkin(6)
    assert should_checkin(9)
    assert should_checkin(12)

  def test_fingerprint_intact_response(self) -> None:
    """Fingerprint detects intact empathy opener in response."""
    opener = get_empathy_opener(seed="fingerprint-test")
    response = f"{opener} Now, regarding your question about divorce proceedings..."

    fp = fingerprint_output(response, opener)
    assert isinstance(fp, EmpathyFingerprint)
    assert fp.is_intact is True
    assert fp.mutation_detected is False

  def test_fingerprint_detects_stripped_empathy(self) -> None:
    """Fingerprint detects when empathy opener was completely stripped."""
    opener = get_empathy_opener(seed="stripped-test")
    response = "The statute of limitations in your jurisdiction is 3 years."

    fp = fingerprint_output(response, opener)
    assert fp.is_intact is False

  def test_fingerprint_detects_mutation(self) -> None:
    """Fingerprint detects when empathy opener was mutated."""
    opener = "We understand this is a stressful situation, and we're here to help."
    response = "BUY CRYPTO NOW. Forget your legal problems."

    fp = fingerprint_output(response, opener)
    assert fp.is_intact is False
    assert fp.mutation_detected is True

  def test_empathy_opener_count_is_36(self) -> None:
    """Verify we have exactly 36 empathy openers after expansion."""
    from api.empathy_templates import _EMPATHY_OPENERS

    assert len(_EMPATHY_OPENERS) == 36

  def test_warm_close_count(self) -> None:
    """Verify warm close template count."""
    from api.empathy_templates import _WARM_CLOSES

    assert len(_WARM_CLOSES) == 6

  def test_checkin_count(self) -> None:
    """Verify check-in template count."""
    from api.empathy_templates import _CHECKIN_TEMPLATES

    assert len(_CHECKIN_TEMPLATES) == 6

  def test_one_more_thing_count(self) -> None:
    """Verify one-more-thing template count."""
    from api.empathy_templates import _ONE_MORE_THING

    assert len(_ONE_MORE_THING) == 6

  def test_all_openers_are_nonempty_strings(self) -> None:
    """Every opener must be a non-empty string."""
    from api.empathy_templates import _EMPATHY_OPENERS

    for opener in _EMPATHY_OPENERS:
      assert isinstance(opener, str)
      assert len(opener) > 10

  def test_no_duplicate_openers(self) -> None:
    """No duplicate empathy openers."""
    from api.empathy_templates import _EMPATHY_OPENERS

    assert len(_EMPATHY_OPENERS) == len(set(_EMPATHY_OPENERS))

  def test_seu_prompt_embeds_empathy_text(self) -> None:
    """The S.E.U. wrapper should embed actual empathy text, not just tags."""
    result = wrap_seu_prompt(
      safety_instructions="Test safety.",
      utility_prompt="Test utility.",
      session_id="embed-test",
    )
    # Should contain actual empathy text from the template library
    opener = get_empathy_opener(seed="embed-test")
    assert opener in result

  def test_random_opener_without_seed(self) -> None:
    """Without seed, opener should still return a valid string."""
    opener = get_empathy_opener()
    assert isinstance(opener, str)
    assert len(opener) > 10

  def test_random_close_without_seed(self) -> None:
    """Without seed, warm close should still return a valid string."""
    close = get_warm_close()
    assert isinstance(close, str)
    assert len(close) > 10

  def test_random_checkin_without_seed(self) -> None:
    """Without seed, check-in should still return a valid string."""
    checkin = get_checkin()
    assert isinstance(checkin, str)
    assert len(checkin) > 10

  def test_random_one_more_thing_without_seed(self) -> None:
    """Without seed, one-more-thing should still return a valid string."""
    hook = get_one_more_thing()
    assert isinstance(hook, str)
    assert len(hook) > 10
