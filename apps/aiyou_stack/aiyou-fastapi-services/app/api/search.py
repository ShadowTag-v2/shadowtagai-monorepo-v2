# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Search API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.conversation import ConversationResponse
from app.schemas.search import (
    ConversationSearchResult,
    MessageSearchResult,
    SearchRequest,
    SearchResponse,
)
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/conversations", response_model=SearchResponse)
async def search_conversations(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Search conversations semantically."""
    service = SearchService(db)
    results = await service.search_conversations(
        query=request.query,
        project_id=request.project_id,
        top_k=request.top_k,
        min_score=request.min_score,
    )

    # Convert to response format
    search_results = []
    for result in results:
        search_results.append(
            ConversationSearchResult(
                conversation=result["conversation"],
                score=result["score"],
                matched_messages=result["matched_messages"],
            ),
        )

    return SearchResponse(
        query=request.query,
        results=search_results,
        total=len(search_results),
    )


@router.post("/messages", response_model=SearchResponse)
async def search_messages(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Search specific messages."""
    service = SearchService(db)
    results = await service.search_messages(
        query=request.query,
        project_id=request.project_id,
        top_k=request.top_k,
        min_score=request.min_score,
    )

    # Convert to response format
    search_results = []
    for result in results:
        search_results.append(
            MessageSearchResult(
                message=result["message"],
                score=result["score"],
                conversation_id=result["conversation_id"],
            ),
        )

    return SearchResponse(
        query=request.query,
        results=search_results,
        total=len(search_results),
    )


@router.get("/suggestions", response_model=list[ConversationResponse])
async def get_suggestions(
    conversation_id: UUID | None = Query(None),  # noqa: B008
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """Get related conversation suggestions."""
    service = SearchService(db)
    suggestions = await service.get_related_suggestions(
        conversation_id=conversation_id,
        limit=limit,
    )
    return suggestions
