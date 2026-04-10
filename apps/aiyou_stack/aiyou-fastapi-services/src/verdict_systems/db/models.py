"""
Verdict Systems - SQLAlchemy Database Models
PostgreSQL schema for production deployment
"""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

from ..enums import (
    CompletionMethod,
    LockoutMode,
    NotificationType,
    PriorityLevel,
    TaskStatus,
    UserRole,
    VerticalType,
)

Base = declarative_base()


class FamilyGroup(Base):
    __tablename__ = "family_groups"
    id = Column(String, primary_key=True)
    name = Column(String)
    admin_id = Column(String)  # Points to primary parent User ID


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    family_group_id = Column(String, ForeignKey("family_groups.id"), nullable=True)

    tasks = relationship("TaskDB", back_populates="assigned_to")


class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    deadline = Column(DateTime(timezone=True))
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    vertical = Column(Enum(VerticalType))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)

    metadata_json = Column(JSON, default={})

    # Lockout
    lockout_mode = Column(Enum(LockoutMode), default=LockoutMode.NONE)
    blocked_apps = Column(JSON, default=[])

    # Completion
    completion_method = Column(Enum(CompletionMethod), default=CompletionMethod.CHECKBOX)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    proof_url = Column(String, nullable=True)

    assigned_to_id = Column(String, ForeignKey("users.id"))
    assigned_to = relationship("User", back_populates="tasks")
    assigned_by_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    type = Column(Enum(NotificationType))
    message = Column(String)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LockoutEvent(Base):
    __tablename__ = "lockout_events"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    task_id = Column(String, ForeignKey("tasks.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    override_reason = Column(String, nullable=True)


class AISession(Base):
    __tablename__ = "ai_sessions"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey("tasks.id"))
    user_id = Column(String, ForeignKey("users.id"))
    transcript = Column(JSON)  # List of messages
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
