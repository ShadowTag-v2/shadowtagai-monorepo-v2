#!/bin/bash
set -e

# ==============================================================================
# 1. PRE-FLIGHT CHECKS & SETUP
# ==============================================================================
echo "🚀 Initiating TOTAL ANTIGRAVITY TRANSFER..."
echo "⚠️  WARNING: This will aggressively restructure your entire repository."
echo "    All loose root files will be moved to 'tools/legacy' or 'docs/archive'."

# Create the Holy Structure
mkdir -p apps libs infra/k8s infra/terraform infra/cloudbuild tools/scripts tools/legacy docs/archive data

# ==============================================================================
# 2. APPLICATION MIGRATION (The "Apps" Bucket)
# ==============================================================================
# These are standalone services or major components identified from your file list.
APPS=(
    "api"
    "voice_consensus"
    "transcode-service"
    "ungpt"
    "vertex-ai-agents"
    "yougle-ai"
    "universal-copilot"
    "shadowtagai"
    "judge6"
    "kosmos"
    "pnkln"
    "seatjudge-monorepo"
    "computer-use"
    "computer_use"       # Potential duplicate/variant
    "digital-freeway-api"
    "fast-api"
    "frontend"
    "hello-world"
    "humanfsd"
    "kosmos_agent"
    "kosmos_dev"
    "landing-pages"
    "media-edge"
    "nightly_intel_pipeline"
    "pinkln-intelligence-pipeline"
    "pinkln-reasoning-engine"
    "pnkln-framework"
    "shadowtag_core"
    "shadowtag_v2"
    "services"           # Generic folder, treating as app collection
    "agent0"
    "antigravity-go"     # Moving Go projects to apps for now
)

echo "📦 Migrating Applications..."
for app in "${APPS[@]}"; do
    if [ -d "$app" ]; then
        echo "   -> Moving $app to apps/"
        # Handle collision if apps/$app already exists from previous runs
        if [ -d "apps/$app" ]; then
            echo "      ! Collision detected. Merging contents..."
            cp -R "$app/"* "apps/$app/" 2>/dev/null || true
            rm -rf "$app"
        else
            mv "$app" apps/
        fi
    fi
done

# ==============================================================================
# 3. INFRASTRUCTURE MIGRATION (The "Infra" Bucket)
# ==============================================================================
# Moving Dockerfiles, Cloudbuild, K8s, Terraform
echo "🏗️  Migrating Infrastructure..."

# Move K8s folder
if [ -d "k8s" ]; then mv k8s/* infra/k8s/ && rm -d k8s; fi

# Move Terraform related
mv *.tf .terraform* infra/terraform/ 2>/dev/null || true
mv main.tf infra/terraform/ 2>/dev/null || true

# Move Cloud Build YAMLs
mv cloudbuild*.yaml infra/cloudbuild/ 2>/dev/null || true

# Move Docker artifacts (Dockerfiles at root go to infra or legacy if loose)
# We will assume loose Dockerfiles belong to the 'monorepo' context or need sorting
mv Dockerfile* infra/ 2>/dev/null || true
mv docker-compose*.yaml infra/ 2>/dev/null || true
mv skaffold.yaml infra/ 2>/dev/null || true

# Move specific config folders
mv configs config infra/ 2>/dev/null || true

# ==============================================================================
# 4. TOOLS & SCRIPTS MIGRATION (The "Tools" Bucket)
# ==============================================================================
echo "🛠️  Migrating Tools & Scripts..."

# Move known script directories
TOOLS_DIRS=(
    "bin"
    "ci"
    "scripts"
    "mcp"
    "mcp-validation"
    "load_testing"
    "k6"
    "benchmark"
    "benchmarks"
    "utils"
    "experiments"
    "pso_experiments"
    "notebooks"
)

for dir in "${TOOLS_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        mv "$dir" tools/
    fi
done

# SWEEP: Move ALL loose .py, .sh, .js, .go files at root to tools/scripts
# Exception: setup.py, manage.py might be needed? No, purely Antigravity now.
echo "   -> Sweeping loose scripts to tools/scripts/..."
mv *.py tools/scripts/ 2>/dev/null || true
mv *.sh tools/scripts/ 2>/dev/null || true
mv *.js tools/scripts/ 2>/dev/null || true
mv *.go tools/scripts/ 2>/dev/null || true

# Restore our transfer script itself if it got moved (self-preservation)
if [ -f "tools/scripts/total_transfer.sh" ]; then
    mv tools/scripts/total_transfer.sh .
fi

# ==============================================================================
# 5. DOCUMENTATION & ARCHIVES (The "Docs" Bucket)
# ==============================================================================
echo "📚 Migrating Documentation & Archives..."

DOCS_DIRS=(
    "doc"
    "docs"
    "whiteboard"
    "transcripts"
    "rubrics"
    "artifacts"
    "prompts"
    "templates"
    "mission"
    "spec"
)

for dir in "${DOCS_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        # Merge if exists
        cp -R "$dir/"* docs/ 2>/dev/null || true && rm -rf "$dir"
    fi
done

# Move loose markdown/text files
mv *.md docs/ 2>/dev/null || true
mv *.txt docs/ 2>/dev/null || true
mv *.json docs/archive/ 2>/dev/null || true # Loose JSONs are usually data or trash

# Restore README.md and crucial configs
if [ -f "docs/README.md" ]; then mv docs/README.md .; fi
if [ -f "docs/archive/package.json" ]; then mv docs/archive/package.json .; fi
if [ -f "docs/archive/pyproject.toml" ]; then mv docs/archive/pyproject.toml .; fi
if [ -f "docs/archive/uv.lock" ]; then mv docs/archive/uv.lock .; fi

# ==============================================================================
# 6. LEGACY & TRASH MIGRATION (The "Cleanup")
# ==============================================================================
echo "🗑️  Sweeping the rest..."

# Move known legacy/archive folders
LEGACY_DIRS=(
    "_archive"
    "Salvaged_Intel"
    "Legacy_Archives"
    "imported_repos"
    "imported_universe"
    "imported_drive_texts"
    "external_repos"
    "external_sdks"
    "third_party" # Google style: third_party should ideally be properly managed, but moving for now
    "y"
)

for dir in "${LEGACY_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        mv "$dir" tools/legacy/
    fi
done

# The "Catch-All": Anything remaining at root that isn't our core structure
# We exclude the folders we just created.
for item in *; do
    if [[ "$item" != "apps" && "$item" != "libs" && "$item" != "infra" && "$item" != "tools" && "$item" != "docs" && "$item" != "data" && "$item" != "total_transfer.sh" && "$item" != "pyproject.toml" && "$item" != "uv.lock" && "$item" != "README.md" && "$item" != ".gitignore" ]]; then
        echo "   -> Stashing loose item '$item' in tools/legacy/_root_stash"
        mkdir -p tools/legacy/_root_stash
        mv "$item" tools/legacy/_root_stash/
    fi
done

# ==============================================================================
# 7. ANTIGRAVITY CONFIGURATION
# ==============================================================================
echo "🔧 Regenerating Workspace Configurations..."

# Function to create pyproject.toml
create_config() {
    local dir=$1
    local name=$(basename "$dir")
    if [ ! -f "$dir/pyproject.toml" ]; then
        echo "   + Config: $name"
        cat > "$dir/pyproject.toml" <<EOF
[project]
name = "${name//-/_}" # sanitize name
version = "0.1.0"
description = "Auto-generated for $name"
dependencies = []
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
    fi
}

# Recursively find directories in apps/ and libs/ and give them configs
# (Only 1 level deep to avoid messing up internal structures)
find apps -maxdepth 1 -mindepth 1 -type d | while read dir; do create_config "$dir"; done
find libs -maxdepth 1 -mindepth 1 -type d | while read dir; do create_config "$dir"; done

# Enforce Root Config
cat > pyproject.toml <<EOF
[project]
name = "shadowtag-v2-monorepo"
version = "2.0.0"
description = "The Antigravity Monorepo"
requires-python = ">=3.11"
dependencies = [
    "ruff>=0.1.0",
    "pytest>=7.0.0"
]

[tool.uv.workspace]
members = ["apps/*", "libs/*"]

[tool.ruff]
line-length = 88
EOF

# ==============================================================================
# 8. FINAL SANITIZATION
# ==============================================================================
echo "🧹 Final Scrub..."

# Nuke all nested node_modules, venvs, and caches found anywhere
find . -name "node_modules" -type d -prune -exec rm -rf {} +
find . -name ".venv" -type d -prune -exec rm -rf {} +
find . -name "__pycache__" -type d -prune -exec rm -rf {} +
find . -name ".DS_Store" -delete

# Reset .gitignore
cat > .gitignore <<EOF
# Root
.venv/
__pycache__/
*.pyc
node_modules/
.DS_Store
.env
dist/
build/

# Artifacts
coverage/
.scannerwork/
.sonar/
test-results/

# Editor
.idea/
.vscode/
!/.vscode/settings.json
!/.vscode/tasks.json

# Legacy Stash (Optional: Ignore the stash so it doesn't clutter git status?)
# tools/legacy/
EOF

echo "🔋 Powering up Antigravity Engine..."
uv sync

echo "✅ TOTAL TRANSFER COMPLETE."
echo "   Your root directory should now be pristine."
