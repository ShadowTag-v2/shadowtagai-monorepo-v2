"""Corp Engine Enterprise Adapters
================================
Plug-and-play connectors for enterprise systems.
GCP-centric architecture - all processing on our managed infrastructure.
Customer systems accessed via API integrations only.

Supported Integrations:
- Microsoft 365 (Graph API, Azure AD, Teams, SharePoint)
- Salesforce (REST API, Bulk API, SOQL)
- More coming: SAP, ServiceNow, Workday, Oracle
"""

from .base_adapter import (
    AdapterConfig,
    AdapterRegistry,
    AdapterStatus,
    BaseAdapter,
    ConnectionHealth,
    SyncResult,
    adapter_registry,
)
from .ms365_adapter import (
    MS365Adapter,
    MS365Config,
    MS365Group,
    MS365User,
)
from .salesforce_adapter import (
    SalesforceAccount,
    SalesforceAdapter,
    SalesforceConfig,
    SalesforceContact,
    SalesforceLead,
    SalesforceOpportunity,
)

# Register adapters with the registry
adapter_registry.register_adapter_class("ms365", MS365Adapter)
adapter_registry.register_adapter_class("salesforce", SalesforceAdapter)

__all__ = [
    # Base
    "BaseAdapter",
    "AdapterConfig",
    "AdapterStatus",
    "ConnectionHealth",
    "SyncResult",
    "AdapterRegistry",
    "adapter_registry",
    # Microsoft 365
    "MS365Adapter",
    "MS365Config",
    "MS365User",
    "MS365Group",
    # Salesforce
    "SalesforceAdapter",
    "SalesforceConfig",
    "SalesforceAccount",
    "SalesforceContact",
    "SalesforceLead",
    "SalesforceOpportunity",
]
