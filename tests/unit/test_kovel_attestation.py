"""Unit tests for Kovel Attestation Receipt System.

Tests cover:
- SHA-256 text hashing
- HMAC receipt signing
- Attestation generation
- Attestation verification
- Rate limiting
- Tamper detection
"""

from __future__ import annotations

import hashlib

import pytest


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
  """Reset in-memory rate limiter between tests."""
  from apps.counselconduit.api.kovel_attestation import _rate_windows

  _rate_windows.clear()
  yield
  _rate_windows.clear()


@pytest.fixture
def attestation_request():
  """Create a standard AttestationRequest for testing."""
  from apps.counselconduit.api.kovel_attestation import AttestationRequest

  return AttestationRequest(
    session_id="sess_test_001",
    attorney_id="atty_test_001",
    firm_id="firm_test_001",
    client_id="client_test_001",
    model_used="gemini-3.1-flash-lite",
    query_text="What are the legal implications of X?",
    response_text="Based on precedent in Y v. Z, the implications are...",
  )


class TestHashText:
  """Tests for _hash_text."""

  def test_deterministic(self):
    from apps.counselconduit.api.kovel_attestation import _hash_text

    assert _hash_text("hello") == _hash_text("hello")

  def test_sha256(self):
    from apps.counselconduit.api.kovel_attestation import _hash_text

    expected = hashlib.sha256(b"hello").hexdigest()
    assert _hash_text("hello") == expected

  def test_different_inputs_different_hashes(self):
    from apps.counselconduit.api.kovel_attestation import _hash_text

    assert _hash_text("query A") != _hash_text("query B")

  def test_empty_string(self):
    from apps.counselconduit.api.kovel_attestation import _hash_text

    result = _hash_text("")
    assert len(result) == 64  # SHA-256 hex digest length


class TestSignReceipt:
  """Tests for _sign_receipt."""

  def test_deterministic(self):
    from apps.counselconduit.api.kovel_attestation import _sign_receipt

    body = {"key": "value", "num": 1}
    assert _sign_receipt(body) == _sign_receipt(body)

  def test_different_bodies_different_signatures(self):
    from apps.counselconduit.api.kovel_attestation import _sign_receipt

    sig1 = _sign_receipt({"key": "value1"})
    sig2 = _sign_receipt({"key": "value2"})
    assert sig1 != sig2

  def test_key_order_irrelevant(self):
    """sort_keys=True should make key order deterministic."""
    from apps.counselconduit.api.kovel_attestation import _sign_receipt

    sig1 = _sign_receipt({"b": 2, "a": 1})
    sig2 = _sign_receipt({"a": 1, "b": 2})
    assert sig1 == sig2

  def test_signature_format(self):
    from apps.counselconduit.api.kovel_attestation import _sign_receipt

    sig = _sign_receipt({"test": "data"})
    assert len(sig) == 64  # HMAC-SHA256 hex digest
    assert all(c in "0123456789abcdef" for c in sig)


class TestGenerateAttestation:
  """Tests for generate_attestation."""

  def test_generates_valid_attestation(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import generate_attestation

    result = generate_attestation(attestation_request)
    assert result.session_id == "sess_test_001"
    assert result.attorney_id == "atty_test_001"
    assert result.firm_id == "firm_test_001"
    assert result.privilege_type == "kovel_doctrine"

  def test_hashes_query_text(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import generate_attestation

    result = generate_attestation(attestation_request)
    expected_hash = hashlib.sha256(attestation_request.query_text.encode()).hexdigest()
    assert result.query_hash == expected_hash

  def test_hashes_response_text(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import generate_attestation

    result = generate_attestation(attestation_request)
    expected_hash = hashlib.sha256(
      attestation_request.response_text.encode()
    ).hexdigest()
    assert result.response_hash == expected_hash

  def test_unique_attestation_ids(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import generate_attestation

    a1 = generate_attestation(attestation_request)
    a2 = generate_attestation(attestation_request)
    assert a1.attestation_id != a2.attestation_id

  def test_has_hmac_signature(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import generate_attestation

    result = generate_attestation(attestation_request)
    assert result.hmac_signature
    assert len(result.hmac_signature) == 64

  def test_timestamp_format(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import generate_attestation

    result = generate_attestation(attestation_request)
    # ISO 8601 format
    assert "T" in result.timestamp
    assert "+" in result.timestamp or "Z" in result.timestamp


class TestVerifyAttestation:
  """Tests for verify_attestation."""

  def test_valid_attestation_verifies(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import (
      generate_attestation,
      verify_attestation,
    )

    attestation = generate_attestation(attestation_request)
    assert verify_attestation(attestation) is True

  def test_tampered_signature_fails(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import (
      generate_attestation,
      verify_attestation,
    )

    attestation = generate_attestation(attestation_request)
    attestation.hmac_signature = "a" * 64  # tamper
    assert verify_attestation(attestation) is False

  def test_tampered_field_fails(self, attestation_request):
    from apps.counselconduit.api.kovel_attestation import (
      generate_attestation,
      verify_attestation,
    )

    attestation = generate_attestation(attestation_request)
    attestation.client_id = "TAMPERED_CLIENT"
    assert verify_attestation(attestation) is False


class TestRateLimiting:
  """Tests for _check_rate_limit."""

  def test_allows_under_limit(self):
    from apps.counselconduit.api.kovel_attestation import _check_rate_limit

    for _ in range(10):
      assert _check_rate_limit("firm_a") is True

  def test_blocks_over_limit(self):
    from apps.counselconduit.api.kovel_attestation import _check_rate_limit

    for _ in range(10):
      _check_rate_limit("firm_a")
    assert _check_rate_limit("firm_a") is False

  def test_independent_per_firm(self):
    from apps.counselconduit.api.kovel_attestation import _check_rate_limit

    for _ in range(10):
      _check_rate_limit("firm_a")
    # firm_b should still be allowed
    assert _check_rate_limit("firm_b") is True


class TestModels:
  """Tests for Pydantic models."""

  def test_attestation_request_valid(self):
    from apps.counselconduit.api.kovel_attestation import AttestationRequest

    req = AttestationRequest(
      session_id="s1",
      attorney_id="a1",
      firm_id="f1",
      client_id="c1",
      model_used="gemini",
      query_text="q",
      response_text="r",
    )
    assert req.session_id == "s1"

  def test_session_attestation_default_metadata(self):
    from apps.counselconduit.api.kovel_attestation import SessionAttestation

    att = SessionAttestation(
      attestation_id="id1",
      session_id="s1",
      attorney_id="a1",
      firm_id="f1",
      client_id="c1",
      model_used="gemini",
      query_hash="h1",
      response_hash="h2",
      timestamp="2026-01-01T00:00:00Z",
      hmac_signature="sig",
    )
    assert att.metadata == {}
    assert att.privilege_type == "kovel_doctrine"
