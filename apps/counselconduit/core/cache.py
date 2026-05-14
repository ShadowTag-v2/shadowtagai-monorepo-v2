# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Proprietary

"""Firestore Cache Core Module for CounselConduit.

Replaces Redis Memorystore with a stateless Firestore-based cache using TTL indexes.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta, timezone

from .firebase_admin import get_firestore

logger = logging.getLogger(__name__)

# Default TTL of 60 seconds for request-scoped caching
DEFAULT_TTL = 60
CACHE_COLLECTION = "counselconduit_cache"


class FirestoreCache:
  """Centralized Firestore cache replacing Redis for stateless Cloud Run environment."""

  @classmethod
  def get_client(cls):
    """Get the singleton Firestore client."""
    return get_firestore()

  @classmethod
  def set(cls, key: str, value: str, ttl: int = DEFAULT_TTL) -> None:
    """Set a value in the cache with the default TTL."""
    try:
      client = cls.get_client()
      expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
      doc_ref = client.collection(CACHE_COLLECTION).document(key)
      doc_ref.set({"value": value, "expiresAt": expires_at})
    except Exception as e:
      logger.error(f"Failed to set cache key {key}: {e}")

  @classmethod
  def get(cls, key: str) -> Optional[str]:
    """Get a value from the cache."""
    try:
      client = cls.get_client()
      doc_ref = client.collection(CACHE_COLLECTION).document(key)
      doc = doc_ref.get()
      if doc.exists:
        data = doc.to_dict()
        expires_at = data.get("expiresAt")

        # Manual TTL check in case Firestore TTL sweep hasn't run yet
        if expires_at and expires_at < datetime.now(timezone.utc):
          cls.delete(key)
          return None

        return data.get("value")
    except Exception as e:
      logger.error(f"Failed to get cache key {key}: {e}")
    return None

  @classmethod
  def delete(cls, key: str) -> None:
    """Delete a value from the cache."""
    try:
      client = cls.get_client()
      client.collection(CACHE_COLLECTION).document(key).delete()
    except Exception as e:
      logger.error(f"Failed to delete cache key {key}: {e}")


def get_cache():
  """Dependency injection helper for FastAPI."""
  return FirestoreCache
