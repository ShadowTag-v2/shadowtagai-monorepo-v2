"""
Salesforce Enterprise Adapter
==============================
API-only integration with customer Salesforce environments.
All processing happens in our GCP infrastructure.

Supported Features:
- Salesforce REST API
- SOQL Queries
- Bulk API for large data sets
- Streaming API for real-time updates
- Metadata API for schema discovery

Objects Supported:
- Accounts, Contacts, Leads, Opportunities
- Cases, Tasks, Events
- Custom Objects

Architecture:
- Customer grants OAuth2 consent (Connected App)
- We access via REST/Bulk APIs
- All data processed in GCP
- Insights and automation pushed back
"""

import asyncio
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

# Type for Salesforce records
SFRecord = TypeVar("SFRecord", bound=dict[str, Any])


class SalesforceConfig(AdapterConfig):
    """Salesforce specific configuration"""

    adapter_type: str = "salesforce"

    # Salesforce OAuth settings
    instance_url: str  # e.g., https://mycompany.salesforce.com
    consumer_key: str  # Connected App consumer key
    # consumer_secret stored in GCP Secret Manager via credentials_vault_key

    # API version
    api_version: str = "v59.0"

    # Objects to sync
    sync_accounts: bool = True
    sync_contacts: bool = True
    sync_leads: bool = True
    sync_opportunities: bool = True
    sync_cases: bool = False
    sync_custom_objects: list[str] = Field(default_factory=list)

    # Write permissions
    write_accounts: bool = False
    write_contacts: bool = False
    write_leads: bool = False
    write_opportunities: bool = False

    # Bulk API settings
    use_bulk_api: bool = True
    bulk_threshold: int = 1000  # Use bulk API for more than this many records


class SalesforceAccount(BaseModel):
    """Salesforce Account object"""

    id: str
    name: str
    account_type: str | None = None
    industry: str | None = None
    annual_revenue: float | None = None
    number_of_employees: int | None = None
    billing_city: str | None = None
    billing_country: str | None = None
    owner_id: str | None = None
    created_date: datetime | None = None
    last_modified_date: datetime | None = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class SalesforceContact(BaseModel):
    """Salesforce Contact object"""

    id: str
    first_name: str | None = None
    last_name: str
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    account_id: str | None = None
    department: str | None = None
    mailing_city: str | None = None
    owner_id: str | None = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class SalesforceLead(BaseModel):
    """Salesforce Lead object"""

    id: str
    first_name: str | None = None
    last_name: str
    company: str
    email: str | None = None
    phone: str | None = None
    status: str | None = None
    lead_source: str | None = None
    rating: str | None = None
    industry: str | None = None
    owner_id: str | None = None
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class SalesforceOpportunity(BaseModel):
    """Salesforce Opportunity object"""

    id: str
    name: str
    account_id: str | None = None
    amount: float | None = None
    stage_name: str
    probability: float | None = None
    close_date: datetime | None = None
    type: str | None = None
    lead_source: str | None = None
    owner_id: str | None = None
    is_closed: bool = False
    is_won: bool = False
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class SalesforceAdapter(BaseAdapter[SFRecord]):
    """
    Salesforce Enterprise Adapter.

    Connects to customer Salesforce via REST API.
    All data processing happens in our GCP infrastructure.
    Customer sees improved lead scoring, pipeline insights, and automation.
    """

    ADAPTER_TYPE = "salesforce"
    ADAPTER_VERSION = "1.0.0"

    def __init__(self, config: SalesforceConfig):
        super().__init__(config)
        self.sf_config = config
        self._access_token: str | None = None
        self._instance_url: str | None = None
        self._token_expiry: datetime | None = None

        # Caches for objects
        self._accounts: dict[str, SalesforceAccount] = {}
        self._contacts: dict[str, SalesforceContact] = {}
        self._leads: dict[str, SalesforceLead] = {}
        self._opportunities: dict[str, SalesforceOpportunity] = {}

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> bool:
        """
        Connect to Salesforce via OAuth2.
        Uses JWT Bearer flow for app-only access.
        """
        self.health.status = AdapterStatus.CONNECTING

        try:
            # Get consumer secret from GCP Secret Manager
            consumer_secret = await self._get_secret(self.sf_config.credentials_vault_key)

            # Request access token
            token_response = await self._request_token(consumer_secret)

            if token_response and "access_token" in token_response:
                self._access_token = token_response["access_token"]
                self._instance_url = token_response.get("instance_url", self.sf_config.instance_url)
                self.health.status = AdapterStatus.CONNECTED
                logger.info(f"Salesforce adapter connected to {self._instance_url}")
                return True
            else:
                self.health.status = AdapterStatus.ERROR
                self.health.last_error = "Failed to obtain access token"
                return False

        except Exception as e:
            self.health.status = AdapterStatus.ERROR
            self.health.last_error = str(e)
            logger.error(f"Salesforce connection failed: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from Salesforce"""
        self._access_token = None
        self._instance_url = None
        self.health.status = AdapterStatus.DISCONNECTED
        logger.info("Salesforce adapter disconnected")
        return True

    async def test_connection(self) -> ConnectionHealth:
        """Test Salesforce connection"""
        try:
            # Query limits to test connection
            response = await self._sf_request("GET", "/services/data")

            if response:
                self.health.status = AdapterStatus.CONNECTED
                self.health.last_error = None
            else:
                self.health.status = AdapterStatus.ERROR
                self.health.last_error = "Salesforce API test failed"

        except Exception as e:
            self.health.status = AdapterStatus.ERROR
            self.health.last_error = str(e)

        return self.health

    # =========================================================================
    # Data Operations
    # =========================================================================

    async def fetch_data(self, query: dict[str, Any]) -> list[SFRecord]:
        """
        Fetch data from Salesforce.
        Routes to appropriate object based on query.
        """
        object_type = query.get("type", "Account")
        batch_size = query.get("batch_size", self.config.batch_size)
        modified_since = query.get("modified_since")

        # Build SOQL query
        soql = self._build_soql_query(object_type, batch_size, modified_since)

        # Decide between REST and Bulk API
        if self.sf_config.use_bulk_api and batch_size > self.sf_config.bulk_threshold:
            return await self._bulk_query(soql)
        else:
            return await self._soql_query(soql)

    async def push_data(self, data: list[SFRecord]) -> SyncResult:
        """
        Push data back to Salesforce.
        Creates, updates, or upserts records.
        """
        result = SyncResult(
            success=True,
            adapter_id=self.config.adapter_id,
            operation="push",
        )

        # Group by object type for batch processing
        by_type: dict[str, list[SFRecord]] = {}
        for record in data:
            obj_type = record.get("_type", "Account")
            if obj_type not in by_type:
                by_type[obj_type] = []
            by_type[obj_type].append(record)

        # Process each object type
        for obj_type, records in by_type.items():
            if not self._can_write(obj_type):
                logger.warning(f"Write not enabled for {obj_type}")
                continue

            try:
                if len(records) > self.sf_config.bulk_threshold:
                    batch_result = await self._bulk_upsert(obj_type, records)
                else:
                    batch_result = await self._batch_update(obj_type, records)

                result.records_updated += batch_result.get("updated", 0)
                result.records_created += batch_result.get("created", 0)
                result.records_failed += batch_result.get("failed", 0)

            except Exception as e:
                result.errors.append(f"{obj_type}: {str(e)}")

        return result

    async def get_schema(self) -> dict[str, Any]:
        """Get Salesforce schema information"""
        # Describe global to get all objects
        response = await self._sf_request(
            "GET", f"/services/data/{self.sf_config.api_version}/sobjects"
        )

        objects = {}
        if response and "sobjects" in response:
            for obj in response["sobjects"]:
                objects[obj["name"]] = {
                    "label": obj.get("label"),
                    "queryable": obj.get("queryable", False),
                    "createable": obj.get("createable", False),
                    "updateable": obj.get("updateable", False),
                }

        return {
            "api_version": self.sf_config.api_version,
            "instance_url": self._instance_url,
            "objects": objects,
            "sync_enabled": {
                "Account": self.sf_config.sync_accounts,
                "Contact": self.sf_config.sync_contacts,
                "Lead": self.sf_config.sync_leads,
                "Opportunity": self.sf_config.sync_opportunities,
                "Case": self.sf_config.sync_cases,
            },
        }

    # =========================================================================
    # SOQL Query Builder
    # =========================================================================

    def _build_soql_query(self, object_type: str, limit: int, modified_since: str | None) -> str:
        """Build SOQL query for object type"""
        fields = self._get_object_fields(object_type)
        query = f"SELECT {', '.join(fields)} FROM {object_type}"

        if modified_since:
            query += f" WHERE LastModifiedDate > {modified_since}"

        query += f" ORDER BY LastModifiedDate DESC LIMIT {limit}"

        return query

    def _get_object_fields(self, object_type: str) -> list[str]:
        """Get fields to query for an object type"""
        field_map = {
            "Account": [
                "Id",
                "Name",
                "Type",
                "Industry",
                "AnnualRevenue",
                "NumberOfEmployees",
                "BillingCity",
                "BillingCountry",
                "OwnerId",
                "CreatedDate",
                "LastModifiedDate",
            ],
            "Contact": [
                "Id",
                "FirstName",
                "LastName",
                "Email",
                "Phone",
                "Title",
                "AccountId",
                "Department",
                "MailingCity",
                "OwnerId",
                "CreatedDate",
                "LastModifiedDate",
            ],
            "Lead": [
                "Id",
                "FirstName",
                "LastName",
                "Company",
                "Email",
                "Phone",
                "Status",
                "LeadSource",
                "Rating",
                "Industry",
                "OwnerId",
                "CreatedDate",
                "LastModifiedDate",
            ],
            "Opportunity": [
                "Id",
                "Name",
                "AccountId",
                "Amount",
                "StageName",
                "Probability",
                "CloseDate",
                "Type",
                "LeadSource",
                "OwnerId",
                "IsClosed",
                "IsWon",
                "CreatedDate",
                "LastModifiedDate",
            ],
            "Case": [
                "Id",
                "CaseNumber",
                "Subject",
                "Status",
                "Priority",
                "Origin",
                "AccountId",
                "ContactId",
                "OwnerId",
                "CreatedDate",
                "LastModifiedDate",
            ],
        }
        return field_map.get(object_type, ["Id", "Name", "LastModifiedDate"])

    # =========================================================================
    # Query Execution
    # =========================================================================

    async def _soql_query(self, query: str) -> list[dict[str, Any]]:
        """Execute SOQL query via REST API"""
        import urllib.parse

        encoded_query = urllib.parse.quote(query)
        endpoint = f"/services/data/{self.sf_config.api_version}/query?q={encoded_query}"

        response = await self._sf_request("GET", endpoint)

        records = []
        if response and "records" in response:
            for record in response["records"]:
                # Clean up Salesforce metadata
                clean_record = {k: v for k, v in record.items() if not k.startswith("attributes")}
                clean_record["_type"] = record.get("attributes", {}).get("type", "Unknown")
                records.append(clean_record)

            # Handle pagination
            while response.get("nextRecordsUrl"):
                response = await self._sf_request("GET", response["nextRecordsUrl"])
                if response and "records" in response:
                    for record in response["records"]:
                        clean_record = {
                            k: v for k, v in record.items() if not k.startswith("attributes")
                        }
                        clean_record["_type"] = record.get("attributes", {}).get("type", "Unknown")
                        records.append(clean_record)

        return records

    async def _bulk_query(self, query: str) -> list[dict[str, Any]]:
        """Execute query via Bulk API 2.0"""
        # Create bulk query job
        job_response = await self._sf_request(
            "POST",
            f"/services/data/{self.sf_config.api_version}/jobs/query",
            json={
                "operation": "query",
                "query": query,
            },
        )

        if not job_response or "id" not in job_response:
            return []

        job_id = job_response["id"]

        # Poll for completion
        while True:
            status = await self._sf_request(
                "GET", f"/services/data/{self.sf_config.api_version}/jobs/query/{job_id}"
            )

            if status and status.get("state") in ["JobComplete", "Failed", "Aborted"]:
                break

            await asyncio.sleep(2)  # Poll every 2 seconds

        # Get results
        if status.get("state") == "JobComplete":
            results = await self._sf_request(
                "GET", f"/services/data/{self.sf_config.api_version}/jobs/query/{job_id}/results"
            )
            return results if isinstance(results, list) else []

        return []

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def _batch_update(
        self, object_type: str, records: list[dict[str, Any]]
    ) -> dict[str, int]:
        """Batch update records via composite API"""
        result = {"created": 0, "updated": 0, "failed": 0}

        # Build composite request
        composite_request = {"allOrNone": False, "compositeRequest": []}

        for i, record in enumerate(records):
            record_id = record.get("Id")
            clean_record = {k: v for k, v in record.items() if not k.startswith("_") and k != "Id"}

            if record_id:
                # Update existing
                composite_request["compositeRequest"].append(
                    {
                        "method": "PATCH",
                        "url": f"/services/data/{self.sf_config.api_version}/sobjects/{object_type}/{record_id}",
                        "referenceId": f"update_{i}",
                        "body": clean_record,
                    }
                )
            else:
                # Create new
                composite_request["compositeRequest"].append(
                    {
                        "method": "POST",
                        "url": f"/services/data/{self.sf_config.api_version}/sobjects/{object_type}",
                        "referenceId": f"create_{i}",
                        "body": clean_record,
                    }
                )

        response = await self._sf_request(
            "POST", f"/services/data/{self.sf_config.api_version}/composite", json=composite_request
        )

        if response and "compositeResponse" in response:
            for resp in response["compositeResponse"]:
                if resp.get("httpStatusCode") in [200, 201, 204]:
                    if resp["referenceId"].startswith("create_"):
                        result["created"] += 1
                    else:
                        result["updated"] += 1
                else:
                    result["failed"] += 1

        return result

    async def _bulk_upsert(self, object_type: str, records: list[dict[str, Any]]) -> dict[str, int]:
        """Bulk upsert via Bulk API 2.0"""
        # Create bulk job
        job_response = await self._sf_request(
            "POST",
            f"/services/data/{self.sf_config.api_version}/jobs/ingest",
            json={
                "object": object_type,
                "operation": "upsert",
                "externalIdFieldName": "Id",
            },
        )

        if not job_response or "id" not in job_response:
            return {"created": 0, "updated": 0, "failed": len(records)}

        job_id = job_response["id"]

        # Upload data
        csv_data = self._records_to_csv(records)
        await self._sf_request(
            "PUT",
            f"/services/data/{self.sf_config.api_version}/jobs/ingest/{job_id}/batches",
            data=csv_data,
            content_type="text/csv",
        )

        # Close job
        await self._sf_request(
            "PATCH",
            f"/services/data/{self.sf_config.api_version}/jobs/ingest/{job_id}",
            json={"state": "UploadComplete"},
        )

        # Poll for completion and get results
        # In production, implement proper polling
        return {"created": 0, "updated": len(records), "failed": 0}

    def _records_to_csv(self, records: list[dict[str, Any]]) -> str:
        """Convert records to CSV for Bulk API"""
        if not records:
            return ""

        # Get headers from first record
        headers = [k for k in records[0] if not k.startswith("_")]

        lines = [",".join(headers)]
        for record in records:
            values = [str(record.get(h, "")) for h in headers]
            lines.append(",".join(values))

        return "\n".join(lines)

    def _can_write(self, object_type: str) -> bool:
        """Check if write is enabled for object type"""
        return {
            "Account": self.sf_config.write_accounts,
            "Contact": self.sf_config.write_contacts,
            "Lead": self.sf_config.write_leads,
            "Opportunity": self.sf_config.write_opportunities,
        }.get(object_type, False)

    # =========================================================================
    # API Helpers
    # =========================================================================

    async def _sf_request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        data: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any] | None:
        """Make a request to Salesforce API"""
        if not self._access_token:
            await self.connect()

        url = f"{self._instance_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": content_type,
        }

        # Placeholder - actual HTTP call would go here
        logger.debug(f"Salesforce API: {method} {url}")

        return {"records": [], "totalSize": 0}

    async def _request_token(self, consumer_secret: str) -> dict[str, Any] | None:
        """Request OAuth2 access token"""
        token_url = f"{self.sf_config.instance_url}/services/oauth2/token"

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.sf_config.consumer_key,
            "client_secret": consumer_secret,
        }

        # Placeholder - actual HTTP call would go here
        logger.debug(f"Requesting token from {token_url}")

        return {
            "access_token": "placeholder_token",
            "instance_url": self.sf_config.instance_url,
            "token_type": "Bearer",
        }

    async def _get_secret(self, secret_name: str) -> str:
        """Get secret from GCP Secret Manager"""
        # In production, use google-cloud-secret-manager
        return "placeholder_secret"

    # =========================================================================
    # Value Calculation - Economic Juggernaut Integration
    # =========================================================================

    async def _process_data(self, data: list[SFRecord]) -> list[SFRecord]:
        """
        Process Salesforce data through our AI pipeline.
        This is where the Economic Juggernaut adds massive value.
        """
        processed = []

        for record in data:
            record_type = record.get("_type", "Unknown")

            # Add AI-enhanced insights based on record type
            record["_ai_insights"] = {
                "processed_at": datetime.utcnow().isoformat(),
                "processor": "economic_juggernaut",
            }

            if record_type == "Lead":
                # Lead scoring
                record["_ai_insights"]["lead_score"] = self._calculate_lead_score(record)
                record["_ai_insights"]["conversion_probability"] = 0.35  # Placeholder
                record["_ai_insights"]["recommended_actions"] = [
                    "Follow up call",
                    "Send case study",
                ]

            elif record_type == "Opportunity":
                # Deal insights
                record["_ai_insights"]["win_probability"] = self._calculate_win_probability(record)
                record["_ai_insights"]["risk_factors"] = self._identify_risk_factors(record)
                record["_ai_insights"]["recommended_next_steps"] = [
                    "Schedule demo",
                    "Involve executive sponsor",
                ]

            elif record_type == "Account":
                # Account health
                record["_ai_insights"]["health_score"] = 0.82  # Placeholder
                record["_ai_insights"]["expansion_potential"] = "high"
                record["_ai_insights"]["churn_risk"] = "low"

            elif record_type == "Contact":
                # Contact engagement
                record["_ai_insights"]["engagement_score"] = 0.65  # Placeholder
                record["_ai_insights"]["influence_level"] = "decision_maker"

            processed.append(record)

        return processed

    def _calculate_lead_score(self, lead: dict[str, Any]) -> float:
        """Calculate AI-powered lead score"""
        score = 50.0  # Base score

        # Industry scoring
        high_value_industries = ["Technology", "Financial Services", "Healthcare"]
        if lead.get("Industry") in high_value_industries:
            score += 15

        # Rating scoring
        rating_scores = {"Hot": 25, "Warm": 15, "Cold": 0}
        score += rating_scores.get(lead.get("Rating", ""), 5)

        # Source scoring
        good_sources = ["Web", "Partner Referral", "Customer Event"]
        if lead.get("LeadSource") in good_sources:
            score += 10

        return min(score, 100.0)

    def _calculate_win_probability(self, opp: dict[str, Any]) -> float:
        """Calculate AI-powered win probability"""
        base_prob = opp.get("Probability", 50) / 100

        # Adjust based on stage
        stage_adjustments = {
            "Prospecting": -0.1,
            "Qualification": -0.05,
            "Needs Analysis": 0,
            "Proposal": 0.05,
            "Negotiation": 0.1,
        }
        adjustment = stage_adjustments.get(opp.get("StageName", ""), 0)

        return min(max(base_prob + adjustment, 0), 1.0)

    def _identify_risk_factors(self, opp: dict[str, Any]) -> list[str]:
        """Identify risk factors for opportunity"""
        risks = []

        # Check close date
        close_date = opp.get("CloseDate")
        if close_date:
            # Would check if close date is in past or very soon
            pass

        # Check amount vs stage
        amount = opp.get("Amount", 0)
        if amount > 100000 and opp.get("StageName") == "Prospecting":
            risks.append("Large deal still in early stage")

        # Check probability
        if opp.get("Probability", 100) < 30:
            risks.append("Low win probability")

        return risks

    async def _calculate_value_added(self, original: list[Any], processed: list[Any]) -> float:
        """
        Calculate value added by Salesforce integration.

        Value sources:
        - Lead scoring saves sales rep time
        - Win probability improves forecast accuracy
        - Risk identification prevents deal slippage
        - Account health predicts retention
        """
        value = 0.0

        for record in processed:
            record_type = record.get("_type", "Unknown")

            if record_type == "Lead":
                # Each scored lead saves ~15 min of sales time
                # At $50/hr, that's ~$12.50 per lead
                value += 12.50

            elif record_type == "Opportunity":
                # Better win probability improves resource allocation
                # Estimated value: 2% of deal amount
                amount = record.get("Amount", 0)
                value += amount * 0.02

            elif record_type == "Account":
                # Account health prevents churn
                # Estimated value: $100 per account analyzed
                value += 100.0

            elif record_type == "Contact":
                # Contact insights improve targeting
                value += 5.0

        return value
