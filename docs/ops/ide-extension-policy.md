# IDE Extension Policy

> **Status:** LOCKED | **Version:** 1.0 | **Updated:** 2026-05-04

## Policy

Heavy IDE daemons are **prohibited** unless:
1. A matching orchestrator config (`nx.json`, `turbo.json`) exists at repo root
2. The extension has been explicitly approved via a Beads decision record

## Current State

| Orchestrator | Config File | Found | Status |
|-------------|-------------|-------|--------|
| Nx | `nx.json` | ❌ Not found | Do not install Nx Console |
| Turborepo | `turbo.json` | ❌ Not found | Do not install Turbo extension |

## Prohibited Extensions

| Extension | ID | Reason |
|-----------|-----|--------|
| Nx Console | `nrwl.angular-console` | No `nx.json` — the extension has no orchestrator to operate. Adds watcher daemon. |
| Prettier | `esbenp.prettier-vscode` | Biome is the canonical formatter (TACSOP 5). |
| ESLint | `dbaeumer.vscode-eslint` | Biome is the canonical linter (TACSOP 5). |
| Beautify | `HookyQR.beautify` | Biome is the canonical formatter (TACSOP 5). |

## Rationale

This repo has **95+ cloned reference repos** in `external_repos/` and a large
`tools/` directory containing Dart and Go packages. IDE daemons that eagerly
index, watch, or analyze the full workspace tree cause:

1. **FSEvents queue overflow** on macOS (max 524,288 watches)
2. **Dart phantom cascade** — recursive `pub get` and analysis across 30+ packages
3. **CPU saturation** from competing watcher daemons

The Monorepo OS model relies on **explicit terminal scripts** for all
orchestration (`scripts/release-readiness-gate.sh`, `scripts/daily-truth-report.sh`,
etc.) rather than implicit IDE background tasks.

## Approved Extensions

Only code-quality extensions that align with the canonical linting stack:

| Extension | Purpose |
|-----------|---------|
| Biome | Lint + format (TS/JS) |
| Ruff | Lint + format (Python) |
| C# Dev Kit | .NET development |
| Dart/Flutter | Active Dart development only |
| Firebase Explorer | Firebase project management |

## Verification

```bash
# Check for prohibited extensions
code --list-extensions | grep -iE "prettier|eslint|beautif|angular-console"

# Check for orchestrator configs
ls -la nx.json turbo.json 2>/dev/null || echo "No orchestrator configs found"
```
