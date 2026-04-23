# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""Cloud Tasks push notification handler for long-running A2A queries.

Receives push notifications from Google Cloud Tasks when:
- Oracle Studio memo generation completes
- Long-running model inference finishes
- Dead-man's switch triggers session expiry

Queue: a2a-notifications (us-central1)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class NotificationType(StrEnum):
    """Types of push notifications from Cloud Tasks."""

    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    SESSION_EXPIRED = "session_expired"
    MEMO_READY = "memo_ready"
    GDPR_DELETE = "gdpr_delete"


@dataclass
class PushNotification:
    """A push notification payload from Cloud Tasks."""

    notification_type: NotificationType
    task_id: str = ""
    session_id: str = ""
    tenant_id: str = ""
    payload: dict[str, Any] | None = None


class CloudTasksHandler:
    """Handles push notifications from Google Cloud Tasks.

    Queue configuration:
    - Queue name: a2a-notifications
    - Region: us-central1
    - Max concurrent dispatches: 100
    - Max retry attempts: 5
    - Min backoff: 10s
    """

    QUEUE_NAME = "a2a-notifications"
    QUEUE_REGION = "us-central1"

    def __init__(
        self,
        session_service: Any = None,
        notification_callback: Any = None,
    ) -> None:
        self._session_service = session_service
        self._callback = notification_callback

    async def handle_push(self, request_body: bytes) -> dict[str, Any]:
        """Handle an incoming Cloud Tasks push notification.

        Args:
            request_body: Raw HTTP request body from Cloud Tasks.

        Returns:
            Response dict with processing result.
        """
        try:
            data = json.loads(request_body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Cloud Tasks push")
            return {"status": "error", "message": "Invalid JSON payload"}

        notification = PushNotification(
            notification_type=NotificationType(data.get("type", "")),
            task_id=data.get("task_id", ""),
            session_id=data.get("session_id", ""),
            tenant_id=data.get("tenant_id", ""),
            payload=data.get("payload"),
        )

        logger.info(
            "Cloud Tasks push received: type=%s task=%s tenant=%s",
            notification.notification_type.value,
            notification.task_id,
            notification.tenant_id,
        )

        handler_map = {
            NotificationType.TASK_COMPLETED: self._handle_task_completed,
            NotificationType.TASK_FAILED: self._handle_task_failed,
            NotificationType.SESSION_EXPIRED: self._handle_session_expired,
            NotificationType.MEMO_READY: self._handle_memo_ready,
            NotificationType.GDPR_DELETE: self._handle_gdpr_delete,
        }

        handler = handler_map.get(notification.notification_type)
        if handler:
            return await handler(notification)

        return {"status": "ignored", "message": "Unknown notification type"}

    async def _handle_task_completed(self, notification: PushNotification) -> dict[str, Any]:
        """Handle task completion notification."""
        logger.info("Task completed: %s", notification.task_id)
        if self._callback:
            await self._callback("task_completed", notification)
        return {"status": "ok", "task_id": notification.task_id}

    async def _handle_task_failed(self, notification: PushNotification) -> dict[str, Any]:
        """Handle task failure notification."""
        logger.warning(
            "Task failed: %s reason=%s",
            notification.task_id,
            notification.payload,
        )
        return {"status": "ok", "task_id": notification.task_id}

    async def _handle_session_expired(self, notification: PushNotification) -> dict[str, Any]:
        """Handle dead-man's switch session expiry."""
        logger.info(
            "Session expired (dead-man's switch): session=%s tenant=%s",
            notification.session_id,
            notification.tenant_id,
        )
        if self._session_service:
            await self._session_service.expire_session(
                notification.tenant_id,
                notification.session_id,
            )
        return {"status": "ok", "session_id": notification.session_id}

    async def _handle_memo_ready(self, notification: PushNotification) -> dict[str, Any]:
        """Handle Oracle memo generation completion."""
        logger.info("Memo ready: task=%s", notification.task_id)
        return {"status": "ok", "task_id": notification.task_id}

    async def _handle_gdpr_delete(self, notification: PushNotification) -> dict[str, Any]:
        """Handle GDPR 30-day deletion request.

        Triggered by Cloud Tasks scheduled 30 days after session creation.
        """
        logger.info(
            "GDPR delete: tenant=%s session=%s",
            notification.tenant_id,
            notification.session_id,
        )
        return {"status": "ok", "session_id": notification.session_id}


class DeadManSwitch:
    """Vent Mode dead-man's switch with 45-minute TTL.

    Schedules a Cloud Tasks push notification to expire the session
    after 45 minutes of inactivity. Each user interaction resets the timer.

    Item 19: Build dead-man's switch for Vent Mode (45min TTL).
    """

    TTL_SECONDS = 45 * 60  # 45 minutes

    def __init__(self, project_id: str = "shadowtag-omega-v4") -> None:
        self._project_id = project_id
        self._active_timers: dict[str, str] = {}  # session_id -> task_name

    async def arm(self, tenant_id: str, session_id: str) -> str:
        """Arm the dead-man's switch for a Vent Mode session.

        Creates a Cloud Tasks task scheduled to fire after TTL_SECONDS.

        Args:
            tenant_id: The law firm tenant ID.
            session_id: The Vent Mode session ID.

        Returns:
            The Cloud Tasks task name.
        """
        try:
            import time as _time

            from google.cloud import tasks_v2
            from google.protobuf import timestamp_pb2

            client = tasks_v2.CloudTasksClient()
            parent = client.queue_path(
                self._project_id,
                CloudTasksHandler.QUEUE_REGION,
                CloudTasksHandler.QUEUE_NAME,
            )

            schedule_time = timestamp_pb2.Timestamp()
            schedule_time.seconds = int(_time.time()) + self.TTL_SECONDS

            task = tasks_v2.Task(
                http_request=tasks_v2.HttpRequest(
                    http_method=tasks_v2.HttpMethod.POST,
                    url=("https://counselconduit-767252945109.us-central1.run.app/api/v1/notifications/push"),
                    headers={"Content-Type": "application/json"},
                    body=json.dumps(
                        {
                            "type": "session_expired",
                            "tenant_id": tenant_id,
                            "session_id": session_id,
                        }
                    ).encode(),
                ),
                schedule_time=schedule_time,
            )

            response = client.create_task(
                parent=parent,
                task=task,
            )
            task_name = response.name
            self._active_timers[session_id] = task_name

            logger.info(
                "Dead-man's switch armed: session=%s ttl=%ds task=%s",
                session_id,
                self.TTL_SECONDS,
                task_name,
            )
            return task_name

        except ImportError:
            logger.warning("google-cloud-tasks not installed. Dead-man's switch disabled.")
            return ""

    async def reset(self, tenant_id: str, session_id: str) -> str:
        """Reset the dead-man's switch (user activity detected).

        Cancels the existing task and creates a new one.

        Args:
            tenant_id: The law firm tenant ID.
            session_id: The Vent Mode session ID.

        Returns:
            The new Cloud Tasks task name.
        """
        await self.disarm(session_id)
        return await self.arm(tenant_id, session_id)

    async def disarm(self, session_id: str) -> None:
        """Disarm the dead-man's switch (session ended normally).

        Args:
            session_id: The Vent Mode session ID.
        """
        task_name = self._active_timers.pop(session_id, None)
        if task_name:
            try:
                from google.cloud import tasks_v2

                client = tasks_v2.CloudTasksClient()
                client.delete_task(name=task_name)
                logger.info("Dead-man's switch disarmed: session=%s", session_id)
            except Exception as e:
                logger.warning("Failed to disarm dead-man's switch: %s", e)
