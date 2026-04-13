"""
Authentication Endpoints

Security:
- Rate limiting via middleware
- Password [VAPORIZED_PWD]
- Account locking on failed attempts
- JWT with refresh tokens
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.security import (
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
from app.services.auth_service import AuthService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(db)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> User:
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
    existing_user = await service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    new_user = await service.create_user(user_data.email, user_data.full_name, hashed_password)

    logger.info("user_registered", user_id=new_user.id, email=user_data.email)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Login user and return JWT tokens

    Security:
    - Account locking after 5 failed attempts
    - Failed attempt tracking
    - Timing-safe password [VAPORIZED_PWD]
    - Separate access and refresh tokens
    """
    user = await service.get_user_by_email(credentials.email)

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
        await service.record_failed_login(user)
        logger.warning("login_failed", user_id=user.id, reason="invalid_password")
        raise auth_error

    # Check if user can login
    if not user.can_login():
        logger.warning("login_failed", user_id=user.id, reason="cannot_login")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive or deleted"
        )

    # Reset failed attempts on successful login
    await service.record_successful_login(user)

    # Create tokens
    tokens = service.create_token_pair(user.id)
    logger.info("login_successful", user_id=user.id)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
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

    user = await service.get_user_by_id(int(user_id))

    if user is None or not user.can_login():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or cannot login"
        )

    tokens = service.create_token_pair(user.id)
    logger.info("token_refreshed", user_id=user.id)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
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

    # Update password via service
    await service.update_password(current_user, hash_password(password_data.new_password))
    logger.info("password_changed", user_id=current_user.id)

    return {"message": "Password changed successfully"}
