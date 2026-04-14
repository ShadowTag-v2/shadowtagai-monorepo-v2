"""Dashboard management API routes"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.dashboard import (
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    WidgetCreate,
    WidgetResponse,
)
from src.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.post("/", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new dashboard

    Create a custom analytics dashboard with widgets for visualizing metrics.
    """
    created_dashboard = await DashboardService.create_dashboard(db, dashboard)

    return created_dashboard


@router.get("/default", response_model=DashboardResponse)
async def get_default_dashboard(db: AsyncSession = Depends(get_db)):
    """Get the default dashboard

    Retrieve the dashboard marked as default.
    """
    dashboard = await DashboardService.get_default_dashboard(db)

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default dashboard found",
        )

    return dashboard


@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard by ID

    Retrieve detailed information about a specific dashboard including all widgets.
    """
    dashboard = await DashboardService.get_dashboard(db, dashboard_id)

    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    return dashboard


@router.get("/", response_model=list[DashboardResponse])
async def list_dashboards(
    is_public: bool = None,
    db: AsyncSession = Depends(get_db),
):
    """List all dashboards

    Retrieve all dashboards, optionally filtered by public status.
    """
    dashboards = await DashboardService.list_dashboards(db, is_public=is_public)

    return dashboards


@router.put("/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    dashboard_data: DashboardUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update dashboard

    Update dashboard properties such as name, description, or layout.
    """
    updated_dashboard = await DashboardService.update_dashboard(db, dashboard_id, dashboard_data)

    if not updated_dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    return updated_dashboard


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete dashboard

    Permanently delete a dashboard and all associated widgets.
    """
    deleted = await DashboardService.delete_dashboard(db, dashboard_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )



@router.post(
    "/{dashboard_id}/widgets", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED,
)
async def add_widget(
    dashboard_id: UUID,
    widget: WidgetCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add widget to dashboard

    Create a new widget on the specified dashboard.
    """
    created_widget = await DashboardService.add_widget(db, dashboard_id, widget)

    if not created_widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard not found",
        )

    return created_widget


@router.delete("/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete widget

    Remove a widget from its dashboard.
    """
    deleted = await DashboardService.delete_widget(db, widget_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

