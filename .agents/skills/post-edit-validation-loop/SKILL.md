---
name: Post-Edit Validation Loop
description: Automatically runs linter/type-checker after every file modification to catch errors immediately. Enforced as a behavioral invariant.
---

# Post-Edit Validation Loop

## Purpose
Catch syntax errors, import failures, and type mismatches immediately after every file write — not at the end of a multi-file session.

## Behavioral Rule (ABSOLUTE)

After EVERY call to `write_to_file`, `replace_file_content`, or `multi_replace_file_content`:

### Python Files (`.py`)
```bash
ruff check --select E,F,W --no-fix <modified_file>
```
- If ruff reports **F401** (unused import) or **F841** (unused variable): auto-fix with `--fix`
- If ruff reports **E999** (syntax error): STOP and fix before proceeding
- If ruff reports **E711/E712** (comparison issues): fix inline

### TypeScript/JavaScript Files (`.ts`, `.tsx`, `.js`, `.jsx`)
```bash
npx biome check --no-errors-on-unmatched <modified_file>
```
- On any `lint/suspicious` error: fix before proceeding
- On any `lint/correctness` error: fix before proceeding

### JSON/YAML Files
```bash
python3 -c "import json; json.load(open('<file>'))"  # JSON
python3 -c "import yaml; yaml.safe_load(open('<file>'))"  # YAML
```

### Markdown Files (`.md`)
- Verify YAML frontmatter with `python3 -c "import yaml; yaml.safe_load(...)"`
- No validation required for pure prose

## When NOT to Validate
- Files in `external_repos/` (read-only reference)
- Files in `archive/` (frozen)
- Binary files (images, fonts)
- Files being deleted

## Error Severity Classification

| Severity | Action | Examples |
|----------|--------|---------|
| **FATAL** | STOP, fix immediately | E999 syntax, F821 undefined name |
| **ERROR** | Fix before next file | F401 unused import, E711 comparison |
| **WARN** | Fix if quick (<10s) | W291 trailing whitespace |
| **INFO** | Ignore | Line length, naming convention |

## Integration with Other Skills
- Feeds into `omni-linter` for full-project sweeps
- Respects `ruff-debt-eradication` exclusion lists
- Coordinates with `blast-pipeline` as the "Lint" stage
