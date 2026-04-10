from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CodeDecision(BaseModel):
    """Represents a decision made by an Agent or Judge."""

    decision_id: str = Field(..., description="Unique ID of the decision")
    timestamp: datetime = Field(default_factory=datetime.now)
    query: str = Field(..., description="The problem or prompt")
    context_hash: str = Field(..., description="Hash of the file/context being acted upon")
    decision: str = Field(..., description="The verdict or code generated")
    reasoning: str = Field(..., description="Judge 6 reasoning")
    outcome: str = Field(..., description="Did it work? (PASS/FAIL)")
    tags: list[str] = Field(default_factory=list)


class DesignPattern(BaseModel):
    """A learned pattern to be recalled later."""

    pattern_name: str
    description: str
    code_example: str
    anti_pattern: str | None = None
    use_cases: list[str]


class MemoryItem(BaseModel):
    """The unit of storage for Vertex Vector Search."""

    id: str
    text_content: str
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
