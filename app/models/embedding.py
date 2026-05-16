# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Vector embedding models for semantic search."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, LargeBinary, Index
from sqlalchemy.orm import relationship

from app.db.base import Base


class VectorEmbedding(Base):
    """Vector embedding model for semantic search."""

    __tablename__ = "vector_embeddings"

    id = Column(Integer, primary_key=True, index=True)

    # Link to message or memory
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)
    memory_id = Column(Integer, ForeignKey("memories.id", ondelete="CASCADE"), nullable=True)

    # Embedding data (stored as binary)
    embedding = Column(LargeBinary, nullable=False)

    # Embedding model used
    model_name = Column(String, nullable=False)
    dimension = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    message = relationship("Message", back_populates="embeddings")
    memory = relationship("Memory", back_populates="embeddings")

    __table_args__ = (
        Index("ix_embeddings_message", "message_id"),
        Index("ix_embeddings_memory", "memory_id"),
    )

    def __repr__(self) -> str:
        return f"<VectorEmbedding(id={self.id}, model={self.model_name})>"
