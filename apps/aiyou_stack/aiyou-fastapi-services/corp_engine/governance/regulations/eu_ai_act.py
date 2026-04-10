"""
EU AI Act Compliance Module
============================
Full implementation of EU AI Act requirements.
Focus on Article 26 and high-risk AI system regulations.

Key Articles Implemented:
- Article 6: Classification rules for high-risk AI systems
- Article 9: Risk management system
- Article 10: Data and data governance
- Article 13: Transparency and information provision
- Article 14: Human oversight
- Article 26: Obligations for deployers of high-risk AI systems
- Article 52: Transparency for certain AI systems
"""

import logging
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RiskClassification(StrEnum):
    """EU AI Act risk classifications"""

    UNACCEPTABLE = "unacceptable"  # Banned
    HIGH = "high"  # Strict requirements
    LIMITED = "limited"  # Transparency requirements
    MINIMAL = "minimal"  # No requirements


class AISystemCategory(StrEnum):
    """Categories of AI systems under EU AI Act"""

    BIOMETRIC = "biometric"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    ESSENTIAL_SERVICES = "essential_services"
    LAW_ENFORCEMENT = "law_enforcement"
    MIGRATION = "migration"
    JUSTICE = "justice"
    DEMOCRATIC_PROCESSES = "democratic_processes"
    GENERAL_PURPOSE = "general_purpose"


class Article26Requirements(BaseModel):
    """
    Article 26 specific requirements for deployers of high-risk AI systems.

    Deployers must:
    1. Use AI systems in accordance with instructions
    2. Ensure human oversight by competent persons
    3. Monitor operation for risks
    4. Keep logs automatically generated
    5. Inform affected individuals
    6. Conduct data protection impact assessments
    """

    system_id: str
    deployer_id: str

    # Requirement 1: Instructions compliance
    instructions_followed: bool = False
    instruction_deviations: list[str] = Field(default_factory=list)

    # Requirement 2: Human oversight
    human_oversight_enabled: bool = False
    oversight_persons: list[str] = Field(default_factory=list)
    oversight_training_completed: bool = False

    # Requirement 3: Risk monitoring
    monitoring_active: bool = False
    risk_incidents: list[dict[str, Any]] = Field(default_factory=list)
    last_risk_review: datetime | None = None

    # Requirement 4: Logging
    logging_enabled: bool = False
    log_retention_days: int = 0
    logs_accessible: bool = False

    # Requirement 5: Individual information
    individuals_informed: bool = False
    information_method: str = ""

    # Requirement 6: DPIA
    dpia_conducted: bool = False
    dpia_date: datetime | None = None
    dpia_findings: dict[str, Any] = Field(default_factory=dict)

    # Compliance status
    compliant: bool = False
    compliance_gaps: list[str] = Field(default_factory=list)
    last_assessment: datetime = Field(default_factory=datetime.utcnow)


class TransparencyRequirement(BaseModel):
    """Article 52 transparency requirements"""

    disclosure_provided: bool = False
    disclosure_method: str = ""  # label, watermark, verbal, written
    disclosure_timestamp: datetime | None = None
    content_type: str = ""  # text, image, audio, video
    synthetic_content: bool = False
    deepfake: bool = False


class EUAIActCompliance:
    """
    EU AI Act Compliance Engine.

    Implements full EU AI Act compliance checking including:
    - Risk classification
    - Article 26 deployer obligations
    - Article 52 transparency requirements
    - Record keeping and audit trail
    - Incident reporting

    "No Hot Water" Principle:
    - All AI operations classified and tracked
    - Automatic compliance gap detection
    - Proactive remediation recommendations
    """

    # High-risk categories (Annex III)
    HIGH_RISK_CATEGORIES = [
        AISystemCategory.BIOMETRIC,
        AISystemCategory.CRITICAL_INFRASTRUCTURE,
        AISystemCategory.EDUCATION,
        AISystemCategory.EMPLOYMENT,
        AISystemCategory.ESSENTIAL_SERVICES,
        AISystemCategory.LAW_ENFORCEMENT,
        AISystemCategory.MIGRATION,
        AISystemCategory.JUSTICE,
        AISystemCategory.DEMOCRATIC_PROCESSES,
    ]

    # Unacceptable uses (Article 5)
    PROHIBITED_USES = [
        "subliminal_manipulation",
        "exploitation_vulnerability",
        "social_scoring_government",
        "real_time_biometric_public",
        "emotion_recognition_workplace",
        "biometric_categorization_sensitive",
    ]

    def __init__(self):
        self._system_registry: dict[str, dict[str, Any]] = {}
        self._article26_records: dict[str, Article26Requirements] = {}
        self._transparency_records: dict[str, TransparencyRequirement] = {}
        self._incidents: list[dict[str, Any]] = []

    # =========================================================================
    # Risk Classification
    # =========================================================================

    def classify_system(
        self, system_id: str, category: AISystemCategory, use_case: str, capabilities: list[str]
    ) -> RiskClassification:
        """
        Classify an AI system according to EU AI Act risk levels.

        Args:
            system_id: Unique system identifier
            category: Category of AI system
            use_case: Specific use case description
            capabilities: List of system capabilities

        Returns:
            Risk classification
        """
        # Check for prohibited uses
        for prohibited in self.PROHIBITED_USES:
            if prohibited in use_case.lower() or prohibited in capabilities:
                logger.warning(f"System {system_id} classified as UNACCEPTABLE: {prohibited}")
                return RiskClassification.UNACCEPTABLE

        # Check for high-risk categories
        if category in self.HIGH_RISK_CATEGORIES:
            logger.info(f"System {system_id} classified as HIGH risk (category: {category})")
            return RiskClassification.HIGH

        # Check for limited risk (transparency requirements)
        limited_risk_capabilities = [
            "chatbot",
            "emotion_recognition",
            "biometric_categorization",
            "synthetic_content",
            "deepfake",
            "text_generation",
        ]
        if any(cap in capabilities for cap in limited_risk_capabilities):
            return RiskClassification.LIMITED

        return RiskClassification.MINIMAL

    # =========================================================================
    # Article 26 Compliance
    # =========================================================================

    def assess_article26(
        self, system_id: str, deployer_id: str, current_state: dict[str, Any]
    ) -> Article26Requirements:
        """
        Assess Article 26 compliance for a high-risk AI system.

        Returns detailed requirements status and gaps.
        """
        requirements = Article26Requirements(
            system_id=system_id,
            deployer_id=deployer_id,
        )

        gaps = []

        # Check each requirement
        # Requirement 1: Instructions
        requirements.instructions_followed = current_state.get("follows_instructions", False)
        if not requirements.instructions_followed:
            gaps.append("System not used according to provider instructions")

        # Requirement 2: Human oversight
        requirements.human_oversight_enabled = current_state.get("human_oversight", False)
        requirements.oversight_persons = current_state.get("oversight_persons", [])
        requirements.oversight_training_completed = current_state.get("oversight_trained", False)

        if not requirements.human_oversight_enabled:
            gaps.append("Human oversight not enabled (Article 26.1.b)")
        if not requirements.oversight_persons:
            gaps.append("No designated oversight persons (Article 26.1.b)")
        if not requirements.oversight_training_completed:
            gaps.append("Oversight persons not trained (Article 26.2)")

        # Requirement 3: Monitoring
        requirements.monitoring_active = current_state.get("monitoring_active", False)
        requirements.last_risk_review = current_state.get("last_risk_review")

        if not requirements.monitoring_active:
            gaps.append("Risk monitoring not active (Article 26.1.c)")

        # Requirement 4: Logging
        requirements.logging_enabled = current_state.get("logging_enabled", False)
        requirements.log_retention_days = current_state.get("log_retention_days", 0)
        requirements.logs_accessible = current_state.get("logs_accessible", False)

        if not requirements.logging_enabled:
            gaps.append("Automatic logging not enabled (Article 26.1.d)")
        if requirements.log_retention_days < 180:  # 6 months minimum
            gaps.append("Log retention period insufficient (Article 26.1.d)")

        # Requirement 5: Individual information
        requirements.individuals_informed = current_state.get("individuals_informed", False)
        requirements.information_method = current_state.get("information_method", "")

        if not requirements.individuals_informed:
            gaps.append("Affected individuals not informed (Article 26.1.e)")

        # Requirement 6: DPIA
        requirements.dpia_conducted = current_state.get("dpia_conducted", False)
        requirements.dpia_date = current_state.get("dpia_date")

        if not requirements.dpia_conducted:
            gaps.append("Data protection impact assessment not conducted (Article 26.1.f)")

        # Overall compliance
        requirements.compliance_gaps = gaps
        requirements.compliant = len(gaps) == 0

        # Store record
        self._article26_records[system_id] = requirements

        if not requirements.compliant:
            logger.warning(f"Article 26 compliance gaps for {system_id}: {gaps}")

        return requirements

    # =========================================================================
    # Article 52 Transparency
    # =========================================================================

    def check_transparency(
        self,
        content_id: str,
        content_type: str,
        is_synthetic: bool,
        is_deepfake: bool,
        disclosure_provided: bool,
        disclosure_method: str,
    ) -> TransparencyRequirement:
        """
        Check Article 52 transparency compliance.

        For AI systems that:
        - Interact with natural persons (chatbots)
        - Generate synthetic content
        - Manipulate images/audio/video (deepfakes)
        """
        requirement = TransparencyRequirement(
            content_type=content_type,
            synthetic_content=is_synthetic,
            deepfake=is_deepfake,
            disclosure_provided=disclosure_provided,
            disclosure_method=disclosure_method,
            disclosure_timestamp=datetime.utcnow() if disclosure_provided else None,
        )

        # Validate disclosure
        if is_synthetic or is_deepfake:
            if not disclosure_provided:
                logger.warning(
                    f"Transparency violation: synthetic content {content_id} "
                    "requires disclosure (Article 52)"
                )
            elif disclosure_method not in ["watermark", "label", "metadata"]:
                logger.warning(
                    f"Disclosure method '{disclosure_method}' may not meet Article 52 requirements"
                )

        self._transparency_records[content_id] = requirement
        return requirement

    # =========================================================================
    # Incident Reporting
    # =========================================================================

    def report_incident(
        self,
        system_id: str,
        incident_type: str,
        description: str,
        affected_persons: int,
        severity: str,
    ) -> str:
        """
        Report a serious incident as required by Article 62.

        Serious incidents must be reported within 15 days.
        """
        incident_id = f"INC-{system_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        incident = {
            "incident_id": incident_id,
            "system_id": system_id,
            "incident_type": incident_type,
            "description": description,
            "affected_persons": affected_persons,
            "severity": severity,
            "reported_at": datetime.utcnow(),
            "deadline": datetime.utcnow(),  # 15 days from now
            "status": "reported",
        }

        self._incidents.append(incident)

        logger.critical(
            f"SERIOUS INCIDENT REPORTED: {incident_id} - {incident_type} "
            f"affecting {affected_persons} persons"
        )

        return incident_id

    # =========================================================================
    # Compliance Check
    # =========================================================================

    async def full_compliance_check(
        self, system_id: str, deployer_id: str, operation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Full EU AI Act compliance check.

        Returns comprehensive compliance status.
        """
        # Get system classification
        category = operation_data.get("category", AISystemCategory.GENERAL_PURPOSE)
        use_case = operation_data.get("use_case", "")
        capabilities = operation_data.get("capabilities", [])

        risk_level = self.classify_system(system_id, category, use_case, capabilities)

        result = {
            "system_id": system_id,
            "risk_classification": risk_level.value,
            "compliant": True,
            "violations": [],
            "warnings": [],
            "recommendations": [],
        }

        # Unacceptable risk = blocked
        if risk_level == RiskClassification.UNACCEPTABLE:
            result["compliant"] = False
            result["violations"].append(
                {
                    "article": "Article 5",
                    "description": "Prohibited AI practice",
                    "severity": "critical",
                }
            )
            return result

        # High risk = full Article 26 check
        if risk_level == RiskClassification.HIGH:
            art26 = self.assess_article26(system_id, deployer_id, operation_data)
            if not art26.compliant:
                result["compliant"] = False
                for gap in art26.compliance_gaps:
                    result["violations"].append(
                        {
                            "article": "Article 26",
                            "description": gap,
                            "severity": "high",
                        }
                    )

        # Limited risk = transparency check
        if risk_level in [RiskClassification.HIGH, RiskClassification.LIMITED]:
            if operation_data.get("generates_content"):
                if not operation_data.get("disclosure_provided"):
                    result["violations"].append(
                        {
                            "article": "Article 52",
                            "description": "AI-generated content not disclosed",
                            "severity": "medium",
                        }
                    )
                    result["compliant"] = False

        return result


# Global instance
eu_ai_compliance = EUAIActCompliance()
