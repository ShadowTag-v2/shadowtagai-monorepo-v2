#!/bin/bash
# 1. Resolve Git State (Commit -> Pull Rebase -> Push)
set -e

echo "🦑 [ShadowTag] Resolving Git State..."

# 1. Check for changes
if [[ -n $(git status -s) ]]; then
  echo "   Use 'git add .' and 'git commit' first."
  git add .
  git commit -m "chore(auto): tactical resolution $(date +%s)" || echo "   Nothing to commit."
fi

# 2. Rebase
echo "   Pulling & Rebasing..."
git pull --rebase origin main || echo "   Rebase conflict? Fix manualy."

# 3. Push
echo "   Pushing to Origin..."
git push origin main
echo "✅ Git State Resolved."
