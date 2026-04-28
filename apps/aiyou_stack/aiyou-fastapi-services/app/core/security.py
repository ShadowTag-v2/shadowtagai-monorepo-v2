# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Security Primitives: JWT, Password Hashing, Token Management

Security Features:
- Bcrypt password hashing (cost factor 12)
- JWT with expiration and rotation
- Refresh token support
- Timing-safe comparisons
- No plaintext secrets in logs
"""

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# Password hashing context (Bcrypt)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def hash_password(password: str) -> str:
    """Hash password using bcrypt

    Security:
    - Bcrypt with configurable cost factor (default 12)
    - Automatic salt generation
    - Timing-safe hashing

    Args:
        password: [VAPORIZED_PWD] password

    Returns:
        Hashed password string

    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (timing-safe)

    Security:
    - Constant-time comparison
    - Prevents timing attacks

    Args:
        plain_password: [VAPORIZED_PWD] password
        hashed_password: Stored hash from database

    Returns:
        True if password matches, False otherwise

    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT access token

    Security:
    - Short expiration (default 30 min)
    - HS256 algorithm
    - Claims validation

    Args:
        data: Payload to encode (typically {"sub": user_id})
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token

    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT refresh token

    Security:
    - Long expiration (default 7 days)
    - Separate from access token
    - Type claim for validation

    Args:
        data: Payload to encode (typically {"sub": user_id})
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT refresh token

    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> dict[str, Any] | None:
    """Decode and validate JWT token

    Security:
    - Signature verification
    - Expiration check
    - Type validation
    - Algorithm verification

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded payload if valid, None otherwise

    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Validate token type
        if payload.get("type") != token_type:
            return None

        # Validate expiration (jwt.decode already checks, but explicit is better)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            return None

        return payload

    except JWTError:
        return None


def verify_access_token(token: str) -> str | None:
    """Verify access token and extract user ID

    Args:
        token: JWT access token

    Returns:
        User ID (subject) if token is valid, None otherwise

    """
    payload = decode_token(token, token_type="access")
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    return user_id


def verify_refresh_token(token: str) -> str | None:
    """Verify refresh token and extract user ID

    Args:
        token: JWT refresh token

    Returns:
        User ID (subject) if token is valid, None otherwise

    """
    payload = decode_token(token, token_type="refresh")
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    return user_id


def validate_password_strength(password: str) -> tuple[bool, str | None]:
    """Validate password meets security requirements

    Security Rules:
    - Minimum length (configurable, default 12)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)

    """
    min_length = settings.MIN_PASSWORD_LENGTH

    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, f"Password must contain at least one special character: {special_chars}"

    return True, None
