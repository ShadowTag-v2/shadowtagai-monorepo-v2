# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Test execution context - holds runtime state separate from configuration."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TestContext:
    """Runtime context for test execution.

    This holds all the runtime state that gets created during test execution,
    keeping it separate from the configuration.
    """

    # Core services
    bongo: Any | None = None
    airweave_client: Any | None = None

    # Infrastructure IDs
    collection_id: str | None = None
    collection_readable_id: str | None = None
    source_connection_id: str | None = None

    # Entity tracking
    created_entities: list[dict[str, Any]] = field(default_factory=list)
    updated_entities: list[dict[str, Any]] = field(default_factory=list)
    partially_deleted_entities: list[dict[str, Any]] = field(default_factory=list)
    remaining_entities: list[dict[str, Any]] = field(default_factory=list)

    # Sync tracking
    last_sync_job_id: str | None = None

    # Metrics and warnings
    metrics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
