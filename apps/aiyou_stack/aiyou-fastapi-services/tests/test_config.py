"""Configuration Tests

Tests for application configuration and settings
"""

import pytest
from src.shadowtag_v4.config import Settings, get_settings


class TestSettings:
    """Test Settings model"""

    def test_default_settings(self):
        """Test default settings values"""
        settings = Settings(
            _env_file=None,
            secret_key="test-key-32-bytes-long-required",
            database_url="sqlite:///test.db",
        )

        assert settings.app_name == "ShadowTag-v4 Platform"
        assert settings.app_version == "0.1.0"
        assert settings.debug is False
        assert settings.environment == "development"

    def test_required_secret_key(self, monkeypatch):
        """Test SECRET_KEY is required"""
        monkeypatch.delenv("SECRET_KEY", raising=False)
        with pytest.raises(Exception):  # noqa: B017
            # Should fail without secret_key
            Settings(_env_file=None, database_url="sqlite:///test.db")

    def test_rate_limiting_defaults(self):
        """Test rate limiting default configuration"""
        settings = Settings(secret_key="test-key", database_url="sqlite:///test.db")

        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_requests_per_minute == 60
        assert settings.rate_limit_burst == 10
        assert settings.rate_limit_upload_per_hour == 20

    def test_cors_defaults_strict(self):
        """Test CORS defaults to strict (empty list)"""
        settings = Settings(_env_file=None, secret_key="test-key", database_url="sqlite:///test.db")

        # Should be empty by default (strict)
        assert settings.cors_origins == []

    def test_jwt_configuration(self):
        """Test JWT configuration"""
        settings = Settings(secret_key="test-key", database_url="sqlite:///test.db")

        assert settings.access_token_expire_minutes == 30
        assert settings.refresh_token_expire_days == 7
        assert settings.algorithm == "HS256"

    def test_database_configuration(self):
        """Test database configuration"""
        settings = Settings(
            secret_key="test-key",
            database_url="postgresql://REDACTED_USER:REDACTED_PASS@localhost/db",
        )

        assert settings.database_url == "postgresql://REDACTED_USER:REDACTED_PASS@localhost/db"
        assert settings.database_pool_size == 5
        assert settings.database_max_overflow == 10

    def test_environment_override(self, monkeypatch):
        """Test environment variables override defaults"""
        monkeypatch.setenv("SECRET_KEY", "env-secret-key")
        monkeypatch.setenv("DATABASE_URL", "postgresql://env/db")
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("DEBUG", "false")

        settings = Settings()

        assert settings.secret_key == "env-secret-key"
        assert settings.database_url == "postgresql://env/db"
        assert settings.environment == "production"
        assert settings.debug is False


class TestGetSettings:
    """Test get_settings function"""

    def test_get_settings_cached(self):
        """Test settings are cached (singleton pattern)"""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be same instance (cached)
        assert settings1 is settings2

    def test_get_settings_returns_settings(self):
        """Test get_settings returns Settings instance"""
        settings = get_settings()

        assert isinstance(settings, Settings)


class TestSecuritySettings:
    """Test security-related settings"""

    def test_production_security(self):
        """Test security settings for production"""
        settings = Settings(
            secret_key="production-secret-key-very-long",
            database_url="postgresql://prod/db",
            environment="production",
            debug=False,
            cors_origins=["https://shadowtag_v4.ai"],
        )

        assert settings.environment == "production"
        assert settings.debug is False
        assert len(settings.cors_origins) > 0
        assert all(origin.startswith("https://") for origin in settings.cors_origins)

    def test_development_security(self):
        """Test security settings for development"""
        settings = Settings(
            secret_key="dev-secret-key",
            database_url="sqlite:///dev.db",
            environment="development",
            debug=True,
            cors_origins=["http://localhost:3000"],
        )

        assert settings.environment == "development"
        assert settings.debug is True


class TestServiceConfiguration:
    """Test service-specific configuration"""

    def test_gemini_configuration(self):
        """Test Gemini AI configuration"""
        settings = Settings(
            secret_key="test-key",
            database_url="sqlite:///test.db",
            gemini_api_key="test-gemini-key",
            gemini_project_id="test-project",
            gemini_location="us-central1",
        )

        assert settings.gemini_api_key == "test-gemini-key"
        assert settings.gemini_project_id == "test-project"
        assert settings.gemini_location == "us-central1"

    def test_shadowtag_configuration(self):
        """Test ShadowTag configuration"""
        settings = Settings(
            secret_key="test-key",
            database_url="sqlite:///test.db",
            shadowtag_enabled=True,
            shadowtag_private_key="test-private-key",
            shadowtag_chain_id="test-chain",
        )

        assert settings.shadowtag_enabled is True
        assert settings.shadowtag_private_key == "test-private-key"
        assert settings.shadowtag_chain_id == "test-chain"

    def test_redis_configuration(self):
        """Test Redis configuration"""
        settings = Settings(
            secret_key="test-key",
            database_url="sqlite:///test.db",
            redis_url="redis://localhost:6379/1",
            redis_max_connections=20,
        )

        assert settings.redis_url == "redis://localhost:6379/1"
        assert settings.redis_max_connections == 20
        assert settings.redis_url == "redis://localhost:6379/1"
        assert settings.redis_max_connections == 20
