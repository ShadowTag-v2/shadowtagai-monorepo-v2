"""
API routes for trigger management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.automation.triggers import trigger_manager
from app.core.database import get_db
from app.models.automation import Trigger
from app.schemas.automation import (
    TriggerCreate,
    TriggerEventRequest,
    TriggerResponse,
    TriggerUpdate,
)

router = APIRouter(prefix="/triggers", tags=["triggers"])


@router.post("/", response_model=TriggerResponse, status_code=201)
async def create_trigger(trigger: TriggerCreate, db: AsyncSession = Depends(get_db)):
    """Create a new trigger."""
    db_trigger = Trigger(**trigger.model_dump())
    db.add(db_trigger)
    await db.commit()
    await db.refresh(db_trigger)

    # Register with trigger manager
    if db_trigger.enabled:
        await trigger_manager._register_trigger(db_trigger)

    return db_trigger


@router.get("/", response_model=list[TriggerResponse])
async def list_triggers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all triggers."""
    result = await db.execute(select(Trigger).offset(skip).limit(limit))
    triggers = result.scalars().all()
    return triggers


@router.get("/{trigger_id}", response_model=TriggerResponse)
async def get_trigger(trigger_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific trigger by ID."""
    result = await db.execute(select(Trigger).where(Trigger.id == trigger_id))
    trigger = result.scalar_one_or_none()

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    return trigger


@router.put("/{trigger_id}", response_model=TriggerResponse)
async def update_trigger(
    trigger_id: int, trigger_update: TriggerUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a trigger."""
    result = await db.execute(select(Trigger).where(Trigger.id == trigger_id))
    trigger = result.scalar_one_or_none()

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Update fields
    update_data = trigger_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trigger, field, value)

    await db.commit()
    await db.refresh(trigger)

    # Update trigger manager
    await trigger_manager.unregister_trigger(trigger.id)
    if trigger.enabled:
        await trigger_manager._register_trigger(trigger)

    return trigger


@router.delete("/{trigger_id}", status_code=204)
async def delete_trigger(trigger_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a trigger."""
    result = await db.execute(select(Trigger).where(Trigger.id == trigger_id))
    trigger = result.scalar_one_or_none()

    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")

    # Remove from trigger manager
    await trigger_manager.unregister_trigger(trigger.id)

    await db.delete(trigger)
    await db.commit()
    return None


@router.post("/events", status_code=202)
async def trigger_event(event_request: TriggerEventRequest, db: AsyncSession = Depends(get_db)):
    """Trigger an event to execute associated workflows."""
    execution_ids = await trigger_manager.trigger_event(
        event_name=event_request.event_name, event_data=event_request.event_data
    )

    return {
        "message": f"Event '{event_request.event_name}' triggered",
        "executions_started": len(execution_ids),
        "execution_ids": execution_ids,
    }


@router.post("/webhooks/{webhook_path:path}", status_code=202)
async def trigger_webhook(webhook_path: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Webhook endpoint for triggering workflows."""
    # Get request body as JSON
    try:
        webhook_data = await request.json()
    except Exception:
        webhook_data = {}

    execution_id = await trigger_manager.trigger_webhook(
        webhook_path=webhook_path, webhook_data=webhook_data
    )

    if execution_id is None:
        raise HTTPException(
            status_code=404, detail=f"No webhook trigger found for path: {webhook_path}"
        )

    return {"message": "Webhook triggered", "execution_id": execution_id}
