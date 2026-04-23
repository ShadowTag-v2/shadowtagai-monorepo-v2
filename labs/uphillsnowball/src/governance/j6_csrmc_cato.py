"""DoD CIO CSRMC & NIST RMF — Continuous Authority to Operate (cATO).

Judge 6.1 is not a tollbooth at the end of the room. It is the J-6
universal Policy Enforcement Point (PEP) enforcing Zero Trust at
every Temporal handoff between J-Staff agents.

Risk is not checked once — it is a continuous posture.

FIPS 199 categorizes every payload. ATP 5-19 / AR 385-10 calculates
residual risk. If risk exceeds the autonomous acceptance threshold,
the operation halts and routes to the Mobile PWA for Theater Commander
cryptographic authorization.

Risk Levels (AR 385-10):
    LOW       → J-Staff accepts autonomously
    MODERATE  → J-Staff accepts autonomously with logging
    HIGH      → HALT → Route to Commander PWA for signature
    EXTREMELY HIGH → RKILL (immediate termination, no appeal)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from temporalio.exceptions import ApplicationError

logger = logging.getLogger("J6-CSRMC-ZeroTrust")


class ImpactLevel(Enum):
    """FIPS 199 Security Categorization impact levels."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class RiskLevel(Enum):
    """AR 385-10 Composite Risk levels."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREMELY_HIGH = "EXTREMELY_HIGH"


class Probability(Enum):
    """ATP 5-19 Probability levels."""

    FREQUENT = "FREQUENT"
    LIKELY = "LIKELY"
    OCCASIONAL = "OCCASIONAL"
    SELDOM = "SELDOM"
    UNLIKELY = "UNLIKELY"


class Severity(Enum):
    """ATP 5-19 Severity levels."""

    CATASTROPHIC = "CATASTROPHIC"
    CRITICAL = "CRITICAL"
    MARGINAL = "MARGINAL"
    NEGLIGIBLE = "NEGLIGIBLE"


@dataclass(frozen=True)
class FIPS199Categorization:
    """NIST RMF Step 1: Security categorization per FIPS 199.

    Attributes:
        confidentiality: Impact if confidentiality is compromised.
        integrity: Impact if integrity is compromised.
        availability: Impact if availability is compromised.
    """

    confidentiality: ImpactLevel
    integrity: ImpactLevel
    availability: ImpactLevel

    @property
    def high_water_mark(self) -> ImpactLevel:
        """Return the highest impact level across all three dimensions."""
        levels = [self.confidentiality, self.integrity, self.availability]
        if ImpactLevel.HIGH in levels:
            return ImpactLevel.HIGH
        if ImpactLevel.MODERATE in levels:
            return ImpactLevel.MODERATE
        return ImpactLevel.LOW


# ATP 5-19 Risk Assessment Matrix
_RISK_MATRIX: dict[tuple[str, str], RiskLevel] = {
    ("FREQUENT", "CATASTROPHIC"): RiskLevel.EXTREMELY_HIGH,
    ("FREQUENT", "CRITICAL"): RiskLevel.EXTREMELY_HIGH,
    ("FREQUENT", "MARGINAL"): RiskLevel.HIGH,
    ("FREQUENT", "NEGLIGIBLE"): RiskLevel.MODERATE,
    ("LIKELY", "CATASTROPHIC"): RiskLevel.EXTREMELY_HIGH,
    ("LIKELY", "CRITICAL"): RiskLevel.HIGH,
    ("LIKELY", "MARGINAL"): RiskLevel.HIGH,
    ("LIKELY", "NEGLIGIBLE"): RiskLevel.MODERATE,
    ("OCCASIONAL", "CATASTROPHIC"): RiskLevel.EXTREMELY_HIGH,
    ("OCCASIONAL", "CRITICAL"): RiskLevel.HIGH,
    ("OCCASIONAL", "MARGINAL"): RiskLevel.MODERATE,
    ("OCCASIONAL", "NEGLIGIBLE"): RiskLevel.LOW,
    ("SELDOM", "CATASTROPHIC"): RiskLevel.HIGH,
    ("SELDOM", "CRITICAL"): RiskLevel.MODERATE,
    ("SELDOM", "MARGINAL"): RiskLevel.LOW,
    ("SELDOM", "NEGLIGIBLE"): RiskLevel.LOW,
    ("UNLIKELY", "CATASTROPHIC"): RiskLevel.HIGH,
    ("UNLIKELY", "CRITICAL"): RiskLevel.MODERATE,
    ("UNLIKELY", "MARGINAL"): RiskLevel.LOW,
    ("UNLIKELY", "NEGLIGIBLE"): RiskLevel.LOW,
}


class Judge6_CSRMC_cATO:
    """DoD CIO Cyber Security Risk Management Construct & NIST RMF cATO.

    Enforces Zero Trust at every J-Staff handoff boundary.
    No agent trusts another agent. Every transfer is inspected,
    categorized, risk-assessed, and authorized.
    """

    @staticmethod
    def categorize_system(payload_type: str) -> FIPS199Categorization:
        """NIST RMF Step 1: Categorize the information system.

        Args:
            payload_type: The type of payload being transferred.

        Returns:
            FIPS 199 categorization with C/I/A impact levels.
        """
        categorization_map: dict[str, FIPS199Categorization] = {
            "LEGAL_FILING": FIPS199Categorization(ImpactLevel.HIGH, ImpactLevel.HIGH, ImpactLevel.MODERATE),
            "MEDICAL_RECORD": FIPS199Categorization(ImpactLevel.HIGH, ImpactLevel.HIGH, ImpactLevel.HIGH),
            "FINANCIAL_ANALYSIS": FIPS199Categorization(ImpactLevel.MODERATE, ImpactLevel.HIGH, ImpactLevel.MODERATE),
            "CODE_MODIFICATION": FIPS199Categorization(ImpactLevel.MODERATE, ImpactLevel.HIGH, ImpactLevel.HIGH),
            "OSINT_REPORT": FIPS199Categorization(ImpactLevel.LOW, ImpactLevel.MODERATE, ImpactLevel.LOW),
        }
        return categorization_map.get(
            payload_type,
            FIPS199Categorization(ImpactLevel.LOW, ImpactLevel.MODERATE, ImpactLevel.LOW),
        )

    @staticmethod
    def calculate_risk(probability: str, severity: str) -> RiskLevel:
        """ATP 5-19 Risk Assessment Matrix calculation.

        Args:
            probability: Probability level string.
            severity: Severity level string.

        Returns:
            Composite risk level.
        """
        key = (probability.upper(), severity.upper())
        return _RISK_MATRIX.get(key, RiskLevel.MODERATE)

    @staticmethod
    def enforce_zero_trust_handoff(
        source: str,
        destination: str,
        payload: dict,
    ) -> bool:
        """ZTA Principle: No implicit trust between J-Staff agents.

        Evaluates FIPS 199 categorization and ATP 5-19 Risk Matrix
        before allowing any J-Staff handoff.

        Args:
            source: Source J-code (e.g., "J5").
            destination: Destination J-code (e.g., "J3").
            payload: The payload dict being transferred.

        Returns:
            True if handoff is authorized.

        Raises:
            ApplicationError: If risk is EXTREMELY_HIGH (RKILL) or
                if HIGH risk lacks commander authorization.
        """
        logger.info("🔐 J-6 ZTA PEP: Intercepting handoff %s → %s", source, destination)

        payload_type = payload.get("type", "UNKNOWN")
        fips = Judge6_CSRMC_cATO.categorize_system(payload_type)

        probability = payload.get("risk_prob", "SELDOM")
        severity = payload.get("risk_sev", "MARGINAL")
        risk = Judge6_CSRMC_cATO.calculate_risk(probability, severity)

        logger.info(
            "  FIPS-199 HWM=%s | Risk=%s (P=%s, S=%s)",
            fips.high_water_mark.value,
            risk.value,
            probability,
            severity,
        )

        if risk == RiskLevel.EXTREMELY_HIGH:
            logger.critical(
                "🛑 RKILL EXECUTED. Risk=%s. Handoff %s→%s terminated.",
                risk.value,
                source,
                destination,
            )
            raise ApplicationError(
                f"RKILL: Extremely High risk. Handoff {source}→{destination} terminated.",
                non_retryable=True,
            )

        if risk == RiskLevel.HIGH:
            logger.warning(
                "⚠️ HIGH RISK: Handoff %s→%s requires Commander authorization via PWA.",
                source,
                destination,
            )
            # In production, this signals the Temporal workflow to wait
            # for commander authorization via the Mobile PWA.
            # The workflow calls wait_condition() until the signal arrives.
            raise ApplicationError(
                f"HIGH_RISK_COMMANDER_AUTH_REQUIRED: {source}→{destination}",
                non_retryable=False,
            )

        logger.info("✅ J-6 cATO verified. Handoff %s→%s authorized.", source, destination)
        return True
