#!/bin/bash
# fork-all-antigravity.sh
# Mass fork all repositories listed in config/antigravity_repos.json

set -euo pipefail

# Configuration
CONFIG_FILE="config/antigravity_repos.json"
GH_USER="${GH_USER:-$(gh api user -q .login 2>/dev/null || echo '')}"

if [[ -z "$GH_USER" ]]; then
  echo "ERROR: Not authenticated with GitHub CLI. Run 'gh auth login' first."
  exit 1
fi

echo "🚀 Starting Mass Fork Operation for User: $GH_USER"

# Check if config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "ERROR: Config file $CONFIG_FILE not found!"
  exit 1
fi

# Load repos from JSON
REPOS=$(jq -r '.[]' "$CONFIG_FILE")
TOTAL_REPOS=$(echo "$REPOS" | wc -l | xargs)
CURRENT=0

echo "📋 Found $TOTAL_REPOS repositories to process."

for repo in $REPOS; do
  CURRENT=$((CURRENT + 1))
  repo_name=$(basename "$repo")

  echo "[$CURRENT/$TOTAL_REPOS] checking $repo..."

  # Check if we already have it
  if gh repo view "$GH_USER/$repo_name" &> /dev/null; then
    echo "  ✅ Already exists: $GH_USER/$repo_name"
  else
    echo "  🍴 Forking $repo -> $GH_USER/$repo_name..."
    # Fork without cloning, suppress output unless error
    if gh repo fork "$repo" --clone=false --default-branch-only 2>&1 | grep -v "already exists"; then
       echo "  ✨ Fork initiated."
       # Rate limit protection
       sleep 2
    else
       echo "  ❌ Failed to fork $repo (or it does not exist/is private)"
    fi
  fi
done

echo "🎉 Mass Fork Operation Complete!"
||||||| merged common ancestors
