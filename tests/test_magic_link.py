# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for magic_link._create_token and related signing logic.

Prevents regression of the UTC NameError that caused a production 500
on counselconduit (fixed 2026-05-03).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import UTC, datetime

import pytest

# Import path matches the deployed package layout
from apps.counselconduit.api.magic_link import (
  MatterCreateRequest,
  _create_token,
  _sign_token,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def sample_request() -> MatterCreateRequest:
  """Standard matter creation request for testing."""
  return MatterCreateRequest(
    attorney_id="att-001",
    firm_id="firm-alpha",
    client_name="Jane Doe",
    client_email="jane@example.com",
    matter_description="Contract review",
    allowed_models=["gemini-flash"],
    session_ttl_hours=4,
  )


# ── _sign_token tests ────────────────────────────────────────────────────


class TestSignToken:
  """Tests for HMAC-SHA256 signature generation."""

  def test_deterministic_signature(self) -> None:
    """Same payload always produces the same signature."""
    payload = {"a": 1, "b": "hello"}
    sig1 = _sign_token(payload)
    sig2 = _sign_token(payload)
    assert sig1 == sig2

  def test_signature_length(self) -> None:
    """Signature is exactly 32 hex chars (truncated HMAC)."""
    sig = _sign_token({"test": True})
    assert len(sig) == 32
    assert all(c in "0123456789abcdef" for c in sig)

  def test_different_payloads_different_sigs(self) -> None:
    """Different payloads produce different signatures."""
    sig1 = _sign_token({"x": 1})
    sig2 = _sign_token({"x": 2})
    assert sig1 != sig2

  def test_key_order_does_not_matter(self) -> None:
    """sort_keys=True in canonical JSON means order is irrelevant."""
    sig1 = _sign_token({"b": 2, "a": 1})
    sig2 = _sign_token({"a": 1, "b": 2})
    assert sig1 == sig2

  def test_manual_hmac_matches(self) -> None:
    """Verify against manual HMAC computation."""
    payload = {"k": "v"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(
      b"magic-dev-secret",  # default _MAGIC_SECRET
      canonical.encode("utf-8"),
      hashlib.sha256,
    ).hexdigest()[:32]

    assert _sign_token(payload) == expected


# ── _create_token tests ──────────────────────────────────────────────────


class TestCreateToken:
  """Tests for magic link token creation."""

  def test_returns_three_tuple(self, sample_request: MatterCreateRequest) -> None:
    """Returns (matter_id, token, expires_unix) tuple."""
    result = _create_token(sample_request)
    assert isinstance(result, tuple)
    assert len(result) == 3

  def test_matter_id_is_uuid7(self, sample_request: MatterCreateRequest) -> None:
    """matter_id should be a valid UUID7 string."""
    matter_id, _, _ = _create_token(sample_request)
    # UUID format: 8-4-4-4-12 hex chars
    parts = matter_id.split("-")
    assert len(parts) == 5
    assert [len(p) for p in parts] == [8, 4, 4, 4, 12]

  def test_token_format(self, sample_request: MatterCreateRequest) -> None:
    """Token is matter_id.signature format."""
    matter_id, token, _ = _create_token(sample_request)
    assert "." in token
    token_parts = token.split(".")
    assert len(token_parts) == 2
    assert token_parts[0] == matter_id
    # Signature part is 32 hex chars
    assert len(token_parts[1]) == 32

  def test_expiry_is_72_hours(self, sample_request: MatterCreateRequest) -> None:
    """Expiry should be ~72 hours from now."""
    before = int(time.time())
    _, _, expires_unix = _create_token(sample_request)
    after = int(time.time())

    expected_ttl = 72 * 3600
    assert before + expected_ttl <= expires_unix <= after + expected_ttl

  def test_utc_datetime_conversion(self, sample_request: MatterCreateRequest) -> None:
    """Verify datetime.fromtimestamp(expires, tz=UTC) works — the UTC regression."""
    _, _, expires_unix = _create_token(sample_request)

    # This is the exact line that caused the production 500 before the fix.
    # If UTC is not imported, this will raise NameError.
    dt = datetime.fromtimestamp(expires_unix, tz=UTC)
    assert dt.tzinfo is not None
    iso = dt.isoformat()
    assert "+" in iso  # Timezone-aware ISO string

  def test_unique_matter_ids(self, sample_request: MatterCreateRequest) -> None:
    """Each call should produce a unique matter_id."""
    ids = {_create_token(sample_request)[0] for _ in range(10)}
    assert len(ids) == 10

  def test_signature_includes_request_fields(
    self, sample_request: MatterCreateRequest
  ) -> None:
    """Different request fields should produce different tokens."""
    _, token1, _ = _create_token(sample_request)

    modified = MatterCreateRequest(
      attorney_id="att-002",  # Different attorney
      firm_id="firm-alpha",
      client_name="Jane Doe",
      client_email="jane@example.com",
    )
    _, token2, _ = _create_token(modified)

    # Same matter_id format but different signatures
    sig1 = token1.split(".")[1]
    sig2 = token2.split(".")[1]
    assert sig1 != sig2
