# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Search service for semantic conversation and memory search."""

import logging
import time
import numpy as np
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message, Memory, VectorEmbedding, Conversation
from app.schemas.search import (
    SearchQuery,
    SearchResponse,
    ConversationSearchResult,
)
from app.schemas.memory import MemorySearchResult
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class SearchService:
    """Service for semantic search across conversations and memories."""

    async def search(self, db: AsyncSession, user_id: int, query: SearchQuery) -> SearchResponse:
        """
        Perform semantic search across conversations and memories.

        Args:
            db: Database session
            user_id: User ID
            query: Search query parameters

        Returns:
            Search results with relevance scores
        """
        start_time = time.time()

        # Generate query embedding
        query_embedding = await embedding_service.generate_embedding(query.query)

        conversation_results = []
        memory_results = []

        # Search conversations if enabled
        if query.search_conversations:
            conversation_results = await self._search_conversations(db, user_id, query_embedding, query)

        # Search memories if enabled
        if query.search_memories:
            memory_results = await self._search_memories(db, user_id, query_embedding, query)

        search_time_ms = (time.time() - start_time) * 1000

        return SearchResponse(
            query=query.query,
            total_results=len(conversation_results) + len(memory_results),
            conversation_results=conversation_results,
            memory_results=memory_results,
            search_time_ms=search_time_ms,
        )

    async def _search_conversations(
        self, db: AsyncSession, user_id: int, query_embedding: np.ndarray, query: SearchQuery
    ) -> list[ConversationSearchResult]:
        """Search in conversation messages."""
        # Build query for message embeddings
        stmt = (
            select(Message, VectorEmbedding, Conversation)
            .join(VectorEmbedding, Message.id == VectorEmbedding.message_id)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(
                and_(
                    Conversation.user_id == user_id,
                    Conversation.is_incognito == False,  # Exclude incognito
                    Conversation.is_active == True,
                )
            )
        )

        # Filter by project if specified
        if query.project_id is not None:
            stmt = stmt.where(Conversation.project_id == query.project_id)

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # Extract embeddings and compute similarities
        results_with_scores = []
        for message, embedding_obj, conversation in rows:
            # Convert stored embedding to numpy array
            stored_embedding = embedding_service.bytes_to_embedding(embedding_obj.embedding)

            # Compute cosine similarity
            similarity = float(np.dot(query_embedding, stored_embedding))

            # Filter by minimum relevance
            if similarity >= query.min_relevance:
                results_with_scores.append((message, conversation, similarity))

        # Sort by relevance score
        results_with_scores.sort(key=lambda x: x[2], reverse=True)

        # Limit to top_k
        results_with_scores = results_with_scores[: query.top_k]

        # Convert to response format
        conversation_results = [
            ConversationSearchResult(
                conversation_id=conversation.id,
                conversation_title=conversation.title,
                message_id=message.id,
                message_content=message.content,
                message_role=message.role,
                relevance_score=score,
                created_at=message.created_at,
                project_id=conversation.project_id,
            )
            for message, conversation, score in results_with_scores
        ]

        return conversation_results

    async def _search_memories(self, db: AsyncSession, user_id: int, query_embedding: np.ndarray, query: SearchQuery) -> list[MemorySearchResult]:
        """Search in memories."""
        # Build query for memory embeddings
        stmt = (
            select(Memory, VectorEmbedding)
            .join(VectorEmbedding, Memory.id == VectorEmbedding.memory_id)
            .where(and_(Memory.user_id == user_id, Memory.is_active == True))
        )

        # Filter by project if specified
        if query.project_id is not None:
            stmt = stmt.where(Memory.project_id == query.project_id)

        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            return []

        # Extract embeddings and compute similarities
        results_with_scores = []
        for memory, embedding_obj in rows:
            # Convert stored embedding to numpy array
            stored_embedding = embedding_service.bytes_to_embedding(embedding_obj.embedding)

            # Compute cosine similarity
            similarity = float(np.dot(query_embedding, stored_embedding))

            # Filter by minimum relevance
            if similarity >= query.min_relevance:
                results_with_scores.append((memory, similarity))

        # Sort by relevance score
        results_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Limit to top_k
        results_with_scores = results_with_scores[: query.top_k]

        # Convert to response format
        memory_results = [
            MemorySearchResult(
                id=memory.id,
                user_id=memory.user_id,
                project_id=memory.project_id,
                title=memory.title,
                content=memory.content,
                memory_type=memory.memory_type,
                confidence_score=memory.confidence_score,
                is_active=memory.is_active,
                is_user_edited=memory.is_user_edited,
                created_at=memory.created_at,
                updated_at=memory.updated_at,
                last_accessed_at=memory.last_accessed_at,
                relevance_score=score,
            )
            for memory, score in results_with_scores
        ]

        # Update last_accessed_at for found memories
        for memory, _ in results_with_scores:
            memory.last_accessed_at = time.time()
        await db.commit()

        return memory_results


# Global singleton instance
search_service = SearchService()
