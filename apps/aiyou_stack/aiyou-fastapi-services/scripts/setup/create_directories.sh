#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# ShadowTag-v2 Cognitive Stack - Directory Structure Creator
# =============================================================================
#
# Creates the complete directory structure for the ShadowTag-v2 Cognitive Stack v5
#
# Usage:
#   ./scripts/setup/create_directories.sh
#
# Reference: gkc Cor.71
# =============================================================================

echo "==================================================================="
echo "  ShadowTag-v2 Cognitive Stack - Directory Structure Creation"
echo "==================================================================="
echo ""

# Define directory structure
DIRECTORIES=(
    # Source code
    "src/models/bdh"
    "src/models/diffusion"
    "src/models/moe_cl"
    "src/models/qwen3/vl"
    "src/models/qwen3/reranker"
    "src/models/xlstm"

    "src/reasoning/rot"

    "src/inference/roe"
    "src/inference/test_time"

    "src/training/rlp"
    "src/training/set_rl"

    "src/retrieval/reranker"
    "src/retrieval/late_interaction"

    "src/validation/hallucination"

    "src/api/routes"
    "src/api/middleware"

    # Infrastructure
    "infrastructure/lambda/document_parser"
    "infrastructure/lambda/video_extractor"
    "infrastructure/database/postgres/migrations"
    "infrastructure/database/redis"
    "infrastructure/database/mongodb/schemas"
    "infrastructure/moe_service"
    "infrastructure/terraform"
    "infrastructure/monitoring"
    "infrastructure/security"

    # Scripts
    "scripts/pipeline"
    "scripts/training"
    "scripts/deployment"
    "scripts/tasks"
    "scripts/chaos"

    # Tests
    "tests/unit"
    "tests/integration"
    "tests/benchmarks"

    # Configs
    "configs"

    # Docs
    "docs/architecture"
    "docs/api"
    "docs/deployment"
    "docs/badges"

    # Data
    "data/processed"
    "data/eval_sets"
    "data/raw"

    # Models
    "models/cache"
    "models/checkpoints"

    # Adapters
    "adapters"

    # Logs
    "logs/training"
    "logs/inference"
    "logs/tasks"

    # Reports
    "reports/training"
    "reports/validation"

    # Backups
    ".backups"

    # Cursor (already created, but ensure it exists)
    ".cursor/MEGA_ROLLUP"
    ".cursor/tasks"
    ".cursor/guardrails"
)

# Create directories
CREATED=0
SKIPPED=0

for dir in "${DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
        echo "⏭️  $dir (exists)"
        ((SKIPPED++))
    else
        mkdir -p "$dir"
        echo "✅ $dir"
        ((CREATED++))
    fi
done

echo ""
echo "==================================================================="
echo "  Summary"
echo "==================================================================="
echo "  ✅ Created: $CREATED directories"
echo "  ⏭️  Skipped: $SKIPPED directories (already exist)"
echo "==================================================================="
echo ""
echo "🎉 Directory structure ready!"
echo ""
echo "💡 Next steps:"
echo "   1. Run: ./scripts/setup/install_extensions.sh"
echo "   2. Run: npm install"
echo "   3. Run: pip install -r requirements.txt"
echo ""
