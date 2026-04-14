"""SQLAlchemy models for the agent system."""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AgentType(enum.StrEnum):
    """Agent types."""

    GROWTH_ENGINEER = "growth_engineer"
    PRODUCT_STRATEGY = "product_strategy"
    DATA_ANALYST = "data_analyst"


class ExecutionStatus(enum.StrEnum):
    """Execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Agent(Base):
    """Agent model."""

    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    allowed_tools = Column(JSON, default=list)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship(
        "AgentExecution", back_populates="agent", cascade="all, delete-orphan",
    )
    tools = relationship("AgentTool", back_populates="agent", cascade="all, delete-orphan")


class AgentExecution(Base):
    """Agent execution model."""

    __tablename__ = "agent_executions"

    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    task = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    meta_data = Column(JSON, default=dict)

    # Relationships
    agent = relationship("Agent", back_populates="executions")
    results = relationship("AgentResult", back_populates="execution", cascade="all, delete-orphan")


class AgentResult(Base):
    """Agent result model."""

    __tablename__ = "agent_results"

    id = Column(String, primary_key=True)
    execution_id = Column(String, ForeignKey("agent_executions.id"), nullable=False)
    result_type = Column(String, nullable=False)  # text, json, image, etc.
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    execution = relationship("AgentExecution", back_populates="results")


class AgentTool(Base):
    """Agent tool model."""

    __tablename__ = "agent_tools"

    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    tool_name = Column(String, nullable=False)
    tool_description = Column(Text)
    input_schema = Column(JSON, default=dict)
    output_schema = Column(JSON, default=dict)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="tools")
