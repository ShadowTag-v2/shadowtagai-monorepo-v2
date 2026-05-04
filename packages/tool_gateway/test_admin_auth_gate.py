# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for Admin Auth Gate (Risk #58)."""

from __future__ import annotations

from typing import Any

import pytest

from tool_gateway.admin_auth_gate import (
    AdminClaim,
    InsufficientPrivilegesError,
    InvalidTokenError,
    MissingTokenError,
    extract_bearer_token,
    gate_admin_request,
    verify_admin_claim,
)


# ── Mock Verifier ─────────────────────────────────────────────────────────


class MockVerifier:
    """Test verifier that returns preconfigured claims."""

    def __init__(self, claims: dict[str, Any] | None = None, *, raise_exc: Exception | None = None):
        self._claims = claims or {}
        self._raise_exc = raise_exc

    def verify_id_token(self, token: str) -> dict[str, Any]:
        if self._raise_exc:
            raise self._raise_exc
        return self._claims


# ── Token Extraction Tests ────────────────────────────────────────────────


class TestExtractBearerToken:
    def test_valid_bearer_token(self):
        assert extract_bearer_token("Bearer abc123") == "abc123"

    def test_case_insensitive_bearer(self):
        assert extract_bearer_token("bearer xyz789") == "xyz789"

    def test_missing_header_raises(self):
        with pytest.raises(MissingTokenError):
            extract_bearer_token(None)

    def test_empty_header_raises(self):
        with pytest.raises(MissingTokenError):
            extract_bearer_token("")

    def test_malformed_header_raises(self):
        with pytest.raises(MissingTokenError):
            extract_bearer_token("Token abc123")

    def test_no_token_value_raises(self):
        with pytest.raises(MissingTokenError):
            extract_bearer_token("Bearer")


# ── Verification Tests ────────────────────────────────────────────────────


class TestVerifyAdminClaim:
    def test_valid_admin_claim(self):
        verifier = MockVerifier({"uid": "user1", "email": "admin@test.com", "admin": True})
        claim = verify_admin_claim("test-token", verifier=verifier)
        assert claim.uid == "user1"
        assert claim.email == "admin@test.com"
        assert claim.is_admin is True

    def test_admin_in_custom_claims(self):
        verifier = MockVerifier({"uid": "user2", "email": "admin2@test.com", "custom_claims": {"admin": True}})
        claim = verify_admin_claim("test-token", verifier=verifier)
        assert claim.is_admin is True

    def test_missing_admin_claim_raises_403(self):
        verifier = MockVerifier({"uid": "user3", "email": "user@test.com", "admin": False})
        with pytest.raises(InsufficientPrivilegesError):
            verify_admin_claim("test-token", verifier=verifier)

    def test_no_admin_key_raises_403(self):
        verifier = MockVerifier({"uid": "user4", "email": "user@test.com"})
        with pytest.raises(InsufficientPrivilegesError):
            verify_admin_claim("test-token", verifier=verifier)

    def test_verifier_exception_raises_401(self):
        verifier = MockVerifier(raise_exc=ValueError("token expired"))
        with pytest.raises(InvalidTokenError):
            verify_admin_claim("bad-token", verifier=verifier)

    def test_custom_admin_claim_key(self):
        verifier = MockVerifier({"uid": "user5", "email": "super@test.com", "superadmin": True})
        claim = verify_admin_claim("test-token", verifier=verifier, admin_claim_key="superadmin")
        assert claim.is_admin is True

    def test_sub_field_fallback(self):
        """Firebase tokens use 'sub' instead of 'uid' sometimes."""
        verifier = MockVerifier({"sub": "sub-user", "email": "sub@test.com", "admin": True})
        claim = verify_admin_claim("test-token", verifier=verifier)
        assert claim.uid == "sub-user"


# ── Full Pipeline Tests ───────────────────────────────────────────────────


class TestGateAdminRequest:
    def test_full_success_pipeline(self):
        verifier = MockVerifier({"uid": "admin1", "email": "a@t.com", "admin": True})
        claim = gate_admin_request("Bearer valid-token", verifier=verifier)
        assert isinstance(claim, AdminClaim)
        assert claim.is_admin is True

    def test_missing_header_pipeline(self):
        with pytest.raises(MissingTokenError) as exc_info:
            gate_admin_request(None)
        assert exc_info.value.status_code == 401

    def test_invalid_token_pipeline(self):
        verifier = MockVerifier(raise_exc=RuntimeError("expired"))
        with pytest.raises(InvalidTokenError) as exc_info:
            gate_admin_request("Bearer expired-token", verifier=verifier)
        assert exc_info.value.status_code == 401

    def test_insufficient_privileges_pipeline(self):
        verifier = MockVerifier({"uid": "user", "email": "u@t.com"})
        with pytest.raises(InsufficientPrivilegesError) as exc_info:
            gate_admin_request("Bearer valid-but-not-admin", verifier=verifier)
        assert exc_info.value.status_code == 403

    def test_error_hierarchy(self):
        """Verify that all auth errors inherit from AuthError."""
        from tool_gateway.admin_auth_gate import AuthError

        assert issubclass(MissingTokenError, AuthError)
        assert issubclass(InvalidTokenError, AuthError)
        assert issubclass(InsufficientPrivilegesError, AuthError)
