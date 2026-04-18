"""Search service for semantic conversation search."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.vector_db import vector_db
from app.models import Conversation, Message
from app.services.conversation_service import ConversationService


class SearchService:
    """Service for searching conversations and messages."""

    def __init__(self, db: AsyncSession):
        """Initialize search service."""
        self.db = db
        self.conversation_service = ConversationService(db)

    async def search_conversations(
        self,
        query: str,
        project_id: UUID | None = None,
        top_k: int = 5,
        min_score: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search conversations semantically using vector search.

        Returns conversations with their matching messages.
        """
        if not settings.enable_conversation_search:
            return []

        # Search in vector database
        vector_results = await vector_db.search_conversations(
            query=query,
            project_id=project_id,
            top_k=top_k * 2,  # Get more results to group by conversation
            min_score=min_score,
        )

        # Group results by conversation
        conversation_map: dict[str, dict[str, Any]] = {}

        for result in vector_results:
            conv_id = result["metadata"].get("conversation_id")
            if not conv_id:
                continue

            if conv_id not in conversation_map:
                conversation_map[conv_id] = {
                    "conversation_id": conv_id,
                    "matched_messages": [],
                    "max_score": result["score"],
                }

            conversation_map[conv_id]["matched_messages"].append(
                {
                    "id": result["id"],
                    "content": result["content"],
                    "role": result["metadata"].get("role"),
                    "timestamp": result["metadata"].get("timestamp"),
                    "score": result["score"],
                },
            )

            # Update max score
            conversation_map[conv_id]["max_score"] = max(
                conversation_map[conv_id]["max_score"], result["score"]
            )

        # Sort by max score and limit
        sorted_conversations = sorted(
            conversation_map.values(),
            key=lambda x: x["max_score"],
            reverse=True,
        )[:top_k]

        # Fetch full conversation details
        results = []
        for conv_data in sorted_conversations:
            conversation = await self.conversation_service.get_conversation(
                UUID(conv_data["conversation_id"]),
            )
            if conversation:
                results.append(
                    {
                        "conversation": conversation,
                        "score": conv_data["max_score"],
                        "matched_messages": conv_data["matched_messages"],
                    },
                )

        return results

    async def search_messages(
        self,
        query: str,
        project_id: UUID | None = None,
        top_k: int = 10,
        min_score: float | None = None,
    ) -> list[dict[str, Any]]:
        """Search individual messages semantically.

        Returns individual messages with their parent conversation context.
        """
        if not settings.enable_conversation_search:
            return []

        # Search in vector database
        vector_results = await vector_db.search_conversations(
            query=query,
            project_id=project_id,
            top_k=top_k,
            min_score=min_score,
        )

        # Fetch message details
        results = []
        for result in vector_results:
            message_id = result["id"]

            # Fetch message from database
            query_stmt = select(Message).where(Message.id == UUID(message_id))
            db_result = await self.db.execute(query_stmt)
            message = db_result.scalar_one_or_none()

            if message:
                results.append(
                    {
                        "message": message,
                        "score": result["score"],
                        "conversation_id": message.conversation_id,
                    },
                )

        return results

    async def get_related_suggestions(
        self,
        conversation_id: UUID | None = None,
        limit: int = 5,
    ) -> list[Conversation]:
        """Get related conversation suggestions based on current conversation.

        Uses the last message in the conversation to find similar conversations.
        """
        if not conversation_id or not settings.enable_conversation_search:
            return []

        # Get current conversation
        conversation = await self.conversation_service.get_conversation(conversation_id)
        if not conversation or not conversation.messages:
            return []

        # Use last message as query
        last_message = max(conversation.messages, key=lambda m: m.timestamp)

        # Search for similar conversations
        search_results = await self.search_conversations(
            query=last_message.content,
            project_id=conversation.project_id,
            top_k=limit + 1,  # +1 to exclude current conversation
        )

        # Filter out current conversation and return suggestions
        suggestions = []
        for result in search_results:
            if result["conversation"].id != conversation_id:
                suggestions.append(result["conversation"])
            if len(suggestions) >= limit:
                break

        return suggestions

    async def index_message(
        self,
        message_id: UUID,
        content: str,
        conversation_id: UUID,
        role: str,
        timestamp: str,
        project_id: UUID | None = None,
    ) -> None:
        """Index a message in the vector database."""
        await vector_db.add_message(
            message_id=str(message_id),
            content=content,
            metadata={
                "conversation_id": str(conversation_id),
                "role": role,
                "timestamp": timestamp,
                "project_id": str(project_id) if project_id else None,
            },
        )

    async def index_conversation(self, conversation: Conversation) -> None:
        """Index all messages in a conversation."""
        if not conversation.messages:
            return

        message_ids = []
        contents = []
        metadatas = []

        for message in conversation.messages:
            message_ids.append(str(message.id))
            contents.append(message.content)
            metadatas.append(
                {
                    "conversation_id": str(conversation.id),
                    "role": message.role.value,
                    "timestamp": message.timestamp.isoformat(),
                    "project_id": str(conversation.project_id) if conversation.project_id else None,
                },
            )

        if message_ids:
            await vector_db.add_messages_bulk(
                message_ids=message_ids,
                contents=contents,
                metadatas=metadatas,
            )
