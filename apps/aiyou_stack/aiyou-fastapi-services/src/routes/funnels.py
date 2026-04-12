"""Funnel analysis API routes"""

from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.funnel import FunnelAnalyticsResponse, FunnelCreate, FunnelResponse, FunnelUpdate
from src.services.funnel_service import FunnelService

router = APIRouter(prefix="/funnels", tags=["funnels"])


@router.post("/", response_model=FunnelResponse, status_code=status.HTTP_201_CREATED)
async def create_funnel(
    funnel: FunnelCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new conversion funnel

    Define a multi-step conversion funnel to track user progression through key events.
    """
    created_funnel = await FunnelService.create_funnel(db, funnel)

    return created_funnel


@router.get("/{funnel_id}", response_model=FunnelResponse)
async def get_funnel(
    funnel_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get funnel by ID

    Retrieve detailed information about a specific funnel including all steps.
    """
    funnel = await FunnelService.get_funnel(db, funnel_id)

    if not funnel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funnel not found",
        )

    return funnel


@router.get("/", response_model=list[FunnelResponse])
async def list_funnels(
    is_active: bool = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all funnels

    Retrieve all conversion funnels, optionally filtered by active status.
    """
    funnels = await FunnelService.list_funnels(db, is_active=is_active)

    return funnels


@router.put("/{funnel_id}", response_model=FunnelResponse)
async def update_funnel(
    funnel_id: UUID,
    funnel_data: FunnelUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update funnel

    Update funnel properties such as name, description, or active status.
    """
    updated_funnel = await FunnelService.update_funnel(db, funnel_id, funnel_data)

    if not updated_funnel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funnel not found",
        )

    return updated_funnel


@router.delete("/{funnel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_funnel(
    funnel_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete funnel

    Permanently delete a funnel and all associated data.
    """
    deleted = await FunnelService.delete_funnel(db, funnel_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funnel not found",
        )

    return None


@router.get("/{funnel_id}/analytics", response_model=FunnelAnalyticsResponse)
async def analyze_funnel(
    funnel_id: UUID,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze funnel performance

    Get detailed analytics for a funnel including conversion rates, drop-off rates,
    and step-by-step breakdown.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    analytics = await FunnelService.analyze_funnel(db, funnel_id, start_date, end_date)

    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funnel not found",
        )

    return analytics
