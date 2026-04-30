"""Memory database model."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MemoryCategory(enum.StrEnum):
    """Memory category enumeration."""

    PREFERENCES = "preferences"
    FACTS = "facts"
    DECISIONS = "decisions"
    PATTERNS = "patterns"


class MemoryEntry(Base):
    """Memory entry model."""

    __tablename__ = "memory_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    category: Mapped[MemoryCategory] = mapped_column(
        Enum(MemoryCategory),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )
    source_conversation_ids: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )

    def __repr__(self) -> str:
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<MemoryEntry {self.id} - {self.category.value}: {content_preview}>"
