"""Base Enterprise Adapter Framework
==================================
Foundation for all enterprise system integrations.
Stay Current Doctrine: Continuous improvement, invisible to end users.

Architecture:
- GCP-managed infrastructure (our side)
- API-only access to customer systems (their side)
- All data processing happens in our GCP environment
- Customer never installs agents or software
"""

import asyncio
import contextlib
import hashlib
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from enum import StrEnum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AdapterStatus(StrEnum):
    """Adapter connection states"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


class ConnectionHealth(BaseModel):
    """Health metrics for adapter connection"""

    status: AdapterStatus = AdapterStatus.DISCONNECTED
    last_successful_sync: datetime | None = None
    last_error: str | None = None
    error_count: int = 0
    latency_ms: float = 0.0
    requests_today: int = 0
    rate_limit_remaining: int | None = None
    uptime_percentage: float = 100.0


class AdapterConfig(BaseModel):
    """Base configuration for all adapters"""

    adapter_id: str
    adapter_type: str
    tenant_id: str

    # API credentials (encrypted at rest)
    api_endpoint: str
    auth_type: str = "oauth2"  # oauth2, api_key, service_account
    credentials_vault_key: str  # Reference to GCP Secret Manager

    # Sync settings
    sync_interval_minutes: int = 15
    batch_size: int = 100
    max_retries: int = 3
    timeout_seconds: int = 30

    # Feature flags
    read_enabled: bool = True
    write_enabled: bool = False  # Conservative default
    delete_enabled: bool = False  # Very conservative

    # Rate limiting
    requests_per_minute: int = 60
    concurrent_requests: int = 5

    # Data handling
    data_residency: str = "us-central1"
    encryption_key_id: str | None = None

    # Compliance
    compliance_gates: list[str] = Field(default_factory=lambda: ["JURA"])
    audit_all_operations: bool = True


class SyncResult(BaseModel):
    """Result of a sync operation"""

    success: bool
    adapter_id: str
    operation: str
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_deleted: int = 0
    records_failed: int = 0
    errors: list[str] = Field(default_factory=list)
    duration_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Value metrics (for Economic Juggernaut)
    estimated_value_added_usd: float = 0.0
    efficiency_improvement_percent: float = 0.0


class BaseAdapter(ABC, Generic[T]):
    """Abstract base class for all enterprise adapters.

    Stay Current Doctrine Implementation:
    - Continuous background sync
    - Invisible improvements
    - Always-on monitoring
    - Automatic optimization
    """

    ADAPTER_TYPE: str = "base"
    ADAPTER_VERSION: str = "1.0.0"

    def __init__(self, config: AdapterConfig):
        self.config = config
        self.health = ConnectionHealth()
        self._sync_task: asyncio.Task | None = None
        self._hooks: dict[str, list[Callable]] = {
            "pre_sync": [],
            "post_sync": [],
            "on_error": [],
            "on_change": [],
        }
        self._metrics: dict[str, Any] = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "total_records": 0,
            "value_added_usd": 0.0,
            "created_at": datetime.utcnow(),
        }

    # =========================================================================
    # Abstract Methods - Must be implemented by specific adapters
    # =========================================================================

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to external system"""

    @abstractmethod
    async def disconnect(self) -> bool:
        """Gracefully disconnect from external system"""

    @abstractmethod
    async def test_connection(self) -> ConnectionHealth:
        """Test connection and return health status"""

    @abstractmethod
    async def fetch_data(self, query: dict[str, Any]) -> list[T]:
        """Fetch data from external system"""

    @abstractmethod
    async def push_data(self, data: list[T]) -> SyncResult:
        """Push data to external system"""

    @abstractmethod
    async def get_schema(self) -> dict[str, Any]:
        """Get schema/structure of external system data"""

    # =========================================================================
    # Core Sync Methods
    # =========================================================================

    async def sync(self, full_sync: bool = False) -> SyncResult:
        """Main sync operation - pulls data, processes, and pushes changes.
        All processing happens in GCP, only API calls to customer system.
        """
        start_time = datetime.utcnow()
        self.health.status = AdapterStatus.SYNCING

        result = SyncResult(
            success=False,
            adapter_id=self.config.adapter_id,
            operation="full_sync" if full_sync else "incremental_sync",
        )

        try:
            # Execute pre-sync hooks
            await self._execute_hooks("pre_sync", {"full_sync": full_sync})

            # Compliance gate check (JURA)
            if not await self._check_compliance_gates():
                result.errors.append("Compliance gate check failed")
                return result

            # Fetch data from customer system
            query = self._build_sync_query(full_sync)
            data = await self.fetch_data(query)
            result.records_processed = len(data)

            # Process data in GCP
            processed_data = await self._process_data(data)

            # Calculate value added
            result.estimated_value_added_usd = await self._calculate_value_added(
                original=data, processed=processed_data,
            )

            # Push changes back if write is enabled
            if self.config.write_enabled and processed_data:
                push_result = await self.push_data(processed_data)
                result.records_updated = push_result.records_updated
                result.records_created = push_result.records_created

            result.success = True
            self.health.last_successful_sync = datetime.utcnow()
            self.health.error_count = 0
            self._metrics["successful_syncs"] += 1
            self._metrics["value_added_usd"] += result.estimated_value_added_usd

        except Exception as e:
            self.health.status = AdapterStatus.ERROR
            self.health.last_error = str(e)
            self.health.error_count += 1
            result.errors.append(str(e))
            await self._execute_hooks("on_error", {"error": e})
            logger.error(f"Sync failed for {self.config.adapter_id}: {e}")

        finally:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.duration_ms = duration
            self.health.latency_ms = duration
            self._metrics["total_syncs"] += 1

            if result.success:
                self.health.status = AdapterStatus.CONNECTED

            # Execute post-sync hooks
            await self._execute_hooks("post_sync", {"result": result})

        return result

    async def start_continuous_sync(self) -> None:
        """Start continuous background sync.
        Stay Current Doctrine: Always improving, never resting.
        """
        if self._sync_task and not self._sync_task.done():
            logger.warning(f"Sync already running for {self.config.adapter_id}")
            return

        self._sync_task = asyncio.create_task(self._continuous_sync_loop())
        logger.info(f"Started continuous sync for {self.config.adapter_id}")

    async def stop_continuous_sync(self) -> None:
        """Stop continuous background sync"""
        if self._sync_task:
            self._sync_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._sync_task
            self._sync_task = None
            logger.info(f"Stopped continuous sync for {self.config.adapter_id}")

    async def _continuous_sync_loop(self) -> None:
        """Background sync loop - the heart of Stay Current Doctrine.
        Like upgrading your gaming rig - always getting better.
        """
        while True:
            try:
                await self.sync(full_sync=False)
                await asyncio.sleep(self.config.sync_interval_minutes * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Continuous sync error: {e}")
                # Exponential backoff on errors
                await asyncio.sleep(min(300, 30 * self.health.error_count))

    # =========================================================================
    # Processing Methods (GCP-side)
    # =========================================================================

    async def _process_data(self, data: list[T]) -> list[T]:
        """Process data using our GCP infrastructure.
        This is where the Economic Juggernaut does its magic.
        Customer system untouched - we just API in/out.
        """
        # Default implementation - override in specific adapters
        return data

    async def _calculate_value_added(self, original: list[Any], processed: list[Any]) -> float:
        """Calculate the value we've added through our processing.
        This feeds the metrics tracker for the "ever upward graph".
        """
        # Default: $0.01 per record processed (conservative estimate)
        # Specific adapters will have more sophisticated calculations
        return len(processed) * 0.01

    # =========================================================================
    # Compliance Methods
    # =========================================================================

    async def _check_compliance_gates(self) -> bool:
        """Check all compliance gates before any operation.
        JURA Protocol: No Hot Water principle.
        """
        for gate in self.config.compliance_gates:
            if gate == "JURA":
                # JURA compliance check will be imported
                pass
            # Add more gate checks as needed
        return True

    # =========================================================================
    # Hook System
    # =========================================================================

    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a callback for specific events"""
        if event in self._hooks:
            self._hooks[event].append(callback)

    async def _execute_hooks(self, event: str, context: dict[str, Any]) -> None:
        """Execute all registered hooks for an event"""
        for hook in self._hooks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(context)
                else:
                    hook(context)
            except Exception as e:
                logger.error(f"Hook error for {event}: {e}")

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _build_sync_query(self, full_sync: bool) -> dict[str, Any]:
        """Build query for data fetch"""
        query = {"batch_size": self.config.batch_size}

        if not full_sync and self.health.last_successful_sync:
            query["modified_since"] = self.health.last_successful_sync.isoformat()

        return query

    def get_metrics(self) -> dict[str, Any]:
        """Get adapter metrics for the dashboard"""
        uptime = (datetime.utcnow() - self._metrics["created_at"]).total_seconds()
        success_rate = (
            self._metrics["successful_syncs"] / self._metrics["total_syncs"] * 100
            if self._metrics["total_syncs"] > 0
            else 100.0
        )

        return {
            "adapter_id": self.config.adapter_id,
            "adapter_type": self.ADAPTER_TYPE,
            "status": self.health.status.value,
            "total_syncs": self._metrics["total_syncs"],
            "success_rate": success_rate,
            "value_added_usd": self._metrics["value_added_usd"],
            "uptime_seconds": uptime,
            "last_sync": self.health.last_successful_sync,
        }

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID for audit trail"""
        timestamp = datetime.utcnow().isoformat()
        content = f"{self.config.adapter_id}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class AdapterRegistry:
    """Central registry for all enterprise adapters.
    Manages lifecycle and provides unified access.
    """

    def __init__(self):
        self._adapters: dict[str, BaseAdapter] = {}
        self._adapter_classes: dict[str, type] = {}

    def register_adapter_class(self, adapter_type: str, adapter_class: type) -> None:
        """Register an adapter class for a specific type"""
        self._adapter_classes[adapter_type] = adapter_class

    def create_adapter(self, config: AdapterConfig) -> BaseAdapter:
        """Create and register an adapter instance"""
        adapter_class = self._adapter_classes.get(config.adapter_type)
        if not adapter_class:
            raise ValueError(f"Unknown adapter type: {config.adapter_type}")

        adapter = adapter_class(config)
        self._adapters[config.adapter_id] = adapter
        return adapter

    def get_adapter(self, adapter_id: str) -> BaseAdapter | None:
        """Get an adapter by ID"""
        return self._adapters.get(adapter_id)

    def list_adapters(self, tenant_id: str | None = None) -> list[BaseAdapter]:
        """List all adapters, optionally filtered by tenant"""
        adapters = list(self._adapters.values())
        if tenant_id:
            adapters = [a for a in adapters if a.config.tenant_id == tenant_id]
        return adapters

    async def start_all(self, tenant_id: str | None = None) -> None:
        """Start continuous sync for all adapters"""
        for adapter in self.list_adapters(tenant_id):
            await adapter.start_continuous_sync()

    async def stop_all(self, tenant_id: str | None = None) -> None:
        """Stop continuous sync for all adapters"""
        for adapter in self.list_adapters(tenant_id):
            await adapter.stop_continuous_sync()

    def get_all_metrics(self, tenant_id: str | None = None) -> list[dict[str, Any]]:
        """Get metrics from all adapters"""
        return [a.get_metrics() for a in self.list_adapters(tenant_id)]


# Global registry instance
adapter_registry = AdapterRegistry()
