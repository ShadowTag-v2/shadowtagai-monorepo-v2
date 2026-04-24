# REPO_MAINTENANCE_RUNBOOK.md — v1.0

> Standard Operating Procedure for monorepo maintenance.
> Boy Scout Rule: no agent writes without a gate; no gate passes without a receipt.

## Five Non-Negotiable Gates

| Gate | Purpose | Script | Required Behavior |
|------|---------|--------|-------------------|
| **Root Guard** | Prevent work in wrong tree | `scripts/pnkln_root_guard.sh` | Fail if repo root, manifest, or canonical paths mismatch |
| **Secret Guard** | Prevent credential leaks | `betterleaks dir -c .betterleaks.toml` | Run before add/commit/push. Block on live secrets. |
| **Drift Guard** | Prevent zombie copies | `scripts/audit_monorepo_state.sh` | Fail if legacy paths diverge from `apps/libs/labs/archive/` layout |
| **Build Guard** | Keep workspace shippable | `ruff check + biome lint` | Run language-specific smoke checks before commit |
| **Memory Guard** | Preserve decisions | `scripts/finish_changes.py` | Append work summary to memory/log after every merge |

## Standard Maintenance Commands

### 1. Inspect
```bash
git status --short
git branch --show-current
git remote -v
```

### 2. Guard
```bash
./scripts/preflight_gate.sh
./scripts/pnkln_root_guard.sh
./scripts/audit_monorepo_state.sh
```

### 3. Search
```bash
rg "TODO|FIXME|HACK|XXX|<<<<<<<|=======|>>>>>>>" apps libs scripts docs
sg scan || true
```

### 4. Security
```bash
# PRIMARY: Betterleaks (12.9x faster than gitleaks)
PATH="$HOME/go/bin:$PATH" betterleaks dir -c .betterleaks.toml --redact .

# DEPRECATED FALLBACK: Gitleaks
# gitleaks detect --source . --redact
```

### 5. Health Check
```bash
python3 scripts/repo_doctor.py
```

### 6. Finish
```bash
python3 scripts/finish_changes.py
```

## Operating Cadence

### Daily
- [ ] Run `scripts/repo_doctor.py`
- [ ] Process dirty files
- [ ] Repair lint/import/build failures
- [ ] Update memory
- [ ] Ship one small PR

### Weekly
- [ ] Run dependency drift audit
- [ ] Run full betterleaks security scan
- [ ] Rebuild memory index
- [ ] Archive stale branches
- [ ] Review blocked Sentinel actions

### Monthly
- [ ] Agent performance scorecard
- [ ] Merge/deprecate agents
- [ ] Re-rank repo ingestion tiers
- [ ] Record customer-zero demo
- [ ] Update product roadmap

## Sentinel Risk Classification

| Risk | Examples | Action |
|------|----------|--------|
| **Low** | Formatting, docs, tests | Auto patch allowed |
| **Medium** | App code, deps, generated files | Patch branch + review |
| **High** | Schema migration, auth, billing, infra | Human approval required |
| **Critical** | Secrets, prod delete, credential export, destructive shell | Block + incident log |

**Product guarantee**: Every agent action is classified, logged, gated, and reversible.

## Large-File Prevention Protocol

The repo has suffered from agent-created obesity (multi-GB pushes). Enforcement:

1. **`.gitignore`** excludes: `tools/external_sdks/`, `browser_artifacts/`, `*.webm`, `*.mp4`, `*.onnx`, `*.bin`, `*.dmg`, `*.zip`, `*.tar.gz`, `.lancedb/`, `external_repos/`
2. **Pre-commit hook**: `check-added-large-files` maxkb=500
3. **Chunked push**: `scripts/chunked_push.py` for large commit batches
4. **Invariant #102**: GitHub Push Chunking Protocol (binary exclusions)

## Secret Leak Prevention Protocol

1. **Pre-commit**: Betterleaks local hook runs on every commit
2. **CI**: `betterleaks-action@v2` in `.github/workflows/security-audit.yml`
3. **Allowlist**: `.betterleaksignore` (1,150 fingerprinted false positives)
4. **Config**: `.betterleaks.toml` with `tools/external_sdks/` excluded
5. **On-demand**: `python3 scripts/gitleaks_guardian.py` for deep audit

## Emergency Procedures

### Secret Leaked in Commit
1. **DO NOT PUSH** if not yet pushed
2. Run `git reset --soft HEAD~1` to undo commit
3. Remove the secret from the file
4. Rotate the secret in GCP Secret Manager
5. If already pushed: use `git filter-repo` to scrub history (see Risk #40, #41)

### Repo Size Explosion
1. Check `du -sh .` vs `git count-objects -vH`
2. Run `git rev-list --objects --all | git cat-file --batch-check | sort -k3 -n -r | head -20`
3. Add offending paths to `.gitignore`
4. If committed: use `git filter-repo --path-glob '*.onnx' --invert-paths`
5. Force push via `scripts/chunked_push.py`

### Manifest Drift
1. Run `scripts/audit_monorepo_state.sh`
2. Compare physical tree vs `monorepo_manifest.yaml`
3. Update manifest or move files to canonical paths
4. Run `scripts/pnkln_root_guard.sh` to verify
