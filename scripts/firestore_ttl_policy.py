#!/usr/bin/env python3
"""Configure Firestore TTL policy for tenant_quotas collection.

Item 13: Adds a TTL policy on the `updated_at` field so stale quota
documents auto-expire after 7 days.

Usage:
    python3 scripts/firestore_ttl_policy.py

Requires:
    google-cloud-firestore-admin SDK
"""

from __future__ import annotations

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "shadowtag-omega-v4"
DATABASE_ID = "(default)"
COLLECTION_ID = "tenant_quotas"
TTL_FIELD = "updated_at"


def configure_ttl_policy() -> None:
    """Create or update TTL policy on tenant_quotas.updated_at."""
    try:
        from google.cloud.firestore_admin_v1 import (
            Field,
            FirestoreAdminClient,
            UpdateFieldRequest,
        )
    except ImportError:
        logger.error("google-cloud-firestore-admin not installed. Run: pip install google-cloud-firestore-admin")
        sys.exit(1)

    client = FirestoreAdminClient()

    field_name = f"projects/{PROJECT_ID}/databases/{DATABASE_ID}/collectionGroups/{COLLECTION_ID}/fields/{TTL_FIELD}"

    field = Field(
        name=field_name,
        ttl_config=Field.TtlConfig(),  # Enable TTL on this field
    )

    request = UpdateFieldRequest(field=field)

    try:
        operation = client.update_field(request=request)
        logger.info("TTL policy update initiated: %s", operation.operation.name)

        # Wait for completion
        result = operation.result(timeout=120)
        logger.info("TTL policy configured on %s.%s", COLLECTION_ID, TTL_FIELD)
        logger.info("Field config: %s", result)

    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("TTL policy already exists on %s.%s", COLLECTION_ID, TTL_FIELD)
        else:
            logger.error("Failed to configure TTL policy: %s", e)
            raise


def verify_ttl_policy() -> None:
    """Verify TTL policy is active."""
    try:
        from google.cloud.firestore_admin_v1 import (
            FirestoreAdminClient,
            GetFieldRequest,
        )
    except ImportError:
        logger.error("google-cloud-firestore-admin not installed")
        return

    client = FirestoreAdminClient()

    field_name = f"projects/{PROJECT_ID}/databases/{DATABASE_ID}/collectionGroups/{COLLECTION_ID}/fields/{TTL_FIELD}"

    request = GetFieldRequest(name=field_name)

    try:
        field = client.get_field(request=request)
        if field.ttl_config:
            state = field.ttl_config.state.name if field.ttl_config.state else "UNKNOWN"
            logger.info("TTL policy ACTIVE on %s.%s — state: %s", COLLECTION_ID, TTL_FIELD, state)
        else:
            logger.warning("TTL policy NOT configured on %s.%s", COLLECTION_ID, TTL_FIELD)
    except Exception as e:
        logger.error("Failed to verify TTL policy: %s", e)


if __name__ == "__main__":
    configure_ttl_policy()
    verify_ttl_policy()
