"""
GDPR (General Data Protection Regulation) Compliance Implementation

Provides:
- Data portability (export user data)
- Right to erasure (delete user data)
- Consent management
- Data processing records
- Breach notification
"""

from datetime import datetime

from .ccpa import CCPACompliance


class GDPRCompliance(CCPACompliance):
    """
    GDPR Compliance Implementation

    Extends CCPA compliance with GDPR-specific features.
    Many requirements overlap with CCPA (data access, deletion).
    """

    def __init__(self, database_client, audit_logger=None):
        super().__init__(database_client, audit_logger)
        # GDPR requires response within 30 days (can extend 60 days with justification)
        self.response_deadline_days = 30

    async def process_data_portability_request(self, user_id: str):
        """
        Process GDPR data portability request (Article 20)

        Similar to CCPA access request but with structured, machine-readable format
        """
        # Reuse CCPA access request logic
        from .ccpa import DataExportFormat

        return await self.process_access_request(
            f"GDPR-{user_id}", export_format=DataExportFormat.JSON
        )

    async def check_consent(self, user_id: str, purpose: str) -> bool:
        """
        Check if user has given consent for a specific purpose

        Args:
            user_id: User ID
            purpose: Purpose of data processing (e.g., "marketing", "analytics")

        Returns:
            True if consent given, False otherwise
        """
        result = await self.db.query(
            "SELECT consent FROM user_consents WHERE user_id = ? AND purpose = ?",
            user_id,
            purpose,
        )
        return result.get("consent", False) if result else False

    async def record_consent(self, user_id: str, purpose: str, granted: bool):
        """
        Record user consent for a specific purpose

        Args:
            user_id: User ID
            purpose: Purpose of data processing
            granted: Whether consent was granted
        """
        await self.db.execute(
            """
            INSERT OR REPLACE INTO user_consents (user_id, purpose, consent, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            user_id,
            purpose,
            granted,
            datetime.utcnow(),
        )

        self.audit_logger.info(
            f"GDPR consent recorded: user {user_id}, purpose {purpose}, granted {granted}"
        )
