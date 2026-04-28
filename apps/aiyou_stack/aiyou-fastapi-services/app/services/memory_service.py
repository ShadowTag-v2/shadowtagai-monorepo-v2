# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Memory service for business logic."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.vector_db import vector_db
from app.models import MemoryCategory, MemoryEntry
from app.schemas.memory import MemoryEntryCreate, MemoryEntryUpdate


class MemoryService:
    """Service for managing memory entries."""

    def __init__(self, db: AsyncSession):
        """Initialize memory service."""
        self.db = db

    async def create_memory_entry(self, memory_data: MemoryEntryCreate) -> MemoryEntry:
        """Create a new memory entry."""
        memory = MemoryEntry(
            category=memory_data.category,
            content=memory_data.content,
            project_id=memory_data.project_id,
            confidence=memory_data.confidence,
            source_conversation_ids=memory_data.source_conversation_ids,
            metadata_=memory_data.metadata,
        )
        self.db.add(memory)
        await self.db.flush()
        await self.db.refresh(memory)

        # Add to vector database
        await vector_db.add_memory_entry(
            memory_id=str(memory.id),
            content=memory.content,
            metadata={
                "category": memory.category.value,
                "project_id": str(memory.project_id) if memory.project_id else None,
                "confidence": memory.confidence,
                "active": memory.active,
            },
        )

        return memory

    async def get_memory_entry(self, memory_id: UUID) -> MemoryEntry | None:
        """Get a memory entry by ID."""
        query = select(MemoryEntry).where(MemoryEntry.id == memory_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_memory_entries(
        self,
        project_id: UUID | None = None,
        category: MemoryCategory | None = None,
        active_only: bool = True,
        min_confidence: float | None = None,
    ) -> list[MemoryEntry]:
        """List memory entries with filters."""
        query = select(MemoryEntry)

        # Apply filters
        if project_id:
            query = query.where(MemoryEntry.project_id == project_id)
        if category:
            query = query.where(MemoryEntry.category == category)
        if active_only:
            query = query.where(MemoryEntry.active)
        if min_confidence:
            query = query.where(MemoryEntry.confidence >= min_confidence)

        query = query.order_by(MemoryEntry.updated_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_memory_by_category(
        self,
        project_id: UUID | None = None,
        active_only: bool = True,
    ) -> dict[str, list[MemoryEntry]]:
        """Get memory entries grouped by category."""
        entries = await self.list_memory_entries(
            project_id=project_id,
            active_only=active_only,
            min_confidence=settings.memory_confidence_threshold,
        )

        # Group by category
        by_category = {
            "preferences": [],
            "facts": [],
            "decisions": [],
            "patterns": [],
        }

        for entry in entries:
            by_category[entry.category.value].append(entry)

        return by_category

    async def update_memory_entry(
        self,
        memory_id: UUID,
        update_data: MemoryEntryUpdate,
    ) -> MemoryEntry | None:
        """Update a memory entry."""
        memory = await self.get_memory_entry(memory_id)
        if not memory:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        if "metadata" in update_dict:
            update_dict["metadata_"] = update_dict.pop("metadata")

        for key, value in update_dict.items():
            setattr(memory, key, value)

        await self.db.flush()
        await self.db.refresh(memory)

        # Update in vector database
        await vector_db.update_memory_entry(
            memory_id=str(memory.id),
            content=memory.content,
            metadata={
                "category": memory.category.value,
                "project_id": str(memory.project_id) if memory.project_id else None,
                "confidence": memory.confidence,
                "active": memory.active,
            },
        )

        return memory

    async def delete_memory_entry(self, memory_id: UUID) -> bool:
        """Delete a memory entry."""
        memory = await self.get_memory_entry(memory_id)
        if not memory:
            return False

        await self.db.delete(memory)
        await self.db.flush()

        # Delete from vector database
        await vector_db.delete_memory_entry(str(memory_id))

        return True

    async def format_memory_context(self, project_id: UUID | None = None) -> str:
        """Format memory entries as context for Claude."""
        by_category = await self.get_memory_by_category(
            project_id=project_id,
            active_only=True,
        )

        context_parts = []

        for category, entries in by_category.items():
            if entries:
                context_parts.append(f"### {category.title()}")
                for entry in entries:
                    context_parts.append(f"- {entry.content}")

        return "\n".join(context_parts) if context_parts else "No persistent memory available."
