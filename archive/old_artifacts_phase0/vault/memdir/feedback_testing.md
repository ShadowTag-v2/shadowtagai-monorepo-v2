# Feedback & Testing — Memdir Taxonomy

## Test Framework
- **Python**: pytest 8.5 via `/opt/homebrew/bin/python3.14 -m pytest`
- **Baseline**: 504 collected, 480 passed, 3 skipped, E2E expected failures
- **System Python**: ⛔ NEVER use `/usr/bin/python3` (3.9, missing StrEnum/datetime.UTC)

## Verification Posture
- BLAST pipeline: Build → Lint → Audit → Scan → Test
- Post-edit validation: ruff/biome after every file write
- Cor.30 CI gate: `.github/workflows/security-audit.yml`
- Betterleaks pre-commit: secrets detection

## Known Test Gaps
- Gideon OS multi-language blocks lack CI (Risk #81)
- IPI quarantine has no E2E test yet
- Intelligence router scan patterns untested against real attacks

## Feedback Channels
- Console output → structured JSON (never raw stack traces)
- Session logger → `.beads/sessions/*.jsonl`
- Risk register → `RISK_REGISTER.md`
- Beads issues → `.beads/issues.jsonl`
