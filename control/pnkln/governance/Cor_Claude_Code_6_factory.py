# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cor_Claude_Code_6Engine factory — wires RKILL notifier from environment.

Environment variables:
    GCP_PROJECT          — GCP project ID (required for live RKILL)
    RKILL_KMS_KEY_NAME   — Full KMS key version resource name
                           projects/<p>/locations/<l>/keyRings/<kr>/cryptoKeys/<k>/cryptoKeyVersions/<v>
    RKILL_ARMOR_POLICY   — Cloud Armor security policy name
    RKILL_ARMOR_PRIORITY — Rule priority for deny-all insertion (default: 1000)
    RKILL_DRY_RUN        — "true" to log without touching GCP (default: "true")

Usage::

    from control.pnkln.governance.Cor_Claude_Code_6_factory import build_engine

    engine = build_engine()        # reads env, RKILL wired in
    engine_dry = build_engine(dry_run=True)   # explicit override

    # or in a FastAPI lifespan:
    app.state.Cor_Claude_Code_6 = build_engine()
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable

from .Cor_Claude_Code_6_core import GovernanceDecision, Cor_Claude_Code_6Engine
from .Cor_Claude_Code_6_rkill_bridge import RkillNotifier
from .rkill import RkillConfig

logger = logging.getLogger("Cor_Claude_Code_6_factory")


def _str_to_bool(val: str) -> bool:
  return val.strip().lower() in {"1", "true", "yes"}


def build_engine(
  dry_run: bool | None = None,
  audit_callback: Callable[[GovernanceDecision], None] | None = None,
) -> Cor_Claude_Code_6Engine:
  """Build a Cor_Claude_Code_6Engine with RKILL auto-lockout wired to ceo_notifier.

  Args:
      dry_run: Override RKILL_DRY_RUN env var. If None, reads from env
               (defaults True so accidental prod runs don't kill infra).
      audit_callback: Optional audit sink (e.g. write to BigQuery).

  Returns:
      Configured Cor_Claude_Code_6Engine ready for production use.
  """
  project = os.environ.get("GCP_PROJECT", "")
  kms_key_name = os.environ.get("RKILL_KMS_KEY_NAME", "")
  armor_policy = os.environ.get("RKILL_ARMOR_POLICY", "")
  armor_priority = int(os.environ.get("RKILL_ARMOR_PRIORITY", "1000"))

  env_dry_run = _str_to_bool(os.environ.get("RKILL_DRY_RUN", "true"))
  effective_dry_run = dry_run if dry_run is not None else env_dry_run

  if not effective_dry_run and not all([project, kms_key_name, armor_policy]):
    missing = [
      v
      for v, val in [
        ("GCP_PROJECT", project),
        ("RKILL_KMS_KEY_NAME", kms_key_name),
        ("RKILL_ARMOR_POLICY", armor_policy),
      ]
      if not val
    ]
    raise OSError(
      f"RKILL_DRY_RUN=false but required env vars not set: {missing}. Set them or set RKILL_DRY_RUN=true."
    )

  cfg = RkillConfig(
    project=project,
    kms_key_name=kms_key_name,
    armor_policy=armor_policy,
    armor_rule_priority=armor_priority,
    trigger_reason="Cor_Claude_Code_6 L5_LOCKOUT auto-triggered",
    dry_run=effective_dry_run,
  )

  notifier = RkillNotifier(cfg)

  logger.info(
    "[Cor_Claude_Code_6_factory] engine built: rkill_dry_run=%s project=%s armor_policy=%s",
    effective_dry_run,
    project or "(unset)",
    armor_policy or "(unset)",
  )

  return Cor_Claude_Code_6Engine(
    ceo_notifier=notifier,
    audit_callback=audit_callback,
  )
