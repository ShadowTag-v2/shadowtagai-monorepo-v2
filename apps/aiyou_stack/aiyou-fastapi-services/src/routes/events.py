"""Event tracking API routes"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.event import EventCreate, EventQuery, EventResponse
from src.services.event_service import EventService
from src.services.user_service import UserService

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def track_event(
    event: EventCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Track a new event

    This endpoint allows you to track user events such as page views, clicks, conversions, etc.
    """
    # Create or update user if user_id is provided
    if event.user_id:
        await UserService.get_or_create_user(db, event.user_id)

    # Create event
    created_event = await EventService.create_event(db, event)

    return created_event


@router.get("/", response_model=list[EventResponse])
async def get_events(
    event_name: str = None,
    event_type: str = None,
    user_id: str = None,
    session_id: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Get events with filtering

    Query events based on various criteria such as event name, type, user, or session.
    """
    query = EventQuery(
        event_name=event_name,
        event_type=event_type,
        user_id=user_id,
        session_id=session_id,
        limit=limit,
        offset=offset,
    )

    events = await EventService.get_events(db, query)

    return events


@router.get("/stats/count")
async def get_event_count(
    event_name: str = None,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Get count of events

    Returns the total count of events, optionally filtered by event name.
    """
    count = await EventService.get_event_count(db, event_name=event_name)

    return {"count": count, "event_name": event_name}


@router.get("/stats/unique-users")
async def get_unique_users(
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Get count of unique users

    Returns the total number of unique users who have triggered events.
    """
    count = await EventService.get_unique_users(db)

    return {"unique_users": count}


@router.get("/stats/top-events")
async def get_top_events(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Get top events by count

    Returns the most frequently occurring events.
    """
    top_events = await EventService.get_top_events(db, limit=limit)

    return {"top_events": top_events}
