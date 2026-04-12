"""Funnel models for conversion tracking"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Funnel(Base):
    """Funnel model for defining conversion funnels"""

    __tablename__ = "funnels"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Funnel identification
    name = Column(String(255), nullable=False)
    description = Column(String(1000))

    # Funnel configuration
    is_active = Column(Boolean, default=True)
    time_window_hours = Column(Integer, default=24)  # Time window for completing funnel

    # Metadata
    created_by = Column(String(255))
    tags = Column(JSON, default=[])

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    steps = relationship("FunnelStep", back_populates="funnel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Funnel(name={self.name})>"


class FunnelStep(Base):
    """Funnel step model for defining steps in a conversion funnel"""

    __tablename__ = "funnel_steps"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    funnel_id = Column(
        UUID(as_uuid=True), ForeignKey("funnels.id", ondelete="CASCADE"), nullable=False
    )

    # Step configuration
    step_order = Column(Integer, nullable=False)
    event_name = Column(String(255), nullable=False)
    event_filters = Column(JSON, default={})  # Additional filters for the event

    # Step metadata
    name = Column(String(255))
    description = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    funnel = relationship("Funnel", back_populates="steps")

    def __repr__(self):
        return f"<FunnelStep(funnel_id={self.funnel_id}, step_order={self.step_order}, event_name={self.event_name})>"


class UserFunnelProgress(Base):
    """Track user progress through funnels"""

    __tablename__ = "user_funnel_progress"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    funnel_id = Column(
        UUID(as_uuid=True), ForeignKey("funnels.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # User identification
    user_id = Column(String(255), index=True, nullable=False)
    session_id = Column(String(255), index=True)

    # Progress tracking
    current_step = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    dropped_at_step = Column(Integer)

    # Step timestamps
    step_timestamps = Column(JSON, default={})  # Maps step_order to timestamp

    # Completion metrics
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    time_to_complete_seconds = Column(Float)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserFunnelProgress(funnel_id={self.funnel_id}, user_id={self.user_id}, current_step={self.current_step})>"
