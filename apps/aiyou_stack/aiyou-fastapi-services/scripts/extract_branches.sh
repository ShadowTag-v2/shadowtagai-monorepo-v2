#!/bin/bash
# Extract ONLY changed files from each branch (diff from main)
set +e

DEMO_REPO="/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/external_repos/ehanc69/ShadowTag-v2-fastapi-services-demo"
MONOREPO="/Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2"
BRANCHES_DIR="$MONOREPO/branches"
export PATH="/opt/homebrew/bin:/usr/bin:/usr/local/bin:$PATH"

mkdir -p "$BRANCHES_DIR"

cd "$DEMO_REPO"

# Ensure we have main
git checkout main --quiet 2>/dev/null || git checkout origin/main --quiet 2>/dev/null

# Get all remote branches (excluding HEAD and main)
BRANCHES=$(git branch -r | grep -v -E 'HEAD|main$' | sed 's/origin\///')

COUNT=0
TOTAL=$(echo "$BRANCHES" | wc -l | tr -d ' ')
SUCCESS=0

for BRANCH in $BRANCHES; do
  COUNT=$((COUNT + 1))

  # Clean branch name for directory
  BRANCH_DIR=$(echo "$BRANCH" | tr '/' '_')
  TARGET="$BRANCHES_DIR/$BRANCH_DIR"

  if [ -d "$TARGET" ]; then
    echo "[$COUNT/$TOTAL] SKIP: $BRANCH_DIR (exists)"
    continue
  fi

  # Get list of changed files in this branch vs main
  CHANGED_FILES=$(git diff --name-only origin/main...origin/$BRANCH 2>/dev/null)

  if [ -z "$CHANGED_FILES" ]; then
    echo "[$COUNT/$TOTAL] SKIP: $BRANCH (no changes)"
    continue
  fi

  FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
  echo "[$COUNT/$TOTAL] $BRANCH ($FILE_COUNT files)"

  mkdir -p "$TARGET"

  # Checkout branch and copy only changed files
  git checkout "origin/$BRANCH" --quiet 2>/dev/null || continue

  for FILE in $CHANGED_FILES; do
    if [ -f "$FILE" ]; then
      DIR=$(dirname "$TARGET/$FILE")
      mkdir -p "$DIR"
      cp "$FILE" "$TARGET/$FILE" 2>/dev/null
    fi
  done

  # Create manifest
  echo "$CHANGED_FILES" > "$TARGET/_MANIFEST.txt"
  SUCCESS=$((SUCCESS + 1))
done

# Return to main
git checkout main --quiet 2>/dev/null || true

echo ""
echo "=== EXTRACTION COMPLETE ==="
echo "Total branches: $TOTAL"
echo "Extracted: $SUCCESS"
echo "Location: $BRANCHES_DIR"
