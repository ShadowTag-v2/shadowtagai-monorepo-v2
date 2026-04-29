---
name: TACSOP5 Omni-Sanitation Pipeline
version: 2.0.0
status: production
description: Self-Healing CI/CD Pipeline Architecture with 7 jobs, necromancy gates, and .NET 11.0 build validation.
tokens:
  lint_python: ruff
  lint_typescript: biome
  lint_structural: ast-grep
  lint_secrets: betterleaks
  type_python: pyright
  type_dotnet: dotnet-build
---

# DESIGN.md — TACSOP 5 Omni-Sanitation & Zero-Trust CI

> Design System for the Self-Healing CI/CD Pipeline Architecture

## Metadata

| Key | Value |
|-----|-------|
| Version | 2.0.0 |
| Status | PRODUCTION |
| Date | 2026-04-26 |
| Pipeline | `.github/workflows/omni-ci.yml` (287 lines, 7 jobs) |
| Trigger | `pull_request` to `main` + `workflow_dispatch` |

---

## Design Tokens

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────┐
│              Omni-Sanitation Pipeline                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐                                    │
│  │ Job 1       │ Zero-Trust Gates                   │
│  │ TruffleHog  │ (Secrets + Supply Chain)           │
│  │ + Dep Review│                                    │
│  └──────┬──────┘                                    │
│         │                                           │
│  ┌──────▼──────┐                                    │
│  │ Job 2       │ Self-Healing Pass                  │
│  │ Biome+Ruff  │ (Auto-Fix + SARIF + Commit)       │
│  │ +AST-Grep   │                                    │
│  └──────┬──────┘                                    │
│         │                                           │
│  ┌──────▼──────┬───────────┬──────────┬──────────┐  │
│  │ Job 3      │ Job 4     │ Job 5    │ Job 7    │  │
│  │ Necromancy │ CodeQL    │ LH CI    │ .NET 11  │  │
│  │ (Knip+Ruff)│ (Semantic)│ (Perf)   │ (Build)  │  │
│  └────────────┴───────────┴──────────┴──────────┘  │
│         │                                           │
│  ┌──────▼──────┐                                    │
│  │ Job 6       │ Debt Metrics                       │
│  │ noqa/nosec  │ (Dashboard)                        │
│  └─────────────┘                                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Linting Stack Tokens

| Token | Tool | Domain | Role |
|-------|------|--------|------|
| `LINT_PYTHON` | ruff | `*.py` | AST lint + format + dead code (F401/F841) |
| `LINT_TYPESCRIPT` | biome | `*.ts/*.tsx/*.js` | AST lint + format |
| `LINT_STRUCTURAL` | ast-grep | All | Structural search-and-replace |
| `LINT_SECRETS` | TruffleHog + Betterleaks | All | Secret detection |
| `LINT_DEAD_JS` | Knip | `*.ts/*.tsx` | Unused exports + deps |
| `LINT_DEAD_PY` | ruff F401/F841 | `*.py` | Unused imports + variables |
| `TYPE_PYTHON` | Pyright | `*.py` | Static type checking |
| `TYPE_DOTNET` | dotnet build | `*.cs` | Compile-time validation |

### Banned Tools

| Tool | Reason | Replacement |
|------|--------|-------------|
| `vulture` | Subsumed by ruff F401/F841 | `ruff check --select F401,F841` |
| `ESLint` | Subsumed by biome | `biome check` |
| `Prettier` | Subsumed by biome | `biome format` |
| `oxc` | Subsumed by biome | `biome check` |
| `pylint` | Subsumed by ruff | `ruff check` |

---

## AST-Grep Rules (7 Codified)

| Rule | File | Language | Purpose |
|------|------|----------|---------|
| No Bare Except | `no-bare-except.yml` | Python | Prevents `except:` without type |
| No Console.log | `no-console-log.yml` | TypeScript | Production hygiene |
| No BullMQ Import | `no-bullmq-import.yml` | TypeScript | Queue doctrine enforcement |
| No BullMQ Python | `no-bullmq-python.yml` | Python | Queue doctrine enforcement |
| No BullMQ Require | `no-bullmq-require.yml` | JavaScript | Queue doctrine enforcement |
| No Mutable Default | `no-mutable-default-arg.yml` | Python | Python footgun prevention |
| No Print Statement | `no-print-statement.yml` | Python | Production hygiene |

---

## Performance Budgets (Lighthouse CI)

| Metric | Threshold | Type |
|--------|-----------|------|
| Performance Score | ≥ 90 | Error |
| Accessibility Score | ≥ 90 | Error |
| Best Practices Score | ≥ 85 | Warning |
| SEO Score | ≥ 90 | Warning |
| First Contentful Paint | < 2000ms | Error |
| Largest Contentful Paint | < 3500ms | Error |
| Cumulative Layout Shift | < 0.1 | Error |
| Total Blocking Time | < 300ms | Error |
| Time to Interactive | < 5000ms | Warning |
| Script Bundle Size | < 300KB | Warning |
| Document Size | < 50KB | Warning |
| Stylesheet Size | < 100KB | Warning |

---

## Self-Healing Behavior Contract

### Local (Agent)
1. After **every file modification**, run `ruff check --fix` + `ruff format` on the modified file
2. If linting fails, fix autonomously — **never prompt the user**
3. Use `ast-grep` for structural patterns ruff/biome cannot express

### Remote (GitHub Actions)
1. On every PR, run `biome check --write` + `ruff check --fix --unsafe-fixes` + `sg scan --update-all`
2. Auto-commit fixes back to the PR branch via `git-auto-commit-action`
3. Generate SARIF for GitHub Advanced Security tab
4. Generate native GitHub annotations for inline PR feedback

### Pre-Push (Git Hook)
1. Git LFS verification
2. Betterleaks staged secret scan
3. Block push if secrets detected (bypass: `--no-verify` emergency only)

---

## Necromancy Gate Contract

### Hard-Fail (Merge Blocking)
- **Knip**: Unused JS/TS exports and dependencies → PR cannot merge
- **Ruff F401/F841**: Unused Python imports and variables → PR cannot merge

### Soft-Fail (Warning Only)
- **Pyright**: Type errors reported but non-blocking (legacy code accommodation)

---

## .NET Build Validation

| Project | TFM | SDK |
|---------|-----|-----|
| AiYou.Kernel | `net11.0` | 11.0.100-preview.3 |
| SemanticKernel | `net11.0` | 11.0.100-preview.3 |
| SeatJudge.Inventory.Mcp | `net11.0` | 11.0.100-preview.3 |
| Explore | `net11.0` | 11.0.100-preview.3 |

**Namespace Rule**: Use fully-qualified `Microsoft.SemanticKernel.Kernel` to avoid collision with `ShadowTagV4.Kernel`.

---

## Daemon Fleet

| Daemon | Script | Purpose |
|--------|--------|---------|
| GCA Autolint | `scripts/gca_autolint_daemon.py` (507L) | GitHub App JWT push, ruff+biome, beads audit trail |
| Dream Consolidation | `scripts/dream_consolidation.py` | Nightly KI maintenance |
| Loop Steward | `scripts/loop_steward.py` | 5-min autonomous task continuation |
| COR.KAIROS | `scripts/kairos_daemon.py` | Background autonomous agent mode |
| pnkln-evolve | `scripts/pnkln_evolve.py` | Recursive self-improvement |

---

## References

- Pipeline: [omni-ci.yml](file:///.github/workflows/omni-ci.yml)
- Skill: [tacsop5-linting-doctrine](file:///.agents/skills/tacsop5-linting-doctrine/SKILL.md)
- Rules: [.ast-grep/rules/](file:///.ast-grep/rules/)
- Config: [lighthouserc.json](file:///lighthouserc.json)
- Config: [sgconfig.yml](file:///sgconfig.yml)
