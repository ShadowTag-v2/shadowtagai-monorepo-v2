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
