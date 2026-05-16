# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Trello-specific Pydantic schemas used for LLM structured generation."""

from pydantic import BaseModel, Field
from typing import Literal


class TrelloCardSpec(BaseModel):
  """Metadata for card generation."""

  title: str = Field(description="The card title - should be clear and actionable")
  token: str = Field(description="Unique verification token to embed in the content")
  priority: Literal["low", "medium", "high", "urgent"] = Field(default="medium")
  labels: list[str] = Field(
    default_factory=list,
    description="Label names for the card (e.g., 'Bug', 'Feature')",
  )


class TrelloCardContent(BaseModel):
  """Content for generated card."""

  description: str = Field(
    description="Main card description in markdown format with verification token"
  )
  objectives: list[str] = Field(
    description="List of objectives/requirements for this card"
  )
  technical_details: str = Field(description="Technical implementation details")
  acceptance_criteria: list[str] = Field(
    description="Definition of done checklist items"
  )


class TrelloCard(BaseModel):
  """Schema for generating Trello card content."""

  spec: TrelloCardSpec
  content: TrelloCardContent


class TrelloChecklistItem(BaseModel):
  """A single item in a checklist."""

  name: str = Field(description="The checklist item text")
  checked: bool = Field(default=False, description="Whether the item is checked")


class TrelloChecklistContent(BaseModel):
  """Content for generated checklist."""

  name: str = Field(description="Name of the checklist")
  items: list[TrelloChecklistItem] = Field(description="List of checklist items")
