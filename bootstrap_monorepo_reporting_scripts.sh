#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

mkdir -p "${ROOT}/scripts" "${ROOT}/docs"
cd "${ROOT}"

cat > scripts/fill_weekly_scorecard.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
OUT="${ROOT}/docs/monorepo-weekly-scorecard.generated.md"
DATE_STR="${1:-$(date +%F)}"

cd "${ROOT}"

count_unresolved() {
  if [ -f monorepo_manifest.yaml ]; then
    grep -c "status: unresolved" monorepo_manifest.yaml || true
  else
    echo 999
  fi
}

path_present() {
  [ -e "$1" ] && echo yes || echo no
}

count_denied_dirs() {
  find apps libs -type d \( \
    -name "_PRE_OMEGA_BACKUP_*" -o \
    -name "ShadowTag-Omega" -o \
    -name "arsenal_recovered" -o \
    -name "*-legacy" \
  \) 2>/dev/null | wc -l | tr -d ' '
}

workflow_has_job() {
  local job="$1"
  if [ -f .github/workflows/main.yml ] && grep -q "^  ${job}:" .github/workflows/main.yml; then
    echo yes
  else
    echo no
  fi
}

file_present() {
  [ -f "$1" ] && echo yes || echo no
}

python_count() {
  find "$1" -type f -name '*.py' 2>/dev/null | wc -l | tr -d ' '
}

build_count() {
  find . -type f -name 'BUILD.bazel' 2>/dev/null | wc -l | tr -d ' '
}

proto_count() {
  find contracts proto -type f -name '*.proto' 2>/dev/null | wc -l | tr -d ' '
}

NODE_PRESENT=no
NPM_PRESENT=no
CHROME_PRESENT=no
CHROME_MCP_PRESENT=no
TOKEN_PRESENT=no

command -v node >/dev/null 2>&1 && NODE_PRESENT=yes
command -v npm >/dev/null 2>&1 && NPM_PRESENT=yes
[ -d "/Applications/Google Chrome.app" ] && CHROME_PRESENT=yes
if command -v npx >/dev/null 2>&1 && npx -y chrome-devtools-mcp@latest --help >/dev/null 2>&1; then
  CHROME_MCP_PRESENT=yes
fi
[ -n "${GOOGLE_OAUTH_ACCESS_TOKEN:-}" ] && TOKEN_PRESENT=yes

UNRESOLVED="$(count_unresolved)"
DENIED_COUNT="$(count_denied_dirs)"
CODEOWNERS="$(file_present .github/CODEOWNERS)"
WORKFLOW="$(file_present .github/workflows/main.yml)"
BAZEL_BUILD_JOB="$(workflow_has_job bazel-build)"
BAZEL_TEST_JOB="$(workflow_has_job bazel-test)"
THIRD_PARTY_DOC="$(file_present third_party/README.md)"
CONTRACTS_DOC="$(file_present contracts/README.md)"
MANIFEST_DOC="$(file_present monorepo_manifest.yaml)"
WORKSPACE_DOC="$(file_present Monorepo-Uphillsnowball.code-workspace)"
PYRIGHT_DOC="$(file_present pyrightconfig.json)"

CANONICAL_SCORE=0
[ "$MANIFEST_DOC" = yes ] && CANONICAL_SCORE=$((CANONICAL_SCORE+8))
if [ "$UNRESOLVED" -eq 0 ]; then
  CANONICAL_SCORE=$((CANONICAL_SCORE+12))
elif [ "$UNRESOLVED" -le 2 ]; then
  CANONICAL_SCORE=$((CANONICAL_SCORE+6))
fi

CLEAN_SCORE=0
if [ "$DENIED_COUNT" -eq 0 ]; then
  CLEAN_SCORE=20
elif [ "$DENIED_COUNT" -le 5 ]; then
  CLEAN_SCORE=10
fi

GOV_SCORE=0
[ "$CODEOWNERS" = yes ] && GOV_SCORE=$((GOV_SCORE+5))
[ "$WORKFLOW" = yes ] && GOV_SCORE=$((GOV_SCORE+3))
[ "$BAZEL_BUILD_JOB" = yes ] && GOV_SCORE=$((GOV_SCORE+3))
[ "$BAZEL_TEST_JOB" = yes ] && GOV_SCORE=$((GOV_SCORE+4))

CI_SCORE=0
[ "$BAZEL_BUILD_JOB" = yes ] && CI_SCORE=$((CI_SCORE+7))
[ "$BAZEL_TEST_JOB" = yes ] && CI_SCORE=$((CI_SCORE+8))

THIRD_SCORE=0
[ "$THIRD_PARTY_DOC" = yes ] && THIRD_SCORE=10

CONTRACT_SCORE=0
[ "$CONTRACTS_DOC" = yes ] && CONTRACT_SCORE=5
if [ "$(proto_count)" -gt 0 ]; then
  CONTRACT_SCORE=10
fi

TOOL_SCORE=0
[ "$WORKSPACE_DOC" = yes ] && TOOL_SCORE=$((TOOL_SCORE+2))
[ "$PYRIGHT_DOC" = yes ] && TOOL_SCORE=$((TOOL_SCORE+2))
[ "$MANIFEST_DOC" = yes ] && TOOL_SCORE=$((TOOL_SCORE+1))

MCP_SCORE=0
[ "$NODE_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$NPM_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$CHROME_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$CHROME_MCP_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))
[ "$TOKEN_PRESENT" = yes ] && MCP_SCORE=$((MCP_SCORE+1))

TOTAL=$((CANONICAL_SCORE + CLEAN_SCORE + GOV_SCORE + CI_SCORE + THIRD_SCORE + CONTRACT_SCORE + TOOL_SCORE + MCP_SCORE))

cat > "${OUT}" <<REPORT
# Monorepo Weekly Scorecard

## Week of
\`${DATE_STR}\`

## Overall score
- Current week score: \`${TOTAL}/100\`
- Last week score: \`__/100\`
- Delta: \`+/-__\`

---

## Category scores

| Category | Weight | Score | Weighted score | Notes |
|---|---:|---:|---:|---|
| Canonical repo resolution | 20 | ${CANONICAL_SCORE} | ${CANONICAL_SCORE} | unresolved repos: ${UNRESOLVED} |
| Live tree cleanliness | 20 | ${CLEAN_SCORE} | ${CLEAN_SCORE} | denied-zone residue count: ${DENIED_COUNT} |
| GitHub governance | 15 | ${GOV_SCORE} | ${GOV_SCORE} | CODEOWNERS=${CODEOWNERS}, workflow=${WORKFLOW} |
| Bazel / CI reliability | 15 | ${CI_SCORE} | ${CI_SCORE} | bazel-build=${BAZEL_BUILD_JOB}, bazel-test=${BAZEL_TEST_JOB} |
| third_party discipline | 10 | ${THIRD_SCORE} | ${THIRD_SCORE} | third_party/README.md=${THIRD_PARTY_DOC} |
| Shared contracts | 10 | ${CONTRACT_SCORE} | ${CONTRACT_SCORE} | contracts doc=${CONTRACTS_DOC}, proto files=$(proto_count) |
| Workspace / tooling stability | 5 | ${TOOL_SCORE} | ${TOOL_SCORE} | workspace=${WORKSPACE_DOC}, pyright=${PYRIGHT_DOC} |
| MCP stack stability | 5 | ${MCP_SCORE} | ${MCP_SCORE} | chrome_mcp=${CHROME_MCP_PRESENT}, token=${TOKEN_PRESENT} |

---

## Examples to audit this week
- Example canonical repo: apps/pnkln-stack_stack/pnkln-stack-fastapi-services
- Example unresolved repo count: ${UNRESOLVED}
- Example denied-zone residue count: ${DENIED_COUNT}
- Example green bazel-build: ${BAZEL_BUILD_JOB}
- Example green bazel-test: ${BAZEL_TEST_JOB}
- Example MCP fixed: chrome-devtools resolvable=${CHROME_MCP_PRESENT}
- Example MCP still timing out: firebase-mcp-server / mcp-toolbox-for-databases / sequential-thinking remain manual-validation items

---

## Quick evidence snapshot

- monorepo_manifest.yaml: ${MANIFEST_DOC}
- .github/CODEOWNERS: ${CODEOWNERS}
- .github/workflows/main.yml: ${WORKFLOW}
- Monorepo-Uphillsnowball.code-workspace: ${WORKSPACE_DOC}
- pyrightconfig.json: ${PYRIGHT_DOC}
- third_party/README.md: ${THIRD_PARTY_DOC}
- contracts/README.md: ${CONTRACTS_DOC}
- Python files under apps: $(python_count apps)
- Python files under libs: $(python_count libs)
- BUILD.bazel files: $(build_count)
- Proto files: $(proto_count)

---

## Executive summary
This scorecard was generated from current repo state rather than hand-written estimates.
The largest remaining blocker is unresolved canonicalization if unresolved repos remain, plus denied-zone residue if backup or legacy trees are still present.
GitHub governance is only partially measurable locally; web UI confirmation is still required for branch protection and required checks.
Next, resolve unresolved repos, remove denied-zone residue from live trees, and verify protected-main enforcement for bazel-build and bazel-test.
REPORT

echo "Wrote ${OUT}"
EOF
chmod +x scripts/fill_weekly_scorecard.sh

cat > scripts/fill_audit_report.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
OUT="${ROOT}/docs/monorepo-audit.generated.md"
DATE_STR="${1:-$(date +%F)}"

cd "${ROOT}"

manifest_present=no
[ -f monorepo_manifest.yaml ] && manifest_present=yes
codeowners_present=no
[ -f .github/CODEOWNERS ] && codeowners_present=yes
workflow_present=no
[ -f .github/workflows/main.yml ] && workflow_present=yes
third_present=no
[ -f third_party/README.md ] && third_present=yes
contracts_present=no
[ -f contracts/README.md ] && contracts_present=yes

UNRESOLVED_LINES="$(grep -n 'status: unresolved' monorepo_manifest.yaml 2>/dev/null || true)"
DENIED_PATHS="$(find apps libs -type d \( -name '_PRE_OMEGA_BACKUP_*' -o -name 'ShadowTag-Omega' -o -name 'arsenal_recovered' -o -name '*-legacy' \) 2>/dev/null | sort || true)"
NESTED_GIT="$(find apps libs -type d -name '.git' 2>/dev/null | sort || true)"
PROTO_FILES="$(find contracts proto -type f -name '*.proto' 2>/dev/null | sort || true)"

cat > "${OUT}" <<REPORT
# Monorepo Audit Report

## Audit date
\`${DATE_STR}\`

## Auditor
Generated from local audit scripts

## Scope
Canonicalization, live tree cleanliness, GitHub governance scaffolding, build/CI scaffolding, third_party policy, contracts policy, workspace stability, and MCP stack scaffolding.

---

## 1. Canonical repo audit

### Manifest present
- \`${manifest_present}\`

### Unresolved entries
\`\`\`
${UNRESOLVED_LINES:-none}
\`\`\`

### Findings
- If unresolved entries remain, the monorepo is not yet fully canonical.
- Canonicalization must continue until no repo remains unresolved.

---

## 2. Live tree cleanliness audit

### Denied-zone residue in live trees
\`\`\`
${DENIED_PATHS:-none}
\`\`\`

### Nested repo markers
\`\`\`
${NESTED_GIT:-none}
\`\`\`

### Findings
- Any denied-zone residue above indicates live tree surgery is incomplete.
- Any nested .git markers under apps/libs indicate duplicate or nested repo risk.

---

## 3. GitHub governance audit

- CODEOWNERS present: \`${codeowners_present}\`
- Workflow present: \`${workflow_present}\`

### Notes
- Local files can confirm governance scaffolding exists.
- GitHub web UI is still required to confirm:
  - protected main
  - PR requirement
  - code owner review requirement
  - required checks: bazel-build, bazel-test

---

## 4. third_party audit

- third_party/README.md present: \`${third_present}\`

### Findings
- Presence of policy doc is only step one.
- Real 10/10 requires actual dependency centralization under \`third_party/\`.

---

## 5. Contracts audit

- contracts/README.md present: \`${contracts_present}\`

### Proto inventory
\`\`\`
${PROTO_FILES:-none}
\`\`\`

### Findings
- If no shared proto/schema files exist, the contract layer is still policy-only rather than operational.

---

## 6. Workspace / tooling audit

- Workspace file present: \`$([ -f Monorepo-Uphillsnowball.code-workspace ] && echo yes || echo no)\`
- Pyright config present: \`$([ -f pyrightconfig.json ] && echo yes || echo no)\`
- Antigravity prompt present: \`$([ -f .antigravity-system-prompt.txt ] && echo yes || echo no)\`

### Findings
- Tooling stabilization is present at the config layer.
- Runtime validation still matters for Python envs, pyright scanning, and workspace drift.

---

## 7. MCP stack audit

- MCP stack doc present: \`$([ -f docs/mcp-stack.md ] && echo yes || echo no)\`
- MCP config present: \`$([ -f antigravity-mcp-config.json ] && echo yes || echo no)\`

### Findings
- Stable-first MCP policy can be enforced from the repo now.
- Timeout-prone MCPs should remain disabled until standalone validation succeeds.

---

## Executive summary
This generated audit reflects the current local repo state, not aspirational docs alone.
The biggest blockers to 10/10 remain unresolved repos, denied-zone residue in live paths, and any missing GitHub enforcement in the web UI.
The repo now has the scaffolding to become a disciplined monorepo, but full completion still depends on canonicalization, cleanup, enforcement, and proof via successful refactors and stable CI.
REPORT

echo "Wrote ${OUT}"
EOF
chmod +x scripts/fill_audit_report.sh

echo
echo "Wrote:"
echo "  ${ROOT}/scripts/fill_weekly_scorecard.sh"
echo "  ${ROOT}/scripts/fill_audit_report.sh"
echo
echo "Run:"
echo "  cd ${ROOT}"
echo "  ./scripts/fill_weekly_scorecard.sh"
echo "  ./scripts/fill_audit_report.sh"
