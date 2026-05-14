# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Brakes Validator - JR Engine Component 3

Validates the BRAKES (risks) of an action:
- What could go wrong?
- Are there security threats?
- Are there compliance violations?
- Are there performance/ethical concerns?
"""

import re
from typing import List
from ..models import Action, BrakesVerdict, VerdictStatus, Severity


class BrakesValidator:
    """
    Validates the BRAKES dimension of an action (risk detection)
    """

    def __init__(self):
        # Security threat patterns (simplified for prototype)
        self.threat_patterns = {
            "sql_injection": r"(SELECT|INSERT|UPDATE|DELETE|DROP|UNION).*FROM",
            "xss": r"<script|javascript:|onerror=|onload=",
            "command_injection": r"(;|\||&|`|\$\()",
            "path_traversal": r"\.\./|\.\.\\",
            "xxe": r"<!DOCTYPE|<!ENTITY",
        }

        # Compliance keywords
        self.compliance_keywords = {"pii", "ssn", "credit_card", "password", "secret", "gdpr", "hipaa", "pci", "unauthorized"}

        # Performance concern keywords
        self.performance_keywords = {"infinite_loop", "recursion", "memory_leak", "blocking", "synchronous", "timeout"}

        # Ethical concern keywords
        self.ethical_keywords = {"bias", "discrimination", "privacy", "surveillance", "manipulation", "deception"}

    def validate(self, action: Action) -> BrakesVerdict:
        """
        Validate the brakes (risks) of an action

        Args:
            action: The action to validate

        Returns:
            BrakesVerdict with detected threats and risks
        """
        # Detect security threats
        threats_detected = self._detect_threats(action)

        # Check for compliance violations
        compliance_violations = self._check_compliance(action)

        # Check for performance concerns
        performance_concerns = self._check_performance(action)

        # Check for ethical concerns
        ethical_concerns = self._check_ethics(action)

        # Calculate risk score (0-10, higher = more risky)
        score = self._calculate_risk_score(
            threats_detected,
            compliance_violations,
            performance_concerns,
            ethical_concerns,
        )

        # Determine severity
        severity = self._determine_severity(score, threats_detected)

        # Determine status
        if score >= 8.0:
            status = VerdictStatus.REJECTED  # Critical risk, block
        elif score >= 6.0:
            status = VerdictStatus.REQUIRES_REVIEW  # High risk, review needed
        elif score >= 4.0:
            status = VerdictStatus.FLAGGED  # Medium risk, flag
        else:
            status = VerdictStatus.APPROVED  # Low risk, clear

        explanation = self._generate_explanation(status, score, threats_detected, compliance_violations)

        return BrakesVerdict(
            status=status,
            score=score,
            threats_detected=threats_detected,
            severity=severity,
            compliance_violations=compliance_violations,
            performance_concerns=performance_concerns,
            ethical_concerns=ethical_concerns,
            explanation=explanation,
            confidence=0.90,  # High confidence in threat detection
        )

    def _detect_threats(self, action: Action) -> list[str]:
        """Detect security threats in action"""
        threats = []

        # Check description and context for threat patterns
        text_to_check = f"{action.description} {str(action.context)}"

        for threat_name, pattern in self.threat_patterns.items():
            if re.search(pattern, text_to_check, re.IGNORECASE):
                threats.append(threat_name)

        # Check for sensitive data exposure
        if any(keyword in text_to_check.lower() for keyword in ["password", "secret", "api_key"]):
            threats.append("sensitive_data_exposure")

        return threats

    def _check_compliance(self, action: Action) -> list[str]:
        """Check for compliance violations"""
        violations = []

        text_to_check = f"{action.description} {str(action.context)}".lower()

        # Check for compliance keywords
        if "pii" in text_to_check or "ssn" in text_to_check:
            violations.append("PII handling without consent")

        if "unauthorized" in text_to_check:
            violations.append("Unauthorized access detected")

        # Check for ATP 5-19 violations (simplified)
        if "bypass" in text_to_check or "circumvent" in text_to_check:
            violations.append("ATP 5-19: Authorization bypass attempt")

        return violations

    def _check_performance(self, action: Action) -> list[str]:
        """Check for performance concerns"""
        concerns = []

        text_to_check = f"{action.description} {str(action.context)}".lower()

        for keyword in self.performance_keywords:
            if keyword in text_to_check:
                concerns.append(f"Performance concern: {keyword}")

        # Check for resource-intensive operations
        if "large" in text_to_check and "dataset" in text_to_check:
            concerns.append("Large dataset operation may impact performance")

        return concerns

    def _check_ethics(self, action: Action) -> list[str]:
        """Check for ethical concerns"""
        concerns = []

        text_to_check = f"{action.description} {str(action.context)}".lower()

        for keyword in self.ethical_keywords:
            if keyword in text_to_check:
                concerns.append(f"Ethical concern: {keyword}")

        return concerns

    def _calculate_risk_score(
        self,
        threats: list[str],
        compliance_violations: list[str],
        performance_concerns: list[str],
        ethical_concerns: list[str],
    ) -> float:
        """Calculate overall risk score (0-10, higher = more risky)"""
        score = 0.0

        # Security threats: +3.0 per threat (capped at 9.0)
        score += min(len(threats) * 3.0, 9.0)

        # Compliance violations: +2.0 per violation (capped at 8.0)
        score += min(len(compliance_violations) * 2.0, 8.0)

        # Performance concerns: +0.5 per concern (capped at 2.0)
        score += min(len(performance_concerns) * 0.5, 2.0)

        # Ethical concerns: +1.0 per concern (capped at 3.0)
        score += min(len(ethical_concerns) * 1.0, 3.0)

        return min(10.0, score)

    def _determine_severity(self, score: float, threats: list[str]) -> Severity:
        """Determine severity level based on risk score and threats"""
        if score >= 8.0 or len(threats) >= 3:
            return Severity.CRITICAL
        elif score >= 6.0 or len(threats) >= 2:
            return Severity.HIGH
        elif score >= 4.0 or len(threats) >= 1:
            return Severity.MEDIUM
        elif score >= 2.0:
            return Severity.LOW
        else:
            return Severity.INFO

    def _generate_explanation(
        self,
        status: VerdictStatus,
        score: float,
        threats: list[str],
        compliance_violations: list[str],
    ) -> str:
        """Generate human-readable explanation"""
        if status == VerdictStatus.REJECTED:
            threat_list = ", ".join(threats) if threats else "none"
            violation_list = ", ".join(compliance_violations) if compliance_violations else "none"
            return f"BLOCKED: Critical risk detected (score: {score}/10). Threats: {threat_list}. Violations: {violation_list}."
        elif status == VerdictStatus.REQUIRES_REVIEW:
            return f"HIGH RISK: Requires review (score: {score}/10). {len(threats)} threats, {len(compliance_violations)} violations."
        elif status == VerdictStatus.FLAGGED:
            return f"MEDIUM RISK: Flagged for attention (score: {score}/10). Some concerns detected but not blocking."
        else:  # APPROVED
            return f"CLEAR: No critical risks detected (score: {score}/10). Action appears safe to proceed."
