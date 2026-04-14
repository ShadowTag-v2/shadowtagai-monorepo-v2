"""Notification endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 20,
    unread_only: bool = False,
):
    """List notifications for current user."""
    result = NotificationService.list_notifications(db, current_user.id, page, size, unread_only)

    return NotificationListResponse(
        items=result["items"],
        total=result["total"],
        unread_count=result["unread_count"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"],
    )


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    notification = NotificationService.get_notification(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    return NotificationService.mark_read(db, notification)


@router.put("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db),
):
    """Mark all notifications as read."""
    NotificationService.mark_all_read(db, current_user.id)
    return {"message": "All notifications marked as read"}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a notification."""
    notification = NotificationService.get_notification(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    NotificationService.delete_notification(db, notification)


@router.get("/preferences", response_model=NotificationPreferenceResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db),
):
    """Get notification preferences for current user."""
    return NotificationService.get_preferences(db, current_user.id)


@router.put("/preferences", response_model=NotificationPreferenceResponse)
async def update_notification_preferences(
    prefs_data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update notification preferences."""
    return NotificationService.update_preferences(db, current_user.id, prefs_data)
