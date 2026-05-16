# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Conversation service for managing chats."""

import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation, Message, VectorEmbedding
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
)
from app.schemas.search import RecentChatsQuery
from app.services.embedding_service import embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations and messages."""

    async def create_conversation(self, db: AsyncSession, user_id: int, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=user_id, project_id=conversation_data.project_id, title=conversation_data.title, is_incognito=conversation_data.is_incognito
        )

        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation

    async def get_conversation(self, db: AsyncSession, conversation_id: int, user_id: int, include_messages: bool = False) -> Conversation | None:
        """Get a conversation by ID."""
        stmt = select(Conversation).where(and_(Conversation.id == conversation_id, Conversation.user_id == user_id))

        if include_messages:
            stmt = stmt.options(selectinload(Conversation.messages))

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_conversations(self, db: AsyncSession, user_id: int, query: RecentChatsQuery) -> list[Conversation]:
        """Get recent conversations."""
        stmt = select(Conversation).where(Conversation.user_id == user_id)

        # Filter by project if specified
        if query.project_id is not None:
            stmt = stmt.where(Conversation.project_id == query.project_id)

        # Exclude incognito chats unless explicitly included
        if not query.include_incognito:
            stmt = stmt.where(Conversation.is_incognito == False)

        stmt = stmt.where(Conversation.is_active == True).order_by(Conversation.last_message_at.desc()).limit(query.limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_conversation(
        self, db: AsyncSession, conversation_id: int, user_id: int, conversation_data: ConversationUpdate
    ) -> Conversation | None:
        """Update a conversation."""
        conversation = await self.get_conversation(db, conversation_id, user_id)

        if not conversation:
            return None

        update_data = conversation_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)

        conversation.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(conversation)

        logger.info(f"Updated conversation {conversation_id}")
        return conversation

    async def delete_conversation(self, db: AsyncSession, conversation_id: int, user_id: int) -> bool:
        """Soft delete a conversation."""
        conversation = await self.get_conversation(db, conversation_id, user_id)

        if not conversation:
            return False

        conversation.is_active = False
        await db.commit()

        logger.info(f"Deleted conversation {conversation_id}")
        return True

    async def add_message(self, db: AsyncSession, user_id: int, message_data: MessageCreate) -> Message | None:
        """
        Add a message to a conversation.

        Args:
            db: Database session
            user_id: User ID
            message_data: Message data

        Returns:
            Created message or None if conversation not found
        """
        # Verify conversation belongs to user
        conversation = await self.get_conversation(db, message_data.conversation_id, user_id)

        if not conversation:
            return None

        # Create message
        message = Message(conversation_id=message_data.conversation_id, role=message_data.role, content=message_data.content)

        db.add(message)
        await db.flush()

        # Generate and store embedding for semantic search
        embedding_vector = await embedding_service.generate_embedding(message_data.content)
        embedding_bytes = embedding_service.embedding_to_bytes(embedding_vector)

        vector_embedding = VectorEmbedding(
            message_id=message.id, embedding=embedding_bytes, model_name=settings.embedding_model, dimension=settings.vector_dimension
        )

        db.add(vector_embedding)

        # Update conversation's last_message_at
        conversation.last_message_at = datetime.now(timezone.utc)

        # Auto-generate title if this is the first user message
        if not conversation.title:
            stmt = select(func.count(Message.id)).where(Message.conversation_id == message_data.conversation_id)
            result = await db.execute(stmt)
            message_count = result.scalar()

            if message_count == 1 and message_data.role == "user":
                # Use first 50 characters as title
                conversation.title = message_data.content[:50] + ("..." if len(message_data.content) > 50 else "")

        await db.commit()
        await db.refresh(message)

        logger.info(f"Added message {message.id} to conversation {message_data.conversation_id}")
        return message

    async def get_messages(self, db: AsyncSession, conversation_id: int, user_id: int, limit: int = 100, offset: int = 0) -> list[Message]:
        """Get messages from a conversation."""
        # Verify conversation belongs to user
        conversation = await self.get_conversation(db, conversation_id, user_id)

        if not conversation:
            return []

        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at).limit(limit).offset(offset)

        result = await db.execute(stmt)
        return list(result.scalars().all())


# Global singleton instance
conversation_service = ConversationService()
