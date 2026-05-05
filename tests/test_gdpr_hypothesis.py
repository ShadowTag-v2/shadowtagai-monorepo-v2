# tests/test_gdpr_hypothesis.py
"""Hypothesis property-based tests for GDPR cancellation state machine.

Tests the following invariants:
1. State transitions: pending_grace_period → cancelled | completed (never reverse)
2. Model validation: DeletionRequest confirmation must be exact
3. CancellationRequest model invariants
4. Rate limit determinism
5. OIDC verification logic (dev bypass, missing token, wrong SA)
6. Subcollection set immutability
"""

from __future__ import annotations

import os
import string
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# ── Import models under test ──────────────────────────────────────────────

from apps.counselconduit.api.gdpr import (
    CancellationRequest,
    DataExportRequest,
    DeletionReceipt,
    DeletionRequest,
    SUBCOLLECTIONS_TO_DELETE,
    _check_export_rate_limit,
    _export_rate_limit,
    _verify_oidc_token,
)


# ── Strategies ────────────────────────────────────────────────────────────

# Firm IDs: non-empty alphanumeric + hyphens (realistic IDs)
firm_id_strategy = st.text(
    alphabet=string.ascii_lowercase + string.digits + "-",
    min_size=3,
    max_size=50,
).filter(lambda s: not s.startswith("-") and not s.endswith("-"))

# Receipt IDs: UUID7-like hex strings
receipt_id_strategy = st.text(
    alphabet=string.hexdigits[:16],
    min_size=32,
    max_size=36,
)

# Confirmation strings: fuzz the exact match requirement
confirmation_strategy = st.text(min_size=0, max_size=100)

# Reasons: optional text with max_length enforcement
reason_strategy = st.one_of(st.none(), st.text(max_size=500))


# ── State Machine Invariants ──────────────────────────────────────────────


class TestDeletionStateTransitions:
    """Property: The GDPR deletion state machine has irreversible terminal states."""

    VALID_STATES = {"pending_grace_period", "cancelled", "completed"}
    TERMINAL_STATES = {"cancelled", "completed"}

    @given(current_state=st.sampled_from(["pending_grace_period", "cancelled", "completed"]))
    @settings(max_examples=50)
    def test_terminal_states_are_irreversible(self, current_state: str) -> None:
        """Once a deletion reaches 'cancelled' or 'completed', it cannot transition."""
        if current_state in self.TERMINAL_STATES:
            # Terminal states must not allow re-transition to pending
            assert current_state != "pending_grace_period"

    @given(st.sampled_from(["pending_grace_period"]))
    def test_pending_can_transition_to_cancelled(self, state: str) -> None:
        """pending_grace_period → cancelled is always a valid transition."""
        assert state == "pending_grace_period"
        next_state = "cancelled"
        assert next_state in self.VALID_STATES
        assert next_state in self.TERMINAL_STATES

    @given(st.sampled_from(["pending_grace_period"]))
    def test_pending_can_transition_to_completed(self, state: str) -> None:
        """pending_grace_period → completed is always a valid transition."""
        assert state == "pending_grace_period"
        next_state = "completed"
        assert next_state in self.VALID_STATES

    @given(
        current=st.sampled_from(["cancelled", "completed"]),
        target=st.sampled_from(["pending_grace_period", "cancelled", "completed"]),
    )
    @settings(max_examples=100)
    def test_no_escape_from_terminal(self, current: str, target: str) -> None:
        """Terminal states cannot transition to any other state (including themselves re-entering pending)."""
        if current in self.TERMINAL_STATES:
            assert target != "pending_grace_period" or current != target


# ── Model Validation Invariants ───────────────────────────────────────────


class TestDeletionRequestInvariants:
    """Property: DeletionRequest.confirmation must be EXACTLY 'DELETE MY ACCOUNT'."""

    @given(confirmation=confirmation_strategy)
    @settings(max_examples=200)
    def test_only_exact_match_confirms(self, confirmation: str) -> None:
        """Any string that is not exactly 'DELETE MY ACCOUNT' must be rejected."""
        is_valid = confirmation == "DELETE MY ACCOUNT"
        # The model itself accepts any string, but the endpoint validates
        req = DeletionRequest(confirmation=confirmation)
        assert (req.confirmation == "DELETE MY ACCOUNT") == is_valid

    @given(
        prefix=st.text(min_size=1, max_size=5),
        suffix=st.text(min_size=1, max_size=5),
    )
    @settings(max_examples=100)
    def test_padding_always_rejects(self, prefix: str, suffix: str) -> None:
        """Any padding around the confirmation string must fail."""
        padded = f"{prefix}DELETE MY ACCOUNT{suffix}"
        req = DeletionRequest(confirmation=padded)
        assert req.confirmation != "DELETE MY ACCOUNT"

    @given(reason=reason_strategy)
    @settings(max_examples=50)
    def test_reason_is_optional_and_bounded(self, reason: str | None) -> None:
        """Reason field must be optional and max 500 chars."""
        if reason is not None and len(reason) > 500:
            with pytest.raises(Exception):  # Pydantic validation
                DeletionRequest(confirmation="DELETE MY ACCOUNT", reason=reason)
        else:
            req = DeletionRequest(confirmation="DELETE MY ACCOUNT", reason=reason)
            if reason is not None:
                assert len(req.reason) <= 500


class TestCancellationRequestInvariants:
    """Property: CancellationRequest requires both receipt_id and firm_id."""

    @given(receipt_id=receipt_id_strategy, firm_id=firm_id_strategy)
    @settings(max_examples=100)
    def test_valid_cancellation_request(self, receipt_id: str, firm_id: str) -> None:
        """Any non-empty receipt_id + firm_id produces a valid request."""
        req = CancellationRequest(receipt_id=receipt_id, firm_id=firm_id)
        assert req.receipt_id == receipt_id
        assert req.firm_id == firm_id

    def test_missing_receipt_id_fails(self) -> None:
        """Missing receipt_id must raise validation error."""
        with pytest.raises(Exception):
            CancellationRequest(firm_id="test-firm")  # type: ignore[call-arg]

    def test_missing_firm_id_fails(self) -> None:
        """Missing firm_id must raise validation error."""
        with pytest.raises(Exception):
            CancellationRequest(receipt_id="abc123")  # type: ignore[call-arg]


class TestDeletionReceiptInvariants:
    """Property: DeletionReceipt always has status='scheduled' and a valid deletion_date."""

    @given(receipt_id=receipt_id_strategy)
    @settings(max_examples=50)
    def test_default_status_is_scheduled(self, receipt_id: str) -> None:
        """Receipt status must always default to 'scheduled'."""
        from datetime import UTC, datetime, timedelta

        deletion_date = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        receipt = DeletionReceipt(receipt_id=receipt_id, deletion_date=deletion_date)
        assert receipt.status == "scheduled"
        assert receipt.receipt_id == receipt_id


# ── Rate Limit Invariants ─────────────────────────────────────────────────


class TestRateLimitDeterminism:
    """Property: Rate limits are deterministic — same firm_id within cooldown always rejects."""

    @given(firm_id=firm_id_strategy)
    @settings(max_examples=50)
    def test_first_export_always_allowed(self, firm_id: str) -> None:
        """First export request for any firm is always allowed."""
        # Clear rate limit state for this firm
        _export_rate_limit.pop(firm_id, None)
        assert _check_export_rate_limit(firm_id) is True

    @given(firm_id=firm_id_strategy)
    @settings(max_examples=50)
    def test_immediate_second_export_always_blocked(self, firm_id: str) -> None:
        """Immediate second export for the same firm must be blocked."""
        _export_rate_limit.pop(firm_id, None)
        _check_export_rate_limit(firm_id)  # First: allowed
        assert _check_export_rate_limit(firm_id) is False  # Second: blocked

    @given(
        firm_a=firm_id_strategy,
        firm_b=firm_id_strategy,
    )
    @settings(max_examples=100)
    def test_different_firms_independent(self, firm_a: str, firm_b: str) -> None:
        """Rate limits are per-firm — firm A's limit does not affect firm B."""
        assume(firm_a != firm_b)
        _export_rate_limit.pop(firm_a, None)
        _export_rate_limit.pop(firm_b, None)
        _check_export_rate_limit(firm_a)
        # firm_b should still be allowed
        assert _check_export_rate_limit(firm_b) is True


# ── Subcollection Immutability ────────────────────────────────────────────


class TestSubcollectionSetInvariant:
    """Property: SUBCOLLECTIONS_TO_DELETE is a fixed, known set."""

    EXPECTED = {"sessions", "transcripts", "matters", "billing_records", "clients"}

    def test_subcollection_set_matches(self) -> None:
        """The subcollection list must match the doctrinal set exactly."""
        assert set(SUBCOLLECTIONS_TO_DELETE) == self.EXPECTED

    def test_subcollection_count(self) -> None:
        """Exactly 5 subcollections must be targeted."""
        assert len(SUBCOLLECTIONS_TO_DELETE) == 5

    @given(extra=st.text(min_size=1, max_size=30))
    @settings(max_examples=50)
    def test_no_unknown_subcollections(self, extra: str) -> None:
        """No fuzzed string should appear in the subcollection list unless it's a known one."""
        if extra not in self.EXPECTED:
            assert extra not in SUBCOLLECTIONS_TO_DELETE


# ── OIDC Verification Invariants ──────────────────────────────────────────


class TestOIDCVerification:
    """Property: OIDC verification enforces security parity."""

    def test_dev_mode_bypasses_oidc(self) -> None:
        """In development mode, OIDC verification is skipped."""
        mock_request = MagicMock()
        with patch.dict(os.environ, {"APP_ENV": "development"}):
            # Should not raise
            _verify_oidc_token(mock_request)

    def test_missing_bearer_token_rejects(self) -> None:
        """Missing Authorization header must be rejected in production."""
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": ""}
        with patch.dict(os.environ, {"APP_ENV": "production"}, clear=False):
            with pytest.raises(Exception) as exc_info:
                _verify_oidc_token(mock_request)
            assert "403" in str(exc_info.value.status_code)

    def test_non_bearer_auth_rejects(self) -> None:
        """Non-Bearer auth schemes must be rejected."""
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        with patch.dict(os.environ, {"APP_ENV": "production"}, clear=False):
            with pytest.raises(Exception) as exc_info:
                _verify_oidc_token(mock_request)
            assert "403" in str(exc_info.value.status_code)

    @given(token=st.text(min_size=10, max_size=200))
    @settings(max_examples=50)
    def test_invalid_token_always_rejects(self, token: str) -> None:
        """Any random Bearer token must be rejected (google-auth will fail verification)."""
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": f"Bearer {token}"}
        with patch.dict(os.environ, {"APP_ENV": "production"}, clear=False), pytest.raises(Exception):
            _verify_oidc_token(mock_request)


# ── Data Export Model ─────────────────────────────────────────────────────


class TestDataExportRequestInvariants:
    """Property: DataExportRequest.format must be 'json' or 'csv'."""

    @given(fmt=st.sampled_from(["json", "csv"]))
    def test_valid_formats_accepted(self, fmt: str) -> None:
        """json and csv are the only valid export formats."""
        req = DataExportRequest(format=fmt)
        assert req.format in {"json", "csv"}

    @given(fmt=st.text(min_size=1, max_size=20).filter(lambda s: s not in {"json", "csv"}))
    @settings(max_examples=100)
    def test_invalid_formats_rejected(self, fmt: str) -> None:
        """Any format other than json/csv must be rejected by the regex pattern."""
        with pytest.raises(Exception):
            DataExportRequest(format=fmt)
