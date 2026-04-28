# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Notification service layer.

Extracts all database operations from notification routes
into a proper service/repository pattern.
"""

from datetime import datetime
from math import ceil

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationPreference
from app.schemas.notification import NotificationPreferenceUpdate


class NotificationService:
    """Service layer for notification operations."""

    @staticmethod
    def list_notifications(
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 20,
        unread_only: bool = False,
    ) -> dict:
        """List notifications for a user with pagination."""
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(not Notification.is_read)

        total = query.count()
        unread_count = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, not Notification.is_read)
            .count()
        )

        notifications = (
            query.order_by(desc(Notification.created_at))
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        return {
            "items": notifications,
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "size": size,
            "pages": ceil(total / size) if total > 0 else 0,
        }

    @staticmethod
    def get_notification(db: Session, notification_id: int, user_id: int) -> Notification | None:
        """Get a notification for a specific user."""
        return (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )

    @staticmethod
    def mark_read(db: Session, notification: Notification) -> Notification:
        """Mark a notification as read."""
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> None:
        """Mark all notifications as read for a user."""
        db.query(Notification).filter(
            Notification.user_id == user_id,
            not Notification.is_read,
        ).update({"is_read": True, "read_at": datetime.utcnow()})
        db.commit()

    @staticmethod
    def delete_notification(db: Session, notification: Notification) -> None:
        """Delete a notification."""
        db.delete(notification)
        db.commit()

    @staticmethod
    def get_preferences(db: Session, user_id: int) -> NotificationPreference:
        """Get or create notification preferences for a user."""
        prefs = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)
            db.commit()
            db.refresh(prefs)
        return prefs

    @staticmethod
    def update_preferences(
        db: Session,
        user_id: int,
        prefs_data: NotificationPreferenceUpdate,
    ) -> NotificationPreference:
        """Update notification preferences."""
        prefs = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .first()
        )
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            db.add(prefs)

        for field, value in prefs_data.model_dump(exclude_unset=True).items():
            setattr(prefs, field, value)

        db.commit()
        db.refresh(prefs)
        return prefs
