# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""RKILL — Emergency AI Safety Kill Protocol (Patent Claim #7).

Two-phase coordinated lockout:
  Phase 1 — Disable Cloud KMS key version (renders all ciphertext inaccessible).
  Phase 2 — Insert Cloud Armor deny-all rule (drops inbound HTTP/HTTPS at WAF).

Both phases run concurrently via asyncio.gather.
On dry_run=True, logs intent without touching GCP.

Required IAM roles on the service account:
  roles/cloudkms.admin        — to disable key versions
  roles/compute.securityAdmin — to patch Cloud Armor security policy

Usage::

    from control.pnkln.governance.rkill import RkillConfig, RkillProtocol

    cfg = RkillConfig(
        project=os.environ["GCP_PROJECT"],
        kms_key_name="projects/my-proj/locations/global/keyRings/kr/cryptoKeys/k/cryptoKeyVersions/1",
        armor_policy="lawtrack-api-prod-policy",
        trigger_reason="RAISE_ACT_FRONTIER violation — automated lockout",
    )
    result = await RkillProtocol(cfg).execute(triggered_by="Cor.Claude_Code_6-auto")
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger("rkill")


@dataclass
class RkillConfig:
    project: str
    kms_key_name: str  # full resource: projects/.../cryptoKeyVersions/N
    armor_policy: str  # Cloud Armor security policy name
    armor_rule_priority: int = 1000  # priority for the inserted deny-all rule
    trigger_reason: str = ""
    dry_run: bool = False


@dataclass
class RkillResult:
    success: bool
    triggered_by: str
    kms_disabled: bool = False
    armor_blocked: bool = False
    errors: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0


class RkillProtocol:
    """Coordinated GCP lockout: KMS disable + Cloud Armor deny-all."""

    def __init__(self, cfg: RkillConfig) -> None:
        self.cfg = cfg

    async def execute(self, triggered_by: str) -> RkillResult:
        t0 = time.perf_counter()
        result = RkillResult(success=False, triggered_by=triggered_by)

        if self.cfg.dry_run:
            logger.warning(
                "[RKILL DRY-RUN] Would disable kms=%s and block armor=%s. Reason: %s",
                self.cfg.kms_key_name,
                self.cfg.armor_policy,
                self.cfg.trigger_reason,
            )
            result.kms_disabled = True
            result.armor_blocked = True
            result.success = True
            result.duration_ms = round((time.perf_counter() - t0) * 1000, 3)
            return result

        kms_task = asyncio.create_task(self._disable_kms_key())
        armor_task = asyncio.create_task(self._insert_armor_deny_rule())
        kms_out, armor_out = await asyncio.gather(kms_task, armor_task, return_exceptions=True)

        if isinstance(kms_out, Exception):
            result.errors.append(f"KMS disable failed: {kms_out}")
        else:
            result.kms_disabled = bool(kms_out)

        if isinstance(armor_out, Exception):
            result.errors.append(f"Cloud Armor block failed: {armor_out}")
        else:
            result.armor_blocked = bool(armor_out)

        result.success = result.kms_disabled and result.armor_blocked
        result.duration_ms = round((time.perf_counter() - t0) * 1000, 3)

        logger.critical(
            "[RKILL] triggered_by=%s kms=%s armor=%s success=%s reason=%s duration_ms=%s",
            triggered_by,
            result.kms_disabled,
            result.armor_blocked,
            result.success,
            self.cfg.trigger_reason,
            result.duration_ms,
        )
        return result

    async def _disable_kms_key(self) -> bool:
        from google.cloud import kms_v1  # type: ignore[import]

        client = kms_v1.KeyManagementServiceAsyncClient()
        request = kms_v1.UpdateCryptoKeyVersionRequest(
            crypto_key_version=kms_v1.CryptoKeyVersion(
                name=self.cfg.kms_key_name,
                state=kms_v1.CryptoKeyVersion.CryptoKeyVersionState.DISABLED,
            ),
            update_mask={"paths": ["state"]},
        )
        await client.update_crypto_key_version(request)
        logger.critical("[RKILL] KMS key disabled: %s", self.cfg.kms_key_name)
        return True

    async def _insert_armor_deny_rule(self) -> bool:
        from google.cloud import compute_v1  # type: ignore[import]

        client = compute_v1.SecurityPoliciesClient()
        rule = compute_v1.SecurityPolicyRule(
            priority=self.cfg.armor_rule_priority,
            description=f"RKILL emergency deny — {self.cfg.trigger_reason[:200]}",
            match=compute_v1.SecurityPolicyRuleMatcher(
                versioned_expr=(compute_v1.SecurityPolicyRuleMatcher.VersionedExpr.SRC_IPS_V1),
                config=compute_v1.SecurityPolicyRuleMatcherConfig(src_ip_ranges=["*"]),
            ),
            action="deny(403)",
        )
        client.add_rule(
            request=compute_v1.AddRuleSecurityPolicyRequest(
                project=self.cfg.project,
                security_policy=self.cfg.armor_policy,
                security_policy_rule_resource=rule,
            )
        )
        logger.critical(
            "[RKILL] Cloud Armor deny-all rule inserted: policy=%s priority=%s",
            self.cfg.armor_policy,
            self.cfg.armor_rule_priority,
        )
        return True
