"""Dashboard management service"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.dashboard import Dashboard, DashboardWidget
from src.schemas.dashboard import DashboardCreate, DashboardUpdate, WidgetCreate


class DashboardService:
    """Service for managing dashboards"""

    @staticmethod
    async def create_dashboard(db: AsyncSession, dashboard_data: DashboardCreate) -> Dashboard:
        """Create a new dashboard with widgets"""
        dashboard = Dashboard(
            name=dashboard_data.name,
            description=dashboard_data.description,
            is_public=dashboard_data.is_public or False,
            layout=dashboard_data.layout or {},
            tags=dashboard_data.tags or [],
        )

        db.add(dashboard)
        await db.flush()

        # Create widgets
        if dashboard_data.widgets:
            for widget_data in dashboard_data.widgets:
                widget = DashboardWidget(
                    dashboard_id=dashboard.id,
                    title=widget_data.title,
                    description=widget_data.description,
                    widget_type=widget_data.widget_type,
                    visualization_type=widget_data.visualization_type,
                    metric_type=widget_data.metric_type,
                    event_filters=widget_data.event_filters or {},
                    time_range=widget_data.time_range,
                    group_by=widget_data.group_by or [],
                    position=widget_data.position or {},
                    chart_config=widget_data.chart_config or {},
                    refresh_interval_seconds=widget_data.refresh_interval_seconds or 300,
                )
                db.add(widget)

        await db.flush()

        # Refresh to load relationships
        await db.refresh(dashboard, ["widgets"])

        return dashboard

    @staticmethod
    async def get_dashboard(db: AsyncSession, dashboard_id: UUID) -> Dashboard | None:
        """Get dashboard by ID"""
        result = await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))
        dashboard = result.scalar_one_or_none()

        if dashboard:
            await db.refresh(dashboard, ["widgets"])

        return dashboard

    @staticmethod
    async def list_dashboards(
        db: AsyncSession,
        is_public: bool | None = None,
        created_by: str | None = None,
    ) -> list[Dashboard]:
        """List dashboards"""
        stmt = select(Dashboard)

        conditions = []

        if is_public is not None:
            conditions.append(Dashboard.is_public == is_public)

        if created_by:
            conditions.append(Dashboard.created_by == created_by)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(Dashboard.created_at.desc())

        result = await db.execute(stmt)
        dashboards = list(result.scalars().all())

        # Load widgets for each dashboard
        for dashboard in dashboards:
            await db.refresh(dashboard, ["widgets"])

        return dashboards

    @staticmethod
    async def update_dashboard(
        db: AsyncSession,
        dashboard_id: UUID,
        dashboard_data: DashboardUpdate,
    ) -> Dashboard | None:
        """Update dashboard"""
        dashboard = await DashboardService.get_dashboard(db, dashboard_id)

        if not dashboard:
            return None

        update_data = dashboard_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dashboard, field, value)

        dashboard.updated_at = datetime.utcnow()
        await db.flush()

        return dashboard

    @staticmethod
    async def delete_dashboard(db: AsyncSession, dashboard_id: UUID) -> bool:
        """Delete dashboard"""
        dashboard = await DashboardService.get_dashboard(db, dashboard_id)

        if not dashboard:
            return False

        await db.delete(dashboard)
        await db.flush()

        return True

    @staticmethod
    async def add_widget(
        db: AsyncSession,
        dashboard_id: UUID,
        widget_data: WidgetCreate,
    ) -> DashboardWidget | None:
        """Add widget to dashboard"""
        dashboard = await DashboardService.get_dashboard(db, dashboard_id)

        if not dashboard:
            return None

        widget = DashboardWidget(
            dashboard_id=dashboard_id,
            title=widget_data.title,
            description=widget_data.description,
            widget_type=widget_data.widget_type,
            visualization_type=widget_data.visualization_type,
            metric_type=widget_data.metric_type,
            event_filters=widget_data.event_filters or {},
            time_range=widget_data.time_range,
            group_by=widget_data.group_by or [],
            position=widget_data.position or {},
            chart_config=widget_data.chart_config or {},
            refresh_interval_seconds=widget_data.refresh_interval_seconds or 300,
        )

        db.add(widget)
        await db.flush()

        return widget

    @staticmethod
    async def delete_widget(db: AsyncSession, widget_id: UUID) -> bool:
        """Delete widget"""
        result = await db.execute(select(DashboardWidget).where(DashboardWidget.id == widget_id))
        widget = result.scalar_one_or_none()

        if not widget:
            return False

        await db.delete(widget)
        await db.flush()

        return True

    @staticmethod
    async def get_default_dashboard(db: AsyncSession) -> Dashboard | None:
        """Get the default dashboard"""
        result = await db.execute(select(Dashboard).where(Dashboard.is_default))
        dashboard = result.scalar_one_or_none()

        if dashboard:
            await db.refresh(dashboard, ["widgets"])

        return dashboard
