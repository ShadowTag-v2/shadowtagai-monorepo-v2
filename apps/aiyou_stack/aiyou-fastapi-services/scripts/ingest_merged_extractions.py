#!/usr/bin/env python3
"""
Ingest Merged Extractions into Memory Bank.

This script takes the output of `merge_web_extractions.py` (JSON) and folds it into
the main system memory file (`memory/current.json`).

It performs schema mapping:
- Maps "conversations" from exports to the internal `conversations` list.
- Maps "documentation/links" to a `knowledge` list (if applicable).
- Filters out low-value noise (like empty localStorage keys).
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "erik-hancock-llm-memory" / "extractions" / "merged_extractions.json"
MEMORY_FILE = BASE_DIR / "erik-hancock-llm-memory" / "memory" / "current.json"


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return None


def save_json(path: Path, data: Any) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Create backup
        if path.exists():
            backup_path = path.with_suffix(f".bak.{int(datetime.now().timestamp())}")
            path.rename(backup_path)
            logger.info(f"Backed up current memory to {backup_path.name}")

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Saved updated memory to {path}")
    except Exception as e:
        logger.error(f"Failed to save {path}: {e}")


def transform_to_conversation(item: dict[str, Any]) -> dict[str, Any] | None:
    """Transform a raw extraction item into a memory conversation object."""

    # 1. Handle Chat/Conversation types
    # Check for direct message list (ChatGPT/Claude API format)
    messages = []
    source = item.get("_source", "unknown_source")

    # Normalize ChatGPT/Claude structures
    if "mapping" in item:  # ChatGPT export distinct structure
        # (Simplified handling for ChatGPT mapping structure if present)
        # For now, assuming linear attributes or raw text
        pass

    # If item has 'messages' list directly
    if "messages" in item and isinstance(item["messages"], list):
        messages = item["messages"]

    # If item is a DOM extraction (often just innerHTML/textContent)
    elif "textContent" in item:
        # Create a single message representing the scrape
        item["textContent"][:200].replace("\n", " ")
        messages = [
            {
                "role": "user",
                "content": f"[Extracted from {source}]\n{item['textContent']}",
                "timestamp": datetime.now().isoformat(),
            }
        ]

    # If item is from LocalStorage (Claude)
    elif source == "claude_localstorage":
        # Filter out metadata keys
        key = item.get("key", "")
        if "syncSource" in key or "attachment" in key or "claudeSpark" in key:
            return None  # Skip noise

        content_val = item.get("content", {})
        # Sometimes content is valid text
        if isinstance(content_val, str) and len(content_val) > 50:
            messages = [{"role": "user", "content": content_val}]
        elif isinstance(content_val, dict):
            # Try to find text in complex object
            if "value" in content_val:
                val = content_val["value"]
                if isinstance(val, str) and len(val) > 50:
                    messages = [{"role": "user", "content": val}]

    # Validation: Must have at least one message
    if not messages:
        return None

    # Construct Conversation Object
    return {
        "conversation_id": item.get("id") or item.get("conversation_id") or str(uuid.uuid4()),
        "messages": messages,
        "source": source,
        "created_at": item.get("create_time") or datetime.now().isoformat(),
        "metadata": {
            "title": item.get("title", "Imported Conversation"),
            "original_keys": list(item.keys()),
        },
    }


def transform_to_knowledge(item: dict[str, Any]) -> dict[str, Any] | None:
    """Transform documentation/link items into knowledge objects."""
    if "url" in item and "title" in item:
        # Likely a bookmark or doc link
        return {
            "topic": item.get("title"),
            "content": item.get("description", ""),
            "source": item.get("url"),
            "learned_at": datetime.now().isoformat(),
        }
    return None


def main():
    logger.info(f"Reading merged extractions from {INPUT_FILE}...")
    extracted_data = load_json(INPUT_FILE)
    if not extracted_data:
        logger.error("No data found or file missing.")
        return

    logger.info(f"Loading system memory from {MEMORY_FILE}...")
    memory = load_json(MEMORY_FILE)
    if not memory:
        logger.warning("Memory file missing/corrupt. Creating new.")
        memory = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "conversations": [],
            "knowledge": [],
        }

    # Ensure sections exist
    if "conversations" not in memory:
        memory["conversations"] = []
    if "knowledge" not in memory:
        memory["knowledge"] = []

    new_convs = 0
    new_knowledge = 0
    skipped = 0

    # Index existing IDs for specific deduplication
    existing_ids = {
        c.get("conversation_id") for c in memory["conversations"] if c.get("conversation_id")
    }

    for item in extracted_data:
        # Try as Knowledge first (cleaner structure usually)
        k_item = transform_to_knowledge(item)
        if k_item:
            # Simple content dedup
            is_dup = any(k["source"] == k_item["source"] for k in memory["knowledge"])
            if not is_dup:
                memory["knowledge"].append(k_item)
                new_knowledge += 1
            else:
                skipped += 1
            continue

        # Try as Conversation
        c_item = transform_to_conversation(item)
        if c_item:
            cid = c_item["conversation_id"]
            if cid not in existing_ids:
                memory["conversations"].append(c_item)
                existing_ids.add(cid)
                new_convs += 1
            else:
                skipped += 1
            continue

        skipped += 1

    memory["last_updated"] = datetime.now().isoformat()

    logger.info("-" * 40)
    logger.info("Ingestion Report:")
    logger.info(f"  New Conversations: {new_convs}")
    logger.info(f"  New Knowledge Items: {new_knowledge}")
    logger.info(f"  Skipped/Duplicate: {skipped}")
    logger.info("-" * 40)

    if new_convs > 0 or new_knowledge > 0:
        save_json(MEMORY_FILE, memory)
    else:
        logger.info("No changes to save.")


if __name__ == "__main__":
    main()
