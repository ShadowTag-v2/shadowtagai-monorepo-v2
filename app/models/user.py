# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""User model."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
  """User model for authentication and memory management."""

  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  email = Column(String, unique=True, index=True, nullable=False)
  username = Column(String, unique=True, index=True, nullable=False)
  hashed_password = Column(String, nullable=False)
  is_active = Column(Boolean, default=True)
  is_superuser = Column(Boolean, default=False)

  # Memory settings
  memory_enabled = Column(Boolean, default=True)
  auto_summarization_enabled = Column(Boolean, default=True)

  # Timestamps
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = Column(
    DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
  )
  last_login = Column(DateTime, nullable=True)

  # Relationships
  projects = relationship(
    "Project", back_populates="user", cascade="all, delete-orphan"
  )
  conversations = relationship(
    "Conversation", back_populates="user", cascade="all, delete-orphan"
  )
  memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")

  def __repr__(self) -> str:
    return f"<User(id={self.id}, email={self.email})>"
