# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""OneNote-specific generation schema."""

from pydantic import BaseModel, Field


class OneNotePage(BaseModel):
    """Schema for OneNote page generation."""

    title: str = Field(description="Page title")
    content: str = Field(description="Page content in HTML format")
