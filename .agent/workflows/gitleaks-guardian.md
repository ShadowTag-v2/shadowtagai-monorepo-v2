---
description: Autonomous secret leak detection, classification, and remediation using Betterleaks (successor to Gitleaks). Scans production code, classifies findings (BLOCK/WARN/IGNORE), auto-remediates false positives, and gates the commit/push pipeline.
---

# Betterleaks Guardian — 5-Layer Secret Defense

Autonomous secret leak scanner, classifier, and pipeline gate.
Uses `scripts/gitleaks_guardian.py` for classification and `betterleaks v1.1+` for detection.
Betterleaks is the successor to Gitleaks by the same authors — 12x faster with CEL-based validation.

## When to Use

- Before any `git push` or `/omega-sync`
- After adding new scripts, configs, or third-party code
- When triaging CI security-audit failures
- Periodic full-workspace audit

## Guardrails

- NEVER print real secret values in output — only redacted prefixes
- BLOCK findings halt the pipeline — no bypass
- IGNORE findings auto-append to `.betterleaksignore` (also reads `.gitleaksignore`)
- All scan results are logged to `.beads/gitleaks_guardian_report.md`

// turbo-all

## Steps

### 1. Run the scoped production scan

Scans only `apps/`, `scripts/`, `libs/`, and root config files.
Skips `external_repos/`, `reference_architectures/`, `tools/antigravity/extensions/`, `tools/external_sdks/`, and all archived content.

```bash
python3 scripts/gitleaks_guardian.py --mode scan --scope production --output .beads/gitleaks_guardian_report.md
```

### 2. Review the generated report

The report is written to `.beads/gitleaks_guardian_report.md`.
Open it and present findings to the user:
- **BLOCK**: Real credentials in production — must remediate before push
- **WARN**: Possible credentials — manual review needed
- **IGNORE**: Auto-classified false positives — already added to `.betterleaksignore`

### 3. Remediate BLOCK findings

For each BLOCK finding, take the recommended action:
- `gcp-api-key` → Move to GCP Secret Manager or use ADC (Application Default Credentials)
- `stripe-secret-key` → Move to Secret Manager, reference via `${STRIPE_SECRET_KEY}`
- `github-pat` / `github-token` → Rotate immediately, use GitHub App PEM per GEMINI.md doctrine
- `private-key` → Remove from source, upload to Secret Manager
- `generic-api-key` → Review manually; if real, move to Secret Manager

### 4. Run the gate check on staged files

After remediation, verify staged files are clean:

```bash
python3 scripts/gitleaks_guardian.py --mode gate
```

This exits with code 0 (clean) or 1 (blocked).

### 5. Commit and push

If the gate passes, proceed with the standard commit flow:

```bash
git add . && git commit -m "chore(security): remediate betterleaks findings"
```

## Integration Points

This workflow is wired into:

| Layer | Component | How |
|-------|-----------|-----|
| 1 | Pre-commit | `.pre-commit-config.yaml` → `betterleaks git --pre-commit --staged` |
| 2 | Finish Changes | `finish_changes.py` → calls `gitleaks_guardian.py --mode gate` |
| 3 | Omega Sync | `omega_sync.py` → calls `gitleaks_guardian.py --mode gate` before push |
| 4 | CI/CD | `security-audit.yml` → `betterleaks-action@v2` on PR/push |
| 5 | On-demand | This workflow (`/gitleaks-guardian`) |

## Optional: Generate Manifest (Audit Mode)

Generate a structured audit manifest of all third-party findings.
Outputs: Markdown (.md), CSV (.csv), per-repo breakdown, and deduped secret list.

```bash
# From a pre-existing scan JSON:
python3 scripts/gitleaks_guardian.py --mode manifest --input /tmp/findings.json

# Or generate a fresh scan and manifest in one step:
python3 scripts/gitleaks_guardian.py --mode scan --scope all --format csv --output .beads/full_audit
```

Manifests are written to `.beads/` (gitignored). Use the CSV for spreadsheet review or Google Doc sharing.

### --format csv

When using `--format csv`, the guardian writes structured CSV output alongside the Markdown report.
This is useful for:
- Sharing with non-technical stakeholders
- Importing into Google Sheets / NotebookLM
- Tracking audit trail over time
