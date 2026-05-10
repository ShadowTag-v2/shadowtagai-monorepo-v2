"""
Authentication Tests

Tests for JWT authentication, password hashing, and session management
"""

from datetime import datetime, timedelta

import pytest
from jose import jwt

from src.ShadowTag-v2.auth import AuthService
from src.ShadowTag-v2.models.user import User, UserRole


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test password hashing produces different hashes for same password"""
        password = "testpassword123"

        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)

        # Hashes should be different (due to random salt)
        assert hash1 != hash2

        # But both should verify
        assert AuthService.verify_password(password, hash1)
        assert AuthService.verify_password(password, hash2)

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "correctpassword"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "correctpassword"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password("wrongpassword", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing empty password"""
        hashed = AuthService.hash_password("")
        assert hashed is not None
        assert len(hashed) > 0


class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_access_token(self, test_settings):
        """Test access token creation"""
        data = {"sub": "user123"}
        token = AuthService.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode and verify
        payload = jwt.decode(
            token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )
        assert payload["sub"] == "user123"
        assert "exp" in payload
        assert "jti" in payload

    def test_create_access_token_with_expiry(self, test_settings):
        """Test access token with custom expiry"""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=15)

        token = AuthService.create_access_token(data, expires_delta)

        payload = jwt.decode(
            token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )

        # Check expiry is approximately 15 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta

        # Allow 5 second tolerance
        assert abs((exp_time - expected_exp).total_seconds()) < 5

    def test_create_refresh_token(self, test_settings):
        """Test refresh token creation"""
        user_id = "user123"
        token = AuthService.create_refresh_token(user_id)

        assert token is not None

        payload = jwt.decode(
            token,
            test_settings.secret_key,
            algorithms=[test_settings.algorithm]
        )

        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
        assert "jti" in payload
        assert "exp" in payload

    def test_decode_valid_token(self, test_settings):
        """Test decoding valid token"""
        data = {"sub": "user123", "role": "user"}
        token = AuthService.create_access_token(data)

        payload = AuthService.decode_token(token)

        assert payload["sub"] == "user123"
        assert payload["role"] == "user"

    def test_decode_invalid_token(self):
        """Test decoding invalid token raises exception"""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            AuthService.decode_token("invalid.token.here")

        assert exc_info.value.status_code == 401

    def test_decode_expired_token(self, test_settings):
        """Test decoding expired token raises exception"""
        from fastapi import HTTPException

        # Create token that expired 1 hour ago
        data = {"sub": "user123"}
        expires_delta = timedelta(hours=-1)
        token = AuthService.create_access_token(data, expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            AuthService.decode_token(token)

        assert exc_info.value.status_code == 401


class TestUserAuthentication:
    """Test user authentication"""

    def test_authenticate_user_success(self, test_db_session, test_user):
        """Test successful user authentication"""
        user = AuthService.authenticate_user(
            test_db_session,
            "test@example.com",
            "testpassword123"
        )

        assert user is not None
        assert user.email == "test@example.com"

    def test_authenticate_user_wrong_password(self, test_db_session, test_user):
        """Test authentication with wrong password"""
        user = AuthService.authenticate_user(
            test_db_session,
            "test@example.com",
            "wrongpassword"
        )

        assert user is None

    def test_authenticate_user_nonexistent_email(self, test_db_session):
        """Test authentication with non-existent email"""
        user = AuthService.authenticate_user(
            test_db_session,
            "nonexistent@example.com",
            "anypassword"
        )

        assert user is None

    def test_authenticate_inactive_user(self, test_db_session):
        """Test authentication of inactive user fails"""
        # Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=AuthService.hash_password("password123"),
            role=UserRole.USER,
            is_active=False
        )
        test_db_session.add(inactive_user)
        test_db_session.commit()

        user = AuthService.authenticate_user(
            test_db_session,
            "inactive@example.com",
            "password123"
        )

        assert user is None


class TestSessionManagement:
    """Test user session management"""

    def test_create_session(self, test_db_session, test_user):
        """Test creating user session"""
        refresh_token = "test_refresh_token"
        access_token_jti = "test_jti"

        session = AuthService.create_session(
            test_db_session,
            test_user.id,
            refresh_token,
            access_token_jti,
            ip_address="127.0.0.1",
            user_agent="TestClient/1.0"
        )

        assert session is not None
        assert session.user_id == test_user.id
        assert session.refresh_token == refresh_token
        assert session.access_token_jti == access_token_jti
        assert session.ip_address == "127.0.0.1"
        assert session.is_revoked is False

    def test_revoke_session(self, test_db_session, test_user):
        """Test revoking session"""
        # Create session
        session = AuthService.create_session(
            test_db_session,
            test_user.id,
            "refresh_token",
            "jti_123"
        )

        # Revoke session
        result = AuthService.revoke_session(test_db_session, session.id)

        assert result is True

        # Verify session is revoked
        test_db_session.refresh(session)
        assert session.is_revoked is True

    def test_revoke_nonexistent_session(self, test_db_session):
        """Test revoking non-existent session"""
        result = AuthService.revoke_session(
            test_db_session,
            "nonexistent-session-id"
        )

        assert result is False


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Test get_current_user dependency"""

    async def test_get_current_user_valid_token(
        self,
        test_db_session,
        test_user,
        user_access_token
    ):
        """Test getting current user with valid token"""
        from fastapi.security import HTTPAuthorizationCredentials

        from src.ShadowTag-v2.auth import get_current_user

        # Create session
        payload = AuthService.decode_token(user_access_token)
        AuthService.create_session(
            test_db_session,
            test_user.id,
            "refresh_token",
            payload["jti"]
        )

        # Mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=user_access_token
        )

        user = await get_current_user(credentials, test_db_session)

        assert user is not None
        assert user.id == test_user.id

    async def test_get_current_user_revoked_session(
        self,
        test_db_session,
        test_user,
        user_access_token
    ):
        """Test getting current user with revoked session"""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        from src.ShadowTag-v2.auth import get_current_user

        # Create and revoke session
        payload = AuthService.decode_token(user_access_token)
        session = AuthService.create_session(
            test_db_session,
            test_user.id,
            "refresh_token",
            payload["jti"]
        )
        AuthService.revoke_session(test_db_session, session.id)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=user_access_token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, test_db_session)

        assert exc_info.value.status_code == 401

    async def test_get_current_user_inactive_user(
        self,
        test_db_session,
        user_access_token
    ):
        """Test getting inactive user"""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        from src.ShadowTag-v2.auth import get_current_user

        # Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=AuthService.hash_password("password"),
            role=UserRole.USER,
            is_active=False
        )
        test_db_session.add(inactive_user)
        test_db_session.commit()

        # Create token and session for inactive user
        token = AuthService.create_access_token({"sub": inactive_user.id})
        payload = AuthService.decode_token(token)
        AuthService.create_session(
            test_db_session,
            inactive_user.id,
            "refresh",
            payload["jti"]
        )

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, test_db_session)

        assert exc_info.value.status_code == 403
