from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class StreamEvent(BaseModel):
    """The Atomic Unit of the Universal Tape.
    Every action, thought, or data point is normalized into this structure.
    """

    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    source_type: Literal["web", "ironwood", "monkey", "memory", "human"]
    source_id: str = Field(..., description="Agent ID, Process ID, or User Name")

    # Context (The "Where")
    location: str = Field("global", description="File path, URL, or System Component")

    # Payload (The "What")
    event_type: str = Field(..., description="e.g., 'thought', 'scrape', 'compile_error', 'metric'")
    content: Any = Field(..., description="The raw data or message")

    # Tags (For future filtering if needed, though indexless is preferred)
    tags: list[str] = Field(default_factory=list)

    def to_jsonl(self) -> str:
        """Render to single-line JSON for the Tape."""
        return self.model_dump_json()
