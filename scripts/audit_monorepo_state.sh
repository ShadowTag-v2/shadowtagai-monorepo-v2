#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "${ROOT}"

echo "== Monorepo State Audit =="
echo "Root: ${ROOT}"
echo

echo "== 1. Canonical manifest =="
if [ -f monorepo_manifest.yaml ]; then
  echo "monorepo_manifest.yaml: present"
  echo "--- unresolved entries ---"
  if grep -n "status: unresolved" monorepo_manifest.yaml; then
    :
  else
    echo "none"
  fi
else
  echo "monorepo_manifest.yaml: MISSING"
fi
echo

echo "== 2. Canonical / non-canonical tree count =="
for p in \
  "archive" \
  "tools/legacy" \
  "docs/legacy_shadowtag_v2" \
  "apps/aiyou_ecosystem/raw_ingest" \
  "apps/aiyou_stack/aiyou-fastapi-services" \
  "apps/aiyou_stack/cosmic-crab-payload"
do
  if [ -e "$p" ]; then
    echo "present: $p"
  else
    echo "missing: $p"
  fi
done
echo

echo "== 3. Denied-zone residue in live tree =="
find apps libs -type d \( -name "node_modules" -o -name ".venv" -o -name ".git" \) -prune -o -type d \( \
  -name "_PRE_OMEGA_BACKUP_*" -o \
  -name "ShadowTag-Omega" -o \
  -name "arsenal_recovered" -o \
  -name "*-legacy" \
\) -print 2>/dev/null | sort || true
echo

echo "== 4. Nested repo markers =="
find apps libs -type d \( -name "node_modules" -o -name ".venv" \) -prune -o -type d -name ".git" -print 2>/dev/null | sort || true
echo

echo "== 5. Python config =="
if [ -f pyrightconfig.json ]; then
  echo "pyrightconfig.json: present"
  echo "--- include entries ---"
  grep -n '"include"' pyrightconfig.json || true
  echo "--- external_memory exclude ---"
  grep -n 'external_memory' pyrightconfig.json || true
  echo "--- external_repos exclude ---"
  grep -n 'external_repos' pyrightconfig.json || true
else
  echo "pyrightconfig.json: MISSING"
fi
echo

echo "== 6. Workspace files =="
for f in \
  ".vscode/settings.json" \
  "Monorepo-Uphillsnowball.code-workspace" \
  ".antigravity-system-prompt.txt" \
  "docs/monorepo-10x-checklist.md" \
  "docs/monorepo-weekly-scorecard.md" \
  "docs/monorepo-audit-template.md"
do
  if [ -f "$f" ]; then
    echo "present: $f"
  else
    echo "missing: $f"
  fi
done
echo

echo "== 7. third_party / contracts =="
for p in "third_party/README.md" "contracts/README.md"; do
  if [ -f "$p" ]; then
    echo "present: $p"
  else
    echo "missing: $p"
  fi
done
echo

echo "== 8. Quick repo stats =="
echo "Python files under apps: $(find apps -name node_modules -prune -o -name .venv -prune -o -type f -name '*.py' -print 2>/dev/null | wc -l | tr -d ' ')"
echo "Python files under libs: $(find libs -name node_modules -prune -o -name .venv -prune -o -type f -name '*.py' -print 2>/dev/null | wc -l | tr -d ' ')"
echo "BUILD.bazel files: $(find . -name node_modules -prune -o -name .venv -prune -o -type f -name 'BUILD.bazel' -print 2>/dev/null | wc -l | tr -d ' ')"
echo "Proto files: $(find contracts proto -name node_modules -prune -o -name .venv -prune -o -type f -name '*.proto' -print 2>/dev/null | wc -l | tr -d ' ')"
echo

echo "== 9. Git working tree =="
git status --short || true
