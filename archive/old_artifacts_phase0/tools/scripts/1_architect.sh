#!/bin/bash
set -e
echo "[Phase 1] The Architect: Structuring 'shadowtag-omega-v2'..."

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# 1. Establish the Foundation
mkdir -p apps libs/utils infra/k8s infra/terraform infra/cloudbuild tools/scripts tools/legacy docs/archive data

# 2. Migration List
APPS=(
    "api" "voice_consensus" "transcode-service" "ungpt" "vertex-ai-agents"
    "yougle-ai" "universal-copilot" "shadowtagai" "judge6" "kosmos" "pnkln"
    "seatjudge-monorepo" "computer-use" "computer_use" "digital-freeway-api"
    "fast-api" "frontend" "hello-world" "humanfsd" "kosmos_agent" "kosmos_dev"
    "landing-pages" "media-edge" "nightly_intel_pipeline"
    "pinkln-intelligence-pipeline" "pinkln-reasoning-engine" "pnkln-framework"
    "shadowtag_core" "shadowtag_v2" "services" "agent0" "antigravity-go"
)

echo "Moving Applications..."
for app in "${APPS[@]}"; do
    if [ -d "$app" ]; then
        if [ -d "apps/$app" ]; then
            echo "   -> Merging $app..."
            cp -R "$app/"* "apps/$app/" 2>/dev/null || true
            rm -rf "$app"
        else
            mv "$app" apps/
        fi
    fi
done

# 3. Promote Shared Libraries
if [ -d "utils" ] && [ ! -d "libs/utils" ]; then
    echo "Promoting 'utils' to 'libs/utils'..."
    mv utils libs/
fi

# 4. Infrastructure Consolidation
echo "Consolidating Infrastructure..."
[ -d "k8s" ] && { mv k8s/* infra/k8s/ 2>/dev/null || true; rmdir k8s 2>/dev/null || true; }
mv *.tf infra/terraform/ 2>/dev/null || true
mv cloudbuild*.yaml infra/cloudbuild/ 2>/dev/null || true
mv Dockerfile* infra/ 2>/dev/null || true
mv docker-compose*.y*ml infra/ 2>/dev/null || true
mv skaffold.yaml infra/ 2>/dev/null || true

# 5. Tooling & Scripts
echo "Sweeping Tools..."
for dir in bin ci mcp mcp-validation load_testing k6 benchmark benchmarks experiments pso_experiments notebooks; do
    [ -d "$dir" ] && mv "$dir" tools/
done

# 6. Docs & Legacy
echo "Archiving..."
for dir in whiteboard transcripts rubrics artifacts prompts templates mission spec; do
    if [ -d "$dir" ]; then
        cp -R "$dir/"* docs/ 2>/dev/null || true
        rm -rf "$dir"
    fi
done

for dir in _archive Salvaged_Intel Legacy_Archives imported_repos imported_universe imported_drive_texts external_repos; do
    [ -d "$dir" ] && mv "$dir" tools/legacy/
done

# 7. Root Cleanup — stash unknown items
mkdir -p tools/legacy/_root_stash
for item in *; do
    case "$item" in
        apps|libs|infra|tools|docs|data|third_party|pyproject.toml|uv.lock|README.md|.gitignore|ruff.toml|biome.json|.aiignore|pyrightconfig.json|REVIEW.md|AGENTS.md|CLAUDE.md|WORKSPACE|BUILD.bazel|.bazelrc|.bazelversion) ;;
        *) [ -e "$item" ] && mv "$item" tools/legacy/_root_stash/ 2>/dev/null || true ;;
    esac
done

echo "[Phase 1] Architecture Established."
