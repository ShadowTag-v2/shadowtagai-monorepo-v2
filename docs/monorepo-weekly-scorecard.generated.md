# Monorepo Weekly Scorecard

## Week of
`2026-04-09`

## Overall score
- Current week score: `65/100`
- Last week score: `__/100`
- Delta: `+/-__`

---

## Category scores

| Category | Weight | Score | Weighted score | Notes |
|---|---:|---:|---:|---|
| Canonical repo resolution | 20 | 14 | 14 | unresolved repos: 2 |
| Live tree cleanliness | 20 | 0 | 0 | denied-zone residue count: 8 |
| GitHub governance | 15 | 15 | 15 | CODEOWNERS=yes, workflow=yes |
| Bazel / CI reliability | 15 | 15 | 15 | bazel-build=yes, bazel-test=yes |
| third_party discipline | 10 | 10 | 10 | third_party/README.md=yes |
| Shared contracts | 10 | 5 | 5 | contracts doc=yes, proto files=0 |
| Workspace / tooling stability | 5 | 5 | 5 | workspace=yes, pyright=yes |
| MCP stack stability | 5 | 1 | 1 | chrome_mcp=no, token=no |

---

## Examples to audit this week
- Example canonical repo: apps/aiyou_stack/aiyou-fastapi-services
- Example unresolved repo count: 2
- Example denied-zone residue count: 8
- Example green bazel-build: yes
- Example green bazel-test: yes
- Example MCP fixed: chrome-devtools resolvable=no
- Example MCP still timing out: firebase-mcp-server / mcp-toolbox-for-databases / sequential-thinking remain manual-validation items

---

## Quick evidence snapshot

- monorepo_manifest.yaml: yes
- .github/CODEOWNERS: yes
- .github/workflows/main.yml: yes
- Monorepo-Uphillsnowball.code-workspace: yes
- pyrightconfig.json: yes
- third_party/README.md: yes
- contracts/README.md: yes
- Python files under apps: 42016
- Python files under libs: 531
- BUILD.bazel files: 1173
- Proto files: 0

---

## Executive summary
This scorecard was generated from current repo state rather than hand-written estimates.
The largest remaining blocker is unresolved canonicalization if unresolved repos remain, plus denied-zone residue if backup or legacy trees are still present.
GitHub governance is only partially measurable locally; web UI confirmation is still required for branch protection and required checks.
Next, resolve unresolved repos, remove denied-zone residue from live trees, and verify protected-main enforcement for bazel-build and bazel-test.
