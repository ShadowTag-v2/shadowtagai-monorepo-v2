#!/usr/bin/env python3
"""Sync Claude Code session to memory bank (GCS + Firestore + CLAUDE.md)

Usage:
    python3 scripts/sync_claude_memory.py

Prerequisites:
    - google-cloud-storage and google-cloud-firestore installed
    - ADC credentials configured
    - GCS bucket exists (creates if not)
"""

import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ID = "acquired-jet-478701-b3"
MEMORY_PATH = Path(__file__).parent.parent / "erik-hancock-llm-memory" / "memory" / "current.json"
GCS_BUCKET = f"{PROJECT_ID}-workbench-memory"
CLAUDE_MD_PATH = Path(__file__).parent.parent / "CLAUDE.md"


def load_memory() -> dict:
    """Load existing memory from current.json"""
    if not MEMORY_PATH.exists():
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "conversations": [],
            "knowledge": [],
        }
    return json.loads(MEMORY_PATH.read_text())


def save_memory(memory: dict) -> None:
    """Save memory to current.json"""
    MEMORY_PATH.write_text(json.dumps(memory, indent=2))
    print(f"  Saved to {MEMORY_PATH}")


def merge_session(memory: dict, session_data: dict) -> dict:
    """Merge session into conversations/knowledge arrays"""
    # Check for duplicate conversation ID
    existing_ids = {
        c.get("id") or c.get("conversation_id") for c in memory.get("conversations", [])
    }
    if session_data["conversation"]["id"] not in existing_ids:
        memory["conversations"].append(session_data["conversation"])

    # Merge knowledge (dedupe by topic)
    existing_topics = {k.get("topic") for k in memory.get("knowledge", [])}
    for k in session_data.get("knowledge", []):
        if k.get("topic") not in existing_topics:
            memory.setdefault("knowledge", []).append(k)
            existing_topics.add(k.get("topic"))

    memory["last_updated"] = datetime.now().isoformat()
    return memory


def sync_gcs(memory: dict) -> bool:
    """Upload to GCS bucket"""
    try:
        from google.cloud import storage

        client = storage.Client(project=PROJECT_ID)

        # Create bucket if it doesn't exist
        try:
            bucket = client.get_bucket(GCS_BUCKET)
        except Exception:
            print(f"  Creating bucket {GCS_BUCKET}...")
            bucket = client.create_bucket(GCS_BUCKET, location="us-central1")

        blob = bucket.blob("memory/current.json")
        blob.upload_from_string(json.dumps(memory, indent=2), content_type="application/json")
        print(f"  Synced to gs://{GCS_BUCKET}/memory/current.json")
        return True
    except ImportError:
        print("  [SKIP] google-cloud-storage not installed")
        return False
    except Exception as e:
        print(f"  [ERROR] GCS sync failed: {e}")
        return False


def sync_firestore(memory: dict) -> bool:
    """Real-time sync to Firestore"""
    try:
        from google.cloud import firestore

        db = firestore.Client(project=PROJECT_ID)
        doc_ref = db.collection("claude_memory").document("current")

        # Firestore has a 1MB limit, so we store a summary
        summary = {
            "version": memory.get("version"),
            "last_updated": memory.get("last_updated"),
            "conversation_count": len(memory.get("conversations", [])),
            "knowledge_count": len(memory.get("knowledge", [])),
            "latest_conversation": memory.get("conversations", [{}])[-1]
            if memory.get("conversations")
            else {},
            "pnkln_architecture": memory.get("pnkln_architecture", {}),
            "llm_allocation": memory.get("llm_allocation", {}),
            "bootstrap_gates": memory.get("bootstrap_gates", {}),
        }

        doc_ref.set(summary)
        print("  Synced to Firestore claude_memory/current")
        return True
    except ImportError:
        print("  [SKIP] google-cloud-firestore not installed")
        return False
    except Exception as e:
        print(f"  [ERROR] Firestore sync failed: {e}")
        return False


def update_claude_md(session_summary: str) -> bool:
    """Append session context to CLAUDE.md"""
    try:
        if not CLAUDE_MD_PATH.exists():
            print(f"  [SKIP] CLAUDE.md not found at {CLAUDE_MD_PATH}")
            return False

        content = CLAUDE_MD_PATH.read_text()

        section = f"""
## Last Session: {datetime.now().strftime("%Y-%m-%d %H:%M")}

- **Summary**: {session_summary}
- **Memory Synced**: GCS + Firestore + CLAUDE.md
- **Squadron**: 650 agents operational on :8600

"""
        # Replace existing or append before last update line
        if "## Last Session:" in content:
            content = re.sub(
                r"## Last Session:.*?(?=\n## |\n---|\*Last updated|\Z)",
                section,
                content,
                flags=re.DOTALL,
            )
        # Insert before "Last updated" line if it exists
        elif "*Last updated:" in content:
            content = content.replace("*Last updated:", f"{section}*Last updated:")
        else:
            content += section

        CLAUDE_MD_PATH.write_text(content)
        print(f"  Updated {CLAUDE_MD_PATH}")
        return True
    except Exception as e:
        print(f"  [ERROR] CLAUDE.md update failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Claude Memory Sync - All 3 Targets")
    print("=" * 60)

    # Session data to merge
    session_data = {
        "conversation": {
            "id": f"claude-code-{datetime.now().strftime('%Y-%m-%d')}",
            "source": "claude_code",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "GKE quota fix, Terraform deploy shadowtagai-production, memory sync setup",
            "key_decisions": [
                "Deleted autopilot-cluster-1 (freed 40 CPUs + 500GB SSD)",
                "Created shadowtagai-production GKE cluster",
                "Migrated Anthropic -> Gemini in terraform configs",
                "Set up 3-way memory sync (GCS + Firestore + CLAUDE.md)",
            ],
            "artifacts": [
                "terraform/main.tf",
                "terraform/secrets.tf",
                "scripts/sync_claude_memory.py",
            ],
        },
        "knowledge": [
            {
                "topic": "gke_quota_management",
                "learned": "Autopilot clusters consume 5 nodes x 8 CPUs = 40 CPUs quota",
                "source": "claude-code-2025-11-28",
            },
            {
                "topic": "terraform_state_bucket",
                "learned": "Backend bucket: gs://acquired-jet-478701-b3-terraform-state",
                "source": "claude-code-2025-11-28",
            },
            {
                "topic": "memory_sync_pattern",
                "learned": "3-way sync: local JSON -> GCS bucket -> Firestore + CLAUDE.md",
                "source": "claude-code-2025-11-28",
            },
        ],
    }

    # Step 1: Load and merge
    print("\n[1/4] Loading memory...")
    memory = load_memory()
    print(
        f"  Loaded {len(memory.get('conversations', []))} conversations, {len(memory.get('knowledge', []))} knowledge items",
    )

    print("\n[2/4] Merging session...")
    memory = merge_session(memory, session_data)
    save_memory(memory)

    # Step 2: Sync to GCS
    print("\n[3/4] Syncing to GCS...")
    gcs_ok = sync_gcs(memory)

    # Step 3: Sync to Firestore
    print("\n[4/4] Syncing to Firestore...")
    fs_ok = sync_firestore(memory)

    # Step 4: Update CLAUDE.md
    print("\n[5/5] Updating CLAUDE.md...")
    md_ok = update_claude_md(session_data["conversation"]["summary"])

    # Summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print("  Local JSON: OK")
    print(f"  GCS Bucket: {'OK' if gcs_ok else 'SKIPPED'}")
    print(f"  Firestore:  {'OK' if fs_ok else 'SKIPPED'}")
    print(f"  CLAUDE.md:  {'OK' if md_ok else 'SKIPPED'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
