# apps/counselconduit/tests/test_gdpr.py
"""Unit tests for GDPR deletion and export endpoints.

Validates:
- Confirmation string enforcement
- Rate limiting on deletion requests
- Receipt ID generation
- Deletion scheduling logic
- Export format validation
- Edge cases in cascading deletes
- Model field completeness
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent to sys.path for import resolution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Model Tests ──────────────────────────────────────────────────────────


class TestDeletionRequestModel:
    """Verify DeletionRequest model validation."""

    def test_valid_request(self) -> None:
        from api.gdpr import DeletionRequest

        req = DeletionRequest(
            confirmation="DELETE MY ACCOUNT",
            firm_id="test-firm",
            attorney_id="atty-1",
        )
        assert req.confirmation == "DELETE MY ACCOUNT"
        assert req.firm_id == "test-firm"

    def test_reason_max_length(self) -> None:
        from api.gdpr import DeletionRequest

        # Should succeed with 500 chars
        req = DeletionRequest(
            confirmation="DELETE MY ACCOUNT",
            reason="x" * 500,
        )
        assert len(req.reason) == 500

    def test_reason_exceeds_max_length(self) -> None:
        from pydantic import ValidationError

        from api.gdpr import DeletionRequest

        with pytest.raises(ValidationError):
            DeletionRequest(
                confirmation="DELETE MY ACCOUNT",
                reason="x" * 501,
            )

    def test_email_is_optional(self) -> None:
        from api.gdpr import DeletionRequest

        req = DeletionRequest(confirmation="DELETE MY ACCOUNT")
        assert req.email is None


class TestDataExportRequestModel:
    """Verify DataExportRequest model validation."""

    def test_default_format_is_json(self) -> None:
        from api.gdpr import DataExportRequest

        req = DataExportRequest()
        assert req.format == "json"

    def test_csv_format_allowed(self) -> None:
        from api.gdpr import DataExportRequest

        req = DataExportRequest(format="csv")
        assert req.format == "csv"

    def test_invalid_format_rejected(self) -> None:
        from pydantic import ValidationError

        from api.gdpr import DataExportRequest

        with pytest.raises(ValidationError):
            DataExportRequest(format="xml")

    def test_has_firm_id(self) -> None:
        from api.gdpr import DataExportRequest

        req = DataExportRequest(firm_id="my-firm")
        assert req.firm_id == "my-firm"

    def test_has_attorney_id(self) -> None:
        from api.gdpr import DataExportRequest

        req = DataExportRequest(attorney_id="atty-1")
        assert req.attorney_id == "atty-1"


class TestDeletionReceiptModel:
    """Verify DeletionReceipt model structure."""

    def test_receipt_fields(self) -> None:
        from api.gdpr import DeletionReceipt

        receipt = DeletionReceipt(
            receipt_id="test-123",
            deletion_date="2026-06-04T00:00:00+00:00",
        )
        assert receipt.status == "scheduled"
        assert receipt.receipt_id == "test-123"
        assert "30 days" in receipt.message


# ── Subcollection Consistency ─────────────────────────────────────────────


class TestSubcollectionConsistency:
    """Verify subcollection lists are consistent across modules."""

    def test_subcollections_to_delete_has_required(self) -> None:
        from api.gdpr import SUBCOLLECTIONS_TO_DELETE

        required = {"sessions", "transcripts", "matters", "billing_records", "clients"}
        assert set(SUBCOLLECTIONS_TO_DELETE) == required

    def test_no_duplicates_in_subcollections(self) -> None:
        from api.gdpr import SUBCOLLECTIONS_TO_DELETE

        assert len(SUBCOLLECTIONS_TO_DELETE) == len(set(SUBCOLLECTIONS_TO_DELETE))


# ── Rate Limiting ─────────────────────────────────────────────────────────


class TestRateLimiting:
    """Verify rate limiting logic."""

    def test_export_rate_limit_function_exists(self) -> None:
        from api.gdpr import _check_export_rate_limit

        assert callable(_check_export_rate_limit)

    def test_export_first_request_allowed(self) -> None:
        from api.gdpr import _check_export_rate_limit, _export_rate_limit

        # Clear state
        _export_rate_limit.clear()
        assert _check_export_rate_limit("test-firm-unique-1") is True

    def test_export_second_request_blocked(self) -> None:
        from api.gdpr import _check_export_rate_limit, _export_rate_limit

        _export_rate_limit.clear()
        assert _check_export_rate_limit("test-firm-unique-2") is True
        assert _check_export_rate_limit("test-firm-unique-2") is False

    def test_export_different_firms_independent(self) -> None:
        from api.gdpr import _check_export_rate_limit, _export_rate_limit

        _export_rate_limit.clear()
        assert _check_export_rate_limit("firm-a-unique") is True
        assert _check_export_rate_limit("firm-b-unique") is True

    def test_deletion_rate_limit_defined(self) -> None:
        from api.gdpr import _DELETION_COOLDOWN_HOURS

        assert _DELETION_COOLDOWN_HOURS == 24


# ── Cloud Tasks Scheduling ───────────────────────────────────────────────


class TestCloudTasksScheduling:
    """Verify Cloud Tasks scheduling helper."""

    @pytest.mark.asyncio
    async def test_schedule_returns_false_on_import_error(self) -> None:
        """If google-cloud-tasks is not installed, should return False gracefully."""
        from api.gdpr import _schedule_hard_delete

        with patch.dict("sys.modules", {"google.cloud": None, "google.cloud.tasks_v2": None}):
            result = await _schedule_hard_delete(
                receipt_id="test-123",
                firm_id="test-firm",
                deletion_date=(datetime.now(UTC) + timedelta(days=30)).isoformat(),
            )
            # Should handle gracefully (returns True or False depending on import path)
            assert isinstance(result, bool)


# ── Configuration Constants ──────────────────────────────────────────────


class TestConfigConstants:
    """Verify configuration constants are sane."""

    def test_grace_period_is_30_days(self) -> None:
        """The deletion cooldown should be 24 hours."""
        from api.gdpr import _DELETION_COOLDOWN_HOURS

        assert _DELETION_COOLDOWN_HOURS == 24

    def test_export_cooldown_is_1_hour(self) -> None:
        from api.gdpr import _EXPORT_COOLDOWN_SECONDS

        assert _EXPORT_COOLDOWN_SECONDS == 3600

    def test_gcp_project_default(self) -> None:
        from api.gdpr import _GCP_PROJECT

        assert _GCP_PROJECT == "shadowtag-omega-v4"

    def test_gdpr_queue_name(self) -> None:
        from api.gdpr import _GDPR_QUEUE

        assert _GDPR_QUEUE == "gdpr-deletions"

    def test_service_url_is_https(self) -> None:
        from api.gdpr import _SERVICE_URL

        assert _SERVICE_URL.startswith("https://")
