# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Notion-specific Pydantic schemas used for LLM structured generation."""

from pydantic import BaseModel, Field
from typing import Literal


class NotionPageSpec(BaseModel):
    title: str = Field(description="The page title")
    token: str = Field(description="Unique verification token")
    category: Literal["documentation", "guide", "reference"] = Field(default="documentation")
    tags: list[str] = Field(default_factory=list, description="Page tags")


class NotionSection(BaseModel):
    title: str = Field(description="Section heading")
    content: str = Field(description="Section content")


class NotionPageContent(BaseModel):
    introduction: str = Field(description="Page introduction")
    sections: list[NotionSection] = Field(
        description="Content sections (max 2 sections to avoid Notion block limits)",
        max_length=2,
    )
    checklist_items: list[str] = Field(
        default_factory=list,
        description="To-do items (max 3 items to avoid Notion block limits)",
        max_length=3,
    )


class NotionPage(BaseModel):
    """Schema for generating Notion page content."""

    spec: NotionPageSpec
    content: NotionPageContent
