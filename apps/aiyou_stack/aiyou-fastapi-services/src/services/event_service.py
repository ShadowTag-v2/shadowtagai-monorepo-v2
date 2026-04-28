# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Event tracking service"""

from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event
from src.models.user import User
from src.schemas.event import EventCreate, EventQuery


class EventService:
    """Service for managing events"""

    @staticmethod
    async def create_event(db: AsyncSession, event_data: EventCreate) -> Event:
        """Create a new event"""
        event = Event(
            event_name=event_data.event_name,
            event_type=event_data.event_type,
            user_id=event_data.user_id,
            anonymous_id=event_data.anonymous_id,
            session_id=event_data.session_id,
            properties=event_data.properties or {},
            page_url=event_data.page_url,
            page_title=event_data.page_title,
            referrer=event_data.referrer,
            user_agent=event_data.user_agent,
            device_type=event_data.device_type,
            browser=event_data.browser,
            os=event_data.os,
            country=event_data.country,
            region=event_data.region,
            city=event_data.city,
            ip_address=event_data.ip_address,
            utm_source=event_data.utm_source,
            utm_medium=event_data.utm_medium,
            utm_campaign=event_data.utm_campaign,
            utm_term=event_data.utm_term,
            utm_content=event_data.utm_content,
            revenue=event_data.revenue,
            currency=event_data.currency,
            timestamp=event_data.timestamp or datetime.utcnow(),
        )

        db.add(event)
        await db.flush()

        # Update user last_seen and event_count
        if event_data.user_id:
            await EventService._update_user_stats(db, event_data.user_id)

        return event

    @staticmethod
    async def _update_user_stats(db: AsyncSession, user_id: str) -> None:
        """Update user statistics"""
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if user:
            user.last_seen = datetime.utcnow()
            user.event_count = user.event_count + 1
            await db.flush()

    @staticmethod
    async def get_events(db: AsyncSession, query: EventQuery) -> list[Event]:
        """Get events with filtering"""
        stmt = select(Event)

        # Apply filters
        conditions = []

        if query.event_name:
            conditions.append(Event.event_name == query.event_name)

        if query.event_type:
            conditions.append(Event.event_type == query.event_type)

        if query.user_id:
            conditions.append(Event.user_id == query.user_id)

        if query.session_id:
            conditions.append(Event.session_id == query.session_id)

        if query.start_date:
            conditions.append(Event.timestamp >= query.start_date)

        if query.end_date:
            conditions.append(Event.timestamp <= query.end_date)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Apply ordering, limit and offset
        stmt = stmt.order_by(Event.timestamp.desc())
        stmt = stmt.limit(query.limit).offset(query.offset)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_event_count(
        db: AsyncSession,
        event_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """Get count of events matching criteria"""
        stmt = select(func.count(Event.id))

        conditions = []

        if event_name:
            conditions.append(Event.event_name == event_name)

        if start_date:
            conditions.append(Event.timestamp >= start_date)

        if end_date:
            conditions.append(Event.timestamp <= end_date)

        if filters:
            for key, value in filters.items():
                # Handle JSON property filtering
                conditions.append(Event.properties[key].astext == str(value))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def get_unique_users(
        db: AsyncSession,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Get count of unique users in time period"""
        stmt = select(func.count(func.distinct(Event.user_id))).where(Event.user_id.isnot(None))

        conditions = []

        if start_date:
            conditions.append(Event.timestamp >= start_date)

        if end_date:
            conditions.append(Event.timestamp <= end_date)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        return result.scalar() or 0

    @staticmethod
    async def get_top_events(
        db: AsyncSession,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get top events by count"""
        stmt = (
            select(Event.event_name, func.count(Event.id).label("count"))
            .group_by(Event.event_name)
            .order_by(func.count(Event.id).desc())
            .limit(limit)
        )

        conditions = []

        if start_date:
            conditions.append(Event.timestamp >= start_date)

        if end_date:
            conditions.append(Event.timestamp <= end_date)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await db.execute(stmt)
        rows = result.all()

        return [{"event_name": row.event_name, "count": row.count} for row in rows]
