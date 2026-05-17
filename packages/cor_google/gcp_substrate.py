# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""GCP Substrate — Firestore + BigQuery telemetry plane."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_firestore_client = None
_bigquery_client = None


@dataclass
class SubstrateConfig:
  """GCP Substrate configuration."""

  project_id: str = field(
    default_factory=lambda: os.environ.get("GCP_PROJECT_ID", "shadowtag-omega-v4")
  )
  firestore_collection: str = "ag_ui_events"
  bigquery_dataset: str = "shadowtag_telemetry"
  bigquery_table: str = "ag_ui_event_log"
  cached_content_ttl_hours: int = 24
  enable_firestore: bool = True
  enable_bigquery: bool = True
  dry_run: bool = field(
    default_factory=lambda: os.environ.get("SUBSTRATE_DRY_RUN", "0") == "1"
  )


class GCPSubstrate:
  """GCP data plane for AG-UI events."""

  def __init__(self, config: SubstrateConfig | None = None) -> None:
    self.config = config or SubstrateConfig()
    self._write_count = 0
    self._error_count = 0

  def _get_firestore_client(self):
    global _firestore_client  # noqa: PLW0603
    if _firestore_client is None and not self.config.dry_run:
      try:
        from google.cloud import firestore

        _firestore_client = firestore.Client(project=self.config.project_id)
      except Exception as e:
        logger.warning("Firestore unavailable: %s", e)
    return _firestore_client

  def _get_bigquery_client(self):
    global _bigquery_client  # noqa: PLW0603
    if _bigquery_client is None and not self.config.dry_run:
      try:
        from google.cloud import bigquery

        _bigquery_client = bigquery.Client(project=self.config.project_id)
      except Exception as e:
        logger.warning("BigQuery unavailable: %s", e)
    return _bigquery_client

  def write_event(self, event_dict: dict[str, Any]) -> bool:
    if self.config.dry_run:
      self._write_count += 1
      return True
    success = False
    if self.config.enable_firestore:
      success = self._write_firestore(event_dict) or success
    if self.config.enable_bigquery:
      success = self._write_bigquery(event_dict) or success
    self._write_count += 1 if success else 0
    self._error_count += 0 if success else 1
    return success

  def _write_firestore(self, event_dict: dict[str, Any]) -> bool:
    client = self._get_firestore_client()
    if not client:
      return False
    try:
      doc_ref = client.collection(self.config.firestore_collection).document(
        event_dict.get("event_id", str(time.time_ns()))
      )
      doc_ref.set(event_dict)
      return True
    except Exception as e:
      logger.error("Firestore write failed: %s", e)
      return False

  def _write_bigquery(self, event_dict: dict[str, Any]) -> bool:
    client = self._get_bigquery_client()
    if not client:
      return False
    try:
      table = f"{self.config.project_id}.{self.config.bigquery_dataset}.{self.config.bigquery_table}"
      errors = client.insert_rows_json(table, [event_dict])
      return not errors
    except Exception as e:
      logger.error("BigQuery write failed: %s", e)
      return False

  def read_agent_card(self, agent_id: str) -> dict[str, Any] | None:
    client = self._get_firestore_client()
    if not client:
      return None
    try:
      doc = client.collection("agent_cards").document(agent_id).get()
      return doc.to_dict() if doc.exists else None
    except Exception as e:
      logger.error("Agent card read failed: %s", e)
      return None

  def write_agent_card(self, agent_id: str, card: dict[str, Any]) -> bool:
    client = self._get_firestore_client()
    if not client:
      return False
    try:
      client.collection("agent_cards").document(agent_id).set(card, merge=True)
      return True
    except Exception as e:
      logger.error("Agent card write failed: %s", e)
      return False

  def get_cached_content_slab(self, slab_key: str) -> dict[str, Any] | None:
    client = self._get_firestore_client()
    if not client:
      return None
    try:
      doc = client.collection("cached_content_slabs").document(slab_key).get()
      if not doc.exists:
        return None
      slab = doc.to_dict()
      ttl_ns = self.config.cached_content_ttl_hours * 3600 * 1_000_000_000
      if time.time_ns() - slab.get("created_ns", 0) > ttl_ns:
        return None
      return slab
    except Exception as e:
      logger.error("Slab read failed: %s", e)
      return None

  def write_cached_content_slab(
    self, slab_key: str, content: str, metadata: dict[str, Any] | None = None
  ) -> bool:
    client = self._get_firestore_client()
    if not client:
      return False
    try:
      client.collection("cached_content_slabs").document(slab_key).set(
        {
          "slab_key": slab_key,
          "content": content,
          "metadata": metadata or {},
          "created_ns": time.time_ns(),
          "ttl_hours": self.config.cached_content_ttl_hours,
        }
      )
      return True
    except Exception as e:
      logger.error("Slab write failed: %s", e)
      return False

  @property
  def stats(self) -> dict[str, Any]:
    return {
      "write_count": self._write_count,
      "error_count": self._error_count,
      "project_id": self.config.project_id,
      "dry_run": self.config.dry_run,
    }
