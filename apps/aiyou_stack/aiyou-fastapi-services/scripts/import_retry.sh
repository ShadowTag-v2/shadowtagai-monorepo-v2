#!/bin/bash
# Retry failed imports
set +e
MONOREPO="/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2"
CLONE_DIR="/tmp/ehanc69_clones"
export PATH="/opt/homebrew/bin:/usr/bin:/usr/local/bin:$PATH"
export GIT_LFS_SKIP_SMUDGE=1

cd "$MONOREPO"

REPOS=(
  shadowtagai-v1
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
)
# Skip empty repos: ShadowTag-v2-prompts, ShadowTag-v2

TOTAL=${#REPOS[@]}
COUNT=0
SUCCESS=0

for REPO in "${REPOS[@]}"; do
  COUNT=$((COUNT + 1))
  echo "[$COUNT/$TOTAL] Retrying $REPO..."

  if [ -d "$MONOREPO/repos/$REPO" ]; then
    echo "  SKIP: already exists"
    continue
  fi

  CLONE_PATH="$CLONE_DIR/$REPO"
  if [ ! -d "$CLONE_PATH/.git" ]; then
    echo "  Re-cloning..."
    rm -rf "$CLONE_PATH"
    git clone --depth 1 --filter=tree:0 --single-branch \
      "https://github.com/ehanc69/$REPO.git" "$CLONE_PATH" 2>&1 || continue
  fi

  DEFAULT_BRANCH=$(cd "$CLONE_PATH" && git rev-parse --abbrev-ref HEAD 2>/dev/null)
  if [ -z "$DEFAULT_BRANCH" ] || [ "$DEFAULT_BRANCH" = "HEAD" ]; then
    echo "  SKIP: empty repo"
    continue
  fi

  REMOTE_NAME="import-$REPO"
  git remote remove "$REMOTE_NAME" 2>/dev/null || true
  git remote add "$REMOTE_NAME" "$CLONE_PATH"
  git fetch "$REMOTE_NAME" "$DEFAULT_BRANCH" --depth=1 2>&1

  if git subtree add --prefix="repos/$REPO" "$REMOTE_NAME/$DEFAULT_BRANCH" --squash \
    -m "Import $REPO from ehanc69/$REPO" 2>&1; then
    echo "  OK: Imported repos/$REPO"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "  FAIL: $REPO"
  fi

  git remote remove "$REMOTE_NAME" 2>/dev/null || true
done

echo ""
echo "=== RETRY COMPLETE: $SUCCESS/$TOTAL succeeded ==="
