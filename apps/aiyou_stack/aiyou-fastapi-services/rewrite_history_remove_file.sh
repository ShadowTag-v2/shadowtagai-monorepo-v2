#!/bin/bash
set -e

# ==============================================================================
# DANGEROUS: REWRITE REPOSITORY HISTORY TO REMOVE LARGE FILES
# ==============================================================================
# This script uses `git-filter-repo` to permanently remove files from all
# branches and tags in the repository's history.
#
# It automatically downloads `git-filter-repo` locally if not found in PATH.
# ==============================================================================

REPO_URL=$1
if [ -z "$REPO_URL" ]; then
  # Auto-detect remote if not provided
  REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
  if [ -z "$REPO_URL" ]; then
      echo "❌ ERROR: You must provide the repository's remote URL as the first argument, or be in a repo with a remote."
      echo "Usage: ./rewrite_history_remove_file.sh <git-remote-url>"
      exit 1
  fi
  echo ">>> Auto-detected remote: $REPO_URL"
fi

REPO_NAME=$(basename -s .git "$REPO_URL")
CLONE_DIR="${REPO_NAME}_clean.git"

# 1. Setup git-filter-repo
if ! command -v git-filter-repo &> /dev/null; then
    if [ ! -f git-filter-repo ]; then
        echo ">>> ⬇️  Downloading git-filter-repo locally..."
        curl -sS -O https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo
        chmod +x git-filter-repo
    fi
    # Use python to run it to avoid shebang issues
    FILTER_CMD="python3 $(pwd)/git-filter-repo"
else
    FILTER_CMD="git-filter-repo"
fi

echo ">>> 🛡️  Step 1: Creating a fresh mirror clone in './${CLONE_DIR}'..."
if [ -d "$CLONE_DIR" ]; then
    echo "Directory $CLONE_DIR already exists. Removing it..."
    rm -rf "$CLONE_DIR"
fi
git clone --mirror "$REPO_URL" "$CLONE_DIR"
cd "$CLONE_DIR"

echo ">>> 🧹 Step 2: Running git-filter-repo to remove files..."
# We need to run the command from inside the repo, but point to the script if it's outside
if [[ "$FILTER_CMD" == *"python3"* ]]; then
    # Point to the script in the parent directory
    $FILTER_CMD --path libs/pnkln_intelligence/knowledge_base/gucci_content_lake.jsonl --path pnkln_intelligence/knowledge_base/gucci_content_lake.jsonl --invert-paths --force
else
    $FILTER_CMD --path libs/pnkln_intelligence/knowledge_base/gucci_content_lake.jsonl --path pnkln_intelligence/knowledge_base/gucci_content_lake.jsonl --invert-paths --force
fi

echo ">>> ✅ Local history rewrite complete."
echo ""
echo ">>> 🚨 MANUAL ACTION REQUIRED 🚨"
echo "------------------------------------------------------------------"
echo "Review the new history. If it is correct, run the following commands"
echo "to PERMANENTLY overwrite the remote repository's history:"
echo ""
echo "  cd ${CLONE_DIR}"
echo "  git push origin --force --all"
echo "  git push origin --force --tags"
echo ""
echo "After pushing, notify all collaborators to delete and re-clone the repo."
echo "------------------------------------------------------------------"
