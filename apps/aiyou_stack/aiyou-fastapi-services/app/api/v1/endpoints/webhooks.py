"""Webhook endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.webhook import WebhookStatus
from app.schemas.webhook import (
    WebhookCreate,
    WebhookDeliveryResponse,
    WebhookEventCreate,
    WebhookEventResponse,
    WebhookResponse,
    WebhookTestRequest,
    WebhookTestResponse,
    WebhookUpdate,
)
from app.services.webhook_service import WebhookService

router = APIRouter()


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook_data: WebhookCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new webhook"""
    user_id = int(current_user.get("sub"))
    service = WebhookService(db)
    webhook = service.create_webhook(user_id, webhook_data)
    return webhook


@router.get("", response_model=list[WebhookResponse])
def list_webhooks(
    integration_id: int | None = Query(None),
    status_filter: WebhookStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user webhooks"""
    user_id = int(current_user.get("sub"))
    service = WebhookService(db)
    webhooks = service.list_webhooks(
        user_id=user_id, integration_id=integration_id, status=status_filter, skip=skip, limit=limit
    )
    return webhooks


@router.get("/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get webhook by ID"""
    user_id = int(current_user.get("sub"))
    service = WebhookService(db)
    webhook = service.get_webhook(webhook_id, user_id)

    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    return webhook


@router.put("/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    webhook_data: WebhookUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update webhook"""
    user_id = int(current_user.get("sub"))
    service = WebhookService(db)
    webhook = service.update_webhook(webhook_id, user_id, webhook_data)

    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete webhook"""
    user_id = int(current_user.get("sub"))
    service = WebhookService(db)
    success = service.delete_webhook(webhook_id, user_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    return None


@router.post(
    "/{webhook_id}/events", response_model=WebhookEventResponse, status_code=status.HTTP_201_CREATED
)
def trigger_webhook(
    webhook_id: int,
    event_data: WebhookEventCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger a webhook event"""
    user_id = int(current_user.get("sub"))
    service = WebhookService(db)

    # Verify webhook exists and belongs to user
    webhook = service.get_webhook(webhook_id, user_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    event = service.create_event(webhook_id, event_data)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create webhook event"
        )

    return event


@router.get(
    "/{webhook_id}/events/{event_id}/deliveries", response_model=list[WebhookDeliveryResponse]
)
def get_event_deliveries(
    webhook_id: int,
    event_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get delivery attempts for a webhook event"""
    user_id = int(current_user.get("sub"))

    # Verify webhook exists and belongs to user
    service = WebhookService(db)
    webhook = service.get_webhook(webhook_id, user_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    deliveries = service.get_event_deliveries(event_id, user_id)
    return deliveries


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: int,
    test_request: WebhookTestRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Test webhook delivery"""
    user_id = int(current_user.get("sub"))
    service = WebhookService(db)
    result = await service.test_webhook(webhook_id, user_id, test_request.payload)
    return result
