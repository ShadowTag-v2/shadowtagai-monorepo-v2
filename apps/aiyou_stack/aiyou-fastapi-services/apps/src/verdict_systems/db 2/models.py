"""
Verdict Systems - SQLAlchemy Database Models
PostgreSQL schema for production deployment
"""

import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ============================================================================
# Enums (mirrored from core.enums for database)
# ============================================================================


class UrgencyLevelDB(enum.StrEnum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    CRITICAL = "critical"


class TaskStatusDB(enum.StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class VerticalTypeDB(enum.StrEnum):
    FAMILY = "family"
    SCHOOL = "school"
    WORKPLACE = "workplace"
    MEDICAL = "medical"
    SENIOR = "senior"
    TRANSPORTATION = "transportation"
    SMART_HOME = "smart_home"


# ============================================================================
# Database Models
# ============================================================================


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False)  # admin, parent, teacher, student, etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime)

    # Settings
    settings = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    # Relationships
    tasks = relationship("TaskDB", back_populates="user", foreign_keys="TaskDB.user_id")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
    )


class TaskDB(Base):
    """Task model with urgency and lockout"""

    __tablename__ = "tasks"

    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    deadline = Column(DateTime, nullable=False)
    estimated_duration_minutes = Column(Integer, default=30)

    # Urgency
    priority = Column(Integer, default=3)  # 1-6
    urgency_level = Column(Enum(UrgencyLevelDB), default=UrgencyLevelDB.GREEN)

    # Status
    status = Column(Enum(TaskStatusDB), default=TaskStatusDB.PENDING, nullable=False)
    completion_method = Column(String(50))
    completed_at = Column(DateTime)

    # Assignment
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    vertical = Column(Enum(VerticalTypeDB), nullable=False)
    group_id = Column(String(50))

    # Lockout
    enable_lockout = Column(Boolean, default=False)
    lockout_grace_minutes = Column(Integer, default=15)
    blocked_apps = Column(JSON, default=list)

    # AI & Approval
    ai_tutor_enabled = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    approver_id = Column(String(50), ForeignKey("users.id"))

    # Metadata
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    notifications_sent = Column(JSON, default=list)

    # Relationships
    user = relationship("User", back_populates="tasks", foreign_keys=[user_id])

    __table_args__ = (
        Index("idx_tasks_user_id", "user_id"),
        Index("idx_tasks_deadline", "deadline"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_urgency", "urgency_level"),
        Index("idx_tasks_vertical", "vertical"),
        Index("idx_tasks_user_status", "user_id", "status"),
    )


class Notification(Base):
    """Notification log"""

    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(50), ForeignKey("tasks.id"))

    notification_type = Column(String(50), nullable=False)
    title = Column(String(200))
    message = Column(Text)

    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)

    delivery_method = Column(String(50))  # push, email, sms, voice
    metadata = Column(JSON, default=dict)

    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_task_id", "task_id"),
        Index("idx_notifications_sent_at", "sent_at"),
    )


class LockoutEvent(Base):
    """Lockout event log"""

    __tablename__ = "lockout_events"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(50), ForeignKey("tasks.id"), nullable=False)
    device_id = Column(String(50))

    activated_at = Column(DateTime, default=datetime.utcnow)
    deactivated_at = Column(DateTime)

    lockout_mode = Column(String(50))
    blocked_apps = Column(JSON, default=list)

    override_by = Column(String(50), ForeignKey("users.id"))
    override_reason = Column(Text)

    metadata = Column(JSON, default=dict)

    __table_args__ = (
        Index("idx_lockout_user_id", "user_id"),
        Index("idx_lockout_task_id", "task_id"),
        Index("idx_lockout_activated", "activated_at"),
    )


class AISession(Base):
    """AI tutor session log"""

    __tablename__ = "ai_sessions"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(50), ForeignKey("tasks.id"))

    session_type = Column(String(50), default="tutor")  # tutor, coach, planner
    subject = Column(String(100))

    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

    messages = Column(JSON, default=list)
    hints_given = Column(Integer, default=0)
    full_solutions_shown = Column(Boolean, default=False)

    metadata = Column(JSON, default=dict)

    __table_args__ = (
        Index("idx_ai_sessions_user_id", "user_id"),
        Index("idx_ai_sessions_task_id", "task_id"),
    )


class FamilyGroup(Base):
    """Family/group model"""

    __tablename__ = "family_groups"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    group_type = Column(String(50), default="family")  # family, class, team, etc.

    admin_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    members = Column(JSON, default=list)  # List of user IDs

    settings = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_family_groups_admin", "admin_id"),)
