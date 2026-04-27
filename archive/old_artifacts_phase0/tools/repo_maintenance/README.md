# Repo Maintenance Toolchain

Deterministic, safe, boring repo maintenance.

## Stack

| Concern             | Tool        | Purpose                                      |
| ------------------- | ----------- | -------------------------------------------- |
| Secrets             | Betterleaks | Find committed/API/cloud secrets             |
| Python lint/format  | Ruff        | Python linting, import cleanup, formatting   |
| JS/TS lint/format   | Biome       | JavaScript/TypeScript linting and formatting |
| Structural rewrites | ast-grep    | AST-aware search and codemods                |

## Usage

```bash
# Run all checks
bash tools/repo_maintenance/run_all.sh

# Run individual checks
bash tools/repo_maintenance/betterleaks_scan.sh
bash tools/repo_maintenance/ruff_check.sh
bash tools/repo_maintenance/biome_check.sh
bash tools/repo_maintenance/ast_grep_scan.sh
```

## Reports

All tool output is written to `tools/repo_maintenance/reports/`.
Reports are gitignored by default (see `.gitkeep`).

## Judge 6 Policy

See [judge6_policy.md](./judge6_policy.md) for auto-fix boundaries.

**One-line rule:**
> Betterleaks blocks secrets; Ruff and Biome clean syntax/style; ast-grep handles structural detection; Judge 6 decides what may change automatically.

## Prerequisites

- **Betterleaks**: `go install github.com/betterleaks/betterleaks@latest`
- **Ruff**: `pip install ruff` or `uv tool install ruff`
- **Biome**: `npm install -g @biomejs/biome` or use `npx`
- **ast-grep**: `npm install -g @ast-grep/cli` or `cargo install ast-grep`
