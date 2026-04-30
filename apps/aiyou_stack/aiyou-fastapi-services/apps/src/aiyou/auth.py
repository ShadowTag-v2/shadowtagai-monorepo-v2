"""Authentication and authorization system.

Implements JWT-based authentication with refresh tokens and role-based access control.
Security: ABSOLUTE GATE - all protected routes must verify authentication.
"""

import uuid
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models.user import User, UserRole, UserSession

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for password and token management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """Create JWT access token.

        Args:
            data: Payload to encode
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token

        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})

        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create refresh token.

        Args:
            user_id: User identifier

        Returns:
            Refresh token string

        """
        token_data = {"sub": user_id, "type": "refresh", "jti": str(uuid.uuid4())}

        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        token_data["exp"] = expire

        encoded_jwt = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired

        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User | None:
        """Authenticate user with email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User object if authentication succeeds, None otherwise

        Security: ABSOLUTE - invalid credentials must return None

        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    def create_session(
        db: Session,
        user_id: str,
        refresh_token: str,
        access_token_jti: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_id: str | None = None,
    ) -> UserSession:
        """Create new user session.

        Args:
            db: Database session
            user_id: User identifier
            refresh_token: Refresh token
            access_token_jti: Access token JTI
            ip_address: Client IP address
            user_agent: Client user agent
            device_id: Device identifier

        Returns:
            Created session object

        """
        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            access_token_jti=access_token_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def revoke_session(db: Session, session_id: str) -> bool:
        """Revoke user session.

        Args:
            db: Database session
            session_id: Session identifier

        Returns:
            True if session was revoked, False if not found

        """
        session = db.query(UserSession).filter(UserSession.id == session_id).first()

        if not session:
            return False

        session.is_revoked = True
        db.commit()

        return True


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Dependency to get current authenticated user.

    Args:
        credentials: HTTP bearer token
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If authentication fails

    Security: ABSOLUTE GATE - must verify token and session validity

    """
    token = credentials.credentials

    # Decode token
    payload = AuthService.decode_token(token)

    user_id: str = payload.get("sub")
    token_jti: str = payload.get("jti")

    if user_id is None or token_jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if session is revoked
    session = (
        db.query(UserSession)
        .filter(UserSession.access_token_jti == token_jti, not UserSession.is_revoked)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last activity
    session.last_activity_at = datetime.utcnow()
    db.commit()

    # Get user
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def require_role(*required_roles: UserRole):
    """Dependency factory to require specific user roles.

    Args:
        required_roles: One or more required roles

    Returns:
        Dependency function that validates user role

    Example:
        @app.get("/admin")
        async def admin_route(user: User = Depends(require_role(UserRole.ADMIN))):
            return {"message": "Admin access granted"}

    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}",
            )
        return current_user

    return Depends(role_checker)
