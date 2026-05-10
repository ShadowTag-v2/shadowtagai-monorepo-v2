# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Teammate Mailbox — P1 #10. Inter-agent async message passing for swarm coordination."""

from __future__ import annotations
import json, logging, os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger("agnt.teammate_mailbox")
MAILBOX_DIR = Path(os.environ.get("REPO_ROOT", os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball"))) / ".beads" / "mailbox"


@dataclass
class Message:
    sender: str
    recipient: str
    subject: str
    body: str
    priority: int = 0
    created_at: str = ""
    read: bool = False
    msg_id: str = ""


class TeammateMailbox:
    """Async message passing between agents (P1 #10).
    Enables Jules, GCA, KAIROS, Loop Steward, and Dream Consolidation
    to coordinate without shared state. File-backed for durability.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._inbox = MAILBOX_DIR / agent_name / "inbox"
        self._outbox = MAILBOX_DIR / agent_name / "outbox"
        self._inbox.mkdir(parents=True, exist_ok=True)
        self._outbox.mkdir(parents=True, exist_ok=True)

    def send(self, recipient: str, subject: str, body: str, priority: int = 0) -> str:
        ts = datetime.now(UTC).isoformat()
        msg_id = f"{self.agent_name}_{int(datetime.now(UTC).timestamp() * 1000)}"
        msg = {
            "sender": self.agent_name,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "priority": priority,
            "created_at": ts,
            "read": False,
            "msg_id": msg_id,
        }
        # Write to recipient's inbox
        recv_inbox = MAILBOX_DIR / recipient / "inbox"
        recv_inbox.mkdir(parents=True, exist_ok=True)
        (recv_inbox / f"{msg_id}.json").write_text(json.dumps(msg, indent=2))
        # Copy to sender's outbox
        (self._outbox / f"{msg_id}.json").write_text(json.dumps(msg, indent=2))
        return msg_id

    def receive(self, mark_read: bool = True) -> list[Message]:
        msgs = []
        for f in sorted(self._inbox.glob("*.json"), key=lambda p: p.stat().st_mtime):
            try:
                data = json.loads(f.read_text())
                if data.get("read"):
                    continue
                msg = Message(**{k: data[k] for k in Message.__dataclass_fields__ if k in data})
                msgs.append(msg)
                if mark_read:
                    data["read"] = True
                    f.write_text(json.dumps(data, indent=2))
            except json.JSONDecodeError, KeyError, OSError:
                continue
        return sorted(msgs, key=lambda m: m.priority, reverse=True)

    def broadcast(self, agents: list[str], subject: str, body: str, priority: int = 0) -> list[str]:
        return [self.send(a, subject, body, priority) for a in agents if a != self.agent_name]

    def unread_count(self) -> int:
        count = 0
        for f in self._inbox.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                if not data.get("read"):
                    count += 1
            except json.JSONDecodeError, OSError:
                continue
        return count
