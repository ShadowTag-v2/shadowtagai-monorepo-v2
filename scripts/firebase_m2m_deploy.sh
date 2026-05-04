#!/usr/bin/env bash
# Firebase M2M Headless Deploy
# Uses service account key from GCP Secret Manager — zero browser interaction.
# Usage: bash scripts/firebase_m2m_deploy.sh [site] [--all]
#
# Examples:
#   bash scripts/firebase_m2m_deploy.sh kovelai
#   bash scripts/firebase_m2m_deploy.sh shadowtagai
#   bash scripts/firebase_m2m_deploy.sh --all
#
# Prerequisites:
#   - .beads/firebase-sa.json exists (SA key from GCP Secret Manager)
#   - firebase-tools installed globally (npm i -g firebase-tools)
#   - SA has roles/firebase.admin on the project

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SA_KEY="$REPO_ROOT/.beads/firebase-sa.json"
PROJECT_ID="shadowtag-omega-v4"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Validate SA key exists
if [[ ! -f "$SA_KEY" ]]; then
    echo -e "${RED}✗ SA key not found at $SA_KEY${NC}"
    echo "  Fetch from Secret Manager:"
    echo "  gcloud secrets versions access latest --secret=firebase-deployer-sa-key --project=$PROJECT_ID > $SA_KEY"
    exit 1
fi

# Validate firebase CLI is installed
if ! command -v firebase &>/dev/null; then
    echo -e "${RED}✗ firebase-tools not installed${NC}"
    echo "  Install: npm i -g firebase-tools"
    exit 1
fi

deploy_site() {
    local site="$1"
    local config_dir=""

    case "$site" in
        kovelai)
            config_dir="$REPO_ROOT/apps/kovelai"
            ;;
        shadowtagai)
            config_dir="$REPO_ROOT"
            ;;
        *)
            echo -e "${RED}✗ Unknown site: $site${NC}"
            echo "  Valid sites: kovelai, shadowtagai"
            return 1
            ;;
    esac

    echo -e "${YELLOW}⟳ Deploying $site...${NC}"

    GOOGLE_APPLICATION_CREDENTIALS="$SA_KEY" \
    CI=true \
    firebase deploy \
        --only "hosting:$site" \
        --project="$PROJECT_ID" \
        --config="$config_dir/firebase.json" \
        2>&1

    echo -e "${GREEN}✔ $site deployed to https://$site.web.app${NC}"
}

# Parse args
if [[ "${1:-}" == "--all" ]]; then
    deploy_site "kovelai"
    echo ""
    deploy_site "shadowtagai"
elif [[ -n "${1:-}" ]]; then
    deploy_site "$1"
else
    echo "Usage: bash scripts/firebase_m2m_deploy.sh [kovelai|shadowtagai|--all]"
    exit 1
fi

echo ""
echo -e "${GREEN}═══ M2M Deploy Complete ═══${NC}"
echo "  Auth: Service Account (zero browser)"
echo "  SA: $(python3 -c "import json;print(json.load(open('$SA_KEY'))['client_email'])" 2>/dev/null || echo 'unknown')"
