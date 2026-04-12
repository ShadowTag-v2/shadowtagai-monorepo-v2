"""
Infrastructure mesh models.

Manages edge nodes, POPs, and distributed compute resources.
"""

import uuid
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class NodeType(StrEnum):
    """Infrastructure node type."""

    TOWER = "tower"
    POLE = "pole"
    AIRCRAFT = "aircraft"
    MARITIME = "maritime"
    VEHICLE = "vehicle"
    GROUND_STATION = "ground_station"
    BUOY = "buoy"


class NodeStatus(StrEnum):
    """Node operational status."""

    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class Node(Base):
    """
    Infrastructure node model.

    Represents individual edge compute + PNT nodes.
    """

    __tablename__ = "infrastructure_nodes"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Node classification
    node_type = Column(SQLEnum(NodeType), nullable=False, index=True)
    status = Column(SQLEnum(NodeStatus), default=NodeStatus.ONLINE, index=True)

    # Physical location
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))
    altitude_meters = Column(Integer)
    country_code = Column(String(2), index=True)
    region = Column(String(100), index=True)

    # Hardware specs
    gpu_model = Column(String(100))  # L40S, H100, etc.
    gpu_count = Column(Integer, default=1)
    ram_gb = Column(Integer)
    storage_tb = Column(Numeric(precision=5, scale=2))
    network_bandwidth_gbps = Column(Integer)

    # PNT capabilities
    has_atomic_clock = Column(Boolean, default=False)
    has_gps = Column(Boolean, default=True)
    pnt_accuracy_meters = Column(Numeric(precision=5, scale=2))

    # Network
    ip_address = Column(String(45))
    public_endpoint = Column(String(500))
    starlink_beam_id = Column(String(100), index=True)

    # Performance metrics
    current_cpu_percent = Column(Integer)
    current_gpu_percent = Column(Integer)
    current_ram_percent = Column(Integer)
    uptime_percent_30d = Column(Numeric(precision=5, scale=2))
    average_latency_ms = Column(Integer)

    # Revenue tracking
    compute_hours_30d = Column(Integer, default=0)
    revenue_cents_30d = Column(Integer, default=0)
    lifetime_revenue_cents = Column(Integer, default=0)

    # Operational
    last_heartbeat_at = Column(DateTime(timezone=True))
    firmware_version = Column(String(50))
    is_maintenance_mode = Column(Boolean, default=False)

    # Timestamps
    deployed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    pop_id = Column(String(36), ForeignKey("infrastructure_pops.id"), index=True)
    pop = relationship("EdgePop", back_populates="nodes")

    def __repr__(self):
        return f"<Node(id={self.id}, type={self.node_type}, status={self.status})>"


class EdgePop(Base):
    """
    Edge Point of Presence model.

    Groups nodes into regional compute clusters.
    """

    __tablename__ = "infrastructure_pops"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # POP metadata
    name = Column(String(200), nullable=False, unique=True, index=True)
    region = Column(String(100), nullable=False, index=True)
    country_code = Column(String(2), index=True)
    city = Column(String(100))

    # Coordinates (central point)
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))

    # Capacity
    node_count = Column(Integer, default=0)
    total_gpu_count = Column(Integer, default=0)
    total_compute_tflops = Column(Numeric(precision=10, scale=2))

    # Performance
    average_latency_ms = Column(Integer)
    uptime_percent_30d = Column(Numeric(precision=5, scale=2))

    # Revenue
    revenue_cents_30d = Column(Integer, default=0)
    lifetime_revenue_cents = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    nodes = relationship("Node", back_populates="pop", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EdgePop(id={self.id}, name={self.name}, nodes={self.node_count})>"
