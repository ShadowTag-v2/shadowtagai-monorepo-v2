#!/usr/bin/env python3
"""
tool_search — Lazy Discovery for Skills System
================================================
Implements Claude Code-style lazy tool loading via semantic search.
Instead of loading all 90+ skills at session start, only load skills
that match the user's current intent.

Usage:
  python tool_search.py "deploy to firebase"
  python tool_search.py "debug memory leak" --top 5
  python tool_search.py --index  # rebuild index
"""

import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from difflib import SequenceMatcher


# --- Configuration -----------------------------------------------------------

SKILLS_DIRS = [
    Path(os.path.expanduser("~/.gemini/antigravity/skills")),
    Path(os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball/.agents/skills")),
]
INDEX_FILE = Path(os.path.expanduser("~/.gemini/antigravity/.tool_search_index.json"))
TOP_K = 5


# --- Data Models -------------------------------------------------------------

@dataclass
class SkillEntry:
    """A single skill registered for search."""
    name: str
    description: str
    path: str
    keywords: list


# --- Index Builder -----------------------------------------------------------

def build_index() -> list[dict]:
    """Scan all skills directories and build a searchable index."""
    entries = []

    for skills_dir in SKILLS_DIRS:
        if not skills_dir.exists():
            continue

        for skill_dir in sorted(skills_dir.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            try:
                content = skill_file.read_text(errors="replace")

                # Extract frontmatter
                name = skill_dir.name
                description = ""
                keywords = []

                # Parse YAML frontmatter
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end > 0:
                        frontmatter = content[3:end]
                        for line in frontmatter.splitlines():
                            if line.startswith("name:"):
                                name = line.split(":", 1)[1].strip().strip("'\"")
                            elif line.startswith("description:"):
                                description = line.split(":", 1)[1].strip().strip("'\"")

                # Extract first non-frontmatter heading as description fallback
                if not description:
                    for line in content.splitlines():
                        if line.startswith("# ") and not line.startswith("---"):
                            description = line[2:].strip()
                            break

                # Build keyword list from content
                # Extract significant words from first 500 chars
                text = content[:500].lower()
                stop_words = {
                    "the", "a", "an", "is", "are", "was", "were", "be",
                    "to", "of", "and", "in", "that", "have", "it", "for",
                    "not", "on", "with", "he", "as", "you", "do", "at",
                    "this", "but", "his", "by", "from", "they", "we",
                    "her", "she", "or", "will", "my", "one", "all",
                    "use", "when", "if", "should", "must", "skill",
                }
                words = set()
                for word in text.split():
                    clean = "".join(c for c in word if c.isalnum())
                    if len(clean) > 3 and clean not in stop_words:
                        words.add(clean)
                keywords = sorted(words)[:20]

                entries.append({
                    "name": name,
                    "description": description[:200],
                    "path": str(skill_file),
                    "keywords": keywords,
                })

            except (OSError, UnicodeDecodeError) as e:
                print(f"[WARN] Error reading {skill_file}: {e}", file=sys.stderr)

    # Write index
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w") as f:
        json.dump(
            {"version": 1, "count": len(entries), "entries": entries},
            f,
            indent=2,
        )

    print(f"[INDEX] Built index with {len(entries)} skills → {INDEX_FILE}")
    return entries


# --- Search ------------------------------------------------------------------

def search(query: str, top_k: int = TOP_K) -> list[dict]:
    """Search the skills index for matching skills."""

    # Load or build index
    if INDEX_FILE.exists():
        with open(INDEX_FILE) as f:
            data = json.load(f)
        entries = data["entries"]
    else:
        entries = build_index()

    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored = []
    for entry in entries:
        score = 0.0

        # Name match (highest weight)
        name_sim = SequenceMatcher(None, query_lower, entry["name"].lower()).ratio()
        score += name_sim * 3.0

        # Description match
        desc_sim = SequenceMatcher(
            None, query_lower, entry["description"].lower()
        ).ratio()
        score += desc_sim * 2.0

        # Keyword overlap
        entry_keywords = set(entry.get("keywords", []))
        keyword_overlap = len(query_words & entry_keywords)
        score += keyword_overlap * 1.5

        # Substring match bonus
        if query_lower in entry["name"].lower():
            score += 2.0
        if query_lower in entry["description"].lower():
            score += 1.0

        scored.append((score, entry))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, entry in scored[:top_k]:
        if score > 0.3:  # Minimum relevance threshold
            results.append({
                **entry,
                "relevance": round(score, 2),
            })

    return results


# --- Main --------------------------------------------------------------------

def main():
    if "--index" in sys.argv:
        build_index()
        return

    if len(sys.argv) < 2:
        print("Usage: python tool_search.py <query> [--top N] [--index]")
        print("\nExamples:")
        print('  python tool_search.py "deploy to firebase"')
        print('  python tool_search.py "debug memory leak" --top 3')
        sys.exit(1)

    query = sys.argv[1]
    top_k = TOP_K

    if "--top" in sys.argv:
        idx = sys.argv.index("--top")
        if idx + 1 < len(sys.argv):
            top_k = int(sys.argv[idx + 1])

    results = search(query, top_k)

    if not results:
        print(f"No skills found matching: '{query}'")
        sys.exit(0)

    print(f"Skills matching '{query}':\n")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['name']} (relevance: {result['relevance']})")
        print(f"     {result['description']}")
        print(f"     → {result['path']}")
        print()


if __name__ == "__main__":
    main()
