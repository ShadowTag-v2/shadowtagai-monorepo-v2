#!/usr/bin/env python3
"""
Notes to Code Converter
Extracts code-relevant content from iPhone Notes and Google Drive docs
"""

import json
import re
from datetime import datetime
from pathlib import Path

# Directories
NOTES_DIR = Path("/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/docs/icloud_notes_imported")
GDRIVE_DIR = Path(
    "/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/docs/gdrive_sync/ShadowTag-v2_Phase_Docs"
)
OUTPUT_DIR = Path("/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/docs/extracted_code")

# Patterns for code-relevant content
CODE_PATTERNS = [
    r"```[\s\S]*?```",  # Code blocks
    r"class\s+\w+",  # Class definitions
    r"def\s+\w+",  # Function definitions
    r"async\s+def\s+\w+",  # Async functions
    r"import\s+\w+",  # Imports
    r"from\s+\w+\s+import",  # From imports
    r"@\w+",  # Decorators
    r"POST\s+/api/",  # API endpoints
    r"GET\s+/api/",
    r"PUT\s+/api/",
    r"DELETE\s+/api/",
]

# Keywords indicating code/technical content
CODE_KEYWORDS = [
    "api",
    "endpoint",
    "function",
    "class",
    "method",
    "agent",
    "swarm",
    "judge",
    "engine",
    "pipeline",
    "workflow",
    "schema",
    "model",
    "fastapi",
    "python",
    "typescript",
    "deploy",
    "kubernetes",
    "gke",
    "terraform",
    "dockerfile",
    "yaml",
    "json",
    "config",
    "env",
    "async",
    "await",
    "redis",
    "postgres",
    "firestore",
    "vertex",
    "gemini",
    "claude",
    "anthropic",
    "openai",
    "llm",
    "prompt",
    "shadowtag",
    "shadowtag_v4",
    "pnkln",
    "n-autoresearch/Kosmos/BioAgents",
    "ultrathink",
]


def is_code_relevant(text: str) -> bool:
    """Check if text contains code-relevant content"""
    text_lower = text.lower()

    # Check for code patterns
    for pattern in CODE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    # Check for keywords (need at least 3)
    keyword_count = sum(1 for kw in CODE_KEYWORDS if kw in text_lower)
    return keyword_count >= 3


def extract_code_blocks(text: str) -> list:
    """Extract code blocks from text"""
    blocks = []

    # Markdown code blocks
    pattern = r"```(\w*)\n([\s\S]*?)```"
    for match in re.finditer(pattern, text):
        lang = match.group(1) or "text"
        code = match.group(2).strip()
        blocks.append({"language": lang, "code": code})

    return blocks


def extract_api_specs(text: str) -> list:
    """Extract API endpoint specifications"""
    specs = []

    # Match API endpoint patterns
    pattern = r"(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/{}]+)"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        specs.append({"method": match.group(1).upper(), "path": match.group(2)})

    return specs


def process_note(filepath: Path) -> dict:
    """Process a single note file"""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return None

    if not is_code_relevant(content):
        return None

    return {
        "source": str(filepath),
        "filename": filepath.name,
        "content": content,
        "code_blocks": extract_code_blocks(content),
        "api_specs": extract_api_specs(content),
        "size": len(content),
    }


def scan_notes_directory() -> list:
    """Scan all iPhone notes"""
    results = []

    for txt_file in NOTES_DIR.rglob("*.txt"):
        result = process_note(txt_file)
        if result:
            results.append(result)
            print(f"  [CODE] {txt_file.name[:60]}...")

    return results


def generate_manifest(results: list) -> dict:
    """Generate a manifest of extracted code"""
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "total_notes_scanned": len(list(NOTES_DIR.rglob("*.txt"))),
        "code_relevant_notes": len(results),
        "total_code_blocks": sum(len(r["code_blocks"]) for r in results),
        "total_api_specs": sum(len(r["api_specs"]) for r in results),
        "files": [],
    }

    for r in results:
        manifest["files"].append(
            {
                "filename": r["filename"],
                "code_blocks": len(r["code_blocks"]),
                "api_specs": len(r["api_specs"]),
                "size": r["size"],
            }
        )

    return manifest


def main():
    print("=" * 60)
    print("NOTES TO CODE CONVERTER")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Scan iPhone notes
    print(f"\nScanning iPhone Notes: {NOTES_DIR}")
    print("-" * 40)
    results = scan_notes_directory()

    # Generate manifest
    manifest = generate_manifest(results)

    # Save manifest
    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Save extracted code blocks
    code_blocks_path = OUTPUT_DIR / "code_blocks.json"
    all_blocks = []
    for r in results:
        for block in r["code_blocks"]:
            all_blocks.append(
                {"source": r["filename"], "language": block["language"], "code": block["code"]}
            )

    with open(code_blocks_path, "w") as f:
        json.dump(all_blocks, f, indent=2)

    # Save API specs
    api_specs_path = OUTPUT_DIR / "api_specs.json"
    all_specs = []
    for r in results:
        for spec in r["api_specs"]:
            all_specs.append({"source": r["filename"], **spec})

    with open(api_specs_path, "w") as f:
        json.dump(all_specs, f, indent=2)

    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Notes scanned:        {manifest['total_notes_scanned']}")
    print(f"Code-relevant notes:  {manifest['code_relevant_notes']}")
    print(f"Code blocks found:    {manifest['total_code_blocks']}")
    print(f"API specs found:      {manifest['total_api_specs']}")
    print(f"\nOutput: {OUTPUT_DIR}")
    print("  - manifest.json")
    print("  - code_blocks.json")
    print("  - api_specs.json")


if __name__ == "__main__":
    main()
