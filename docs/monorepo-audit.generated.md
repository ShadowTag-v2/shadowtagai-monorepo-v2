# Monorepo Audit Report

## Audit date
`2026-04-09`

## Auditor
Generated from local audit scripts

## Scope
Canonicalization, live tree cleanliness, GitHub governance scaffolding, build/CI scaffolding, third_party policy, contracts policy, workspace stability, and MCP stack scaffolding.

---

## 1. Canonical repo audit

### Manifest present
- `yes`

### Unresolved entries
```
55:    status: unresolved
62:    status: unresolved
```

### Findings
- If unresolved entries remain, the monorepo is not yet fully canonical.
- Canonicalization must continue until no repo remains unresolved.

---

## 2. Live tree cleanliness audit

### Denied-zone residue in live trees
```
apps/aiyou-web-dashboard/node_modules/character-entities-legacy
apps/aiyou-web-dashboard/node_modules/mdast-util-mdx-jsx/node_modules/character-entities-legacy
apps/aiyou_stack/aiyou-fastapi-services/apps/omega-ui/node_modules/character-entities-legacy
apps/aiyou_stack/aiyou-fastapi-services/apps/omega-ui/node_modules/mdast-util-mdx-jsx/node_modules/character-entities-legacy
apps/aiyou_stack/aiyou-fastapi-services/apps/omega-ui/node_modules/stringify-entities/node_modules/character-entities-legacy
apps/aiyou_stack/nascent-apollo/libs/arsenal_recovered
libs/cyberpunk_stack/openclaw/dist/extensions/diffs/node_modules/character-entities-legacy
libs/cyberpunk_stack/openclaw/node_modules/character-entities-legacy
```

### Nested repo markers
```
libs/autoresearch_sources/n-autoresearch/.git
```

### Findings
- Any denied-zone residue above indicates live tree surgery is incomplete.
- Any nested .git markers under apps/libs indicate duplicate or nested repo risk.

---

## 3. GitHub governance audit

- CODEOWNERS present: `yes`
- Workflow present: `yes`

### Notes
- Local files can confirm governance scaffolding exists.
- GitHub web UI is still required to confirm:
  - protected main
  - PR requirement
  - code owner review requirement
  - required checks: bazel-build, bazel-test

---

## 4. third_party audit

- third_party/README.md present: `yes`

### Findings
- Presence of policy doc is only step one.
- Real 10/10 requires actual dependency centralization under `third_party/`.

---

## 5. Contracts audit

- contracts/README.md present: `yes`

### Proto inventory
```
none
```

### Findings
- If no shared proto/schema files exist, the contract layer is still policy-only rather than operational.

---

## 6. Workspace / tooling audit

- Workspace file present: `yes`
- Pyright config present: `yes`
- Antigravity prompt present: `yes`

### Findings
- Tooling stabilization is present at the config layer.
- Runtime validation still matters for Python envs, pyright scanning, and workspace drift.

---

## 7. MCP stack audit

- MCP stack doc present: `yes`
- MCP config present: `yes`

### Findings
- Stable-first MCP policy can be enforced from the repo now.
- Timeout-prone MCPs should remain disabled until standalone validation succeeds.

---

## Executive summary
This generated audit reflects the current local repo state, not aspirational docs alone.
The biggest blockers to 10/10 remain unresolved repos, denied-zone residue in live paths, and any missing GitHub enforcement in the web UI.
The repo now has the scaffolding to become a disciplined monorepo, but full completion still depends on canonicalization, cleanup, enforcement, and proof via successful refactors and stable CI.
