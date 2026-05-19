# apps/counselconduit/api/_firestore_pool.py
"""Firestore AsyncClient singleton pool.

Provides a cached AsyncClient instance to avoid creating new gRPC connections
on every request. The client is thread-safe and connection-pooled internally
by the google-cloud-firestore SDK.

Usage:
    from api._firestore_pool import get_async_client
    db = get_async_client()
    doc = await db.collection("foo").document("bar").get()
"""

from __future__ import annotations

import logging

logger = logging.getLogger("counselconduit.firestore_pool")

_async_client = None


def get_async_client():
  """Return a cached Firestore AsyncClient singleton.

  The AsyncClient maintains its own gRPC channel pool internally.
  Creating one per process and reusing it is the recommended pattern
  for Cloud Run (single-process, multi-request concurrency).
  """
  global _async_client  # noqa: PLW0603
  if _async_client is None:
    from google.cloud import firestore

    _async_client = firestore.AsyncClient()
    logger.info("Firestore AsyncClient singleton initialized")
  return _async_client
