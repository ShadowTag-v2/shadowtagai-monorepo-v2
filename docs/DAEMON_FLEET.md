# Daemon Fleet — Ruff Integration Guide

## Astral Ruff Ecosystem

This monorepo uses all three Astral-maintained Ruff components:

| Component | Repository | Artifact | Purpose |
|-----------|-----------|----------|---------|
| **Ruff Core** | [astral-sh/ruff](https://github.com/astral-sh/ruff) | `ruff` binary | Linter + formatter (Rust-native, 10-100x faster than flake8) |
| **Ruff Pre-commit** | [astral-sh/ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit) | `.pre-commit-config.yaml` | Git hook integration (runs on commit) |
| **Ruff VSCode** | [astral-sh/ruff-vscode](https://github.com/astral-sh/ruff-vscode) | `charliermarsh.ruff` extension | IDE integration (lint-on-type, format-on-save) |

> **Note:** `astral-sh/ruff-lsp` is **deprecated**. Ruff now ships a native LSP server (`ruff server`). The VSCode extension uses this natively.

## Configuration Hierarchy

Ruff reads config in this precedence order:

```
ruff.toml     (project-level, highest precedence)
  ↓
pyproject.toml [tool.ruff]  (fallback)
  ↓
VSCode settings.json ruff.*  (IDE-level overrides)
```

### Current Pinned Version: `0.15.11`

All surfaces pin to `ruff >= 0.15.11`:
- `pyproject.toml` → `ruff>=0.15.11`
- `.pre-commit-config.yaml` → `rev: v0.15.11`
- `.venv/bin/ruff` → `0.15.11`
- System ruff → `0.15.11`
- CI (`astral-sh/ruff-action@v3`) → latest

### Target Version: `py314`

Matches CPython 3.14.3 runtime (per AGENTS.md).

## Integration Points

### 1. `gca_autolint_daemon.py` (Scheduled CI)
- Runs `ruff check --fix --output-format=json` for structured results
- Runs `ruff check --statistics` for PR summaries
- Runs `ruff format` (or `ruff format --diff` in dry-run mode)
- Captures ruff version in beads audit entries
- `--aggressive` flag enables `--unsafe-fixes`
- Uses `.venv/bin/ruff` via PATH augmentation

### 2. `dead-code-audit.sh` (Pre-commit Gate)
- Runs `ruff check --fix --exit-zero` (report-only, never blocks)
- Runs `ruff check --statistics` for summary
- Prefers `.venv/bin/ruff`, falls back to system PATH
- Complementary to daemon (fast, local, no auth/push)

### 3. `.pre-commit-config.yaml` (Git Hooks)
- Uses `astral-sh/ruff-pre-commit` mirror (not raw binary)
- `ruff` hook: check + fix
- `ruff-format` hook: format on commit
- Excludes: tools/, third_party/, libs/, labs/, reference_architectures/, external_repos/, etc.

### 4. `.github/workflows/omni-autolint.yml` (GitHub Actions)
- `astral-sh/setup-uv@v6`: Installs uv for tool execution
- `astral-sh/ruff-action@v3`: Native ruff GitHub Action (lint check)
- `uv run ruff check --fix --output-format=json`: Structured JSON output
- `uv run ruff check --statistics`: Rule violation summary

### 5. VSCode (IDE)
- Extension: `charliermarsh.ruff` (recommended in `.vscode/extensions.json`)
- Native server: `ruff.nativeServer: "on"` (replaces deprecated ruff-lsp)
- Lint-on-type: `ruff.lint.run: "onType"`
- Fix-all on save: `ruff.fixAll: true`
- Import strategy: `fromEnvironment` (uses `.venv/bin/ruff`)

## Ruff + Vulture Complementarity

| Concern | Ruff | Vulture |
|---------|------|---------|
| **Unused imports** | ✅ F401 | ✅ |
| **Unused variables** | ✅ F841 | ✅ |
| **Unused functions** | ❌ | ✅ |
| **Unused classes** | ❌ | ✅ |
| **Unused attributes** | ❌ | ✅ |
| **Code style** | ✅ E/W series | ❌ |
| **Security** | ✅ S series (bandit) | ❌ |
| **Import sorting** | ✅ I series (isort) | ❌ |
| **Type annotations** | ✅ ANN series | ❌ |
| **Auto-fix** | ✅ | ❌ (report-only) |

**Both are needed.** Ruff handles style/imports/security. Vulture catches dead functions/classes/attributes that ruff doesn't flag.

## Unfixable Rules (Critical)

```toml
[tool.ruff.lint]
unfixable = ["B018", "F841"]
```

- **B018**: Would strip `print()` calls treating f-string args as "useless expressions"
- **F841**: Would strip variable assignments used only for logging/print output
- Root cause: The v9.7 unsafe-fixes sweep silently killed `prune_gca_chat_threads.py` output

## Incremental Rule Adoption Strategy

Current select: `["E", "F", "I", "UP", "B", "SIM"]`

Recommended next additions (in order):
1. `PTH` — pathlib migration (510 violations, mostly mechanical)
2. `ANN` — type annotations (261 violations, gradual)
3. `D` — docstrings (audit-only, use `--extend-select D --statistics`)
4. `S` — security (already via bandit hook, but ruff S-rules are faster)
