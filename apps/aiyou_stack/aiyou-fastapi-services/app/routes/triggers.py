"""API routes for trigger management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.triggers import trigger_manager
from app.core.database import get_db
from app.schemas.automation import (
    TriggerCreate,
    TriggerEventRequest,
    TriggerResponse,
    TriggerUpdate,
)
from app.services.automation_service import TriggerService

router = APIRouter(prefix="/triggers", tags=["triggers"])


def get_trigger_service(db: AsyncSession = Depends(get_db)) -> TriggerService:
    """Dependency to get TriggerService instance."""
    return TriggerService(db)


@router.post("/", response_model=TriggerResponse, status_code=201)
async def create_trigger(
    trigger: TriggerCreate,
    service: TriggerService = Depends(get_trigger_service),
):
    """Create a new trigger."""
    db_trigger = await service.create(trigger.model_dump())

    # Register with trigger manager
    if db_trigger.enabled:
        await trigger_manager._register_trigger(db_trigger)

    return db_trigger


@router.get("/", response_model=list[TriggerResponse])
async def list_triggers(
    skip: int = 0,
    limit: int = 100,
    service: TriggerService = Depends(get_trigger_service),
):
    """List all triggers."""
    return await service.list(skip, limit)


@router.get("/{trigger_id}", response_model=TriggerResponse)
async def get_trigger(
    trigger_id: int,
    service: TriggerService = Depends(get_trigger_service),
):
    """Get a specific trigger by ID."""
    trigger = await service.get(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return trigger


@router.put("/{trigger_id}", response_model=TriggerResponse)
async def update_trigger(
    trigger_id: int,
    trigger_update: TriggerUpdate,
    service: TriggerService = Depends(get_trigger_service),
):
    """Update a trigger."""
    trigger = await service.get(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    update_data = trigger_update.model_dump(exclude_unset=True)
    trigger = await service.update(trigger, update_data)

    # Update trigger manager
    await trigger_manager.unregister_trigger(trigger.id)
    if trigger.enabled:
        await trigger_manager._register_trigger(trigger)

    return trigger


@router.delete("/{trigger_id}", status_code=204)
async def delete_trigger(
    trigger_id: int,
    service: TriggerService = Depends(get_trigger_service),
):
    """Delete a trigger."""
    trigger = await service.get(trigger_id)
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Remove from trigger manager
    await trigger_manager.unregister_trigger(trigger.id)

    await service.delete(trigger)


@router.post("/events", status_code=202)
async def trigger_event(event_request: TriggerEventRequest):
    """Trigger an event to execute associated workflows."""
    execution_ids = await trigger_manager.trigger_event(
        event_name=event_request.event_name, event_data=event_request.event_data,
    )

    return {
        "message": f"Event '{event_request.event_name}' triggered",
        "executions_started": len(execution_ids),
        "execution_ids": execution_ids,
    }


@router.post("/webhooks/{webhook_path:path}", status_code=202)
async def trigger_webhook(webhook_path: str, request: Request):
    """Webhook endpoint for triggering workflows."""
    try:
        webhook_data = await request.json()
    except Exception:
        webhook_data = {}

    execution_id = await trigger_manager.trigger_webhook(
        webhook_path=webhook_path, webhook_data=webhook_data,
    )

    if execution_id is None:
        raise HTTPException(
            status_code=404, detail=f"No webhook trigger found for path: {webhook_path}",
        )

    return {"message": "Webhook triggered", "execution_id": execution_id}
