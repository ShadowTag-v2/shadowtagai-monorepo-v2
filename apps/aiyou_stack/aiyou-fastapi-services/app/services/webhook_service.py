"""Webhook service with event handling and retry logic"""

import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.models.webhook import (
    Webhook,
    WebhookDelivery,
    WebhookEvent,
    WebhookEventStatus,
    WebhookStatus,
)
from app.schemas.webhook import WebhookCreate, WebhookEventCreate, WebhookUpdate

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing webhooks"""

    def __init__(self, db: Session):
        self.db = db

    def create_webhook(self, user_id: int, data: WebhookCreate) -> Webhook:
        """Create a new webhook"""
        webhook = Webhook(
            user_id=user_id,
            integration_id=data.integration_id,
            name=data.name,
            url=data.url,
            secret=data.secret,
            events=data.events,
            headers=data.headers,
            max_retries=data.max_retries,
            retry_delay=data.retry_delay,
            timeout=data.timeout,
            status=WebhookStatus.ACTIVE,
        )

        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)

        logger.info(f"Created webhook {webhook.id} for user {user_id}")
        return webhook

    def get_webhook(self, webhook_id: int, user_id: int) -> Webhook | None:
        """Get webhook by ID"""
        return (
            self.db.query(Webhook)
            .filter(Webhook.id == webhook_id, Webhook.user_id == user_id)
            .first()
        )

    def list_webhooks(
        self,
        user_id: int,
        integration_id: int | None = None,
        status: WebhookStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Webhook]:
        """List user webhooks"""
        query = self.db.query(Webhook).filter(Webhook.user_id == user_id)

        if integration_id:
            query = query.filter(Webhook.integration_id == integration_id)
        if status:
            query = query.filter(Webhook.status == status)

        return query.offset(skip).limit(limit).all()

    def update_webhook(self, webhook_id: int, user_id: int, data: WebhookUpdate) -> Webhook | None:
        """Update webhook"""
        webhook = self.get_webhook(webhook_id, user_id)
        if not webhook:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(webhook, field, value)

        webhook.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(webhook)

        logger.info(f"Updated webhook {webhook_id}")
        return webhook

    def delete_webhook(self, webhook_id: int, user_id: int) -> bool:
        """Delete webhook"""
        webhook = self.get_webhook(webhook_id, user_id)
        if not webhook:
            return False

        self.db.delete(webhook)
        self.db.commit()

        logger.info(f"Deleted webhook {webhook_id}")
        return True

    def create_event(self, webhook_id: int, event_data: WebhookEventCreate) -> WebhookEvent | None:
        """Create a webhook event"""
        webhook = self.db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook or webhook.status != WebhookStatus.ACTIVE:
            return None

        # Check if event type is subscribed
        if webhook.events and event_data.event_type not in webhook.events:
            logger.info(
                f"Event type {event_data.event_type} not subscribed for webhook {webhook_id}",
            )
            return None

        event = WebhookEvent(
            webhook_id=webhook_id,
            event_type=event_data.event_type,
            payload=event_data.payload,
            status=WebhookEventStatus.PENDING,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        logger.info(f"Created event {event.id} for webhook {webhook_id}")
        return event

    def get_pending_events(self, limit: int = 100) -> list[WebhookEvent]:
        """Get pending webhook events ready for processing"""
        now = datetime.utcnow()

        return (
            self.db.query(WebhookEvent)
            .filter(
                WebhookEvent.status.in_([WebhookEventStatus.PENDING, WebhookEventStatus.RETRYING]),
                (WebhookEvent.next_retry_at.is_(None)) | (WebhookEvent.next_retry_at <= now),
            )
            .limit(limit)
            .all()
        )

    def _generate_signature(self, payload: bytes, secret: str) -> str:
        """Generate HMAC signature for webhook payload"""
        return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    async def deliver_event(self, event: WebhookEvent) -> WebhookDelivery:
        """Deliver a webhook event"""
        webhook = event.webhook

        # Update event status
        event.status = WebhookEventStatus.PROCESSING
        self.db.commit()

        # Prepare request
        import json

        request_body = event.payload
        request_body_str = json.dumps(request_body)
        request_headers = webhook.headers.copy() if webhook.headers else {}
        request_headers["Content-Type"] = "application/json"
        request_headers["X-Webhook-Event"] = event.event_type
        request_headers["X-Webhook-ID"] = str(event.id)

        # Add signature if secret is configured
        if webhook.secret:
            signature = self._generate_signature(request_body_str.encode(), webhook.secret)
            request_headers["X-Webhook-Signature"] = f"sha256={signature}"

        start_time = datetime.utcnow()
        delivery = WebhookDelivery(
            event_id=event.id, request_headers=request_headers, request_body=request_body,
        )

        try:
            async with httpx.AsyncClient(timeout=webhook.timeout) as client:
                response = await client.post(
                    webhook.url, content=request_body_str, headers=request_headers,
                )

                duration = (datetime.utcnow() - start_time).total_seconds() * 1000

                delivery.response_status = response.status_code
                delivery.response_headers = dict(response.headers)
                delivery.response_body = response.text
                delivery.duration_ms = int(duration)
                delivery.success = 200 <= response.status_code < 300

                if delivery.success:
                    event.status = WebhookEventStatus.DELIVERED
                    event.processed_at = datetime.utcnow()
                    webhook.total_events += 1
                    webhook.last_triggered_at = datetime.utcnow()
                else:
                    await self._handle_delivery_failure(event, webhook, str(response.status_code))

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            delivery.duration_ms = int(duration)
            delivery.success = False
            delivery.error_message = str(e)

            await self._handle_delivery_failure(event, webhook, str(e))

        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)

        logger.info(f"Delivered event {event.id} to webhook {webhook.id}: {delivery.success}")
        return delivery

    async def _handle_delivery_failure(self, event: WebhookEvent, webhook: Webhook, error: str):
        """Handle webhook delivery failure with retry logic"""
        event.retry_count += 1
        event.last_error = error

        if event.retry_count < webhook.max_retries:
            # Calculate next retry time with exponential backoff
            delay = webhook.retry_delay * (2 ** (event.retry_count - 1))
            event.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
            event.status = WebhookEventStatus.RETRYING
            logger.info(
                f"Scheduled retry {event.retry_count} for event {event.id} at {event.next_retry_at}",
            )
        else:
            event.status = WebhookEventStatus.FAILED
            webhook.failed_events += 1
            logger.error(f"Event {event.id} failed after {event.retry_count} attempts")

    async def process_pending_events(self):
        """Process all pending webhook events"""
        events = self.get_pending_events()
        logger.info(f"Processing {len(events)} pending webhook events")

        for event in events:
            try:
                await self.deliver_event(event)
            except Exception as e:
                logger.error(f"Error processing event {event.id}: {e}")

    def get_event_deliveries(self, event_id: int, user_id: int) -> list[WebhookDelivery]:
        """Get delivery attempts for an event"""
        event = (
            self.db.query(WebhookEvent)
            .join(Webhook)
            .filter(WebhookEvent.id == event_id, Webhook.user_id == user_id)
            .first()
        )

        if not event:
            return []

        return (
            self.db.query(WebhookDelivery)
            .filter(WebhookDelivery.event_id == event_id)
            .order_by(WebhookDelivery.created_at.desc())
            .all()
        )

    async def test_webhook(
        self, webhook_id: int, user_id: int, test_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Test webhook delivery"""
        webhook = self.get_webhook(webhook_id, user_id)
        if not webhook:
            return {"success": False, "error": "Webhook not found"}

        # Create test event
        event_data = WebhookEventCreate(event_type="test", payload=test_payload)

        # Temporarily allow test events
        original_events = webhook.events
        if not webhook.events or "test" not in webhook.events:
            webhook.events = (webhook.events or []) + ["test"]
            self.db.commit()

        event = self.create_event(webhook_id, event_data)

        if not event:
            return {"success": False, "error": "Failed to create test event"}

        # Deliver the event
        start_time = datetime.utcnow()

        try:
            delivery = await self.deliver_event(event)
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Restore original events
            webhook.events = original_events
            self.db.commit()

            return {
                "success": delivery.success,
                "status_code": delivery.response_status,
                "response": delivery.response_body,
                "error": delivery.error_message,
                "duration_ms": int(duration),
            }

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Restore original events
            webhook.events = original_events
            self.db.commit()

            return {"success": False, "error": str(e), "duration_ms": int(duration)}
