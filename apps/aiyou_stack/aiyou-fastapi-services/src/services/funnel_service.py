"""Funnel analysis service"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event
from src.models.funnel import Funnel, FunnelStep, UserFunnelProgress
from src.schemas.funnel import (
    FunnelAnalyticsResponse,
    FunnelCreate,
    FunnelStepAnalytics,
    FunnelUpdate,
)


class FunnelService:
    """Service for managing conversion funnels"""

    @staticmethod
    async def create_funnel(db: AsyncSession, funnel_data: FunnelCreate) -> Funnel:
        """Create a new funnel with steps"""
        funnel = Funnel(
            name=funnel_data.name,
            description=funnel_data.description,
            time_window_hours=funnel_data.time_window_hours,
            tags=funnel_data.tags or [],
        )

        db.add(funnel)
        await db.flush()

        # Create funnel steps
        for step_data in funnel_data.steps:
            step = FunnelStep(
                funnel_id=funnel.id,
                step_order=step_data.step_order,
                event_name=step_data.event_name,
                event_filters=step_data.event_filters or {},
                name=step_data.name,
                description=step_data.description,
            )
            db.add(step)

        await db.flush()

        # Refresh to load relationships
        await db.refresh(funnel, ["steps"])

        return funnel

    @staticmethod
    async def get_funnel(db: AsyncSession, funnel_id: UUID) -> Funnel | None:
        """Get funnel by ID"""
        result = await db.execute(select(Funnel).where(Funnel.id == funnel_id))
        funnel = result.scalar_one_or_none()

        if funnel:
            await db.refresh(funnel, ["steps"])

        return funnel

    @staticmethod
    async def list_funnels(db: AsyncSession, is_active: bool | None = None) -> list[Funnel]:
        """List all funnels"""
        stmt = select(Funnel)

        if is_active is not None:
            stmt = stmt.where(Funnel.is_active == is_active)

        stmt = stmt.order_by(Funnel.created_at.desc())

        result = await db.execute(stmt)
        funnels = list(result.scalars().all())

        # Load steps for each funnel
        for funnel in funnels:
            await db.refresh(funnel, ["steps"])

        return funnels

    @staticmethod
    async def update_funnel(
        db: AsyncSession, funnel_id: UUID, funnel_data: FunnelUpdate
    ) -> Funnel | None:
        """Update funnel"""
        funnel = await FunnelService.get_funnel(db, funnel_id)

        if not funnel:
            return None

        update_data = funnel_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(funnel, field, value)

        funnel.updated_at = datetime.utcnow()
        await db.flush()

        return funnel

    @staticmethod
    async def delete_funnel(db: AsyncSession, funnel_id: UUID) -> bool:
        """Delete funnel"""
        funnel = await FunnelService.get_funnel(db, funnel_id)

        if not funnel:
            return False

        await db.delete(funnel)
        await db.flush()

        return True

    @staticmethod
    async def analyze_funnel(
        db: AsyncSession,
        funnel_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> FunnelAnalyticsResponse | None:
        """Analyze funnel performance"""
        funnel = await FunnelService.get_funnel(db, funnel_id)

        if not funnel:
            return None

        # Sort steps by order
        steps = sorted(funnel.steps, key=lambda s: s.step_order)

        if not steps:
            return None

        # Get users who entered the funnel (completed first step)
        first_step = steps[0]
        users_entered_result = await db.execute(
            select(func.count(func.distinct(Event.user_id))).where(
                and_(
                    Event.event_name == first_step.event_name,
                    Event.timestamp >= start_date,
                    Event.timestamp <= end_date,
                    Event.user_id.isnot(None),
                )
            )
        )
        total_users_entered = users_entered_result.scalar() or 0

        # Analyze each step
        step_analytics = []
        previous_users = total_users_entered

        for _i, step in enumerate(steps):
            # Get users who completed this step
            users_completed_result = await db.execute(
                select(func.count(func.distinct(Event.user_id))).where(
                    and_(
                        Event.event_name == step.event_name,
                        Event.timestamp >= start_date,
                        Event.timestamp <= end_date,
                        Event.user_id.isnot(None),
                    )
                )
            )
            users_completed = users_completed_result.scalar() or 0

            # Calculate conversion and drop-off rates
            conversion_rate = users_completed / previous_users if previous_users > 0 else 0
            drop_off_rate = 1 - conversion_rate

            step_analytics.append(
                FunnelStepAnalytics(
                    step_order=step.step_order,
                    event_name=step.event_name,
                    name=step.name,
                    users_entered=previous_users,
                    users_completed=users_completed,
                    conversion_rate=round(conversion_rate, 4),
                    drop_off_rate=round(drop_off_rate, 4),
                    avg_time_to_next_step=None,  # TODO: Implement time calculation
                )
            )

            previous_users = users_completed

        # Get users who completed entire funnel (last step)
        last_step = steps[-1]
        users_completed_funnel_result = await db.execute(
            select(func.count(func.distinct(Event.user_id))).where(
                and_(
                    Event.event_name == last_step.event_name,
                    Event.timestamp >= start_date,
                    Event.timestamp <= end_date,
                    Event.user_id.isnot(None),
                )
            )
        )
        total_users_completed = users_completed_funnel_result.scalar() or 0

        overall_conversion_rate = (
            total_users_completed / total_users_entered if total_users_entered > 0 else 0
        )

        return FunnelAnalyticsResponse(
            funnel_id=funnel.id,
            funnel_name=funnel.name,
            total_users_entered=total_users_entered,
            total_users_completed=total_users_completed,
            overall_conversion_rate=round(overall_conversion_rate, 4),
            avg_completion_time=None,  # TODO: Implement
            steps=step_analytics,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    async def track_user_progress(
        db: AsyncSession,
        funnel_id: UUID,
        user_id: str,
        event_name: str,
        session_id: str | None = None,
    ) -> None:
        """Track user progress through a funnel"""
        funnel = await FunnelService.get_funnel(db, funnel_id)

        if not funnel or not funnel.is_active:
            return

        # Find the step for this event
        matching_step = None
        for step in funnel.steps:
            if step.event_name == event_name:
                matching_step = step
                break

        if not matching_step:
            return

        # Get or create user progress
        result = await db.execute(
            select(UserFunnelProgress).where(
                and_(
                    UserFunnelProgress.funnel_id == funnel_id,
                    UserFunnelProgress.user_id == user_id,
                    not UserFunnelProgress.completed,
                )
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            # Create new progress tracking
            progress = UserFunnelProgress(
                funnel_id=funnel_id,
                user_id=user_id,
                session_id=session_id,
                current_step=matching_step.step_order,
                step_timestamps={str(matching_step.step_order): datetime.utcnow().isoformat()},
            )
            db.add(progress)
        else:
            # Update existing progress
            if matching_step.step_order > progress.current_step:
                progress.current_step = matching_step.step_order
                timestamps = progress.step_timestamps or {}
                timestamps[str(matching_step.step_order)] = datetime.utcnow().isoformat()
                progress.step_timestamps = timestamps

                # Check if funnel is completed
                max_step = max(step.step_order for step in funnel.steps)
                if progress.current_step >= max_step:
                    progress.completed = True
                    progress.completed_at = datetime.utcnow()

                    # Calculate time to complete
                    if progress.started_at:
                        time_diff = progress.completed_at - progress.started_at
                        progress.time_to_complete_seconds = time_diff.total_seconds()

        await db.flush()
