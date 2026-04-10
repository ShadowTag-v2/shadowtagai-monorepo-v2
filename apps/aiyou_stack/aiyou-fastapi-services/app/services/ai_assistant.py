"""
AI Assistant service with conversation management and context handling.
"""

import uuid
from collections.abc import AsyncIterator
from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.conversation import Conversation, Message
from app.services.llm_client import LLMClientFactory
from app.services.prompt_manager import PromptManager

logger = structlog.get_logger()


class AIAssistant:
    """AI Assistant with conversation management and context handling."""

    def __init__(self, db: AsyncSession, provider: str | None = None, model: str | None = None):
        self.db = db
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model
        self.llm_client = LLMClientFactory.create_client(provider=self.provider, model=self.model)
        self.prompt_manager = PromptManager()
        logger.info("AI Assistant initialized", provider=self.provider, model=self.model)

    async def create_conversation(
        self,
        user_id: str | None = None,
        title: str | None = None,
        system_prompt: str | None = None,
        metadata: dict | None = None,
    ) -> Conversation:
        """Create a new conversation."""
        session_id = str(uuid.uuid4())

        conversation = Conversation(
            session_id=session_id,
            user_id=user_id,
            title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            system_prompt=system_prompt or settings.DEFAULT_SYSTEM_PROMPT,
            model_provider=self.provider,
            model_name=self.model,
            metadata=metadata or {},
        )

        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)

        logger.info("Conversation created", session_id=session_id, conversation_id=conversation.id)

        return conversation

    async def get_conversation(self, session_id: str) -> Conversation | None:
        """Get a conversation by session ID."""
        result = await self.db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation_history(
        self, session_id: str, limit: int | None = None
    ) -> list[Message]:
        """Get conversation message history."""
        conversation = await self.get_conversation(session_id)
        if not conversation:
            return []

        query = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )

        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        messages = result.scalars().all()

        logger.info(
            "Retrieved conversation history", session_id=session_id, message_count=len(messages)
        )

        return list(messages)

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tokens: int | None = None,
        metadata: dict | None = None,
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens=tokens,
            metadata=metadata or {},
        )

        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)

        return message

    def _format_messages_for_llm(self, messages: list[Message]) -> list[dict[str, str]]:
        """Format database messages for LLM API."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role in ["user", "assistant"]
        ]

    async def chat(
        self,
        message: str,
        session_id: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        save_history: bool = True,
        user_id: str | None = None,
    ) -> tuple[str, str]:
        """
        Send a chat message and get a response.

        Returns:
            Tuple of (response_text, session_id)
        """
        # Get or create conversation
        if session_id:
            conversation = await self.get_conversation(session_id)
            if not conversation:
                raise ValueError(f"Conversation not found: {session_id}")
        else:
            conversation = await self.create_conversation(
                user_id=user_id, system_prompt=system_prompt
            )
            session_id = conversation.session_id

        # Add user message to history
        if save_history:
            await self.add_message(conversation_id=conversation.id, role="user", content=message)

        # Get conversation history
        history = await self.get_conversation_history(
            session_id, limit=settings.MAX_CONVERSATION_HISTORY
        )

        # Format messages for LLM
        llm_messages = self._format_messages_for_llm(history)

        # Get response from LLM
        response = await self.llm_client.chat(
            messages=llm_messages,
            system_prompt=system_prompt or conversation.system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Save assistant response
        if save_history:
            await self.add_message(
                conversation_id=conversation.id, role="assistant", content=response
            )

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        await self.db.flush()

        logger.info(
            "Chat completed",
            session_id=session_id,
            message_length=len(message),
            response_length=len(response),
        )

        return response, session_id

    async def chat_stream(
        self,
        message: str,
        session_id: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        save_history: bool = True,
        user_id: str | None = None,
    ) -> AsyncIterator[tuple[str, str]]:
        """
        Send a chat message and stream the response.

        Yields:
            Tuples of (text_chunk, session_id)
        """
        # Get or create conversation
        if session_id:
            conversation = await self.get_conversation(session_id)
            if not conversation:
                raise ValueError(f"Conversation not found: {session_id}")
        else:
            conversation = await self.create_conversation(
                user_id=user_id, system_prompt=system_prompt
            )
            session_id = conversation.session_id

        # Add user message to history
        if save_history:
            await self.add_message(conversation_id=conversation.id, role="user", content=message)

        # Get conversation history
        history = await self.get_conversation_history(
            session_id, limit=settings.MAX_CONVERSATION_HISTORY
        )

        # Format messages for LLM
        llm_messages = self._format_messages_for_llm(history)

        # Stream response from LLM
        full_response = []
        async for chunk in self.llm_client.chat_stream(
            messages=llm_messages,
            system_prompt=system_prompt or conversation.system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            full_response.append(chunk)
            yield chunk, session_id

        # Save complete assistant response
        if save_history and full_response:
            complete_response = "".join(full_response)
            await self.add_message(
                conversation_id=conversation.id, role="assistant", content=complete_response
            )

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        await self.db.flush()

        logger.info("Streaming chat completed", session_id=session_id, chunks=len(full_response))

    async def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation and its messages."""
        conversation = await self.get_conversation(session_id)
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.flush()

        logger.info("Conversation deleted", session_id=session_id)
        return True

    async def list_conversations(
        self, user_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        """List conversations for a user."""
        query = select(Conversation)

        if user_id:
            query = query.where(Conversation.user_id == user_id)

        query = query.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        conversations = result.scalars().all()

        return list(conversations)
