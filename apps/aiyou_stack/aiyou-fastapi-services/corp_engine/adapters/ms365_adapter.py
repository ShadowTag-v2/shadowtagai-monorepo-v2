"""Microsoft 365 Enterprise Adapter
=================================
API-only integration with customer MS365 environments.
All processing happens in our GCP infrastructure.

Supported Services:
- Microsoft Graph API (Users, Groups, Mail, Calendar, OneDrive, SharePoint)
- Azure AD (Authentication, Authorization)
- Microsoft Teams (Channels, Messages, Meetings)
- Power Platform (Power Automate, Power BI)

Architecture:
- Customer grants OAuth2 consent
- We access via Graph API
- All data processed in GCP
- Changes pushed back via API
"""

import logging
from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel, Field

from .base_adapter import (
    AdapterConfig,
    AdapterStatus,
    BaseAdapter,
    ConnectionHealth,
    SyncResult,
)

logger = logging.getLogger(__name__)

# Type for MS365 entities
MS365Entity = TypeVar("MS365Entity", bound=dict[str, Any])


class MS365Config(AdapterConfig):
    """Microsoft 365 specific configuration"""

    adapter_type: str = "ms365"

    # Azure AD App Registration
    tenant_id: str  # Azure AD tenant ID
    client_id: str  # App registration client ID
    # client_secret stored in GCP Secret Manager via credentials_vault_key

    # Scopes requested
    scopes: list[str] = Field(
        default_factory=lambda: [
            "User.Read.All",
            "Group.Read.All",
            "Mail.Read",
            "Calendar.Read",
            "Files.Read.All",
            "Sites.Read.All",
        ],
    )

    # Services to sync
    sync_users: bool = True
    sync_groups: bool = True
    sync_mail: bool = False  # Opt-in for mail
    sync_calendar: bool = False
    sync_files: bool = False
    sync_teams: bool = False

    # Write permissions (conservative defaults)
    write_users: bool = False
    write_groups: bool = False
    write_mail: bool = False


class MS365User(BaseModel):
    """Microsoft 365 User entity"""

    id: str
    display_name: str
    user_principal_name: str
    mail: str | None = None
    job_title: str | None = None
    department: str | None = None
    office_location: str | None = None
    mobile_phone: str | None = None
    last_sign_in: datetime | None = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class MS365Group(BaseModel):
    """Microsoft 365 Group entity"""

    id: str
    display_name: str
    description: str | None = None
    mail: str | None = None
    group_types: list[str] = Field(default_factory=list)
    member_count: int = 0
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class MS365Adapter(BaseAdapter[MS365Entity]):
    """Microsoft 365 Enterprise Adapter.

    Connects to customer MS365 via Graph API.
    All data processing happens in our GCP infrastructure.
    Customer sees improved analytics, recommendations, and automation.
    """

    ADAPTER_TYPE = "ms365"
    ADAPTER_VERSION = "1.0.0"

    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    GRAPH_API_BETA = "https://graph.microsoft.com/beta"

    def __init__(self, config: MS365Config):
        super().__init__(config)
        self.ms365_config = config
        self._access_token: str | None = None
        self._token_expiry: datetime | None = None
        self._cached_users: dict[str, MS365User] = {}
        self._cached_groups: dict[str, MS365Group] = {}

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> bool:
        """Connect to Microsoft 365 via OAuth2.
        Uses client credentials flow for app-only access.
        """
        self.health.status = AdapterStatus.CONNECTING

        try:
            # Get client secret from GCP Secret Manager
            client_secret = await self._get_secret(self.ms365_config.credentials_vault_key)

            # Request access token
            token_response = await self._request_token(client_secret)

            if token_response and "access_token" in token_response:
                self._access_token = token_response["access_token"]
                self._token_expiry = datetime.utcnow()  # + expires_in
                self.health.status = AdapterStatus.CONNECTED
                logger.info(f"MS365 adapter connected for tenant {self.ms365_config.tenant_id}")
                return True
            self.health.status = AdapterStatus.ERROR
            self.health.last_error = "Failed to obtain access token"
            return False

        except Exception as e:
            self.health.status = AdapterStatus.ERROR
            self.health.last_error = str(e)
            logger.error(f"MS365 connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from Microsoft 365"""
        self._access_token = None
        self._token_expiry = None
        self.health.status = AdapterStatus.DISCONNECTED
        logger.info(f"MS365 adapter disconnected for tenant {self.ms365_config.tenant_id}")
        return True

    async def test_connection(self) -> ConnectionHealth:
        """Test Microsoft 365 connection"""
        try:
            # Try to fetch organization info
            response = await self._graph_request("GET", "/organization")

            if response:
                self.health.status = AdapterStatus.CONNECTED
                self.health.last_error = None
            else:
                self.health.status = AdapterStatus.ERROR
                self.health.last_error = "Graph API test failed"

        except Exception as e:
            self.health.status = AdapterStatus.ERROR
            self.health.last_error = str(e)

        return self.health

    # =========================================================================
    # Data Operations
    # =========================================================================

    async def fetch_data(self, query: dict[str, Any]) -> list[MS365Entity]:
        """Fetch data from Microsoft 365.
        Routes to appropriate service based on query.
        """
        data_type = query.get("type", "users")
        batch_size = query.get("batch_size", self.config.batch_size)
        modified_since = query.get("modified_since")

        if data_type == "users":
            return await self._fetch_users(batch_size, modified_since)
        if data_type == "groups":
            return await self._fetch_groups(batch_size, modified_since)
        if data_type == "mail":
            return await self._fetch_mail(query.get("user_id"), batch_size)
        if data_type == "calendar":
            return await self._fetch_calendar(query.get("user_id"), batch_size)
        if data_type == "files":
            return await self._fetch_files(query.get("site_id"), batch_size)
        logger.warning(f"Unknown MS365 data type: {data_type}")
        return []

    async def push_data(self, data: list[MS365Entity]) -> SyncResult:
        """Push data back to Microsoft 365.
        Only enabled for configured write operations.
        """
        result = SyncResult(
            success=True,
            adapter_id=self.config.adapter_id,
            operation="push",
        )

        for item in data:
            try:
                item_type = item.get("_type", "unknown")

                if item_type == "user" and self.ms365_config.write_users:
                    await self._update_user(item)
                    result.records_updated += 1
                elif item_type == "group" and self.ms365_config.write_groups:
                    await self._update_group(item)
                    result.records_updated += 1
                else:
                    logger.warning(f"Write not enabled for type: {item_type}")

            except Exception as e:
                result.records_failed += 1
                result.errors.append(str(e))

        return result

    async def get_schema(self) -> dict[str, Any]:
        """Get Microsoft 365 schema information"""
        return {
            "services": {
                "users": {
                    "enabled": self.ms365_config.sync_users,
                    "write_enabled": self.ms365_config.write_users,
                    "fields": ["id", "displayName", "userPrincipalName", "mail", "jobTitle"],
                },
                "groups": {
                    "enabled": self.ms365_config.sync_groups,
                    "write_enabled": self.ms365_config.write_groups,
                    "fields": ["id", "displayName", "description", "mail", "groupTypes"],
                },
                "mail": {
                    "enabled": self.ms365_config.sync_mail,
                    "write_enabled": self.ms365_config.write_mail,
                    "fields": ["id", "subject", "from", "toRecipients", "receivedDateTime"],
                },
                "calendar": {
                    "enabled": self.ms365_config.sync_calendar,
                    "fields": ["id", "subject", "start", "end", "attendees"],
                },
                "files": {
                    "enabled": self.ms365_config.sync_files,
                    "fields": ["id", "name", "size", "createdDateTime", "lastModifiedDateTime"],
                },
            },
            "api_version": "v1.0",
            "graph_endpoint": self.GRAPH_API_BASE,
        }

    # =========================================================================
    # Service-Specific Fetchers
    # =========================================================================

    async def _fetch_users(
        self,
        batch_size: int,
        modified_since: str | None,
    ) -> list[dict[str, Any]]:
        """Fetch users from Azure AD"""
        endpoint = "/users"
        params = {
            "$top": batch_size,
            "$select": "id,displayName,userPrincipalName,mail,jobTitle,department,officeLocation,mobilePhone",
        }

        if modified_since:
            # Delta query for incremental sync
            params["$filter"] = f"lastModifiedDateTime ge {modified_since}"

        response = await self._graph_request("GET", endpoint, params=params)

        users = []
        if response and "value" in response:
            for user_data in response["value"]:
                user = MS365User(
                    id=user_data["id"],
                    display_name=user_data.get("displayName", ""),
                    user_principal_name=user_data.get("userPrincipalName", ""),
                    mail=user_data.get("mail"),
                    job_title=user_data.get("jobTitle"),
                    department=user_data.get("department"),
                    office_location=user_data.get("officeLocation"),
                    mobile_phone=user_data.get("mobilePhone"),
                )
                self._cached_users[user.id] = user
                users.append({"_type": "user", **user.model_dump()})

        return users

    async def _fetch_groups(
        self,
        batch_size: int,
        modified_since: str | None,
    ) -> list[dict[str, Any]]:
        """Fetch groups from Azure AD"""
        endpoint = "/groups"
        params = {
            "$top": batch_size,
            "$select": "id,displayName,description,mail,groupTypes",
        }

        response = await self._graph_request("GET", endpoint, params=params)

        groups = []
        if response and "value" in response:
            for group_data in response["value"]:
                group = MS365Group(
                    id=group_data["id"],
                    display_name=group_data.get("displayName", ""),
                    description=group_data.get("description"),
                    mail=group_data.get("mail"),
                    group_types=group_data.get("groupTypes", []),
                )
                self._cached_groups[group.id] = group
                groups.append({"_type": "group", **group.model_dump()})

        return groups

    async def _fetch_mail(self, user_id: str | None, batch_size: int) -> list[dict[str, Any]]:
        """Fetch mail messages"""
        if not user_id or not self.ms365_config.sync_mail:
            return []

        endpoint = f"/users/{user_id}/messages"
        params = {
            "$top": batch_size,
            "$select": "id,subject,from,toRecipients,receivedDateTime,bodyPreview",
            "$orderby": "receivedDateTime desc",
        }

        response = await self._graph_request("GET", endpoint, params=params)

        messages = []
        if response and "value" in response:
            for msg in response["value"]:
                messages.append(
                    {
                        "_type": "mail",
                        "id": msg["id"],
                        "subject": msg.get("subject", ""),
                        "from": msg.get("from", {}),
                        "to_recipients": msg.get("toRecipients", []),
                        "received_at": msg.get("receivedDateTime"),
                        "body_preview": msg.get("bodyPreview", ""),
                    },
                )

        return messages

    async def _fetch_calendar(self, user_id: str | None, batch_size: int) -> list[dict[str, Any]]:
        """Fetch calendar events"""
        if not user_id or not self.ms365_config.sync_calendar:
            return []

        endpoint = f"/users/{user_id}/calendar/events"
        params = {
            "$top": batch_size,
            "$select": "id,subject,start,end,attendees,location",
            "$orderby": "start/dateTime desc",
        }

        response = await self._graph_request("GET", endpoint, params=params)

        events = []
        if response and "value" in response:
            for event in response["value"]:
                events.append(
                    {
                        "_type": "calendar_event",
                        "id": event["id"],
                        "subject": event.get("subject", ""),
                        "start": event.get("start", {}),
                        "end": event.get("end", {}),
                        "attendees": event.get("attendees", []),
                        "location": event.get("location", {}),
                    },
                )

        return events

    async def _fetch_files(self, site_id: str | None, batch_size: int) -> list[dict[str, Any]]:
        """Fetch files from SharePoint/OneDrive"""
        if not self.ms365_config.sync_files:
            return []

        # Default to root site if not specified
        endpoint = f"/sites/{site_id}/drive/root/children" if site_id else "/me/drive/root/children"
        params = {
            "$top": batch_size,
            "$select": "id,name,size,createdDateTime,lastModifiedDateTime,file,folder",
        }

        response = await self._graph_request("GET", endpoint, params=params)

        files = []
        if response and "value" in response:
            for item in response["value"]:
                files.append(
                    {
                        "_type": "file",
                        "id": item["id"],
                        "name": item.get("name", ""),
                        "size": item.get("size", 0),
                        "created_at": item.get("createdDateTime"),
                        "modified_at": item.get("lastModifiedDateTime"),
                        "is_folder": "folder" in item,
                    },
                )

        return files

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def _update_user(self, user_data: dict[str, Any]) -> None:
        """Update user in Azure AD"""
        user_id = user_data.get("id")
        if not user_id:
            raise ValueError("User ID required for update")

        # Only update allowed fields
        update_payload = {}
        allowed_fields = ["displayName", "jobTitle", "department", "officeLocation"]

        for field in allowed_fields:
            if field in user_data:
                update_payload[field] = user_data[field]

        if update_payload:
            await self._graph_request("PATCH", f"/users/{user_id}", json=update_payload)

    async def _update_group(self, group_data: dict[str, Any]) -> None:
        """Update group in Azure AD"""
        group_id = group_data.get("id")
        if not group_id:
            raise ValueError("Group ID required for update")

        update_payload = {}
        allowed_fields = ["displayName", "description"]

        for field in allowed_fields:
            if field in group_data:
                update_payload[field] = group_data[field]

        if update_payload:
            await self._graph_request("PATCH", f"/groups/{group_id}", json=update_payload)

    # =========================================================================
    # API Helpers
    # =========================================================================

    async def _graph_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Make a request to Microsoft Graph API"""
        if not self._access_token:
            await self.connect()

        # In production, use aiohttp or httpx
        # This is a placeholder showing the structure
        url = f"{self.GRAPH_API_BASE}{endpoint}"


        # Placeholder - actual HTTP call would go here
        logger.debug(f"MS365 API: {method} {url}")

        # Simulate response for structure purposes
        return {"value": []}

    async def _request_token(self, client_secret: str) -> dict[str, Any] | None:
        """Request OAuth2 access token"""
        # In production, call Azure AD token endpoint
        token_url = (
            f"https://login.microsoftonline.com/{self.ms365_config.tenant_id}/oauth2/v2.0/token"
        )


        # Placeholder - actual HTTP call would go here
        logger.debug(f"Requesting token from {token_url}")

        return {"access_token": "placeholder_token", "expires_in": 3600}

    async def _get_secret(self, _secret_name: str) -> str:
        """Get secret from GCP Secret Manager"""
        # In production, use google-cloud-secret-manager
        # This is a placeholder
        return "placeholder_secret"

    # =========================================================================
    # Value Calculation
    # =========================================================================

    async def _process_data(self, data: list[MS365Entity]) -> list[MS365Entity]:
        """Process MS365 data through our AI pipeline.
        This is where the Economic Juggernaut adds value.
        """
        processed = []

        for item in data:
            # Add AI-enhanced insights
            item["_ai_insights"] = {
                "processed_at": datetime.utcnow().isoformat(),
                "processor": "economic_juggernaut",
            }

            # Example: Analyze user engagement
            if item.get("_type") == "user":
                item["_ai_insights"]["engagement_score"] = 0.85  # Placeholder

            # Example: Group health analysis
            elif item.get("_type") == "group":
                item["_ai_insights"]["collaboration_score"] = 0.72  # Placeholder

            processed.append(item)

        return processed

    async def _calculate_value_added(self, original: list[Any], processed: list[Any]) -> float:
        """Calculate value added by MS365 integration.

        Value sources:
        - Time saved on manual data analysis
        - Improved collaboration insights
        - Automated user provisioning recommendations
        - Security posture improvements
        """
        base_value = len(processed) * 0.05  # $0.05 per record processed

        # Additional value for specific insights
        for item in processed:
            if item.get("_ai_insights"):
                base_value += 0.02  # Additional for AI enhancement

        return base_value
