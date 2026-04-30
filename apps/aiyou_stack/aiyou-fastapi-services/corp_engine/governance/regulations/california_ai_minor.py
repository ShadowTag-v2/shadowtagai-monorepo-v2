"""California AI Minor Protection Act Compliance
==============================================
Implementation of California's AI protections for minors.
Based on AB 2273 (California Age-Appropriate Design Code Act)
and related AI minor protection legislation.

Key Protections:
1. Age verification requirements
2. Prohibition on harmful algorithmic amplification
3. Data minimization for minors
4. Parental notification and consent
5. Prohibition on behavioral targeting of minors
6. Transparency in AI-generated content
"""

import logging
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MinorProtectionLevel(StrEnum):
    """Protection levels based on age"""

    UNDER_13 = "under_13"  # COPPA + maximum protection
    TEEN_13_15 = "teen_13_15"  # High protection
    TEEN_16_17 = "teen_16_17"  # Standard minor protection
    ADULT = "adult"  # Standard protections


class ContentRisk(StrEnum):
    """Content risk classifications for minors"""

    SAFE = "safe"
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk"
    HIGH_RISK = "high_risk"
    PROHIBITED = "prohibited"


class MinorDataCategory(StrEnum):
    """Categories of data that require special handling for minors"""

    LOCATION = "location"
    BEHAVIORAL = "behavioral"
    BIOMETRIC = "biometric"
    HEALTH = "health"
    FINANCIAL = "financial"
    EDUCATIONAL = "educational"
    SOCIAL = "social"
    COMMUNICATIONS = "communications"


class MinorComplianceResult(BaseModel):
    """Result of minor protection compliance check"""

    user_id: str
    protection_level: MinorProtectionLevel
    compliant: bool
    violations: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    parental_consent_required: bool = False
    data_minimization_applied: bool = False
    content_filtered: bool = False
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class DataProtectionStatus(BaseModel):
    """Status of data protection measures for a minor"""

    user_id: str
    age_verified: bool = False
    verification_method: str = ""
    parental_consent: bool = False
    consent_timestamp: datetime | None = None
    consent_scope: list[str] = Field(default_factory=list)
    data_categories_collected: list[MinorDataCategory] = Field(default_factory=list)
    data_categories_minimized: list[MinorDataCategory] = Field(default_factory=list)
    retention_period_days: int = 0
    deletion_scheduled: datetime | None = None


class CaliforniaAIMinorCompliance:
    """California AI Minor Protection Compliance Engine.

    Implements protections required by California law including:
    - Age-Appropriate Design Code (AB 2273)
    - CPRA minor provisions
    - AI-specific minor protections

    Core Principles:
    1. Best interests of the child
    2. Age-appropriate privacy by default
    3. High privacy by default for minors
    4. No profiling with harmful effects
    5. No dark patterns targeting minors
    """

    # Prohibited practices for minors
    PROHIBITED_PRACTICES = [
        "behavioral_profiling",
        "targeted_advertising",
        "dark_patterns",
        "harmful_content_amplification",
        "location_tracking_without_consent",
        "selling_minor_data",
        "emotion_manipulation",
        "addiction_features",
        "social_pressure_features",
        "autoplay_without_limits",
    ]

    # Data that requires explicit consent for minors
    SENSITIVE_DATA_CATEGORIES = [
        MinorDataCategory.LOCATION,
        MinorDataCategory.BIOMETRIC,
        MinorDataCategory.HEALTH,
        MinorDataCategory.BEHAVIORAL,
    ]

    def __init__(self):
        self._user_records: dict[str, DataProtectionStatus] = {}
        self._compliance_log: list[MinorComplianceResult] = []

    # =========================================================================
    # Age Determination
    # =========================================================================

    def determine_protection_level(
        self,
        birth_date: date | None = None,
        age: int | None = None,
    ) -> MinorProtectionLevel:
        """Determine appropriate protection level based on age.

        Args:
            birth_date: User's date of birth
            age: User's age (if birth_date not available)

        Returns:
            Appropriate protection level

        """
        if birth_date:
            today = date.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

        if age is None:
            # Unknown age = maximum protection
            logger.warning("Age unknown, applying maximum protection")
            return MinorProtectionLevel.UNDER_13

        if age < 13:
            return MinorProtectionLevel.UNDER_13
        if age < 16:
            return MinorProtectionLevel.TEEN_13_15
        if age < 18:
            return MinorProtectionLevel.TEEN_16_17
        return MinorProtectionLevel.ADULT

    # =========================================================================
    # Core Compliance Check
    # =========================================================================

    async def check_compliance(
        self,
        user_id: str,
        protection_level: MinorProtectionLevel,
        operation: str,
        data: dict[str, Any],
    ) -> MinorComplianceResult:
        """Main compliance check for operations involving minors.

        Args:
            user_id: User identifier
            protection_level: User's protection level
            operation: Type of operation being performed
            data: Data involved in the operation

        Returns:
            Compliance result with any violations and required actions

        """
        result = MinorComplianceResult(
            user_id=user_id,
            protection_level=protection_level,
            compliant=True,
        )

        # Adults don't need minor-specific protections
        if protection_level == MinorProtectionLevel.ADULT:
            return result

        violations = []
        warnings = []
        required_actions = []

        # Check for prohibited practices
        for practice in self.PROHIBITED_PRACTICES:
            if data.get(practice):
                violations.append(
                    {
                        "practice": practice,
                        "description": f"Prohibited practice for minors: {practice}",
                        "severity": "critical",
                        "reference": "CA Age-Appropriate Design Code",
                    },
                )

        # Check parental consent requirements
        consent_check = self._check_parental_consent(user_id, protection_level, operation, data)
        if consent_check["required"] and not consent_check["obtained"]:
            violations.append(
                {
                    "practice": "missing_parental_consent",
                    "description": consent_check["reason"],
                    "severity": "critical",
                    "reference": "COPPA / CA Privacy Rights Act",
                },
            )
            result.parental_consent_required = True
            required_actions.append("Obtain verifiable parental consent")

        # Check data minimization
        data_categories = data.get("data_categories", [])
        minimization = self._check_data_minimization(protection_level, data_categories)
        if not minimization["compliant"]:
            for issue in minimization["issues"]:
                violations.append(
                    {
                        "practice": "data_collection_violation",
                        "description": issue,
                        "severity": "high",
                        "reference": "CA Data Minimization Requirements",
                    },
                )
            required_actions.extend(minimization["actions"])
        result.data_minimization_applied = minimization["minimization_applied"]

        # Check AI-specific requirements
        if data.get("ai_generated") or data.get("ai_processed"):
            ai_check = self._check_ai_requirements(protection_level, data)
            violations.extend(ai_check["violations"])
            warnings.extend(ai_check["warnings"])
            required_actions.extend(ai_check["actions"])
            result.content_filtered = ai_check.get("content_filtered", False)

        # Check content risk
        if data.get("content"):
            content_risk = self._assess_content_risk(data.get("content"), protection_level)
            if content_risk == ContentRisk.PROHIBITED:
                violations.append(
                    {
                        "practice": "prohibited_content",
                        "description": "Content not appropriate for user age",
                        "severity": "critical",
                        "reference": "CA Age-Appropriate Design Code",
                    },
                )
            elif content_risk == ContentRisk.HIGH_RISK:
                warnings.append("Content may not be age-appropriate - review recommended")

        # Set overall compliance
        result.compliant = len(violations) == 0
        result.violations = violations
        result.warnings = warnings
        result.required_actions = required_actions

        # Log result
        self._compliance_log.append(result)

        if not result.compliant:
            logger.warning(
                f"Minor protection violations for {user_id} "
                f"(level: {protection_level.value}): {len(violations)} violations",
            )

        return result

    # =========================================================================
    # Parental Consent
    # =========================================================================

    def _check_parental_consent(
        self,
        user_id: str,
        protection_level: MinorProtectionLevel,
        operation: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Check parental consent requirements"""
        result = {
            "required": False,
            "obtained": False,
            "reason": "",
        }

        # Under 13 always requires parental consent for data collection
        if protection_level == MinorProtectionLevel.UNDER_13:
            result["required"] = True
            result["reason"] = "COPPA requires parental consent for users under 13"

        # Sensitive data requires consent for all minors
        data_categories = data.get("data_categories", [])
        if any(cat in self.SENSITIVE_DATA_CATEGORIES for cat in data_categories):
            result["required"] = True
            result["reason"] = "Sensitive data collection requires parental consent for minors"

        # Check if consent has been obtained
        user_record = self._user_records.get(user_id)
        if user_record and user_record.parental_consent:
            result["obtained"] = True

        return result

    def record_parental_consent(
        self,
        user_id: str,
        consent_scope: list[str],
        verification_method: str,
    ) -> DataProtectionStatus:
        """Record parental consent for a minor"""
        if user_id not in self._user_records:
            self._user_records[user_id] = DataProtectionStatus(user_id=user_id)

        record = self._user_records[user_id]
        record.parental_consent = True
        record.consent_timestamp = datetime.utcnow()
        record.consent_scope = consent_scope
        record.verification_method = verification_method

        logger.info(f"Parental consent recorded for {user_id}: {consent_scope}")
        return record

    # =========================================================================
    # Data Minimization
    # =========================================================================

    def _check_data_minimization(
        self,
        protection_level: MinorProtectionLevel,
        data_categories: list[Any],
    ) -> dict[str, Any]:
        """Check data minimization requirements for minors"""
        result = {
            "compliant": True,
            "issues": [],
            "actions": [],
            "minimization_applied": False,
        }

        # Maximum protection = minimal data collection
        if protection_level == MinorProtectionLevel.UNDER_13:
            prohibited = [
                MinorDataCategory.BEHAVIORAL,
                MinorDataCategory.BIOMETRIC,
                MinorDataCategory.LOCATION,
            ]
            for cat in data_categories:
                if cat in prohibited:
                    result["compliant"] = False
                    result["issues"].append(
                        f"Collection of {cat.value if hasattr(cat, 'value') else cat} "
                        "data prohibited for users under 13",
                    )
                    result["actions"].append(
                        f"Remove {cat.value if hasattr(cat, 'value') else cat} data collection",
                    )

        # Teen protection = restricted data collection
        elif protection_level in [MinorProtectionLevel.TEEN_13_15, MinorProtectionLevel.TEEN_16_17]:
            restricted = [MinorDataCategory.BEHAVIORAL, MinorDataCategory.BIOMETRIC]
            for cat in data_categories:
                if cat in restricted:
                    result["issues"].append(
                        f"Collection of {cat.value if hasattr(cat, 'value') else cat} data restricted for minors",
                    )
                    result["actions"].append(
                        f"Obtain explicit consent for {cat.value if hasattr(cat, 'value') else cat} data or minimize collection",
                    )

        if result["issues"]:
            result["minimization_applied"] = True

        return result

    # =========================================================================
    # AI-Specific Requirements
    # =========================================================================

    def _check_ai_requirements(
        self,
        protection_level: MinorProtectionLevel,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Check AI-specific requirements for content involving minors"""
        violations = []
        warnings = []
        actions = []
        content_filtered = False

        # AI transparency requirement
        if data.get("ai_generated") and not data.get("ai_disclosure"):
            violations.append(
                {
                    "practice": "missing_ai_disclosure",
                    "description": "AI-generated content must be disclosed to minors",
                    "severity": "high",
                    "reference": "CA AI Minor Protection",
                },
            )
            actions.append("Add age-appropriate AI content disclosure")

        # Algorithmic amplification check
        if data.get("algorithm_amplified"):
            if protection_level == MinorProtectionLevel.UNDER_13:
                violations.append(
                    {
                        "practice": "algorithmic_amplification",
                        "description": "Algorithmic content amplification prohibited for users under 13",
                        "severity": "critical",
                        "reference": "CA Age-Appropriate Design Code",
                    },
                )
            else:
                warnings.append("Algorithmic amplification should prioritize minor well-being")

        # Recommendation system check
        if data.get("personalized_recommendations"):  # noqa: SIM102
            if protection_level in [MinorProtectionLevel.UNDER_13, MinorProtectionLevel.TEEN_13_15]:
                violations.append(
                    {
                        "practice": "personalized_recommendations",
                        "description": "Personalized recommendations restricted for minors under 16",
                        "severity": "high",
                        "reference": "CA Age-Appropriate Design Code",
                    },
                )
                content_filtered = True

        # Emotion manipulation check
        if data.get("emotion_targeting"):
            violations.append(
                {
                    "practice": "emotion_targeting",
                    "description": "AI systems must not manipulate minor emotions",
                    "severity": "critical",
                    "reference": "CA AI Minor Protection",
                },
            )

        return {
            "violations": violations,
            "warnings": warnings,
            "actions": actions,
            "content_filtered": content_filtered,
        }

    # =========================================================================
    # Content Risk Assessment
    # =========================================================================

    def _assess_content_risk(
        self,
        content: Any,
        protection_level: MinorProtectionLevel,
    ) -> ContentRisk:
        """Assess content risk for a minor"""
        # In production, this would use content classification AI
        # For now, basic keyword/flag based assessment

        if isinstance(content, dict):
            flags = content.get("content_flags", [])

            # Prohibited content for all minors
            prohibited_flags = ["adult", "violence_graphic", "drugs", "self_harm"]
            if any(flag in flags for flag in prohibited_flags):
                return ContentRisk.PROHIBITED

            # High risk for younger users
            high_risk_flags = ["violence", "scary", "mature_themes"]
            if protection_level == MinorProtectionLevel.UNDER_13:
                if any(flag in flags for flag in high_risk_flags):
                    return ContentRisk.PROHIBITED
            elif protection_level == MinorProtectionLevel.TEEN_13_15:  # noqa: SIM102
                if any(flag in flags for flag in high_risk_flags):
                    return ContentRisk.HIGH_RISK

        return ContentRisk.SAFE

    # =========================================================================
    # Reporting
    # =========================================================================

    def get_compliance_report(self, user_id: str | None = None, limit: int = 100) -> dict[str, Any]:
        """Generate compliance report"""
        records = self._compliance_log[-limit:]
        if user_id:
            records = [r for r in records if r.user_id == user_id]

        total = len(records)
        compliant = sum(1 for r in records if r.compliant)
        violations_by_type = {}

        for record in records:
            for violation in record.violations:
                practice = violation.get("practice", "unknown")
                violations_by_type[practice] = violations_by_type.get(practice, 0) + 1

        return {
            "total_checks": total,
            "compliant_checks": compliant,
            "compliance_rate": compliant / total if total > 0 else 1.0,
            "violations_by_type": violations_by_type,
            "protection_level_breakdown": self._get_level_breakdown(records),
        }

    def _get_level_breakdown(self, records: list[MinorComplianceResult]) -> dict[str, int]:
        """Get breakdown by protection level"""
        breakdown = {}
        for record in records:
            level = record.protection_level.value
            breakdown[level] = breakdown.get(level, 0) + 1
        return breakdown


# Global instance
ca_minor_compliance = CaliforniaAIMinorCompliance()
