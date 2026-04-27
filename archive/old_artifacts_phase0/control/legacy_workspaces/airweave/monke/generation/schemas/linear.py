from typing import Literal

from pydantic import BaseModel, Field


class LinearIssueSpec(BaseModel):
    title: str = Field(description="Issue title. MUST start with the token.")
    token: str
    priority: Literal["none", "low", "medium", "high", "urgent"] = "none"
    labels: list[str] = []


class LinearIssueContent(BaseModel):
    description: str = Field(description="Markdown description; include context and steps.")
    comments: list[str] = Field(default_factory=list, description="Seed comments")


class LinearIssue(BaseModel):
    spec: LinearIssueSpec
    content: LinearIssueContent
