#!/usr/bin/env python3
"""Drive Content Analyzer ("The Gucci Finder")

Parses pnkln_intelligence/knowledge_base/drive_index.json to identify high-value assets.
Categorizes them into:
- STRATEGY (Business plans, Valuations, Decks)
- TECHNICAL (Architecture, API Clients, Code)
- LEGAL (Compliance, Contracts, Standards)
- KNOWLEDGE (Books, Papers, Research)

Outputs: pnkln_intelligence/knowledge_base/gucci_manifest.md
"""

import json
import os
from datetime import datetime

INDEX_FILE = "pnkln_intelligence/knowledge_base/drive_index.json"
OUTPUT_FILE = "pnkln_intelligence/knowledge_base/gucci_manifest.md"

CATEGORIES = {
    "STRATEGY": [
        "valuation",
        "business plan",
        "pitch",
        "deck",
        "strategy",
        "roadmap",
        "revenue",
        "monetization",
        "positioning",
    ],
    "TECHNICAL": [
        ".py",
        ".go",
        ".java",
        ".yaml",
        ".yml",
        ".json",
        ".sql",
        "architecture",
        "api",
        "spec",
        "design",
        "schema",
    ],
    "LEGAL": [
        "compliance",
        "pci",
        "gdpr",
        "nist",
        "contract",
        "agreement",
        "term sheet",
        "law",
        "legal",
        "corporations code",
    ],
    "KNOWLEDGE": [".pdf", "book", "paper", "research", "manual", "guide", "learning", "analysis"],
}


def analyze_file(file_item):
    name = file_item.get("name", "").lower()
    mime = file_item.get("mimeType", "")

    # Skip folders
    if mime == "application/vnd.google-apps.folder":
        return None

    matched_categories = []

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in name:
                matched_categories.append(category)
                break

    if not matched_categories:
        return None

    return {
        "name": file_item["name"],
        "link": file_item["webViewLink"],
        "categories": matched_categories,
        "size": file_item.get("size", "0"),
    }


def main():
    if not os.path.exists(INDEX_FILE):
        print(f"Error: Index file not found at {INDEX_FILE}")
        return

    print(f"Loading index from {INDEX_FILE}...")
    with open(INDEX_FILE) as f:
        data = json.load(f)

    files = data.get("files", [])
    print(f"Analyzing {len(files)} files...")

    gucci_assets = {cat: [] for cat in CATEGORIES}

    for file_item in files:
        result = analyze_file(file_item)
        if result:
            # Add to primary category (first match) or specific logic could be added
            # For now, add to all matched categories to be exhaustive
            for cat in result["categories"]:
                gucci_assets[cat].append(result)

    # Generate Markdown Report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_content = f"""# 💎 The Gucci Manifest (Drive Analysis)
**Generated:** {timestamp}
**Source:** {data.get("target_folder_id")}
**Total Files Indexed:** {len(files)}

"""

    for category, assets in gucci_assets.items():
        if not assets:
            continue

        md_content += f"## {category} ({len(assets)})\n"
        # Sort by name
        assets.sort(key=lambda x: x["name"])

        for asset in assets:
            # Clean size
            try:
                size_mb = float(asset["size"]) / (1024 * 1024)
                size_str = f"{size_mb:.1f}MB" if size_mb > 1 else f"{int(asset['size']) // 1024}KB"
            except Exception:
                size_str = "?"

            md_content += f"- [{asset['name']}]({asset['link']}) `({size_str})`\n"
        md_content += "\n"

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(md_content)

    print(f"Manifest generated at: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
