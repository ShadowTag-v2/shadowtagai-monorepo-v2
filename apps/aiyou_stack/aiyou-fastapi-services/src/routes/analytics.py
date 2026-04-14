"""Analytics and insights API routes"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.analytics import (
    InsightResponse,
    TimeSeriesQuery,
    TimeSeriesResponse,
    UserBehaviorResponse,
)
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/time-series", response_model=TimeSeriesResponse)
async def get_time_series(
    query: TimeSeriesQuery,
    db: AsyncSession = Depends(get_db),
):
    """Get time series data

    Retrieve time series data for a specific metric over a time period.
    Supports metrics like event_count, user_count, revenue, etc.
    """
    data = await AnalyticsService.get_time_series(db, query)

    return data


@router.get("/user-behavior", response_model=UserBehaviorResponse)
async def analyze_user_behavior(
    user_id: str = None,
    segment: str = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Analyze user behavior

    Get detailed analysis of user behavior including session metrics,
    most common events, and conversion paths.
    Can analyze a specific user or a user segment.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    behavior = await AnalyticsService.analyze_user_behavior(
        db,
        user_id=user_id,
        segment=segment,
        start_date=start_date,
        end_date=end_date,
    )

    return behavior


@router.get("/insights", response_model=InsightResponse)
async def generate_insights(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """Generate insights

    Generate actionable insights from your analytics data including trends,
    anomalies, and recommendations.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    insights = await AnalyticsService.generate_insights(db, start_date, end_date)

    return insights


@router.get("/overview")
async def get_analytics_overview(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """Get analytics overview

    Get a high-level overview of key metrics including total events,
    unique users, and top events.
    """
    from src.services.event_service import EventService

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get key metrics
    total_events = await EventService.get_event_count(db, start_date=start_date, end_date=end_date)
    unique_users = await EventService.get_unique_users(db, start_date=start_date, end_date=end_date)
    top_events = await EventService.get_top_events(
        db, start_date=start_date, end_date=end_date, limit=5,
    )

    return {
        "time_period": f"{days}d",
        "start_date": start_date,
        "end_date": end_date,
        "total_events": total_events,
        "unique_users": unique_users,
        "top_events": top_events,
        "avg_events_per_user": round(total_events / unique_users, 2) if unique_users > 0 else 0,
    }
