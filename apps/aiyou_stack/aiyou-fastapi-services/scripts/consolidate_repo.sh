#!/bin/bash
set -e

# Repository Consolidation Script
# Implements the approved consolidation_plan.md

echo "🚀 Starting Repository Consolidation..."
ROOT_DIR=$(pwd)
echo "📂 Working directory: $ROOT_DIR"

# 1. Setup Directories
echo "🛠️ Creating target structure..."
mkdir -p _staging/agents
mkdir -p _staging/infrastructure
mkdir -p _staging/legacy
mkdir -p src/n-autoresearch/Kosmos/BioAgents
mkdir -p src/pnkln
mkdir -p src/shadowtag
mkdir -p infrastructure
mkdir -p docs
mkdir -p bin

# 2. Phase 1: Grouping (Move to Staging)
echo "📦 Phase 1: Grouping scattered directories..."

# Agents
for d in active_shield_medical agent0 agents kosmos_agent vertex-ai-agents; do
    if [ -d "$d" ]; then
        echo "  -> Moving $d to _staging/agents"
        mv "$d" _staging/agents/
    fi
done

# Infrastructure
for d in deploy deployment k8s kubernetes terraform cloud-run-go; do
    if [ -d "$d" ]; then
        echo "  -> Moving $d to _staging/infrastructure"
        mv "$d" _staging/infrastructure/
    fi
done

# Legacy (pinkln* with 'i', shadowtagai*)
# Using find to be safe with globs regarding non-existence
find . -maxdepth 1 -name "pinkln*" -type d -exec mv {} _staging/legacy/ \;
find . -maxdepth 1 -name "shadowtagai*" -type d -exec mv {} _staging/legacy/ \;
find . -maxdepth 1 -name "legacy_scripts*" -type d -exec mv {} _staging/legacy/ \;

# 3. Phase 2: Merging (Move from Staging/Root to Target)
echo "🏗️ Phase 2: Merging into Unified Structure..."

# Merge Agents -> src/n-autoresearch/Kosmos/BioAgents
# Moving contents of staging agents to src/n-autoresearch/Kosmos/BioAgents
if [ -d "_staging/agents" ]; then
    echo "  -> Merging agents into src/n-autoresearch/Kosmos/BioAgents"
    cp -R _staging/agents/* src/n-autoresearch/Kosmos/BioAgents/ 2>/dev/null || true
fi

# Merge Infrastructure -> infrastructure
if [ -d "_staging/infrastructure" ]; then
    echo "  -> Merging infrastructure"
    cp -R _staging/infrastructure/* infrastructure/ 2>/dev/null || true
fi

# Merge Pnkln (Core) -> src/pnkln
# pnkln* (no i) directories
echo "  -> Consolidating pnkln core framework..."
find . -maxdepth 1 -name "pnkln*" -type d -not -name "pnkln_mission_start.py" -exec mv {} src/pnkln/ \;

# Merge Documentation
echo "  -> Consolidating documentation..."
find . -maxdepth 1 -name "*.md" -not -name "README.md" -not -name "CLAUDE.md" -not -name "GEMINI.md" -not -name "task.md" -exec mv {} docs/ \;

# 4. Cleanup
echo "🧹 Phase 3: Cleanup..."
# Remove staging if empty or just keep for safety check?
# Validated plan said cleanup. We copied from staging, so we can remove staging.
rm -rf _staging

# 5. External Repos & Backup Recovery
echo "🔗 Phase 4: External repos and backup recovery..."

ANTIGRAVITY_REPOS="$HOME/antigravity-repos"
ANTIGRAVITY_FLAT="$HOME/antigravity-flattened"
GOOGLE_DRIVE_BACKUP="$HOME/Library/CloudStorage/GoogleDrive-founder@shadowtagai.com/My Drive/From Mac"

# Symlink antigravity repos
mkdir -p external_repos
if [ -d "$ANTIGRAVITY_REPOS" ] && [ ! -L "external_repos/antigravity-repos" ]; then
    ln -sf "$ANTIGRAVITY_REPOS" external_repos/antigravity-repos
    echo "  -> Symlinked antigravity-repos"
fi

# Copy recovered backup docs
if [ -d "$GOOGLE_DRIVE_BACKUP" ]; then
    echo "  -> Recovering critical docs from Google Drive backup..."
    cp -n "$GOOGLE_DRIVE_BACKUP/ShadowTag-v2JR_CLAUDE_CODE_INFRASTRUCTURE.md" docs/ 2>/dev/null || true
    cp -n "$GOOGLE_DRIVE_BACKUP/github-mcp-integration-plan.md" docs/ 2>/dev/null || true
    cp -n "$GOOGLE_DRIVE_BACKUP/Cor_54_Pnkln_vs_Google_Vertex_AI_Architecture.md" docs/ 2>/dev/null || true
fi

# 6. Verify workspace symlinks
echo "🔍 Phase 5: Verifying workspace symlinks..."
for dir in "$HOME/ShadowTag-v2-stack/ShadowTag-v2-"*; do
    if [ -L "$dir" ]; then
        echo "  $dir -> $(readlink "$dir")"
    elif [ -d "$dir" ]; then
        echo "  $dir (NOT SYMLINKED - consider linking)"
    fi
done

echo "✅ Consolidation Complete!"
echo "New Top-Level Structure:"
ls -d */
echo ""
echo "Antigravity repos: $(ls "$ANTIGRAVITY_REPOS" 2>/dev/null | wc -l | tr -d ' ') repos"
echo "Flattened index: $(python3 -c "import json; print(json.load(open('$ANTIGRAVITY_FLAT/index.json'))['stats']['total_repos'])" 2>/dev/null || echo 'N/A') repos indexed"
