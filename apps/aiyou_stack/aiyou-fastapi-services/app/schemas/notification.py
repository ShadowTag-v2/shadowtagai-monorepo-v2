"""Notification schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """Notification response schema."""

    id: int
    user_id: int
    notification_type: str
    title: str
    message: str | None = None
    related_user_id: int | None = None
    related_post_id: int | None = None
    related_comment_id: int | None = None
    related_topic_id: int | None = None
    action_url: str | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Notification list with pagination."""

    items: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    size: int
    pages: int


class NotificationPreferenceUpdate(BaseModel):
    """Notification preference update schema."""

    email_new_follower: bool | None = None
    email_new_comment: bool | None = None
    email_new_reply: bool | None = None
    email_post_liked: bool | None = None
    email_mention: bool | None = None
    email_digest: bool | None = None
    app_new_follower: bool | None = None
    app_new_comment: bool | None = None
    app_new_reply: bool | None = None
    app_post_liked: bool | None = None
    app_mention: bool | None = None


class NotificationPreferenceResponse(BaseModel):
    """Notification preference response schema."""

    id: int
    user_id: int
    email_new_follower: bool
    email_new_comment: bool
    email_new_reply: bool
    email_post_liked: bool
    email_mention: bool
    email_digest: bool
    app_new_follower: bool
    app_new_comment: bool
    app_new_reply: bool
    app_post_liked: bool
    app_mention: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
