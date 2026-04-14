"""User Management Endpoints

Security:
- Authentication required
- User can only access own data
- Admin checks for sensitive operations
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get UserService instance."""
    return UserService(db)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current user information

    Security:
    - Authentication required
    - Returns only safe fields (no password hash)
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> User:
    """Update current user information

    Security:
    - Authentication required
    - Input validation via schema
    - XSS prevention
    """
    return await service.update_user(current_user, user_data.full_name, user_data.email)


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> dict:
    """Soft delete current user account

    Security:
    - Authentication required
    - Soft delete (preserves data for audit)
    - Deactivates account immediately
    """
    await service.soft_delete_user(current_user)
    return {"message": "Account deleted successfully"}
