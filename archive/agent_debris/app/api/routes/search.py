"""Search API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.search import SearchQuery, SearchResponse
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


# Mock user dependency (replace with real auth)
async def get_current_user_id() -> int:
    """Get current user ID from auth token."""
    return 1  # TODO: Implement real authentication


@router.post("/", response_model=SearchResponse)
async def search_conversations_and_memories(query: SearchQuery, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """
    Search through conversations and memories using semantic search.

    This endpoint implements Claude's conversation_search tool functionality.
    """
    results = await search_service.search(db, user_id, query)
    return results


@router.get("/conversations", response_model=SearchResponse)
async def search_conversations_only(
    query: str,
    project_id: int = None,
    top_k: int = 10,
    min_relevance: float = 0.5,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Search through conversations only.

    Simplified endpoint for conversation-only search.
    """
    search_query = SearchQuery(
        query=query, project_id=project_id, top_k=top_k, min_relevance=min_relevance, search_conversations=True, search_memories=False
    )

    results = await search_service.search(db, user_id, search_query)
    return results


@router.get("/memories", response_model=SearchResponse)
async def search_memories_only(
    query: str,
    project_id: int = None,
    top_k: int = 10,
    min_relevance: float = 0.5,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Search through memories only.

    Simplified endpoint for memory-only search.
    """
    search_query = SearchQuery(
        query=query, project_id=project_id, top_k=top_k, min_relevance=min_relevance, search_conversations=False, search_memories=True
    )

    results = await search_service.search(db, user_id, search_query)
    return results
