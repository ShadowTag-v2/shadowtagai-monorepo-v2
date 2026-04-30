# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for get_current_attorney FastAPI dependency.

Tests the Firebase Auth verification dependency, ensuring:
- Missing auth header raises 403
- Empty auth header raises 403
- Development mode bypass with dev_ prefix tokens
- Non-dev tokens in dev mode still verify via Firebase
- Firebase token verification integration in production
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)


# ── Tests: Missing Auth ──────────────────────────────────────────────────


class TestGetCurrentAttorneyMissingAuth:
    """Test get_current_attorney with missing authentication."""

    @pytest.mark.asyncio
    async def test_missing_auth_header_raises_403(self) -> None:
        """Missing X-Kovel-Auth header should raise HTTP 403."""
        from apps.counselconduit.api.auth import get_current_attorney
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_current_attorney(x_kovel_auth=None)

        assert exc_info.value.status_code == 403
        assert "Kovel Authentication Missing" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_empty_auth_header_raises_403(self) -> None:
        """Empty X-Kovel-Auth header should also raise HTTP 403."""
        from apps.counselconduit.api.auth import get_current_attorney
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_current_attorney(x_kovel_auth="")

        assert exc_info.value.status_code == 403


# ── Tests: Development Mode Bypass ───────────────────────────────────────


class TestGetCurrentAttorneyDevMode:
    """Test get_current_attorney in development mode."""

    @pytest.mark.asyncio
    async def test_dev_token_bypass(self) -> None:
        """dev_ prefixed tokens should bypass Firebase verification in dev mode."""
        from apps.counselconduit.api.auth import get_current_attorney

        with patch.dict(os.environ, {"APP_ENV": "development"}):
            result = await get_current_attorney(
                x_kovel_auth="dev_test_attorney_uid",
            )

        assert result["uid"] == "dev_test_attorney_uid"
        assert result["email"] == "dev@kovelai.test"
        assert result["name"] == "Development Attorney"

    @pytest.mark.asyncio
    async def test_dev_token_returns_expected_keys(self) -> None:
        """Dev mode bypass should return uid, email, and name keys."""
        from apps.counselconduit.api.auth import get_current_attorney

        with patch.dict(os.environ, {"APP_ENV": "development"}):
            result = await get_current_attorney(
                x_kovel_auth="dev_another_attorney",
            )

        assert "uid" in result
        assert "email" in result
        assert "name" in result

    @pytest.mark.asyncio
    async def test_dev_token_without_prefix_verifies_firebase(self) -> None:
        """Non-dev_ tokens in dev mode should still go through Firebase verification."""
        from apps.counselconduit.api.auth import get_current_attorney

        with (
            patch.dict(os.environ, {"APP_ENV": "development"}),
            patch("apps.counselconduit.api.auth.verify_firebase_token") as mock_verify,
        ):
            mock_verify.return_value = {
                "uid": "firebase-uid-123",
                "email": "attorney@firm.com",
                "name": "Jane Attorney",
                "email_verified": True,
            }

            result = await get_current_attorney(
                x_kovel_auth="valid_firebase_token",
            )

        assert result["uid"] == "firebase-uid-123"
        mock_verify.assert_called_once_with("valid_firebase_token")


# ── Tests: Firebase Token Verification ───────────────────────────────────


class TestGetCurrentAttorneyFirebaseVerification:
    """Test Firebase token verification flow."""

    @pytest.mark.asyncio
    async def test_valid_firebase_token(self) -> None:
        """Valid Firebase token should return decoded claims."""
        from apps.counselconduit.api.auth import get_current_attorney

        with (
            patch.dict(os.environ, {"APP_ENV": "production"}, clear=False),
            patch("apps.counselconduit.api.auth.verify_firebase_token") as mock_verify,
        ):
            mock_verify.return_value = {
                "uid": "uid-456",
                "email": "partner@biglaw.com",
                "name": "Senior Partner",
                "email_verified": True,
            }

            result = await get_current_attorney(
                x_kovel_auth="valid.jwt.token",
            )

        assert result["uid"] == "uid-456"
        assert result["email"] == "partner@biglaw.com"
        assert result["email_verified"] is True

    @pytest.mark.asyncio
    async def test_firebase_token_missing_optional_fields(self) -> None:
        """Token with missing optional fields should use defaults."""
        from apps.counselconduit.api.auth import get_current_attorney

        with (
            patch.dict(os.environ, {"APP_ENV": "production"}, clear=False),
            patch("apps.counselconduit.api.auth.verify_firebase_token") as mock_verify,
        ):
            mock_verify.return_value = {
                "uid": "uid-789",
            }

            result = await get_current_attorney(
                x_kovel_auth="sparse.jwt.token",
            )

        assert result["uid"] == "uid-789"
        assert result["email"] == ""
        assert result["name"] == ""
        assert result["email_verified"] is False

    @pytest.mark.asyncio
    async def test_production_rejects_dev_prefix(self) -> None:
        """Production mode should NOT bypass dev_ prefixed tokens."""
        from apps.counselconduit.api.auth import get_current_attorney

        with (
            patch.dict(os.environ, {"APP_ENV": "production"}, clear=False),
            patch("apps.counselconduit.api.auth.verify_firebase_token") as mock_verify,
        ):
            mock_verify.return_value = {
                "uid": "dev_fake_uid",
                "email": "attacker@evil.com",
                "name": "Attacker",
                "email_verified": False,
            }

            result = await get_current_attorney(
                x_kovel_auth="dev_fake_uid",
            )

        # In production, dev_ tokens go through Firebase verification
        mock_verify.assert_called_once_with("dev_fake_uid")
        assert result["uid"] == "dev_fake_uid"
