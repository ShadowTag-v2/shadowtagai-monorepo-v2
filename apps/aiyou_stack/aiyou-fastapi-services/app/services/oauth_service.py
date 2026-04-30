"""OAuth service for handling OAuth flows"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.integration import (
    Integration,
    IntegrationCredential,
    IntegrationStatus,
)

logger = logging.getLogger(__name__)


class OAuthService:
    """Service for OAuth authentication flows"""

    # OAuth provider configurations
    PROVIDERS = {
        "google": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "access_token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
            "scope": "openid email profile",
        },
        "github": {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "authorize_url": "https://github.com/login/oauth/authorize",
            "access_token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
            "scope": "user repo",
        },
    }

    def __init__(self, db: Session):
        self.db = db
        self._states: dict[str, dict[str, Any]] = {}  # In production, use Redis

    def get_provider_config(self, provider: str) -> dict[str, str] | None:
        """Get OAuth provider configuration"""
        return self.PROVIDERS.get(provider.lower())

    def initiate_oauth_flow(
        self,
        provider: str,
        integration_id: int,
        redirect_uri: str,
        scope: str | None = None,
    ) -> dict[str, str]:
        """Initiate OAuth authorization flow"""
        config = self.get_provider_config(provider)
        if not config:
            raise ValueError(f"Unsupported OAuth provider: {provider}")

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state with integration info (use Redis in production)
        self._states[state] = {
            "integration_id": integration_id,
            "provider": provider,
            "redirect_uri": redirect_uri,
            "created_at": datetime.utcnow(),
        }

        # Build authorization URL
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": scope or config["scope"],
        }

        auth_url = config["authorize_url"] + "?" + "&".join(f"{k}={v}" for k, v in params.items())

        logger.info(f"Initiated OAuth flow for {provider} with state {state}")

        return {"authorization_url": auth_url, "state": state}

    async def handle_oauth_callback(
        self,
        code: str,
        state: str,
        user_id: int,
    ) -> Integration | None:
        """Handle OAuth callback and exchange code for tokens"""
        # Verify state
        state_data = self._states.pop(state, None)
        if not state_data:
            logger.error(f"Invalid OAuth state: {state}")
            return None

        integration_id = state_data["integration_id"]
        provider = state_data["provider"]
        redirect_uri = state_data["redirect_uri"]

        # Get integration
        integration = (
            self.db.query(Integration)
            .filter(Integration.id == integration_id, Integration.user_id == user_id)
            .first()
        )

        if not integration:
            logger.error(f"Integration {integration_id} not found")
            return None

        # Get provider config
        config = self.get_provider_config(provider)
        if not config:
            logger.error(f"Provider config not found for {provider}")
            return None

        # Exchange code for tokens
        try:
            import httpx

            token_params = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["access_token_url"],
                    data=token_params,
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                token_data = response.json()

            # Extract tokens
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            token_type = token_data.get("token_type", "Bearer")
            expires_in = token_data.get("expires_in")
            scope = token_data.get("scope")

            if not access_token:
                logger.error("No access token in OAuth response")
                return None

            # Calculate expiration
            expires_at = None
            if expires_in:
                expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            # Delete existing credentials
            self.db.query(IntegrationCredential).filter(
                IntegrationCredential.integration_id == integration_id,
            ).delete()

            # Store credentials
            credential = IntegrationCredential(
                integration_id=integration_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                scope=scope,
                expires_at=expires_at,
                extra_data=token_data,
            )

            self.db.add(credential)

            # Update integration status
            integration.status = IntegrationStatus.ACTIVE
            integration.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(integration)

            logger.info(f"Successfully completed OAuth flow for integration {integration_id}")

            return integration

        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            integration.status = IntegrationStatus.ERROR
            integration.last_error = str(e)
            self.db.commit()
            return None

    async def refresh_access_token(
        self,
        integration_id: int,
        user_id: int,
    ) -> IntegrationCredential | None:
        """Refresh OAuth access token"""
        integration = (
            self.db.query(Integration)
            .filter(Integration.id == integration_id, Integration.user_id == user_id)
            .first()
        )

        if not integration:
            return None

        credential = (
            self.db.query(IntegrationCredential)
            .filter(IntegrationCredential.integration_id == integration_id)
            .first()
        )

        if not credential or not credential.refresh_token:
            logger.error(f"No refresh token for integration {integration_id}")
            return None

        # Get provider config
        config = self.get_provider_config(integration.provider)
        if not config:
            return None

        try:
            import httpx

            token_params = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "refresh_token": credential.refresh_token,
                "grant_type": "refresh_token",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["access_token_url"],
                    data=token_params,
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                token_data = response.json()

            # Update credentials
            credential.access_token = token_data.get("access_token")
            if token_data.get("refresh_token"):
                credential.refresh_token = token_data.get("refresh_token")

            expires_in = token_data.get("expires_in")
            if expires_in:
                credential.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            credential.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(credential)

            logger.info(f"Refreshed access token for integration {integration_id}")

            return credential

        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None

    def cleanup_expired_states(self):
        """Clean up expired OAuth states (call periodically)"""
        cutoff = datetime.utcnow() - timedelta(minutes=10)
        expired = [state for state, data in self._states.items() if data["created_at"] < cutoff]

        for state in expired:
            del self._states[state]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired OAuth states")
