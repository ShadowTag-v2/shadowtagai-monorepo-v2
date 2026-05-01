#!/usr/bin/env python3
"""
AGNT RPC Bus — Ported from Claude Code's bridge/ architecture

Grounded in:
  - Claude_Source_Code/bridge/bridgeMain.ts (115K, core RPC bus)
  - Claude_Source_Code/bridge/bridgeMessaging.ts (15K, message routing)
  - Claude_Source_Code/bridge/bridgeApi.ts (18K, API surface)
  - Claude_Source_Code/bridge/capacityWake.ts (1841B, wake primitives)
  - Claude_Source_Code/bridge/replBridge.ts (100K, REPL bridge)
  - Claude_Source_Code/bridge/types.ts (10K, type definitions)

Architecture:
  SQLite-backed JSON-RPC bus for inter-daemon communication. Each daemon
  (KAIROS, Loop Steward, YOLO Classifier, etc.) registers as a service
  and can send/receive structured messages through the bus.

  This replaces ad-hoc file-based IPC with a proper message bus modeled
  after Claude Code's bridge architecture, specifically:
    - bridgeMain.ts: session lifecycle, poll loops, capacity management
    - bridgeMessaging.ts: message serialization and delivery
    - capacityWake.ts: wake-on-capacity primitive for idle daemons
    - bridgeApi.ts: RPC method registry and dispatch

Usage:
  python scripts/agnt_rpc_bus.py --start           # Start the bus
  python scripts/agnt_rpc_bus.py --send '{"method":"ping"}'  # Send a message
  python scripts/agnt_rpc_bus.py --status           # Show bus status

Integration:
  All daemons import RPCClient from this module to communicate.
  Bus state is persisted in .beads/rpc_bus.db (SQLite).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from collections.abc import Callable

# ── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BEADS_DIR = PROJECT_ROOT / ".beads"
DB_PATH = BEADS_DIR / "rpc_bus.db"

# From capacityWake.ts: wake intervals
POLL_INTERVAL_MS = 500
CAPACITY_WAKE_INTERVAL_MS = 100

# Message TTL (seconds)
MESSAGE_TTL = 3600  # 1 hour
CLEANUP_INTERVAL = 300  # 5 minutes


# ── Types (from bridge/types.ts) ────────────────────────────────────────


@dataclass
class RPCMessage:
    """
    JSON-RPC 2.0 message, modeled after bridge/types.ts.

    Maps to Claude Code's bridge message format:
      - bridgeMessaging.ts handles serialization
      - bridgeApi.ts handles dispatch
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: str = ""
    params: dict = field(default_factory=dict)
    result: Any | None = None
    error: str | None = None
    source: str = ""  # Sending daemon name
    target: str = ""  # Target daemon (empty = broadcast)
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"  # pending, delivered, processed, expired

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.params,
            "result": self.result,
            "error": self.error,
            "source": self.source,
            "target": self.target,
            "timestamp": self.timestamp,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict) -> RPCMessage:
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            method=d.get("method", ""),
            params=d.get("params", {}),
            result=d.get("result"),
            error=d.get("error"),
            source=d.get("source", ""),
            target=d.get("target", ""),
            timestamp=d.get("timestamp", time.time()),
            status=d.get("status", "pending"),
        )


@dataclass
class ServiceRegistration:
    """Registered daemon service, modeled after bridge/bridgeMain.ts session registry."""

    name: str
    pid: int
    registered_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    methods: list[str] = field(default_factory=list)
    status: str = "active"  # active, idle, dead

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "pid": self.pid,
            "registered_at": self.registered_at,
            "last_heartbeat": self.last_heartbeat,
            "methods": self.methods,
            "status": self.status,
            "age_seconds": time.time() - self.registered_at,
        }


# ── SQLite Storage Layer ─────────────────────────────────────────────────


class RPCStorage:
    """
    SQLite-backed message store.

    Maps to Claude Code's sessionStorage.ts (180K!) pattern for persisting
    messages and state across process restarts. Uses WAL mode for concurrent
    daemon access.
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    method TEXT NOT NULL,
                    params TEXT DEFAULT '{}',
                    result TEXT,
                    error TEXT,
                    source TEXT NOT NULL,
                    target TEXT DEFAULT '',
                    timestamp REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                );

                CREATE TABLE IF NOT EXISTS services (
                    name TEXT PRIMARY KEY,
                    pid INTEGER NOT NULL,
                    registered_at REAL NOT NULL,
                    last_heartbeat REAL NOT NULL,
                    methods TEXT DEFAULT '[]',
                    status TEXT DEFAULT 'active'
                );

                CREATE INDEX IF NOT EXISTS idx_messages_target
                    ON messages(target, status);
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp
                    ON messages(timestamp);
                CREATE INDEX IF NOT EXISTS idx_services_status
                    ON services(status);
            """)

    @contextmanager
    def _connect(self):
        """Thread-safe connection context manager."""
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def enqueue(self, msg: RPCMessage) -> None:
        """Enqueue a message for delivery."""
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO messages (id, method, params, source, target, timestamp, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (msg.id, msg.method, json.dumps(msg.params), msg.source, msg.target, msg.timestamp, msg.status),
            )

    def dequeue(self, target: str, limit: int = 10) -> list[RPCMessage]:
        """Dequeue pending messages for a target service."""
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT * FROM messages
                   WHERE (target = ? OR target = '') AND status = 'pending'
                   ORDER BY timestamp ASC LIMIT ?""",
                (target, limit),
            ).fetchall()

            messages = []
            for row in rows:
                msg = RPCMessage(
                    id=row["id"],
                    method=row["method"],
                    params=json.loads(row["params"] or "{}"),
                    source=row["source"],
                    target=row["target"],
                    timestamp=row["timestamp"],
                    status="delivered",
                )
                messages.append(msg)
                # Mark as delivered
                conn.execute(
                    "UPDATE messages SET status = 'delivered' WHERE id = ?",
                    (msg.id,),
                )

            return messages

    def complete(self, msg_id: str, result: Any = None, error: str = None) -> None:
        """Mark a message as processed."""
        with self._connect() as conn:
            conn.execute(
                """UPDATE messages SET status = 'processed', result = ?, error = ?
                   WHERE id = ?""",
                (json.dumps(result) if result else None, error, msg_id),
            )

    def register_service(self, reg: ServiceRegistration) -> None:
        """Register or update a daemon service."""
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO services (name, pid, registered_at, last_heartbeat, methods, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (reg.name, reg.pid, reg.registered_at, reg.last_heartbeat, json.dumps(reg.methods), reg.status),
            )

    def heartbeat(self, name: str) -> None:
        """Update service heartbeat."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE services SET last_heartbeat = ?, status = 'active' WHERE name = ?",
                (time.time(), name),
            )

    def get_services(self) -> list[ServiceRegistration]:
        """Get all registered services."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM services ORDER BY name").fetchall()
            return [
                ServiceRegistration(
                    name=row["name"],
                    pid=row["pid"],
                    registered_at=row["registered_at"],
                    last_heartbeat=row["last_heartbeat"],
                    methods=json.loads(row["methods"] or "[]"),
                    status=row["status"],
                )
                for row in rows
            ]

    def cleanup_expired(self) -> int:
        """Remove expired messages and mark dead services."""
        cutoff = time.time() - MESSAGE_TTL
        dead_cutoff = time.time() - 60  # 60s without heartbeat = dead
        with self._connect() as conn:
            result = conn.execute(
                "DELETE FROM messages WHERE timestamp < ? AND status != 'processed'",
                (cutoff,),
            )
            conn.execute(
                "UPDATE services SET status = 'dead' WHERE last_heartbeat < ?",
                (dead_cutoff,),
            )
            return result.rowcount

    def get_stats(self) -> dict:
        """Get bus statistics."""
        with self._connect() as conn:
            msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            pending = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'pending'").fetchone()[0]
            services = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM services WHERE status = 'active'").fetchone()[0]
            return {
                "total_messages": msg_count,
                "pending_messages": pending,
                "total_services": services,
                "active_services": active,
                "db_size_kb": self.db_path.stat().st_size / 1024 if self.db_path.exists() else 0,
            }


# ── RPC Client (for daemons to import) ───────────────────────────────────


class RPCClient:
    """
    Client for daemons to communicate via the RPC bus.

    Maps to Claude Code's bridgeApi.ts API surface:
      - send(): enqueue message (bridgeMessaging.ts)
      - receive(): poll for messages (replBridge.ts poll loop)
      - register(): register service (bridgeMain.ts session registration)
      - heartbeat(): keep-alive (capacityWake.ts wake primitive)

    Usage from daemons:
        from scripts.agnt_rpc_bus import RPCClient

        client = RPCClient("kairos_daemon")
        client.register(methods=["execute_task", "heartbeat"])
        client.send("yolo_classifier", "classify", {"command": "rm -rf /"})
        messages = client.receive()
    """

    def __init__(self, service_name: str, db_path: Path = DB_PATH) -> None:
        self.service_name = service_name
        self.storage = RPCStorage(db_path)
        self._handlers: dict[str, Callable] = {}

    def register(self, methods: list[str] = None) -> None:
        """Register this daemon as a service on the bus."""
        reg = ServiceRegistration(
            name=self.service_name,
            pid=os.getpid(),
            methods=methods or [],
        )
        self.storage.register_service(reg)

    def heartbeat(self) -> None:
        """Send heartbeat to indicate this service is alive."""
        self.storage.heartbeat(self.service_name)

    def send(
        self,
        target: str,
        method: str,
        params: dict = None,
    ) -> str:
        """Send a message to a target service. Returns message ID."""
        msg = RPCMessage(
            method=method,
            params=params or {},
            source=self.service_name,
            target=target,
        )
        self.storage.enqueue(msg)
        return msg.id

    def broadcast(self, method: str, params: dict = None) -> str:
        """Broadcast a message to all services."""
        msg = RPCMessage(
            method=method,
            params=params or {},
            source=self.service_name,
            target="",  # empty = broadcast
        )
        self.storage.enqueue(msg)
        return msg.id

    def receive(self, limit: int = 10) -> list[RPCMessage]:
        """Poll for pending messages addressed to this service."""
        return self.storage.dequeue(self.service_name, limit)

    def complete(self, msg_id: str, result: Any = None, error: str = None) -> None:
        """Mark a message as processed with optional result/error."""
        self.storage.complete(msg_id, result, error)

    def on(self, method: str, handler: Callable) -> None:
        """Register a handler for a specific method."""
        self._handlers[method] = handler

    def process_pending(self) -> int:
        """Process all pending messages using registered handlers."""
        messages = self.receive()
        processed = 0
        for msg in messages:
            handler = self._handlers.get(msg.method)
            if handler:
                try:
                    result = handler(msg.params)
                    self.complete(msg.id, result=result)
                    processed += 1
                except Exception as e:
                    self.complete(msg.id, error=str(e))
            else:
                self.complete(msg.id, error=f"No handler for method: {msg.method}")
        return processed


# ── Bus Server ───────────────────────────────────────────────────────────


class RPCBusServer:
    """
    Main bus server process.

    Maps to Claude Code's bridgeMain.ts main loop:
      - Poll for capacity (capacityWake.ts)
      - Process incoming messages
      - Clean up expired messages
      - Monitor service health
    """

    def __init__(self) -> None:
        self.storage = RPCStorage()
        self.logger = logging.getLogger("rpc_bus")
        self._running = False

    def start(self) -> None:
        """Start the bus server (blocking)."""
        self._running = True
        self.logger.info("RPC Bus starting (PID %d, DB: %s)", os.getpid(), DB_PATH)

        # Register ourselves
        self.storage.register_service(
            ServiceRegistration(
                name="rpc_bus",
                pid=os.getpid(),
                methods=["ping", "status", "cleanup"],
            )
        )

        last_cleanup = time.time()

        try:
            while self._running:
                # Heartbeat
                self.storage.heartbeat("rpc_bus")

                # Process internal messages
                messages = self.storage.dequeue("rpc_bus", limit=50)
                for msg in messages:
                    self._handle_internal(msg)

                # Periodic cleanup
                if time.time() - last_cleanup > CLEANUP_INTERVAL:
                    removed = self.storage.cleanup_expired()
                    if removed > 0:
                        self.logger.info("Cleaned up %d expired messages", removed)
                    last_cleanup = time.time()

                time.sleep(POLL_INTERVAL_MS / 1000)

        except KeyboardInterrupt:
            self.logger.info("RPC Bus shutting down")
        finally:
            self._running = False

    def stop(self) -> None:
        """Signal the bus to stop."""
        self._running = False

    def _handle_internal(self, msg: RPCMessage) -> None:
        """Handle internal bus messages."""
        if msg.method == "ping":
            self.storage.complete(msg.id, result={"pong": True, "timestamp": time.time()})
        elif msg.method == "status":
            self.storage.complete(msg.id, result=self.storage.get_stats())
        elif msg.method == "cleanup":
            removed = self.storage.cleanup_expired()
            self.storage.complete(msg.id, result={"removed": removed})
        else:
            self.storage.complete(msg.id, error=f"Unknown method: {msg.method}")


# ── Output Formatters ────────────────────────────────────────────────────


def format_status(storage: RPCStorage) -> str:
    """Format bus status for human consumption."""
    stats = storage.get_stats()
    services = storage.get_services()

    lines = []
    lines.append("═══ AGNT RPC Bus Status ═══")
    lines.append(f"  DB: {DB_PATH} ({stats['db_size_kb']:.1f} KB)")
    lines.append(f"  Messages: {stats['total_messages']} total, {stats['pending_messages']} pending")
    lines.append(f"  Services: {stats['active_services']}/{stats['total_services']} active")
    lines.append("")

    if services:
        lines.append("  | Service              | PID    | Status | Last Heartbeat       | Methods |")
        lines.append("  |----------------------|--------|--------|----------------------|---------|")
        for svc in services:
            hb_time = time.strftime("%H:%M:%S", time.localtime(svc.last_heartbeat))
            status_emoji = {"active": "🟢", "idle": "🟡", "dead": "🔴"}.get(svc.status, "?")
            methods_str = str(len(svc.methods))
            lines.append(f"  | {svc.name:<20s} | {svc.pid:<6d} | {status_emoji}     | {hb_time:<20s} | {methods_str:<7s} |")
    else:
        lines.append("  No services registered")

    return "\n".join(lines)


# ── CLI Entry Point ──────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="AGNT RPC Bus (ported from Claude Code bridge/ architecture)")
    parser.add_argument("--start", action="store_true", help="Start the bus server")
    parser.add_argument("--status", action="store_true", help="Show bus status")
    parser.add_argument("--send", type=str, help="Send a JSON-RPC message")
    parser.add_argument("--cleanup", action="store_true", help="Clean up expired messages")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--init", action="store_true", help="Initialize the database")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    storage = RPCStorage()

    if args.start:
        server = RPCBusServer()
        server.start()
    elif args.status:
        if args.json:
            print(json.dumps(storage.get_stats(), indent=2))
        else:
            print(format_status(storage))
    elif args.send:
        try:
            data = json.loads(args.send)
            msg = RPCMessage.from_dict(data)
            msg.source = msg.source or "cli"
            storage.enqueue(msg)
            print(f"Message enqueued: {msg.id}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.cleanup:
        removed = storage.cleanup_expired()
        print(f"Cleaned up {removed} expired messages")
    elif args.init:
        print(f"Database initialized at {DB_PATH}")
        print(json.dumps(storage.get_stats(), indent=2))
    else:
        # Default: show status
        print(format_status(storage))


if __name__ == "__main__":
    main()
