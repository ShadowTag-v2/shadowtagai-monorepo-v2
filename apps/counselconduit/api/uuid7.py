# apps/counselconduit/api/uuid7.py
"""UUIDv7 Generator — Voice AI IDOR Defense.

UUIDv7 provides:
- Time-ordered (sortable without separate timestamp column)
- Cryptographically random suffix (no sequential guessing)
- Standard UUID format (drop-in replacement for UUIDv4)

This replaces sequential integer IDs throughout the system to prevent
Insecure Direct Object Reference (IDOR) attacks.
"""

from __future__ import annotations

import os
import struct
import time
import uuid


def uuid7() -> uuid.UUID:
    """Generate a UUIDv7 (RFC 9562).

    Format: unix_ts_ms (48 bits) | ver (4 bits) | rand_a (12 bits) |
            var (2 bits) | rand_b (62 bits)

    Returns:
        A new UUIDv7 instance, time-ordered and cryptographically random.
    """
    # Current Unix timestamp in milliseconds
    timestamp_ms = int(time.time() * 1000)

    # 48-bit timestamp
    ts_bytes = struct.pack(">Q", timestamp_ms)[-6:]  # last 6 bytes = 48 bits

    # 10 random bytes for rand_a (12 bits) + rand_b (62 bits)
    rand_bytes = os.urandom(10)

    # Assemble 16 bytes
    uuid_bytes = bytearray(ts_bytes + rand_bytes)

    # Set version 7 (bits 48-51)
    uuid_bytes[6] = (uuid_bytes[6] & 0x0F) | 0x70

    # Set variant 10 (bits 64-65)
    uuid_bytes[8] = (uuid_bytes[8] & 0x3F) | 0x80

    return uuid.UUID(bytes=bytes(uuid_bytes))


def uuid7_str() -> str:
    """Generate a UUIDv7 as a string."""
    return str(uuid7())


# ── Pydantic Integration ──────────────────────────────────────────────────

def new_entity_id() -> str:
    """Generate a new entity ID. Use this for ALL new records.

    Usage in Pydantic models:
        class Attorney(BaseModel):
            id: str = Field(default_factory=new_entity_id)
            firm_id: str = Field(default_factory=new_entity_id)
    """
    return uuid7_str()
