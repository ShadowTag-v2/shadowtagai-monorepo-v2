"""Memory model for storing synthesized information."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.base import Base


class Memory(Base):
    """Memory model for storing synthesized conversation insights."""

    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)

    # Memory content
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)

    # Memory type: 'fact', 'preference', 'context', 'insight'
    memory_type = Column(String, nullable=False, default='fact')

    # Source tracking
    source_conversation_ids = Column(Text, nullable=True)  # JSON array of conversation IDs
    confidence_score = Column(Float, default=1.0)  # Confidence in this memory

    # Memory status
    is_active = Column(Boolean, default=True)
    is_user_edited = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")
    project = relationship("Project", back_populates="memories")
    embeddings = relationship("VectorEmbedding", back_populates="memory", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_memories_user_project', 'user_id', 'project_id'),
        Index('ix_memories_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Memory(id={self.id}, type={self.memory_type})>"


# Import Boolean that was missing
from sqlalchemy import Boolean
