# Changelog

## [v12.1] - 2026-04-25

- fix(truth): Stage 3 canonicalization — align manifest v12.0→v12.1 with 7 drift corrections
- fix(truth): gold_master_tag v11.9→v11.7 (actual latest tag), risk_register_count 86→94
- fix(truth): skill counts agent 49→51, global 224→209, duplicates 7→0 (all resolved)
- fix(truth): CI workflow count 74→75, Lighthouse labels desktop (not mobile)
- fix(secrets): prodding_engine.py api_key="TBD" → os.getenv("TESLA_API_KEY") compliance
- audit(lighthouse): kovelai A100/BP96/SEO100, shadowtagai A100/BP96/SEO100 (improved A93→A100)
- audit(tests): 504 collected, 499 passed, 3 skipped, 2 xfailed (full suite verified)
- audit(ruff): 0 F401/F841 violations across apps/libs/scripts/tests
- chore(branches): deleted stale merged branch feat/design-spec-gold-standard

## [v11.3-gold] - 2026-04-24

- fix(truth): canonicalize .NET version across all truth surfaces (11.0 Preview→10.0.106, matching global.json + csproj)
- fix(truth): update test baseline to 504 collected / 480 unit passed / 3 skipped (pytest 3.14)
- fix(truth): align gold_master_tag v11.2→v11.3, dotnet_version 10.0.202→10.0.106 in manifest
- audit(firebase): project health verified — 2 Firestore DBs (PITR+delete protection), 1 web app ACTIVE
- audit(lighthouse): kovelai.web.app A94/BP100/SEO100, shadowtagai.web.app A95/BP96/SEO100
- audit(ruff): 0 F401/F841 violations in apps/tests/scripts
- audit(pre-commit): betterleaks + detect-private-key + ruff + check-yaml all verified

## [v11.0-obsidian] - 2026-04-23

- chore(sweep): V11 items 1-22 — biome vendor exclude, .NET 10.0.106 truth, print→logging, npm audit, k6 load test
- fix(pyright): V10 Epistemic Airgap — add all Python source roots to extraPaths + executionEnvironments
- chore(sweep): items 2-7 — firebase-admin upgrade + print cleanup + Knip dead code removal

## [v11.0-obsidian] - Initial Release

- fix(sweep): V11 remainder — ast-grep rule fix + pre-commit biome fix + project ID alignment
- feat(obsidian): V11 Obsidian Release — Lighthouse Budget + 11x Extractor + IDE Governance
- feat(security): V10 Epistemic Airgap — Zero-Trust Cognitive Routing
- fix(truth): align .NET version across all 5 truth surfaces to 10.0.202
- feat(ci): V7/V8 GitOps Ascension — Zero-Trust CI + AST-Grep + Debt Burn
- feat(omega): V5+V6 Omni-Sanitation + IDE Stabilization + Omega Egress
- feat: V4 cognitive-structural-synthesis + 22-item sweep
- refactor: ruff 828→0 debt eradication + pre-commit scope fix
- feat: 22-item hardening sweep + cognitive structural synthesis
- ci(hygiene): add vulture CI gate + fix pre-commit ruff exclusions + py3.9 compat
