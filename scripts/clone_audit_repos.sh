#!/bin/bash
set -e

mkdir -p external_repos/claude_audit_repos
cd external_repos/claude_audit_repos

REPOS=(
  "https://github.com/affaan-m/everything-claude-code.git"
  "https://github.com/Piebald-AI/claude-code-system-prompts.git"
  "https://github.com/sickn33/antigravity-awesome-skills.git"
  "https://github.com/study8677/antigravity-workspace-template.git"
  "https://github.com/guanyang/antigravity-skills.git"
  "https://github.com/harikrishna8121999/antigravity-workflows.git"
)

echo "Starting safe clone of external audit repositories..."

for repo in "${REPOS[@]}"; do
  # Extract the folder name from the git URL
  FOLDER_NAME=$(basename "$repo" .git)
  
  if [ -d "$FOLDER_NAME" ]; then
    echo "Directory $FOLDER_NAME already exists, skipping clone."
  else
    git clone "$repo" || echo "Warning: failed to clone $repo"
  fi
done

echo "Safe cloning complete. Repositories isolated in external_repos/claude_audit_repos/"
