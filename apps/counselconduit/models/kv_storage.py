"""
Pydantic models for the Persistent KV Storage API.

Inspired by Claude Code's memory/artifact persistence pattern
(CL4R1T4S competitive intel). Provides typed models for
tenant-scoped key-value storage backed by Firestore.

Per AGENTS.md §Security:
  - All request inputs validated with Pydantic
  - Never return raw database objects
  - Tenant isolation enforced at model level
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class KVNamespace(str, Enum):
    """Scoped namespaces for KV storage isolation."""
    SESSION = "session"          # Per-session ephemeral state
    MEMORY = "memory"            # Cross-session persistent memory
    PREFERENCE = "preference"    # User/tenant preferences
    ARTIFACT = "artifact"        # Generated artifacts (memos, attestations)
    CACHE = "cache"              # TTL-bound cache entries


class KVEntryCreate(BaseModel):
    """Request model: create or update a KV entry."""
    key: str = Field(
        ...,
        min_length=1,
        max_length=256,
        description="Unique key within the namespace",
        pattern=r"^[a-zA-Z0-9_\-\.\/]+$",
    )
    namespace: KVNamespace = Field(
        default=KVNamespace.SESSION,
        description="Storage namespace for isolation",
    )
    value: Any = Field(
        ...,
        description="JSON-serializable value to store",
    )
    ttl_seconds: int | None = Field(
        default=None,
        ge=60,
        le=2_592_000,  # max 30 days
        description="Time-to-live in seconds (None = permanent)",
    )
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Arbitrary string metadata (labels, tags)",
    )

    @field_validator("value")
    @classmethod
    def validate_value_size(cls, v: Any) -> Any:
        """Enforce max value size (1MB serialized)."""
        import json
        serialized = json.dumps(v, default=str)
        if len(serialized) > 1_048_576:
            msg = "Value exceeds 1MB serialized limit"
            raise ValueError(msg)
        return v


class KVEntryResponse(BaseModel):
    """Response model: a stored KV entry."""
    key: str
    namespace: KVNamespace
    value: Any
    tenant_id: str = Field(
        ...,
        description="Owning tenant (firm) UUID",
    )
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    version: int = Field(
        default=1,
        description="Optimistic concurrency version (Firestore generation)",
    )


class KVListRequest(BaseModel):
    """Request model: list entries in a namespace."""
    namespace: KVNamespace = Field(
        default=KVNamespace.SESSION,
        description="Namespace to list",
    )
    prefix: str | None = Field(
        default=None,
        max_length=256,
        description="Key prefix filter",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Max entries to return",
    )
    cursor: str | None = Field(
        default=None,
        description="Pagination cursor from previous response",
    )


class KVListResponse(BaseModel):
    """Response model: paginated list of KV entries."""
    entries: list[KVEntryResponse]
    next_cursor: str | None = None
    total_count: int = Field(
        ...,
        description="Total entries matching the query (not just this page)",
    )


class KVDeleteRequest(BaseModel):
    """Request model: delete a KV entry."""
    key: str = Field(
        ...,
        min_length=1,
        max_length=256,
        pattern=r"^[a-zA-Z0-9_\-\.\/]+$",
    )
    namespace: KVNamespace = Field(
        default=KVNamespace.SESSION,
    )


class KVDeleteResponse(BaseModel):
    """Response model: deletion confirmation."""
    key: str
    namespace: KVNamespace
    deleted: bool = True
    deleted_at: datetime
