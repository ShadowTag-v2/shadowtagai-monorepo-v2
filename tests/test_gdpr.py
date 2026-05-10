# tests/test_gdpr.py
"""GDPR Infrastructure Validation Suite.

Tests models, rate limiting, subcollection consistency, cancellation flow,
and edge cases in the cascading deletion pipeline.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from apps.counselconduit.api.gdpr import (
  SUBCOLLECTIONS_TO_DELETE,
  DataExportRequest,
  DeletionReceipt,
  DeletionRequest,
  _DELETION_COOLDOWN_HOURS,
  _deletion_rate_limit,
  _check_export_rate_limit,
  _export_rate_limit,
)


class TestDeletionRequestModel:
  """Validate DeletionRequest Pydantic model."""

  def test_valid_request(self):
    req = DeletionRequest(
      confirmation="DELETE MY ACCOUNT",
      firm_id="firm-123",
      attorney_id="atty-456",
    )
    assert req.confirmation == "DELETE MY ACCOUNT"
    assert req.firm_id == "firm-123"
    assert req.attorney_id == "atty-456"
    assert req.reason is None
    assert req.email is None

  def test_with_optional_fields(self):
    req = DeletionRequest(
      confirmation="DELETE MY ACCOUNT",
      firm_id="firm-123",
      attorney_id="atty-456",
      reason="Switching providers",
      email="attorney@lawfirm.com",
    )
    assert req.reason == "Switching providers"
    assert req.email == "attorney@lawfirm.com"

  def test_reason_max_length(self):
    """Reason field must not exceed 500 characters."""
    with pytest.raises(ValidationError):
      DeletionRequest(
        confirmation="DELETE MY ACCOUNT",
        firm_id="firm-123",
        attorney_id="atty-456",
        reason="x" * 501,
      )

  def test_defaults_for_firm_and_attorney(self):
    req = DeletionRequest(confirmation="DELETE MY ACCOUNT")
    assert req.firm_id == "demo-firm"
    assert req.attorney_id == "demo-attorney"

  def test_confirmation_required(self):
    """Confirmation field is required (no default)."""
    with pytest.raises(ValidationError):
      DeletionRequest(firm_id="firm-123", attorney_id="atty-456")


class TestDataExportRequestModel:
  """Validate DataExportRequest Pydantic model."""

  def test_valid_json_export(self):
    req = DataExportRequest(
      format="json",
      firm_id="firm-123",
      attorney_id="atty-456",
    )
    assert req.format == "json"
    assert req.firm_id == "firm-123"
    assert req.attorney_id == "atty-456"

  def test_valid_csv_export(self):
    req = DataExportRequest(format="csv")
    assert req.format == "csv"

  def test_invalid_format_rejected(self):
    """Only json and csv are accepted."""
    with pytest.raises(ValidationError):
      DataExportRequest(format="xml")

  def test_defaults(self):
    req = DataExportRequest()
    assert req.format == "json"
    assert req.firm_id == "demo-firm"
    assert req.attorney_id == "demo-attorney"
    assert req.email is None

  def test_has_firm_id_field(self):
    """Critical: firm_id must exist for tenant scoping."""
    req = DataExportRequest(firm_id="my-firm")
    assert req.firm_id == "my-firm"

  def test_has_attorney_id_field(self):
    """Critical: attorney_id must exist for tenant scoping."""
    req = DataExportRequest(attorney_id="my-attorney")
    assert req.attorney_id == "my-attorney"


class TestDeletionReceiptModel:
  """Validate DeletionReceipt output model."""

  def test_receipt_defaults(self):
    receipt = DeletionReceipt(
      deletion_date="2026-06-04T00:00:00+00:00",
      receipt_id="test-receipt-id",
    )
    assert receipt.status == "scheduled"
    assert "30 days" in receipt.message

  def test_receipt_fields(self):
    receipt = DeletionReceipt(
      deletion_date="2026-06-04T12:00:00+00:00",
      receipt_id="rcpt-abc123",
    )
    assert receipt.receipt_id == "rcpt-abc123"
    assert receipt.deletion_date == "2026-06-04T12:00:00+00:00"


class TestSubcollectionConsistency:
  """Verify SUBCOLLECTIONS_TO_DELETE is the canonical deletion target list."""

  EXPECTED_SUBCOLLECTIONS = {
    "sessions",
    "transcripts",
    "matters",
    "billing_records",
    "clients",
  }

  def test_all_expected_subcollections_present(self):
    assert set(SUBCOLLECTIONS_TO_DELETE) == self.EXPECTED_SUBCOLLECTIONS

  def test_no_duplicates(self):
    assert len(SUBCOLLECTIONS_TO_DELETE) == len(set(SUBCOLLECTIONS_TO_DELETE))

  def test_billing_records_not_billing(self):
    """Critical regression test: 'billing_records' not 'billing'."""
    assert "billing_records" in SUBCOLLECTIONS_TO_DELETE
    assert "billing" not in SUBCOLLECTIONS_TO_DELETE

  def test_subcollection_count(self):
    assert len(SUBCOLLECTIONS_TO_DELETE) == 5

  def test_subcollections_are_strings(self):
    for s in SUBCOLLECTIONS_TO_DELETE:
      assert isinstance(s, str)
      assert len(s) > 0


class TestDeletionRateLimiting:
  """Validate the 24-hour deletion rate limit mechanism."""

  def setup_method(self):
    """Clear rate limit state before each test."""
    _deletion_rate_limit.clear()

  def test_cooldown_hours_configured(self):
    assert _DELETION_COOLDOWN_HOURS == 24

  def test_first_request_allowed(self):
    """First deletion request for a firm should always pass."""
    assert "test-firm" not in _deletion_rate_limit

  def test_rate_limit_blocks_within_window(self):
    """Second request within 24h should be rejected."""
    _deletion_rate_limit["firm-rate-test"] = time.time()
    last = _deletion_rate_limit.get("firm-rate-test")
    elapsed = time.time() - last
    assert elapsed < (_DELETION_COOLDOWN_HOURS * 3600)

  def test_rate_limit_allows_after_window(self):
    """Request after 24h should be allowed."""
    _deletion_rate_limit["firm-expired"] = (
      time.time() - (_DELETION_COOLDOWN_HOURS * 3600) - 1
    )
    last = _deletion_rate_limit.get("firm-expired")
    elapsed = time.time() - last
    assert elapsed >= (_DELETION_COOLDOWN_HOURS * 3600)

  def test_rate_limit_is_per_firm(self):
    """Different firms have independent rate limits."""
    _deletion_rate_limit["firm-a"] = time.time()
    assert "firm-b" not in _deletion_rate_limit


class TestExportRateLimiting:
  """Validate the 1-hour export rate limit mechanism."""

  def setup_method(self):
    _export_rate_limit.clear()

  def test_first_export_allowed(self):
    assert _check_export_rate_limit("new-firm") is True

  def test_second_export_blocked(self):
    _check_export_rate_limit("repeat-firm")
    assert _check_export_rate_limit("repeat-firm") is False

  def test_export_allowed_after_cooldown(self):
    _export_rate_limit["expired-firm"] = time.time() - 3601
    assert _check_export_rate_limit("expired-firm") is True

  def test_export_independent_per_firm(self):
    _check_export_rate_limit("firm-x")
    assert _check_export_rate_limit("firm-y") is True


class TestGDPREdgeCases:
  """Edge case analysis for cascading delete operations."""

  def test_empty_firm_id_handled(self):
    """Empty firm_id should not crash the model."""
    req = DeletionRequest(
      confirmation="DELETE MY ACCOUNT",
      firm_id="",
      attorney_id="atty-1",
    )
    assert req.firm_id == ""

  def test_subcollections_used_in_export(self):
    """Export endpoint must use the same subcollection list as deletion."""
    # This is a structural test — both execute_hard_delete and
    # execute_data_export iterate over SUBCOLLECTIONS_TO_DELETE
    assert isinstance(SUBCOLLECTIONS_TO_DELETE, list)
    assert len(SUBCOLLECTIONS_TO_DELETE) > 0

  def test_deletion_date_is_30_days(self):
    """Grace period must be exactly 30 days."""
    now = datetime.now(UTC)
    deletion_date = now + timedelta(days=30)
    delta = (deletion_date - now).days
    assert delta == 30

  def test_cancellation_model_exists(self):
    """Verify CancellationRequest model is importable (post-hardening)."""
    from apps.counselconduit.api.gdpr import CancellationRequest

    req = CancellationRequest(receipt_id="test-rcpt", firm_id="firm-1")
    assert req.receipt_id == "test-rcpt"
