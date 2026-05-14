# Monorepo Audit Report

## Audit date
`2026-03-21`

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
none
```

### Findings
- If unresolved entries remain, the monorepo is not yet fully canonical.
- Canonicalization must continue until no repo remains unresolved.

---

## 2. Live tree cleanliness audit

### Denied-zone residue in live trees
```
apps/aiyou_stack/.quarantine/aiyou-fastapi-services-legacy
apps/aiyou_stack/.quarantine/aiyou-fastapi-services-legacy/aiyou-fastapi-services-legacy
apps/aiyou_stack/aiyou-fastapi-services/_PRE_OMEGA_BACKUP_1768415640
apps/aiyou_stack/aiyou-fastapi-services/_PRE_OMEGA_BACKUP_1768415766
apps/aiyou_stack/aiyou-fastapi-services/_PRE_OMEGA_BACKUP_1768415932
apps/aiyou_stack/codex/codex-rs/execpolicy-legacy
apps/pnkln_stack/.quarantine/pnkln-fastapi-services-legacy
apps/pnkln_stack/.quarantine/pnkln-fastapi-services-legacy/pnkln-fastapi-services-legacy
apps/pnkln_stack/codex/codex-rs/execpolicy-legacy
apps/pnkln_stack/pnkln-fastapi-services/_PRE_OMEGA_BACKUP_1768415640
apps/pnkln_stack/pnkln-fastapi-services/_PRE_OMEGA_BACKUP_1768415766
apps/pnkln_stack/pnkln-fastapi-services/_PRE_OMEGA_BACKUP_1768415932
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/character-entities-legacy@1.1.4/node_modules/character-entities-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/character-entities-legacy@3.0.0/node_modules/character-entities-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/ts-jest@29.4.5_@babel+core@7.28.5_@jest+transform@30.2.0_@jest+types@30.2.0_babel-jest@_503c0f083ff2b5e752a2c02d03bda892/node_modules/ts-jest/presets/default-esm-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/ts-jest@29.4.5_@babel+core@7.28.5_@jest+transform@30.2.0_@jest+types@30.2.0_babel-jest@_503c0f083ff2b5e752a2c02d03bda892/node_modules/ts-jest/presets/default-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/ts-jest@29.4.5_@babel+core@7.28.5_@jest+transform@30.2.0_@jest+types@30.2.0_babel-jest@_503c0f083ff2b5e752a2c02d03bda892/node_modules/ts-jest/presets/js-with-babel-esm-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/ts-jest@29.4.5_@babel+core@7.28.5_@jest+transform@30.2.0_@jest+types@30.2.0_babel-jest@_503c0f083ff2b5e752a2c02d03bda892/node_modules/ts-jest/presets/js-with-babel-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/ts-jest@29.4.5_@babel+core@7.28.5_@jest+transform@30.2.0_@jest+types@30.2.0_babel-jest@_503c0f083ff2b5e752a2c02d03bda892/node_modules/ts-jest/presets/js-with-ts-esm-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/deer-flow/web/node_modules/.pnpm/ts-jest@29.4.5_@babel+core@7.28.5_@jest+transform@30.2.0_@jest+types@30.2.0_babel-jest@_503c0f083ff2b5e752a2c02d03bda892/node_modules/ts-jest/presets/js-with-ts-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/langgraph/libs/cli/js-examples/node_modules/ts-jest/presets/default-esm-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/langgraph/libs/cli/js-examples/node_modules/ts-jest/presets/default-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/langgraph/libs/cli/js-examples/node_modules/ts-jest/presets/js-with-babel-esm-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/langgraph/libs/cli/js-examples/node_modules/ts-jest/presets/js-with-babel-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/langgraph/libs/cli/js-examples/node_modules/ts-jest/presets/js-with-ts-esm-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/langgraph/libs/cli/js-examples/node_modules/ts-jest/presets/js-with-ts-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/Piped/node_modules/.pnpm/@vitejs+plugin-legacy@7.2.1_terser@5.43.1_vite@7.1.5_jiti@2.5.1_lightningcss@1.30.1_terser@5.43.1_yaml@2.8.1_/node_modules/@vitejs/plugin-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/spring-ai-alibaba/spring-ai-alibaba-studio/agent-chat-ui/node_modules/.pnpm/character-entities-legacy@1.1.4/node_modules/character-entities-legacy
apps/pnkln_stack/pnkln-fastapi-services/vendor/spring-ai-alibaba/spring-ai-alibaba-studio/agent-chat-ui/node_modules/.pnpm/character-entities-legacy@3.0.0/node_modules/character-entities-legacy
libs/terraform/internal/command/testdata/backend-changed-with-legacy
libs/terraform/internal/command/testdata/backend-new-legacy
libs/terraform/internal/command/testdata/backend-plan-legacy
libs/terraform/internal/command/testdata/backend-unchanged-with-legacy
libs/terraform/internal/command/testdata/backend-unset-with-legacy
libs/terraform/internal/command/testdata/init-get-provider-detected-legacy
libs/terraform/internal/command/testdata/plan-out-backend-legacy
```

### Nested repo markers
```
none
```

### Findings
- Any denied-zone residue above indicates live tree surgery is incomplete.
- Any nested .git markers under apps/libs indicate duplicate or nested repo risk.

---

## 3. GitHub governance audit

- CODEOWNERS present: `yes`
- Workflow present: `no`

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

- Workspace file present: `no`
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
