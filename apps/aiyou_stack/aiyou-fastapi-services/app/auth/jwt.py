"""JWT token creation and validation.
Implements OAuth2 password bearer flow for secure authentication.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings
from app.models.user import TokenData, User

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login", auto_error=False)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: The payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token.

    Args:
        data: The payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string

    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify and decode a JWT token.

    Args:
        token: The JWT token to verify
        token_type: Expected token type (access or refresh)

    Returns:
        TokenData containing the decoded token information

    Raises:
        HTTPException: If token is invalid or expired

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        username: str = payload.get("sub")
        token_type_claim: str = payload.get("type")

        if username is None:
            raise credentials_exception

        if token_type_claim != token_type:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception from None

    return token_data


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> User | None:
    """Get the current authenticated user from JWT token.

    Args:
        token: The JWT token from the request

    Returns:
        User object if authenticated, None otherwise

    Raises:
        HTTPException: If token is invalid

    """
    if token is None:
        return None

    token_data = verify_token(token)

    # In a real application, you would fetch the user from the database
    # For now, we'll create a mock user
    # TODO: Replace with actual database query
    user = User(
        username=token_data.username,
        email=f"{token_data.username}@example.com",
        is_active=True,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current authenticated and active user.

    Args:
        current_user: The current user from JWT token

    Returns:
        User object if authenticated and active

    Raises:
        HTTPException: If user is not authenticated or inactive

    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return current_user
