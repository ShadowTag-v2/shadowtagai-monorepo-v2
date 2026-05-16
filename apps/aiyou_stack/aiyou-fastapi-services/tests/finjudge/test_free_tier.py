"""FinJudge Free Tier Tests
Test API key management, signup, and rate limiting
"""

import pytest

from src.finjudge.api.auth import APIKeyManager, TierLevel


class TestAPIKeyManager:
    """Test API key generation and validation"""

    def test_generate_free_tier_key(self):
        """Test generating a free tier API key"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        plaintext_key, api_key = manager.generate_key(
            email="redacted@shadowtag-v4.local",
            organization="Test Corp",
            tier=TierLevel.FREE,
        )

        assert plaintext_key.startswith("fj_")
        assert api_key.email == "redacted@shadowtag-v4.local"
        assert api_key.organization == "Test Corp"
        assert api_key.tier == TierLevel.FREE
        assert api_key.monthly_limit == 1000
        assert api_key.current_month_usage == 0
        assert api_key.is_active is True

    def test_validate_key_success(self):
        """Test successful API key validation"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        plaintext_key, api_key = manager.generate_key(
            email="redacted@shadowtag-v4.local",
            tier=TierLevel.FREE,
        )

        is_valid, validated_key, error = manager.validate_key(plaintext_key)

        assert is_valid is True
        assert validated_key is not None
        assert validated_key.email == "redacted@shadowtag-v4.local"
        assert error is None

    def test_validate_key_invalid_format(self):
        """Test validation with invalid key format"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        is_valid, api_key, error = manager.validate_key("invalid_key")

        assert is_valid is False
        assert api_key is None
        assert "Invalid key format" in error

    def test_validate_key_not_found(self):
        """Test validation with non-existent key"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        is_valid, api_key, error = manager.validate_key("fj_nonexistent_key_12345")

        assert is_valid is False
        assert api_key is None
        assert "not found" in error

    def test_rate_limit_enforcement(self):
        """Test rate limiting on free tier"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        plaintext_key, api_key = manager.generate_key(
            email="redacted@shadowtag-v4.local",
            tier=TierLevel.FREE,
        )

        # Record 1000 requests (at limit)
        for i in range(1000):
            manager.record_usage(
                api_key_id=api_key.id,
                endpoint="/v1/judge",
                decision_id=f"test_{i}",
            )

        # 1001st request should be rejected
        is_valid, validated_key, error = manager.validate_key(plaintext_key)

        assert is_valid is False
        assert "Monthly limit exceeded" in error

    def test_usage_stats(self):
        """Test usage statistics retrieval"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        plaintext_key, api_key = manager.generate_key(
            email="redacted@shadowtag-v4.local",
            tier=TierLevel.FREE,
        )

        # Record some usage
        for i in range(10):
            manager.record_usage(
                api_key_id=api_key.id,
                endpoint="/v1/judge",
                decision_id=f"test_{i}",
                risk_level="MODERATE",
                disposition="APPROVE",
            )

        stats = manager.get_usage_stats(api_key.id)

        assert stats["tier"] == "free"
        assert stats["current_month_usage"] == 10
        assert stats["monthly_limit"] == 1000
        assert stats["remaining"] == 990
        assert stats["total_usage"] == 10

    def test_upgrade_tier(self):
        """Test upgrading from free to pro tier"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        plaintext_key, api_key = manager.generate_key(
            email="redacted@shadowtag-v4.local",
            tier=TierLevel.FREE,
        )

        # Upgrade to Pro
        success = manager.upgrade_tier(
            api_key_id=api_key.id,
            new_tier=TierLevel.PRO,
            stripe_customer_id="cus_test123",
            stripe_subscription_id="sub_test123",
        )

        assert success is True

        # Validate upgraded key has new limits
        is_valid, upgraded_key, error = manager.validate_key(plaintext_key)

        assert is_valid is True
        assert upgraded_key.tier == TierLevel.PRO
        assert upgraded_key.monthly_limit == 10000
        assert upgraded_key.stripe_customer_id == "cus_test123"

    def test_multiple_keys_same_email(self):
        """Test generating multiple keys for same email"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")

        key1, api_key1 = manager.generate_key(email="redacted@shadowtag-v4.local")
        key2, api_key2 = manager.generate_key(email="redacted@shadowtag-v4.local")

        assert key1 != key2
        assert api_key1.id != api_key2.id

        # Both keys should be valid
        is_valid1, _, _ = manager.validate_key(key1)
        is_valid2, _, _ = manager.validate_key(key2)

        assert is_valid1 is True
        assert is_valid2 is True


class TestTierConfigurations:
    """Test tier pricing and limits"""

    def test_free_tier_config(self):
        """Test free tier configuration"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")
        config = manager.TIER_CONFIGS[TierLevel.FREE]

        assert config["monthly_limit"] == 1000
        assert config["price"] == 0
        assert "basic_judge" in config["features"]

    def test_pro_tier_config(self):
        """Test pro tier configuration"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")
        config = manager.TIER_CONFIGS[TierLevel.PRO]

        assert config["monthly_limit"] == 10000
        assert config["price"] == 99
        assert "analytics_dashboard" in config["features"]

    def test_enterprise_tier_unlimited(self):
        """Test enterprise tier has unlimited requests"""
        manager = APIKeyManager(db_url="sqlite:///:memory:")
        config = manager.TIER_CONFIGS[TierLevel.ENTERPRISE]

        assert config["monthly_limit"] is None  # Unlimited
        assert config["price"] == 2499


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
