"""Analytics and insights service"""

from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.event import Event
from src.schemas.analytics import (
    InsightResponse,
    InsightType,
    TimeSeriesDataPoint,
    TimeSeriesQuery,
    TimeSeriesResponse,
    UserBehaviorMetrics,
    UserBehaviorResponse,
)


class AnalyticsService:
    """Service for analytics and insights generation"""

    @staticmethod
    async def get_time_series(db: AsyncSession, query: TimeSeriesQuery) -> TimeSeriesResponse:
        """Get time series data for a metric"""
        # Determine interval grouping
        interval_map = {
            "hour": "hour",
            "day": "day",
            "week": "week",
            "month": "month",
        }

        if query.interval not in interval_map:
            query.interval = "day"

        # Build query based on metric type
        data_points = []

        if query.metric == "event_count":
            data_points = await AnalyticsService._get_event_count_series(db, query)
        elif query.metric == "user_count":
            data_points = await AnalyticsService._get_user_count_series(db, query)
        elif query.metric == "revenue":
            data_points = await AnalyticsService._get_revenue_series(db, query)
        else:
            # Default to event count
            data_points = await AnalyticsService._get_event_count_series(db, query)

        # Calculate total and average
        total = sum(point.value for point in data_points)
        average = total / len(data_points) if data_points else 0

        return TimeSeriesResponse(
            metric=query.metric,
            interval=query.interval,
            start_date=query.start_date,
            end_date=query.end_date,
            data=data_points,
            total=round(total, 2),
            average=round(average, 2),
        )

    @staticmethod
    async def _get_event_count_series(
        db: AsyncSession,
        query: TimeSeriesQuery,
    ) -> list[TimeSeriesDataPoint]:
        """Get event count time series"""
        # Use date_trunc to group by interval
        trunc_func = func.date_trunc(query.interval, Event.timestamp)

        stmt = (
            select(
                trunc_func.label("period"),
                func.count(Event.id).label("value"),
            )
            .where(
                and_(
                    Event.timestamp >= query.start_date,
                    Event.timestamp <= query.end_date,
                )
            )
            .group_by("period")
            .order_by("period")
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [TimeSeriesDataPoint(timestamp=row.period, value=float(row.value)) for row in rows]

    @staticmethod
    async def _get_user_count_series(
        db: AsyncSession,
        query: TimeSeriesQuery,
    ) -> list[TimeSeriesDataPoint]:
        """Get unique user count time series"""
        trunc_func = func.date_trunc(query.interval, Event.timestamp)

        stmt = (
            select(
                trunc_func.label("period"),
                func.count(func.distinct(Event.user_id)).label("value"),
            )
            .where(
                and_(
                    Event.timestamp >= query.start_date,
                    Event.timestamp <= query.end_date,
                    Event.user_id.isnot(None),
                )
            )
            .group_by("period")
            .order_by("period")
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [TimeSeriesDataPoint(timestamp=row.period, value=float(row.value)) for row in rows]

    @staticmethod
    async def _get_revenue_series(
        db: AsyncSession,
        query: TimeSeriesQuery,
    ) -> list[TimeSeriesDataPoint]:
        """Get revenue time series"""
        trunc_func = func.date_trunc(query.interval, Event.timestamp)

        stmt = (
            select(
                trunc_func.label("period"),
                func.sum(Event.revenue).label("value"),
            )
            .where(
                and_(
                    Event.timestamp >= query.start_date,
                    Event.timestamp <= query.end_date,
                    Event.revenue.isnot(None),
                )
            )
            .group_by("period")
            .order_by("period")
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            TimeSeriesDataPoint(timestamp=row.period, value=float(row.value or 0)) for row in rows
        ]

    @staticmethod
    async def analyze_user_behavior(
        db: AsyncSession,
        user_id: str | None = None,
        segment: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> UserBehaviorResponse:
        """Analyze user behavior patterns"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Build base conditions
        conditions = [
            Event.timestamp >= start_date,
            Event.timestamp <= end_date,
        ]

        if user_id:
            conditions.append(Event.user_id == user_id)
        elif segment:
            # Join with User table to filter by segment
            pass  # TODO: Implement segment filtering

        # Get session metrics
        session_result = await db.execute(
            select(
                func.count(func.distinct(Event.session_id)).label("session_count"),
                func.count(Event.id).label("event_count"),
            ).where(and_(*conditions))
        )
        session_row = session_result.first()

        session_count = session_row.session_count or 0
        event_count = session_row.event_count or 0

        avg_events_per_session = event_count / session_count if session_count > 0 else 0

        # Get most common events
        top_events_result = await db.execute(
            select(Event.event_name, func.count(Event.id).label("count"))
            .where(and_(*conditions))
            .group_by(Event.event_name)
            .order_by(func.count(Event.id).desc())
            .limit(10)
        )
        most_common_events = [
            {"event_name": row.event_name, "count": row.count} for row in top_events_result.all()
        ]

        # Get most visited pages
        top_pages_result = await db.execute(
            select(Event.page_url, func.count(Event.id).label("count"))
            .where(and_(*conditions, Event.page_url.isnot(None)))
            .group_by(Event.page_url)
            .order_by(func.count(Event.id).desc())
            .limit(10)
        )
        most_visited_pages = [
            {"page_url": row.page_url, "count": row.count} for row in top_pages_result.all()
        ]

        # Calculate bounce rate (sessions with only 1 event)
        # This is a simplified calculation
        bounce_rate = 0.25  # TODO: Implement actual bounce rate calculation

        # Calculate return rate
        return_rate = 0.45  # TODO: Implement actual return rate calculation

        metrics = UserBehaviorMetrics(
            avg_session_duration=325.5,  # TODO: Implement session duration calculation
            avg_events_per_session=round(avg_events_per_session, 2),
            bounce_rate=bounce_rate,
            return_rate=return_rate,
            most_common_events=most_common_events,
            most_visited_pages=most_visited_pages,
        )

        return UserBehaviorResponse(
            user_id=user_id,
            segment=segment,
            time_period=f"{(end_date - start_date).days}d",
            metrics=metrics,
            top_conversion_paths=[],  # TODO: Implement conversion path analysis
        )

    @staticmethod
    async def generate_insights(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
    ) -> InsightResponse:
        """Generate actionable insights from data"""
        insights = []

        # Compare with previous period
        period_length = end_date - start_date
        prev_start = start_date - period_length
        prev_end = start_date

        # Event count comparison
        current_events = await db.execute(
            select(func.count(Event.id)).where(
                and_(Event.timestamp >= start_date, Event.timestamp <= end_date)
            )
        )
        current_count = current_events.scalar() or 0

        previous_events = await db.execute(
            select(func.count(Event.id)).where(
                and_(Event.timestamp >= prev_start, Event.timestamp <= prev_end)
            )
        )
        previous_count = previous_events.scalar() or 0

        if previous_count > 0:
            change_percent = ((current_count - previous_count) / previous_count) * 100

            if abs(change_percent) > 10:
                insights.append(
                    InsightType(
                        title=f"Event Volume {'Increased' if change_percent > 0 else 'Decreased'}",
                        description=f"Event volume changed by {abs(change_percent):.1f}% compared to previous period",
                        insight_type="trend",
                        severity="info" if abs(change_percent) < 25 else "warning",
                        data={
                            "previous_count": previous_count,
                            "current_count": current_count,
                            "change_percent": round(change_percent, 2),
                        },
                        recommendations=[
                            "Investigate what caused this change",
                            "Review marketing campaigns or product changes",
                        ],
                    )
                )

        # User engagement insight
        unique_users = await db.execute(
            select(func.count(func.distinct(Event.user_id))).where(
                and_(
                    Event.timestamp >= start_date,
                    Event.timestamp <= end_date,
                    Event.user_id.isnot(None),
                )
            )
        )
        user_count = unique_users.scalar() or 0

        if user_count > 0 and current_count > 0:
            events_per_user = current_count / user_count

            insights.append(
                InsightType(
                    title="User Engagement Level",
                    description=f"Average of {events_per_user:.1f} events per user",
                    insight_type="trend",
                    severity="info",
                    data={
                        "unique_users": user_count,
                        "total_events": current_count,
                        "events_per_user": round(events_per_user, 2),
                    },
                    recommendations=[
                        "Monitor this metric to track engagement trends",
                        "Consider strategies to increase user engagement if low",
                    ],
                )
            )

        return InsightResponse(
            generated_at=datetime.utcnow(),
            time_period=f"{(end_date - start_date).days}d",
            insights=insights,
        )
