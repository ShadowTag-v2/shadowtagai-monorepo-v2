# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pydantic schemas for API validation."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .agent_models import AgentType, ExecutionStatus


class AgentCreate(BaseModel):
    """Schema for creating an agent."""

    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(..., description="Type of agent")
    description: str | None = Field(None, description="Agent description")
    system_prompt: str = Field(..., description="System prompt for the agent")
    allowed_tools: list[str] = Field(default_factory=list, description="List of allowed tools")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentResponse(BaseModel):
    """Schema for agent response."""

    id: str
    name: str
    agent_type: AgentType
    description: str | None
    allowed_tools: list[str]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentExecuteRequest(BaseModel):
    """Schema for agent execution request."""

    task: str = Field(..., description="Task to execute")
    context: dict[str, Any] = Field(default_factory=dict, description="Execution context")
    stream: bool = Field(default=False, description="Stream the response")


class AgentExecuteResponse(BaseModel):
    """Schema for agent execution response."""

    execution_id: str
    agent_id: str
    status: ExecutionStatus
    result: Any | None = None
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    duration_seconds: int | None = None

    class Config:
        from_attributes = True


class AgentHistoryResponse(BaseModel):
    """Schema for agent execution history."""

    executions: list[AgentExecuteResponse]
    total: int
    page: int
    page_size: int


class AnalyticsMetrics(BaseModel):
    """Schema for analytics metrics."""

    metrics: dict[str, Any] = Field(..., description="Metrics to analyze")
    time_range: str | None = Field(None, description="Time range for metrics")
    dimensions: list[str] = Field(default_factory=list, description="Dimensions to analyze")


class ABTestRequest(BaseModel):
    """Schema for A/B test request."""

    test_name: str = Field(..., description="Name of the A/B test")
    variant_a: dict[str, Any] = Field(..., description="Variant A configuration")
    variant_b: dict[str, Any] = Field(..., description="Variant B configuration")
    success_metrics: list[str] = Field(..., description="Metrics to measure success")
    sample_size: int | None = Field(None, description="Required sample size")


class ViralLoopRequest(BaseModel):
    """Schema for viral loop analysis request."""

    user_actions: list[dict[str, Any]] = Field(..., description="User actions data")
    conversion_events: list[str] = Field(..., description="Conversion events to track")
    viral_coefficient_target: float | None = Field(None, description="Target viral coefficient")


class GrowthAnalysisResponse(BaseModel):
    """Schema for growth analysis response."""

    analysis_type: str
    insights: list[str]
    recommendations: list[str]
    metrics: dict[str, Any]
    visualization_data: dict[str, Any] | None = None
