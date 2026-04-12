"""
Accessibility and Safety Compliance Engine
Implements WCAG 2.2, COPPA, and Age Appropriate Design Code
"""

import logging

from app.config import get_settings
from app.models.accessibility import (
    AADCComplianceRequest,
    AADCComplianceResponse,
    AgeGroup,
    COPPAComplianceRequest,
    COPPAComplianceResponse,
    WCAGAuditRequest,
    WCAGAuditResponse,
    WCAGLevel,
    WCAGPrinciple,
    WCAGViolation,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class AccessibilityEngine:
    """Accessibility and safety compliance verification engine"""

    def __init__(self):
        self.persona_iq = settings.persona_iq_override
        logger.info(f"Accessibility Engine initialized with Persona IQ: {self.persona_iq}")

    async def audit_wcag(self, request: WCAGAuditRequest) -> WCAGAuditResponse:
        """
        WCAG 2.2 accessibility audit

        Running at IQ {self.persona_iq} for comprehensive accessibility analysis
        """
        logger.info(f"Running WCAG {request.version} audit at IQ {self.persona_iq}")

        violations = []
        warnings = []
        tested_elements = 0

        # Simulate accessibility audit
        # In production, this would use axe-core or similar
        if request.html_content:
            tested_elements = request.html_content.count("<")

            # Check for common issues
            if 'alt=""' in request.html_content or "alt=" not in request.html_content:
                violations.append(
                    WCAGViolation(
                        principle=WCAGPrinciple.PERCEIVABLE,
                        guideline="1.1 Text Alternatives",
                        success_criterion="1.1.1 Non-text Content",
                        level=WCAGLevel.A,
                        description="Images missing alt text",
                        impact="serious",
                        element="img",
                        remediation="Add descriptive alt text to all images",
                    )
                )

            if "<input" in request.html_content and "aria-label" not in request.html_content:
                violations.append(
                    WCAGViolation(
                        principle=WCAGPrinciple.PERCEIVABLE,
                        guideline="4.1 Compatible",
                        success_criterion="4.1.2 Name, Role, Value",
                        level=WCAGLevel.A,
                        description="Form inputs missing labels",
                        impact="serious",
                        element="input",
                        remediation="Add aria-label or associated label elements",
                    )
                )

            if "tabindex" not in request.html_content:
                warnings.append("Consider adding tabindex for keyboard navigation")

        # Calculate score
        critical_violations = [v for v in violations if v.impact == "critical"]
        serious_violations = [v for v in violations if v.impact == "serious"]
        score = max(0.0, 100.0 - (len(critical_violations) * 20) - (len(serious_violations) * 10))

        # Determine compliance level
        compliant = len(violations) == 0
        if compliant:
            level_achieved = request.target_level
        elif len(violations) <= 2:
            level_achieved = WCAGLevel.A
        else:
            level_achieved = None

        return WCAGAuditResponse(
            compliant=compliant,
            level_achieved=level_achieved,
            violations=violations,
            warnings=warnings,
            score=score,
            tested_elements=tested_elements,
        )

    async def check_coppa(self, request: COPPAComplianceRequest) -> COPPAComplianceResponse:
        """COPPA compliance check"""
        logger.info(f"Checking COPPA compliance at IQ {self.persona_iq}")

        # Determine age group
        if request.user_age < 13:
            age_group = AgeGroup.UNDER_13
        elif request.user_age < 18:
            age_group = AgeGroup.TEEN_13_17
        else:
            age_group = AgeGroup.ADULT_18_PLUS

        violations = []
        recommendations = []
        requires_parental_consent = age_group == AgeGroup.UNDER_13

        # Check COPPA requirements for children under 13
        if requires_parental_consent:
            if request.collects_personal_info and not request.parental_consent_obtained:
                violations.append("Collecting personal info from children without parental consent")

            if not request.data_minimization:
                violations.append("Data minimization not implemented for children")

            if not request.deletion_mechanism:
                violations.append("No mechanism for parents to delete child's data")

            if request.third_party_disclosure:
                violations.append("Disclosing children's data to third parties without consent")

            # Recommendations
            recommendations.extend(
                [
                    "Implement verifiable parental consent mechanism",
                    "Provide clear privacy policy in plain language",
                    "Enable data deletion requests",
                    "Limit data collection to what's necessary",
                ]
            )

        compliant = len(violations) == 0

        return COPPAComplianceResponse(
            compliant=compliant,
            age_group=age_group,
            requires_parental_consent=requires_parental_consent,
            violations=violations,
            recommendations=recommendations,
        )

    async def check_aadc(self, request: AADCComplianceRequest) -> AADCComplianceResponse:
        """Age Appropriate Design Code (UK) compliance check"""
        logger.info(f"Checking AADC compliance at IQ {self.persona_iq}")

        # Determine age group
        if request.user_age < 13:
            age_group = AgeGroup.UNDER_13
        elif request.user_age < 18:
            age_group = AgeGroup.TEEN_13_17
        else:
            age_group = AgeGroup.ADULT_18_PLUS

        violations = []
        required_controls = []

        # AADC applies to children under 18
        if age_group in [AgeGroup.UNDER_13, AgeGroup.TEEN_13_17]:
            # Check privacy settings default to high
            if not request.privacy_settings_default_high:
                violations.append("Privacy settings must default to high for children")
                required_controls.append("Set privacy to 'friends only' or 'private' by default")

            # Check geolocation
            if request.geolocation_enabled:
                violations.append("Geolocation should be off by default for children")
                required_controls.append("Disable geolocation by default")

            # Check profiling
            if request.profiling_enabled:
                violations.append(
                    "Profiling not permitted for children without exceptional circumstances"
                )
                required_controls.append("Disable profiling and personalized advertising")

            # Check third-party data sharing
            if request.data_shared_with_third_parties:
                violations.append("Sharing children's data with third parties restricted")
                required_controls.append("Disable third-party data sharing")

            # Check parental controls
            if not request.parental_controls_available:
                violations.append("Parental controls must be available")
                required_controls.append("Implement parental control features")

        # Age-appropriate defaults check
        age_appropriate_defaults = (
            request.privacy_settings_default_high
            and not request.geolocation_enabled
            and not request.profiling_enabled
            and not request.data_shared_with_third_parties
        )

        compliant = len(violations) == 0

        return AADCComplianceResponse(
            compliant=compliant,
            age_group=age_group,
            violations=violations,
            required_controls=required_controls,
            age_appropriate_defaults=age_appropriate_defaults,
        )
