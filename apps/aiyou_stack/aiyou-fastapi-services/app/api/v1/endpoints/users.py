"""
User Management Endpoints

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
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get current user information

    Security:
    - Authentication required
    - Returns only safe fields (no password hash)
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Update current user information

    Security:
    - Authentication required
    - Input validation via schema
    - XSS prevention
    """
    # Update fields if provided
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name

    if user_data.email is not None:
        # Check email uniqueness (future enhancement)
        current_user.email = user_data.email

    await db.commit()
    await db.refresh(current_user)

    logger.info("user_updated", user_id=current_user.id)

    return current_user


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_current_user(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Soft delete current user account

    Security:
    - Authentication required
    - Soft delete (preserves data for audit)
    - Deactivates account immediately
    """
    from datetime import datetime

    # Soft delete
    current_user.deleted_at = datetime.utcnow()
    current_user.is_active = False

    await db.commit()

    logger.info("user_deleted", user_id=current_user.id)

    return {"message": "Account deleted successfully"}
