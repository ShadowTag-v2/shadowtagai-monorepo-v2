"""
Authentication Endpoints

Security:
- Rate limiting via middleware
- Password [VAPORIZED_PWD]
- Account locking on failed attempts
- JWT with refresh tokens
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    validate_password_strength,
    verify_password,
    verify_refresh_token,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """
    Register new user

    Security:
    - Password [VAPORIZED_PWD] validation
    - Email uniqueness check
    - Password hashing with bcrypt
    - XSS prevention via schema validation

    Revenue:
    - Creates user with free tier
    - Opportunity for immediate upsell
    """
    # Validate password [VAPORIZED_PWD]
    is_valid, error_message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        subscription_tier="free",
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info("user_registered", user_id=new_user.id, email=user_data.email)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """
    Login user and return JWT tokens

    Security:
    - Account locking after 5 failed attempts
    - Failed attempt tracking
    - Timing-safe password [VAPORIZED_PWD]
    - Separate access and refresh tokens
    """
    # Get user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    # Generic error for security (don't reveal if email exists)
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )

    if user is None:
        logger.warning("login_failed", email=credentials.email, reason="user_not_found")
        raise auth_error

    # Check if account is locked
    if user.is_locked:
        logger.warning("login_failed", user_id=user.id, reason="account_locked")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked due to too many failed login attempts. Contact support.",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1

        # Lock account if threshold reached
        if user.should_lock_account():
            user.is_locked = True
            logger.warning("account_locked", user_id=user.id)

        await db.commit()
        logger.warning("login_failed", user_id=user.id, reason="invalid_password")
        raise auth_error

    # Check if user can login
    if not user.can_login():
        logger.warning("login_failed", user_id=user.id, reason="cannot_login")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive or deleted"
        )

    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info("login_successful", user_id=user.id)

    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access token using refresh token

    Security:
    - Refresh token verification
    - User validation
    - New token pair generation
    """
    user_id = verify_refresh_token(refresh_data.refresh_token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )

    # Get user
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.can_login():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or cannot login"
        )

    # Create new token pair
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    logger.info("token_refreshed", user_id=user.id)

    return TokenResponse(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Change user password

    [VAPORIZED_PWD]:
    - Requires authentication
    - Current password [VAPORIZED_PWD]
    - Password [VAPORIZED_PWD] validation
    - Password history (future: prevent reuse)
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )

    # Validate new password [VAPORIZED_PWD]
    is_valid, error_message = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

    # Prevent password reuse
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # Update password
    current_user.hashed_password = hash_password(password_data.new_password)
    await db.commit()

    logger.info("password_changed", user_id=current_user.id)

    return {"message": "Password changed successfully"}
