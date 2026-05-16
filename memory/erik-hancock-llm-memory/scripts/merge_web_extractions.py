#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Merge Web Extractions with 0xSero Local Data

Takes JSON files from extract_claude_web.js and merges them with
existing 0xSero extracted conversations from local databases.

USAGE:
    python scripts/merge_web_extractions.py

This will:
1. Find all claude_web_extraction_*.json files in extractions/
2. Parse and normalize the data
3. Merge with existing memory/current.json
4. Generate updated memory snapshot
5. Update Gemini metadata for new conversations
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

EXTRACTIONS_DIR = Path(__file__).parent.parent / "extractions"
MEMORY_DIR = Path(__file__).parent.parent / "memory"
CURRENT_MEMORY = MEMORY_DIR / "current.json"


def load_web_extractions() -> list[dict]:
  """Load all web extraction JSON files."""
  print("🔍 Scanning for web extraction files...")

  if not EXTRACTIONS_DIR.exists():
    EXTRACTIONS_DIR.mkdir(parents=True)
    print(f"   Created {EXTRACTIONS_DIR}")
    return []

  extraction_files = list(EXTRACTIONS_DIR.glob("claude_web_extraction_*.json"))
  print(f"   Found {len(extraction_files)} extraction files")

  extractions = []
  for file_path in extraction_files:
    try:
      with open(file_path) as f:
        data = json.load(f)
        extractions.append({"file": file_path.name, "data": data})
      print(f"   ✓ Loaded {file_path.name}")
    except Exception as e:
      print(f"   ✗ Error loading {file_path.name}: {e}")

  return extractions


def parse_web_conversations(extractions: list[dict]) -> list[dict]:
  """Parse web extractions and normalize to conversation schema."""
  print("\n📋 Parsing web conversations...")

  conversations = []

  for extraction in extractions:
    data = extraction["data"]
    platform = data["metadata"]["platform"]

    print(f"\n   Processing {extraction['file']} ({platform})...")

    # Try to extract from multiple sources
    sources = data["sources"]

    # 1. Try API data first (most structured)
    if sources.get("api", {}).get("conversations"):
      api_convos = parse_api_conversations(sources["api"]["conversations"], platform)
      conversations.extend(api_convos)
      print(f"      ✓ API: {len(api_convos)} conversations")

    # 2. Try IndexedDB
    if sources.get("indexedDB", {}).get("data"):
      idb_convos = parse_indexeddb_conversations(sources["indexedDB"]["data"], platform)
      conversations.extend(idb_convos)
      print(f"      ✓ IndexedDB: {len(idb_convos)} conversations")

    # 3. Try localStorage
    if sources.get("localStorage", {}).get("data"):
      ls_convos = parse_localstorage_conversations(
        sources["localStorage"]["data"], platform
      )
      conversations.extend(ls_convos)
      print(f"      ✓ localStorage: {len(ls_convos)} conversations")

    # 4. DOM as last resort (least structured)
    if sources.get("dom", {}).get("data"):
      dom_convos = parse_dom_conversations(sources["dom"]["data"], platform)
      conversations.extend(dom_convos)
      print(f"      ✓ DOM: {len(dom_convos)} conversations")

  # Deduplicate by conversation_id
  unique_convos = {}
  for convo in conversations:
    convo_id = convo.get("conversation_id")
    if convo_id and convo_id not in unique_convos:
      unique_convos[convo_id] = convo

  print(f"\n   Total unique conversations: {len(unique_convos)}")
  return list(unique_convos.values())


def parse_api_conversations(api_data: Any, platform: str) -> list[dict]:
  """Parse conversations from API response."""
  conversations = []

  # Handle different API response formats
  if isinstance(api_data, dict):
    # Try common keys
    for key in ["conversations", "data", "items", "results"]:
      if key in api_data and isinstance(api_data[key], list):
        api_data = api_data[key]
        break

  if not isinstance(api_data, list):
    return conversations

  for item in api_data:
    if not isinstance(item, dict):
      continue

    # Generate conversation ID
    convo_id = item.get("id") or item.get("uuid") or generate_id(str(item))

    # Extract messages
    messages = []
    if "messages" in item:
      for msg in item["messages"]:
        messages.append(
          {
            "role": msg.get("role", "unknown"),
            "content": msg.get("content", ""),
            "timestamp": msg.get("created_at") or msg.get("timestamp"),
            "code_context": msg.get("files", []),
          }
        )

    conversation = {
      "conversation_id": convo_id,
      "messages": messages,
      "source": platform,
      "created_at": item.get("created_at") or int(datetime.now().timestamp() * 1000),
      "metadata": {
        "title": item.get("title", "Untitled"),
        "tags": [],
        "difficulty": "unknown",
        "quality_score": 0.0,
        "project": "web-extracted",
        "technologies": [],
      },
    }

    conversations.append(conversation)

  return conversations


def parse_indexeddb_conversations(idb_data: dict, platform: str) -> list[dict]:
  """Parse conversations from IndexedDB data."""
  conversations = []

  for store_name, records in idb_data.items():
    if not isinstance(records, list):
      continue

    for record in records:
      if not isinstance(record, dict):
        continue

      # Try to identify conversation structure
      convo_id = (
        record.get("id")
        or record.get("conversationId")
        or record.get("uuid")
        or generate_id(str(record))
      )

      # Extract messages
      messages = []
      if "messages" in record:
        msg_data = record["messages"]
        if isinstance(msg_data, list):
          for msg in msg_data:
            if isinstance(msg, dict):
              messages.append(
                {
                  "role": msg.get("role", "unknown"),
                  "content": msg.get("content", msg.get("text", "")),
                  "timestamp": msg.get("timestamp"),
                  "code_context": [],
                }
              )

      if messages:
        conversation = {
          "conversation_id": convo_id,
          "messages": messages,
          "source": platform,
          "created_at": int(datetime.now().timestamp() * 1000),
          "metadata": {
            "tags": [],
            "difficulty": "unknown",
            "quality_score": 0.0,
            "project": "web-extracted",
            "technologies": [],
          },
        }
        conversations.append(conversation)

  return conversations


def parse_localstorage_conversations(ls_data: dict, platform: str) -> list[dict]:
  """Parse conversations from localStorage data."""
  conversations = []

  for key, value in ls_data.items():
    if not isinstance(value, dict):
      continue

    # Try to identify if this is a conversation
    has_messages = "messages" in value or "conversation" in value

    if has_messages:
      convo_id = value.get("id") or value.get("conversationId") or generate_id(key)

      messages = []
      msg_data = value.get(
        "messages", value.get("conversation", {}).get("messages", [])
      )

      if isinstance(msg_data, list):
        for msg in msg_data:
          if isinstance(msg, dict):
            messages.append(
              {
                "role": msg.get("role", "unknown"),
                "content": msg.get("content", msg.get("text", "")),
                "timestamp": msg.get("timestamp"),
                "code_context": [],
              }
            )

      if messages:
        conversation = {
          "conversation_id": convo_id,
          "messages": messages,
          "source": platform,
          "created_at": int(datetime.now().timestamp() * 1000),
          "metadata": {
            "tags": [],
            "difficulty": "unknown",
            "quality_score": 0.0,
            "project": "web-extracted",
            "technologies": [],
          },
        }
        conversations.append(conversation)

  return conversations


def parse_dom_conversations(dom_data: list[dict], platform: str) -> list[dict]:
  """Parse conversations from DOM elements (least reliable)."""
  # DOM parsing is tricky - this is a basic implementation
  # Real implementation would need platform-specific selectors
  return []


def generate_id(data: str) -> str:
  """Generate a deterministic ID from data."""
  return hashlib.md5(data.encode()).hexdigest()[:16]


def load_existing_memory() -> dict:
  """Load existing memory from current.json."""
  if not CURRENT_MEMORY.exists():
    return {
      "version": "1.0.0",
      "last_updated": datetime.now().isoformat(),
      "conversations": [],
      "pnkln_architecture": {},
      "llm_allocation": {},
      "jr_framework": {},
    }

  with open(CURRENT_MEMORY) as f:
    return json.load(f)


def merge_conversations(existing: list[dict], new: list[dict]) -> list[dict]:
  """Merge new conversations with existing, avoiding duplicates."""
  print("\n🔀 Merging conversations...")

  # Build index of existing conversation IDs
  existing_ids = {conv["conversation_id"] for conv in existing}

  # Add only new conversations
  added = 0
  for conv in new:
    if conv["conversation_id"] not in existing_ids:
      existing.append(conv)
      added += 1

  print(f"   Existing: {len(existing_ids)}")
  print(f"   New: {len(new)}")
  print(f"   Added: {added}")
  print(f"   Total: {len(existing)}")

  return existing


def save_updated_memory(memory: dict):
  """Save updated memory to current.json and create snapshot."""
  print("\n💾 Saving updated memory...")

  # Update timestamp
  memory["last_updated"] = datetime.now().isoformat()

  # Save to current.json
  with open(CURRENT_MEMORY, "w") as f:
    json.dump(memory, f, indent=2)

  print(f"   ✓ Saved to {CURRENT_MEMORY}")

  # Create snapshot
  snapshots_dir = MEMORY_DIR / "snapshots"
  snapshots_dir.mkdir(exist_ok=True)

  snapshot_file = (
    snapshots_dir / f"memory_web_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
  )
  with open(snapshot_file, "w") as f:
    json.dump(memory, f, indent=2)

  print(f"   ✓ Created snapshot: {snapshot_file.name}")


def main():
  """Main execution flow."""
  print("=" * 60)
  print("Claude Web Extraction Merger v1.0")
  print("=" * 60)

  # 1. Load web extractions
  extractions = load_web_extractions()
  if not extractions:
    print("\n⚠️  No web extraction files found!")
    print(f"   Place claude_web_extraction_*.json files in {EXTRACTIONS_DIR}")
    return

  # 2. Parse conversations
  new_conversations = parse_web_conversations(extractions)
  if not new_conversations:
    print("\n⚠️  No conversations found in extraction files!")
    return

  # 3. Load existing memory
  print("\n📖 Loading existing memory...")
  memory = load_existing_memory()
  print(f"   Current conversations: {len(memory.get('conversations', []))}")

  # 4. Merge
  memory["conversations"] = merge_conversations(
    memory.get("conversations", []), new_conversations
  )

  # 5. Save
  save_updated_memory(memory)

  # 6. Summary
  print("\n" + "=" * 60)
  print("✅ Merge Complete!")
  print("=" * 60)
  print(f"   Total conversations: {len(memory['conversations'])}")
  print(f"   New from web: {len(new_conversations)}")
  print("\n💡 Next steps:")
  print(f"   1. Review {CURRENT_MEMORY}")
  print("   2. Run Gemini metadata generation: python scripts/extract_and_commit.py")
  print("   3. Deploy to Claude Code: python scripts/claude_code_memory_local.py")


if __name__ == "__main__":
  main()
