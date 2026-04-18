"""CRDT-based Collaborative Mapping System

Implements conflict-free replicated data types (CRDTs) for:
- Distributed map updates (work zones, hazards, POIs)
- Convergent merge without coordination
- Nowgrep indexing for spatial queries
- Integration with MAPDELTA protocol
"""

import json
import time
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class MapFeature:
    """Geographic map feature"""

    feature_id: str
    feature_type: str  # "work_zone", "hazard", "traffic_light", "poi"
    geometry: dict[str, Any]  # GeoJSON geometry
    properties: dict[str, Any]
    created_at: int  # Unix timestamp in ms
    updated_at: int
    creator_node: str  # Node that created this feature
    version: int = 1
    deleted: bool = False
    valid_until: int | None = None  # Expiry timestamp


@dataclass
class MapDelta:
    """CRDT delta for map updates"""

    delta_id: str
    parent_deltas: list[str]  # Parent delta IDs (for causal ordering)
    operation: str  # "add", "update", "remove"
    feature: MapFeature
    timestamp: int
    node_id: str


class LWWElementSet:
    """Last-Write-Wins Element Set CRDT

    Each element has a timestamp. On conflict, newest wins.
    Handles additions and removals with causal ordering.
    """

    def __init__(self):
        self.add_set: dict[str, tuple[Any, int, str]] = {}  # id -> (value, timestamp, node_id)
        self.remove_set: dict[str, tuple[int, str]] = {}  # id -> (timestamp, node_id)

    def add(self, element_id: str, value: Any, timestamp: int, node_id: str):
        """Add element with timestamp"""
        # Check if we should add
        if element_id in self.add_set:
            existing_ts = self.add_set[element_id][1]
            # Only update if newer (or same timestamp but higher node_id for determinism)
            if timestamp > existing_ts or (
                timestamp == existing_ts and node_id > self.add_set[element_id][2]
            ):
                self.add_set[element_id] = (value, timestamp, node_id)
        else:
            self.add_set[element_id] = (value, timestamp, node_id)

    def remove(self, element_id: str, timestamp: int, node_id: str):
        """Remove element with timestamp"""
        if element_id in self.remove_set:
            existing_ts = self.remove_set[element_id][0]
            if timestamp > existing_ts or (
                timestamp == existing_ts and node_id > self.remove_set[element_id][1]
            ):
                self.remove_set[element_id] = (timestamp, node_id)
        else:
            self.remove_set[element_id] = (timestamp, node_id)

    def get(self, element_id: str) -> Any | None:
        """Get element if it exists and not removed"""
        if element_id not in self.add_set:
            return None

        value, add_ts, add_node = self.add_set[element_id]

        # Check if removed
        if element_id in self.remove_set:
            remove_ts, remove_node = self.remove_set[element_id]
            # Removal wins if timestamp is newer
            if remove_ts > add_ts or (remove_ts == add_ts and remove_node > add_node):
                return None

        return value

    def get_all(self) -> dict[str, Any]:
        """Get all non-removed elements"""
        result = {}
        for element_id in self.add_set:
            value = self.get(element_id)
            if value is not None:
                result[element_id] = value
        return result

    def merge(self, other: "LWWElementSet"):
        """Merge with another LWW set"""
        # Merge add set
        for element_id, (value, timestamp, node_id) in other.add_set.items():
            self.add(element_id, value, timestamp, node_id)

        # Merge remove set
        for element_id, (timestamp, node_id) in other.remove_set.items():
            self.remove(element_id, timestamp, node_id)


class CRDTMapStore:
    """CRDT-based map store for collaborative mapping

    Uses LWW-Element-Set CRDT for conflict-free updates
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.features = LWWElementSet()  # Feature storage
        self.deltas: dict[str, MapDelta] = {}  # Delta history
        self.applied_deltas: set[str] = set()  # Track applied deltas

        # Spatial index (simplified - production would use R-tree)
        self.spatial_index: dict[str, list[str]] = defaultdict(list)  # grid_cell -> [feature_ids]

        # Statistics
        self.stats = {
            "total_features": 0,
            "active_features": 0,
            "deltas_applied": 0,
            "merge_conflicts": 0,
        }

    def apply_delta(self, delta: MapDelta) -> bool:
        """Apply map delta

        Returns True if delta was newly applied
        """
        # Check if already applied
        if delta.delta_id in self.applied_deltas:
            return False

        # Verify parent deltas (causal ordering)
        for parent_id in delta.parent_deltas:
            if parent_id and parent_id not in self.applied_deltas:
                # Parent not yet applied - defer this delta
                return False

        # Apply operation
        if delta.operation == "add":
            self._add_feature(delta.feature, delta.timestamp, delta.node_id)
        elif delta.operation == "update":
            self._update_feature(delta.feature, delta.timestamp, delta.node_id)
        elif delta.operation == "remove":
            self._remove_feature(delta.feature.feature_id, delta.timestamp, delta.node_id)

        # Record delta
        self.deltas[delta.delta_id] = delta
        self.applied_deltas.add(delta.delta_id)
        self.stats["deltas_applied"] += 1

        return True

    def _add_feature(self, feature: MapFeature, timestamp: int, node_id: str):
        """Add feature to map"""
        self.features.add(feature.feature_id, feature, timestamp, node_id)
        self._index_feature(feature)
        self.stats["total_features"] += 1
        self.stats["active_features"] = len(self.features.get_all())

    def _update_feature(self, feature: MapFeature, timestamp: int, node_id: str):
        """Update existing feature"""
        # Remove from old index
        self._unindex_feature(feature.feature_id)

        # Update
        feature.updated_at = timestamp
        feature.version += 1
        self.features.add(feature.feature_id, feature, timestamp, node_id)

        # Re-index
        self._index_feature(feature)
        self.stats["active_features"] = len(self.features.get_all())

    def _remove_feature(self, feature_id: str, timestamp: int, node_id: str):
        """Remove feature from map"""
        self.features.remove(feature_id, timestamp, node_id)
        self._unindex_feature(feature_id)
        self.stats["active_features"] = len(self.features.get_all())

    def get_feature(self, feature_id: str) -> MapFeature | None:
        """Get feature by ID"""
        return self.features.get(feature_id)

    def query_area(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        feature_types: list[str] | None = None,
    ) -> list[MapFeature]:
        """Query features in geographic area"""
        # Get grid cells
        cells = self._get_grid_cells(min_lat, max_lat, min_lon, max_lon)

        # Collect features
        feature_ids = set()
        for cell in cells:
            feature_ids.update(self.spatial_index.get(cell, []))

        # Filter and return
        features = []
        for feature_id in feature_ids:
            feature = self.features.get(feature_id)
            if feature:
                # Check if in bounds
                if self._in_bounds(feature, min_lat, max_lat, min_lon, max_lon):
                    # Check type filter
                    if feature_types is None or feature.feature_type in feature_types:
                        # Check not expired
                        if feature.valid_until is None or feature.valid_until > int(
                            time.time() * 1000,
                        ):
                            features.append(feature)

        return features

    def merge_remote(self, remote_deltas: list[MapDelta]):
        """Merge deltas from remote node"""
        # Sort by causal order
        sorted_deltas = self._topological_sort(remote_deltas)

        # Apply each delta
        for delta in sorted_deltas:
            applied = self.apply_delta(delta)
            if not applied and delta.delta_id not in self.applied_deltas:
                # Conflict - record it
                self.stats["merge_conflicts"] += 1

    def create_delta(
        self,
        operation: str,
        feature: MapFeature,
        parent_deltas: list[str] | None = None,
    ) -> MapDelta:
        """Create new map delta"""
        delta = MapDelta(
            delta_id=str(uuid.uuid4()),
            parent_deltas=parent_deltas or [],
            operation=operation,
            feature=feature,
            timestamp=int(time.time() * 1000),
            node_id=self.node_id,
        )

        # Apply locally
        self.apply_delta(delta)

        return delta

    def _index_feature(self, feature: MapFeature):
        """Add feature to spatial index"""
        # Get bounding box from geometry
        bbox = self._get_bbox(feature.geometry)
        if not bbox:
            return

        min_lat, max_lat, min_lon, max_lon = bbox
        cells = self._get_grid_cells(min_lat, max_lat, min_lon, max_lon)

        for cell in cells:
            if feature.feature_id not in self.spatial_index[cell]:
                self.spatial_index[cell].append(feature.feature_id)

    def _unindex_feature(self, feature_id: str):
        """Remove feature from spatial index"""
        for cell_features in self.spatial_index.values():
            if feature_id in cell_features:
                cell_features.remove(feature_id)

    def _get_bbox(self, geometry: dict[str, Any]) -> tuple[float, float, float, float] | None:
        """Get bounding box from GeoJSON geometry"""
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates", [])

        if geom_type == "Point":
            lon, lat = coords
            return (lat, lat, lon, lon)
        if geom_type == "LineString" or geom_type == "MultiPoint":
            lats = [c[1] for c in coords]
            lons = [c[0] for c in coords]
            return (min(lats), max(lats), min(lons), max(lons))
        if geom_type == "Polygon":
            # Exterior ring
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return (min(lats), max(lats), min(lons), max(lons))

        return None

    def _get_grid_cells(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        cell_size: float = 0.01,  # ~1km at equator
    ) -> list[str]:
        """Get grid cells covering area"""
        cells = []

        lat = min_lat
        while lat <= max_lat:
            lon = min_lon
            while lon <= max_lon:
                cell = f"{int(lat / cell_size)}:{int(lon / cell_size)}"
                cells.append(cell)
                lon += cell_size
            lat += cell_size

        return cells

    def _in_bounds(
        self,
        feature: MapFeature,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
    ) -> bool:
        """Check if feature is in bounds"""
        bbox = self._get_bbox(feature.geometry)
        if not bbox:
            return False

        f_min_lat, f_max_lat, f_min_lon, f_max_lon = bbox

        # Check overlap
        return not (
            f_max_lat < min_lat or f_min_lat > max_lat or f_max_lon < min_lon or f_min_lon > max_lon
        )

    def _topological_sort(self, deltas: list[MapDelta]) -> list[MapDelta]:
        """Sort deltas by causal order (topological sort)"""
        # Build dependency graph
        {d.delta_id: d for d in deltas}
        in_degree = {d.delta_id: 0 for d in deltas}

        for delta in deltas:
            for parent in delta.parent_deltas:
                if parent in in_degree:
                    in_degree[delta.delta_id] += 1

        # Kahn's algorithm
        queue = [d for d in deltas if in_degree[d.delta_id] == 0]
        sorted_deltas = []

        while queue:
            current = queue.pop(0)
            sorted_deltas.append(current)

            # Find children
            for delta in deltas:
                if current.delta_id in delta.parent_deltas:
                    in_degree[delta.delta_id] -= 1
                    if in_degree[delta.delta_id] == 0:
                        queue.append(delta)

        return sorted_deltas

    def export_deltas(self, since_timestamp: int | None = None) -> list[dict]:
        """Export deltas for sync"""
        deltas = []

        for delta in self.deltas.values():
            if since_timestamp is None or delta.timestamp >= since_timestamp:
                deltas.append(
                    {
                        "delta_id": delta.delta_id,
                        "parent_deltas": delta.parent_deltas,
                        "operation": delta.operation,
                        "feature": asdict(delta.feature),
                        "timestamp": delta.timestamp,
                        "node_id": delta.node_id,
                    },
                )

        return deltas

    def get_stats(self) -> dict:
        """Get map store statistics"""
        return {
            **self.stats,
            "spatial_index_cells": len(self.spatial_index),
            "total_deltas": len(self.deltas),
        }


class MapSyncProtocol:
    """Protocol for syncing maps between nodes"""

    def __init__(self, map_store: CRDTMapStore):
        self.map_store = map_store

    async def sync_with_peer(self, peer_deltas: list[dict]) -> dict:
        """Sync with peer's map state

        Returns: sync statistics
        """
        # Convert to MapDelta objects
        deltas = []
        for delta_dict in peer_deltas:
            feature_dict = delta_dict["feature"]
            feature = MapFeature(**feature_dict)

            delta = MapDelta(
                delta_id=delta_dict["delta_id"],
                parent_deltas=delta_dict["parent_deltas"],
                operation=delta_dict["operation"],
                feature=feature,
                timestamp=delta_dict["timestamp"],
                node_id=delta_dict["node_id"],
            )
            deltas.append(delta)

        # Merge
        initial_count = self.map_store.stats["deltas_applied"]
        self.map_store.merge_remote(deltas)
        new_deltas = self.map_store.stats["deltas_applied"] - initial_count

        return {
            "received_deltas": len(peer_deltas),
            "applied_deltas": new_deltas,
            "conflicts": self.map_store.stats["merge_conflicts"],
        }

    def get_delta_digest(self) -> str:
        """Get digest of all deltas for quick sync check"""
        import hashlib

        delta_ids = sorted(self.map_store.applied_deltas)
        combined = ":".join(delta_ids)
        return hashlib.sha256(combined.encode()).hexdigest()


# Example usage
if __name__ == "__main__":
    # Create map store
    store = CRDTMapStore(node_id="vehicle-001")

    # Add work zone
    work_zone = MapFeature(
        feature_id=str(uuid.uuid4()),
        feature_type="work_zone",
        geometry={
            "type": "Polygon",
            "coordinates": [
                [
                    [-122.4194, 37.7749],
                    [-122.4194, 37.7750],
                    [-122.4193, 37.7750],
                    [-122.4193, 37.7749],
                    [-122.4194, 37.7749],
                ],
            ],
        },
        properties={"name": "Road Construction", "severity": "high", "lanes_closed": 2},
        created_at=int(time.time() * 1000),
        updated_at=int(time.time() * 1000),
        creator_node="vehicle-001",
        valid_until=int(time.time() * 1000) + 86400000,  # 24 hours
    )

    delta = store.create_delta("add", work_zone)
    print(f"Created delta: {delta.delta_id}")

    # Query area
    features = store.query_area(
        min_lat=37.774,
        max_lat=37.776,
        min_lon=-122.420,
        max_lon=-122.418,
        feature_types=["work_zone"],
    )

    print(f"\nFound {len(features)} features")
    for feature in features:
        print(f"  - {feature.feature_type}: {feature.properties.get('name')}")

    # Stats
    print("\nMap Store Statistics:")
    print(json.dumps(store.get_stats(), indent=2))
