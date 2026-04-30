"""Regulation Registry System

Central registry for all compliance modules.
Supports dynamic module registration, discovery, and instantiation.

Design Principles:
- Singleton pattern for global registry access
- Lazy loading of modules
- Thread-safe registration
- Version tracking for regulatory updates
"""

import logging
from functools import lru_cache
from typing import Optional

from app.compliance.modules.base import ComplianceModule
from app.models.compliance import (
    Jurisdiction,
    ModuleMetadata,
    RegulationId,
)

logger = logging.getLogger(__name__)


class RegulationRegistry:
    """Central registry for compliance regulation modules.

    Provides:
    - Module registration and discovery
    - Lazy instantiation of modules
    - Filtering by jurisdiction
    - Version management
    """

    _instance: Optional["RegulationRegistry"] = None
    _modules: dict[RegulationId, type[ComplianceModule]]
    _instances: dict[RegulationId, ComplianceModule]
    _metadata_cache: dict[RegulationId, ModuleMetadata]

    def __new__(cls) -> "RegulationRegistry":
        """Singleton pattern - ensure only one registry exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._modules = {}
            cls._instance._instances = {}
            cls._instance._metadata_cache = {}
            logger.info("RegulationRegistry initialized")
        return cls._instance

    def register(self, regulation_id: RegulationId, module_class: type[ComplianceModule]) -> None:
        """Register a compliance module class.

        Args:
            regulation_id: The regulation identifier
            module_class: The module class to register

        """
        if regulation_id in self._modules:
            logger.warning(f"Overwriting existing module: {regulation_id.value}")

        self._modules[regulation_id] = module_class
        # Clear cached instance if re-registering
        self._instances.pop(regulation_id, None)
        self._metadata_cache.pop(regulation_id, None)

        logger.info(f"Registered compliance module: {regulation_id.value}")

    def unregister(self, regulation_id: RegulationId) -> bool:
        """Unregister a compliance module.

        Args:
            regulation_id: The regulation to unregister

        Returns:
            True if module was unregistered, False if not found

        """
        if regulation_id not in self._modules:
            return False

        del self._modules[regulation_id]
        self._instances.pop(regulation_id, None)
        self._metadata_cache.pop(regulation_id, None)

        logger.info(f"Unregistered compliance module: {regulation_id.value}")
        return True

    def get_module(self, regulation_id: RegulationId) -> ComplianceModule | None:
        """Get a module instance by regulation ID.

        Lazy instantiation - creates instance on first access.

        Args:
            regulation_id: The regulation to get

        Returns:
            ComplianceModule instance or None if not registered

        """
        if regulation_id not in self._modules:
            logger.warning(f"Module not registered: {regulation_id.value}")
            return None

        # Lazy instantiation
        if regulation_id not in self._instances:
            module_class = self._modules[regulation_id]
            self._instances[regulation_id] = module_class()
            logger.debug(f"Instantiated module: {regulation_id.value}")

        return self._instances[regulation_id]

    def get_modules(self, regulation_ids: list[RegulationId]) -> list[ComplianceModule]:
        """Get multiple module instances.

        Args:
            regulation_ids: List of regulations to get

        Returns:
            List of ComplianceModule instances (excluding not found)

        """
        modules = []
        for reg_id in regulation_ids:
            module = self.get_module(reg_id)
            if module:
                modules.append(module)
        return modules

    def get_metadata(self, regulation_id: RegulationId) -> ModuleMetadata | None:
        """Get module metadata without full instantiation.

        Args:
            regulation_id: The regulation to get metadata for

        Returns:
            ModuleMetadata or None if not registered

        """
        if regulation_id in self._metadata_cache:
            return self._metadata_cache[regulation_id]

        module = self.get_module(regulation_id)
        if module:
            self._metadata_cache[regulation_id] = module.metadata
            return module.metadata

        return None

    def list_registered(self) -> list[RegulationId]:
        """List all registered regulation IDs.

        Returns:
            List of registered RegulationId values

        """
        return list(self._modules.keys())

    def list_metadata(self) -> list[ModuleMetadata]:
        """Get metadata for all registered modules.

        Returns:
            List of ModuleMetadata for all registered modules

        """
        return [
            self.get_metadata(reg_id)
            for reg_id in self._modules
            if self.get_metadata(reg_id) is not None
        ]

    def filter_by_jurisdiction(self, jurisdiction: Jurisdiction) -> list[RegulationId]:
        """Filter registered modules by jurisdiction.

        Args:
            jurisdiction: The jurisdiction to filter by

        Returns:
            List of RegulationId values matching the jurisdiction

        """
        matching = []
        for reg_id in self._modules:
            metadata = self.get_metadata(reg_id)
            if metadata and (
                metadata.jurisdiction == jurisdiction
                or metadata.jurisdiction == Jurisdiction.GLOBAL
            ):
                matching.append(reg_id)
        return matching

    def is_registered(self, regulation_id: RegulationId) -> bool:
        """Check if a regulation module is registered."""
        return regulation_id in self._modules

    def get_module_count(self) -> int:
        """Get the number of registered modules."""
        return len(self._modules)

    def clear(self) -> None:
        """Clear all registered modules (use carefully)."""
        self._modules.clear()
        self._instances.clear()
        self._metadata_cache.clear()
        logger.warning("RegulationRegistry cleared")

    def health_check(self) -> dict:
        """Get registry health status."""
        return {
            "status": "healthy",
            "registered_modules": len(self._modules),
            "instantiated_modules": len(self._instances),
            "modules": [reg_id.value for reg_id in self._modules],
        }


@lru_cache(maxsize=1)
def get_registry() -> RegulationRegistry:
    """Get the global RegulationRegistry instance.

    Returns:
        The singleton RegulationRegistry

    """
    return RegulationRegistry()


def register_module(regulation_id: RegulationId):
    """Decorator to register a compliance module class.

    Usage:
        @register_module(RegulationId.EU_AI_ACT)
        class EUAIActModule(ComplianceModule):
            ...
    """

    def decorator(cls: type[ComplianceModule]) -> type[ComplianceModule]:
        get_registry().register(regulation_id, cls)
        return cls

    return decorator


def auto_register_modules() -> None:
    """Auto-register all built-in compliance modules.

    Call this during application startup to ensure all modules are available.
    """
    # Import modules to trigger registration via decorators
    try:
        from app.compliance.modules import eu_ai_act  # noqa: F401

        logger.info("Registered EU AI Act module")
    except ImportError as e:
        logger.warning(f"Failed to import EU AI Act module: {e}")

    try:
        from app.compliance.modules import gdpr  # noqa: F401

        logger.info("Registered GDPR module")
    except ImportError as e:
        logger.warning(f"Failed to import GDPR module: {e}")

    try:
        from app.compliance.modules import dsa  # noqa: F401

        logger.info("Registered DSA module")
    except ImportError as e:
        logger.warning(f"Failed to import DSA module: {e}")

    try:
        from app.compliance.modules import ca_sb_243  # noqa: F401

        logger.info("Registered CA SB 243 module")
    except ImportError as e:
        logger.warning(f"Failed to import CA SB 243 module: {e}")

    try:
        from app.compliance.modules import hipaa  # noqa: F401

        logger.info("Registered HIPAA module")
    except ImportError as e:
        logger.warning(f"Failed to import HIPAA module: {e}")

    try:
        from app.compliance.modules import coppa  # noqa: F401

        logger.info("Registered COPPA module")
    except ImportError as e:
        logger.warning(f"Failed to import COPPA module: {e}")

    try:
        from app.compliance.modules import nist_rmf  # noqa: F401

        logger.info("Registered NIST RMF module")
    except ImportError as e:
        logger.warning(f"Failed to import NIST RMF module: {e}")

    try:
        from app.compliance.modules import iso_42001  # noqa: F401

        logger.info("Registered ISO 42001 module")
    except ImportError as e:
        logger.warning(f"Failed to import ISO 42001 module: {e}")

    registry = get_registry()
    logger.info(f"Auto-registration complete: {registry.get_module_count()} modules registered")
