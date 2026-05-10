"""agnt_bridge — Safe Harbor Local IPC Bridge.

Authenticated Unix Domain Socket transport for IDE ↔ agent
communication. Replaces all upstream WebSocket/OAuth patterns
with HMAC-SHA256 local auth and AF_UNIX sockets.

Zero network egress. Zero remote telemetry.
"""

from .auth import AuthToken, BridgeAuth
from .bounded_set import BoundedUUIDSet
from .flush_gate import FlushGate
from .gate import get_bridge_disabled_reason, is_bridge_enabled
from .transport import UDSServer, UDSTransport

__all__ = [
  "AuthToken",
  "BridgeAuth",
  "BoundedUUIDSet",
  "FlushGate",
  "UDSServer",
  "UDSTransport",
  "get_bridge_disabled_reason",
  "is_bridge_enabled",
]
