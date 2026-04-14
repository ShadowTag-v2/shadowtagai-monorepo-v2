#!/bin/bash
# LanceDB SKILL.md Ingestion Script
# Ingests all SKILL.md files into LanceDB for semantic search
# Usage: ./scripts/ingest_skills_lancedb.sh

set -euo pipefail

echo "=== LANCEDB SKILL INGESTION ==="
echo ""

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_GLOBAL="$HOME/.gemini/antigravity/skills"
SKILLS_WORKSPACE="$REPO_ROOT/.agents/skills"

# Collect all SKILL.md files
SKILL_FILES=()
while IFS= read -r -d '' file; do
    SKILL_FILES+=("$file")
done < <(find "$SKILLS_GLOBAL" "$SKILLS_WORKSPACE" -name "SKILL.md" -print0 2>/dev/null)

echo "Found ${#SKILL_FILES[@]} SKILL.md files"
echo ""

# Create ingestion manifest
MANIFEST_DIR="$REPO_ROOT/apps/data/lancedb"
mkdir -p "$MANIFEST_DIR"

MANIFEST="$MANIFEST_DIR/skill_manifest.jsonl"

# Use Python to safely generate JSONL (shell echo breaks on quotes/special chars in descriptions)
python3 - "$MANIFEST" "${SKILL_FILES[@]}" << 'MANIFEST_EOF'
import json, sys, os, re

manifest_path = sys.argv[1]
skill_files = sys.argv[2:]

with open(manifest_path, 'w') as out:
    for skill_file in skill_files:
        skill_dir = os.path.dirname(skill_file)
        skill_name = os.path.basename(skill_dir)
        
        # Extract description from YAML frontmatter
        description = ""
        try:
            with open(skill_file) as f:
                content = f.read()
            # Match description field in YAML frontmatter
            m = re.search(r'^description:\s*["\']?(.*?)(?:["\']?\s*$)', content, re.MULTILINE)
            if m:
                description = m.group(1).strip().strip('"').strip("'")
            # Handle multi-line descriptions with >
            m2 = re.search(r'^description:\s*>\s*\n((?:\s{2,}.*\n?)+)', content, re.MULTILINE)
            if m2:
                description = ' '.join(line.strip() for line in m2.group(1).strip().splitlines())
        except Exception:
            pass
        
        file_size = os.path.getsize(skill_file)
        
        entry = {
            "skill_name": skill_name,
            "path": skill_file,
            "size_bytes": file_size,
            "description": description[:500],  # Cap at 500 chars
        }
        out.write(json.dumps(entry) + '\n')

print(f"Wrote {len(skill_files)} entries to {manifest_path}")
MANIFEST_EOF

echo "Manifest written to: $MANIFEST"
echo "Entries: $(wc -l < "$MANIFEST")"
echo ""

# Check if LanceDB Python package is available
if python3 -c "import lancedb" 2>/dev/null; then
    echo "✅ LanceDB Python package available"
    
    # Run actual ingestion
    python3 << 'PYTHON_EOF'
import json
import os
import lancedb

# Connect to local LanceDB
db_path = os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball/apps/data/lancedb/skills.lance")
db = lancedb.connect(db_path)

# Read manifest
manifest_path = os.path.expanduser("~/.gemini/antigravity/Monorepo-Uphillsnowball/apps/data/lancedb/skill_manifest.jsonl")
records = []
with open(manifest_path) as f:
    for line in f:
        entry = json.loads(line.strip())
        # Read full content
        with open(entry["path"]) as sf:
            content = sf.read()
        records.append({
            "skill_name": entry["skill_name"],
            "path": entry["path"],
            "description": entry.get("description", ""),
            "content": content,
            "size_bytes": entry["size_bytes"],
        })

# Create/overwrite table (use mode='overwrite' to avoid drop+create race)
table = db.create_table("skills", records, mode="overwrite")
print(f"✅ Ingested {len(records)} skills into LanceDB")
print(f"   Table: skills")
print(f"   Records: {table.count_rows()}")
PYTHON_EOF
else
    echo "⚠️  LanceDB Python package not installed"
    echo "   Install with: pip install lancedb"
    echo "   Manifest saved for manual ingestion"
fi

echo ""
echo "=== INGESTION COMPLETE ==="
