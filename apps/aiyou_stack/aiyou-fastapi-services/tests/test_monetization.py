# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import pytest

from src.config.pricing import PricingTier
from src.pnkln.api.monetization import MonetizationEngine
from src.pnkln.registry.unified import UnifiedRegistry, registry


def test_monetization_engine():
    engine = MonetizationEngine()

    # 1. Create Key
    key = engine.create_api_key(user_id="user_123", tier=PricingTier.ENTERPRISE)
    assert key.startswith("ay_enterprise_")

    # 2. Validate Key
    key_obj = engine.validate_key(key)
    assert key_obj is not None
    assert key_obj.user_id == "user_123"

    # 3. Track Usage & Cost
    # Assuming 'decision_simple' is in API_COSTS from pricing.py, typically $0.0003
    try:
        usage = engine.track_request(key, "decision_simple")
        assert usage["cost"] > 0
        assert engine.calculate_total_revenue() > 0
    except ValueError as e:
        pytest.fail(f"Tracking failed: {e}")


def test_registry_registration():
    local_registry = UnifiedRegistry()

    @local_registry.register(name="test_tool", description="A test tool")
    def test_func(x):
        return x * 2

    tool = local_registry.get_tool("test_tool")
    assert tool is not None
    assert tool.description == "A test tool"

    result = local_registry.execute("test_tool", x=21)
    assert result == 42


def test_gemini_schema_gen():
    schemas = registry.generate_gemini_schema()
    assert isinstance(schemas, list)
    # Check for the default 'get_current_price' tool we added in the file
    valid_names = [s["name"] for s in schemas]
    assert "get_current_price" in valid_names
