# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gossip Protocol for V2X Mesh Networking

Implements epidemic-style message propagation with:
- Geo-scoped TTL (messages expire based on distance)
- Anti-entropy (periodic sync to recover missed messages)
- Adaptive fanout (adjust based on network density)
- Backpressure (rate limiting to prevent broadcast storms)
"""

import asyncio
import math
import random
import time
from collections import defaultdict
from dataclasses import dataclass

from armp_protocol import ARMPMessage, Priority


@dataclass
class PeerInfo:
    """Information about a mesh peer"""

    peer_id: bytes
    last_seen: float  # Unix timestamp
    position: tuple[float, float] | None = None  # lat, lon
    distance_m: float | None = None
    rtt_ms: float = 0  # Round-trip time
    packet_loss: float = 0  # 0.0 - 1.0
    reliability_score: float = 1.0  # 0.0 - 1.0


@dataclass
class GossipConfig:
    """Gossip protocol configuration"""

    # Fanout (number of peers to forward to)
    min_fanout: int = 3
    max_fanout: int = 8
    target_fanout: int = 5

    # Timing
    beacon_interval_ms: int = 1000  # Send beacon every 1s
    sync_interval_ms: int = 5000  # Anti-entropy sync every 5s
    peer_timeout_ms: int = 10000  # Drop peer after 10s silence

    # Rate limiting
    max_messages_per_second: int = 100  # Per priority level
    burst_size: int = 20

    # Geographic
    max_propagation_distance_m: float = 5000  # 5km max range
    neighbor_distance_m: float = 500  # Direct neighbors within 500m


class TokenBucket:
    """Token bucket for rate limiting"""

    def __init__(self, rate: int, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens, return True if allowed"""
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        # Refill tokens
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class GossipProtocol:
    """Epidemic gossip protocol for mesh networking"""

    def __init__(
        self,
        node_id: bytes,
        config: GossipConfig | None = None,
        send_callback=None,  # async def send(peer_id, message)
    ):
        self.node_id = node_id
        self.config = config or GossipConfig()
        self.send_callback = send_callback

        # Peer management
        self.peers: dict[bytes, PeerInfo] = {}
        self.active_peers: set[bytes] = set()

        # Message tracking
        self.message_cache: dict[str, ARMPMessage] = {}  # msg_hash -> message
        self.peer_message_versions: dict[bytes, set[str]] = defaultdict(
            set,
        )  # peer_id -> {msg_hashes}

        # Rate limiting per priority
        self.rate_limiters: dict[Priority, TokenBucket] = {
            Priority.CRITICAL: TokenBucket(200, 50),  # 200/s, burst 50
            Priority.HIGH: TokenBucket(100, 30),  # 100/s, burst 30
            Priority.MEDIUM: TokenBucket(50, 20),  # 50/s, burst 20
            Priority.LOW: TokenBucket(20, 10),  # 20/s, burst 10
        }

        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_dropped": 0,
            "rate_limited": 0,
        }

        # Current position (updated by vehicle state manager)
        self.current_position: tuple[float, float] | None = None

    def update_position(self, lat: float, lon: float):
        """Update current vehicle position"""
        self.current_position = (lat, lon)
        self._update_peer_distances()

    def add_peer(self, peer_id: bytes, position: tuple[float, float] | None = None):
        """Add or update peer information"""
        if peer_id not in self.peers:
            self.peers[peer_id] = PeerInfo(
                peer_id=peer_id,
                last_seen=time.time(),
                position=position,
            )
        else:
            self.peers[peer_id].last_seen = time.time()
            if position:
                self.peers[peer_id].position = position

        self.active_peers.add(peer_id)
        self._update_peer_distances()

    def remove_peer(self, peer_id: bytes):
        """Remove peer"""
        self.active_peers.discard(peer_id)
        self.peers.pop(peer_id, None)
        self.peer_message_versions.pop(peer_id, None)

    async def handle_message(self, message: ARMPMessage, from_peer: bytes | None = None) -> bool:
        """Handle incoming message
        Returns True if message is new and should be processed
        """
        msg_hash = message.compute_hash()

        # Update peer info
        if from_peer:
            self.add_peer(from_peer)
            self.peer_message_versions[from_peer].add(msg_hash)

        # Check if we've seen this message
        if msg_hash in self.message_cache:
            return False

        # Check geo-scope
        if not self._is_in_scope(message):
            self.stats["messages_dropped"] += 1
            return False

        # Rate limiting
        if not self._check_rate_limit(message.header.priority):
            self.stats["rate_limited"] += 1
            return False

        # Store message
        self.message_cache[msg_hash] = message
        self.stats["messages_received"] += 1

        # Gossip to peers
        await self._gossip_message(message, exclude_peer=from_peer)

        # Clean old messages periodically
        if len(self.message_cache) > 5000:
            self._clean_message_cache()

        return True

    async def broadcast_message(self, message: ARMPMessage):
        """Broadcast message to mesh"""
        msg_hash = message.compute_hash()
        self.message_cache[msg_hash] = message

        await self._gossip_message(message)

    async def _gossip_message(self, message: ARMPMessage, exclude_peer: bytes | None = None):
        """Forward message to selected peers"""
        # Select peers for forwarding
        target_peers = self._select_gossip_targets(message, exclude_peer)

        # Send to each target
        tasks = []
        for peer_id in target_peers:
            if self.send_callback:
                tasks.append(self.send_callback(peer_id, message))
            self.peer_message_versions[peer_id].add(message.compute_hash())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            self.stats["messages_sent"] += len(tasks)

    def _select_gossip_targets(
        self,
        message: ARMPMessage,
        exclude_peer: bytes | None = None,
    ) -> list[bytes]:
        """Select peers to forward message to"""
        # Filter eligible peers
        eligible = []
        msg_hash = message.compute_hash()

        for peer_id in self.active_peers:
            if peer_id == exclude_peer:
                continue
            if peer_id == message.header.sender_id:
                continue
            if msg_hash in self.peer_message_versions.get(peer_id, set()):
                continue

            peer = self.peers[peer_id]

            # Check if peer is in message geo-scope
            if message.header.geo_scope and peer.position:
                distance = self._haversine_distance(
                    (message.header.geo_scope.latitude, message.header.geo_scope.longitude),
                    peer.position,
                )
                if distance > message.header.geo_scope.radius_meters:
                    continue

            eligible.append((peer_id, peer))

        if not eligible:
            return []

        # Adaptive fanout based on priority and network density
        fanout = self._compute_fanout(message.header.priority, len(eligible))

        # Sort by reliability score and distance
        eligible.sort(key=lambda x: (x[1].reliability_score, -(x[1].distance_m or 0)), reverse=True)

        # Select top peers
        selected = [peer_id for peer_id, _ in eligible[:fanout]]

        # Add some randomness to avoid always selecting same peers
        if len(eligible) > fanout:
            extra = random.sample([p for p, _ in eligible[fanout:]], min(2, len(eligible) - fanout))
            selected.extend(extra)

        return selected

    def _compute_fanout(self, priority: Priority, num_eligible: int) -> int:
        """Compute adaptive fanout based on priority and network density"""
        # Higher priority = more redundancy
        base_fanout = {
            Priority.CRITICAL: self.config.max_fanout,
            Priority.HIGH: self.config.target_fanout + 2,
            Priority.MEDIUM: self.config.target_fanout,
            Priority.LOW: self.config.min_fanout,
        }.get(priority, self.config.target_fanout)

        # Adjust for network density
        if num_eligible < base_fanout:
            return num_eligible
        if num_eligible > base_fanout * 3:
            # Dense network, reduce fanout to avoid congestion
            return max(self.config.min_fanout, int(base_fanout * 0.8))

        return base_fanout

    def _is_in_scope(self, message: ARMPMessage) -> bool:
        """Check if message is in our geographic scope"""
        if not message.header.geo_scope:
            return True

        if not self.current_position:
            return True  # Accept all messages if we don't know our position

        # Check distance from message origin
        distance = self._haversine_distance(
            (message.header.geo_scope.latitude, message.header.geo_scope.longitude),
            self.current_position,
        )

        return distance <= message.header.geo_scope.radius_meters

    def _check_rate_limit(self, priority: Priority) -> bool:
        """Check rate limit for priority level"""
        limiter = self.rate_limiters.get(priority)
        if not limiter:
            return True
        return limiter.consume(1)

    def _update_peer_distances(self):
        """Update distances to all peers based on current position"""
        if not self.current_position:
            return

        for peer in self.peers.values():
            if peer.position:
                peer.distance_m = self._haversine_distance(self.current_position, peer.position)

    def _haversine_distance(self, pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
        """Calculate distance between two lat/lon coordinates in meters"""
        lat1, lon1 = pos1
        lat2, lon2 = pos2

        # Radius of Earth in meters
        R = 6371000

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def _clean_message_cache(self, max_age_seconds: int = 60):
        """Remove old messages from cache"""
        now = int(time.time() * 1000)
        to_remove = []

        for msg_hash, message in self.message_cache.items():
            age_ms = now - message.header.timestamp_ms
            if age_ms > max_age_seconds * 1000:
                to_remove.append(msg_hash)

        for msg_hash in to_remove:
            del self.message_cache[msg_hash]

        # Also clean peer message versions
        for peer_id in list(self.peer_message_versions.keys()):
            self.peer_message_versions[peer_id] = {
                h for h in self.peer_message_versions[peer_id] if h in self.message_cache
            }

    def cleanup_stale_peers(self):
        """Remove peers that haven't been seen recently"""
        now = time.time()
        timeout_seconds = self.config.peer_timeout_ms / 1000

        to_remove = []
        for peer_id, peer in self.peers.items():
            if now - peer.last_seen > timeout_seconds:
                to_remove.append(peer_id)

        for peer_id in to_remove:
            self.remove_peer(peer_id)

    def get_stats(self) -> dict:
        """Get protocol statistics"""
        return {
            **self.stats,
            "active_peers": len(self.active_peers),
            "total_peers": len(self.peers),
            "cached_messages": len(self.message_cache),
        }


class AntiEntropySync:
    """Anti-entropy sync for message recovery"""

    def __init__(self, gossip: GossipProtocol):
        self.gossip = gossip

    async def sync_with_peer(self, peer_id: bytes):
        """Perform anti-entropy sync with a peer
        Exchange message digests and request missing messages
        """
        # Get our message hashes
        our_hashes = set(self.gossip.message_cache.keys())

        # Get peer's message hashes (this would come from actual sync protocol)
        peer_hashes = self.gossip.peer_message_versions.get(peer_id, set())

        # Find messages we have that peer doesn't
        to_send = our_hashes - peer_hashes

        # Find messages peer has that we don't
        to_request = peer_hashes - our_hashes

        # Send missing messages
        for msg_hash in to_send:
            message = self.gossip.message_cache.get(msg_hash)
            if message and self.gossip.send_callback:
                await self.gossip.send_callback(peer_id, message)

        return {"sent": len(to_send), "requested": len(to_request)}

    async def periodic_sync(self, interval_seconds: int = 5):
        """Run periodic anti-entropy sync"""
        while True:
            await asyncio.sleep(interval_seconds)

            # Sync with random subset of peers
            if self.gossip.active_peers:
                num_sync = min(3, len(self.gossip.active_peers))
                peers_to_sync = random.sample(list(self.gossip.active_peers), num_sync)

                for peer_id in peers_to_sync:
                    try:
                        await self.sync_with_peer(peer_id)
                    except Exception as e:
                        print(f"Sync error with {peer_id.hex()}: {e}")
