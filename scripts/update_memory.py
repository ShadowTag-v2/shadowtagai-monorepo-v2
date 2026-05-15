import os
import json
from datetime import datetime

# Update CLAUDE.md
claude_path = "CLAUDE.md"
if os.path.exists(claude_path):
  with open(claude_path, "a") as f:
    f.write(
      "\n- [2026-05-13] Thread Update: CounselConduit stateless architecture migrated from Redis to Firestore (Native Mode).\n"
    )

# Update issues.jsonl
beads_path = ".beads/issues.jsonl"
if os.path.exists(beads_path):
  with open(beads_path, "a") as f:
    f.write(
      json.dumps(
        {
          "timestamp": datetime.now().isoformat(),
          "action": "update_architecture",
          "details": "Replaced Redis Memorystore with Firestore Native Mode for CounselConduit cache and state.",
        }
      )
      + "\n"
    )

# Update TASK.md (already done directly, but ensuring it's logged)
print("Updated CLAUDE.md and issues.jsonl with Firestore transition.")
