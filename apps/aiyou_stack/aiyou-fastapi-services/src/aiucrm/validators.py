# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AiUCRM Validators
Specialized compliance validators for different regulatory frameworks
"""

from typing import Any


class LegalComplianceValidator:
    """Validates legal compliance across multiple frameworks"""

    FRAMEWORKS = {
        "EU_AI_ACT": {
            "high_risk_use_cases": [
                "biometric_id",
                "critical_infrastructure",
                "law_enforcement",
                "education_scoring",
            ],
            "prohibited_use_cases": [
                "social_scoring",
                "subliminal_manipulation",
                "exploitation_vulnerable",
            ],
        },
        "HIPAA": {
            "required_controls": ["encryption", "access_logs", "phi_protection"],
        },
        "FAA": {
            "required_certifications": ["DO-178C", "DO-254"],
        },
        "DoD_RAI": {
            "required_controls": [
                "responsible_use",
                "equitable",
                "traceable",
                "reliable",
                "governable",
            ],
        },
    }

    def validate(self, request: dict[str, Any], frameworks: list[str]) -> dict[str, Any]:
        """Validate against specified legal frameworks"""
        violations = []
        score = 1.0

        for framework in frameworks:
            if framework == "EU_AI_ACT":
                violations.extend(self._check_eu_ai_act(request))
            elif framework == "HIPAA":
                violations.extend(self._check_hipaa(request))
            elif framework == "FAA":
                violations.extend(self._check_faa(request))
            elif framework == "DoD_RAI":
                violations.extend(self._check_dod_rai(request))

        if violations:
            score = max(0.0, 1.0 - (len(violations) * 0.3))

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "score": score,
            "frameworks_checked": frameworks,
        }

    def _check_eu_ai_act(self, request: dict[str, Any]) -> list[str]:
        """Check EU AI Act compliance"""
        violations = []
        operation_type = request.get("operation_type", "")

        # Check prohibited use cases
        if operation_type in self.FRAMEWORKS["EU_AI_ACT"]["prohibited_use_cases"]:
            violations.append(f"EU AI Act: Prohibited use case '{operation_type}'")

        # Check high-risk requirements
        if operation_type in self.FRAMEWORKS["EU_AI_ACT"]["high_risk_use_cases"]:
            if not request.get("risk_assessment_completed"):
                violations.append("EU AI Act: High-risk use case requires risk assessment")
            if not request.get("human_oversight"):
                violations.append("EU AI Act: High-risk use case requires human oversight")

        return violations

    def _check_hipaa(self, request: dict[str, Any]) -> list[str]:
        """Check HIPAA compliance"""
        violations = []

        if "medical" in request.get("operation_type", ""):
            if not request.get("phi_encrypted"):
                violations.append("HIPAA: PHI must be encrypted")
            if not request.get("access_logs_enabled"):
                violations.append("HIPAA: Access logs required")
            if not request.get("user_consent"):
                violations.append("HIPAA: Patient consent required")

        return violations

    def _check_faa(self, request: dict[str, Any]) -> list[str]:
        """Check FAA compliance"""
        violations = []

        if (
            "aerospace" in request.get("operation_type", "")
            or "aviation" in request.get("operation_type", "")
        ) and not request.get("do_178c_certified"):
            violations.append("FAA: DO-178C certification required for airborne software")

        return violations

    def _check_dod_rai(self, request: dict[str, Any]) -> list[str]:
        """Check DoD Responsible AI compliance"""
        violations = []

        if request.get("defense_application"):
            rai_principles = ["responsible", "equitable", "traceable", "reliable", "governable"]
            for principle in rai_principles:
                if not request.get(f"rai_{principle}"):
                    violations.append(f"DoD RAI: Missing '{principle}' principle validation")

        return violations


class EthicalValidator:
    """Validates ethical compliance (Purpose/Reasons/Brakes)"""

    def validate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate ethical compliance"""
        purpose_valid = request.get("purpose") is not None and len(request.get("purpose", "")) > 0
        user_consent = request.get("user_consent", False)
        no_harm_principle = not request.get("potential_harm", False)

        score = (
            (1.0 if purpose_valid else 0.0) * 0.4
            + (1.0 if user_consent else 0.0) * 0.4
            + (1.0 if no_harm_principle else 0.0) * 0.2
        )

        return {
            "compliant": purpose_valid and user_consent and no_harm_principle,
            "purpose_valid": purpose_valid,
            "user_consent": user_consent,
            "no_harm_principle": no_harm_principle,
            "score": score,
        }


class OperationalSafetyValidator:
    """Validates operational safety risks"""

    HIGH_RISK_OPERATIONS = [
        "medical_diagnosis",
        "financial_advice",
        "legal_decision",
        "critical_infrastructure_control",
        "autonomous_vehicle_control",
    ]

    def validate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate operational safety"""
        operation_type = request.get("operation_type", "")
        is_high_risk = operation_type in self.HIGH_RISK_OPERATIONS

        risk_factors = []
        if is_high_risk:
            if not request.get("fallback_mechanism"):
                risk_factors.append("No fallback mechanism for high-risk operation")
            if not request.get("human_oversight"):
                risk_factors.append("No human oversight for high-risk operation")

        score = 1.0 if not risk_factors else max(0.5, 1.0 - len(risk_factors) * 0.2)

        return {
            "compliant": len(risk_factors) == 0,
            "high_risk": is_high_risk,
            "risk_factors": risk_factors,
            "score": score,
        }


class DataSovereigntyValidator:
    """Validates data sovereignty compliance"""

    REGIONAL_REQUIREMENTS = {
        "EU": ["GDPR_compliant", "data_localization"],
        "CHINA": ["cybersecurity_law_compliant", "data_localization", "government_access"],
        "US": ["CCPA_compliant"],
    }

    def validate(self, request: dict[str, Any]) -> dict[str, Any]:
        """Validate data sovereignty"""
        data_region = request.get("data_region", "US")
        operation_region = request.get("operation_region", data_region)

        violations = []

        # Check regional requirements
        if data_region in self.REGIONAL_REQUIREMENTS:
            for requirement in self.REGIONAL_REQUIREMENTS[data_region]:
                if not request.get(requirement):
                    violations.append(f"Missing {data_region} requirement: {requirement}")

        # Check cross-border transfer
        cross_border_transfer = data_region != operation_region
        if cross_border_transfer and not request.get("cross_border_approval"):
            violations.append("Cross-border data transfer requires explicit approval")

        score = 1.0 if not violations else max(0.6, 1.0 - len(violations) * 0.2)

        return {
            "compliant": len(violations) == 0,
            "data_region": data_region,
            "operation_region": operation_region,
            "cross_border_transfer": cross_border_transfer,
            "violations": violations,
            "score": score,
        }
