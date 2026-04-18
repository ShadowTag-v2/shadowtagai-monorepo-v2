import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    timestamp: datetime
    role: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryInterface(ABC):
    @abstractmethod
    def add(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        pass

    @abstractmethod
    def get_context(self, limit: int = 10) -> str:
        """Retrieve recent context formatted as a string."""


class ShortTermMemory(MemoryInterface):
    """In-memory rolling buffer for active conversation context."""

    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.buffer: list[MemoryEntry] = []

    def add(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        entry = MemoryEntry(
            timestamp=datetime.now(),
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.buffer.append(entry)
        if len(self.buffer) > self.max_entries:
            self.buffer.pop(0)

    def get_context(self, limit: int = 10) -> str:
        entries = self.buffer[-limit:]
        return "\n".join([f"{e.role}: {e.content}" for e in entries])

    def clear(self) -> None:
        self.buffer = []


class LongTermMemory(MemoryInterface):
    """Interface for persistent storage (Vector DB / SQL).
    Currently a stub for future integration with Chroma/PGVector.
    """

    def __init__(self, storage_path: str = "./data/memory"):
        self.storage_path = storage_path
        # TODO: Initialize actual storage connection

    def add(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        # Stub implementation
        pass

    def get_context(self, limit: int = 10) -> str:
        # Stub implementation
        return ""


class SecureMemoryWrapper(MemoryInterface):
    """Decorator/Proxy that sanitizes inputs before storing them in the underlying memory.
    Redacts sensitive keys, emails, and PII.
    """

    def __init__(self, wrapped_memory: MemoryInterface):
        self._memory = wrapped_memory
        self._patterns = [
            (r"(sk-[a-zA-Z0-9]{20,})", "[REDACTED_API_KEY]"),
            (
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "[REDACTED_EMAIL]",
            ),
            (r"(\d{4}-\d{4}-\d{4}-\d{4})", "[REDACTED_CARD]"),
        ]

    def _sanitize(self, text: str) -> str:
        sanitized = text
        for pattern, replacement in self._patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    def add(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        clean_content = self._sanitize(content)
        self._memory.add(role, clean_content, metadata)

    def get_context(self, limit: int = 10) -> str:
        # Content in memory is already sanitized, but we pass through just in case
        return self._memory.get_context(limit)
