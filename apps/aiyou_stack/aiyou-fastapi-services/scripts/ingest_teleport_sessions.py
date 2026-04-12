"""
ANTIGRAVITY :: GOD MODE :: CORTICAL INGESTION
Classification: TIER 30 SOVEREIGN
Context: 1M+
"""

import json
import os

MANIFEST_PATH = "Docs/TELEPORT_MANIFEST.json"
MEMORY_PATH = "src/governance/memory/learned_rules.json"


def ingest_memories():
    print(">>> 🧠 INITIALIZING CORTICAL STACK INGESTION...")

    if not os.path.exists(MANIFEST_PATH):
        print("❌ Manifest not found. Run Block 2 first.")
        return

    with open(MANIFEST_PATH) as f:
        data = json.load(f)

    judges = data["priorities"]["JUDGE_LEVEL"]
    print(f"    Found {len(judges)} High-Priority Judge Personas.")

    # Simulating extraction for now
    new_rules = [
        {
            "context": "python",
            "file_match": "test",
            "rule": "allow_wildcard_imports",
            "action": "suppress",
            "source": "session_011CUvwBxnYT8QujGMHRutvC",
        },
        {
            "context": "terraform",
            "file_match": "dev",
            "rule": "allow_http_traffic",
            "action": "warn",
            "source": "session_01Fdo7s3HzwmT5BPicwxbQiC",
        },
    ]

    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, "w") as f:
        json.dump(new_rules, f, indent=2)

    print(f">>> ✅ INGESTED {len(new_rules)} RULES. MEMORY ACTIVE.")


if __name__ == "__main__":
    ingest_memories()
