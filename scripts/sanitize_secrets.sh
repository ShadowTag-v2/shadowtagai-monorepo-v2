#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "$ROOT"

REPORT="secrets_report.json"
PATHS="secret_paths.txt"

echo "Running gitleaks detection..."
gitleaks detect --no-git -f json -r "$REPORT" || true

if [ -f "$REPORT" ]; then
    jq -r '.[].File' "$REPORT" | sort -u > "$PATHS"
else
    touch "$PATHS"
fi

# Guarantee master omitted boundaries are secure
echo "reference/" >> .gitignore
echo "apps/" >> .gitignore

# Prevent future staging
cat "$PATHS" >> .gitignore
sort -u .gitignore -o .tmp_gitignore
mv .tmp_gitignore .gitignore

# Remove already tracked files from index, but keep them locally
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  if git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then
    git rm --cached -- "$f" || true
  fi
done < "$PATHS"

echo "Sanitized paths listed in $PATHS"
echo "Review git diff --cached and amend the blocked commit before resuming push."
