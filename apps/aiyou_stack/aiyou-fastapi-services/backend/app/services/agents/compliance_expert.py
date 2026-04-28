# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Compliance Expert Agent - AI-powered privacy compliance specialist
Implements GDPR, CCPA, cookie consent, and legal compliance requirements
"""

import json
import logging
from typing import Any

from anthropic import Anthropic

from app.config import settings

logger = logging.getLogger(__name__)


class ComplianceExpertAgent:
    """AI-powered compliance expert that analyzes code, endpoints, and data practices
    for GDPR, CCPA, and other privacy regulation compliance.
    """

    def __init__(self):
        """Initialize the Compliance Expert Agent"""
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL

        self.system_prompt = """You are a Privacy Compliance Expert specializing in GDPR, CCPA, and international data protection laws.

Your responsibilities:
- Analyze code, APIs, and data practices for compliance issues
- Identify privacy risks and data protection violations
- Provide clear, actionable recommendations
- Ensure legal requirements are met without expensive legal consultations
- Focus on practical implementation of privacy regulations

Key regulations you enforce:
1. GDPR (General Data Protection Regulation) - EU
2. CCPA (California Consumer Privacy Act) - California, USA
3. Cookie consent requirements
4. Data retention policies
5. Privacy by design principles

When analyzing code or systems, check for:
- Proper consent mechanisms
- Data minimization
- Purpose limitation
- Storage limitation
- Accuracy and integrity
- Security measures
- User rights (access, deletion, portability)
- Breach notification procedures
- Privacy by design and default
- Data protection impact assessments

Provide responses in JSON format with:
- is_compliant: boolean
- compliance_score: 0-100
- issues: array of issues with severity, description, regulation, recommendation
- recommendations: array of actionable steps
- summary: brief overview

Be thorough but practical. Focus on what matters most for legal compliance."""

    async def analyze_endpoint(
        self,
        endpoint_code: str,
        endpoint_path: str,
        request_method: str = "GET",
    ) -> dict[str, Any]:
        """Analyze an API endpoint for compliance issues

        Args:
            endpoint_code: The source code of the endpoint
            endpoint_path: The URL path of the endpoint
            request_method: HTTP method (GET, POST, etc.)

        Returns:
            Compliance analysis results

        """
        prompt = f"""Analyze this API endpoint for privacy compliance:

Endpoint: {request_method} {endpoint_path}

Code:
```python
{endpoint_code}
```

Check for:
1. Proper authentication and authorization
2. Data access logging (audit trail)
3. PII handling and protection
4. Consent validation before data processing
5. Rate limiting and abuse prevention
6. Error handling that doesn't leak sensitive data
7. GDPR/CCPA compliance for data access
8. Proper data validation and sanitization

Provide detailed compliance analysis in JSON format."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            result_text = response.content[0].text

            # Try to parse as JSON
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # If not JSON, create structured response
                result = {
                    "is_compliant": False,
                    "compliance_score": 50,
                    "issues": [
                        {
                            "severity": "medium",
                            "issue_type": "analysis_error",
                            "description": "Unable to parse compliance analysis",
                            "recommendation": "Manual review required",
                            "regulation": "GENERAL",
                        },
                    ],
                    "recommendations": [result_text],
                    "summary": "Compliance analysis completed",
                }

            return result

        except Exception as e:
            logger.error(f"Error in endpoint analysis: {e}")
            raise

    async def analyze_data_processing(
        self,
        data_type: str,
        processing_purpose: str,
        storage_duration: str,
        third_party_sharing: bool = False,
    ) -> dict[str, Any]:
        """Analyze data processing activity for compliance

        Args:
            data_type: Type of data being processed (e.g., "email", "location")
            processing_purpose: Why the data is being processed
            storage_duration: How long data is stored
            third_party_sharing: Whether data is shared with third parties

        Returns:
            Compliance analysis results

        """
        prompt = f"""Analyze this data processing activity for GDPR/CCPA compliance:

Data Type: {data_type}
Processing Purpose: {processing_purpose}
Storage Duration: {storage_duration}
Third-Party Sharing: {third_party_sharing}

Evaluate:
1. Legal basis for processing (GDPR Art. 6)
2. Purpose limitation compliance
3. Data minimization principles
4. Storage limitation requirements
5. Third-party data sharing compliance
6. Required consent mechanisms
7. User rights that must be supported
8. Data protection impact assessment needs

Provide compliance analysis in JSON format."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            result_text = response.content[0].text

            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = self._create_fallback_response(result_text)

            return result

        except Exception as e:
            logger.error(f"Error in data processing analysis: {e}")
            raise

    async def check_consent_requirements(
        self,
        user_location: str,
        data_categories: list[str],
        processing_purposes: list[str],
    ) -> dict[str, Any]:
        """Determine what consent is required for data processing

        Args:
            user_location: User's location (country code or region)
            data_categories: List of data categories being processed
            processing_purposes: List of processing purposes

        Returns:
            Consent requirements analysis

        """
        prompt = f"""Determine consent requirements for this data processing:

User Location: {user_location}
Data Categories: {", ".join(data_categories)}
Processing Purposes: {", ".join(processing_purposes)}

Analyze:
1. Whether explicit consent is required
2. Which specific consents are needed (functional, analytics, marketing, etc.)
3. Consent method requirements (opt-in vs opt-out)
4. Cookie consent requirements
5. Consent expiration periods
6. Consent withdrawal mechanisms needed
7. GDPR vs CCPA requirements based on location

Provide detailed consent requirements in JSON format."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            result_text = response.content[0].text

            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = self._create_fallback_response(result_text)

            return result

        except Exception as e:
            logger.error(f"Error in consent requirements check: {e}")
            raise

    async def generate_privacy_policy(
        self,
        company_name: str,
        data_practices: list[str],
        user_rights: list[str],
        contact_email: str,
    ) -> str:
        """Generate a privacy policy based on data practices

        Args:
            company_name: Name of the company
            data_practices: List of data collection and processing practices
            user_rights: List of user rights being supported
            contact_email: Contact email for privacy inquiries

        Returns:
            Generated privacy policy text

        """
        prompt = f"""Generate a GDPR and CCPA compliant privacy policy for:

Company: {company_name}
Data Practices: {", ".join(data_practices)}
User Rights Supported: {", ".join(user_rights)}
Privacy Contact: {contact_email}

Include all required sections:
1. Introduction and scope
2. Data controller information
3. Types of data collected
4. Legal basis for processing
5. Purposes of processing
6. Data retention periods
7. Third-party sharing
8. User rights (GDPR & CCPA)
9. Cookies and tracking
10. Security measures
11. International transfers
12. Children's privacy
13. Changes to policy
14. Contact information

Make it clear, comprehensive, and legally compliant."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            policy_text = response.content[0].text
            return policy_text

        except Exception as e:
            logger.error(f"Error generating privacy policy: {e}")
            raise

    async def audit_compliance(
        self,
        system_description: str,
        regulations: list[str] = None,
    ) -> dict[str, Any]:
        """Perform comprehensive compliance audit

        Args:
            system_description: Description of the system to audit
            regulations: List of regulations to check against

        Returns:
            Comprehensive audit results

        """
        if regulations is None:
            regulations = ["GDPR", "CCPA"]
        prompt = f"""Perform a comprehensive compliance audit:

System Description:
{system_description}

Regulations to Check: {", ".join(regulations)}

Audit for:
1. Data collection practices
2. Consent mechanisms
3. User rights implementation
4. Data retention policies
5. Security measures
6. Breach notification procedures
7. Privacy by design implementation
8. Data processing agreements
9. Cookie compliance
10. Cross-border data transfers

Provide detailed audit results with:
- Overall compliance score (0-100)
- Critical issues requiring immediate attention
- Medium/low priority issues
- Recommendations prioritized by importance
- Implementation timeline suggestions

Return results in JSON format."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            result_text = response.content[0].text

            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = self._create_fallback_response(result_text)

            return result

        except Exception as e:
            logger.error(f"Error in compliance audit: {e}")
            raise

    def _create_fallback_response(self, text: str) -> dict[str, Any]:
        """Create a fallback response when JSON parsing fails"""
        return {
            "is_compliant": False,
            "compliance_score": 50,
            "issues": [
                {
                    "severity": "medium",
                    "issue_type": "analysis_incomplete",
                    "description": "Compliance analysis completed but requires review",
                    "recommendation": "Manual review recommended",
                    "regulation": "GENERAL",
                },
            ],
            "recommendations": [text],
            "summary": "Compliance analysis completed - manual review recommended",
        }
