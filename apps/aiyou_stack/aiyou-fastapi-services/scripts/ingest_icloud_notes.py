#!/usr/bin/env python3
"""
Ingest iCloud Notes export into ShadowTag-v2 docs/notes/
Reads exported note directories, extracts text, builds index.
"""

import csv
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

NOTES_ROOT = Path(os.path.expanduser("~/Downloads/iCloud Notes"))
NOTES_DIR = NOTES_ROOT / "Notes"
DELETED_DIR = NOTES_ROOT / "Recently Deleted"
DETAILS_CSV = NOTES_ROOT / "Notes Details.csv"

OUTPUT_DIR = Path(os.path.expanduser("~/shadowtag_v4-stack/ShadowTag-v2/docs/notes"))
INDEX_FILE = OUTPUT_DIR / "index.json"


def sanitize_filename(name: str, max_len: int = 80) -> str:
    """Convert note title to safe filename."""
    name = re.sub(r"[^\w\s\-.]", "", name)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:max_len] if name else "untitled"


def read_note_text(note_dir: Path) -> str:
    """Read the .txt file from a note directory."""
    for f in note_dir.iterdir():
        if f.suffix == ".txt":
            return f.read_text(errors="replace")
    return ""


def parse_details_csv() -> dict:
    """Parse the Notes Details CSV for metadata."""
    metadata = {}
    if not DETAILS_CSV.exists():
        return metadata
    with open(DETAILS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("Title", "").strip()
            if title:
                metadata[title] = {
                    "created": row.get(" Created On", "").strip(),
                    "modified": row.get(" Modified On", "").strip(),
                    "pinned": row.get(" Pinned", "").strip() == "Yes",
                    "deleted": row.get(" Deleted", "").strip() == "Yes",
                    "has_drawing": row.get(" Drawing/Handwriting", "").strip() == "Yes",
                }
    return metadata


def classify_note(title: str, text: str) -> str:
    """Classify note into category based on content."""
    t = (title + " " + text[:500]).lower()
    if any(k in t for k in ["cor.", "cor ", "cor1", "boardroom"]):
        return "cor"
    if any(k in t for k in ["pnkln", "pinkln", "ultrathink"]):
        return "pnkln"
    if any(k in t for k in ["antigravity", "autoresearch", "n-autoresearch/Kosmos/BioAgents", "swarm"]):
        return "antigravity"
    if any(k in t for k in ["deploy", "gke", "cloud run", "terraform", "k8s"]):
        return "infrastructure"
    if any(k in t for k in ["prompt", "gemini", "claude", "gpt"]):
        return "prompts"
    if any(k in t for k in ["business", "revenue", "valuation", "investor"]):
        return "business"
    if any(k in t for k in ["judge", "governance", "safety", "doctrine"]):
        return "governance"
    return "general"


def ingest():
    """Main ingestion pipeline."""
    print(f"Ingesting iCloud Notes from {NOTES_DIR}")

    if not NOTES_DIR.exists():
        print(f"ERROR: {NOTES_DIR} not found")
        return

    # Parse metadata
    metadata = parse_details_csv()
    print(f"Found {len(metadata)} entries in details CSV")

    # Create output structure
    categories = [
        "cor",
        "pnkln",
        "antigravity",
        "infrastructure",
        "prompts",
        "business",
        "governance",
        "general",
    ]
    for cat in categories:
        (OUTPUT_DIR / cat).mkdir(parents=True, exist_ok=True)

    index = {
        "source": str(NOTES_ROOT),
        "ingested_at": datetime.now().isoformat(),
        "total_notes": 0,
        "categories": {c: [] for c in categories},
        "notes": [],
    }

    note_dirs = sorted(NOTES_DIR.iterdir()) if NOTES_DIR.exists() else []
    print(f"Processing {len(note_dirs)} note directories...")

    for note_dir in note_dirs:
        if not note_dir.is_dir():
            continue

        title = note_dir.name
        text = read_note_text(note_dir)
        if not text:
            continue

        category = classify_note(title, text)
        safe_name = sanitize_filename(title)
        output_file = OUTPUT_DIR / category / f"{safe_name}.md"

        # Get metadata if available
        meta = metadata.get(title, {})

        # Write as markdown
        header = f"# {title}\n\n"
        if meta:
            header += f"**Created:** {meta.get('created', 'unknown')}  \n"
            header += f"**Modified:** {meta.get('modified', 'unknown')}  \n"
            header += f"**Category:** {category}  \n\n---\n\n"

        output_file.write_text(header + text)

        # Copy images
        images = [
            f for f in note_dir.iterdir() if f.suffix in (".png", ".jpg", ".jpeg", ".avif", ".gif")
        ]
        if images:
            img_dir = OUTPUT_DIR / category / f"{safe_name}_assets"
            img_dir.mkdir(exist_ok=True)
            for img in images:
                shutil.copy2(img, img_dir / img.name)

        entry = {
            "title": title,
            "category": category,
            "file": str(output_file.relative_to(OUTPUT_DIR)),
            "images": len(images),
            "chars": len(text),
            "created": meta.get("created", ""),
            "modified": meta.get("modified", ""),
        }
        index["notes"].append(entry)
        index["categories"][category].append(safe_name)
        index["total_notes"] += 1

    # Write index
    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

    print("\nIngestion complete!")
    print(f"  Total notes: {index['total_notes']}")
    for cat in categories:
        count = len(index["categories"][cat])
        if count:
            print(f"  {cat}: {count}")
    print(f"\nOutput: {OUTPUT_DIR}")
    print(f"Index:  {INDEX_FILE}")


if __name__ == "__main__":
    ingest()
