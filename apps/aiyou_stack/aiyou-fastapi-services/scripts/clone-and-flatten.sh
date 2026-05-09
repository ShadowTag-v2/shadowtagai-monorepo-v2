#!/bin/bash
# clone-and-flatten.sh
# 1. Clone all repos from config/antigravity_repos.json (forked versions)
# 2. Flatten them into a single text format for LLM consumption

set -euo pipefail

# Configuration
CONFIG_FILE="config/antigravity_repos.json"
BASE_DIR="$HOME/antigravity-repos"
FLATTEN_DIR="$HOME/antigravity-knowledge"
GH_USER="${GH_USER:-$(gh api user -q .login 2>/dev/null || echo '')}"

if [[ -z "$GH_USER" ]]; then
  echo "ERROR: Not authenticated. Run 'gh auth login'."
  exit 1
fi

echo "🚀 Starting Clone & Flatten Operation"
echo "📂 Working Directory: $BASE_DIR"
echo "📄 Flatten Output: $FLATTEN_DIR"

mkdir -p "$BASE_DIR"
mkdir -p "$FLATTEN_DIR"

# Check config
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "ERROR: Config file $CONFIG_FILE not found!"
  exit 1
fi

REPOS=$(jq -r '.[]' "$CONFIG_FILE")

# 1. CLONE PHASE
echo "=== PHASE 1: CLONING ==="
for repo in $REPOS; do
  repo_name=$(basename "$repo")
  target_path="$BASE_DIR/$repo_name"

  if [[ -d "$target_path" ]]; then
    echo "  ✅ Pulling latest for $repo_name..."
    git -C "$target_path" pull --quiet || echo "    ⚠️ Pull failed (dirty tree?)"
  else
    echo "  ⬇️  Cloning $GH_USER/$repo_name..."
    # Try cloning from our fork first, fallback to upstream if strict fork check failed earlier
    if ! gh repo clone "$GH_USER/$repo_name" "$target_path" -- --quiet; then
        echo "    ⚠️ Fork clone failed, trying upstream $repo..."
        gh repo clone "$repo" "$target_path" -- --quiet || echo "    ❌ Failed to clone $repo_name"
    fi
  fi
done

# 2. FLATTEN PHASE
echo "=== PHASE 2: FLATTENING ==="
# We will use a python one-liner or helper script for this to be robust
# But for now, a simple find loop to create a combined file per repo

for repo in $REPOS; do
  repo_name=$(basename "$repo")
  src_dir="$BASE_DIR/$repo_name"
  out_file="$FLATTEN_DIR/$repo_name.txt"

  if [[ ! -d "$src_dir" ]]; then
    continue
  fi

  echo "  📄 Flattening $repo_name -> $out_file..."

  # Header
  echo "# REPOSITORY: $repo" > "$out_file"
  echo "# DATE: $(date)" >> "$out_file"
  echo "# CONTENT:" >> "$out_file"
  echo "" >> "$out_file"

  # Find text files (skip .git, binary, large files, etc)
  # Using fd or find
  if command -v fd &> /dev/null; then
    fd --type f --hidden --exclude .git --exclude node_modules --exclude '*.png' --exclude '*.jpg' --exclude '*.pyc' . "$src_dir" \
      --exec bash -c "echo '## FILE: {/}' >> '$out_file'; echo '\`\`\`' >> '$out_file'; cat '{}' >> '$out_file'; echo '\`\`\`' >> '$out_file'; echo '' >> '$out_file'"
  else
    find "$src_dir" -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -name '*.png' -not -name '*.jpg' -not -name '*.pyc' \
      -exec bash -c "echo '## FILE: {}' >> '$out_file'; echo '\`\`\`' >> '$out_file'; cat '{}' >> '$out_file'; echo '\`\`\`' >> '$out_file'; echo '' >> '$out_file'" \;
  fi

done

echo "🎉 Clone & Flatten Complete!"
echo "Files are available in $FLATTEN_DIR"
||||||| merged common ancestors
