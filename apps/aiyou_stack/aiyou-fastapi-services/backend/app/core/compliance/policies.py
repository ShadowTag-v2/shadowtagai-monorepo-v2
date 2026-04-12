"""
Compliance Policies - GDPR and CCPA compliance rules and policies
"""

from dataclasses import dataclass
from enum import StrEnum


class Regulation(StrEnum):
    """Privacy regulations"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    PIPEDA = "pipeda"  # Canada
    LGPD = "lgpd"  # Brazil
    POPIA = "popia"  # South Africa


class UserRight(StrEnum):
    """User rights under privacy laws"""

    ACCESS = "access"  # Right to access personal data
    RECTIFICATION = "rectification"  # Right to correct data
    ERASURE = "erasure"  # Right to deletion (right to be forgotten)
    RESTRICTION = "restriction"  # Right to restrict processing
    PORTABILITY = "portability"  # Right to data portability
    OBJECTION = "objection"  # Right to object to processing
    AUTOMATED_DECISION = "automated_decision"  # Rights related to automated decisions
    WITHDRAW_CONSENT = "withdraw_consent"  # Right to withdraw consent


@dataclass
class CompliancePolicy:
    """Compliance policy definition"""

    name: str
    regulation: Regulation
    description: str
    required: bool
    applies_to_all: bool
    jurisdictions: list[str]


class GDPRPolicies:
    """GDPR compliance policies"""

    @staticmethod
    def get_lawful_bases() -> dict[str, str]:
        """GDPR Article 6 - Lawful bases for processing"""
        return {
            "consent": "The individual has given clear consent for you to process their personal data for a specific purpose.",
            "contract": "The processing is necessary for a contract you have with the individual, or because they have asked you to take specific steps before entering into a contract.",
            "legal_obligation": "The processing is necessary for you to comply with the law (not including contractual obligations).",
            "vital_interests": "The processing is necessary to protect someone's life.",
            "public_task": "The processing is necessary for you to perform a task in the public interest or for your official functions.",
            "legitimate_interests": "The processing is necessary for your legitimate interests or the legitimate interests of a third party, unless there is a good reason to protect the individual's personal data which overrides those legitimate interests.",
        }

    @staticmethod
    def get_user_rights() -> dict[UserRight, str]:
        """GDPR user rights"""
        return {
            UserRight.ACCESS: "Right to access their personal data (GDPR Article 15)",
            UserRight.RECTIFICATION: "Right to rectification of inaccurate data (GDPR Article 16)",
            UserRight.ERASURE: "Right to erasure (right to be forgotten) (GDPR Article 17)",
            UserRight.RESTRICTION: "Right to restriction of processing (GDPR Article 18)",
            UserRight.PORTABILITY: "Right to data portability (GDPR Article 20)",
            UserRight.OBJECTION: "Right to object to processing (GDPR Article 21)",
            UserRight.AUTOMATED_DECISION: "Rights related to automated decision making and profiling (GDPR Article 22)",
        }

    @staticmethod
    def get_data_protection_principles() -> dict[str, str]:
        """GDPR Article 5 - Data protection principles"""
        return {
            "lawfulness": "Processed lawfully, fairly and in a transparent manner",
            "purpose_limitation": "Collected for specified, explicit and legitimate purposes",
            "data_minimization": "Adequate, relevant and limited to what is necessary",
            "accuracy": "Accurate and, where necessary, kept up to date",
            "storage_limitation": "Kept in a form which permits identification for no longer than necessary",
            "integrity_confidentiality": "Processed in a manner that ensures appropriate security",
            "accountability": "Controller shall be responsible for and able to demonstrate compliance",
        }

    @staticmethod
    def get_consent_requirements() -> dict[str, bool]:
        """GDPR consent requirements"""
        return {
            "must_be_freely_given": True,
            "must_be_specific": True,
            "must_be_informed": True,
            "must_be_unambiguous": True,
            "must_be_clear_affirmative_action": True,  # No pre-ticked boxes
            "can_be_withdrawn": True,
            "withdrawal_must_be_easy": True,
            "separate_from_other_terms": True,  # Unbundled
            "documented": True,
        }

    @staticmethod
    def get_breach_notification_requirements() -> dict[str, any]:
        """GDPR breach notification requirements"""
        return {
            "notification_to_authority_hours": 72,
            "must_notify_authority": True,
            "must_notify_individuals_if_high_risk": True,
            "must_document_all_breaches": True,
            "required_information": [
                "Nature of breach",
                "Categories and approximate number of individuals concerned",
                "Categories and approximate number of records concerned",
                "Likely consequences",
                "Measures taken or proposed to address the breach",
                "Contact point for more information",
            ],
        }


class CCPAPolicies:
    """CCPA compliance policies"""

    @staticmethod
    def get_consumer_rights() -> dict[str, str]:
        """CCPA consumer rights"""
        return {
            "right_to_know": "Right to know what personal information is collected, used, shared, or sold",
            "right_to_delete": "Right to delete personal information held by businesses",
            "right_to_opt_out": "Right to opt-out of sale of personal information",
            "right_to_non_discrimination": "Right to non-discrimination for exercising CCPA rights",
            "right_to_access": "Right to access personal information in portable format",
        }

    @staticmethod
    def get_disclosure_requirements() -> list[str]:
        """CCPA disclosure requirements"""
        return [
            "Categories of personal information collected",
            "Sources of personal information",
            "Business purpose for collecting or selling",
            "Categories of third parties with whom information is shared",
            "Specific pieces of information collected",
        ]

    @staticmethod
    def get_request_response_times() -> dict[str, int]:
        """CCPA response time requirements (in days)"""
        return {
            "verification_time": 10,
            "response_time": 45,
            "extension_allowed": 45,  # Additional days if needed
        }

    @staticmethod
    def get_do_not_sell_requirements() -> dict[str, bool]:
        """CCPA Do Not Sell requirements"""
        return {
            "must_provide_opt_out": True,
            "must_have_clear_link": True,
            "link_title_must_be_do_not_sell": True,
            "cannot_require_account_creation": True,
            "must_wait_12_months_before_asking_to_opt_in": True,
        }


class CookiePolicy:
    """Cookie compliance policies"""

    @staticmethod
    def get_cookie_categories() -> dict[str, dict[str, any]]:
        """Cookie categories and their requirements"""
        return {
            "necessary": {
                "description": "Essential for website functionality",
                "consent_required": False,
                "examples": ["Session management", "Authentication", "Security"],
            },
            "functional": {
                "description": "Enable enhanced functionality and personalization",
                "consent_required": True,
                "examples": ["Language preferences", "Remember user choices"],
            },
            "analytics": {
                "description": "Help understand how visitors use the website",
                "consent_required": True,
                "examples": ["Google Analytics", "Usage statistics"],
            },
            "advertising": {
                "description": "Used to show relevant ads",
                "consent_required": True,
                "examples": ["Ad targeting", "Retargeting"],
            },
        }

    @staticmethod
    def get_consent_requirements() -> dict[str, bool]:
        """Cookie consent requirements"""
        return {
            "must_get_consent_before_setting": True,
            "must_provide_clear_information": True,
            "must_allow_granular_choice": True,  # Per category
            "must_be_easy_to_withdraw": True,
            "pre_ticked_boxes_not_valid": True,
            "must_provide_cookie_policy": True,
        }


class DataRetentionPolicies:
    """Data retention policy guidelines"""

    @staticmethod
    def get_default_retention_periods() -> dict[str, int]:
        """Default retention periods in days"""
        return {
            "user_accounts": 365 * 3,  # 3 years after account closure
            "audit_logs": 365 * 7,  # 7 years for legal compliance
            "consent_records": 365 * 7,  # 7 years
            "financial_records": 365 * 7,  # 7 years
            "marketing_data": 365 * 2,  # 2 years
            "analytics_data": 365 * 2,  # 2 years
            "session_data": 30,  # 30 days
            "temporary_files": 7,  # 7 days
        }

    @staticmethod
    def get_retention_principles() -> list[str]:
        """Data retention principles"""
        return [
            "Keep data only as long as necessary for the purpose",
            "Define retention periods for each data category",
            "Regularly review and delete outdated data",
            "Document retention policies and reasons",
            "Implement automated deletion where possible",
            "Consider legal hold requirements",
            "Maintain audit trail of deletions",
        ]


class PrivacyByDesign:
    """Privacy by design principles"""

    @staticmethod
    def get_principles() -> dict[str, str]:
        """Privacy by design principles"""
        return {
            "proactive": "Proactive not reactive; preventive not remedial",
            "privacy_default": "Privacy as the default setting",
            "privacy_embedded": "Privacy embedded into design",
            "full_functionality": "Full functionality - positive-sum, not zero-sum",
            "end_to_end": "End-to-end security - full lifecycle protection",
            "visibility_transparency": "Visibility and transparency - keep it open",
            "respect_privacy": "Respect for user privacy - keep it user-centric",
        }


# Compliance policy registry
COMPLIANCE_POLICIES: list[CompliancePolicy] = [
    CompliancePolicy(
        name="GDPR Lawful Basis",
        regulation=Regulation.GDPR,
        description="Ensure processing has a lawful basis under GDPR Article 6",
        required=True,
        applies_to_all=False,
        jurisdictions=["EU", "EEA", "UK"],
    ),
    CompliancePolicy(
        name="GDPR User Rights",
        regulation=Regulation.GDPR,
        description="Implement all GDPR user rights",
        required=True,
        applies_to_all=False,
        jurisdictions=["EU", "EEA", "UK"],
    ),
    CompliancePolicy(
        name="CCPA Consumer Rights",
        regulation=Regulation.CCPA,
        description="Implement CCPA consumer rights",
        required=True,
        applies_to_all=False,
        jurisdictions=["California", "US"],
    ),
    CompliancePolicy(
        name="Cookie Consent",
        regulation=Regulation.GDPR,
        description="Obtain valid consent for non-essential cookies",
        required=True,
        applies_to_all=False,
        jurisdictions=["EU", "EEA", "UK"],
    ),
    CompliancePolicy(
        name="Data Breach Notification",
        regulation=Regulation.GDPR,
        description="72-hour breach notification requirement",
        required=True,
        applies_to_all=True,
        jurisdictions=["ALL"],
    ),
]
