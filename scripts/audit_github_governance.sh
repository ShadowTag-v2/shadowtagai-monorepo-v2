#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "${ROOT}"

echo "== GitHub Governance Audit =="
echo

echo "== 1. Required repo files =="
for f in ".github/CODEOWNERS" ".github/workflows/main.yml"; do
  if [ -f "$f" ]; then
    echo "present: $f"
  else
    echo "missing: $f"
  fi
done
echo

echo "== 2. Workflow job names =="
if [ -f ".github/workflows/main.yml" ]; then
  grep -n '^  bazel-build:' .github/workflows/main.yml || echo "missing job: bazel-build"
  grep -n '^  bazel-test:' .github/workflows/main.yml || echo "missing job: bazel-test"
else
  echo "workflow file missing"
fi
echo

echo "== 3. CODEOWNERS quick view =="
if [ -f ".github/CODEOWNERS" ]; then
  sed -n '1,80p' .github/CODEOWNERS
else
  echo "CODEOWNERS missing"
fi
echo

echo "== 4. Git remote =="
git remote -v || true
echo

echo "== 5. Current branch =="
git branch --show-current || true
echo

echo "== 6. Recent commits =="
git log --oneline -n 10 || true
echo

echo "== 7. Guidance =="
echo "Manual GitHub checks still required in the web UI:"
echo "- main branch protection enabled"
echo "- PRs required"
echo "- at least 1 approval"
echo "- code owner review required"
echo "- required checks: bazel-build, bazel-test"
echo "- direct pushes blocked"
