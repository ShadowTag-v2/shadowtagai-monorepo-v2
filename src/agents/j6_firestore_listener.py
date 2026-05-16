# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Judge 6 Firestore Listener — Real-Time Risk Scoring via Firestore.

Bridges the Judge 6 Sentinel to Cloud Firestore for:
  1. Persisting sentinel decisions to the `j6_decisions` collection
  2. Reading operational risk metadata from `j6_risk_config`
  3. Streaming real-time decision updates via Firestore snapshots

Architecture follows the tengu_j6_bridge.py pattern: Python-side logic
delegates to Firestore via the Firebase MCP server, maintaining the
MCP-first routing invariant from AGENTS.md.

Usage::
    listener = J6FirestoreListener(sentinel)
    await listener.persist_decision(decision)
    config = await listener.load_risk_config()
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agents.judge6_sentinel import (
  Judge6Sentinel,
  SentinelDecision,
)

logger = logging.getLogger("j6-firestore")

# Firestore collection paths
DECISIONS_COLLECTION = "j6_decisions"
RISK_CONFIG_COLLECTION = "j6_risk_config"
RISK_CONFIG_DOC = "active_config"

# Disk cache path (for offline/fallback operation per tengu_j6_bridge.py pattern)
CACHE_DIR = Path("/tmp/j6_cache")


@dataclass
class J6RiskConfig:
  """Operational risk configuration loaded from Firestore."""

  max_auto_promote_per_hour: int = 50
  escalation_threshold: float = 0.3  # % regression triggers auto-escalation
  board_quorum_size: int = 5  # Minimum board members for STATE B quorum
  catastrophic_keywords: list[str] = field(
    default_factory=lambda: [
      "database migration",
      "auth change",
      "payment",
      "force push",
      "history rewrite",
    ]
  )
  updated_at: float = field(default_factory=time.time)


class J6FirestoreListener:
  """Bridges Judge 6 Sentinel to Cloud Firestore.

  This class does NOT call Firestore directly — it produces MCP execution
  plans (like Kosmos) that the Antigravity orchestrator executes via the
  firebase-mcp-server. For local testing, decisions are cached to disk.
  """

  def __init__(
    self,
    sentinel: Judge6Sentinel | None = None,
    project_id: str = "shadowtag-omega-v4",
    database_id: str = "(default)",
  ) -> None:
    self.sentinel = sentinel or Judge6Sentinel()
    self._project_id = project_id
    self._database_id = database_id
    self._config: J6RiskConfig = J6RiskConfig()
    self._pending_writes: list[dict[str, Any]] = []
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("⚖️ J6 Firestore Listener initialized (project=%s)", project_id)

  def decision_to_firestore_doc(self, decision: SentinelDecision) -> dict[str, Any]:
    """Convert a SentinelDecision to a Firestore document payload."""
    return {
      "fields": {
        "decision_id": {"stringValue": decision.decision_id},
        "source": {"stringValue": decision.source},
        "verdict": {"stringValue": decision.verdict.value},
        "risk_severity": {"stringValue": decision.risk_severity.value},
        "rationale": {"stringValue": decision.rationale},
        "board_synthesis": {
          "stringValue": json.dumps(decision.board_synthesis)
          if decision.board_synthesis
          else ""
        },
        "metadata": {"stringValue": json.dumps(decision.metadata)},
        "timestamp": {"doubleValue": decision.timestamp},
      }
    }

  def plan_persist_decision(self, decision: SentinelDecision) -> dict[str, Any]:
    """Produce an MCP execution plan to persist a decision to Firestore.

    Returns a dict with the MCP tool call specification that the
    Antigravity orchestrator will execute.
    """
    parent = f"projects/{self._project_id}/databases/{self._database_id}/documents"
    doc = self.decision_to_firestore_doc(decision)

    plan = {
      "agent": "j6_firestore_listener",
      "action": "persist_decision",
      "mcp_call": {
        "server": "firebase-mcp-server",
        "tool": "firestore_add_document",
        "args": {
          "parent": parent,
          "collectionId": DECISIONS_COLLECTION,
          "documentId": decision.decision_id,
          "document": doc,
        },
      },
    }

    # Also cache locally (tengu pattern: disk fallback)
    self._cache_decision(decision)
    self._pending_writes.append(plan)

    logger.info(
      "⚖️ Planned Firestore write for decision %s (verdict=%s)",
      decision.decision_id,
      decision.verdict.value,
    )
    return plan

  def plan_load_risk_config(self) -> dict[str, Any]:
    """Produce an MCP execution plan to load risk config from Firestore."""
    return {
      "agent": "j6_firestore_listener",
      "action": "load_risk_config",
      "mcp_call": {
        "server": "firebase-mcp-server",
        "tool": "firestore_get_document",
        "args": {
          "name": (
            f"projects/{self._project_id}"
            f"/databases/{self._database_id}"
            f"/documents/{RISK_CONFIG_COLLECTION}/{RISK_CONFIG_DOC}"
          ),
        },
      },
    }

  def apply_risk_config(self, firestore_response: dict[str, Any]) -> J6RiskConfig:
    """Parse Firestore document response into J6RiskConfig.

    Called by the orchestrator after executing the MCP plan.
    """
    fields = firestore_response.get("fields", {})
    config = J6RiskConfig(
      max_auto_promote_per_hour=int(
        fields.get("max_auto_promote_per_hour", {}).get("integerValue", 50)
      ),
      escalation_threshold=float(
        fields.get("escalation_threshold", {}).get("doubleValue", 0.3)
      ),
      board_quorum_size=int(fields.get("board_quorum_size", {}).get("integerValue", 5)),
    )

    keywords_raw = fields.get("catastrophic_keywords", {}).get("stringValue", "")
    if keywords_raw:
      try:
        config.catastrophic_keywords = json.loads(keywords_raw)
      except json.JSONDecodeError:
        pass

    self._config = config
    logger.info(
      "⚖️ Risk config loaded from Firestore (threshold=%.1f%%)",
      config.escalation_threshold * 100,
    )
    return config

  def _cache_decision(self, decision: SentinelDecision) -> None:
    """Cache decision to disk (tengu_j6_bridge.py pattern)."""
    cache_file = CACHE_DIR / f"{decision.decision_id}.json"
    doc = {
      "decision_id": decision.decision_id,
      "source": decision.source,
      "verdict": decision.verdict.value,
      "risk_severity": decision.risk_severity.value,
      "rationale": decision.rationale,
      "timestamp": decision.timestamp,
    }
    try:
      cache_file.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    except OSError as e:
      logger.warning("Cache write failed: %s", e)

  def get_cached_decisions(self, limit: int = 20) -> list[dict[str, Any]]:
    """Read cached decisions from disk (for offline/recovery)."""
    decisions = []
    cache_files = sorted(CACHE_DIR.glob("j6_*.json"), reverse=True)[:limit]
    for f in cache_files:
      try:
        decisions.append(json.loads(f.read_text(encoding="utf-8")))
      except (OSError, json.JSONDecodeError) as e:
        logger.warning("Cache read failed for %s: %s", f.name, e)
    return decisions

  def get_pending_writes(self) -> list[dict[str, Any]]:
    """Return pending Firestore write plans (for orchestrator consumption)."""
    return list(self._pending_writes)

  def clear_pending_writes(self) -> None:
    """Clear pending writes after orchestrator confirms execution."""
    self._pending_writes.clear()

  def get_diagnostics(self) -> dict[str, Any]:
    """Return listener diagnostics."""
    return {
      "listener": "j6_firestore",
      "project_id": self._project_id,
      "pending_writes": len(self._pending_writes),
      "cached_decisions": len(list(CACHE_DIR.glob("j6_*.json"))),
      "config": {
        "max_auto_promote": self._config.max_auto_promote_per_hour,
        "escalation_threshold": self._config.escalation_threshold,
        "board_quorum": self._config.board_quorum_size,
      },
      "sentinel": self.sentinel.get_diagnostics(),
    }
