# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Memory service for managing user memories."""

import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Memory, VectorEmbedding, Project, Conversation, Message
from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemorySynthesisResponse,
)
from app.services.embedding_service import embedding_service
from app.services.summarization_service import summarization_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing memories and synthesis."""

    async def create_memory(self, db: AsyncSession, user_id: int, memory_data: MemoryCreate) -> Memory:
        """
        Create a new memory.

        Args:
            db: Database session
            user_id: User ID
            memory_data: Memory creation data

        Returns:
            Created memory
        """
        # Create memory record
        memory = Memory(
            user_id=user_id,
            project_id=memory_data.project_id,
            title=memory_data.title,
            content=memory_data.content,
            memory_type=memory_data.memory_type,
            confidence_score=memory_data.confidence_score,
            source_conversation_ids=json.dumps(memory_data.source_conversation_ids or []),
        )

        db.add(memory)
        await db.flush()

        # Generate and store embedding
        embedding_vector = await embedding_service.generate_embedding(memory_data.content)
        embedding_bytes = embedding_service.embedding_to_bytes(embedding_vector)

        vector_embedding = VectorEmbedding(
            memory_id=memory.id, embedding=embedding_bytes, model_name=settings.embedding_model, dimension=settings.vector_dimension
        )

        db.add(vector_embedding)
        await db.commit()
        await db.refresh(memory)

        logger.info(f"Created memory {memory.id} for user {user_id}")
        return memory

    async def get_memories(
        self, db: AsyncSession, user_id: int, project_id: int | None = None, memory_type: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Memory]:
        """Get user memories with optional filtering."""
        stmt = select(Memory).where(and_(Memory.user_id == user_id, Memory.is_active == True))

        if project_id is not None:
            stmt = stmt.where(Memory.project_id == project_id)

        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type)

        stmt = stmt.order_by(Memory.created_at.desc()).limit(limit).offset(offset)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_memory(self, db: AsyncSession, memory_id: int, user_id: int, memory_data: MemoryUpdate) -> Memory | None:
        """Update a memory."""
        stmt = select(Memory).where(and_(Memory.id == memory_id, Memory.user_id == user_id))
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()

        if not memory:
            return None

        # Update fields
        update_data = memory_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(memory, field, value)

        memory.is_user_edited = True
        memory.updated_at = datetime.now(timezone.utc)

        # If content changed, regenerate embedding
        if "content" in update_data:
            embedding_vector = await embedding_service.generate_embedding(memory.content)
            embedding_bytes = embedding_service.embedding_to_bytes(embedding_vector)

            # Update or create embedding
            stmt = select(VectorEmbedding).where(VectorEmbedding.memory_id == memory_id)
            result = await db.execute(stmt)
            vector_embedding = result.scalar_one_or_none()

            if vector_embedding:
                vector_embedding.embedding = embedding_bytes
            else:
                vector_embedding = VectorEmbedding(
                    memory_id=memory.id, embedding=embedding_bytes, model_name=settings.embedding_model, dimension=settings.vector_dimension
                )
                db.add(vector_embedding)

        await db.commit()
        await db.refresh(memory)

        logger.info(f"Updated memory {memory_id}")
        return memory

    async def delete_memory(self, db: AsyncSession, memory_id: int, user_id: int) -> bool:
        """Soft delete a memory."""
        stmt = select(Memory).where(and_(Memory.id == memory_id, Memory.user_id == user_id))
        result = await db.execute(stmt)
        memory = result.scalar_one_or_none()

        if not memory:
            return False

        memory.is_active = False
        await db.commit()

        logger.info(f"Deleted memory {memory_id}")
        return True

    async def synthesize_user_memories(self, db: AsyncSession, user_id: int, project_id: int | None = None) -> MemorySynthesisResponse:
        """
        Create a synthesis of all user memories.

        Args:
            db: Database session
            user_id: User ID
            project_id: Optional project ID to limit synthesis

        Returns:
            Memory synthesis response
        """
        # Get all active memories
        memories = await self.get_memories(db, user_id, project_id=project_id, limit=settings.max_memory_items_per_project)

        if not memories:
            return MemorySynthesisResponse(
                total_memories=0, synthesis="No memories available", updated_at=datetime.now(timezone.utc), project_id=project_id
            )

        # Format memories for synthesis
        memory_dicts = [
            {"memory_type": m.memory_type, "title": m.title, "content": m.content, "confidence_score": m.confidence_score} for m in memories
        ]

        # Generate synthesis using Claude
        synthesis = await summarization_service.synthesize_memories(memory_dicts)

        # Update project summary if applicable
        if project_id:
            stmt = select(Project).where(and_(Project.id == project_id, Project.user_id == user_id))
            result = await db.execute(stmt)
            project = result.scalar_one_or_none()

            if project:
                project.summary = synthesis
                project.last_synthesis_at = datetime.now(timezone.utc)
                await db.commit()

        return MemorySynthesisResponse(
            total_memories=len(memories), synthesis=synthesis, updated_at=datetime.now(timezone.utc), project_id=project_id
        )

    async def auto_extract_memories_from_conversation(self, db: AsyncSession, conversation_id: int, user_id: int) -> list[Memory]:
        """
        Automatically extract and create memories from a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            List of created memories
        """
        # Get conversation and messages
        stmt = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.is_incognito == False,  # Skip incognito conversations
            )
        )
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            return []

        # Get messages
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
        result = await db.execute(stmt)
        messages = list(result.scalars().all())

        if len(messages) < settings.summarization_min_messages:
            logger.info(f"Conversation {conversation_id} has too few messages for extraction")
            return []

        # Extract memories using Claude
        extracted = await summarization_service.extract_memories(messages)

        created_memories = []
        for mem_data in extracted:
            memory_create = MemoryCreate(
                title=mem_data.get("title"),
                content=mem_data["content"],
                memory_type=mem_data.get("type", "fact"),
                project_id=conversation.project_id,
                source_conversation_ids=[conversation_id],
                confidence_score=0.8,  # Auto-extracted memories have lower confidence
            )

            memory = await self.create_memory(db, user_id, memory_create)
            created_memories.append(memory)

        logger.info(f"Extracted {len(created_memories)} memories from conversation {conversation_id}")
        return created_memories


# Global singleton instance
memory_service = MemoryService()
