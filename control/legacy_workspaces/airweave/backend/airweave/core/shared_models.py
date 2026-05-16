# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Shared models for the backend."""

from enum import Enum, StrEnum


class ConnectionStatus(StrEnum):
    """Connection status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class SyncJobStatus(StrEnum):
    """Sync job status enum."""

    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"  # Changed from IN_PROGRESS for consistency
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"


class IntegrationType(StrEnum):
    """Integration type enum."""

    SOURCE = "source"
    DESTINATION = "destination"
    AUTH_PROVIDER = "auth_provider"


class AirweaveFieldFlag(StrEnum):
    """Flags for AirweaveField metadata (composition over inheritance).

    These flags mark fields with semantic meaning that the entity pipeline
    extracts to populate BaseEntity fields uniformly across all sources.
    """

    IS_ENTITY_ID = "is_entity_id"
    IS_NAME = "is_name"
    IS_CREATED_AT = "is_created_at"
    IS_UPDATED_AT = "is_updated_at"
    EMBEDDABLE = "embeddable"
    UNHASHABLE = "unhashable"


class SyncStatus(StrEnum):
    """Sync status enum."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class SourceConnectionStatus(StrEnum):
    """Source connection status enum - represents overall connection state."""

    ACTIVE = "active"  # Authenticated and ready to sync
    PENDING_AUTH = "pending_auth"  # Awaiting authentication (OAuth flow, etc.)
    SYNCING = "syncing"  # Currently running a sync job
    ERROR = "error"  # Last sync failed or auth error
    INACTIVE = "inactive"  # Manually disabled
    PENDING_SYNC = "pending_sync"  # Awaiting a sync job to start


class CollectionStatus(StrEnum):
    """Collection status enum."""

    ACTIVE = "ACTIVE"
    NEEDS_SOURCE = "NEEDS SOURCE"
    ERROR = "ERROR"


class ActionType(StrEnum):
    """Action type enum."""

    ENTITIES = "entities"
    QUERIES = "queries"
    SOURCE_CONNECTIONS = "source_connections"
    TEAM_MEMBERS = "team_members"


class RateLimitLevel(StrEnum):
    """Rate limiting level for sources.

    Determines how rate limits are tracked and enforced.
    """

    ORG = "org"  # Organization-wide (all users share the limit)
    CONNECTION = "connection"  # Per-connection (each user has independent limit)


class FeatureFlag(StrEnum):
    """Available feature flags in Airweave.

    Add new flags here to enable feature gating at the organization level.
    """

    S3_DESTINATION = "s3_destination"
    PRIORITY_SUPPORT = "priority_support"
    SOURCE_RATE_LIMITING = "source_rate_limiting"


class AuthMethod(StrEnum):
    """Authentication methods used in API requests.

    Defines the valid authentication methods for API context.
    """

    AUTH0 = "auth0"  # User authentication via Auth0 JWT tokens
    API_KEY = "api_key"  # Programmatic access via API keys
    SYSTEM = "system"  # Internal system operations (local dev, migrations)
    INTERNAL_SYSTEM = "internal_system"  # Internal service-to-service calls
    STRIPE_WEBHOOK = "stripe_webhook"  # Stripe webhook handlers
    OAUTH_CALLBACK = "oauth_callback"  # OAuth callback handlers
