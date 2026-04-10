<<<<<<< HEAD
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
=======
#!/bin/bash
# scripts/fork-all-antigravity.sh
# Mass fork script for all identified repos

set -e

CONFIG_FILE="config/antigravity_repos.json"
GITHUB_USER="ehanc69"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file not found: $CONFIG_FILE"
    exit 1
fi

# Read cleaned repos
REPOS=$(cat "$CONFIG_FILE" | sed 's/github.com\///')

echo "Starting mass fork of $(echo "$REPOS" | wc -l) repositories..."

count=0
for REPO in $REPOS; do
    # Check if we already have it (skip check to save API calls, gh repo fork handles it gracefully usually)
    # But to be safe and avoid "already exists" errors spamming, we can just try and ignore error.

    echo "Forking $REPO... ($count)"
    gh repo fork "$REPO" --clone=false --org "$GITHUB_USER" 2>/dev/null || echo "  - Skipped/Failed $REPO"

    count=$((count+1))
    # Rate limiting: 2 seconds sleep
    sleep 2

    # Optional: limit for testing
    # if [ $count -ge 10 ]; then break; fi
done

echo "Forking process finished."
>>>>>>> upstream/claude/gptram-integration-01
