"""CoreWeave GPU Orchestration Service.

Manages GPU resources across cloud and edge nodes.
"""

import time
import uuid


# Mock client simulating CoreWeave API interactions
class CoreWeaveClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def list_nodes(self):
        """Mock list nodes."""
        return [
            {"id": "node-1", "type": "L40S", "status": "idle", "region": "us-east-1"},
            {"id": "node-2", "type": "H100", "status": "busy", "region": "us-central-1"},
            {"id": "node-3", "type": "A100", "status": "idle", "region": "eu-west-1"},
        ]

    def provision_node(self, node_type: str, region: str):
        """Mock provision node."""
        return {
            "id": f"node-{uuid.uuid4()}",
            "type": node_type,
            "status": "provisioning",
            "region": region,
        }


class GPUOrchestrator:
    """GPU Orchestration Logic."""

    def __init__(self, api_key: str):
        self.client = CoreWeaveClient(api_key)
        self._node_cache = []
        self._last_refresh = 0

    def get_available_nodes(self, min_gpu_type: str = "L40S") -> list[dict]:
        """Get list of available nodes meeting criteria."""
        self._refresh_if_needed()
        return [
            node
            for node in self._node_cache
            if node["status"] == "idle"
            and self._check_gpu_compatibility(node["type"], min_gpu_type)
        ]

    def request_compute(self, workload_type: str, region: str = "us-east-1") -> str | None:
        """Request compute resource for a workload."""
        # Simple scheduling logic
        nodes = self.get_available_nodes()
        regional_nodes = [n for n in nodes if n["region"] == region]

        if regional_nodes:
            # Pick first available in region
            return regional_nodes[0]["id"]

        # Fallback: Provision new node if autoscaling allows (mocked)
        # In production this would check cost policies
        try:
            node = self.client.provision_node("L40S", region)
            return node["id"]
        except Exception:
            return None

    def _refresh_if_needed(self):
        """Refresh node cache every 30 seconds."""
        if time.time() - self._last_refresh > 30:
            self._node_cache = self.client.list_nodes()
            self._last_refresh = time.time()

    def _check_gpu_compatibility(self, current: str, required: str) -> bool:
        """Check if current GPU type meets requirements."""
        # Simple hierarchy: H100 > A100 > L40S > A10G
        tiers = ["A10G", "L40S", "A100", "H100"]
        try:
            curr_idx = tiers.index(current)
            req_idx = tiers.index(required)
            return curr_idx >= req_idx
        except ValueError:
            return False
