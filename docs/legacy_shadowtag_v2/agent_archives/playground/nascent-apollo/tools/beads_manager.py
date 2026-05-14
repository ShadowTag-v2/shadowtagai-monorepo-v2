# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import os
from datetime import datetime, timezone

# --- V5 HIPPOCAMPUS: THE BEADS ENGINE ---
# Purpose: Long-Term Memory & Decision Logging.
# Format: JSONL (Append-Only Log)

BEADS_FILE = ".beads/issues.jsonl"


class BeadsEngine:
    def __init__(self):
        self.ensure_memory_exists()

    def ensure_memory_exists(self):
        if not os.path.exists(".beads"):
            os.makedirs(".beads")
        if not os.path.exists(BEADS_FILE):
            with open(BEADS_FILE, "w") as f:
                f.write("")  # Touch file

    def remember(self, action: str, details: str):
        """
        Logs an action to the infinite tape.
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "details": details,
            "agent_version": "Omega-V5",
        }
        with open(BEADS_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
        print(f"📿 BEADS: Remembered -> {action}")

    def recall(self) -> list:
        """
        Retrieves full history.
        """
        history = []
        if os.path.exists(BEADS_FILE):
            with open(BEADS_FILE) as f:
                for line in f:
                    if line.strip():
                        history.append(json.loads(line))
        print(f"🧠 RECALL: {len(history)} memories loaded.")
        return history


if __name__ == "__main__":
    # CLI Entrypoint for 'python3 tools/beads_manager.py'
    engine = BeadsEngine()
    engine.recall()
