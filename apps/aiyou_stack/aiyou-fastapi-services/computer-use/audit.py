"""Computer-Use Agent Audit Logging

Logs all agent actions to JSONL for compliance and debugging.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(os.environ.get("CU_AUDIT", ".ci/computer_use_audit.jsonl"))
AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)


def log(event: str, **kw: dict[str, Any]) -> None:
    """Log an event to the audit trail.

    Args:
        event: Event type (e.g., "start", "action", "blocked", "done")
        **kw: Additional key-value pairs to log

    """
    rec = {
        "ts": int(time.time()),
        "iso_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        **kw,
    }

    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def get_audit_log() -> list[dict]:
    """Read the entire audit log.

    Returns:
        List of audit records (parsed JSON objects)

    """
    if not AUDIT_PATH.exists():
        return []

    records = []
    with AUDIT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # Skip malformed lines

    return records
