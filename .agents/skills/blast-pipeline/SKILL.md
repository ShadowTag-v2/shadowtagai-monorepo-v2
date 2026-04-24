---
name: BLAST Pipeline
description: Zero-Trust Automation Architecture enforcing Build → Lint → Audit → Scan → Test sequence before any deployment or commit.
---

# BLAST Pipeline

## Purpose
Enforce the BLAST (Build → Lint → Audit → Scan → Test) sequence as a mandatory gate before deployments, commits, and PR merges. This is the zero-trust automation architecture referenced in the TACSOP.

## Pipeline Stages

### Stage 1: BUILD
Verify the project compiles/transpiles without errors.

```bash
# Python
/opt/homebrew/bin/python3.14 -m py_compile <file>

# TypeScript
npx tsc --noEmit

# .NET
dotnet build --no-restore

# Go
go build ./...
```

**Gate**: Any compilation error → HALT pipeline.

### Stage 2: LINT
Run language-specific linters with fix mode.

```bash
# Python (ruff subsumes vulture in V22)
ruff check --select F401,F841 --fix .

# TypeScript
npx biome check --fix .

# Go
golangci-lint run

# Shell
shellcheck scripts/*.sh
```

**Gate**: Any FATAL lint error → HALT. WARN errors are logged but don't block.

### Stage 3: AUDIT
Security-focused review of dependencies and code patterns.

```bash
# Python
pip-audit --strict

# Node
npm audit --audit-level=high

# Secrets
betterleaks detect --config .betterleaks.toml

# AST patterns
ast-grep scan --config .ast-grep/
```

**Gate**: Any HIGH/CRITICAL vulnerability → HALT. Known false positives in `.betterleaks.toml` allowlist.

### Stage 4: SCAN
Static analysis and pattern matching beyond linting.

```bash
# Type checking
/opt/homebrew/bin/python3.14 -m mypy --ignore-missing-imports <package>

# Cor.30 compliance
# (Automated checks from docs/SECURITY_DOD.md checklist)

# Dead code
ruff check --select F401,F811,F841 --statistics .
```

**Gate**: Type errors in modified files → HALT. Dead code → auto-fix.

### Stage 5: TEST
Run the test suite with coverage.

```bash
# Python (MUST use 3.14)
/opt/homebrew/bin/python3.14 -m pytest --tb=short -q

# TypeScript
npm test

# Integration
# Run only if unit tests pass
```

**Gate**: Baseline: 480 unit passed, 3 skipped. Any regression → HALT.

## When to Trigger BLAST

| Event | Stages Required |
|-------|----------------|
| Before `git commit` | L + A + S |
| Before `git push` | Full BLAST |
| Before `firebase deploy` | Full BLAST |
| Before `gcloud builds submit` | Full BLAST |
| Before PR merge | Full BLAST |
| After file edit (single file) | L only (via post-edit-validation-loop) |
| After dependency change | A + T |

## Abbreviated Mode

For speed during development, use abbreviated BLAST:

```bash
# Quick BLAST (Lint + Test only)
ruff check --select E,F --fix . && /opt/homebrew/bin/python3.14 -m pytest --tb=short -q -x
```

## Integration
- Stage 2 (Lint) delegates to `post-edit-validation-loop` for single-file
- Stage 2 (Lint) delegates to `omni-linter` for full-project
- Stage 3 (Audit) uses `gitleaks-guardian` workflow for secrets
- Stage 4 (Scan) uses `cor30-security-enforcer` skill for compliance
- Stage 5 (Test) respects pytest.ini v8.5 baseline
