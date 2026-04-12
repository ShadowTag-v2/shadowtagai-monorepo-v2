"""Conversation service for business logic."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation, Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from app.schemas.message import MessageCreate


class ConversationService:
    """Service for managing conversations."""

    def __init__(self, db: AsyncSession):
        """Initialize conversation service."""
        self.db = db

    async def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            title=conversation_data.title,
            project_id=conversation_data.project_id,
            metadata_=conversation_data.metadata,
            incognito=conversation_data.incognito,
        )
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        """Get a conversation by ID."""
        query = select(Conversation).where(Conversation.id == conversation_id)
        query = query.options(selectinload(Conversation.messages))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_conversations(
        self,
        project_id: UUID | None = None,
        include_incognito: bool = False,
        active_only: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Conversation], int]:
        """List conversations with pagination."""
        query = select(Conversation)

        # Apply filters
        if project_id:
            query = query.where(Conversation.project_id == project_id)
        if not include_incognito:
            query = query.where(not Conversation.incognito)
        if active_only:
            query = query.where(Conversation.active)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        query = query.order_by(Conversation.updated_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.options(selectinload(Conversation.messages))

        result = await self.db.execute(query)
        conversations = result.scalars().all()

        return list(conversations), total

    async def update_conversation(
        self, conversation_id: UUID, update_data: ConversationUpdate
    ) -> Conversation | None:
        """Update a conversation."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        if "metadata" in update_dict:
            update_dict["metadata_"] = update_dict.pop("metadata")

        for key, value in update_dict.items():
            setattr(conversation, key, value)

        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.flush()
        return True

    async def add_message(
        self, conversation_id: UUID, message_data: MessageCreate
    ) -> Message | None:
        """Add a message to a conversation."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None

        message = Message(
            conversation_id=conversation_id,
            role=message_data.role,
            content=message_data.content,
            metadata_=message_data.metadata,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_recent_conversations_for_synthesis(
        self,
        project_id: UUID | None = None,
        since: str | None = None,
        limit: int = 100,
    ) -> list[Conversation]:
        """Get recent conversations for memory synthesis."""
        query = select(Conversation).where(
            not Conversation.incognito,
            Conversation.active,
        )

        if project_id:
            query = query.where(Conversation.project_id == project_id)

        if since:
            query = query.where(Conversation.updated_at > since)

        query = query.order_by(Conversation.updated_at.desc()).limit(limit)
        query = query.options(selectinload(Conversation.messages))

        result = await self.db.execute(query)
        return list(result.scalars().all())
