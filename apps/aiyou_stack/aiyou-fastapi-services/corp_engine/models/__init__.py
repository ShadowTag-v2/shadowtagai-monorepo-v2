"""Corp Engine Models - Multi-tenant SaaS data models"""

from .tenant import (
    LICENSE_TIERS,
    Base,
    IntelFeed,
    LicenseTier,
    LicenseTierLimits,
    Tenant,
    TenantCreate,
    TenantResponse,
    TenantStatus,
    User,
    Workspace,
)

# Convenience alias
LICENSE_LIMITS = LICENSE_TIERS

__all__ = [
    "LICENSE_LIMITS",
    "LICENSE_TIERS",
    "Base",
    "IntelFeed",
    "LicenseTier",
    "LicenseTierLimits",
    "Tenant",
    "TenantCreate",
    "TenantResponse",
    "TenantStatus",
    "User",
    "Workspace",
]
