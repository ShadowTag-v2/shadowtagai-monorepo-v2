# apps/counselconduit/tests/test_centralized_auth.py
import pytest
from unittest.mock import patch
from fastapi import HTTPException
from apps.counselconduit.api.auth import verify_firebase_token


def test_verify_firebase_token_revoked():
  with patch("firebase_admin.auth.verify_id_token") as mock_verify:
    from firebase_admin import auth

    mock_verify.side_effect = auth.RevokedIdTokenError("Token revoked")

    with pytest.raises(HTTPException) as excinfo:
      verify_firebase_token("revoked_token")

    assert excinfo.value.status_code == 401
    assert "revoked" in excinfo.value.detail.lower()


def test_verify_firebase_token_invalid():
  with patch("firebase_admin.auth.verify_id_token") as mock_verify:
    from firebase_admin import auth

    mock_verify.side_effect = auth.InvalidIdTokenError("Invalid token")

    with pytest.raises(HTTPException) as excinfo:
      verify_firebase_token("invalid_token")

    assert excinfo.value.status_code == 401
    assert "invalid" in excinfo.value.detail.lower()


def test_verify_firebase_token_expired():
  with patch("firebase_admin.auth.verify_id_token") as mock_verify:
    from firebase_admin import auth

    mock_verify.side_effect = auth.ExpiredIdTokenError("Expired token", "expired")

    with pytest.raises(HTTPException) as excinfo:
      verify_firebase_token("expired_token")

    assert excinfo.value.status_code == 401
    assert "expired" in excinfo.value.detail.lower()


def test_verify_firebase_token_success():
  with patch("firebase_admin.auth.verify_id_token") as mock_verify:
    mock_verify.return_value = {"uid": "user123", "email": "test@example.com"}

    claims = verify_firebase_token("valid_token")

    assert claims["uid"] == "user123"
    mock_verify.assert_called_once_with("valid_token", check_revoked=True)
