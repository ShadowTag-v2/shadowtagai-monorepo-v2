#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

mkdir -p "${ROOT}/scripts"
cd "${ROOT}"

cat > scripts/audit_monorepo_state.sh <<'EOF'
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
  "apps/pnkln-stack_ecosystem/raw_ingest" \
  "apps/pnkln-stack_stack/pnkln-stack-fastapi-services" \
  "apps/pnkln-stack_stack/cosmic-crab-payload"
do
  if [ -e "$p" ]; then
    echo "present: $p"
  else
    echo "missing: $p"
  fi
done
echo

echo "== 3. Denied-zone residue in live tree =="
find apps libs -type d \( \
  -name "_PRE_OMEGA_BACKUP_*" -o \
  -name "ShadowTag-Omega" -o \
  -name "arsenal_recovered" -o \
  -name "*-legacy" \
\) 2>/dev/null | sort || true
echo

echo "== 4. Nested repo markers =="
find apps libs -type d -name ".git" 2>/dev/null | sort || true
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
echo "Python files under apps: $(find apps -type f -name '*.py' 2>/dev/null | wc -l | tr -d ' ')"
echo "Python files under libs: $(find libs -type f -name '*.py' 2>/dev/null | wc -l | tr -d ' ')"
echo "BUILD.bazel files: $(find . -type f -name 'BUILD.bazel' 2>/dev/null | wc -l | tr -d ' ')"
echo "Proto files: $(find contracts proto -type f -name '*.proto' 2>/dev/null | wc -l | tr -d ' ')"
echo

echo "== 9. Git working tree =="
git status --short || true
EOF
chmod +x scripts/audit_monorepo_state.sh

cat > scripts/audit_mcp_state.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
cd "${ROOT}"

echo "== MCP Stack Audit =="
echo

echo "== 1. Config files =="
for f in "docs/mcp-stack.md" "antigravity-mcp-config.json"; do
  if [ -f "$f" ]; then
    echo "present: $f"
  else
    echo "missing: $f"
  fi
done
echo

echo "== 2. Node / npm / Chrome =="
if command -v node >/dev/null 2>&1; then
  echo "node: $(node -v)"
else
  echo "node: MISSING"
fi

if command -v npm >/dev/null 2>&1; then
  echo "npm: $(npm -v)"
else
  echo "npm: MISSING"
fi

if [ -d "/Applications/Google Chrome.app" ]; then
  echo "chrome: present"
else
  echo "chrome: MISSING"
fi
echo

echo "== 3. MCP config enabled flags =="
if [ -f antigravity-mcp-config.json ]; then
  grep -n '"enabled"' antigravity-mcp-config.json || true
else
  echo "antigravity-mcp-config.json missing"
fi
echo

echo "== 4. Chrome remote debug port =="
if command -v curl >/dev/null 2>&1; then
  if curl -s http://127.0.0.1:9222/json/version >/dev/null 2>&1; then
    echo "chrome remote debug: reachable on 9222"
    curl -s http://127.0.0.1:9222/json/version | head -c 300; echo
  else
    echo "chrome remote debug: NOT reachable on 9222"
  fi
else
  echo "curl missing"
fi
echo

echo "== 5. chrome-devtools-mcp resolution =="
if command -v npx >/dev/null 2>&1; then
  if npx -y chrome-devtools-mcp@latest --help >/dev/null 2>&1; then
    echo "chrome-devtools-mcp: resolves"
  else
    echo "chrome-devtools-mcp: FAILED to resolve"
  fi
else
  echo "npx missing"
fi
echo

echo "== 6. Developer Knowledge token presence =="
if [ -n "${GOOGLE_OAUTH_ACCESS_TOKEN:-}" ]; then
  echo "GOOGLE_OAUTH_ACCESS_TOKEN: present in environment"
else
  echo "GOOGLE_OAUTH_ACCESS_TOKEN: NOT present"
fi
echo

echo "== 7. Known timeout-prone MCPs =="
for name in firebase-mcp-server mcp-toolbox-for-databases sequential-thinking; do
  echo "expected default state: disabled -> $name"
done
echo

echo "== 8. Recommended action =="
echo "Keep only chrome-devtools and google-developer-knowledge enabled by default until the timeout-prone MCPs are validated standalone."
EOF
chmod +x scripts/audit_mcp_state.sh

cat > scripts/audit_github_governance.sh <<'EOF'
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
EOF
chmod +x scripts/audit_github_governance.sh

echo
echo "Wrote:"
echo "  ${ROOT}/scripts/audit_monorepo_state.sh"
echo "  ${ROOT}/scripts/audit_mcp_state.sh"
echo "  ${ROOT}/scripts/audit_github_governance.sh"
echo
echo "Run:"
echo "  cd ${ROOT}"
echo "  ./scripts/audit_monorepo_state.sh"
echo "  ./scripts/audit_mcp_state.sh"
echo "  ./scripts/audit_github_governance.sh"
