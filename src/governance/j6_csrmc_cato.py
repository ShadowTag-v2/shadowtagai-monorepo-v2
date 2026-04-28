# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""DoD CIO CSRMC & NIST RMF Continuous ATO — Judge 6.1 J-6 Policy Enforcement.

Implements Zero Trust Architecture (ZTA) handoff enforcement between J-Staff
agents. Every inter-agent handoff is inspected, categorized per FIPS-199,
and evaluated against the ATP 5-19 / AR 385-10 risk matrix.

References:
    - DoD CIO Cyber Security Risk Management Construct (CSRMC)
    - NIST Risk Management Framework (RMF)
    - ATP 5-19: Risk Management
    - AR 385-10: The Army Safety Program
    - FIPS 199: Standards for Security Categorization
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("J6-CSRMC-ZeroTrust")


class CSRMCBlockError(Exception):
    """Raised when a ZTA handoff is blocked by CSRMC policy."""


@dataclass
class FIPS199Categorization:
    """NIST FIPS 199 security impact categorization."""

    confidentiality: str  # LOW, MODERATE, HIGH
    integrity: str
    availability: str


class Judge6CSRMC:
    """DoD CIO CSRMC & NIST RMF Continuous ATO enforcement.

    Acts as the J-6 Policy Enforcement Point (PEP) for every
    Temporal workflow handoff between agents.
    """

    # ATP 5-19 risk severity levels
    UNACCEPTABLE_SEVERITIES = frozenset({"CATASTROPHIC", "CRITICAL"})

    @staticmethod
    def categorize_system(payload_type: str) -> FIPS199Categorization:
        """NIST RMF Step 1: Categorize the information system.

        Args:
            payload_type: The type of payload being transferred.

        Returns:
            FIPS 199 impact categorization.
        """
        categorization_map: dict[str, FIPS199Categorization] = {
            "TRAIN_PY_MODIFICATION": FIPS199Categorization("MODERATE", "HIGH", "HIGH"),
            "DATABASE_MIGRATION": FIPS199Categorization("HIGH", "HIGH", "HIGH"),
            "AUTH_CHANGE": FIPS199Categorization("HIGH", "HIGH", "MODERATE"),
        }
        return categorization_map.get(
            payload_type,
            FIPS199Categorization("LOW", "MODERATE", "LOW"),
        )

    @staticmethod
    def enforce_zero_trust_handoff(
        source: str,
        destination: str,
        payload: dict[str, Any],
    ) -> bool:
        """ZTA Policy Enforcement Point — inspects every J-Staff handoff.

        No implicit trust. Evaluates ATP 5-19 Risk Matrix before
        authorizing inter-agent data transfers.

        Args:
            source: Originating J-Staff code (e.g., "J5").
            destination: Destination J-Staff code (e.g., "J3").
            payload: The payload being transferred, with risk metadata.

        Returns:
            True if handoff is authorized.

        Raises:
            CSRMCBlockError: If risk is unacceptable.
        """
        logger.info("🔐 J-6 ZTA PEP: Intercepting handoff %s -> %s", source, destination)

        fips = Judge6CSRMC.categorize_system(payload.get("type", "UNKNOWN"))
        severity = payload.get("risk_sev", "MARGINAL")

        if fips.integrity == "HIGH" and severity in Judge6CSRMC.UNACCEPTABLE_SEVERITIES:
            logger.critical(
                "🛑 J-6 ZTA VIOLATION: Unacceptable Risk (%s). Handoff Blocked.",
                severity,
            )
            raise CSRMCBlockError(f"CSRMC_ZTA_BLOCK: {source}->{destination} blocked (severity={severity})")

        logger.info("✅ J-6 cATO Verified. Handoff Authorized.")
        return True
