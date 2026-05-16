# Monorepo Weekly Scorecard

## Week of
`2026-03-21`

## Overall score
- Current week score: `47/100`
- Last week score: `__/100`
- Delta: `+/-__`

---

## Category scores

| Category | Weight | Score | Weighted score | Notes |
|---|---:|---:|---:|---|
| Canonical repo resolution | 20 | 20 | 20 | unresolved repos: 0 |
| Live tree cleanliness | 20 | 0 | 0 | denied-zone residue count: 36 |
| GitHub governance | 15 | 5 | 5 | CODEOWNERS=yes, workflow=no |
| Bazel / CI reliability | 15 | 0 | 0 | bazel-build=no, bazel-test=no |
| third_party discipline | 10 | 10 | 10 | third_party/README.md=yes |
| Shared contracts | 10 | 5 | 5 | contracts doc=yes, proto files=0 |
| Workspace / tooling stability | 5 | 3 | 3 | workspace=no, pyright=yes |
| MCP stack stability | 5 | 4 | 4 | chrome_mcp=yes, token=no |

---

## Examples to audit this week
- Example canonical repo: apps/aiyou_stack/aiyou-fastapi-services
- Example unresolved repo count: 0
- Example denied-zone residue count: 36
- Example green bazel-build: no
- Example green bazel-test: no
- Example MCP fixed: chrome-devtools resolvable=yes
- Example MCP still timing out: firebase-mcp-server / mcp-toolbox-for-databases / sequential-thinking remain manual-validation items

---

## Quick evidence snapshot

- monorepo_manifest.yaml: yes
- .github/CODEOWNERS: yes
- .github/workflows/main.yml: no
- Monorepo-Uphillsnowball.code-workspace: no
- pyrightconfig.json: yes
- third_party/README.md: yes
- contracts/README.md: yes
- Python files under apps: 163494
- Python files under libs: 9483
- BUILD.bazel files: 2102
- Proto files: 0

---

## Executive summary
This scorecard was generated from current repo state rather than hand-written estimates.
The largest remaining blocker is unresolved canonicalization if unresolved repos remain, plus denied-zone residue if backup or legacy trees are still present.
GitHub governance is only partially measurable locally; web UI confirmation is still required for branch protection and required checks.
Next, resolve unresolved repos, remove denied-zone residue from live trees, and verify protected-main enforcement for bazel-build and bazel-test.
