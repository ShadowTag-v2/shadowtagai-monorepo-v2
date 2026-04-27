"""Asana-specific Pydantic schemas used for LLM structured generation."""

from typing import Literal

from pydantic import BaseModel, Field


class AsanaTaskSpec(BaseModel):
    title: str = Field(description="The task title - should be clear and actionable")
    token: str = Field(description="Unique verification token to embed in the content")
    priority: Literal["low", "medium", "high"] = Field(default="medium")
    tags: list[str] = Field(default_factory=list, description="Task tags/labels")


class AsanaTaskContent(BaseModel):
    description: str = Field(description="Main task description in markdown format")
    objectives: list[str] = Field(description="List of task objectives/requirements")
    technical_details: str = Field(description="Technical implementation details")
    acceptance_criteria: list[str] = Field(description="Definition of done")
    comments: list[str] = Field(description="Initial comments to add to the task")


class AsanaTask(BaseModel):
    """Schema for generating Asana task content."""

    spec: AsanaTaskSpec
    content: AsanaTaskContent
