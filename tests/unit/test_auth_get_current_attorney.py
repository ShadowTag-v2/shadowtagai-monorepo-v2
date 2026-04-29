# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for get_current_attorney FastAPI dependency.

Tests the Firebase Auth verification dependency, ensuring:
- Missing auth header raises 403
- Development mode bypass with dev_ prefix tokens
- user_type inheritance from AntGateMiddleware via request.state
- Firebase token verification integration
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_request(user_type: str = "external") -> MagicMock:
    """Create a mock Request with user_type on state."""
    request = MagicMock()
    request.state = MagicMock()
    request.state.user_type = user_type
    return request


# ── Tests: Missing Auth ──────────────────────────────────────────────────


class TestGetCurrentAttorneyMissingAuth:
    """Test get_current_attorney with missing authentication."""

    @pytest.mark.asyncio
    async def test_missing_auth_header_raises_403(self) -> None:
        """Missing X-Kovel-Auth header should raise HTTP 403."""
        from apps.counselconduit.api.auth import get_current_attorney
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_current_attorney(request=_make_request(), x_kovel_auth=None)

        assert exc_info.value.status_code == 403
        assert "Kovel Authentication Missing" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_empty_auth_header_raises_403(self) -> None:
        """Empty X-Kovel-Auth header should also raise HTTP 403."""
        from apps.counselconduit.api.auth import get_current_attorney
        from fastapi import HTTPException

        # FastAPI Header(None) yields None for missing headers, not empty string
        # but let's test the empty string case too since the check is `if not x_kovel_auth`
        with pytest.raises(HTTPException) as exc_info:
            await get_current_attorney(request=_make_request(), x_kovel_auth="")

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
                request=_make_request(),
                x_kovel_auth="dev_test_attorney_uid",
            )

        assert result["uid"] == "dev_test_attorney_uid"
        assert result["email"] == "dev@kovelai.test"
        assert result["name"] == "Development Attorney"
        assert result["user_type"] == "external"

    @pytest.mark.asyncio
    async def test_dev_token_inherits_ant_user_type(self) -> None:
        """Dev mode should still inherit user_type from AntGateMiddleware."""
        from apps.counselconduit.api.auth import get_current_attorney

        with patch.dict(os.environ, {"APP_ENV": "development"}):
            result = await get_current_attorney(
                request=_make_request(user_type="ant"),
                x_kovel_auth="dev_test_attorney",
            )

        assert result["user_type"] == "ant"

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
                request=_make_request(),
                x_kovel_auth="valid_firebase_token",
            )

        assert result["uid"] == "firebase-uid-123"
        mock_verify.assert_called_once_with("valid_firebase_token")


# ── Tests: user_type Inheritance ─────────────────────────────────────────


class TestGetCurrentAttorneyUserTypeInheritance:
    """Test user_type inheritance from AntGateMiddleware."""

    @pytest.mark.asyncio
    async def test_inherits_external_user_type(self) -> None:
        """External user_type should propagate to attorney dict."""
        from apps.counselconduit.api.auth import get_current_attorney

        with (
            patch.dict(os.environ, {"APP_ENV": "development"}),
        ):
            result = await get_current_attorney(
                request=_make_request(user_type="external"),
                x_kovel_auth="dev_attorney",
            )

        assert result["user_type"] == "external"

    @pytest.mark.asyncio
    async def test_inherits_ant_user_type(self) -> None:
        """Ant user_type should propagate to attorney dict."""
        from apps.counselconduit.api.auth import get_current_attorney

        with patch.dict(os.environ, {"APP_ENV": "development"}):
            result = await get_current_attorney(
                request=_make_request(user_type="ant"),
                x_kovel_auth="dev_attorney",
            )

        assert result["user_type"] == "ant"

    @pytest.mark.asyncio
    async def test_no_request_defaults_to_external(self) -> None:
        """When request is None, user_type should default to 'external'."""
        from apps.counselconduit.api.auth import get_current_attorney

        with patch.dict(os.environ, {"APP_ENV": "development"}):
            result = await get_current_attorney(
                request=None,
                x_kovel_auth="dev_attorney",
            )

        assert result["user_type"] == "external"

    @pytest.mark.asyncio
    async def test_missing_state_attribute_defaults_to_external(self) -> None:
        """When request.state has no user_type, should default to 'external'."""
        from apps.counselconduit.api.auth import get_current_attorney

        request = MagicMock()
        request.state = MagicMock(spec=[])  # No user_type attribute

        with patch.dict(os.environ, {"APP_ENV": "development"}):
            result = await get_current_attorney(
                request=request,
                x_kovel_auth="dev_attorney",
            )

        assert result["user_type"] == "external"


# ── Tests: Firebase Token Verification ───────────────────────────────────


class TestGetCurrentAttorneyFirebaseVerification:
    """Test Firebase token verification flow."""

    @pytest.mark.asyncio
    async def test_valid_firebase_token(self) -> None:
        """Valid Firebase token should return decoded claims with user_type."""
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
                request=_make_request(user_type="ant"),
                x_kovel_auth="valid.jwt.token",
            )

        assert result["uid"] == "uid-456"
        assert result["email"] == "partner@biglaw.com"
        assert result["user_type"] == "ant"
        assert result["email_verified"] is True
