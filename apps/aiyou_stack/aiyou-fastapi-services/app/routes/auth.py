"""Authentication endpoints.
Provides login, registration, token refresh, and logout functionality.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_password_hash,
    verify_token,
)
from app.config import settings
from app.models.response import APIResponse
from app.models.user import RefreshToken, Token, User, UserCreate
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginResponse(BaseModel):
    """Login response with user info and tokens."""

    user: User
    token: Token


@router.post(
    "/register",
    response_model=APIResponse[User],
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account with username, email, and password.",
)
async def register(user_data: UserCreate):
    """Register a new user.

    This is a simplified example. In production, you would:
    - Check if username/email already exists
    - Save user to database
    - Send verification email
    - Return user object without password
    """
    # Hash the password
    get_password_hash(user_data.password)

    # Create user object (in production, save to database)
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False,
    )

    return success_response(data=user, message="User registered successfully")


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    summary="User Login",
    description="Authenticate with username and password to receive access tokens.",
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login with username and password.

    Returns:
    - User information
    - Access token (short-lived)
    - Refresh token (long-lived)

    This is a simplified example. In production, you would:
    - Fetch user from database
    - Verify password hash
    - Check if user is active
    - Create and return tokens

    """
    # Mock user authentication
    # In production, fetch user from database
    mock_user = User(
        id=1,
        username=form_data.username,
        email=f"{form_data.username}@example.com",
        full_name="Demo User",
        is_active=True,
        is_superuser=False,
    )

    # In production, verify against stored hash
    # For demo, accept any password
    # if not verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(...)

    # Create tokens
    access_token = create_access_token(data={"sub": mock_user.username})

    refresh_token = create_refresh_token(data={"sub": mock_user.username})

    token_response = Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )

    response_data = LoginResponse(user=mock_user, token=token_response)

    return success_response(data=response_data, message="Login successful")


@router.post(
    "/refresh",
    response_model=APIResponse[Token],
    summary="Refresh Access Token",
    description="Use a refresh token to obtain a new access token.",
)
async def refresh_access_token(refresh_data: RefreshToken):
    """Refresh access token using refresh token.

    This extends the user's session without requiring re-authentication.
    """
    try:
        # Verify refresh token
        token_data = verify_token(refresh_data.refresh_token, token_type="refresh")

        # Create new access token
        new_access_token = create_access_token(data={"sub": token_data.username})

        # Optionally create new refresh token (token rotation)
        new_refresh_token = create_refresh_token(data={"sub": token_data.username})

        token_response = Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

        return success_response(data=token_response, message="Token refreshed successfully")

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from None


@router.get(
    "/me",
    response_model=APIResponse[User],
    summary="Get Current User",
    description="Get information about the currently authenticated user.",
)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current authenticated user information.

    Requires valid JWT access token in Authorization header.
    """
    return success_response(data=current_user, message="User information retrieved successfully")


@router.post(
    "/logout",
    response_model=APIResponse[None],
    summary="Logout",
    description="Logout the current user (client-side token removal).",
)
async def logout(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Logout endpoint.

    In stateless JWT auth, logout is typically handled client-side by removing tokens.
    For additional security, you could:
    - Implement token blacklisting
    - Use short-lived tokens
    - Store tokens in Redis with expiration
    """
    return success_response(message="Logout successful. Please remove tokens from client.")
