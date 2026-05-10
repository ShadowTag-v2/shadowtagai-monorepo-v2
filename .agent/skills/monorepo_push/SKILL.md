---
name: Monorepo Push Gate
description: BANS raw `git push`. All pushes route through the GitHub App authenticated gate script.
---

# Monorepo Push Gate

## Prohibition

**`git push` is BANNED.** Any raw `git push origin main`, `git push -f`, or equivalent direct push command is a Tier 1 violation. This applies to all agents, all terminals, all contexts.

## Mandatory Execution Path

All pushes MUST use the GitHub App JWT-authenticated pipeline:

```bash
python3 scripts/auth_github_app.py --push
```

### What This Enforces

1. **Pre-Push Gate 1 — Force-Push Guard**: Blocks `--force` and `--force-with-lease` unless STATE B Clutch is engaged.
2. **Pre-Push Gate 2 — Bloat Check**: Rejects commits containing files >5MB or total push >50MB.
3. **Pre-Push Gate 3 — Release Readiness**: Validates dirty tree state and session files.
4. **Pre-Push Gate 4 — Secret Egress Scan**: Final Betterleaks scan before wire transmission.
5. **JWT Authentication**: Generates ephemeral GitHub App installation token (App ID `3018200`). No PATs, no SSH passphrase prompts, no `gh auth` browser flows.

### PEM Fallback Chain

The script resolves the PEM through a 5-tier cascade:
1. GCP Secret Manager (`github-app-shadowtag-v2-pem`)
2. `keys/` directory
3. `~/Downloads/` (canonical PEM location)
4. `~/.ssh/`
5. `$SHADOWTAG_PEM` env var

## Detection Pattern

If any agent tool log contains `git push` without `auth_github_app.py`, flag as `PUSH_GATE_VIOLATION` in `.beads/issues.jsonl`.

## Cross-References

- `scripts/auth_github_app.py` — Canonical push script
- `AGENTS.md` → GitHub Doctrine
- `GEMINI.md` → GitHub Doctrine section
- `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` — No destructive ops
