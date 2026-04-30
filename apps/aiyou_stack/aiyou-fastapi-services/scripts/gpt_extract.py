#!/usr/bin/env python3
"""ChatGPT Conversation Extractor
Extracts conversations from ChatGPT data export
"""

import json
from datetime import datetime
from pathlib import Path

CHATGPT_DIR = Path("/Users/pikeymickey/Downloads/ChatGPT data")
OUTPUT_DIR = Path("/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/docs/chatgpt_extracted")


def extract_messages(mapping: dict) -> list:
    """Extract messages from conversation mapping"""
    messages = []

    for _node_id, node in mapping.items():
        if node.get("message"):
            msg = node["message"]
            author = msg.get("author", {}).get("role", "unknown")
            content = msg.get("content", {})

            if content.get("content_type") == "text":
                parts = content.get("parts", [])
                text = " ".join(p for p in parts if isinstance(p, str) and p.strip())
                if text:
                    messages.append(
                        {"role": author, "content": text, "timestamp": msg.get("create_time")},
                    )

    return messages


def main():
    print("=" * 60)
    print("CHATGPT CONVERSATION EXTRACTOR")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load conversations
    conv_file = CHATGPT_DIR / "conversations.json"
    if not conv_file.exists():
        print(f"ERROR: {conv_file} not found")
        return

    with open(conv_file) as f:
        conversations = json.load(f)

    print(f"\nFound {len(conversations)} conversations")

    all_extracted = []
    code_blocks = []

    for conv in conversations:
        title = conv.get("title", "Untitled")
        mapping = conv.get("mapping", {})
        messages = extract_messages(mapping)

        if messages:
            extracted = {
                "title": title,
                "id": conv.get("conversation_id", conv.get("id")),
                "created": conv.get("create_time"),
                "messages": messages,
            }
            all_extracted.append(extracted)

            # Extract code blocks from assistant messages
            for msg in messages:
                if msg["role"] == "assistant":
                    content = msg["content"]
                    # Find code blocks
                    import re

                    blocks = re.findall(r"```(\w*)\n([\s\S]*?)```", content)
                    for lang, code in blocks:
                        code_blocks.append(
                            {
                                "conversation": title,
                                "language": lang or "text",
                                "code": code.strip(),
                            },
                        )

            print(f"  [{len(messages):3d} msgs] {title[:50]}...")

    # Save extracted conversations
    output_file = OUTPUT_DIR / "conversations_extracted.json"
    with open(output_file, "w") as f:
        json.dump(all_extracted, f, indent=2, default=str)

    # Save code blocks
    code_file = OUTPUT_DIR / "code_blocks.json"
    with open(code_file, "w") as f:
        json.dump(code_blocks, f, indent=2)

    # Create manifest
    manifest = {
        "extracted_at": datetime.now().isoformat(),
        "total_conversations": len(conversations),
        "conversations_with_content": len(all_extracted),
        "total_messages": sum(len(c["messages"]) for c in all_extracted),
        "code_blocks_found": len(code_blocks),
    }

    manifest_file = OUTPUT_DIR / "manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Conversations extracted:  {len(all_extracted)}")
    print(f"Total messages:           {manifest['total_messages']}")
    print(f"Code blocks found:        {len(code_blocks)}")
    print(f"\nOutput: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
