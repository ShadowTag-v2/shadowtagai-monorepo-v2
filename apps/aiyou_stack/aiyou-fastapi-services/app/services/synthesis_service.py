"""Memory synthesis service."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.claude_client import claude_client
from app.models.memory import MemoryCategory
from app.schemas.memory import MemoryEntryCreate
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService


class SynthesisService:
    """Service for memory synthesis from conversations."""

    def __init__(self, db: AsyncSession):
        """Initialize synthesis service."""
        self.db = db
        self.conversation_service = ConversationService(db)
        self.memory_service = MemoryService(db)

    async def synthesize_memory(
        self,
        project_id: UUID | None = None,
        since: datetime | None = None,
        force: bool = False,
    ) -> dict[str, int]:
        """
        Synthesize memory from recent conversations.

        Returns:
            Dict with counts of entries created/updated and conversations processed.
        """
        # Get recent conversations
        if not since and not force:
            # Default to conversations from the last synthesis interval
            since = datetime.utcnow() - timedelta(hours=settings.memory_synthesis_interval_hours)

        conversations = await self.conversation_service.get_recent_conversations_for_synthesis(
            project_id=project_id,
            since=since,
            limit=100,
        )

        if not conversations:
            return {
                "entries_created": 0,
                "entries_updated": 0,
                "conversations_processed": 0,
            }

        # Format conversations for synthesis
        conversations_data = []
        for conv in conversations:
            conv_data = {
                "id": str(conv.id),
                "title": conv.title,
                "messages": [
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                    }
                    for msg in conv.messages
                ],
            }
            conversations_data.append(conv_data)

        # Get existing memory for context
        existing_memory = await self.memory_service.format_memory_context(project_id=project_id)

        # Use Claude to synthesize memory
        memory_synthesis = await claude_client.synthesize_memory(
            conversations=conversations_data,
            existing_memory=existing_memory if existing_memory else None,
        )

        # Process and store synthesized memory
        entries_created = 0
        entries_updated = 0

        conversation_ids = [str(conv.id) for conv in conversations]

        for category_name, entries in memory_synthesis.items():
            if category_name not in ["preferences", "facts", "decisions", "patterns"]:
                continue

            category = MemoryCategory[category_name.upper()]

            for entry_data in entries:
                # Check if similar memory already exists
                existing = await self._find_similar_memory(
                    content=entry_data["content"],
                    category=category,
                    project_id=project_id,
                )

                if existing:
                    # Update existing memory entry
                    # Merge source conversation IDs
                    existing_ids = existing.source_conversation_ids or []
                    merged_ids = list(set(existing_ids + conversation_ids))

                    # Update confidence (take max)
                    new_confidence = max(
                        existing.confidence,
                        entry_data.get("confidence", 0.8),
                    )

                    from app.schemas.memory import MemoryEntryUpdate

                    await self.memory_service.update_memory_entry(
                        memory_id=existing.id,
                        update_data=MemoryEntryUpdate(
                            confidence=new_confidence,
                            metadata={
                                **(existing.metadata_ or {}),
                                "last_reinforced": datetime.utcnow().isoformat(),
                                "source_conversation_ids": merged_ids,
                            },
                        ),
                    )
                    entries_updated += 1
                else:
                    # Create new memory entry
                    await self.memory_service.create_memory_entry(
                        memory_data=MemoryEntryCreate(
                            category=category,
                            content=entry_data["content"],
                            project_id=project_id,
                            confidence=entry_data.get("confidence", 0.8),
                            source_conversation_ids=conversation_ids,
                            metadata={
                                "synthesized_at": datetime.utcnow().isoformat(),
                            },
                        )
                    )
                    entries_created += 1

        return {
            "entries_created": entries_created,
            "entries_updated": entries_updated,
            "conversations_processed": len(conversations),
        }

    async def _find_similar_memory(
        self,
        content: str,
        category: MemoryCategory,
        project_id: UUID | None = None,
    ) -> object | None:
        """Find similar existing memory entry."""
        # Get all memory in the same category
        existing_memories = await self.memory_service.list_memory_entries(
            project_id=project_id,
            category=category,
            active_only=True,
        )

        # Simple similarity check (in production, use embeddings)
        content_lower = content.lower()
        for memory in existing_memories:
            memory_lower = memory.content.lower()

            # Check if content is very similar (simple heuristic)
            if content_lower == memory_lower:
                return memory

            # Check for substantial overlap (>70% of words)
            content_words = set(content_lower.split())
            memory_words = set(memory_lower.split())
            overlap = len(content_words & memory_words) / max(len(content_words), len(memory_words))

            if overlap > 0.7:
                return memory

        return None


async def run_periodic_synthesis(db: AsyncSession):
    """Run periodic memory synthesis (called by scheduler)."""
    if not settings.enable_memory_synthesis:
        return

    service = SynthesisService(db)

    # Synthesize for all projects (None = global)
    result = await service.synthesize_memory(project_id=None, force=False)

    print(
        f"Memory synthesis completed: "
        f"{result['entries_created']} created, "
        f"{result['entries_updated']} updated, "
        f"{result['conversations_processed']} conversations processed"
    )
