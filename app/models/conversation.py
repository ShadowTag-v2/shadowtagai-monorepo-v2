# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Conversation model."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Conversation(Base):
    """Conversation model for chat sessions."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    title = Column(String, nullable=True)

    # Incognito mode - when True, conversation is not saved to memory
    is_incognito = Column(Boolean, default=False)

    # Conversation summary (auto-generated)
    summary = Column(Text, nullable=True)
    last_summarized_at = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_message_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="conversations")
    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """Message model for individual chat messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)

    # Message content
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)

    # Metadata
    tokens = Column(Integer, nullable=True)
    model = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    embeddings = relationship("VectorEmbedding", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"
