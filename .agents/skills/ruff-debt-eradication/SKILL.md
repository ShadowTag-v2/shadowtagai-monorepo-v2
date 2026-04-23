---
name: ruff-debt-eradication
description: Standard Operating Procedure for resolving massive Python linting backlogs (>100 errors) safely using Unsafe Auto-fixes, Strategic Exclusion, Chunked Refactoring, and noqa Baselining.
---
# Ruff Debt Eradication

## When to use this skill
When Ruff or another linter returns hundreds of structural errors (e.g., `SIM`, `RET`, `C901`, `PLR`). Do NOT attempt to manually rewrite the whole codebase in one shot.

## The Pipeline (Strict Order of Operations)

**1. The "Unsafe" Auto-Fix Pass:**
Many "non-auto-fixable" rules (like `SIM102` nested ifs or `UP` modernizations) actually CAN be fixed mathematically by Ruff's Rust engine if explicitly permitted.
Run: `ruff check . --fix --unsafe-fixes`
*Must run the test suite immediately after. If tests pass, execute a micro-commit for these automated fixes.*

**2. Triage & Exclude (Shrink the pile):**
Run `ruff check . --statistics`. Analyze the output. If a large portion are low-value pedantic rules or highly opinionated formatting clashes, add them to the `extend-ignore` list in the project's Ruff config (`pyproject.toml` or `ruff.toml`).

**3. Chunked Refactoring (The AI Pass):**
Do NOT fix multiple rule types at once. Pick ONE specific rule category (e.g., `flake8-simplify` -> `--select SIM`).
- Run `ruff check . --select <RULE_ID>`
- Refactor a maximum of 3-5 files at a time.
- Run `pytest` (or relevant test suite) on those files.
- Micro-commit: `git commit -am "refactor: resolve Ruff <RULE_ID> errors"`

**4. The Debt Baseline (The Escape Hatch):**
If hundreds of complex architectural warnings remain and are blocking CI/CD, baseline the debt.
Run: `ruff check . --add-noqa`
This automatically appends `# noqa: <RULE_ID>` to the failing lines, instantly clearing the CI blocker so the debt can be paid down incrementally over future PRs.

## Excluded Paths (Monorepo-Uphillsnowball Specific)
Always pass `--exclude "tools/,third_party/,reference_architectures/,libs/autoresearch_sources/,.venv/,node_modules/,external_repos/,clones/"` to avoid touching vendored or R&D code.

## Safety Rules
1. **Never** run `--unsafe-fixes` without immediately running tests after.
2. **Never** fix more than one rule category per AI pass.
3. **Never** manually rewrite >5 files in a single prompt.
4. **Always** micro-commit after each pass.
5. The `--add-noqa` escape hatch is ONLY for CI/CD unblockers, never for hiding real bugs.
