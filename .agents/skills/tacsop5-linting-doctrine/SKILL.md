---
name: tacsop5-linting-doctrine
description: >
  MANDATORY: Cor.Antigravity TACSOP 5 — Continuous Self-Healing Linting Doctrine.
  Codifies the permanent linting posture, chunked push protocol, file hygiene,
  and autonomous AST correction behaviors. Read before ANY lint, push, or refactor operation.
---

# TACSOP 5 — Continuous Self-Healing Linting Doctrine

## 1. Linting Stack (V22 Pruned Singularity)

**Two engines. One weapon. Zero vulture.**

| Tool | Domain | Role |
|------|--------|------|
| `ruff` | Python | AST linting + formatting + dead code (F401/F841). Replaces vulture, pyflakes. |
| `biome` | TypeScript/JS/JSON | AST linting + formatting. Replaces ESLint + Prettier. |
| `ast-grep` | All | Structural search-and-replace weapon. NOT a lint target — a surgical tool. |

**Banned:** `vulture` (subsumed by ruff F401/F841), `oxc` (subsumed by biome), `ESLint` (subsumed by biome), `Prettier` (subsumed by biome).

### Execution Commands

```bash
# Python (ruff)
ruff check --fix .                      # Safe fixes
ruff check --fix --unsafe-fixes .       # Aggressive fixes (--aggressive flag)
ruff format .                           # Auto-format
ruff check --select F401,F841 --statistics .  # Dead code audit

# TypeScript/JS (biome)
npx @biomejs/biome check --write .      # Lint + format

# Dead code audit script
bash scripts/dead-code-audit.sh

# Full daemon (GCA Autolint)
python3 scripts/gca_autolint_daemon.py --yes --json
```

## 2. Continuous Self-Healing Behavior

**ABSOLUTE RULE:** Never prompt the user with linting errors. Fix them silently.

1. After EVERY file modification, run `ruff check --fix` and `ruff format` on the modified file.
2. If `ruff` or `biome` exit with code > 0, intercept the trace and fix it autonomously.
3. Use `ast-grep` for structural patterns that ruff/biome cannot express.
4. The "red squiggly line" is deprecated — errors are self-corrected before the user sees them.

**Implementation:** The `post-edit-validation-loop` skill enforces this at the behavioral level.

## 3. GCA Autolint Daemon

**Script:** `scripts/gca_autolint_daemon.py` (507 lines, production-ready)

### Features
- GitHub App JWT authentication (5-tier PEM fallback chain)
- `GIT_ASKPASS` secure token injection (token never in URL or process args)
- PATH augmentation for non-interactive shells
- Ruff + Biome execution with JSON output
- `.beads/issues.jsonl` audit trail
- `.beads/heartbeat.json` daemon health check
- Dry-run, aggressive, headless modes
- GWS notification support

### Usage
```bash
python3 scripts/gca_autolint_daemon.py --yes           # Headless auto-approve
python3 scripts/gca_autolint_daemon.py --dry-run        # Lint only, no push
python3 scripts/gca_autolint_daemon.py --aggressive     # Enable unsafe fixes
CI=true python3 scripts/gca_autolint_daemon.py          # CI mode
```

## 4. Chunked Git Push Protocol

**Context:** GitHub enforces a 100MB per-file limit and has pack size limits. The monorepo is 122GB workspace / 51GB .git.

### Protocol
1. **Before pushing:** Run `.gitignore` audit to ensure all large binaries, external repos, and vector DBs are excluded.
2. **Chunk size:** Each push should target ≤100MB of new content.
3. **Batch of 5:** Push 5 sequential chunks, then STOP.
4. **Token renewal:** After each batch of 5, regenerate the GitHub App installation token (tokens expire in 1 hour).
5. **Resume:** After token renewal, push the next batch of 5.

### Implementation
```bash
# The gca_autolint_daemon.py handles token generation.
# For manual chunked pushes, use:
python3 scripts/auth_github_app.py  # Generate fresh token
git push --thin origin HEAD:refs/heads/<branch>  # Push with thin pack
```

### .gitignore Mandatory Patterns
These MUST be present in `.gitignore`:
```
external_repos/
.lancedb_data/
*.bin
*.weights
*.onnx
*.pt
*.pem
*.key
.venv/
node_modules/
__pycache__/
.env
*.heapsnapshot
```

## 5. Pre-Push Hygiene Checklist

Before ANY push to remote:

1. **PII scan:** `grep -rn 'password\|secret\|api_key\|token' --include='*.py' --include='*.ts' . | grep -v '.gitignore\|SKILL.md\|AGENTS.md'`
2. **Dead code:** `ruff check --select F401,F841 --statistics .`
3. **Large files:** `git ls-files | xargs ls -la | sort -k5 -rn | head -20`
4. **Secrets:** `betterleaks scan .` or `git diff --cached | grep -iE 'sk-|ghp_|gho_|AIza|ya29\.'`
5. **Binary check:** `git diff --cached --diff-filter=A --name-only | xargs file | grep -v text`

## 6. Monolithic File Refactoring Directive

**Rule:** Files exceeding 500 lines SHOULD be refactored. Files exceeding 1000 lines MUST be refactored.

### Refactoring Pattern
1. Identify logical boundaries (classes, route groups, utility functions).
2. Create a directory with `__init__.py` (Python) or `index.ts` (TypeScript).
3. Extract each logical unit into its own module.
4. Re-export from `__init__.py` / `index.ts` for backward compatibility.
5. Run full test suite to verify no regressions.

## 7. UI Consistency Audit

**The 10X QA Hack:** After every screen/component is finished:

1. Run: `grep -rn 'onClick\|onPress\|href=' --include='*.tsx' --include='*.jsx' . | grep -v node_modules`
2. Look for: orphaned actions, duplicate components, inconsistent button styles, broken user flows.
3. Save findings to `audit.md` in the component directory.
4. Fix everything at once in a single commit.

**Skill reference:** `.agents/skills/ui-consistency-auditor/SKILL.md`

## 8. WCAG Auto-Correction Loop

When modifying any `DESIGN.md` or design tokens:

1. Run `npx @google-labs/design-cli lint <file_path>`.
2. If WCAG contrast ratio < 4.5:1, darken ink or lighten canvas.
3. Re-run linter until exit code 0.
4. Only then proceed to scaffold React/A2UI components.

**Semantic roles:** `primary` = main text ink, `neutral` = canvas background. Never assume `primary` = brand button color.

## 9. Prompt Repetition for Sub-Agent Tasks

**arXiv:2512.14982 — Rule of Three**

- Applies ONLY to non-reasoning model tiers (flash, lite, mini).
- Do NOT apply to reasoning/thinking models.
- For data extraction via browser subagent: repeat the instruction 3x in the prompt.
- For NotebookLM queries: repeat the query in the context.

## 10. IDE Stabilization Invariants

When IDE becomes unstable (Extension Host crashes, LSP hangs):

1. **Purge Vim state:** Remove `globalStorage/vscodevim.vim` cache.
2. **Clean LSP schemas:** Strip undocumented keys from `.vscode/settings.json` for `ruff` and `ty`.
3. **Shield FSEvents:** Add `.lancedb_data`, `.venv`, `node_modules`, `.git/objects` to `files.watcherExclude`.
4. **Prune git refs:** `git pack-refs --all --prune` in submodule directories.
5. **Reload window:** `Cmd+Shift+P → Developer: Reload Window`.

**Skill reference:** `.agents/skills/ide-host-stabilization/SKILL.md`
