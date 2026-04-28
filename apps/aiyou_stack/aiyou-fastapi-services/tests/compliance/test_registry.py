# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for the Regulation Registry System"""

from app.compliance.modules.base import ComplianceModule
from app.compliance.registry import (
    auto_register_modules,
    get_registry,
)
from app.models.compliance import Jurisdiction, RegulationId


class TestRegulationRegistry:
    """Test cases for RegulationRegistry"""

    def test_registry_singleton(self):
        """Registry should be a singleton"""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2

    def test_auto_register_modules(self):
        """Auto registration should register all built-in modules"""
        registry = get_registry()
        registry.clear()  # Start fresh

        auto_register_modules()

        # Check that modules are registered
        assert registry.is_registered(RegulationId.EU_AI_ACT)
        assert registry.is_registered(RegulationId.GDPR)
        assert registry.is_registered(RegulationId.DSA)
        assert registry.is_registered(RegulationId.CA_SB_243)
        assert registry.is_registered(RegulationId.HIPAA)

    def test_get_module(self):
        """Should retrieve registered modules"""
        auto_register_modules()
        registry = get_registry()

        module = registry.get_module(RegulationId.EU_AI_ACT)
        assert module is not None
        assert module.module_id == RegulationId.EU_AI_ACT

    def test_get_module_not_found(self):
        """Should return None for unregistered modules"""
        registry = get_registry()
        registry.clear()

        module = registry.get_module(RegulationId.EU_AI_ACT)
        assert module is None

    def test_list_registered(self):
        """Should list all registered regulation IDs"""
        auto_register_modules()
        registry = get_registry()

        registered = registry.list_registered()
        assert RegulationId.EU_AI_ACT in registered
        assert RegulationId.GDPR in registered

    def test_filter_by_jurisdiction(self):
        """Should filter modules by jurisdiction"""
        auto_register_modules()
        registry = get_registry()

        eu_modules = registry.filter_by_jurisdiction(Jurisdiction.EU)
        assert RegulationId.EU_AI_ACT in eu_modules
        assert RegulationId.GDPR in eu_modules
        assert RegulationId.DSA in eu_modules

        us_modules = registry.filter_by_jurisdiction(Jurisdiction.US)
        assert RegulationId.CA_SB_243 in us_modules
        assert RegulationId.HIPAA in us_modules

    def test_get_metadata(self):
        """Should retrieve module metadata"""
        auto_register_modules()
        registry = get_registry()

        metadata = registry.get_metadata(RegulationId.EU_AI_ACT)
        assert metadata is not None
        assert metadata.id == RegulationId.EU_AI_ACT
        assert metadata.jurisdiction == Jurisdiction.EU
        assert "AI Act" in metadata.name

    def test_health_check(self):
        """Health check should return status"""
        auto_register_modules()
        registry = get_registry()

        health = registry.health_check()
        assert health["status"] == "healthy"
        assert health["registered_modules"] > 0


class TestRegisterDecorator:
    """Test cases for the @register_module decorator"""

    def test_decorator_registers_module(self):
        """Decorator should register the module class"""
        auto_register_modules()
        registry = get_registry()

        # Modules registered via decorator should be accessible
        module = registry.get_module(RegulationId.EU_AI_ACT)
        assert module is not None
        assert isinstance(module, ComplianceModule)
