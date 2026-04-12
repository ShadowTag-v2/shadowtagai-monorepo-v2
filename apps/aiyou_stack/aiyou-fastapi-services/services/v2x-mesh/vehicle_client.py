"""
V2X On-Vehicle Client Service

Runs on vehicle compute (Tesla HW5/HW6 or aftermarket edge box).
Handles:
- V2X radio communication (PC5/NR-V2X)
- Message signing and verification
- Local planner integration
- Vehicle state management
- Edge reasoning hooks
"""

import asyncio
import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from armp_protocol import (
    ARMPMessage,
    ARMPProtocol,
    GeoScope,
    MessageType,
)
from gossip_protocol import GossipConfig, GossipProtocol


@dataclass
class VehicleState:
    """Current vehicle state"""

    vehicle_id: str
    vehicle_type: str  # "car", "truck", "bus", "emergency"
    position: tuple[float, float, float]  # lat, lon, altitude
    velocity: tuple[float, float, float]  # vx, vy, vz (m/s)
    heading: float  # degrees
    acceleration: tuple[float, float, float]  # ax, ay, az (m/s²)
    timestamp: float
    capabilities: list[str]


@dataclass
class V2XClientConfig:
    """V2X client configuration"""

    vehicle_id: str
    vehicle_type: str = "car"
    beacon_interval_s: float = 1.0
    event_broadcast_radius_m: int = 1000
    map_sync_interval_s: float = 5.0
    use_tee: bool = True  # Use Trusted Execution Environment
    radio_interface: str = "pc5"  # "pc5" or "wifi_direct"


class VehicleClient:
    """On-vehicle V2X mesh client"""

    def __init__(
        self,
        config: V2XClientConfig,
        crypto_provider=None,  # For Ed25519 signing in TEE
        radio_provider=None,  # For actual radio transmission
        planner_callback: Callable | None = None,  # Hook to local FSD planner
    ):
        self.config = config
        self.crypto_provider = crypto_provider
        self.radio_provider = radio_provider
        self.planner_callback = planner_callback

        # Generate or load node ID
        self.node_id = self._load_or_generate_node_id()

        # Initialize protocols
        self.armp = ARMPProtocol(self.node_id)
        self.gossip = GossipProtocol(
            node_id=self.node_id, config=GossipConfig(), send_callback=self._send_to_radio
        )

        # Current vehicle state
        self.vehicle_state: VehicleState | None = None

        # Message handlers
        self.message_handlers: dict[MessageType, list[Callable]] = {
            MessageType.BEACON: [],
            MessageType.EVENT: [],
            MessageType.MAPDELTA: [],
            MessageType.CONSENSUS: [],
            MessageType.REVOCATION: [],
        }

        # Background tasks
        self.tasks: list[asyncio.Task] = []
        self.running = False

        # Statistics
        self.stats = {
            "beacons_sent": 0,
            "events_sent": 0,
            "events_received": 0,
            "total_messages_processed": 0,
            "fsd_interventions": 0,  # Alerts that triggered FSD action
        }

    def _load_or_generate_node_id(self) -> bytes:
        """Load persistent node ID or generate new one"""
        # In production, this would load from TEE/TPM
        # For now, generate based on vehicle ID
        return hashlib.sha256(self.config.vehicle_id.encode()).digest()[:8]

    async def start(self):
        """Start the V2X client"""
        self.running = True

        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._beacon_loop()),
            asyncio.create_task(self._radio_receive_loop()),
            asyncio.create_task(self._cleanup_loop()),
        ]

        print(f"V2X Client started for vehicle {self.config.vehicle_id}")

    async def stop(self):
        """Stop the V2X client"""
        self.running = False

        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("V2X Client stopped")

    def update_vehicle_state(self, state: VehicleState):
        """Update current vehicle state"""
        self.vehicle_state = state
        self.gossip.update_position(state.position[0], state.position[1])

    def register_handler(self, msg_type: MessageType, handler: Callable):
        """Register message handler callback"""
        self.message_handlers[msg_type].append(handler)

    async def broadcast_event(
        self,
        event_type: str,
        severity: int,
        description: str,
        affected_radius_m: float = None,
        sensor_data_hash: str | None = None,
    ):
        """Broadcast safety event to mesh"""
        if not self.vehicle_state:
            print("Cannot broadcast event: no vehicle state")
            return

        # Default to config radius if not specified
        if affected_radius_m is None:
            affected_radius_m = self.config.event_broadcast_radius_m

        # Create geo-scope
        geo_scope = GeoScope(
            latitude=self.vehicle_state.position[0],
            longitude=self.vehicle_state.position[1],
            radius_meters=int(affected_radius_m),
            ttl_hops=3,
        )

        # Create event message
        message = self.armp.create_event(
            event_type=event_type,
            severity=severity,
            position=self.vehicle_state.position,
            affected_radius_m=affected_radius_m,
            description=description,
            geo_scope=geo_scope,
            sensor_data_hash=sensor_data_hash,
        )

        # Sign message
        await self._sign_message(message)

        # Broadcast to mesh
        await self.gossip.broadcast_message(message)

        self.stats["events_sent"] += 1
        print(f"Broadcast event: {event_type} (severity={severity})")

    async def _beacon_loop(self):
        """Periodically broadcast beacon messages"""
        while self.running:
            try:
                if self.vehicle_state:
                    await self._send_beacon()
                await asyncio.sleep(self.config.beacon_interval_s)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Beacon loop error: {e}")
                await asyncio.sleep(1)

    async def _send_beacon(self):
        """Send beacon message"""
        if not self.vehicle_state:
            return

        # Create geo-scope (local area)
        geo_scope = GeoScope(
            latitude=self.vehicle_state.position[0],
            longitude=self.vehicle_state.position[1],
            radius_meters=500,  # Beacons only to immediate neighbors
            ttl_hops=1,
        )

        # Create beacon message
        message = self.armp.create_beacon(
            vehicle_type=self.vehicle_state.vehicle_type,
            position=self.vehicle_state.position,
            velocity=self.vehicle_state.velocity,
            heading=self.vehicle_state.heading,
            acceleration=self.vehicle_state.acceleration,
            capabilities=self.vehicle_state.capabilities,
            geo_scope=geo_scope,
        )

        # Sign message
        await self._sign_message(message)

        # Broadcast
        await self.gossip.broadcast_message(message)

        self.stats["beacons_sent"] += 1

    async def _radio_receive_loop(self):
        """Receive messages from radio"""
        while self.running:
            try:
                # In production, this would read from actual radio
                # For now, simulate receiving from network
                if self.radio_provider:
                    raw_data = await self.radio_provider.receive()
                    if raw_data:
                        await self._handle_raw_message(raw_data)

                await asyncio.sleep(0.01)  # 10ms poll interval
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Radio receive error: {e}")
                await asyncio.sleep(0.1)

    async def _handle_raw_message(self, raw_data: bytes):
        """Handle raw message from radio"""
        try:
            # Unpack message
            message = ARMPMessage.unpack(raw_data)

            # Verify signature
            if not await self._verify_signature(message):
                print(f"Invalid signature for message from {message.header.sender_id.hex()}")
                return

            # Validate message
            if not self.armp.validate_message(message):
                return

            # Let gossip protocol handle propagation
            is_new = await self.gossip.handle_message(message, from_peer=message.header.sender_id)

            if is_new:
                # Process message
                await self._process_message(message)

        except Exception as e:
            print(f"Error handling message: {e}")

    async def _process_message(self, message: ARMPMessage):
        """Process validated message"""
        self.stats["total_messages_processed"] += 1

        # Update peer info from beacon
        if message.header.msg_type == MessageType.BEACON:
            payload = message.payload
            self.gossip.add_peer(
                message.header.sender_id, position=(payload.position[0], payload.position[1])
            )

        # Handle critical events
        elif message.header.msg_type == MessageType.EVENT:
            self.stats["events_received"] += 1
            payload = message.payload

            # High severity events trigger FSD planner
            if payload.severity >= 7 and self.planner_callback:
                intervention = await self.planner_callback(message)
                if intervention:
                    self.stats["fsd_interventions"] += 1
                    print(f"FSD intervention triggered by event: {payload.event_type}")

        # Call registered handlers
        handlers = self.message_handlers.get(message.header.msg_type, [])
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                print(f"Handler error for {message.header.msg_type}: {e}")

    async def _sign_message(self, message: ARMPMessage):
        """Sign message using Ed25519 in TEE"""
        if self.crypto_provider:
            # In production, this uses HSM/TPM
            signature = await self.crypto_provider.sign(message.pack())
            message.signature = signature
        else:
            # Mock signature for development
            import hashlib

            message.signature = hashlib.sha256(message.pack()).digest()[:64]

    async def _verify_signature(self, message: ARMPMessage) -> bool:
        """Verify message signature"""
        if not message.signature:
            return False

        if self.crypto_provider:
            return await self.crypto_provider.verify(
                message.header.sender_id,
                message.pack()[:-64],  # Exclude signature from verification
                message.signature,
            )

        # Mock verification for development
        return True

    async def _send_to_radio(self, peer_id: bytes, message: ARMPMessage):
        """Send message via radio"""
        if self.radio_provider:
            packed = message.pack()
            await self.radio_provider.send(peer_id, packed)

    async def _cleanup_loop(self):
        """Periodic cleanup of stale data"""
        while self.running:
            try:
                await asyncio.sleep(10)
                self.gossip.cleanup_stale_peers()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cleanup error: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get client statistics"""
        return {
            **self.stats,
            **self.gossip.get_stats(),
            "vehicle_id": self.config.vehicle_id,
            "vehicle_type": self.config.vehicle_type,
            "position": self.vehicle_state.position if self.vehicle_state else None,
            "uptime_seconds": time.time() - self.start_time if hasattr(self, "start_time") else 0,
        }


# Mock providers for development/testing


class MockCryptoProvider:
    """Mock crypto provider for development"""

    def __init__(self):

        self.keys = {}

    async def sign(self, data: bytes) -> bytes:
        """Mock signing"""
        import hashlib

        return hashlib.sha256(data).digest()[:64]

    async def verify(self, node_id: bytes, data: bytes, signature: bytes) -> bool:
        """Mock verification"""
        return len(signature) == 64


class MockRadioProvider:
    """Mock radio provider for testing"""

    def __init__(self):
        self.message_queue = asyncio.Queue()

    async def send(self, peer_id: bytes, data: bytes):
        """Mock send"""
        print(f"Radio TX -> {peer_id.hex()[:8]}: {len(data)} bytes")

    async def receive(self) -> bytes | None:
        """Mock receive"""
        try:
            return await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
        except TimeoutError:
            return None


# Example usage
if __name__ == "__main__":
    import hashlib

    async def main():
        # Create client
        config = V2XClientConfig(vehicle_id="TEST-VEHICLE-001", vehicle_type="car")

        client = VehicleClient(
            config=config, crypto_provider=MockCryptoProvider(), radio_provider=MockRadioProvider()
        )

        # Define FSD planner callback
        async def fsd_planner_hook(message: ARMPMessage):
            """Hook to FSD planner for critical events"""
            if message.header.msg_type == MessageType.EVENT:
                event = message.payload
                print(
                    f"FSD Planner: Processing event {event.event_type} (severity={event.severity})"
                )
                # In production, this would interface with actual FSD planner
                return True  # Intervention taken
            return False

        client.planner_callback = fsd_planner_hook

        # Start client
        await client.start()

        # Simulate vehicle state updates
        for i in range(10):
            state = VehicleState(
                vehicle_id=config.vehicle_id,
                vehicle_type=config.vehicle_type,
                position=(37.7749 + i * 0.0001, -122.4194 + i * 0.0001, 10.0),
                velocity=(15.0, 0.0, 0.0),
                heading=90.0,
                acceleration=(0.0, 0.0, 0.0),
                timestamp=time.time(),
                capabilities=["fsd", "v2x", "gpu_edge"],
            )
            client.update_vehicle_state(state)

            # Simulate event
            if i == 5:
                await client.broadcast_event(
                    event_type="hard_brake",
                    severity=8,
                    description="Emergency braking detected ahead",
                )

            await asyncio.sleep(1)

        # Print stats
        print("\nClient Statistics:")
        import json

        print(json.dumps(client.get_stats(), indent=2))

        await client.stop()

    asyncio.run(main())
