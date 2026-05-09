# REVIEW.md — Antigravity PR Review Rules

## Sovereign PR Review Doctrine

This document is the **single source of truth** for the Jules + GCA PR Review Swarm.

---

## Review Tiers

| Tier | Engine | Scope | Latency |
|------|--------|-------|---------|
| **1** | ruff + biome + ast-grep | Lint, format, dead code, static analysis | <5s |
| **2** | Colab T4 via Google Drive IPC | Heavy ML inference, model validation | 30-60s |
| **3** | M1 Max ANE via ane_bridge.py | On-device inference, 12.5MB L2 limit | 10-20s |

---

## Severity Levels

| Emoji | Level | Action |
|-------|-------|--------|
| 🔴 | **Critical** | Blocks merge. Must be physically verified. |
| 🟡 | **Warning** | Lint violation or style issue. Auto-fixable. |
| 🟢 | **Info** | Suggestion only. No action required. |

---

## Review Rules

1. **Never post unverified findings.** Every 🔴 must be reproduced by at least one Tier.
2. **Auto-fix before reporting.** Run `ast_surgery.ts` first. Only report what cannot be auto-fixed.
3. **No false positives.** If in doubt, downgrade to 🟢.
4. **Respect the Boy Scout Rule.** Leave the codebase cleaner than you found it.
5. **Security findings are always 🔴.** Hardcoded secrets, SQL injection, XSS = instant block.

---

## Language-Specific Rules

### Python
- Linter: `ruff` (NOT flake8, NOT pylint)
- Formatter: `ruff format` (NOT black)
- Dead code: `ruff check --select F401,F841`

### TypeScript / JavaScript
- Linter: `biome` (NOT ESLint)
- Formatter: `biome format` (NOT Prettier)
- Structural: `ast-grep` for pattern matching

### Go
- Linter: `golangci-lint`
- Formatter: `gofmt`

### Rust
- Linter: `clippy`
- Formatter: `rustfmt`

---

## Prohibited Patterns

- `console.log` in production code (use structured logging)
- `any` type in TypeScript (use proper types)
- Hardcoded API keys or secrets
- `import *` in Python
- Direct Firestore reads without batch/transaction in write paths
- Static Firebase imports (must use dynamic `await import()`)

---

## Auto-Fix Pipeline

```
ast_surgery.ts
  ├── ruff check --fix .
  ├── ruff format .
  ├── biome check --write .
  └── ast-grep (dynamic Firebase imports)
```
