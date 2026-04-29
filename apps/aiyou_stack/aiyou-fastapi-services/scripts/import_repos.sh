#!/bin/bash
# Import all ehanc69 owned repos into the ShadowTag-v2 monorepo
# Each repo goes under repos/<repo-name>/ as a subtree (squashed)
set +e  # Don't exit on error, log and continue

MONOREPO="/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2"
CLONE_DIR="/tmp/ehanc69_clones"
LOG_FILE="$MONOREPO/scripts/import_repos.log"
FAILED_FILE="$MONOREPO/scripts/import_failed.log"

export PATH="/opt/homebrew/bin:/usr/bin:/usr/local/bin:$PATH"
export GIT_LFS_SKIP_SMUDGE=1

mkdir -p "$CLONE_DIR"
echo "" > "$LOG_FILE"
echo "" > "$FAILED_FILE"

cd "$MONOREPO"

# Skip these repos (already the monorepo itself, or templates)
SKIP="ShadowTag-v2 ShadowTag-v2jr-template-2"

# All owned repos
REPOS=(
  erik-hancock-llm-memory
  shadowtagai-v1
  shadowtag_v2
  kosmos
  Cor.Claude_Code_6
  codepmcs
  antigravity-go
  pnkln
  ShadowTag-v2-core
  ShadowTag-v2-api
  ShadowTag-v2-frontend
  ShadowTag-v2-clients
  ShadowTag-v2-mlops
  ShadowTag-v2-data-contracts
  ShadowTag-v2-infra
  ShadowTag-v2-devops
  ShadowTag-v2-observability
  ShadowTag-v2-sre
  ShadowTag-v2-security
  ShadowTag-v2-sops
  ShadowTag-v2-docs
  ShadowTag-v2-objections-decisions
  ShadowTag-v2-rollup
  ShadowTag-v2-policy
  Pipeline
  ShadowTag-v2-examples
  ShadowTag-v2-backend
  core
  ShadowTag-v2-evals
  ShadowTag-v2-governance
  ShadowTag-v2-ui-kit
  ShadowTag-v2-offline-appliance
  ShadowTag-v2-risk-engine
  ShadowTag-v2-indexer
  ShadowTag-v2-codesmith
  ShadowTag-v2-prompts
  security
  sre
  observability
  mlops
  docs
  prompts
  infra
  fastapi-services
  ShadowTag-v2-exec
  ShadowTag-v2-ml
  ShadowTag-v2-data
  ShadowTag-v2-risk
  ShadowTag-v2-ci
  ShadowTag-v2
)

TOTAL=${#REPOS[@]}
COUNT=0
SUCCESS=0
FAIL=0

for REPO in "${REPOS[@]}"; do
  COUNT=$((COUNT + 1))
  echo "[$COUNT/$TOTAL] Processing $REPO..."

  # Check if already imported
  if [ -d "$MONOREPO/repos/$REPO" ]; then
    echo "  SKIP: repos/$REPO already exists" | tee -a "$LOG_FILE"
    continue
  fi

  # Clone (shallow, treeless, skip LFS)
  CLONE_PATH="$CLONE_DIR/$REPO"
  if [ ! -d "$CLONE_PATH" ]; then
    echo "  Cloning..."
    if ! git clone --depth 1 --filter=tree:0 --single-branch \
        "https://github.com/ehanc69/$REPO.git" "$CLONE_PATH" 2>&1; then
      echo "  FAIL: Clone failed for $REPO" | tee -a "$FAILED_FILE"
      FAIL=$((FAIL + 1))
      continue
    fi
  fi

  # Get default branch
  DEFAULT_BRANCH=$(cd "$CLONE_PATH" && git rev-parse --abbrev-ref HEAD)

  # Add as remote and fetch
  REMOTE_NAME="import-$REPO"
  git remote remove "$REMOTE_NAME" 2>/dev/null || true
  git remote add "$REMOTE_NAME" "$CLONE_PATH"
  git fetch "$REMOTE_NAME" "$DEFAULT_BRANCH" --depth=1 2>&1

  # Subtree add (squashed - no history bloat)
  if git subtree add --prefix="repos/$REPO" "$REMOTE_NAME/$DEFAULT_BRANCH" --squash -m "Import $REPO from ehanc69/$REPO" 2>&1; then
    echo "  OK: Imported to repos/$REPO" | tee -a "$LOG_FILE"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "  FAIL: Subtree add failed for $REPO" | tee -a "$FAILED_FILE"
    FAIL=$((FAIL + 1))
  fi

  # Clean up remote
  git remote remove "$REMOTE_NAME" 2>/dev/null || true

done

echo ""
echo "=== IMPORT COMPLETE ==="
echo "Total: $TOTAL | Success: $SUCCESS | Failed: $FAIL | Skipped: $((TOTAL - SUCCESS - FAIL))"
echo "Log: $LOG_FILE"
echo "Failures: $FAILED_FILE"
