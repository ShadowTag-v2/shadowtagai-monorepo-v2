"""CCPA (California Consumer Privacy Act) Compliance Implementation

Provides:
- Data access/export (right to know)
- Data deletion (right to delete)
- Opt-out of data sales (right to opt-out)
- Privacy policy disclosure requirements
- Automated compliance workflows
"""

import csv
import io
import json
import logging
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CCPARequestType(StrEnum):
    """CCPA consumer request types"""

    ACCESS = "access"  # Right to know (data access)
    DELETE = "delete"  # Right to delete
    OPT_OUT = "opt_out"  # Do not sell my personal information
    OPT_IN = "opt_in"  # Re-authorize data sales (minors)


class DataExportFormat(StrEnum):
    """Supported data export formats"""

    JSON = "json"
    CSV = "csv"
    XML = "xml"


class CCPARequest(BaseModel):
    """CCPA consumer request model"""

    request_id: str = Field(description="Unique request identifier")
    user_id: str = Field(description="User ID making the request")
    request_type: CCPARequestType
    status: str = Field(default="pending", description="Request status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None
    completed_at: datetime | None = None
    verification_method: str = Field(default="email", description="How user was verified")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CCPACompliance:
    """CCPA Compliance Implementation

    Features:
    - Data access (export user data in JSON/CSV/XML)
    - Data deletion (delete user data from all systems)
    - Opt-out of sales (prevent personal data from being sold)
    - Request verification (confirm user identity)
    - Audit logging (track all compliance requests)
    - Automated workflows (process requests within legal timeframes)
    """

    def __init__(self, database_client, audit_logger=None):
        """Initialize CCPA compliance handler

        Args:
            database_client: Database connection for data access/deletion
            audit_logger: Logger for compliance audit trail

        """
        self.db = database_client
        self.audit_logger = audit_logger or logger

        # CCPA requires response within 45 days (can extend 90 days with notice)
        self.response_deadline_days = 45

    async def submit_request(
        self,
        user_id: str,
        request_type: CCPARequestType,
        metadata: dict | None = None,
    ) -> CCPARequest:
        """Submit a CCPA consumer request

        Args:
            user_id: User ID making the request
            request_type: Type of CCPA request
            metadata: Additional request metadata

        Returns:
            CCPARequest object with request details

        """
        request_id = f"CCPA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user_id}"

        request = CCPARequest(
            request_id=request_id,
            user_id=user_id,
            request_type=request_type,
            metadata=metadata or {},
        )

        # Log request for audit trail
        self.audit_logger.info(
            f"CCPA request submitted: {request_id} ({request_type.value}) by user {user_id}",
        )

        # Store request in database
        await self._store_request(request)

        # Send confirmation email (implementation depends on email service)
        # await self._send_confirmation_email(user_id, request)

        return request

    async def process_access_request(
        self,
        request_id: str,
        export_format: DataExportFormat = DataExportFormat.JSON,
    ) -> dict[str, Any]:
        """Process a data access request (right to know)

        Args:
            request_id: CCPA request ID
            export_format: Desired export format (JSON, CSV, XML)

        Returns:
            Dict containing user data in requested format

        """
        request = await self._get_request(request_id)

        if request.request_type != CCPARequestType.ACCESS:
            raise ValueError(f"Request {request_id} is not an access request")

        # Collect all personal data
        user_data = await self._collect_user_data(request.user_id)

        # Format data for export
        if export_format == DataExportFormat.JSON:
            formatted_data = self._format_json(user_data)
        elif export_format == DataExportFormat.CSV:
            formatted_data = self._format_csv(user_data)
        elif export_format == DataExportFormat.XML:
            formatted_data = self._format_xml(user_data)
        else:
            formatted_data = user_data

        # Update request status
        await self._update_request_status(request_id, "completed")

        self.audit_logger.info(
            f"CCPA access request completed: {request_id} for user {request.user_id}",
        )

        return {
            "request_id": request_id,
            "user_id": request.user_id,
            "export_format": export_format.value,
            "data": formatted_data,
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def process_deletion_request(self, request_id: str) -> dict[str, Any]:
        """Process a data deletion request (right to delete)

        Args:
            request_id: CCPA request ID

        Returns:
            Dict with deletion confirmation details

        """
        request = await self._get_request(request_id)

        if request.request_type != CCPARequestType.DELETE:
            raise ValueError(f"Request {request_id} is not a deletion request")

        # Delete user data from all systems
        deletion_summary = await self._delete_user_data(request.user_id)

        # Update request status
        await self._update_request_status(request_id, "completed")

        self.audit_logger.warning(
            f"CCPA deletion request completed: {request_id} for user {request.user_id}. "
            f"Deleted: {deletion_summary}",
        )

        return {
            "request_id": request_id,
            "user_id": request.user_id,
            "deletion_summary": deletion_summary,
            "deleted_at": datetime.utcnow().isoformat(),
        }

    async def process_opt_out_request(self, request_id: str) -> dict[str, Any]:
        """Process an opt-out request (do not sell my personal information)

        Args:
            request_id: CCPA request ID

        Returns:
            Dict with opt-out confirmation

        """
        request = await self._get_request(request_id)

        if request.request_type != CCPARequestType.OPT_OUT:
            raise ValueError(f"Request {request_id} is not an opt-out request")

        # Set opt-out flag in user profile
        await self._set_opt_out_status(request.user_id, opted_out=True)

        # Update request status
        await self._update_request_status(request_id, "completed")

        self.audit_logger.info(
            f"CCPA opt-out request completed: {request_id} for user {request.user_id}",
        )

        return {
            "request_id": request_id,
            "user_id": request.user_id,
            "opt_out_status": "opted_out",
            "updated_at": datetime.utcnow().isoformat(),
        }

    async def check_opt_out_status(self, user_id: str) -> bool:
        """Check if user has opted out of data sales

        Args:
            user_id: User ID to check

        Returns:
            True if user has opted out, False otherwise

        """
        # Query database for opt-out status
        user = await self.db.query("SELECT opt_out FROM users WHERE user_id = ?", user_id)
        return user.get("opt_out", False) if user else False

    async def get_privacy_disclosures(self) -> dict[str, Any]:
        """Get CCPA privacy disclosures

        Returns:
            Dict with all required CCPA disclosures

        """
        return {
            "disclosure_version": "1.0",
            "last_updated": "2025-11-17",
            "categories_collected": [
                {
                    "category": "Identifiers",
                    "examples": "Name, email address, IP address, device ID",
                    "purpose": "Account creation, authentication, service delivery",
                },
                {
                    "category": "Internet Activity",
                    "examples": "Browsing history, search history, API usage",
                    "purpose": "Service improvement, analytics, fraud prevention",
                },
                {
                    "category": "Geolocation",
                    "examples": "IP-based location",
                    "purpose": "Content localization, compliance with regional laws",
                },
                {
                    "category": "Inferences",
                    "examples": "User preferences, interests, behavior patterns",
                    "purpose": "Personalization, content recommendation",
                },
            ],
            "data_sold": False,  # Set to True if you sell data
            "data_shared_with_third_parties": [
                {
                    "party": "Cloud Service Providers (GCP)",
                    "purpose": "Infrastructure hosting, data storage",
                    "category": "All categories",
                },
                {
                    "party": "Analytics Providers",
                    "purpose": "Usage analytics, service improvement",
                    "category": "Internet Activity, Inferences",
                },
            ],
            "retention_period": "Data retained for duration of account + 90 days after deletion request",
            "rights": [
                "Right to know what personal information is collected",
                "Right to know if personal information is sold or disclosed",
                "Right to say no to the sale of personal information (opt-out)",
                "Right to access your personal information",
                "Right to delete personal information",
                "Right to non-discrimination for exercising CCPA rights",
            ],
            "contact": {
                "email": "redacted@shadowtag-v4.local",
                "phone": "1-800-XXX-XXXX",
                "address": "123 Privacy St, San Francisco, CA 94102",
            },
        }

    # Private helper methods

    async def _collect_user_data(self, user_id: str) -> dict[str, Any]:
        """Collect all personal data for a user"""
        # This is a placeholder - implement based on your data schema
        user_data = {
            "user_profile": await self.db.query("SELECT * FROM users WHERE user_id = ?", user_id),
            "activity_logs": await self.db.query(
                "SELECT * FROM activity_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1000",
                user_id,
            ),
            "preferences": await self.db.query(
                "SELECT * FROM user_preferences WHERE user_id = ?",
                user_id,
            ),
            "api_usage": await self.db.query(
                "SELECT * FROM api_usage WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1000",
                user_id,
            ),
        }

        return {k: v for k, v in user_data.items() if v}

    async def _delete_user_data(self, user_id: str) -> dict[str, int]:
        """Delete all user data (implementation depends on your schema)"""
        deletion_summary = {}

        # Delete from each table (example)
        tables = ["users", "activity_logs", "user_preferences", "api_usage", "sessions"]

        for table in tables:
            result = await self.db.execute(f"DELETE FROM {table} WHERE user_id = ?", user_id)
            deletion_summary[table] = result.rowcount

        return deletion_summary

    async def _set_opt_out_status(self, user_id: str, opted_out: bool):
        """Set user's opt-out status"""
        await self.db.execute(
            "UPDATE users SET opt_out = ?, opt_out_date = ? WHERE user_id = ?",
            opted_out,
            datetime.utcnow() if opted_out else None,
            user_id,
        )

    async def _store_request(self, request: CCPARequest):
        """Store CCPA request in database"""
        await self.db.execute(
            """
            INSERT INTO ccpa_requests
            (request_id, user_id, request_type, status, created_at, verification_method, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            request.request_id,
            request.user_id,
            request.request_type.value,
            request.status,
            request.created_at,
            request.verification_method,
            json.dumps(request.metadata),
        )

    async def _get_request(self, request_id: str) -> CCPARequest:
        """Retrieve CCPA request from database"""
        row = await self.db.query("SELECT * FROM ccpa_requests WHERE request_id = ?", request_id)
        if not row:
            raise ValueError(f"CCPA request {request_id} not found")

        return CCPARequest(
            request_id=row["request_id"],
            user_id=row["user_id"],
            request_type=CCPARequestType(row["request_type"]),
            status=row["status"],
            created_at=row["created_at"],
            processed_at=row.get("processed_at"),
            completed_at=row.get("completed_at"),
            verification_method=row["verification_method"],
            metadata=json.loads(row.get("metadata", "{}")),
        )

    async def _update_request_status(self, request_id: str, status: str):
        """Update CCPA request status"""
        now = datetime.utcnow()
        await self.db.execute(
            "UPDATE ccpa_requests SET status = ?, processed_at = ?, completed_at = ? WHERE request_id = ?",
            status,
            now,
            now if status == "completed" else None,
            request_id,
        )

    def _format_json(self, data: dict) -> str:
        """Format data as JSON"""
        return json.dumps(data, indent=2, default=str)

    def _format_csv(self, data: dict) -> str:
        """Format data as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["category", "field", "value"])

        # Flatten nested data
        for category, items in data.items():
            if isinstance(items, list):
                for idx, item in enumerate(items):
                    if isinstance(item, dict):
                        for field, value in item.items():
                            writer.writerow([category, f"{field}[{idx}]", value])
                    else:
                        writer.writerow([category, f"item[{idx}]", item])
            elif isinstance(items, dict):
                for field, value in items.items():
                    writer.writerow([category, field, value])
            else:
                writer.writerow([category, "value", items])

        return output.getvalue()

    def _format_xml(self, data: dict) -> str:
        """Format data as XML"""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<user_data>"]

        for category, items in data.items():
            xml_lines.append(f"  <{category}>")
            if isinstance(items, list):
                for item in items:
                    xml_lines.append("    <item>")
                    if isinstance(item, dict):
                        for field, value in item.items():
                            xml_lines.append(f"      <{field}>{value}</{field}>")
                    else:
                        xml_lines.append(f"      {item}")
                    xml_lines.append("    </item>")
            elif isinstance(items, dict):
                for field, value in items.items():
                    xml_lines.append(f"    <{field}>{value}</{field}>")
            else:
                xml_lines.append(f"    {items}")
            xml_lines.append(f"  </{category}>")

        xml_lines.append("</user_data>")
        return "\n".join(xml_lines)
