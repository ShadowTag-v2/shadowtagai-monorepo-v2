#!/usr/bin/env bash
# Monorepo state audit — timeout-guarded to prevent hangs in CI/agent shells.
set -euo pipefail

# Configurable timeout (default 30s per command)
AUDIT_TIMEOUT="${AUDIT_TIMEOUT:-30}"

ROOT="${MONOREPO_ROOT:-/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball}"
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
  "apps/ShadowTag-v2_ecosystem/raw_ingest" \
  "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services" \
  "apps/ShadowTag-v2_stack/cosmic-crab-payload"
do
  if [ -e "$p" ]; then
    echo "present: $p"
  else
    echo "missing: $p"
  fi
done
echo

echo "== 3. Denied-zone residue in live tree =="
timeout "${AUDIT_TIMEOUT}" find apps libs -maxdepth 5 -type d \( -name "node_modules" -o -name ".venv" -o -name ".git" \) -prune -o -type d \( \
  -name "_PRE_OMEGA_BACKUP_*" -o \
  -name "ShadowTag-Omega" -o \
  -name "arsenal_recovered" -o \
  -name "*-legacy" \
\) -print 2>/dev/null | sort || echo "(timed out or empty)"
echo

echo "== 4. Nested repo markers =="
timeout "${AUDIT_TIMEOUT}" find apps libs -maxdepth 5 -type d \( -name "node_modules" -o -name ".venv" \) -prune -o -type d -name ".git" -print 2>/dev/null | sort || echo "(timed out or empty)"
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
echo "Python files under apps: $(timeout "${AUDIT_TIMEOUT}" find apps -name node_modules -prune -o -name .venv -prune -o -type f -name '*.py' -print 2>/dev/null | wc -l | tr -d ' ')"
echo "Python files under libs: $(timeout "${AUDIT_TIMEOUT}" find libs -name node_modules -prune -o -name .venv -prune -o -type f -name '*.py' -print 2>/dev/null | wc -l | tr -d ' ')"
echo "BUILD.bazel files: $(timeout "${AUDIT_TIMEOUT}" find . -maxdepth 6 -name node_modules -prune -o -name .venv -prune -o -type f -name 'BUILD.bazel' -print 2>/dev/null | wc -l | tr -d ' ')"
echo "Proto files: $(timeout "${AUDIT_TIMEOUT}" find contracts proto -maxdepth 4 -name node_modules -prune -o -name .venv -prune -o -type f -name '*.proto' -print 2>/dev/null | wc -l | tr -d ' ')"
echo

echo "== 9. Git working tree =="
timeout "${AUDIT_TIMEOUT}" git status --short 2>/dev/null || echo "(git status timed out)"
