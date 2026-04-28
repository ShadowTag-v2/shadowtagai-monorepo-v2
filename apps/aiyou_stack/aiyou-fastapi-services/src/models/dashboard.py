# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Dashboard models for creating analytics dashboards"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class Dashboard(Base):
    """Dashboard model for organizing analytics views"""

    __tablename__ = "dashboards"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Dashboard identification
    name = Column(String(255), nullable=False)
    description = Column(String(1000))

    # Dashboard configuration
    is_public = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)

    # Layout configuration
    layout = Column(JSON, default={})  # Grid layout configuration

    # Ownership
    created_by = Column(String(255))
    tags = Column(JSON, default=[])

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    widgets = relationship(
        "DashboardWidget",
        back_populates="dashboard",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Dashboard(name={self.name})>"


class DashboardWidget(Base):
    """Dashboard widget model for individual analytics visualizations"""

    __tablename__ = "dashboard_widgets"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    dashboard_id = Column(
        UUID(as_uuid=True),
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Widget identification
    title = Column(String(255), nullable=False)
    description = Column(String(500))

    # Widget configuration
    widget_type = Column(String(100), nullable=False)  # chart, table, metric, funnel, etc.
    visualization_type = Column(String(100))  # line, bar, pie, area, etc.

    # Query configuration
    metric_type = Column(String(100))  # event_count, user_count, conversion_rate, etc.
    event_filters = Column(JSON, default={})
    time_range = Column(String(50))  # 7d, 30d, 90d, custom
    group_by = Column(JSON, default=[])  # Fields to group by

    # Display configuration
    position = Column(JSON, default={})  # x, y, width, height
    chart_config = Column(JSON, default={})  # Chart-specific configuration

    # Data refresh
    refresh_interval_seconds = Column(Integer, default=300)  # 5 minutes default
    last_refreshed = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

    def __repr__(self):
        return f"<DashboardWidget(title={self.title}, widget_type={self.widget_type})>"
