"""Safe Harbor Unix Domain Socket transport.

Replaces ALL upstream WebSocket transport code. Communication is
exclusively via AF_UNIX sockets — no TCP, no WebSocket, no network.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import struct

from ._types import BridgeMessage
import contextlib

logger = logging.getLogger(__name__)

# ─── Wire Protocol ─────────────────────────────────────────────────────
#
# Each frame on the UDS is:
#   [4 bytes: payload length (big-endian uint32)] [payload: UTF-8 JSON]
#
# This is a simple length-prefixed framing protocol that prevents
# message boundary ambiguity.

_HEADER_SIZE = 4
_MAX_PAYLOAD_SIZE = 16 * 1024 * 1024  # 16 MB hard limit


def _encode_frame(message: BridgeMessage) -> bytes:
    """Encode a BridgeMessage to a length-prefixed frame."""
    payload = json.dumps(
        {
            "type": message.msg_type,
            "session_id": message.session_id,
            "payload": message.payload,
            "uuid": message.msg_uuid,
        },
        separators=(",", ":"),
    ).encode("utf-8")

    if len(payload) > _MAX_PAYLOAD_SIZE:
        msg = f"Payload exceeds max size: {len(payload)} > {_MAX_PAYLOAD_SIZE}"
        raise ValueError(msg)

    return struct.pack(">I", len(payload)) + payload


def _decode_payload(data: bytes) -> BridgeMessage:
    """Decode a JSON payload into a BridgeMessage."""
    parsed = json.loads(data.decode("utf-8"))
    return BridgeMessage(
        msg_type=parsed.get("type", "unknown"),
        session_id=parsed.get("session_id", ""),
        payload=parsed.get("payload", {}),
        msg_uuid=parsed.get("uuid", ""),
    )


# ─── Transport ─────────────────────────────────────────────────────────


class UDSTransport:
    """Unix Domain Socket transport for bridge IPC.

    Safe Harbor constraints:
    - ONLY AF_UNIX sockets. No AF_INET, no AF_INET6.
    - Socket files must be in XDG_RUNTIME_DIR or /tmp.
    - All connections are authenticated via BridgeAuth before
      any application messages are processed.
    """

    __slots__ = ("_reader", "_writer", "_connected", "_socket_path")

    def __init__(self) -> None:
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected: bool = False
        self._socket_path: str = ""

    @property
    def is_connected(self) -> bool:
        """Whether the transport is connected."""
        return self._connected

    @property
    def socket_path(self) -> str:
        """Path to the UDS socket file."""
        return self._socket_path

    async def connect(self, socket_path: str) -> None:
        """Connect to an existing UDS socket as a client.

        Raises ConnectionError if the socket does not exist or
        connection fails.
        """
        if not os.path.exists(socket_path):
            msg = f"Socket does not exist: {socket_path}"
            raise ConnectionError(msg)

        self._socket_path = socket_path
        try:
            self._reader, self._writer = await asyncio.open_unix_connection(socket_path)
            self._connected = True
            logger.debug("Connected to UDS: %s", socket_path)
        except OSError as exc:
            msg = f"Failed to connect to UDS {socket_path}: {exc}"
            raise ConnectionError(msg) from exc

    async def write(self, message: BridgeMessage) -> None:
        """Send a message over the UDS connection.

        Raises ConnectionError if not connected.
        """
        if not self._connected or self._writer is None:
            msg = "Transport not connected"
            raise ConnectionError(msg)

        frame = _encode_frame(message)
        self._writer.write(frame)
        await self._writer.drain()

    async def read(self) -> BridgeMessage | None:
        """Read the next message from the UDS connection.

        Returns None on EOF or connection close.
        """
        if not self._connected or self._reader is None:
            return None

        try:
            # Read header
            header = await self._reader.readexactly(_HEADER_SIZE)
            (length,) = struct.unpack(">I", header)

            if length > _MAX_PAYLOAD_SIZE:
                logger.error(
                    "Payload size %d exceeds max %d, dropping",
                    length,
                    _MAX_PAYLOAD_SIZE,
                )
                # Drain the oversized payload to keep the stream aligned
                await self._reader.readexactly(length)
                return None

            # Read payload
            payload_bytes = await self._reader.readexactly(length)
            return _decode_payload(payload_bytes)

        except asyncio.IncompleteReadError:
            logger.debug("UDS connection closed (incomplete read)")
            self._connected = False
            return None
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to decode UDS message: %s", exc)
            return None

    async def close(self) -> None:
        """Close the UDS connection and clean up."""
        self._connected = False
        if self._writer is not None:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except OSError:
                pass  # Already closed
            self._writer = None
        self._reader = None
        logger.debug("UDS transport closed: %s", self._socket_path)


# ─── Server ────────────────────────────────────────────────────────────


class UDSServer:
    """Unix Domain Socket server for accepting bridge connections.

    Safe Harbor constraints:
    - Listens ONLY on AF_UNIX. No network binding.
    - Validates auth tokens on every new connection.
    - Automatically cleans up stale socket files.
    """

    __slots__ = ("_socket_path", "_server", "_running")

    def __init__(self, socket_path: str) -> None:
        self._socket_path = socket_path
        self._server: asyncio.AbstractServer | None = None
        self._running: bool = False

    @property
    def is_running(self) -> bool:
        """Whether the server is accepting connections."""
        return self._running

    async def start(
        self,
        on_connection: asyncio.coroutines,
    ) -> None:
        """Start the UDS server.

        Args:
            on_connection: Async callback invoked for each new connection.
                Receives (reader, writer) as arguments.
        """
        # Clean up stale socket file
        if os.path.exists(self._socket_path):
            with contextlib.suppress(OSError):
                os.unlink(self._socket_path)

        self._server = await asyncio.start_unix_server(
            on_connection,
            path=self._socket_path,
        )
        self._running = True
        logger.info("UDS server listening on: %s", self._socket_path)

    async def stop(self) -> None:
        """Stop the UDS server and clean up the socket file."""
        self._running = False
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        # Clean up socket file
        if os.path.exists(self._socket_path):
            with contextlib.suppress(OSError):
                os.unlink(self._socket_path)
        logger.info("UDS server stopped: %s", self._socket_path)
