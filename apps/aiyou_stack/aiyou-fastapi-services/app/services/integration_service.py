"""Integration service with retry logic and error handling"""

import logging
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.models.integration import Integration, IntegrationCredential, IntegrationStatus
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationCredentialCreate,
    IntegrationTestRequest,
    IntegrationUpdate,
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """Service for managing integrations"""

    def __init__(self, db: Session):
        self.db = db

    def create_integration(self, user_id: int, data: IntegrationCreate) -> Integration:
        """Create a new integration"""
        integration = Integration(
            user_id=user_id,
            name=data.name,
            provider=data.provider,
            type=data.type,
            base_url=data.base_url,
            api_version=data.api_version,
            config=data.config,
            metadata=data.metadata,
            max_retries=data.max_retries,
            retry_backoff=data.retry_backoff,
            timeout=data.timeout,
            status=IntegrationStatus.PENDING,
        )

        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)

        logger.info(f"Created integration {integration.id} for user {user_id}")
        return integration

    def get_integration(self, integration_id: int, user_id: int) -> Integration | None:
        """Get integration by ID"""
        return (
            self.db.query(Integration)
            .filter(Integration.id == integration_id, Integration.user_id == user_id)
            .first()
        )

    def list_integrations(
        self,
        user_id: int,
        provider: str | None = None,
        status: IntegrationStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Integration]:
        """List user integrations"""
        query = self.db.query(Integration).filter(Integration.user_id == user_id)

        if provider:
            query = query.filter(Integration.provider == provider)
        if status:
            query = query.filter(Integration.status == status)

        return query.offset(skip).limit(limit).all()

    def update_integration(
        self,
        integration_id: int,
        user_id: int,
        data: IntegrationUpdate,
    ) -> Integration | None:
        """Update integration"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(integration, field, value)

        integration.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(integration)

        logger.info(f"Updated integration {integration_id}")
        return integration

    def delete_integration(self, integration_id: int, user_id: int) -> bool:
        """Delete integration"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return False

        self.db.delete(integration)
        self.db.commit()

        logger.info(f"Deleted integration {integration_id}")
        return True

    def add_credentials(
        self,
        integration_id: int,
        user_id: int,
        credentials: IntegrationCredentialCreate,
    ) -> IntegrationCredential | None:
        """Add or update integration credentials"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return None

        # Delete existing credentials
        self.db.query(IntegrationCredential).filter(
            IntegrationCredential.integration_id == integration_id,
        ).delete()

        # Create new credentials
        credential = IntegrationCredential(
            integration_id=integration_id,
            **credentials.model_dump(),
        )

        self.db.add(credential)

        # Update integration status
        integration.status = IntegrationStatus.ACTIVE
        integration.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(credential)

        logger.info(f"Added credentials for integration {integration_id}")
        return credential

    def get_credentials(self, integration_id: int, user_id: int) -> IntegrationCredential | None:
        """Get integration credentials"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return None

        return (
            self.db.query(IntegrationCredential)
            .filter(IntegrationCredential.integration_id == integration_id)
            .first()
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def make_request(
        self,
        integration: Integration,
        endpoint: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic"""
        # Get credentials
        credential = (
            self.db.query(IntegrationCredential)
            .filter(IntegrationCredential.integration_id == integration.id)
            .first()
        )

        # Build headers
        request_headers = headers or {}

        if credential:
            if credential.access_token:
                token_type = credential.token_type or "Bearer"
                request_headers["Authorization"] = f"{token_type} {credential.access_token}"
            elif credential.api_key:
                # Common API key header patterns
                request_headers["X-API-Key"] = credential.api_key

        # Build URL
        base_url = integration.base_url or ""
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(timeout=integration.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    json=json_data,
                    params=params,
                )
                response.raise_for_status()

                # Update integration status
                integration.last_sync_at = datetime.utcnow()
                integration.status = IntegrationStatus.ACTIVE
                integration.error_count = 0
                integration.last_error = None
                self.db.commit()

                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.text else None,
                    "headers": dict(response.headers),
                }

        except Exception as e:
            # Update error tracking
            integration.error_count += 1
            integration.last_error = str(e)
            integration.status = IntegrationStatus.ERROR
            self.db.commit()

            logger.error(f"Integration {integration.id} request failed: {e}")
            raise

    async def test_integration(
        self,
        integration_id: int,
        user_id: int,
        test_request: IntegrationTestRequest | None = None,
    ) -> dict[str, Any]:
        """Test integration connection"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return {"success": False, "error": "Integration not found"}

        start_time = datetime.utcnow()

        try:
            endpoint = test_request.endpoint if test_request else ""
            method = test_request.method if test_request else "GET"
            headers = test_request.headers if test_request else {}
            body = test_request.body if test_request else None

            result = await self.make_request(
                integration=integration,
                endpoint=endpoint,
                method=method,
                headers=headers,
                json_data=body,
            )

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "success": True,
                "status_code": result["status_code"],
                "response": result["data"],
                "duration_ms": int(duration),
            }

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {"success": False, "error": str(e), "duration_ms": int(duration)}
