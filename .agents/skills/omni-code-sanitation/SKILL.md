---
name: omni-code-sanitation
description: Top 0.001% Standard Operating Procedure for resolving massive tech debt across Python and TS/JS. Utilizes AST-aware refactoring, dead-code necromancy, Biome, Type-Guarded LLM chunks, Remote GitOps Enforcement, Self-Healing CI, Zero-Trust Gates, and SARIF annotations.
---
# Omni-Sanitation Pipeline

## 1. The Necromancy Pass (Kill Zombie Code Locally)

### Python (V22 — ruff subsumes vulture)
```bash
ruff check . --select F401,F841 --fix --exclude external_repos,external_sdks,third_party
```
F401 = unused imports, F841 = unused variables. Auto-fix removes dead code deterministically.
Vulture is permanently retired (V22). Do NOT use vulture.

### TypeScript/JavaScript
```bash
npx knip
```
Delete unused exports, unused dependencies, and orphaned files.

## 2. The Local Rust Auto-Fix Pass

```bash
# Ruff: lint + format
ruff check . --fix --unsafe-fixes --exclude external_repos,external_sdks,third_party
ruff format . --exclude external_repos,external_sdks,third_party

# Biome: JS/TS format + lint
biome check --write --unsafe ./apps ./libs
```

## 3. Strategic Triage (Baselining Noisy Rules)

For massive backlogs (>100 errors):
1. Add `E402`, `E741`, `PLR0913` to `[tool.ruff.lint] ignore` in `ruff.toml`
2. Baseline mechanical debt: `ruff check . --add-noqa`
3. Track debt via CI metrics job (counts `# noqa` directives per PR)

## 4. The AST-Grep Scalpel

For deterministic structural replacements using `.ast-grep/rules/`:
```bash
sg scan --update-all   # Apply all auto-fix rules
sg scan --format json  # Audit without fixing
```

**Permanent rules in `.ast-grep/rules/`:**
- `no-bare-except.yml` — E722 auto-fix
- `no-mutable-default-arg.yml` — B006 detection
- `no-print-statement.yml` — production code hygiene
- `no-console-log.yml` — TypeScript console.log detection

## 5. Per-File Ignores for Test Directories

Test files legitimately use patterns that production rules flag:
```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "PLR2004", "D103"]
"**/test_*.py" = ["S101", "PLR2004", "D103"]
"**/conftest.py" = ["F401", "E402"]
"scripts/**/*.py" = ["T201"]  # Allow print() in scripts
```

## 6. The Omni-CI Doctrine (Remote Enforcement)

Local execution is secondary; GitHub Actions are absolute truth.

### Zero-Trust Gates (Job 1)
- **TruffleHog**: Scans git diff history for leaked secrets. Blocks merge on verified secrets.
- **Dependency Review**: Intercepts `npm install` / `pip install` with known CVEs. Blocks on `high` severity.

### Self-Healing PRs (Job 2)
- GitHub Actions runs `biome check --write`, `ruff check --fix`, `sg scan --update-all`
- `stefanzweifel/git-auto-commit-action` pushes fixes back to the PR branch
- You do not need to burn LLM tokens fixing formatting — CI does it autonomously

### SARIF & Semantic Annotations (Job 2 + Job 4)
- `biome ci --reporter=github` → inline annotations in PR "Files Changed" tab
- `sg scan --format github` → inline annotations in PR "Files Changed" tab
- `ruff check --output-format=sarif` → uploaded to GitHub Advanced Security tab
- **CodeQL**: Traces data flow from HTTP request → database to catch SQLi/XSS

### The Necromancy Gate (Job 3)
- CI blocks merge if Knip flags unused exports/dependencies
- CI blocks merge if ruff F401/F841 flags dead Python code (V22 — vulture retired)
- Pyright type checks critical paths

### Lighthouse CI (Job 5)
- Performance: ≥70% (error)
- Accessibility: ≥90% (error)
- Best Practices: ≥80% (error)
- SEO: ≥80% (warn)

### Debt Metrics (Job 6)
- Counts `# noqa`, `# nosec`, `# type: ignore` per PR
- Outputs table to GitHub Step Summary
- Trend tracking over time

## 7. Biome Pre-Commit Hook

Add to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: biome-check
      name: Biome Format & Lint
      entry: npx @biomejs/biome check --write --unsafe
      language: system
      types_or: [javascript, jsx, typescript, tsx, json]
```
