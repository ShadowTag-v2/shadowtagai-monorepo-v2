# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import datetime
import json
import os
import uuid

BEADS_FILE = ".beads/issues.jsonl"


class BeadsEngine:
    """The Persistent Work Queue."""

    def __init__(self):
        os.makedirs(os.path.dirname(BEADS_FILE), exist_ok=True)

    def log(self, content: str, tag: str = "TASK"):
        entry = {
            "id": uuid.uuid4().hex[:6],
            "timestamp": datetime.datetime.now().isoformat(),
            "tag": tag,
            "content": content,
            "status": "open",
        }
        with open(BEADS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return f"✅ Bead Added: [{tag}] {content}"

    def recall(self) -> str:
        if not os.path.exists(BEADS_FILE):
            return "Memory Empty."
        with open(BEADS_FILE) as f:
            lines = f.readlines()
        return "\n".join([json.loads(line)["content"] for line in lines[-5:]])
