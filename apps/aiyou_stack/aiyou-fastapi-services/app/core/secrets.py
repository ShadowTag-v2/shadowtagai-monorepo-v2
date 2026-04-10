"""
Google Secret Manager Integration
Production-ready secrets management with automatic environment variable fallback
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Try to import Google Secret Manager (optional dependency)
try:
    from google.cloud import secretmanager

    GOOGLE_SECRET_MANAGER_AVAILABLE = True
except ImportError:
    GOOGLE_SECRET_MANAGER_AVAILABLE = False
    logger.warning("⚠️ google-cloud-secret-manager not installed, using environment variables only")


class SecretManager:
    """
    Google Secret Manager client with automatic fallback to environment variables

    Features:
    - Retrieves secrets from Google Secret Manager in production
    - Automatic fallback to environment variables in development
    - Secret caching to reduce API calls
    - JSON parsing for structured secrets
    - Bulk secret retrieval
    """

    def __init__(self, project_id: str | None = None):
        """
        Initialize Secret Manager client

        Args:
            project_id: GCP project ID (if None, uses environment variables only)
        """
        self.project_id = project_id
        self.client = None
        self.cache: dict[str, str] = {}

        if project_id and GOOGLE_SECRET_MANAGER_AVAILABLE:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
                logger.info(f"✅ Google Secret Manager initialized for project: {project_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Secret Manager, using env vars: {e}")
        else:
            logger.info("ℹ️ Using environment variables for secrets (no GCP project configured)")

    def get_secret(self, secret_id: str, version: str = "latest") -> str | None:
        """
        Retrieve secret from Secret Manager with fallback to environment variables

        Args:
            secret_id: Secret name in Secret Manager (e.g., "youtube-api-key")
            version: Secret version (default: "latest")

        Returns:
            Secret value as string, or None if not found
        """
        # Check cache first
        cache_key = f"{secret_id}:{version}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Try Secret Manager
        if self.client and self.project_id:
            try:
                name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
                response = self.client.access_secret_version(request={"name": name})
                secret_value = response.payload.data.decode("UTF-8")

                # Cache the result
                self.cache[cache_key] = secret_value
                logger.debug(f"✅ Retrieved secret '{secret_id}' from Secret Manager")
                return secret_value

            except Exception as e:
                logger.warning(f"⚠️ Failed to get secret '{secret_id}' from Secret Manager: {e}")

        # Fallback to environment variable
        # Convert secret_id to standard env var format: youtube-api-key → YOUTUBE_API_KEY
        env_var_name = secret_id.upper().replace("-", "_")
        env_value = os.getenv(env_var_name)

        if env_value:
            logger.debug(
                f"✅ Retrieved secret '{secret_id}' from environment variable {env_var_name}"
            )
            self.cache[cache_key] = env_value
            return env_value

        logger.error(f"❌ Secret '{secret_id}' not found in Secret Manager or environment")
        return None

    def get_secret_json(self, secret_id: str, version: str = "latest") -> dict[str, Any] | None:
        """
        Retrieve JSON secret and parse it

        Args:
            secret_id: Secret name in Secret Manager
            version: Secret version (default: "latest")

        Returns:
            Parsed JSON as dict, or None if not found or invalid JSON
        """
        secret_value = self.get_secret(secret_id, version)
        if not secret_value:
            return None

        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse secret '{secret_id}' as JSON: {e}")
            return None

    def get_api_keys(self) -> dict[str, str]:
        """
        Retrieve all API keys for external services

        Returns:
            Dict mapping service name to API key
        """
        api_keys = {}

        # YouTube Data API
        youtube_key = self.get_secret("youtube-api-key")
        if youtube_key:
            api_keys["youtube"] = youtube_key

        # Twitter API
        twitter_bearer = self.get_secret("twitter-bearer-token")
        if twitter_bearer:
            api_keys["twitter"] = twitter_bearer

        # NewsAPI
        news_key = self.get_secret("newsapi-key")
        if news_key:
            api_keys["news"] = news_key

        # Reddit API (JSON with client_id and client_secret)
        reddit_creds = self.get_secret_json("reddit-api-credentials")
        if reddit_creds:
            api_keys["reddit"] = reddit_creds

        logger.info(f"✅ Loaded {len(api_keys)} API keys")
        return api_keys

    def get_auth_keys(self) -> dict[str, str]:
        """
        Retrieve authentication keys for FastAPI middleware

        Returns:
            Dict mapping plain API keys to tier names
        """
        # Retrieve API keys configuration (JSON format)
        # Example JSON: {"key123": "tier_1", "key456": "enterprise"}
        auth_keys_json = self.get_secret_json("fastapi-auth-keys")

        if auth_keys_json:
            logger.info(f"✅ Loaded {len(auth_keys_json)} authentication keys from Secret Manager")
            return auth_keys_json

        # Fallback: try environment variable
        auth_keys_env = os.getenv("FASTAPI_AUTH_KEYS")
        if auth_keys_env:
            try:
                auth_keys = json.loads(auth_keys_env)
                logger.info(f"✅ Loaded {len(auth_keys)} authentication keys from environment")
                return auth_keys
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse FASTAPI_AUTH_KEYS as JSON")

        # Default: development key (INSECURE, only for local testing)
        logger.warning("⚠️ Using default development auth key (INSECURE)")
        return {"dev-key-12345": "tier_1"}

    def get_database_url(self) -> str:
        """
        Retrieve database connection URL

        Returns:
            Database URL string
        """
        db_url = self.get_secret("database-url")
        if db_url:
            return db_url

        # Fallback to default SQLite
        default_url = "sqlite+aiosqlite:///./ShadowTag_governance.db"
        logger.warning(f"⚠️ Using default database URL: {default_url}")
        return default_url

    def get_redis_url(self) -> str:
        """
        Retrieve Redis connection URL

        Returns:
            Redis URL string
        """
        redis_url = self.get_secret("redis-url")
        if redis_url:
            return redis_url

        # Fallback to default local Redis
        default_url = "redis://localhost:6379/0"
        logger.warning(f"⚠️ Using default Redis URL: {default_url}")
        return default_url

    def clear_cache(self):
        """
        Clear the secret cache (useful for testing or forcing refresh)
        """
        self.cache.clear()
        logger.info("🔄 Secret cache cleared")


# Singleton instance
_secret_manager_instance: SecretManager | None = None


def get_secret_manager(project_id: str | None = None) -> SecretManager:
    """
    Get or create singleton Secret Manager instance

    Args:
        project_id: GCP project ID (optional)

    Returns:
        SecretManager instance
    """
    global _secret_manager_instance

    if _secret_manager_instance is None:
        _secret_manager_instance = SecretManager(project_id=project_id)

    return _secret_manager_instance
