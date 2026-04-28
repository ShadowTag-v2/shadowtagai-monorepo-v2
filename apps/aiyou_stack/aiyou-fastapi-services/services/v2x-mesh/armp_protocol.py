# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ARMP (ShadowTag-v4 Resilient Mesh Protocol) v1.0
Core protocol implementation for V2V/V2X mesh networking

Handles:
- BEACON: Periodic presence announcements
- EVENT: Critical safety events (collision, hazard)
- MAPDELTA: CRDT-based map updates
- CONSENSUS: Multi-node agreement on shared state
- REVOCATION: Identity/credential revocation
"""

import hashlib
import json
import struct
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageType(Enum):
    """ARMP message types"""

    BEACON = 0x01
    EVENT = 0x02
    MAPDELTA = 0x03
    CONSENSUS = 0x04
    REVOCATION = 0x05


class Priority(Enum):
    """Message priority levels for RF contention management"""

    CRITICAL = 0  # Collision imminent, <50ms latency
    HIGH = 1  # Safety event, <100ms latency
    MEDIUM = 2  # Traffic update, <500ms latency
    LOW = 3  # Map update, <2s latency


@dataclass
class GeoScope:
    """Geographic scope for message propagation"""

    latitude: float
    longitude: float
    radius_meters: int  # Propagation radius
    ttl_hops: int = 3  # Maximum hop count


@dataclass
class ARMPHeader:
    """ARMP protocol header (fixed 32 bytes)"""

    version: int = 1
    msg_type: MessageType = MessageType.BEACON
    priority: Priority = Priority.MEDIUM
    timestamp_ms: int = 0  # Unix timestamp in milliseconds
    sender_id: bytes = field(default_factory=lambda: b"\x00" * 8)  # 8-byte pseudonym
    sequence: int = 0
    geo_scope: GeoScope | None = None
    signature_offset: int = 0  # Offset to Ed25519 signature

    def pack(self) -> bytes:
        """Pack header to bytes"""
        packed = struct.pack(
            "!BBHHQI",
            self.version,
            self.msg_type.value,
            self.priority.value,
            0,  # Reserved
            self.timestamp_ms,
            self.sequence,
        )
        packed += self.sender_id[:8].ljust(8, b"\x00")

        # Add geo-scope if present
        if self.geo_scope:
            geo_packed = struct.pack(
                "!ffHH",
                self.geo_scope.latitude,
                self.geo_scope.longitude,
                self.geo_scope.radius_meters,
                self.geo_scope.ttl_hops,
            )
            packed += geo_packed
        else:
            packed += b"\x00" * 12

        return packed[:32].ljust(32, b"\x00")

    @classmethod
    def unpack(cls, data: bytes) -> "ARMPHeader":
        """Unpack header from bytes"""
        if len(data) < 32:
            raise ValueError(f"Invalid header size: {len(data)}")

        version, msg_type, priority, _, timestamp_ms, sequence = struct.unpack("!BBHHQI", data[:16])
        sender_id = data[16:24]

        # Unpack geo-scope
        lat, lon, radius, ttl = struct.unpack(
            "!ffHH",
            data[24:36] if len(data) >= 36 else data[24:32] + b"\x00" * 4,
        )
        geo_scope = GeoScope(lat, lon, radius, ttl) if radius > 0 else None

        return cls(
            version=version,
            msg_type=MessageType(msg_type),
            priority=Priority(priority),
            timestamp_ms=timestamp_ms,
            sender_id=sender_id,
            sequence=sequence,
            geo_scope=geo_scope,
        )


@dataclass
class BeaconPayload:
    """BEACON message payload - periodic presence announcement"""

    vehicle_type: str  # "car", "truck", "bus", "emergency"
    position: tuple[float, float, float]  # lat, lon, altitude
    velocity: tuple[float, float, float]  # vx, vy, vz (m/s)
    heading: float  # degrees
    acceleration: tuple[float, float, float]  # ax, ay, az (m/s²)
    capabilities: list[str]  # ["fsd", "v2x", "gpu_edge"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "vehicle_type": self.vehicle_type,
            "position": self.position,
            "velocity": self.velocity,
            "heading": self.heading,
            "acceleration": self.acceleration,
            "capabilities": self.capabilities,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BeaconPayload":
        return cls(
            vehicle_type=data["vehicle_type"],
            position=tuple(data["position"]),
            velocity=tuple(data["velocity"]),
            heading=data["heading"],
            acceleration=tuple(data["acceleration"]),
            capabilities=data["capabilities"],
        )


@dataclass
class EventPayload:
    """EVENT message payload - critical safety event"""

    event_type: str  # "collision_risk", "hard_brake", "pedestrian", "obstacle"
    severity: int  # 0-10
    position: tuple[float, float, float]
    affected_radius_m: float
    description: str
    sensor_data_hash: str | None = None  # Hash of supporting sensor data

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "severity": self.severity,
            "position": self.position,
            "affected_radius_m": self.affected_radius_m,
            "description": self.description,
            "sensor_data_hash": self.sensor_data_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventPayload":
        return cls(
            event_type=data["event_type"],
            severity=data["severity"],
            position=tuple(data["position"]),
            affected_radius_m=data["affected_radius_m"],
            description=data["description"],
            sensor_data_hash=data.get("sensor_data_hash"),
        )


@dataclass
class MapDeltaPayload:
    """MAPDELTA message payload - CRDT map update"""

    delta_id: str  # UUID for this delta
    parent_deltas: list[str]  # Parent delta IDs (for CRDT merge)
    operation: str  # "add", "update", "remove"
    feature_type: str  # "work_zone", "hazard", "traffic_light", "poi"
    geometry: dict[str, Any]  # GeoJSON geometry
    properties: dict[str, Any]  # Feature properties
    valid_until: int | None = None  # Unix timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "delta_id": self.delta_id,
            "parent_deltas": self.parent_deltas,
            "operation": self.operation,
            "feature_type": self.feature_type,
            "geometry": self.geometry,
            "properties": self.properties,
            "valid_until": self.valid_until,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MapDeltaPayload":
        return cls(
            delta_id=data["delta_id"],
            parent_deltas=data["parent_deltas"],
            operation=data["operation"],
            feature_type=data["feature_type"],
            geometry=data["geometry"],
            properties=data["properties"],
            valid_until=data.get("valid_until"),
        )


@dataclass
class ConsensusPayload:
    """CONSENSUS message payload - k-of-n agreement"""

    proposal_id: str  # UUID for this consensus round
    round_number: int
    proposal_type: str  # "map_update", "revocation", "config_change"
    proposal_data: dict[str, Any]
    votes: dict[str, bool]  # node_id -> vote (True=approve, False=reject)
    threshold: int  # Required votes for consensus (k)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "round_number": self.round_number,
            "proposal_type": self.proposal_type,
            "proposal_data": self.proposal_data,
            "votes": self.votes,
            "threshold": self.threshold,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConsensusPayload":
        return cls(
            proposal_id=data["proposal_id"],
            round_number=data["round_number"],
            proposal_type=data["proposal_type"],
            proposal_data=data["proposal_data"],
            votes=data["votes"],
            threshold=data["threshold"],
        )


@dataclass
class RevocationPayload:
    """REVOCATION message payload - credential/identity revocation"""

    revoked_id: bytes  # Node ID or credential hash being revoked
    reason: str  # "compromised", "misbehavior", "expired"
    revocation_authority: str  # Issuer of revocation
    proof: str  # Cryptographic proof of authority
    effective_time: int  # Unix timestamp

    def to_dict(self) -> dict[str, Any]:
        return {
            "revoked_id": self.revoked_id.hex(),
            "reason": self.reason,
            "revocation_authority": self.revocation_authority,
            "proof": self.proof,
            "effective_time": self.effective_time,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RevocationPayload":
        return cls(
            revoked_id=bytes.fromhex(data["revoked_id"]),
            reason=data["reason"],
            revocation_authority=data["revocation_authority"],
            proof=data["proof"],
            effective_time=data["effective_time"],
        )


class ARMPMessage:
    """Complete ARMP protocol message"""

    def __init__(self, header: ARMPHeader, payload: Any, signature: bytes | None = None):
        self.header = header
        self.payload = payload
        self.signature = signature  # Ed25519 signature (64 bytes)

    def pack(self) -> bytes:
        """Pack complete message to bytes"""
        # Pack header
        packed = self.header.pack()

        # Serialize payload
        payload_dict = self.payload.to_dict()
        payload_json = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")

        # Add payload length and payload
        packed += struct.pack("!I", len(payload_json))
        packed += payload_json

        # Add signature if present
        if self.signature:
            packed += self.signature[:64].ljust(64, b"\x00")

        return packed

    @classmethod
    def unpack(cls, data: bytes) -> "ARMPMessage":
        """Unpack message from bytes"""
        # Unpack header
        header = ARMPHeader.unpack(data[:32])

        # Unpack payload
        payload_len = struct.unpack("!I", data[32:36])[0]
        payload_json = data[36 : 36 + payload_len]
        payload_dict = json.loads(payload_json.decode("utf-8"))

        # Reconstruct payload based on message type
        payload_classes = {
            MessageType.BEACON: BeaconPayload,
            MessageType.EVENT: EventPayload,
            MessageType.MAPDELTA: MapDeltaPayload,
            MessageType.CONSENSUS: ConsensusPayload,
            MessageType.REVOCATION: RevocationPayload,
        }

        payload_class = payload_classes.get(header.msg_type)
        if not payload_class:
            raise ValueError(f"Unknown message type: {header.msg_type}")

        payload = payload_class.from_dict(payload_dict)

        # Extract signature if present
        signature_start = 36 + payload_len
        signature = (
            data[signature_start : signature_start + 64]
            if len(data) >= signature_start + 64
            else None
        )

        return cls(header, payload, signature)

    def compute_hash(self) -> str:
        """Compute message hash for deduplication"""
        packed = self.pack()
        # Hash everything except signature
        hashable = packed[:-64] if self.signature else packed
        return hashlib.sha256(hashable).hexdigest()

    def is_replay(self, seen_hashes: set, max_age_ms: int = 5000) -> bool:
        """Check if message is a replay attack"""
        msg_hash = self.compute_hash()

        # Check if we've seen this exact message before
        if msg_hash in seen_hashes:
            return True

        # Check if message is too old
        current_time_ms = int(time.time() * 1000)
        return current_time_ms - self.header.timestamp_ms > max_age_ms


class ARMPProtocol:
    """ARMP protocol handler"""

    def __init__(self, node_id: bytes):
        self.node_id = node_id
        self.sequence = 0
        self.seen_messages: set = set()  # Message hashes
        self.message_cache: dict[str, ARMPMessage] = {}  # For deduplication

    def create_beacon(
        self,
        vehicle_type: str,
        position: tuple,
        velocity: tuple,
        heading: float,
        acceleration: tuple,
        capabilities: list[str],
        geo_scope: GeoScope,
    ) -> ARMPMessage:
        """Create BEACON message"""
        header = ARMPHeader(
            msg_type=MessageType.BEACON,
            priority=Priority.LOW,
            timestamp_ms=int(time.time() * 1000),
            sender_id=self.node_id,
            sequence=self._next_sequence(),
            geo_scope=geo_scope,
        )

        payload = BeaconPayload(
            vehicle_type=vehicle_type,
            position=position,
            velocity=velocity,
            heading=heading,
            acceleration=acceleration,
            capabilities=capabilities,
        )

        return ARMPMessage(header, payload)

    def create_event(
        self,
        event_type: str,
        severity: int,
        position: tuple,
        affected_radius_m: float,
        description: str,
        geo_scope: GeoScope,
        sensor_data_hash: str | None = None,
    ) -> ARMPMessage:
        """Create EVENT message"""
        # Map severity to priority
        priority = (
            Priority.CRITICAL
            if severity >= 8
            else Priority.HIGH
            if severity >= 5
            else Priority.MEDIUM
        )

        header = ARMPHeader(
            msg_type=MessageType.EVENT,
            priority=priority,
            timestamp_ms=int(time.time() * 1000),
            sender_id=self.node_id,
            sequence=self._next_sequence(),
            geo_scope=geo_scope,
        )

        payload = EventPayload(
            event_type=event_type,
            severity=severity,
            position=position,
            affected_radius_m=affected_radius_m,
            description=description,
            sensor_data_hash=sensor_data_hash,
        )

        return ARMPMessage(header, payload)

    def create_mapdelta(
        self,
        delta_id: str,
        parent_deltas: list[str],
        operation: str,
        feature_type: str,
        geometry: dict[str, Any],
        properties: dict[str, Any],
        geo_scope: GeoScope,
        valid_until: int | None = None,
    ) -> ARMPMessage:
        """Create MAPDELTA message"""
        header = ARMPHeader(
            msg_type=MessageType.MAPDELTA,
            priority=Priority.MEDIUM,
            timestamp_ms=int(time.time() * 1000),
            sender_id=self.node_id,
            sequence=self._next_sequence(),
            geo_scope=geo_scope,
        )

        payload = MapDeltaPayload(
            delta_id=delta_id,
            parent_deltas=parent_deltas,
            operation=operation,
            feature_type=feature_type,
            geometry=geometry,
            properties=properties,
            valid_until=valid_until,
        )

        return ARMPMessage(header, payload)

    def validate_message(self, message: ARMPMessage) -> bool:
        """Validate incoming message"""
        # Check for replay
        if message.is_replay(self.seen_messages):
            return False

        # Add to seen messages
        self.seen_messages.add(message.compute_hash())

        # Clean old hashes periodically (keep last 10000)
        if len(self.seen_messages) > 10000:
            # Keep only recent messages
            self.seen_messages = set(list(self.seen_messages)[-5000:])

        return True

    def _next_sequence(self) -> int:
        """Get next sequence number"""
        self.sequence = (self.sequence + 1) % 0xFFFFFFFF
        return self.sequence
