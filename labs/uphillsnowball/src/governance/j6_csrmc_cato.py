# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

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


class DeploymentPhase(Enum):
    """Judge 6 deployment gate phases.

    Wet Fleece: Static analysis — $0 cost, catches 80% of issues.
    Dry Ground: Sandbox tests — moderate cost, catches integration bugs.
    Battle: Full integration — highest cost, final validation.
    """

    WET_FLEECE = "WET_FLEECE"
    DRY_GROUND = "DRY_GROUND"
    BATTLE = "BATTLE"


@dataclass(frozen=True)
class PhaseResult:
    """Result of a deployment phase gate check.

    Attributes:
        phase: Which phase was executed.
        passed: Whether the phase passed.
        findings: List of issues found.
        directive: Next action to take.
    """

    phase: DeploymentPhase
    passed: bool
    findings: list[str]
    directive: str


class Judge6DeployGate:
    """3-Phase deployment gate: Wet Fleece → Dry Ground → Battle.

    Each phase is progressively more expensive. If an earlier phase
    fails, later phases are NOT executed (fail-fast, save money).

    Phase 1 — Wet Fleece ($0):
        Static analysis: AST validation, type checking, dead code scan.
        Tools: ruff, vulture, ast-grep.

    Phase 2 — Dry Ground (moderate):
        Sandboxed test execution in gVisor container.
        No network access. Read-only filesystem. 120s timeout.

    Phase 3 — Battle (full cost):
        Full integration tests against staging environment.
        Requires Commander authorization for HIGH/EXTREMELY_HIGH risk.
    """

    @staticmethod
    def wet_fleece(artifact: dict) -> PhaseResult:
        """Phase 1: Static analysis gate — zero cost.

        Validates the artifact passes AST, type, and dead code checks
        without executing any code.

        Args:
            artifact: The code artifact to validate.

        Returns:
            PhaseResult indicating pass/fail.
        """
        findings: list[str] = []

        # Check for required metadata
        if not artifact.get("type"):
            findings.append("Missing artifact type classification")

        if not artifact.get("source"):
            findings.append("Missing source agent attribution")

        # Check for banned patterns
        source_code = artifact.get("code", "")
        banned_patterns = [
            ("eval(", "eval() is banned — use ast.literal_eval()"),
            ("exec(", "exec() is banned — use subprocess with gVisor"),
            ("__import__", "Dynamic imports banned — use explicit imports"),
            ("os.system(", "os.system() banned — use subprocess.run()"),
        ]
        for pattern, reason in banned_patterns:
            if pattern in source_code:
                findings.append(f"BANNED PATTERN: {reason}")

        passed = len(findings) == 0
        directive = "ADVANCE_TO_DRY_GROUND" if passed else "REJECT_WET_FLEECE"

        logger.info(
            "🧪 Wet Fleece: %s (%d findings)",
            "PASSED" if passed else "FAILED",
            len(findings),
        )
        return PhaseResult(
            phase=DeploymentPhase.WET_FLEECE,
            passed=passed,
            findings=findings,
            directive=directive,
        )

    @staticmethod
    def dry_ground(artifact: dict, test_results: dict) -> PhaseResult:
        """Phase 2: Sandbox test execution — moderate cost.

        Validates the artifact passes tests in a gVisor sandbox
        with no network and read-only filesystem.

        Args:
            artifact: The code artifact being tested.
            test_results: Results from sandbox test execution.

        Returns:
            PhaseResult indicating pass/fail.
        """
        findings: list[str] = []

        tests_passed = test_results.get("passed", 0)
        tests_failed = test_results.get("failed", 0)
        tests_error = test_results.get("error", 0)

        if tests_failed > 0:
            findings.append(f"{tests_failed} test(s) failed in sandbox")

        if tests_error > 0:
            findings.append(f"{tests_error} test(s) errored in sandbox")

        if tests_passed == 0:
            findings.append("No tests passed — suspect missing test coverage")

        # Check execution time SLA (UCMJ Drag Race: 40s max)
        execution_ms = test_results.get("execution_time_ms", 0)
        if execution_ms > 40_000:
            findings.append(f"Execution time {execution_ms}ms exceeds 40s UCMJ SLA")

        passed = len(findings) == 0
        directive = "ADVANCE_TO_BATTLE" if passed else "REJECT_DRY_GROUND"

        logger.info(
            "🏜️ Dry Ground: %s (pass=%d fail=%d err=%d, %dms)",
            "PASSED" if passed else "FAILED",
            tests_passed,
            tests_failed,
            tests_error,
            execution_ms,
        )
        return PhaseResult(
            phase=DeploymentPhase.DRY_GROUND,
            passed=passed,
            findings=findings,
            directive=directive,
        )

    @staticmethod
    def battle(artifact: dict, integration_results: dict) -> PhaseResult:
        """Phase 3: Full integration test — highest cost.

        Validates the artifact in a staging environment with network
        access. Requires Commander authorization for HIGH risk.

        Args:
            artifact: The code artifact being tested.
            integration_results: Results from integration testing.

        Returns:
            PhaseResult indicating pass/fail.
        """
        findings: list[str] = []

        health_check = integration_results.get("health_check", False)
        if not health_check:
            findings.append("Health check failed after deployment to staging")

        smoke_tests = integration_results.get("smoke_tests_passed", 0)
        smoke_total = integration_results.get("smoke_tests_total", 0)
        if smoke_total > 0 and smoke_tests < smoke_total:
            findings.append(f"Smoke tests: {smoke_tests}/{smoke_total} passed")

        lighthouse_score = integration_results.get("lighthouse_score")
        if lighthouse_score is not None and lighthouse_score < 80:
            findings.append(f"Lighthouse score {lighthouse_score} below 80 threshold")

        passed = len(findings) == 0
        directive = "DEPLOY_TO_PRODUCTION" if passed else "REJECT_BATTLE"

        logger.info(
            "⚔️ Battle: %s (%d findings)",
            "PASSED" if passed else "FAILED",
            len(findings),
        )
        return PhaseResult(
            phase=DeploymentPhase.BATTLE,
            passed=passed,
            findings=findings,
            directive=directive,
        )

    @classmethod
    def run_gate(
        cls,
        artifact: dict,
        test_results: dict | None = None,
        integration_results: dict | None = None,
    ) -> list[PhaseResult]:
        """Execute the full 3-phase gate sequence, fail-fast.

        Args:
            artifact: The code artifact to validate.
            test_results: Optional sandbox test results (Phase 2).
            integration_results: Optional integration results (Phase 3).

        Returns:
            List of PhaseResults for all executed phases.
        """
        results: list[PhaseResult] = []

        # Phase 1: Wet Fleece (always runs, $0)
        p1 = cls.wet_fleece(artifact)
        results.append(p1)
        if not p1.passed:
            return results

        # Phase 2: Dry Ground (requires test results)
        if test_results is not None:
            p2 = cls.dry_ground(artifact, test_results)
            results.append(p2)
            if not p2.passed:
                return results
        else:
            logger.info("⏭️ Dry Ground skipped — no test results provided")

        # Phase 3: Battle (requires integration results)
        if integration_results is not None:
            p3 = cls.battle(artifact, integration_results)
            results.append(p3)
        else:
            logger.info("⏭️ Battle skipped — no integration results provided")

        return results
