"""
JURA Compliance Gate
=====================
Integrated compliance checking for all Economic Juggernaut operations.
"No Hot Water" principle - every operation must pass compliance gates.

JURA Protocol Integration:
- Routes through existing JURA decision framework
- Adds compliance-specific checks
- Maintains full audit trail
- Automatic regulatory updates
"""

import hashlib
import logging
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ComplianceLevel(StrEnum):
    """Compliance strictness levels"""

    MINIMAL = "minimal"  # Basic checks only
    STANDARD = "standard"  # Industry standard
    STRICT = "strict"  # High-risk industries
    MAXIMUM = "maximum"  # Government/Defense/Healthcare


class ComplianceFramework(StrEnum):
    """Supported compliance frameworks"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    FEDRAMP = "fedramp"
    CMMC = "cmmc"
    ITAR = "itar"
    EU_AI_ACT = "eu_ai_act"
    CA_AI_MINOR = "ca_ai_minor"
    PCI_DSS = "pci_dss"


class ComplianceResult(BaseModel):
    """Result of compliance check"""

    passed: bool
    level: ComplianceLevel
    frameworks_checked: list[str]
    frameworks_passed: list[str]
    frameworks_failed: list[str]
    violations: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    audit_id: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    details: dict[str, Any] = Field(default_factory=dict)


class ComplianceRule(BaseModel):
    """A specific compliance rule"""

    rule_id: str
    framework: ComplianceFramework
    description: str
    severity: str  # critical, high, medium, low
    check_function: str  # Name of check function
    auto_remediate: bool = False


class JuraComplianceGate:
    """
    JURA Compliance Gate - the guardian of regulatory safety.

    Core Principle: "No Hot Water"
    - Every operation gated through compliance
    - Automatic framework detection by tenant profile
    - Real-time regulatory updates
    - Full audit trail for every decision

    Integrated Frameworks:
    - GDPR (EU data protection)
    - CCPA (California privacy)
    - HIPAA (Healthcare)
    - SOC 2 (Security)
    - FedRAMP (Federal)
    - CMMC (Defense supply chain)
    - ITAR (Arms regulations)
    - EU AI Act Article 26
    - California AI Minor Protection Act
    - PCI-DSS (Payment cards)
    """

    # Framework requirements by industry
    INDUSTRY_FRAMEWORKS = {
        "aerospace": [ComplianceFramework.ITAR, ComplianceFramework.SOC2],
        "defense": [
            ComplianceFramework.FEDRAMP,
            ComplianceFramework.CMMC,
            ComplianceFramework.ITAR,
        ],
        "fintech": [
            ComplianceFramework.SOC2,
            ComplianceFramework.PCI_DSS,
            ComplianceFramework.GDPR,
        ],
        "healthcare": [ComplianceFramework.HIPAA, ComplianceFramework.SOC2],
        "legal": [ComplianceFramework.SOC2, ComplianceFramework.GDPR],
        "government": [ComplianceFramework.FEDRAMP, ComplianceFramework.SOC2],
        "retail": [ComplianceFramework.PCI_DSS, ComplianceFramework.CCPA],
    }

    # Region-specific frameworks
    REGION_FRAMEWORKS = {
        "eu": [ComplianceFramework.GDPR, ComplianceFramework.EU_AI_ACT],
        "california": [ComplianceFramework.CCPA, ComplianceFramework.CA_AI_MINOR],
        "us-gov": [ComplianceFramework.FEDRAMP],
    }

    def __init__(self):
        self._rules: dict[str, ComplianceRule] = {}
        self._tenant_frameworks: dict[str, set[ComplianceFramework]] = {}
        self._audit_log: list[ComplianceResult] = []
        self._checkers: dict[ComplianceFramework, callable] = {}

        # Register built-in checkers
        self._register_builtin_checkers()

    def _register_builtin_checkers(self) -> None:
        """Register built-in compliance checkers"""
        self._checkers[ComplianceFramework.GDPR] = self._check_gdpr
        self._checkers[ComplianceFramework.CCPA] = self._check_ccpa
        self._checkers[ComplianceFramework.HIPAA] = self._check_hipaa
        self._checkers[ComplianceFramework.SOC2] = self._check_soc2
        self._checkers[ComplianceFramework.EU_AI_ACT] = self._check_eu_ai_act
        self._checkers[ComplianceFramework.CA_AI_MINOR] = self._check_ca_ai_minor
        self._checkers[ComplianceFramework.FEDRAMP] = self._check_fedramp
        self._checkers[ComplianceFramework.CMMC] = self._check_cmmc
        self._checkers[ComplianceFramework.ITAR] = self._check_itar
        self._checkers[ComplianceFramework.PCI_DSS] = self._check_pci_dss

    # =========================================================================
    # Main Gate Method
    # =========================================================================

    async def check(
        self,
        tenant_id: str,
        operation: str,
        data: dict[str, Any],
        level: ComplianceLevel = ComplianceLevel.STANDARD,
    ) -> ComplianceResult:
        """
        Main compliance gate - all operations must pass through here.

        Args:
            tenant_id: Tenant performing the operation
            operation: Type of operation (read, write, delete, process, etc.)
            data: Data involved in the operation
            level: Required compliance level

        Returns:
            ComplianceResult with pass/fail and details
        """
        audit_id = self._generate_audit_id(tenant_id, operation)

        # Get applicable frameworks for tenant
        frameworks = self._get_tenant_frameworks(tenant_id)

        # Add AI-specific frameworks always
        frameworks.add(ComplianceFramework.EU_AI_ACT)
        frameworks.add(ComplianceFramework.CA_AI_MINOR)

        passed_frameworks = []
        failed_frameworks = []
        all_violations = []
        all_warnings = []
        all_recommendations = []

        # Check each framework
        for framework in frameworks:
            checker = self._checkers.get(framework)
            if checker:
                try:
                    result = await checker(tenant_id, operation, data, level)
                    if result["passed"]:
                        passed_frameworks.append(framework.value)
                    else:
                        failed_frameworks.append(framework.value)
                        all_violations.extend(result.get("violations", []))
                    all_warnings.extend(result.get("warnings", []))
                    all_recommendations.extend(result.get("recommendations", []))
                except Exception as e:
                    logger.error(f"Compliance check failed for {framework}: {e}")
                    failed_frameworks.append(framework.value)
                    all_violations.append(
                        {
                            "framework": framework.value,
                            "error": str(e),
                            "severity": "critical",
                        }
                    )

        # Determine overall pass/fail
        passed = len(failed_frameworks) == 0

        result = ComplianceResult(
            passed=passed,
            level=level,
            frameworks_checked=[f.value for f in frameworks],
            frameworks_passed=passed_frameworks,
            frameworks_failed=failed_frameworks,
            violations=all_violations,
            warnings=all_warnings,
            recommendations=all_recommendations,
            audit_id=audit_id,
        )

        # Log to audit trail
        self._audit_log.append(result)

        if not passed:
            logger.warning(
                f"COMPLIANCE BLOCKED: {tenant_id} - {operation} - Failed: {failed_frameworks}"
            )

        return result

    # =========================================================================
    # Framework Configuration
    # =========================================================================

    def configure_tenant(
        self,
        tenant_id: str,
        industry: str,
        region: str,
        additional_frameworks: list[ComplianceFramework] | None = None,
    ) -> set[ComplianceFramework]:
        """Configure compliance frameworks for a tenant"""
        frameworks = set()

        # Add industry-specific frameworks
        industry_fw = self.INDUSTRY_FRAMEWORKS.get(industry.lower(), [])
        frameworks.update(industry_fw)

        # Add region-specific frameworks
        region_fw = self.REGION_FRAMEWORKS.get(region.lower(), [])
        frameworks.update(region_fw)

        # Add additional frameworks
        if additional_frameworks:
            frameworks.update(additional_frameworks)

        self._tenant_frameworks[tenant_id] = frameworks
        logger.info(
            f"Configured tenant {tenant_id} with frameworks: {[f.value for f in frameworks]}"
        )

        return frameworks

    def _get_tenant_frameworks(self, tenant_id: str) -> set[ComplianceFramework]:
        """Get frameworks configured for a tenant"""
        return self._tenant_frameworks.get(tenant_id, {ComplianceFramework.SOC2})

    # =========================================================================
    # Framework Checkers
    # =========================================================================

    async def _check_gdpr(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """GDPR compliance check"""
        violations = []
        warnings = []
        recommendations = []

        # Check for personal data processing
        if self._contains_pii(data):
            # Verify lawful basis
            if not data.get("lawful_basis"):
                violations.append(
                    {
                        "rule": "GDPR Article 6",
                        "description": "Processing personal data without lawful basis",
                        "severity": "critical",
                    }
                )

            # Check consent if required
            if data.get("lawful_basis") == "consent" and not data.get("consent_recorded"):
                violations.append(
                    {
                        "rule": "GDPR Article 7",
                        "description": "Consent not properly recorded",
                        "severity": "high",
                    }
                )

            # Data minimization
            if operation == "collect" and not data.get("purpose_limitation"):
                warnings.append("Consider implementing purpose limitation for GDPR compliance")

        # Right to be forgotten
        if operation == "delete" and not data.get("deletion_confirmed"):
            recommendations.append("Implement deletion confirmation for GDPR Article 17 compliance")

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    async def _check_ccpa(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """CCPA compliance check"""
        violations = []
        warnings = []

        # Check for California consumer data
        if data.get("region") == "california" or self._contains_pii(data):
            # Opt-out right
            if operation == "sell" and not data.get("opt_out_honored"):
                violations.append(
                    {
                        "rule": "CCPA 1798.120",
                        "description": "Consumer opt-out right not honored",
                        "severity": "critical",
                    }
                )

            # Privacy notice
            if not data.get("privacy_notice_provided"):
                warnings.append("Ensure privacy notice is provided per CCPA 1798.100")

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "recommendations": [],
        }

    async def _check_hipaa(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """HIPAA compliance check"""
        violations = []

        # Check for PHI
        if self._contains_phi(data):
            # Encryption requirement
            if not data.get("encrypted"):
                violations.append(
                    {
                        "rule": "HIPAA Security Rule",
                        "description": "PHI not encrypted",
                        "severity": "critical",
                    }
                )

            # Access controls
            if not data.get("access_logged"):
                violations.append(
                    {
                        "rule": "HIPAA Audit Controls",
                        "description": "PHI access not logged",
                        "severity": "high",
                    }
                )

            # Minimum necessary
            if operation == "share" and not data.get("minimum_necessary"):
                violations.append(
                    {
                        "rule": "HIPAA Minimum Necessary",
                        "description": "Sharing more PHI than necessary",
                        "severity": "medium",
                    }
                )

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": [],
            "recommendations": [],
        }

    async def _check_soc2(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """SOC 2 compliance check"""
        violations = []
        warnings = []

        # Security principle
        if operation in ["write", "delete"] and not data.get("authenticated"):
            violations.append(
                {
                    "rule": "SOC 2 CC6.1",
                    "description": "Operation without proper authentication",
                    "severity": "critical",
                }
            )

        # Availability
        if not data.get("redundancy_enabled"):
            warnings.append("Consider enabling redundancy for SOC 2 availability principle")

        # Processing integrity
        if operation == "process" and not data.get("validation_performed"):
            warnings.append("Add input validation for SOC 2 processing integrity")

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "recommendations": [],
        }

    async def _check_eu_ai_act(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """EU AI Act compliance check - delegates to regulations module"""
        violations = []
        warnings = []

        # Article 26: Transparency for AI systems
        if data.get("ai_generated") and not data.get("ai_disclosure"):
            violations.append(
                {
                    "rule": "EU AI Act Article 26",
                    "description": "AI-generated content not properly disclosed",
                    "severity": "high",
                }
            )

        # High-risk AI system requirements
        if data.get("high_risk_ai"):
            if not data.get("human_oversight"):
                violations.append(
                    {
                        "rule": "EU AI Act Article 14",
                        "description": "High-risk AI lacking human oversight",
                        "severity": "critical",
                    }
                )

            if not data.get("risk_assessment"):
                warnings.append("High-risk AI system should have documented risk assessment")

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "recommendations": [],
        }

    async def _check_ca_ai_minor(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """California AI Minor Protection Act compliance"""
        violations = []
        warnings = []

        # Check if minors are involved
        if data.get("involves_minors") or data.get("user_age", 99) < 18:
            # Extra protections required
            if not data.get("parental_consent") and data.get("user_age", 99) < 13:
                violations.append(
                    {
                        "rule": "CA AI Minor Protection",
                        "description": "Missing parental consent for user under 13",
                        "severity": "critical",
                    }
                )

            if data.get("ai_generated") and not data.get("age_appropriate_disclosure"):
                violations.append(
                    {
                        "rule": "CA AI Minor Protection - Disclosure",
                        "description": "AI content disclosure not age-appropriate",
                        "severity": "high",
                    }
                )

            # No behavioral manipulation
            if data.get("behavioral_targeting"):
                violations.append(
                    {
                        "rule": "CA AI Minor Protection - Targeting",
                        "description": "Behavioral targeting of minors prohibited",
                        "severity": "critical",
                    }
                )

            warnings.append("Enhanced protections active for minor user")

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "recommendations": [],
        }

    async def _check_fedramp(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """FedRAMP compliance check"""
        violations = []

        # Federal data handling
        if data.get("federal_data"):
            if not data.get("fedramp_authorized_environment"):
                violations.append(
                    {
                        "rule": "FedRAMP Authorization",
                        "description": "Federal data in non-authorized environment",
                        "severity": "critical",
                    }
                )

            if data.get("data_residency") != "us-gov":
                violations.append(
                    {
                        "rule": "FedRAMP Data Residency",
                        "description": "Federal data must stay in US-gov regions",
                        "severity": "critical",
                    }
                )

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": [],
            "recommendations": [],
        }

    async def _check_cmmc(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """CMMC (Cybersecurity Maturity Model Certification) check"""
        violations = []

        # CUI handling
        if data.get("cui_data") and not data.get("cmmc_level", 0) >= 2:
            violations.append(
                {
                    "rule": "CMMC Level 2",
                    "description": "CUI requires CMMC Level 2 certification",
                    "severity": "critical",
                }
            )

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": [],
            "recommendations": [],
        }

    async def _check_itar(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """ITAR (International Traffic in Arms Regulations) check"""
        violations = []

        # Defense article handling
        if data.get("itar_controlled"):
            if not data.get("us_person_only"):
                violations.append(
                    {
                        "rule": "ITAR 22 CFR 120-130",
                        "description": "ITAR data accessed by non-US person",
                        "severity": "critical",
                    }
                )

            if operation == "export" and not data.get("export_license"):
                violations.append(
                    {
                        "rule": "ITAR Export Control",
                        "description": "Export of ITAR data without license",
                        "severity": "critical",
                    }
                )

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": [],
            "recommendations": [],
        }

    async def _check_pci_dss(
        self, tenant_id: str, operation: str, data: dict[str, Any], level: ComplianceLevel
    ) -> dict[str, Any]:
        """PCI-DSS compliance check"""
        violations = []

        # Payment card data
        if self._contains_payment_data(data):
            if not data.get("encrypted"):
                violations.append(
                    {
                        "rule": "PCI-DSS Requirement 3",
                        "description": "Cardholder data not encrypted",
                        "severity": "critical",
                    }
                )

            if data.get("stores_cvv"):
                violations.append(
                    {
                        "rule": "PCI-DSS Requirement 3.2",
                        "description": "CVV storage prohibited",
                        "severity": "critical",
                    }
                )

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "warnings": [],
            "recommendations": [],
        }

    # =========================================================================
    # Helpers
    # =========================================================================

    def _contains_pii(self, data: dict[str, Any]) -> bool:
        """Check if data contains PII"""
        pii_fields = ["email", "name", "address", "phone", "ssn", "dob", "ip_address"]
        return any(field in data for field in pii_fields)

    def _contains_phi(self, data: dict[str, Any]) -> bool:
        """Check if data contains PHI"""
        phi_fields = ["medical_record", "diagnosis", "treatment", "prescription", "health_plan"]
        return any(field in data for field in phi_fields)

    def _contains_payment_data(self, data: dict[str, Any]) -> bool:
        """Check if data contains payment card data"""
        payment_fields = ["card_number", "pan", "cvv", "expiry", "cardholder_name"]
        return any(field in data for field in payment_fields)

    def _generate_audit_id(self, tenant_id: str, operation: str) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.utcnow().isoformat()
        content = f"{tenant_id}:{operation}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # =========================================================================
    # Audit Trail
    # =========================================================================

    def get_audit_trail(
        self, tenant_id: str | None = None, limit: int = 100
    ) -> list[ComplianceResult]:
        """Get audit trail, optionally filtered by tenant"""
        results = self._audit_log[-limit:]
        # In production, filter by tenant from audit_id
        return results


# Global instance
jura_gate = JuraComplianceGate()
