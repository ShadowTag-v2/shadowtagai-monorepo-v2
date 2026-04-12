#!/bin/bash
set -e
echo "🍏 [Phase 1] The Architect: Structuring 'shadowtag-omega-v2'..."

# 1. Establish the Foundation
mkdir -p apps libs/utils/src/libs/utils infra/k8s infra/terraform infra/cloudbuild tools/scripts tools/legacy docs/archive data

# 2. Migration List (Exhaustive based on your logs)
APPS=(
    "api" "voice_consensus" "transcode-service" "ungpt" "vertex-ai-agents"
    "yougle-ai" "universal-copilot" "shadowtagai" "judge6" "kosmos" "pnkln"
    "seatjudge-monorepo" "computer-use" "computer_use" "digital-freeway-api"
    "fast-api" "frontend" "hello-world" "humanfsd" "kosmos_agent" "kosmos_dev"
    "landing-pages" "media-edge" "nightly_intel_pipeline"
    "pinkln-intelligence-pipeline" "pinkln-reasoning-engine" "pnkln-framework"
    "shadowtag_core" "shadowtag_v2" "services" "agent0" "antigravity-go"
)

echo "📦 Moving Applications..."
for app in "${APPS[@]}"; do
    if [ -d "$app" ]; then
        # Merge-move strategy to prevent data loss on collision
        if [ -d "apps/$app" ]; then
            echo "   -> Merging $app..."
            cp -R "$app/"* "apps/$app/" 2>/dev/null || true
            rm -rf "$app"
        else
            mv "$app" apps/
        fi
    fi
done

# 3. Promote Shared Libraries (The "Nerves")
if [ -d "utils" ]; then
    echo "🧠 Promoting 'utils' to 'libs/utils'..."
    # We move contents deeper to support 'src/libs/utils' layout if preferred, 
    # or simple flat layout. Let's stick to flat for Python simplicity unless src-layout needed.
    # Moving to libs/utils directly for simpler import 'from libs import utils'
    mv utils libs/
fi

# 4. Infrastructure Consolidation
echo "🏗️  Consolidating Infrastructure..."
# K8s
if [ -d "k8s" ]; then mv k8s/* infra/k8s/ 2>/dev/null && rm -d k8s; fi
# Terraform
mv *.tf .terraform* infra/terraform/ 2>/dev/null || true
mv main.tf infra/terraform/ 2>/dev/null || true
# Cloud Build
mv cloudbuild*.yaml infra/cloudbuild/ 2>/dev/null || true
# Containers
mv Dockerfile* infra/ 2>/dev/null || true
mv docker-compose*.yaml infra/ 2>/dev/null || true
mv skaffold.yaml infra/ 2>/dev/null || true
# Configs
mv configs config infra/ 2>/dev/null || true

# 5. Tooling & Scripts
echo "🛠️  Sweeping Tools..."
TOOLS_DIRS=("bin" "ci" "scripts" "mcp" "mcp-validation" "load_testing" "k6" "benchmark" "benchmarks" "experiments" "pso_experiments" "notebooks")
for dir in "${TOOLS_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        if [ -d "tools/$dir" ]; then
            cp -R "$dir/"* "tools/$dir/" 2>/dev/null || true
            rm -rf "$dir"
        else
            mv "$dir" tools/
        fi
    fi
done
# Loose Scripts
mv *.py tools/scripts/ 2>/dev/null || true
mv *.sh tools/scripts/ 2>/dev/null || true
mv *.js tools/scripts/ 2>/dev/null || true
mv *.go tools/scripts/ 2>/dev/null || true

# 6. Docs & Legacy (The Archive)
echo "📚 Archiving..."
DOCS_DIRS=("doc" "docs" "whiteboard" "transcripts" "rubrics" "artifacts" "prompts" "templates" "mission" "spec")
for dir in "${DOCS_DIRS[@]}"; do
    if [ -d "$dir" ]; then cp -R "$dir/"* docs/ 2>/dev/null || true && rm -rf "$dir"; fi
done

LEGACY_DIRS=("_archive" "Salvaged_Intel" "Legacy_Archives" "imported_repos" "imported_universe" "imported_drive_texts" "external_repos" "external_sdks" "third_party" "y")
for dir in "${LEGACY_DIRS[@]}"; do
    if [ -d "$dir" ]; then mv "$dir" tools/legacy/; fi
done

mv *.md docs/ 2>/dev/null || true
mv *.txt docs/ 2>/dev/null || true
mv *.json docs/archive/ 2>/dev/null || true

# Restore Vital Files
if [ -f "docs/README.md" ]; then mv docs/README.md .; fi
if [ -f "tools/scripts/1_architect.sh" ]; then mv tools/scripts/1_architect.sh .; fi

# 7. The Final Polish (Root Cleanup)
mkdir -p tools/legacy/_root_stash
for item in *; do
    if [[ "$item" != "apps" && "$item" != "libs" && "$item" != "infra" && "$item" != "tools" && "$item" != "docs" && "$item" != "data" && "$item" != "pyproject.toml" && "$item" != "uv.lock" && "$item" != "README.md" && "$item" != ".gitignore" && "$item" != "1_architect.sh" ]]; then
        mv "$item" tools/legacy/_root_stash/
    fi
done

echo "✅ [Phase 1] Architecture Established."
